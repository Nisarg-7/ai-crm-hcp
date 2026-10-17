import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHealth } from '../store/healthSlice';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const { data, status, error } = useSelector((state) => state.health);

  useEffect(() => {
    dispatch(fetchHealth());
  }, [dispatch]);

  return (
    <div>
      <h1>Welcome, {user?.full_name}</h1>
      <p className="muted">Territory: {user?.territory || 'Not assigned'}</p>
            <p><Link to="/hcps">Browse HCPs &rarr;</Link></p>

            <p><Link to="/log-interaction">Log an interaction &rarr;</Link></p>

      <div className="card">
        <h2>System status</h2>
        {status === 'loading' && <p>Checking...</p>}
        {status === 'failed' && <p className="bad">{error}</p>}
        {status === 'succeeded' && (
          <>
            <p>API: <strong className="ok">{data.status}</strong></p>
            <p>
              Database:{' '}
              <strong className={data.database === 'ok' ? 'ok' : 'bad'}>
                {data.database}
              </strong>
            </p>
          </>
        )}
      </div>
    </div>
  );
}