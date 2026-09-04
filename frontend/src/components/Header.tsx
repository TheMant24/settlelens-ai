import { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';
import './Header.css';

type HealthState = 'checking' | 'online' | 'offline';

export function Header() {
  const [health, setHealth] = useState<HealthState>('checking');

  useEffect(() => {
    let cancelled = false;
    let timeoutId: number | undefined;

    async function check() {
      const ok = await checkHealth();
      if (!cancelled) {
        setHealth(ok ? 'online' : 'offline');
        // Re-check every 15s
        timeoutId = window.setTimeout(check, 15000);
      }
    }

    check();
    return () => {
      cancelled = true;
      if (timeoutId) window.clearTimeout(timeoutId);
    };
  }, []);

  const statusText = {
    checking: 'Connecting…',
    online: 'Backend online',
    offline: 'Backend offline',
  }[health];

  return (
    <header className="header">
      <div className="header-inner">
        <div className="brand">
          <div className="brand-logo" aria-hidden="true">S</div>
          <div>
            <div className="brand-name">SettleLens AI</div>
            <div className="brand-tagline">Settlement Investigation</div>
          </div>
        </div>
        <div className="header-status" role="status" aria-live="polite">
          <span className={`status-dot ${health}`} aria-hidden="true" />
          <span>{statusText}</span>
        </div>
      </div>
    </header>
  );
}