from sqlalchemy.orm import Session
from ..models.transaction import BankSettlement
from typing import Optional, Dict, Any

def get_bank_settlement_by_processor_ref(db: Session, processor_ref: str) -> Optional[Dict[str, Any]]:
    """
    Fetch bank settlement by processor_ref
    """
    settlement = db.query(BankSettlement).filter(
        BankSettlement.processor_ref == processor_ref
    ).first()

    if settlement:
        return {
            "processor_ref": settlement.processor_ref,
            "settlement_id": settlement.settlement_id,
            "amount": settlement.amount,
            "status": settlement.status,
            "bank_timestamp": settlement.bank_timestamp,
            "settlement_date": settlement.settlement_date
        }
    return None

def get_bank_settlement_by_settlement_id(db: Session, settlement_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch bank settlement by settlement_id
    """
    settlement = db.query(BankSettlement).filter(
        BankSettlement.settlement_id == settlement_id
    ).first()

    if settlement:
        return {
            "processor_ref": settlement.processor_ref,
            "settlement_id": settlement.settlement_id,
            "amount": settlement.amount,
            "status": settlement.status,
            "bank_timestamp": settlement.bank_timestamp,
            "settlement_date": settlement.settlement_date
        }
    return None