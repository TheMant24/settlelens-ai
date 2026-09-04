#!/usr/bin/env python3
"""Simple validation script to check if our modules can be imported"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    print("Testing imports...")

    # Test config
    from app.config import FREELLMAPI_API_KEY, DATABASE_URL
    print("✓ Config imported")

    # Test database
    from app.database import engine, Base, get_db
    print("✓ Database imported")

    # Test models
    from app.models.transaction import GatewayTransaction, BankSettlement, LedgerEntry
    print("✓ Models imported")

    # Test services
    from app.services.gateway_client import get_gateway_transaction
    from app.services.bank_client import get_bank_settlement_by_processor_ref
    from app.services.ledger_client import get_ledger_entry_by_transaction_id
    from app.services.investigator import investigate_transaction
    print("✓ Services imported")

    # Test data loader
    from app.services.data_loader import seed_database
    print("✓ Data loader imported")

    print("\n✅ All imports successful!")
    print(f"Database URL: {DATABASE_URL}")
    print(f"FreeLLMAPI Key present: {bool(FREELLMAPI_API_KEY)}")

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)