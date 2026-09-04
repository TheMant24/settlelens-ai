"""Investigate API endpoint"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import InvestigateRequest, InvestigateResponse
from ..services.investigator import investigate_transaction
from ..services.llm_client import call_llm, validate_llm_response, LLMClientError

router = APIRouter()


@router.post("/investigate", response_model=InvestigateResponse)
def investigate(
    request: InvestigateRequest,
    db: Session = Depends(get_db),
):
    """
    Investigate a transaction by ID.

    Returns a structured response with:
    - status: Overall settlement status
    - plain_english: Plain English explanation
    - exceptions: List of data gaps or uncertainties
    - confidence: Confidence score (0-1)
    """
    # 1. Run deterministic investigation
    try:
        investigation = investigate_transaction(db, request.transaction_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")

    # 2. If transaction doesn't exist at all, short-circuit (no LLM needed)
    if investigation["status"] == "UNKNOWN" and not investigation.get("gateway_data"):
        return InvestigateResponse(
            transaction_id=request.transaction_id,
            status="UNKNOWN",
            plain_english=(
                f"No transaction with ID '{request.transaction_id}' was found in our gateway records. "
                "Please verify the transaction ID and try again."
            ),
            exceptions=[
                "Transaction not found in gateway",
                "No bank settlement data available",
                "No ledger entry available",
            ],
            confidence=0.0,
        )

    # 3. Build structured context for the LLM (factual data only)
    context = {
        "transaction_id": investigation["transaction_id"],
        "overall_status": investigation["status"],
        "data_completeness": {
            "gateway_present": investigation["gateway_data"] is not None,
            "bank_present": investigation["bank_data"] is not None,
            "ledger_present": investigation["ledger_data"] is not None,
        },
        "factual_amounts": {
            "gateway_amount": investigation["gateway_data"]["amount"] if investigation["gateway_data"] else None,
            "bank_amount": investigation["bank_data"]["amount"] if investigation["bank_data"] else None,
            "ledger_amount": investigation["ledger_data"]["amount"] if investigation["ledger_data"] else None,
        },
        "factual_statuses": {
            "gateway_status": investigation["gateway_data"]["status"] if investigation["gateway_data"] else None,
            "bank_status": investigation["bank_data"]["status"] if investigation["bank_data"] else None,
            "ledger_reconciled": investigation["ledger_data"]["reconciled"] if investigation["ledger_data"] else None,
        },
        "factual_metadata": {
            "merchant_id": investigation["gateway_data"]["merchant_id"] if investigation["gateway_data"] else None,
            "processor_ref": investigation["gateway_data"]["processor_ref"] if investigation["gateway_data"] else None,
            "currency": investigation["gateway_data"]["currency"] if investigation["gateway_data"] else None,
            "gateway_timestamp": investigation["gateway_data"]["gateway_timestamp"] if investigation["gateway_data"] else None,
            "bank_timestamp": investigation["bank_data"]["bank_timestamp"] if investigation["bank_data"] else None,
        },
        "consistency_checks": {
            "all_sources_present": investigation["all_sources_present"],
            "amount_consistent": investigation["amount_consistent"],
            "status_consistent": investigation["status_consistent"],
        },
        "anomalies": investigation["anomalies"],
        "duplicate_gateway_transactions": investigation["duplicate_gateway_transactions"],
        "factual_confidence": investigation["confidence"],
    }

    # 4. Call the LLM to explain the factual data
    try:
        llm_result = call_llm(context)
        validated = validate_llm_response(llm_result)
    except LLMClientError as e:
        # LLM failed - return a deterministic fallback based on factual data
        anomalies = investigation["anomalies"]
        if investigation["gateway_data"]:
            merchant = investigation["gateway_data"].get("merchant_id", "unknown")
            amount = investigation["gateway_data"].get("amount", 0)
            plain_english = (
                f"Transaction {request.transaction_id} (merchant {merchant}, ${amount:.2f}) "
                f"has an overall status of {investigation['status']}. "
                f"The LLM explanation service is currently unavailable, so this summary is based "
                f"on factual data only."
            )
        else:
            plain_english = (
                f"Transaction {request.transaction_id} could not be fully investigated "
                f"and the explanation service is currently unavailable."
            )

        return InvestigateResponse(
            transaction_id=request.transaction_id,
            status=investigation["status"],
            plain_english=plain_english,
            exceptions=anomalies + [f"LLM service error: {str(e)}"],
            confidence=investigation["confidence"] * 0.5,  # Reduce confidence when LLM unavailable
        )

    # 5. Merge factual exceptions with LLM exceptions (LLM should not drop them, but ensure they're present)
    factual_exceptions = investigation["anomalies"]
    llm_exceptions = validated["exceptions"]
    # Combine and deduplicate
    combined_exceptions = list(dict.fromkeys(factual_exceptions + llm_exceptions))

    # 6. Return final structured response
    return InvestigateResponse(
        transaction_id=request.transaction_id,
        status=validated["status"],
        plain_english=validated["plain_english"],
        exceptions=combined_exceptions,
        confidence=validated["confidence"],
    )