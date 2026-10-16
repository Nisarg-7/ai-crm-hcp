import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import useDebounce from '../hooks/useDebounce';
import { fetchHcps } from '../store/hcpsSlice';

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

      <input
        type="search"
        className="search-input"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by name, specialty, city or hospital"
      />

      {listStatus === 'loading' && list.length === 0 && (
        <p className="muted">Loading HCPs...</p>
      )}

      {listStatus === 'failed' && <p className="bad">{listError}</p>}

      {listStatus === 'succeeded' && list.length === 0 && (
        <p className="muted">No HCPs match "{debouncedSearch}".</p>
      )}

      <div className="hcp-grid">
        {list.map((hcp) => (
          <Link key={hcp.id} to={`/hcps/${hcp.id}`} className="card hcp-card">
            <h3>{hcp.full_name}</h3>
            <p className="hcp-specialty">{hcp.specialty || 'Specialty not set'}</p>
            <p className="muted">
              {[hcp.organization, hcp.city].filter(Boolean).join(', ')}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}