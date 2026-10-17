import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchHcps } from '../store/hcpsSlice';
import { createInteraction, resetCreate } from '../store/interactionsSlice';
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

function nowForInput() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function LogInteractionForm() {
  const dispatch = useDispatch();
  const hcps = useSelector((state) => state.hcps.list);
  const hcpsStatus = useSelector((state) => state.hcps.listStatus);
  const products = useSelector((state) => state.products);
  const { createStatus, createError, lastCreated } = useSelector(
    (state) => state.interactions
  );

  const [hcpId, setHcpId] = useState('');
  const [type, setType] = useState('visit');
  const [date, setDate] = useState(nowForInput());
  const [sentiment, setSentiment] = useState('');
  const [productIds, setProductIds] = useState([]);
  const [summary, setSummary] = useState('');
  const [notes, setNotes] = useState('');
  const [followUps, setFollowUps] = useState([]);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    dispatch(resetCreate());
    dispatch(fetchHcps(''));
    dispatch(fetchProducts());
  }, [dispatch]);

  const saving = createStatus === 'loading';

  const toggleProduct = (id) => {
    setProductIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const addFollowUp = () => {
    setFollowUps((prev) => [...prev, { description: '', due_date: '' }]);
  };

  const updateFollowUp = (index, field, value) => {
    setFollowUps((prev) =>
      prev.map((f, i) => (i === index ? { ...f, [field]: value } : f))
    );
  };

  const removeFollowUp = (index) => {
    setFollowUps((prev) => prev.filter((_, i) => i !== index));
  };

  const resetForm = () => {
    setHcpId('');
    setType('visit');
    setDate(nowForInput());
    setSentiment('');
    setProductIds([]);
    setSummary('');
    setNotes('');
    setFollowUps([]);
    setFormError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError('');

    if (!hcpId) {
      setFormError('Please select an HCP.');
      return;
    }
    if (!date) {
      setFormError('Please enter the date and time of the interaction.');
      return;
    }

    const payload = {
      hcp_id: Number(hcpId),
      interaction_type: type,
      interaction_date: new Date(date).toISOString(),
      sentiment: sentiment || null,
      summary: summary.trim() || null,
      notes: notes.trim() || null,
      source: 'form',
      product_ids: productIds,
      follow_ups: followUps
        .filter((f) => f.description.trim())
        .map((f) => ({
          description: f.description.trim(),
          due_date: f.due_date || null,
        })),
    };

    dispatch(createInteraction(payload))
      .unwrap()
      .then(() => resetForm())
      .catch(() => {});
  };

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      {createStatus === 'succeeded' && lastCreated && (
        <div className="success-box">
          Interaction logged for {lastCreated.hcp.full_name}.{' '}
          <Link to={`/hcps/${lastCreated.hcp_id}`}>View history</Link>
        </div>
      )}

      <label htmlFor="hcp">HCP *</label>
      <select
        id="hcp"
        value={hcpId}
        onChange={(e) => setHcpId(e.target.value)}
        disabled={saving}
      >
        <option value="">
          {hcpsStatus === 'loading' && hcps.length === 0
            ? 'Loading HCPs...'
            : 'Select an HCP'}
        </option>
        {hcps.map((h) => (
          <option key={h.id} value={h.id}>
            {h.full_name}
            {h.specialty ? ` (${h.specialty})` : ''}
          </option>
        ))}
      </select>

      <div className="form-row">
        <div className="form-col">
          <label htmlFor="type">Interaction type *</label>
          <select
            id="type"
            value={type}
            onChange={(e) => setType(e.target.value)}
            disabled={saving}
          >
            {TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-col">
          <label htmlFor="date">Date and time *</label>
          <input
            id="date"
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            disabled={saving}
          />
        </div>
        <div className="form-col">
          <label htmlFor="sentiment">HCP sentiment</label>
          <select
            id="sentiment"
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
            disabled={saving}
          >
            {SENTIMENTS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <label>Products discussed</label>
      {products.status === 'loading' && <p className="muted">Loading products...</p>}
      {products.status === 'failed' && <p className="bad">{products.error}</p>}
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
      <textarea
        id="summary"
        rows={3}
        maxLength={2000}
        value={summary}
        onChange={(e) => setSummary(e.target.value)}
        placeholder="What was discussed?"
        disabled={saving}
      />

      <label htmlFor="notes">Notes</label>
      <textarea
        id="notes"
        rows={3}
        maxLength={5000}
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Anything else worth remembering"
        disabled={saving}
      />

      <label>Follow-ups</label>
      {followUps.map((f, index) => (
        <div key={index} className="followup-row">
          <input
            type="text"
            value={f.description}
            onChange={(e) => updateFollowUp(index, 'description', e.target.value)}
            placeholder="e.g. Send clinical data PDF"
            maxLength={500}
            disabled={saving}
          />
          <input
            type="date"
            value={f.due_date}
            onChange={(e) => updateFollowUp(index, 'due_date', e.target.value)}
            disabled={saving}
          />
          <button
            type="button"
            className="btn btn-secondary btn-small"
            onClick={() => removeFollowUp(index)}
            disabled={saving}
          >
            Remove
          </button>
        </div>
      ))}
      <div>
        <button
          type="button"
          className="btn btn-secondary btn-small"
          onClick={addFollowUp}
          disabled={saving}
        >
          + Add follow-up
        </button>
      </div>

      {formError && <p className="bad error-text">{formError}</p>}
      {createStatus === 'failed' && <p className="bad error-text">{createError}</p>}

      <button type="submit" className="btn" disabled={saving}>
        {saving ? 'Saving...' : 'Log interaction'}
      </button>
    </form>
  );
}