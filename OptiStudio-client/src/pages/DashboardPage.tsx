import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import GroupIcon from '@mui/icons-material/Group';
import VerifiedIcon from '@mui/icons-material/Verified';
import SlideshowIcon from '@mui/icons-material/Slideshow';

export default function DashboardPage() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="dashboard-header-inner">
          <img
            src="https://www.optimusinfo.com/wp-content/uploads/2014/11/optimusinfologo.png"
            alt="OptiStudio"
            className="dashboard-logo"
          />
          <div className="dashboard-header-right">
            <span className="role-badge">{user?.role}</span>
            <button onClick={handleLogout} className="btn-logout">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-welcome-card" style={{ marginBottom: '20px' }}>
          <div className="dashboard-avatar">
            {(user?.name || user?.email || '?').charAt(0).toUpperCase()}
          </div>
          <h1>Welcome, {user?.name || 'User'}</h1>
          <p className="dashboard-email">{user?.email}</p>
          <div className="dashboard-badges">
            <span className="badge-verified" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <VerifiedIcon sx={{ fontSize: 16 }} /> Email Verified
            </span>
            <span className="badge-role">{user?.role}</span>
          </div>
        </div>

        <div className="dashboard-grid">
          {/* Presales Deck Generation & Intelligent Chat — Admin and Architect only */}
          {(hasRole('Admin') || hasRole('Architect')) && (
            <div className="dashboard-card" onClick={() => navigate('/chat')} style={{ cursor: 'pointer' }}>
              <div className="card-icon"><DescriptionIcon sx={{ fontSize: 40, color: '#1976d2' }} /></div>
              <h3>Presales Deck Generation</h3>
              <p>Generate architecture diagrams, DFDs, presentations, and query project data.</p>
            </div>
          )}

          {/* Approve Deck — Admin only */}
          {hasRole('Admin') && (
            <div className="dashboard-card" onClick={() => navigate('/admin/approve')} style={{ cursor: 'pointer' }}>
              <div className="card-icon"><CheckCircleIcon sx={{ fontSize: 40, color: '#2e7d32' }} /></div>
              <h3>Approve Final Deck</h3>
              <p>Review and approve architecture designs and presales decks.</p>
            </div>
          )}

          {/* Approved Decks — All roles can access */}
          <div className="dashboard-card" onClick={() => navigate('/approved-decks')} style={{ cursor: 'pointer' }}>
            <div className="card-icon"><SlideshowIcon sx={{ fontSize: 40, color: '#7b1fa2' }} /></div>
            <h3>Approved Decks</h3>
            <p>View and preview all approved presentations and documents.</p>
          </div>

          {/* User Management — Admin only */}
          {hasRole('Admin') && (
            <div className="dashboard-card" onClick={() => navigate('/admin/users')} style={{ cursor: 'pointer' }}>
              <div className="card-icon"><GroupIcon sx={{ fontSize: 40, color: '#ed6c02' }} /></div>
              <h3>User Management</h3>
              <p>Manage users and assign roles across the platform.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
