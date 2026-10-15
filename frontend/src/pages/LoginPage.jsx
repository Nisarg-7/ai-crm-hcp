import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { login } from '../store/authSlice';

export default function LoginPage() {
  const dispatch = useDispatch();
  const { token, status, error } = useSelector((state) => state.auth);
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
      <form className="card login-card" onSubmit={handleSubmit}>
        <h1>AI-First CRM</h1>
        <p className="muted">Sign in to log your HCP interactions</p>

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

        <p className="muted hint">
          Demo login: rep1@democrm.com / Demo@1234
        </p>
      </form>
    </div>
  );
}