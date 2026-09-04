import { useState } from 'react';
import { Header } from './components/Header';
import { TransactionInput } from './components/TransactionInput';
import { InvestigationResult } from './components/InvestigationResult';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorState } from './components/ErrorState';
import { EmptyState } from './components/EmptyState';
import { investigateTransaction, ApiError } from './services/api';
import type { InvestigateResponse } from './types/investigation';
import './App.css';

type InvestigationState =
  | { kind: 'idle' }
  | { kind: 'loading'; transactionId: string }
  | { kind: 'success'; data: InvestigateResponse }
  | { kind: 'error'; title: string; message: string; hint?: string };

function App() {
  const [state, setState] = useState<InvestigationState>({ kind: 'idle' });

  async function handleInvestigate(transactionId: string) {
    setState({ kind: 'loading', transactionId });

    try {
      const data = await investigateTransaction(transactionId);
      setState({ kind: 'success', data });
    } catch (err) {
      if (err instanceof ApiError) {
        const isNetwork = err.status === 0;
        setState({
          kind: 'error',
          title: isNetwork ? 'Cannot reach investigation service' : 'Investigation failed',
          message: err.detail,
          hint: isNetwork
            ? 'Make sure the backend server is running on http://localhost:8000'
            : undefined,
        });
      } else {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setState({
          kind: 'error',
          title: 'Unexpected error',
          message,
        });
      }
    }
  }

  return (
    <div className="app">
      <Header />

      <main className="main">
        <section className="hero">
          <div className="hero-badge">
            <span aria-hidden="true">◆</span>
            Origin Hackathon · PS-8
          </div>
          <h1 className="hero-title">Trace any transaction across your entire settlement stack</h1>
          <p className="hero-subtitle">
            SettleLens AI correlates gateway, bank, and ledger data, explains settlement status in
            plain English, and tells you honestly when something doesn't add up.
          </p>
        </section>

        <TransactionInput
          onInvestigate={handleInvestigate}
          isLoading={state.kind === 'loading'}
        />

        {state.kind === 'idle' && <EmptyState />}
        {state.kind === 'loading' && <LoadingSpinner transactionId={state.transactionId} />}
        {state.kind === 'success' && <InvestigationResult result={state.data} />}
        {state.kind === 'error' && (
          <ErrorState title={state.title} message={state.message} hint={state.hint} />
        )}
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <span>SettleLens AI · Settlement Investigation</span>
          <span className="footer-tag">Built for Origin Hackathon</span>
        </div>
      </footer>
    </div>
  );
}

export default App;