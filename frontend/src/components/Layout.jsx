import { useDispatch, useSelector } from 'react-redux';
import { NavLink, Outlet } from 'react-router-dom';
import { logout } from '../store/authSlice';

export default function Layout() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);

  return (
    <div>
      <header className="topbar">
        <div className="topbar-left">
          <strong className="brand">AI-First CRM</strong>
          <nav className="nav">
            <NavLink to="/" end>Home</NavLink>
            <NavLink to="/hcps">HCPs</NavLink>
            <NavLink to="/log-interaction">Log Interaction</NavLink>
          </nav>
        </div>
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