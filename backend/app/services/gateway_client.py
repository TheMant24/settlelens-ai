from sqlalchemy.orm import Session
from ..models.transaction import GatewayTransaction
from typing import Optional, Dict, Any

def get_gateway_transaction(db: Session, transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch gateway transaction by transaction_id
    """
    transaction = db.query(GatewayTransaction).filter(
        GatewayTransaction.transaction_id == transaction_id
    ).first()

    if transaction:
        return {
            "transaction_id": transaction.transaction_id,
            "merchant_id": transaction.merchant_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "status": transaction.status,
            "gateway_timestamp": transaction.gateway_timestamp,
            "processor_ref": transaction.processor_ref
        }
    return None

def get_gateway_transactions_by_processor_ref(db: Session, processor_ref: str) -> list:
    """
    Fetch all gateway transactions by processor_ref (for handling duplicates)
    """
    transactions = db.query(GatewayTransaction).filter(
        GatewayTransaction.processor_ref == processor_ref
    ).all()

    return [
        {
            "transaction_id": t.transaction_id,
            "merchant_id": t.merchant_id,
            "amount": t.amount,
            "currency": t.currency,
            "status": t.status,
            "gateway_timestamp": t.gateway_timestamp,
            "processor_ref": t.processor_ref
        }
        for t in transactions
    ]