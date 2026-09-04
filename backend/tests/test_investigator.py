import pytest
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models.transaction import GatewayTransaction, BankSettlement, LedgerEntry
from app.services.investigator import investigate_transaction

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_ts(ts_str):
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))

def setup_test_data(db):
    """Create test data for various scenarios"""

    # Successful settlement case
    gateway_success = GatewayTransaction(
        transaction_id="txn_success",
        merchant_id="merch_success",
        amount=99.99,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:00:00Z"),
        processor_ref="gw_success"
    )

    bank_success = BankSettlement(
        processor_ref="gw_success",
        settlement_id="set_success",
        amount=99.99,
        status="SETTLED",
        bank_timestamp=parse_ts("2026-01-01T14:00:00Z"),
        settlement_date="2026-01-02"
    )

    ledger_success = LedgerEntry(
        transaction_id="txn_success",
        ledger_id="led_success",
        account="acc_success",
        amount=99.99,
        entry_type="CREDIT",
        posted_date="2026-01-02",
        reconciled=True
    )

    # Failed transaction case
    gateway_failed = GatewayTransaction(
        transaction_id="txn_failed",
        merchant_id="merch_failed",
        amount=75.25,
        currency="USD",
        status="FAILED",
        gateway_timestamp=parse_ts("2026-01-01T10:10:00Z"),
        processor_ref="gw_failed"
    )

    bank_failed = BankSettlement(
        processor_ref="gw_failed",
        settlement_id="set_failed",  # Added set_failed to avoid empty string unique constraint issue
        amount=0.0,
        status="FAILED",
        bank_timestamp=parse_ts("2026-01-01T14:05:00Z"),
        settlement_date="2026-01-02"
    )

    # Missing ledger case
    gateway_missing = GatewayTransaction(
        transaction_id="txn_missing_ledger",
        merchant_id="merch_missing",
        amount=200.00,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:15:00Z"),
        processor_ref="gw_missing"
    )

    bank_missing = BankSettlement(
        processor_ref="gw_missing",
        settlement_id="set_missing",
        amount=200.00,
        status="SETTLED",
        bank_timestamp=parse_ts("2026-01-01T14:10:00Z"),
        settlement_date="2026-01-02"
    )
    # Note: No ledger entry for this transaction

    # Amount mismatch case
    gateway_mismatch = GatewayTransaction(
        transaction_id="txn_amount_mismatch",
        merchant_id="merch_mismatch",
        amount=50.00,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:20:00Z"),
        processor_ref="gw_mismatch"
    )

    bank_mismatch = BankSettlement(
        processor_ref="gw_mismatch",
        settlement_id="set_mismatch",
        amount=55.00,  # Different amount
        status="SETTLED",
        bank_timestamp=parse_ts("2026-01-01T14:15:00Z"),
        settlement_date="2026-01-02"
    )

    ledger_mismatch = LedgerEntry(
        transaction_id="txn_amount_mismatch",
        ledger_id="led_mismatch",
        account="acc_mismatch",
        amount=60.00,  # Different amount
        entry_type="CREDIT",
        posted_date="2026-01-02",
        reconciled=True
    )

    # Duplicate transaction case
    gateway_dup_1 = GatewayTransaction(
        transaction_id="txn_duplicate_1",
        merchant_id="merch_dup",
        amount=120.00,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:25:00Z"),
        processor_ref="gw_dup"
    )

    gateway_dup_2 = GatewayTransaction(
        transaction_id="txn_duplicate_2",
        merchant_id="merch_dup",
        amount=120.00,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:26:00Z"),  # Slightly different time
        processor_ref="gw_dup"  # Same processor ref
    )

    bank_dup = BankSettlement(
        processor_ref="gw_dup",
        settlement_id="set_dup",
        amount=120.00,
        status="SETTLED",
        bank_timestamp=parse_ts("2026-01-01T14:20:00Z"),
        settlement_date="2026-01-02"
    )

    ledger_dup_1 = LedgerEntry(
        transaction_id="txn_duplicate_1",
        ledger_id="led_dup1",
        account="acc_dup",
        amount=120.00,
        entry_type="CREDIT",
        posted_date="2026-01-02",
        reconciled=True
    )

    ledger_dup_2 = LedgerEntry(
        transaction_id="txn_duplicate_2",
        ledger_id="led_dup2",
        account="acc_dup",
        amount=120.00,
        entry_type="CREDIT",
        posted_date="2026-01-02",
        reconciled=True
    )

    # Unknown transaction case (not in ledger or bank)
    gateway_unknown = GatewayTransaction(
        transaction_id="txn_unknown",
        merchant_id="merch_unknown",
        amount=85.99,
        currency="USD",
        status="SETTLED",
        gateway_timestamp=parse_ts("2026-01-01T10:30:00Z"),
        processor_ref="gw_unknown"
    )

    bank_unknown = BankSettlement(
        processor_ref="gw_unknown",
        settlement_id="set_unknown",  # Added set_unknown
        amount=0.0,
        status="UNKNOWN",
        bank_timestamp=parse_ts("2026-01-01T14:25:00Z"),
        settlement_date="2026-01-02"
    )
    # Note: No ledger entry

    # Add all to session
    db.add_all([
        gateway_success, bank_success, ledger_success,
        gateway_failed, bank_failed,
        gateway_missing, bank_missing,
        gateway_mismatch, bank_mismatch, ledger_mismatch,
        gateway_dup_1, gateway_dup_2, bank_dup, ledger_dup_1, ledger_dup_2,
        gateway_unknown, bank_unknown
    ])
    db.commit()

