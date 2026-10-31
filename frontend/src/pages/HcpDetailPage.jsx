import { useEffect } from 'react';
import { ArrowLeft, Building2, Mail, Phone } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import { fetchHcpById } from '../store/hcpsSlice';
import { fetchInteractions } from '../store/interactionsSlice';

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function initials(name) {
  return (name || '?')
    .replace(/^Dr\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

export default function HcpDetailPage() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { selected, selectedStatus, selectedError } = useSelector((state) => state.hcps);
  const { list, status, error } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchHcpById(id));
    dispatch(fetchInteractions(id));
  }, [id, dispatch]);

  if (selectedStatus === 'loading' || selectedStatus === 'idle') {
    return (
      <div>
        <div className="skeleton" style={{ height: 110, marginBottom: 24 }} />
        <div className="skeleton" style={{ height: 90 }} />
      </div>
    );
  }

  if (selectedStatus === 'failed') {
    return (
      <div>
        <p className="bad">{selectedError}</p>
        <Link to="/hcps" className="back-link">
          <ArrowLeft size={16} /> Back to HCP list
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link to="/hcps" className="back-link">
        <ArrowLeft size={16} /> Back to HCP list
      </Link>

      <div className="card hcp-header">
        <span className="hcp-avatar hcp-avatar-lg">{initials(selected.full_name)}</span>
        <div>
          <h1>{selected.full_name}</h1>
          <p className="hcp-specialty">{selected.specialty || 'Specialty not set'}</p>
          <p className="muted hcp-contact">
            <span>
              <Building2 size={14} />
              {[selected.organization, selected.city].filter(Boolean).join(', ') || 'No organization'}
            </span>
            <span>
              <Mail size={14} />
              {selected.email || 'No email'}
            </span>
            <span>
              <Phone size={14} />
              {selected.phone || 'No phone'}
            </span>
          </p>
        </div>
      </div>

      <h2>Interaction history</h2>

      {status === 'loading' && (
        <>
          <div className="skeleton" style={{ height: 90, marginBottom: 12 }} />
          <div className="skeleton" style={{ height: 90 }} />
        </>
      )}
      {status === 'failed' && <p className="bad">{error}</p>}
      {status === 'succeeded' && list.length === 0 && (
        <p className="muted">No interactions logged with this HCP yet.</p>
      )}

      {list.map((item) => (
        <div key={item.id} className="card interaction-card">
          <div className="interaction-top">
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
          {item.notes && <p className="muted">{item.notes}</p>}

          {item.products.length > 0 && (
            <p className="muted">
              Products: {item.products.map((p) => p.name).join(', ')}
            </p>
          )}

          {item.follow_ups.length > 0 && (
            <ul className="followups">
              {item.follow_ups.map((f) => (
                <li key={f.id}>
                  {f.description}
                  {f.due_date && <span className="muted"> (due {formatDate(f.due_date)})</span>}
                  <span className={`badge badge-${f.status}`}>{f.status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}