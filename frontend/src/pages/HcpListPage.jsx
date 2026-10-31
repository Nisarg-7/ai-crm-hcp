import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import useDebounce from '../hooks/useDebounce';
import { fetchHcps } from '../store/hcpsSlice';

function initials(name) {
  return (name || '?')
    .replace(/^Dr\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

export default function HcpListPage() {
  const dispatch = useDispatch();
  const { list, listStatus, listError } = useSelector((state) => state.hcps);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    dispatch(fetchHcps(debouncedSearch));
  }, [debouncedSearch, dispatch]);

  return (
    <div>
      <h1>Healthcare Professionals</h1>
      <p className="muted">Search by name, specialty, city or hospital.</p>

      <div className="search-wrap">
        <Search size={16} className="search-icon" />
        <input
          type="search"
          className="search-input search-input-icon"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, specialty, city or hospital"
        />
      </div>

      {listStatus === 'loading' && list.length === 0 && (
        <div className="hcp-grid">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="skeleton" style={{ height: 110 }} />
          ))}
        </div>
      )}

      {listStatus === 'failed' && <p className="bad">{listError}</p>}

      {listStatus === 'succeeded' && list.length === 0 && (
        <p className="muted">No HCPs match "{debouncedSearch}".</p>
      )}

      <div className="hcp-grid">
        {list.map((hcp) => (
          <Link key={hcp.id} to={`/hcps/${hcp.id}`} className="card hcp-card">
            <div className="hcp-card-top">
              <span className="hcp-avatar">{initials(hcp.full_name)}</span>
              <div>
                <h3>{hcp.full_name}</h3>
                <p className="hcp-specialty">{hcp.specialty || 'Specialty not set'}</p>
              </div>
            </div>
            <p className="muted">
              {[hcp.organization, hcp.city].filter(Boolean).join(', ')}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}