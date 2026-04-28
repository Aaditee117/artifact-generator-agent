import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DownloadIcon from '@mui/icons-material/Download';
import { useNavigate } from 'react-router-dom';
import { agentService } from '../services/agentService';
import { useAuth } from '../context/AuthContext';

interface ArtifactInfo {
  action: string;
  artifactType: string;
  blobUrl: string;
  storagePath: string;
  contextSummary: string;
  version: number;
  updatedAt: string;
  approvalStatus: string;
}

interface SessionInfo {
  session_id: string;
  title?: string;
  artifacts: ArtifactInfo[];
  latest_update: string;
  author_name?: string;
}

const AdminApprovePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rejectDialog, setRejectDialog] = useState<{ open: boolean; artifact?: ArtifactInfo; sessionId?: string }>({ open: false });
  const [rejectReason, setRejectReason] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    try {
      setLoading(true);
      const res = await agentService.adminListSessions();
      if (res.data.success) {
        setSessions(res.data.sessions);
      } else {
        setError('Failed to load sessions');
      }
    } catch {
      setError('Failed to connect to agent service');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleApprove = async (sessionId: string, artifact: ArtifactInfo) => {
    const key = `${sessionId}_${artifact.action}_${artifact.artifactType}`;
    setActionLoading(key);
    try {
      const res = await agentService.adminApprove({
        session_id: sessionId,
        action: artifact.action,
        artifact_type: artifact.artifactType,
        approved_by: user?.name || user?.email || 'Admin',
      });
      if (res.data.success) {
        await loadSessions();
      }
    } catch {
      setError('Failed to approve artifact');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async () => {
    if (!rejectDialog.artifact || !rejectDialog.sessionId) return;

    const key = `${rejectDialog.sessionId}_${rejectDialog.artifact.action}_${rejectDialog.artifact.artifactType}`;
    setActionLoading(key);
    try {
      const res = await agentService.adminReject({
        session_id: rejectDialog.sessionId,
        action: rejectDialog.artifact.action,
        artifact_type: rejectDialog.artifact.artifactType,
        reason: rejectReason,
      });
      if (res.data.success) {
        setRejectDialog({ open: false });
        setRejectReason('');
        await loadSessions();
      }
    } catch {
      setError('Failed to reject artifact');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'approved':
        return <Chip label="Approved" color="success" size="small" />;
      case 'rejected':
        return <Chip label="Rejected" color="error" size="small" />;
      default:
        return <Chip label="Pending" color="warning" size="small" />;
    }
  };

  const formatAction = (action: string) => {
    return action
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton onClick={() => navigate('/dashboard')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Approve Final Decks
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {sessions.length === 0 ? (
        <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 8 }}>
          No generated artifacts awaiting review.
        </Typography>
      ) : (
        sessions.map((session) => (
          <Paper key={session.session_id} sx={{ mb: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 2, bgcolor: '#f8f8f8', borderBottom: '1px solid #eee' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {session.title ? (
                  (() => {
                    let decodedTitle = session.title;
                    try { decodedTitle = decodeURIComponent(session.title); } catch {}
                    return <>
                      Title: <b>{decodedTitle}</b> <span style={{ color: '#888', fontWeight: 400 }}>({session.session_id.slice(0, 8)}...)</span>
                    </>;
                  })()
                ) : (
                  <>Session: {session.session_id.slice(0, 8)}...</>
                )}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                <b>Author:</b> {session.author_name || 'Unknown'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Last updated: {new Date(session.latest_update).toLocaleString()}
              </Typography>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Artifact</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Version</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {session.artifacts.map((artifact) => {
                    const key = `${session.session_id}_${artifact.action}_${artifact.artifactType}`;
                    const isLoading = actionLoading === key;

                    return (
                      <TableRow key={key}>
                        <TableCell>{formatAction(artifact.action)}</TableCell>
                        <TableCell>
                          <Chip label={artifact.artifactType.toUpperCase()} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell>v{artifact.version}</TableCell>
                        <TableCell>{getStatusChip(artifact.approvalStatus)}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {artifact.blobUrl && (
                              <>
                                <Tooltip title="Preview">
                                  <IconButton
                                    size="small"
                                    onClick={() => window.open(artifact.blobUrl, '_blank')}
                                  >
                                    <VisibilityIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Download">
                                  <IconButton
                                    size="small"
                                    component="a"
                                    href={artifact.blobUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    <DownloadIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </>
                            )}
                            {artifact.approvalStatus === 'pending' && (
                              <>
                                <Button
                                  size="small"
                                  variant="contained"
                                  color="success"
                                  startIcon={isLoading ? <CircularProgress size={14} /> : <CheckCircleIcon />}
                                  disabled={isLoading}
                                  onClick={() => handleApprove(session.session_id, artifact)}
                                >
                                  Approve
                                </Button>
                                <Button
                                  size="small"
                                  variant="outlined"
                                  color="error"
                                  startIcon={<CancelIcon />}
                                  disabled={isLoading}
                                  onClick={() =>
                                    setRejectDialog({ open: true, artifact, sessionId: session.session_id })
                                  }
                                >
                                  Reject
                                </Button>
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        ))
      )}

      {/* Reject Dialog */}
      <Dialog open={rejectDialog.open} onClose={() => setRejectDialog({ open: false })} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Artifact</DialogTitle>
        <DialogContent>
          <TextField
            label="Reason for rejection"
            multiline
            rows={3}
            fullWidth
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setRejectDialog({ open: false }); setRejectReason(''); }}>
            Cancel
          </Button>
          <Button onClick={handleReject} color="error" variant="contained" disabled={!!actionLoading}>
            {actionLoading ? <CircularProgress size={20} /> : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminApprovePage;