@pytest.fixture
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        setup_test_data(db)
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

def test_successful_settlement(db_session):
    """Test a successful settlement scenario"""
    result = investigate_transaction(db_session, "txn_success")

    assert result["transaction_id"] == "txn_success"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is not None
    assert len(result["duplicate_gateway_transactions"]) == 0
    assert result["status"] == "SETTLED"
    assert result["amount_consistent"] == True
    assert result["status_consistent"] == True
    assert result["confidence"] > 0.8  # Should be high confidence
    assert len(result["anomalies"]) == 0

def test_failed_transaction(db_session):
    """Test a failed transaction scenario"""
    result = investigate_transaction(db_session, "txn_failed")

    assert result["transaction_id"] == "txn_failed"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is None  # Missing ledger
    assert result["status"] == "FAILED"
    assert len(result["anomalies"]) > 0  # Should have missing ledger anomaly
    assert result["confidence"] < 0.8  # Lower confidence due to missing data

def test_missing_ledger_entry(db_session):
    """Test transaction with missing ledger entry"""
    result = investigate_transaction(db_session, "txn_missing_ledger")

    assert result["transaction_id"] == "txn_missing_ledger"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is None
    assert any("ledger" in a.lower() for a in result["anomalies"])
    assert result["confidence"] < 0.8

def test_amount_mismatch(db_session):
    """Test transaction with amount mismatch across sources"""
    result = investigate_transaction(db_session, "txn_amount_mismatch")

    assert result["transaction_id"] == "txn_amount_mismatch"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is not None
    assert result["amount_consistent"] == False
    assert any("Amount mismatch" in a for a in result["anomalies"])
    assert result["confidence"] < 0.8

def test_duplicate_transactions(db_session):
    """Test transaction with duplicate gateway entries"""
    result = investigate_transaction(db_session, "txn_duplicate_1")

    assert result["transaction_id"] == "txn_duplicate_1"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is not None
    assert len(result["duplicate_gateway_transactions"]) == 1  # Should find the duplicate
    assert any("duplicate gateway transaction" in a.lower() for a in result["anomalies"])
    assert result["confidence"] < 0.9  # Reduced confidence due to duplicates

def test_unknown_transaction(db_session):
    """Test transaction not found in bank or ledger"""
    result = investigate_transaction(db_session, "txn_unknown")

    assert result["transaction_id"] == "txn_unknown"
    assert result["gateway_data"] is not None
    assert result["bank_data"] is not None
    assert result["ledger_data"] is None
    assert result["status"] in ["UNKNOWN", "SETTLED"]
    assert len(result["anomalies"]) > 0
    assert result["confidence"] < 0.8

def test_transaction_not_found(db_session):
    """Test completely unknown transaction ID"""
    result = investigate_transaction(db_session, "txn_does_not_exist")

    assert result["transaction_id"] == "txn_does_not_exist"
    assert result["gateway_data"] is None
    assert result["bank_data"] is None
    assert result["ledger_data"] is None
    assert result["status"] == "UNKNOWN"
    assert any("not found in gateway" in a.lower() for a in result["anomalies"])
    assert result["confidence"] == 0.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])