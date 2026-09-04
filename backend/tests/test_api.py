"""Tests for the /investigate API endpoint"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.schemas import InvestigateResponse

client = TestClient(app)


def test_investigate_successful():
    """Test investigation of a successful transaction"""
    with patch('app.api.investigate.call_llm') as mock_llm, \
         patch('app.api.investigate.validate_llm_response') as mock_validate, \
         patch('app.services.investigator.investigate_transaction') as mock_investigate:

        # Mock the investigator response
        mock_investigate.return_value = {
            "transaction_id": "txn_success",
            "gateway_data": {
                "transaction_id": "txn_success",
                "merchant_id": "merch_success",
                "amount": 99.99,
                "currency": "USD",
                "status": "SETTLED",
                "gateway_timestamp": "2026-01-01T10:00:00Z",
                "processor_ref": "gw_success"
            },
            "bank_data": {
                "processor_ref": "gw_success",
                "settlement_id": "set_success",
                "amount": 99.99,
                "status": "SETTLED",
                "bank_timestamp": "2026-01-01T14:00:00Z",
                "settlement_date": "2026-01-02"
            },
            "ledger_data": {
                "transaction_id": "txn_success",
                "ledger_id": "led_success",
                "account": "acc_success",
                "amount": 99.99,
                "entry_type": "CREDIT",
                "posted_date": "2026-01-02",
                "reconciled": True
            },
            "duplicate_gateway_transactions": [],
            "anomalies": [],
            "confidence": 0.95,
            "all_sources_present": True,
            "amount_consistent": True,
            "status_consistent": True,
            "status": "SETTLED"
        }

        # Mock the LLM response
        mock_llm.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_success for merch_success was successfully settled for $99.99. All systems confirm completion.",
            "exceptions": [],
            "confidence": 0.95
        }

        mock_validate.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_success for merch_success was successfully settled for $99.99. All systems confirm completion.",
            "exceptions": [],
            "confidence": 0.95
        }

        # Call the endpoint
        response = client.post("/investigate", json={"transaction_id": "txn_success"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "txn_success"
        assert data["status"] == "SETTLED"
        # Check that plain_english contains key elements rather than exact string
        plain_lower = data["plain_english"].lower()
        assert "txn_success" in plain_lower
        assert "merch_success" in plain_lower
        assert "99.99" in plain_lower
        assert "settled" in plain_lower
        assert isinstance(data["exceptions"], list)
        assert data["confidence"] >= 0.9


def test_investigate_missing_ledger():
    """Test investigation with missing ledger entry"""
    with patch('app.api.investigate.call_llm') as mock_llm, \
         patch('app.api.investigate.validate_llm_response') as mock_validate, \
         patch('app.services.investigator.investigate_transaction') as mock_investigate:

        mock_investigate.return_value = {
            "transaction_id": "txn_missing_ledger",
            "gateway_data": {
                "transaction_id": "txn_missing_ledger",
                "merchant_id": "merch_missing",
                "amount": 200.00,
                "currency": "USD",
                "status": "SETTLED",
                "gateway_timestamp": "2026-01-01T10:15:00Z",
                "processor_ref": "gw_missing"
            },
            "bank_data": {
                "processor_ref": "gw_missing",
                "settlement_id": "set_missing",
                "amount": 200.00,
                "status": "SETTLED",
                "bank_timestamp": "2026-01-01T14:10:00Z",
                "settlement_date": "2026-01-02"
            },
            "ledger_data": None,  # Missing ledger
            "duplicate_gateway_transactions": [],
            "anomalies": ["Missing data from: ledger"],
            "confidence": 0.6,
            "all_sources_present": False,
            "amount_consistent": True,
            "status_consistent": True,
            "status": "SETTLED"
        }

        mock_llm.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_missing_ledger for merch_missing shows $200.00 as settled in gateway and bank, but no ledger entry was found for verification.",
            "exceptions": ["Missing data from: ledger"],
            "confidence": 0.6
        }

        mock_validate.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_missing_ledger for merch_missing shows $200.00 as settled in gateway and bank, but no ledger entry was found for verification.",
            "exceptions": ["Missing data from: ledger"],
            "confidence": 0.6
        }

        response = client.post("/investigate", json={"transaction_id": "txn_missing_ledger"})

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "txn_missing_ledger"
        assert data["status"] == "SETTLED"
        assert any("ledger" in exc.lower() for exc in data["exceptions"])
        assert data["confidence"] < 0.8


def test_investigate_amount_mismatch():
    """Test investigation with amount mismatch"""
    with patch('app.api.investigate.call_llm') as mock_llm, \
         patch('app.api.investigate.validate_llm_response') as mock_validate, \
         patch('app.services.investigator.investigate_transaction') as mock_investigate:

        mock_investigate.return_value = {
            "transaction_id": "txn_amount_mismatch",
            "gateway_data": {
                "transaction_id": "txn_amount_mismatch",
                "merchant_id": "merch_mismatch",
                "amount": 50.00,
                "currency": "USD",
                "status": "SETTLED",
                "gateway_timestamp": "2026-01-01T10:20:00Z",
                "processor_ref": "gw_mismatch"
            },
            "bank_data": {
                "processor_ref": "gw_mismatch",
                "settlement_id": "set_mismatch",
                "amount": 55.00,
                "status": "SETTLED",
                "bank_timestamp": "2026-01-01T14:15:00Z",
                "settlement_date": "2026-01-02"
            },
            "ledger_data": {
                "transaction_id": "txn_amount_mismatch",
                "ledger_id": "led_mismatch",
                "account": "acc_mismatch",
                "amount": 60.00,
                "entry_type": "CREDIT",
                "posted_date": "2026-01-02",
                "reconciled": True
            },
            "duplicate_gateway_transactions": [],
            "anomalies": ["Amount mismatch across sources: gateway: $50.00, bank: $55.00, ledger: $60.00"],
            "confidence": 0.4,
            "all_sources_present": True,
            "amount_consistent": False,
            "status_consistent": True,
            "status": "SETTLED"
        }

        mock_llm.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_amount_mismatch for merch_mismatch shows inconsistent amounts: $50.00 in gateway, $55.00 in bank, and $60.00 in ledger, suggesting a possible data entry error.",
            "exceptions": ["Amount mismatch across sources: gateway: $50.00, bank: $55.00, ledger: $60.00"],
            "confidence": 0.4
        }

        mock_validate.return_value = {
            "status": "SETTLED",
            "plain_english": "Transaction txn_amount_mismatch for merch_mismatch shows inconsistent amounts: $50.00 in gateway, $55.00 in bank, and $60.00 in ledger, suggesting a possible data entry error.",
            "exceptions": ["Amount mismatch across sources: gateway: $50.00, bank: $55.00, ledger: $60.00"],
            "confidence": 0.4
        }

        response = client.post("/investigate", json={"transaction_id": "txn_amount_mismatch"})

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "txn_amount_mismatch"
        assert data["status"] == "SETTLED"
        assert any("amount mismatch" in exc.lower() for exc in data["exceptions"])
        assert data["confidence"] < 0.5


def test_investigate_unknown_transaction():
    """Test investigation of completely unknown transaction"""
    with patch('app.services.investigator.investigate_transaction') as mock_investigate:

        mock_investigate.return_value = {
            "transaction_id": "txn_does_not_exist",
            "gateway_data": None,
            "bank_data": None,
            "ledger_data": None,
            "duplicate_gateway_transactions": [],
            "anomalies": ["Transaction not found in gateway"],
            "confidence": 0.0,
            "all_sources_present": False,
            "amount_consistent": False,
            "status_consistent": False,
            "status": "UNKNOWN"
        }

        response = client.post("/investigate", json={"transaction_id": "txn_does_not_exist"})

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "txn_does_not_exist"
        assert data["status"] == "UNKNOWN"
        assert data["confidence"] == 0.0
        assert any("not found in gateway" in exc.lower() for exc in data["exceptions"])
        assert "please verify the transaction id" in data["plain_english"].lower()


def test_investigate_invalid_request():
    """Test invalid request body"""
    response = client.post("/investigate", json={})  # Missing transaction_id
    assert response.status_code == 422  # Validation error

    response = client.post("/investigate", json={"transaction_id": ""})  # Empty string
    assert response.status_code == 422


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "SettleLens AI"
    assert data["status"] == "healthy"