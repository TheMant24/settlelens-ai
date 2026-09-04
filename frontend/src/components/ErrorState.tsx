import './ErrorState.css';

interface Props {
  title: string;
  message: string;
  hint?: string;
}

export function ErrorState({ title, message, hint }: Props) {
  return (
    <div className="error-state" role="alert">
      <div className="error-icon" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <div className="error-content">
        <div className="error-title">{title}</div>
        <div className="error-message">{message}</div>
        {hint && <div className="error-hint">{hint}</div>}
      </div>
    </div>
  );
}