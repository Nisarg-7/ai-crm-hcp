import { useState } from 'react';
import ChatPanel from '../components/ChatPanel';
import LogInteractionForm from '../components/LogInteractionForm';

export default function LogInteractionPage() {
  const [tab, setTab] = useState('chat');

  return (
    <div>
      <h1>Log Interaction</h1>
      <p className="muted">Record a meeting, call or email with a Healthcare Professional.</p>

      <div className="tabs">
        <button
          type="button"
          className={`tab ${tab === 'chat' ? 'tab-active' : ''}`}
          onClick={() => setTab('chat')}
        >
          AI Conversation
        </button>
        <button
          type="button"
          className={`tab ${tab === 'form' ? 'tab-active' : ''}`}
          onClick={() => setTab('form')}
        >
          Structured Form
        </button>
      </div>

      <div style={{ display: tab === 'chat' ? 'block' : 'none' }}>
        <ChatPanel />
      </div>
      <div style={{ display: tab === 'form' ? 'block' : 'none' }}>
        <LogInteractionForm />
      </div>
    </div>
  );
}