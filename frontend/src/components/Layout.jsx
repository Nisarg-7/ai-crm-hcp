import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import useTheme from '../hooks/useTheme';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function Layout() {
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="app-main">
        <Topbar
          theme={theme}
          onToggleTheme={toggleTheme}
          onMenu={() => setMenuOpen(true)}
        />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}