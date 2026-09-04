#!/usr/bin/env python3
"""Debug script to check table creation"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.database import engine, Base
from app.models.transaction import GatewayTransaction, BankSettlement, LedgerEntry

print("Creating tables...")
Base.metadata.create_all(bind=engine)

print("Checking tables:")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables: {tables}")

for table in tables:
    print(f"\nTable: {table}")
    columns = inspector.get_columns(table)
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")