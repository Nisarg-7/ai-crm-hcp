import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHealth } from './store/healthSlice';

export default function App() {
  const dispatch = useDispatch();
  const { data, status, error } = useSelector((state) => state.health);

  useEffect(() => {
    dispatch(fetchHealth());
  }, [dispatch]);

  return (
    <div className="page">
      <h1>AI-First CRM: HCP Module</h1>
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