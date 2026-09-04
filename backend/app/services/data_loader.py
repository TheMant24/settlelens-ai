import csv
import os
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import SessionLocal, engine, Base
from ..models.transaction import GatewayTransaction, BankSettlement, LedgerEntry
from ..config import DATABASE_URL

# Get the project root directory (parent of backend's parent)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def parse_timestamp(ts_str):
    if not ts_str:
        return None
    try:
        # Try ISO format
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def load_gateway_transactions(db: Session):
    csv_path = DATA_DIR / "gateway_transactions.csv"
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if transaction already exists
            exists = db.query(GatewayTransaction).filter_by(transaction_id=row['transaction_id']).first()
            if not exists:
                db_transaction = GatewayTransaction(
                    transaction_id=row['transaction_id'],
                    merchant_id=row['merchant_id'],
                    amount=float(row['amount']),
                    currency=row['currency'],
                    status=row['status'],
                    gateway_timestamp=parse_timestamp(row['gateway_timestamp']),
                    processor_ref=row['processor_ref']
                )
                db.add(db_transaction)
    db.commit()

def load_bank_settlements(db: Session):
    csv_path = DATA_DIR / "bank_settlements.csv"
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Skip records with empty settlement_id (they represent failed/unknown transactions with no settlement)
            if not row['settlement_id'] or row['settlement_id'].strip() == '':
                continue

            # Check if settlement already exists
            exists = db.query(BankSettlement).filter_by(settlement_id=row['settlement_id']).first()
            if not exists:
                db_settlement = BankSettlement(
                    processor_ref=row['processor_ref'],
                    settlement_id=row['settlement_id'],
                    amount=float(row['amount']) if row['amount'] else 0.0,
                    status=row['status'],
                    bank_timestamp=parse_timestamp(row['bank_timestamp']),
                    settlement_date=row['settlement_date']
                )
                db.add(db_settlement)
    db.commit()

def load_ledger_entries(db: Session):
    csv_path = DATA_DIR / "ledger_entries.csv"
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if ledger entry already exists
            exists = db.query(LedgerEntry).filter_by(ledger_id=row['ledger_id']).first()
            if not exists:
                db_ledger = LedgerEntry(
                    transaction_id=row['transaction_id'],
                    ledger_id=row['ledger_id'],
                    account=row['account'],
                    amount=float(row['amount']) if row['amount'] else 0.0,
                    entry_type=row['entry_type'],
                    posted_date=row['posted_date'],
                    reconciled=row['reconciled'].lower() == 'true'
                )
                db.add(db_ledger)
    db.commit()

def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    db = SessionLocal()
    try:
        load_gateway_transactions(db)
        load_bank_settlements(db)
        load_ledger_entries(db)
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()