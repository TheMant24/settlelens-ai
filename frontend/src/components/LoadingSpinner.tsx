import './LoadingSpinner.css';

interface Props {
  transactionId: string;
}

export function LoadingSpinner({ transactionId }: Props) {
  return (
    <div className="loading" role="status" aria-live="polite">
      <div className="loading-spinner" aria-hidden="true" />
      <div className="loading-text">Investigating transaction…</div>
      <div className="loading-subtext">{transactionId}</div>
    </div>
  );
}