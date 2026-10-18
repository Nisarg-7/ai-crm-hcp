import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import {
  fetchInteractionById,
  resetUpdate,
  updateInteraction,
} from '../store/interactionsSlice';
import { fetchProducts } from '../store/productsSlice';

const TYPES = [
  { value: 'visit', label: 'Visit' },
  { value: 'call', label: 'Call' },
  { value: 'email', label: 'Email' },
  { value: 'conference', label: 'Conference' },
];

const SENTIMENTS = [
  { value: '', label: 'Not specified' },
  { value: 'positive', label: 'Positive' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'negative', label: 'Negative' },
];

function toInputDateTime(iso) {
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function EditForm({ interaction }) {
  const dispatch = useDispatch();
  const products = useSelector((state) => state.products);
  const { updateStatus, updateError } = useSelector((state) => state.interactions);

  const [type, setType] = useState(interaction.interaction_type);
  const [date, setDate] = useState(toInputDateTime(interaction.interaction_date));
  const [sentiment, setSentiment] = useState(interaction.sentiment || '');
  const [productIds, setProductIds] = useState(interaction.products.map((p) => p.id));
  const [summary, setSummary] = useState(interaction.summary || '');
  const [notes, setNotes] = useState(interaction.notes || '');
  const [formError, setFormError] = useState('');

  const saving = updateStatus === 'loading';

  const toggleProduct = (id) => {
    setProductIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError('');
    dispatch(resetUpdate());

    if (!date) {
      setFormError('Please enter the date and time of the interaction.');
      return;
    }

    const changes = {
      interaction_type: type,
      interaction_date: new Date(date).toISOString(),
      sentiment: sentiment || null,
      summary: summary.trim() || null,
      notes: notes.trim() || null,
      product_ids: productIds,
    };

    dispatch(updateInteraction({ id: interaction.id, changes }));
  };

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      {updateStatus === 'succeeded' && (
        <div className="success-box">
          Changes saved. <Link to={`/hcps/${interaction.hcp_id}`}>Back to history</Link>
        </div>
      )}

      <label>HCP</label>
      <p className="readonly-value">
        {interaction.hcp.full_name}
        {interaction.hcp.specialty ? ` (${interaction.hcp.specialty})` : ''}
      </p>

      <div className="form-row">
        <div className="form-col">
          <label htmlFor="type">Interaction type *</label>
          <select id="type" value={type} onChange={(e) => setType(e.target.value)} disabled={saving}>
            {TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div className="form-col">
          <label htmlFor="date">Date and time *</label>
          <input id="date" type="datetime-local" value={date} onChange={(e) => setDate(e.target.value)} disabled={saving} />
        </div>
        <div className="form-col">
          <label htmlFor="sentiment">HCP sentiment</label>
          <select id="sentiment" value={sentiment} onChange={(e) => setSentiment(e.target.value)} disabled={saving}>
            {SENTIMENTS.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      <label>Products discussed</label>
      <div className="checkbox-list">
        {products.list.map((p) => (
          <label key={p.id} className="checkbox-item">
            <input
              type="checkbox"
              checked={productIds.includes(p.id)}
              onChange={() => toggleProduct(p.id)}
              disabled={saving}
            />
            {p.name}
          </label>
        ))}
      </div>

      <label htmlFor="summary">Summary</label>
      <textarea id="summary" rows={3} maxLength={2000} value={summary} onChange={(e) => setSummary(e.target.value)} disabled={saving} />

      <label htmlFor="notes">Notes</label>
      <textarea id="notes" rows={3} maxLength={5000} value={notes} onChange={(e) => setNotes(e.target.value)} disabled={saving} />

      {interaction.follow_ups.length > 0 && (
        <>
          <label>Follow-ups (read-only)</label>
          <ul className="followups">
            {interaction.follow_ups.map((f) => (
              <li key={f.id}>
                {f.description}
                <span className={`badge badge-${f.status}`}>{f.status}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {formError && <p className="bad error-text">{formError}</p>}
      {updateStatus === 'failed' && <p className="bad error-text">{updateError}</p>}

      <button type="submit" className="btn" disabled={saving}>
        {saving ? 'Saving...' : 'Save changes'}
      </button>
    </form>
  );
}

export default function EditInteractionPage() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { current, currentStatus, currentError } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(resetUpdate());
    dispatch(fetchInteractionById(id));
    dispatch(fetchProducts());
  }, [id, dispatch]);

  if (currentStatus === 'loading' || currentStatus === 'idle') {
    return <p className="muted">Loading interaction...</p>;
  }

  if (currentStatus === 'failed') {
    return (
      <div>
        <p className="bad">{currentError}</p>
        <Link to="/interactions">Back to My Interactions</Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Edit Interaction</h1>
      <p className="muted">Changes are saved only for the fields shown below.</p>
      <EditForm key={current.id} interaction={current} />
    </div>
  );
}