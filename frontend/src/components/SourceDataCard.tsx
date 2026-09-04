import type { ReactNode } from 'react';
import './SourceDataCard.css';

export type SourceKind = 'gateway' | 'bank' | 'ledger';

interface Props {
  kind: SourceKind;
  title: string;
  subtitle: string;
  found: boolean;
  data?: Record<string, ReactNode> | null;
  hasAnomaly?: boolean;
  /** Optional keys to highlight (e.g. mismatched amount) */
  highlightKeys?: string[];
}

const ICONS: Record<SourceKind, ReactNode> = {
  gateway: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="14" rx="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  ),
  bank: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 21h18" />
      <path d="M3 10h18" />
      <path d="M5 6l7-3 7 3" />
      <path d="M4 10v11" />
      <path d="M20 10v11" />
      <path d="M8 14v3" />
      <path d="M12 14v3" />
      <path d="M16 14v3" />
    </svg>
  ),
  ledger: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      <line x1="8" y1="7" x2="16" y2="7" />
      <line x1="8" y1="11" x2="16" y2="11" />
    </svg>
  ),
};

const AMOUNT_KEYS = ['amount'];

export function SourceDataCard({
  kind,
  title,
  subtitle,
  found,
  data,
  hasAnomaly,
  highlightKeys = [],
}: Props) {
  const classes = ['source-card', kind];
  if (!found) classes.push('missing');
  if (hasAnomaly && found) classes.push('has-anomaly');

  return (
    <div className={classes.join(' ')}>
      <div className="source-header">
        <div className={`source-icon ${found ? kind : 'muted'}`} aria-hidden="true">
          {ICONS[kind]}
        </div>
        <div style={{ flex: 1 }}>
          <div className="source-title">{title}</div>
          <div className="source-subtitle">{subtitle}</div>
        </div>
        <div className={`source-status ${found ? 'found' : 'missing'}`}>
          {found ? 'Found' : 'Missing'}
        </div>
      </div>

      {found && data ? (
        <div className="data-list">
          {Object.entries(data).map(([key, value]) => {
            const isAmount = AMOUNT_KEYS.includes(key);
            const isHighlight = highlightKeys.includes(key);
            const valueClasses = ['data-value'];
            if (isHighlight) valueClasses.push('highlight');
            if (isAmount) valueClasses.push('amount');
            return (
              <div key={key} className="data-row">
                <span className="data-label">{key.replace(/_/g, ' ')}</span>
                <span className={valueClasses.join(' ')}>{value}</span>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="missing-message">
          <div className="missing-message-icon" aria-hidden="true">∅</div>
          <div>No data found in this source</div>
        </div>
      )}
    </div>
  );
}