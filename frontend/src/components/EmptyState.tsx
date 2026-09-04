import './EmptyState.css';

export function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-illustration" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </div>
      <div className="empty-title">Ready to investigate</div>
      <div className="empty-text">
        Enter a transaction ID above or pick one of the sample scenarios to see how SettleLens
        correlates data across gateway, bank, and ledger systems.
      </div>
    </div>
  );
}