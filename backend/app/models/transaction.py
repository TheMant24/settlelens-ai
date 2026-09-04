from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer
from ..database import Base
from datetime import datetime

class GatewayTransaction(Base):
    __tablename__ = "gateway_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    merchant_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    gateway_timestamp = Column(DateTime)
    processor_ref = Column(String, index=True)

class BankSettlement(Base):
    __tablename__ = "bank_settlements"

    id = Column(Integer, primary_key=True, index=True)
    processor_ref = Column(String, index=True)
    settlement_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    status = Column(String)
    bank_timestamp = Column(DateTime)
    settlement_date = Column(String)  # Storing as string for simplicity

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)
    ledger_id = Column(String, unique=True, index=True)
    account = Column(String)
    amount = Column(Float)
    entry_type = Column(String)
    posted_date = Column(String)  # Storing as string for simplicity
    reconciled = Column(Boolean)