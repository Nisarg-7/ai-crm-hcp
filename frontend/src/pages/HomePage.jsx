import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchDashboard } from '../store/dashboardSlice';
import { fetchHealth } from '../store/healthSlice';

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export default function HomePage() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const { data, status, error } = useSelector((state) => state.dashboard);
  const health = useSelector((state) => state.health);

  useEffect(() => {
    dispatch(fetchDashboard());
    dispatch(fetchHealth());
  }, [dispatch]);

  return (
    <div>
      <h1>Welcome, {user?.full_name}</h1>
      <p className="muted">Territory: {user?.territory || 'Not assigned'}</p>

      <div className="quick-actions">
        <Link to="/log-interaction" className="btn quick-btn">Log an interaction</Link>
        <Link to="/hcps" className="btn btn-secondary quick-btn">Browse HCPs</Link>
      </div>

      {status === 'loading' && !data && <p className="muted">Loading dashboard...</p>}
      {status === 'failed' && <p className="bad">{error}</p>}

      {data && (
        <>
          <div className="stat-grid">
            <div className="card stat">
              <span className="stat-number">{data.counts.total_interactions}</span>
              <span className="muted">Total interactions</span>
            </div>
            <div className="card stat">
              <span className="stat-number">{data.counts.last_7_days}</span>
              <span className="muted">Last 7 days</span>
            </div>
            <div className="card stat">
              <span className="stat-number">{data.counts.open_follow_ups}</span>
              <span className="muted">Open follow-ups</span>
            </div>
          </div>

          <div className="dash-columns">
            <div className="card">
              <h2>Recent interactions</h2>
              {data.recent_interactions.length === 0 && (
                <p className="muted">Nothing logged yet.</p>
              )}
              {data.recent_interactions.map((i) => (
                <div key={i.id} className="dash-row">
                  <Link to={`/hcps/${i.hcp_id}`} className="hcp-link">{i.hcp_name}</Link>
                  <span className="muted">
                    {i.interaction_type} &middot; {formatDate(i.interaction_date)}
                  </span>
                  {i.sentiment && (
                    <span className={`badge badge-${i.sentiment}`}>{i.sentiment}</span>
                  )}
                  {i.source === 'ai_chat' && <span className="badge badge-ai">AI chat</span>}
                </div>
              ))}
              <p><Link to="/interactions">See all &rarr;</Link></p>
            </div>

            <div className="card">
              <h2>Open follow-ups</h2>
              {data.open_follow_ups.length === 0 && (
                <p className="muted">No open follow-ups.</p>
              )}
              {data.open_follow_ups.map((f) => (
                <div key={f.id} className="dash-row">
                  <span>{f.description}</span>
                  <span className="muted">
                    <Link to={`/hcps/${f.hcp_id}`} className="hcp-link">{f.hcp_name}</Link>
                    {' '}&middot; {f.due_date ? `due ${formatDate(f.due_date)}` : 'no due date'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <div className="card status-card">
        <strong>System status</strong>{' '}
        {health.status === 'succeeded' ? (
          <span>
            API <span className="ok">{health.data.status}</span> &middot; Database{' '}
            <span className={health.data.database === 'ok' ? 'ok' : 'bad'}>
              {health.data.database}
            </span>
          </span>
        ) : health.status === 'failed' ? (
          <span className="bad">{health.error}</span>
        ) : (
          <span className="muted">Checking...</span>
        )}
      </div>
    </div>
  );
}