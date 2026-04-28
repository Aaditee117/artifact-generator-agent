import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import VerifyOtpPage from './pages/VerifyOtpPage';
import DashboardPage from './pages/DashboardPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminApprovePage from './pages/AdminApprovePage';
import ApprovedDecksPage from './pages/ApprovedDecksPage';
import ChatPage from './pages/ChatPage';
import ProtectedRoute from './components/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-otp" element={<VerifyOtpPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <RoleProtectedRoute allowedRoles={['Admin']}>
                <AdminUsersPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/approve"
            element={
              <RoleProtectedRoute allowedRoles={['Admin']}>
                <AdminApprovePage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/approved-decks"
            element={
              <RoleProtectedRoute allowedRoles={['Admin', 'Architect', 'Developer']}>
                <ApprovedDecksPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <RoleProtectedRoute allowedRoles={['Admin', 'Architect']}>
                <ChatPage />
              </RoleProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
