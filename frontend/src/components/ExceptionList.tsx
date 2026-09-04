import './ExceptionList.css';

interface Props {
  exceptions: string[];
}

const ERROR_KEYWORDS = ['not found', 'failed', 'error', 'mismatch', 'conflict'];
const WARNING_KEYWORDS = ['missing', 'insufficient', 'partial', 'uncertain', 'duplicate'];

function classifyException(text: string): 'error' | 'warning' | 'info' {
  const lower = text.toLowerCase();
  if (ERROR_KEYWORDS.some((kw) => lower.includes(kw))) return 'error';
  if (WARNING_KEYWORDS.some((kw) => lower.includes(kw))) return 'warning';
  return 'info';
}

export function ExceptionList({ exceptions }: Props) {
  const hasExceptions = exceptions.length > 0;
  return (
    <section className="exceptions">
      <div className="exceptions-header">
        <span className="exceptions-title">Exceptions & Anomalies</span>
        <span className={`exceptions-count ${hasExceptions ? '' : 'zero'}`}>
          {exceptions.length}
        </span>
      </div>

      {hasExceptions ? (
        <ul className="exceptions-list">
          {exceptions.map((exc, idx) => {
            const severity = classifyException(exc);
            return (
              <li key={idx} className={`exception-item severity-${severity}`}>
                <span className={`exception-icon ${severity}`} aria-hidden="true">
                  {severity === 'error' ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="15" y1="9" x2="9" y2="15" />
                      <line x1="9" y1="9" x2="15" y2="15" />
                    </svg>
                  ) : severity === 'warning' ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                      <line x1="12" y1="9" x2="12" y2="13" />
                      <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="12" y1="16" x2="12" y2="12" />
                      <line x1="12" y1="8" x2="12.01" y2="8" />
                    </svg>
                  )}
                </span>
                <span>{exc}</span>
              </li>
            );
          })}
        </ul>
      ) : (
        <div className="exceptions-empty">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span>No exceptions — all data sources agree</span>
        </div>
      )}
    </section>
  );
}