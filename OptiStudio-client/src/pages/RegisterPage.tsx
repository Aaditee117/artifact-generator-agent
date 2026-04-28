import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const passwordRules = [
    { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
    { label: 'One uppercase letter (A-Z)', test: (p: string) => /[A-Z]/.test(p) },
    { label: 'One lowercase letter (a-z)', test: (p: string) => /[a-z]/.test(p) },
    { label: 'One digit (0-9)', test: (p: string) => /[0-9]/.test(p) },
    { label: 'One special character (!@#$...)', test: (p: string) => /[^a-zA-Z0-9]/.test(p) },
  ];

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await register(name, email, password, confirmPassword);
      if (result.success) {
        navigate('/verify-otp', { state: { email } });
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      const msg = err.response?.data?.message || err.response?.data?.errors?.join(' ') || 'Registration failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <img src="https://www.optimusinfo.com/wp-content/uploads/2014/11/optimusinfologo.png" alt="OptiStudio" />
        </div>
        <h2>Create Account</h2>
        <p className="auth-subtitle">Register to get started</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setPasswordFocused(true)}
              onBlur={() => setPasswordFocused(false)}
              placeholder="Enter a strong password"
              required
            />
            {(passwordFocused || password.length > 0) && (
              <ul className="password-rules">
                {passwordRules.map((rule, idx) => (
                  <li key={idx} className={rule.test(password) ? 'rule-pass' : 'rule-fail'} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="rule-icon" style={{ display: 'flex', alignItems: 'center' }}>
                      {rule.test(password) ? (
                        <CheckCircleIcon sx={{ fontSize: 16, color: '#2e7d32' }} />
                      ) : (
                        <RadioButtonUncheckedIcon sx={{ fontSize: 16, color: '#9e9e9e' }} />
                      )}
                    </span>
                    {rule.label}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Registering...' : 'Sign Up'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
