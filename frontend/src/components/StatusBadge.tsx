import type { SettlementStatus } from '../types/investigation';
import './StatusBadge.css';

interface Props {
  status: SettlementStatus;
}

const LABELS: Record<SettlementStatus, string> = {
  SETTLED: 'Settled',
  PENDING: 'Pending',
  FAILED: 'Failed',
  PARTIAL: 'Partial',
  UNKNOWN: 'Unknown',
};

export function StatusBadge({ status }: Props) {
  const statusKey = status.toLowerCase() as SettlementStatus;
  return (
    <span className={`status-badge ${statusKey}`}>
      {LABELS[status] || status}
    </span>
  );
}