import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIsAuthenticated } from '@azure/msal-react';
import { useAuth } from '../context/AuthContext';
import { useEffect } from 'react';

export default function LoginPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const isAuthenticated = useIsAuthenticated();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, user, navigate]);

  const handleMicrosoftLogin = async () => {
    setError('');
    setLoading(true);

    try {
      await login();
      // Redirect happens automatically via MSAL
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Microsoft login failed.';
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <img src="https://www.optimusinfo.com/wp-content/uploads/2014/11/optimusinfologo.png" alt="OptiStudio" />
        </div>
        <h2>Welcome to OptiStudio</h2>
        <p className="auth-subtitle">Sign in with your organization account</p>

        {error && <div className="auth-error">{error}</div>}

        <button 
          onClick={handleMicrosoftLogin} 
          className="btn-microsoft" 
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            width: '100%',
            padding: '12px 24px',
            backgroundColor: '#ffffff',
            border: '1px solid #8c8c8c',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '15px',
            fontWeight: 600,
            color: '#5e5e5e',
            transition: 'background-color 0.2s, border-color 0.2s',
          }}
          onMouseOver={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = '#f5f5f5';
              e.currentTarget.style.borderColor = '#666';
            }
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#ffffff';
            e.currentTarget.style.borderColor = '#8c8c8c';
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 21 21">
            <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
            <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
            <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
            <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
          </svg>
          {loading ? 'Signing in...' : 'Sign in with Microsoft'}
        </button>

        <p className="auth-info" style={{ marginTop: '24px', fontSize: '13px', color: '#666', textAlign: 'center' }}>
          Use your Optimus Information Inc. Microsoft account to sign in.
        </p>
      </div>
    </div>
  );
}
