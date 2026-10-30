import { Home, MessageSquarePlus, Stethoscope, History, Activity } from 'lucide-react';
import { useSelector } from 'react-redux';
import { NavLink } from 'react-router-dom';

const LINKS = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/hcps', label: 'HCPs', icon: Stethoscope, end: false },
  { to: '/log-interaction', label: 'Log Interaction', icon: MessageSquarePlus, end: false },
  { to: '/interactions', label: 'My Interactions', icon: History, end: true },
];

function initials(name) {
  return (name || '?')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

export default function Sidebar({ open, onClose }) {
  const user = useSelector((state) => state.auth.user);

  return (
    <>
      <div
        className={`sidebar-backdrop ${open ? 'sidebar-backdrop-visible' : ''}`}
        onClick={onClose}
      />
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <span className="brand-mark">
            <Activity size={20} />
          </span>
          <span className="brand-name">HCP Sync</span>
        </div>

        <nav className="sidebar-nav">
          {LINKS.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className="side-link" onClick={onClose}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-user">
          <span className="avatar">{initials(user?.full_name)}</span>
          <div className="sidebar-user-text">
            <strong>{user?.full_name}</strong>
            <span className="muted">{user?.territory || 'No territory'}</span>
          </div>
        </div>
      </aside>
    </>
  );
}