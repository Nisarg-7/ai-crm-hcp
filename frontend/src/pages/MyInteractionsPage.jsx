import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchInteractions } from '../store/interactionsSlice';

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export default function MyInteractionsPage() {
  const dispatch = useDispatch();
  const { list, status, error } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  return (
    <div>
      <h1>My Interactions</h1>
      <p className="muted">Everything you have logged, newest first.</p>

      {status === 'loading' && <p className="muted">Loading interactions...</p>}
      {status === 'failed' && <p className="bad">{error}</p>}
      {status === 'succeeded' && list.length === 0 && (
        <p className="muted">
          You haven't logged any interactions yet.{' '}
          <Link to="/log-interaction">Log your first one</Link>
        </p>
      )}

      {list.map((item) => (
        <div key={item.id} className="card interaction-card">
          <div className="interaction-top">
            <Link to={`/hcps/${item.hcp_id}`} className="hcp-link">
              {item.hcp.full_name}
            </Link>
            <strong>
              {item.interaction_type.charAt(0).toUpperCase() + item.interaction_type.slice(1)}
            </strong>
            <span className="muted">{formatDate(item.interaction_date)}</span>
            {item.sentiment && (
              <span className={`badge badge-${item.sentiment}`}>{item.sentiment}</span>
            )}
            {item.source === 'ai_chat' && <span className="badge badge-ai">AI chat</span>}
            <Link to={`/interactions/${item.id}/edit`} className="edit-link">Edit</Link>
          </div>

          {item.summary && <p>{item.summary}</p>}

          {item.products.length > 0 && (
            <p className="muted">
              Products: {item.products.map((p) => p.name).join(', ')}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}