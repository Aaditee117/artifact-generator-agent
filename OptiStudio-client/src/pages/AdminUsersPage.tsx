import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminService } from '../services/authService';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';

interface UserItem {
  id: string;
  name: string;
  email: string;
  isEmailVerified: boolean;
  role: string;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    const debounce = setTimeout(() => {
      fetchUsers(searchTerm);
    }, 400);
    return () => clearTimeout(debounce);
  }, [searchTerm]);

  const fetchUsers = async (search?: string) => {
    try {
      const response = await adminService.getAllUsers(search);
      if (response.data.success) {
        setUsers(response.data.users);
      }
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError('You do not have permission to access this page.');
      } else {
        setError('Failed to load users.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    setUpdatingId(userId);
    setError('');

    try {
      const response = await adminService.updateUserRole(userId, newRole);
      if (response.data.success) {
        setUsers(prev =>
          prev.map(u => (u.id === userId ? { ...u, role: newRole } : u))
        );
      } else {
        setError(response.data.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update role.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="auth-container">
        <div className="loading-spinner" />
      </div>
    );
  }

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
        <div className="admin-header">
          <button className="btn-back" onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>
          <h2>User Management</h2>
          <p className="admin-subtitle">{users.length} registered users</p>
        </div>

        <div className="admin-search-bar">
          <span className="search-icon" style={{ display: 'flex', alignItems: 'center' }}>
            <SearchIcon sx={{ fontSize: 20, color: '#666' }} />
          </span>
          <input
            type="text"
            placeholder="Search by name, email, or role..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button className="search-clear" onClick={() => setSearchTerm('')} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CloseIcon sx={{ fontSize: 18 }} />
            </button>
          )}
        </div>

        {error && <div className="auth-error">{error}</div>}

        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Verified</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>
                    <span className="user-name">{u.name || '—'}</span>
                  </td>
                  <td>
                    <span className="user-email">{u.email}</span>
                  </td>
                  <td>
                    <span className={`role-tag role-${u.role.toLowerCase()}`}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span className={u.isEmailVerified ? 'status-verified' : 'status-unverified'} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {u.isEmailVerified ? (
                        <><CheckCircleOutlineIcon sx={{ fontSize: 16, color: '#2e7d32' }} /> Verified</>
                      ) : (
                        <><CancelOutlinedIcon sx={{ fontSize: 16, color: '#d32f2f' }} /> Pending</>
                      )}
                    </span>
                  </td>
                  <td>
                    <select
                      value={u.role}
                      onChange={e => handleRoleChange(u.id, e.target.value)}
                      disabled={updatingId === u.id || u.email === user?.email}
                      className="role-select"
                    >
                      <option value="Developer">Developer</option>
                      <option value="Architect">Architect</option>
                      <option value="Admin">Admin</option>
                    </select>
                    {updatingId === u.id && <span className="updating-text">Saving...</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
