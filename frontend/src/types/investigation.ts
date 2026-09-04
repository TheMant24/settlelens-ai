// Types matching the backend Pydantic schemas

export type SettlementStatus = 'SETTLED' | 'PENDING' | 'FAILED' | 'PARTIAL' | 'UNKNOWN';

export interface InvestigateRequest {
  transaction_id: string;
}

export interface InvestigateResponse {
  transaction_id: string;
  status: SettlementStatus;
  plain_english: string;
  exceptions: string[];
  confidence: number;
}

export interface ErrorResponse {
  detail: string;
}

// Source data structure - what comes back from each data source client
export interface GatewayData {
  transaction_id: string;
  merchant_id: string;
  amount: number;
  currency: string;
  status: string;
  gateway_timestamp: string;
  processor_ref: string;
}

export interface BankData {
  processor_ref: string;
  settlement_id: string;
  amount: number;
  status: string;
  bank_timestamp: string;
  settlement_date: string;
}

export interface LedgerData {
  transaction_id: string;
  ledger_id: string;
  account: string;
  amount: number;
  entry_type: string;
  posted_date: string;
  reconciled: boolean;
}

// Extended response type with source data (would need backend changes for full impl)
export interface InvestigateResponseWithSources extends InvestigateResponse {
  sources?: {
    gateway?: GatewayData | null;
    bank?: BankData | null;
    ledger?: LedgerData | null;
  };
}