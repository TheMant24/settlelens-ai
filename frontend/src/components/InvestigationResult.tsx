import type { InvestigateResponse } from '../types/investigation';
import { StatusBadge } from './StatusBadge';
import { ConfidenceMeter } from './ConfidenceMeter';
import { ExceptionList } from './ExceptionList';
import { SourceDataCard } from './SourceDataCard';
import './InvestigationResult.css';

interface Props {
  result: InvestigateResponse;
}

// The backend emits this exact anomaly phrase when a source is truly missing.
// Using the full phrase (not just "ledger") avoids false positives like
// "Amount mismatch across sources: gateway: $50.00, bank: $55.00, ledger: $60.00".
// Constants are stored in lowercase so they can be matched against the lowercased
// exception text without a case-sensitivity bug.
const MISSING_GATEWAY = 'missing data from: gateway';
const MISSING_BANK = 'missing data from: bank';
const MISSING_LEDGER = 'missing data from: ledger';

export function InvestigationResult({ result }: Props) {
  const exceptionText = result.exceptions.join(' | ').toLowerCase();

  // Show a source as found unless the backend reports it as truly missing.
  // The backend investigator emits the "Missing data from: <source>" anomaly
  // only when that source has no record. Substring matching on the full phrase
  // prevents words like "ledger" appearing inside other anomaly text from
  // marking the source as missing.
  const gatewayFound = !exceptionText.includes(MISSING_GATEWAY);
  const bankFound = !exceptionText.includes(MISSING_BANK);
  const ledgerFound = !exceptionText.includes(MISSING_LEDGER);

  // Placeholder data while the API returns only the explanation fields.
  // Replace with real `data` once the backend exposes source records.
  const gatewayData = gatewayFound ? { transaction_id: result.transaction_id } : null;
  const bankData = bankFound ? { settlement_id: '—' } : null;
  const ledgerData = ledgerFound ? { ledger_id: '—' } : null;

  // Highlight anomalies visually
  const hasMismatch = exceptionText.includes('amount mismatch');
  const hasDuplicate = exceptionText.includes('duplicate');

  return (
    <div className="result">
      {/* Summary card */}
      <section className="summary-card">
        <div className="summary-top">
          <div className="summary-txn">
            <span className="summary-txn-label">Transaction</span>
            <span className="summary-txn-id">{result.transaction_id}</span>
          </div>
          <div className="summary-status">
            <StatusBadge status={result.status} />
          </div>
        </div>

        {/* Plain English explanation */}
        <div className="explanation-card">
          <div className="explanation-icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div className="explanation-content">
            <div className="explanation-label">AI Analysis</div>
            <div className="explanation-text">{result.plain_english}</div>
          </div>
        </div>

        {/* Confidence */}
        <div className="summary-footer">
          <ConfidenceMeter confidence={result.confidence} />
          <div />
        </div>
      </section>

      {/* Sources flow */}
      <section className="sources-section">
        <div className="sources-header">
          <span className="sources-title">Data Sources</span>
          <span className="sources-arrow">Gateway → Bank → Ledger</span>
        </div>
        <div className="sources-grid">
          <SourceDataCard
            kind="gateway"
            title="Gateway"
            subtitle="Payment processor"
            found={gatewayFound}
            data={gatewayData || undefined}
            hasAnomaly={hasDuplicate}
          />
          <SourceDataCard
            kind="bank"
            title="Bank"
            subtitle="Settlement record"
            found={bankFound}
            data={bankData || undefined}
            hasAnomaly={hasMismatch}
          />
          <SourceDataCard
            kind="ledger"
            title="Ledger"
            subtitle="Internal accounting"
            found={ledgerFound}
            data={ledgerData || undefined}
            hasAnomaly={hasMismatch && ledgerFound}
          />
        </div>
      </section>

      {/* Exceptions */}
      <ExceptionList exceptions={result.exceptions} />
    </div>
  );
}