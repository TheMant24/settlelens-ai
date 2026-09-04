from sqlalchemy.orm import Session
from ..models.transaction import LedgerEntry
from typing import Optional, Dict, Any

def get_ledger_entry_by_transaction_id(db: Session, transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch ledger entry by transaction_id
    """
    ledger_entry = db.query(LedgerEntry).filter(
        LedgerEntry.transaction_id == transaction_id
    ).first()

    if ledger_entry:
        return {
            "transaction_id": ledger_entry.transaction_id,
            "ledger_id": ledger_entry.ledger_id,
            "account": ledger_entry.account,
            "amount": ledger_entry.amount,
            "entry_type": ledger_entry.entry_type,
            "posted_date": ledger_entry.posted_date,
            "reconciled": ledger_entry.reconciled
        }
    return None

def get_ledger_entries_by_ledger_id(db: Session, ledger_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch ledger entry by ledger_id
    """
    ledger_entry = db.query(LedgerEntry).filter(
        LedgerEntry.ledger_id == ledger_id
    ).first()

    if ledger_entry:
        return {
            "transaction_id": ledger_entry.transaction_id,
            "ledger_id": ledger_entry.ledger_id,
            "account": ledger_entry.account,
            "amount": ledger_entry.amount,
            "entry_type": ledger_entry.entry_type,
            "posted_date": ledger_entry.posted_date,
            "reconciled": ledger_entry.reconciled
        }
    return None