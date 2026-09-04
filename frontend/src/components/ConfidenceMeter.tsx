import './ConfidenceMeter.css';

interface Props {
  confidence: number;
}

function classify(c: number): 'high' | 'medium' | 'low' {
  if (c >= 0.8) return 'high';
  if (c >= 0.5) return 'medium';
  return 'low';
}

function describe(c: number): string {
  if (c >= 0.9) return 'Very high confidence — all data sources agree';
  if (c >= 0.7) return 'High confidence — minor uncertainty';
  if (c >= 0.5) return 'Moderate confidence — some anomalies present';
  if (c >= 0.3) return 'Low confidence — significant anomalies';
  if (c > 0) return 'Very low confidence — major data gaps';
  return 'No data found';
}

export function ConfidenceMeter({ confidence }: Props) {
  const cls = classify(confidence);
  const pct = Math.round(confidence * 100);
  return (
    <div className="confidence">
      <div className="confidence-header">
        <span className="confidence-label">AI Confidence</span>
        <span className="confidence-value">{pct}%</span>
      </div>
      <div className="confidence-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div className={`confidence-fill ${cls}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="confidence-detail">{describe(confidence)}</div>
    </div>
  );
}