import { LogOut, Menu, Moon, Sun } from 'lucide-react';
import { useDispatch } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { logout } from '../store/authSlice';

function pageTitle(pathname) {
  if (pathname === '/') return 'Home';
  if (pathname === '/hcps') return 'HCPs';
  if (pathname.startsWith('/hcps/')) return 'HCP Details';
  if (pathname === '/log-interaction') return 'Log Interaction';
  if (pathname === '/interactions') return 'My Interactions';
  if (pathname.endsWith('/edit')) return 'Edit Interaction';
  return 'HCP Sync';
}

export default function Topbar({ theme, onToggleTheme, onMenu }) {
  const dispatch = useDispatch();
  const { pathname } = useLocation();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          type="button"
          className="icon-btn menu-btn"
          onClick={onMenu}
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
        <h2 className="topbar-title">{pageTitle(pathname)}</h2>
      </div>

      <div className="topbar-right">
        <button
          type="button"
          className="icon-btn"
          onClick={onToggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button
          type="button"
          className="icon-btn"
          onClick={() => dispatch(logout())}
          aria-label="Log out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}