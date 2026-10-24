import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { clearChat, retryLast, sendMessage } from '../store/chatSlice';

const EXAMPLES = [
  'Find me cardiologists',
  'I met Dr. Kapoor today, he was positive about CardioSafe. Remind me to send the safety PDF by Friday.',
  'What happened in my past meetings with Dr. Iyer?',
  'Change my last call with Dr. Iyer to neutral',
];

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, status, error } = useSelector((state) => state.chat);
  const [text, setText] = useState('');
  const bottomRef = useRef(null);

  const loading = status === 'loading';

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, status]);

  const submit = () => {
    const value = text.trim();
    if (!value || loading) return;
    setText('');
    dispatch(sendMessage(value));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="card chat-card">
      <div className="chat-header">
        <strong>AI Assistant</strong>
        <button
          type="button"
          className="btn btn-secondary btn-small"
          onClick={() => dispatch(clearChat())}
          disabled={loading || messages.length === 0}
        >
          New chat
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p className="muted">
              Describe your interaction in plain English, or ask about your HCPs. Try:
            </p>
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="example-chip"
                onClick={() => setText(example)}
              >
                {example}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, index) => (
          <div key={index} className={`bubble-row bubble-row-${m.role}`}>
            <div className={`bubble bubble-${m.role}`}>{m.content}</div>
          </div>
        ))}

        {loading && (
          <div className="bubble-row bubble-row-assistant">
            <div className="bubble bubble-assistant typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        {status === 'failed' && (
          <div className="chat-error">
            <span>{error}</span>
            <button
              type="button"
              className="btn btn-small"
              onClick={() => dispatch(retryLast())}
            >
              Retry
            </button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          rows={2}
          value={text}
          maxLength={4000}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for a new line)"
          disabled={loading}
        />
        <button
          type="button"
          className="btn"
          onClick={submit}
          disabled={loading || !text.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}