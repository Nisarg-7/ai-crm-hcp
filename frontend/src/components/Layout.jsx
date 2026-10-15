import { useDispatch, useSelector } from 'react-redux';
import { Outlet } from 'react-router-dom';
import { logout } from '../store/authSlice';

export default function Layout() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);

  return (
    <div>
      <header className="topbar">
        <strong className="brand">AI-First CRM</strong>
        <div className="topbar-right">
          <span className="muted">Welcome, {user?.full_name}</span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => dispatch(logout())}
          >
            Logout
          </button>
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}