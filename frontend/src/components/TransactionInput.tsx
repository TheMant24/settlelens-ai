import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import './TransactionInput.css';

interface Props {
  onInvestigate: (transactionId: string) => void;
  isLoading: boolean;
}

const EXAMPLES: { id: string; label: string; tone: 'success' | 'warning' | 'error' | 'info' | 'muted' }[] = [
  { id: 'txn_success', label: 'Successful', tone: 'success' },
  { id: 'txn_delayed_bank', label: 'Delayed', tone: 'info' },
  { id: 'txn_failed', label: 'Failed', tone: 'error' },
  { id: 'txn_missing_ledger', label: 'Missing Ledger', tone: 'warning' },
  { id: 'txn_amount_mismatch', label: 'Amount Mismatch', tone: 'warning' },
  { id: 'txn_duplicate_1', label: 'Duplicates', tone: 'warning' },
  { id: 'txn_unknown', label: 'Unknown ID', tone: 'muted' },
];

export function TransactionInput({ onInvestigate, isLoading }: Props) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onInvestigate(trimmed);
  };

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      submit();
    }
  };

  const useExample = (id: string) => {
    if (isLoading) return;
    setValue(id);
    onInvestigate(id);
  };

  return (
    <section className="investigator">
      <h2 className="investigator-title">Investigate a Transaction</h2>
      <p className="investigator-subtitle">
        Enter a transaction ID to trace it across gateway, bank, and ledger systems
      </p>

      <div className="input-row">
        <div className="input-field">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKey}
            placeholder="e.g. txn_success"
            disabled={isLoading}
            spellCheck={false}
            autoComplete="off"
            aria-label="Transaction ID"
          />
        </div>
        <button
          className="investigate-btn"
          onClick={submit}
          disabled={isLoading || !value.trim()}
          type="button"
        >
          {isLoading ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Investigating…
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Investigate
            </>
          )}
        </button>
      </div>

      <div className="examples">
        <div className="examples-label">Try a sample transaction</div>
        <div className="examples-grid">
          {EXAMPLES.map((ex) => (
            <button
              key={ex.id}
              type="button"
              className="example-chip"
              onClick={() => useExample(ex.id)}
              disabled={isLoading}
            >
              <span className={`example-chip-label ${ex.tone}`}>{ex.label}</span>
              <span>{ex.id}</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}