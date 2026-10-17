import { useState } from 'react';
import LogInteractionForm from '../components/LogInteractionForm';

export default function LogInteractionPage() {
  const [tab, setTab] = useState('form');

  return (
    <div>
      <h1>Log Interaction</h1>
      <p className="muted">Record a meeting, call or email with a Healthcare Professional.</p>

      <div className="tabs">
        <button
          type="button"
          className={`tab ${tab === 'form' ? 'tab-active' : ''}`}
          onClick={() => setTab('form')}
        >
          Structured Form
        </button>
        <button
          type="button"
          className="tab tab-disabled"
          disabled
          title="Coming in Week 2"
        >
          AI Conversation (coming soon)
        </button>
      </div>

      {tab === 'form' && <LogInteractionForm />}
    </div>
  );
}