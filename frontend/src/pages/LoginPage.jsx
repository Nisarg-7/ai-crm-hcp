import { useState } from 'react';
import { Activity, Moon, Sun } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import useTheme from '../hooks/useTheme';
import { login } from '../store/authSlice';

export default function LoginPage() {
  const dispatch = useDispatch();
  const { token, status, error } = useSelector((state) => state.auth);
  const { theme, toggleTheme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  if (token) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(login({ email: email.trim(), password }));
  };

  const loading = status === 'loading';

  return (
    <div className="login-wrap">
      <button
        type="button"
        className="icon-btn login-theme"
        onClick={toggleTheme}
        aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <form className="card login-card" onSubmit={handleSubmit}>
        <div className="login-brand">
          <span className="brand-mark">
            <Activity size={20} />
          </span>
          <h1>HCP Sync</h1>
        </div>
        <p className="muted">AI-first CRM for life-science field reps</p>

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="rep1@democrm.com"
          required
          autoFocus
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Your password"
          required
        />

        {error && <p className="bad error-text">{error}</p>}

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign in'}
        </button>

        <div className="demo-box">
          Demo login: rep1@democrm.com / Demo@1234
        </div>
      </form>
    </div>
  );
}