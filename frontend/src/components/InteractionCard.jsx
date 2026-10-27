import { Link } from 'react-router-dom';

const LABELS = {
  logged: 'Interaction logged',
  edited: 'Interaction updated',
  follow_up_added: 'Follow-up added',
};

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export default function InteractionCard({ card }) {
  const type = card.interaction_type.charAt(0).toUpperCase() + card.interaction_type.slice(1);

  return (
    <div className="result-card">
      <div className="result-card-top">
        <strong>{LABELS[card.action] || 'Interaction'}</strong>
        <span className="muted">#{card.interaction_id}</span>
      </div>
      <p className="result-line">
        {type} with <strong>{card.hcp_name}</strong> on {formatDate(card.interaction_date)}
      </p>
      {card.sentiment && (
        <p className="result-line">
          Sentiment: <span className={`badge badge-${card.sentiment}`}>{card.sentiment}</span>
        </p>
      )}
      {card.products.length > 0 && (
        <p className="result-line">Products: {card.products.join(', ')}</p>
      )}
      {card.follow_ups.length > 0 && (
        <ul className="followups">
          {card.follow_ups.map((f, index) => (
            <li key={index}>{f}</li>
          ))}
        </ul>
      )}
      <div className="result-links">
        <Link to={`/hcps/${card.hcp_id}`}>View history</Link>
        <Link to={`/interactions/${card.interaction_id}/edit`}>Edit</Link>
      </div>
    </div>
  );
}