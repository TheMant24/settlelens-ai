from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from .gateway_client import get_gateway_transaction, get_gateway_transactions_by_processor_ref
from .bank_client import get_bank_settlement_by_processor_ref
from .ledger_client import get_ledger_entry_by_transaction_id

def investigate_transaction(db: Session, transaction_id: str) -> Dict[str, Any]:
    """
    Investigate a transaction by correlating data from gateway, bank, and ledger sources.
    Returns a dictionary with factual findings that the LLM will later explain.
    """
    # Initialize result structure
    result = {
        "transaction_id": transaction_id,
        "gateway_data": None,
        "bank_data": None,
        "ledger_data": None,
        "duplicate_gateway_transactions": [],
        "anomalies": [],
        "confidence_factors": [],
        "status": "UNKNOWN",
        "amount_consistent": False,
        "status_consistent": False,
        "all_sources_present": False,
        "confidence": 0.0  # Default confidence
    }

    # 1. Fetch gateway transaction
    gateway_data = get_gateway_transaction(db, transaction_id)
    result["gateway_data"] = gateway_data

    if not gateway_data:
        result["anomalies"].append("Transaction not found in gateway")
        # Already has confidence: 0.0 from initialization
        return result

    # 2. Fetch bank settlement using processor_ref from gateway
    processor_ref = gateway_data["processor_ref"]
    bank_data = get_bank_settlement_by_processor_ref(db, processor_ref)
    result["bank_data"] = bank_data

    # 3. Fetch ledger entry
    ledger_data = get_ledger_entry_by_transaction_id(db, transaction_id)
    result["ledger_data"] = ledger_data

    # 4. Check for duplicate gateway transactions (same processor_ref)
    if processor_ref:
        duplicates = get_gateway_transactions_by_processor_ref(db, processor_ref)
        # Filter out the original transaction
        result["duplicate_gateway_transactions"] = [
            tx for tx in duplicates if tx["transaction_id"] != transaction_id
        ]
        if result["duplicate_gateway_transactions"]:
            result["anomalies"].append(
                f"Found {len(result['duplicate_gateway_transactions'])} duplicate gateway transaction(s) with same processor_ref"
            )

    # 5. Analyze consistency and determine status
    analyze_consistency(result)

    # 6. Calculate confidence based on data completeness and consistency
    result["confidence"] = calculate_confidence(result)

    return result

def analyze_consistency(result: Dict[str, Any]) -> None:
    """Analyze data consistency and update result with findings."""
    gateway = result["gateway_data"]
    bank = result["bank_data"]
    ledger = result["ledger_data"]

    # Check which sources are present
    sources_present = sum([
        bool(gateway),
        bool(bank),
        bool(ledger)
    ])
    result["all_sources_present"] = (sources_present == 3)

    if not result["all_sources_present"]:
        missing = []
        if not gateway: missing.append("gateway")
        if not bank: missing.append("bank")
        if not ledger: missing.append("ledger")
        result["anomalies"].append(f"Missing data from: {', '.join(missing)}")

    # Amount consistency check
    amounts = []
    if gateway: amounts.append(("gateway", gateway["amount"]))
    if bank and bank["amount"] > 0: amounts.append(("bank", bank["amount"]))  # Skip zero/failed amounts
    if ledger: amounts.append(("ledger", ledger["amount"]))

    if len(amounts) >= 2:
        # Check if all amounts are within $0.01 of each other
        base_amount = amounts[0][1]
        all_consistent = all(abs(amt - base_amount) <= 0.01 for _, amt in amounts)
        result["amount_consistent"] = all_consistent

        if not all_consistent:
            amount_details = ", ".join([f"{source}: ${amt:.2f}" for source, amt in amounts])
            result["anomalies"].append(f"Amount mismatch across sources: {amount_details}")
    else:
        result["amount_consistent"] = False
        if len(amounts) < 2:
            result["anomalies"].append("Insufficient amount data for consistency check")

    # Status consistency check
    statuses = []
    if gateway: statuses.append(("gateway", gateway["status"]))
    if bank: statuses.append(("bank", bank["status"]))
    # Ledger doesn't have a status field, but we can infer from reconciled field
    if ledger:
        ledger_status = "SETTLED" if ledger["reconciled"] else "PENDING"
        statuses.append(("ledger", ledger_status))

    if len(statuses) >= 2:
        # Check if all statuses are compatible
        status_values = [status for _, status in statuses]
        # Define status compatibility
        compatible_groups = [
            {"SETTLED", "SETTLED"},  # Exact match
            {"PENDING", "PENDING"},  # Exact match
            {"FAILED", "FAILED"},    # Exact match
            {"AUTHORIZED", "SETTLED"},  # Authorized can lead to settled
            {"AUTHORIZED", "PENDING"},  # Authorized can be pending
        ]

        all_compatible = True
        for i in range(len(status_values)):
            for j in range(i+1, len(status_values)):
                pair = {status_values[i], status_values[j]}
                if pair not in compatible_groups:
                    all_compatible = False
                    break
            if not all_compatible:
                break

        result["status_consistent"] = all_compatible

        if not all_compatible:
            status_details = ", ".join([f"{source}: {status}" for source, status in statuses])
            result["anomalies"].append(f"Status inconsistency across sources: {status_details}")

        # Determine overall status based on priority: FAILED > SETTLED > PENDING > AUTHORIZED > UNKNOWN
        status_priority = {"FAILED": 4, "SETTLED": 3, "PENDING": 2, "AUTHORIZED": 1, "UNKNOWN": 0}
        if statuses:
            # Get the highest priority status
            result["status"] = max(statuses, key=lambda x: status_priority.get(x[1], 0))[1]
        else:
            result["status"] = "UNKNOWN"
    else:
        result["status_consistent"] = False
        if len(statuses) < 2:
            result["anomalies"].append("Insufficient status data for consistency check")
        # Set status from available data
        if gateway:
            result["status"] = gateway["status"]
        elif bank:
            result["status"] = bank["status"]
        elif ledger:
            result["status"] = "SETTLED" if ledger["reconciled"] else "PENDING"
        else:
            result["status"] = "UNKNOWN"

def calculate_confidence(result: Dict[str, Any]) -> float:
    """Calculate confidence score based on data completeness and consistency."""
    confidence = 1.0

    # Reduce confidence for missing sources
    if not result["all_sources_present"]:
        confidence -= 0.3  # Significant penalty for missing data

    # Reduce confidence for amount inconsistencies
    if not result["amount_consistent"]:
        confidence -= 0.2

    # Reduce confidence for status inconsistencies
    if not result["status_consistent"]:
        confidence -= 0.2

    # Reduce confidence for duplicates
    if result["duplicate_gateway_transactions"]:
        confidence -= 0.1 * len(result["duplicate_gateway_transactions"])
        confidence = max(0.0, confidence)  # Don't go below 0

    # Reduce confidence for each anomaly
    confidence -= 0.05 * len(result["anomalies"])
    confidence = max(0.0, confidence)  # Don't go below 0

    # Ensure confidence is between 0 and 1
    return min(1.0, max(0.0, confidence))