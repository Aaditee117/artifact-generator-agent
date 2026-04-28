import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import FolderIcon from '@mui/icons-material/Folder';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import SlideshowIcon from '@mui/icons-material/Slideshow';
import DescriptionIcon from '@mui/icons-material/Description';
import TableChartIcon from '@mui/icons-material/TableChart';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ImageIcon from '@mui/icons-material/Image';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import EditIcon from '@mui/icons-material/Edit';
import DownloadIcon from '@mui/icons-material/Download';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import GridViewIcon from '@mui/icons-material/GridView';
import ViewListIcon from '@mui/icons-material/ViewList';

interface ApprovedArtifact {
  name: string;
  size: number;
  last_modified: string;
  content_type: string;
  url: string;
  approved_by?: string;
  created_by?: string;
}

export default function ApprovedDecksPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [artifacts, setArtifacts] = useState<ApprovedArtifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pptPreview, setPptPreview] = useState<{ open: boolean; artifact: ApprovedArtifact | null }>({ 
    open: false, 
    artifact: null 
  });
  
  // New state for filtering, sorting, and pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'presentation' | 'diagram' | 'document'>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'name' | 'size'>('newest');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9;

  // Helper function to determine artifact type
  const getArtifactType = (artifact: ApprovedArtifact): 'presentation' | 'diagram' | 'document' | 'spreadsheet' => {
    const fileName = artifact.name.toLowerCase();
    if (fileName.endsWith('.pptx') || fileName.endsWith('.ppt') || artifact.content_type?.includes('presentation')) {
      return 'presentation';
    }
    if (fileName.endsWith('.drawio') || fileName.endsWith('.png') || fileName.endsWith('.svg')) {
      return 'diagram';
    }
    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls') || artifact.content_type?.includes('spreadsheet')) {
      return 'spreadsheet';
    }
    return 'document';
  };

  // Group artifacts by base name
  const groupedArtifacts = useMemo(() => {
    // Normalize a filename to a canonical key for grouping
    const normalizeKey = (fileName: string) => {
      return fileName
        .replace(/\.(drawio|png|svg|jpg|pptx|ppt|pdf|docx|doc)$/i, '')
        .replace(/[-_]+/g, '_')
        .toLowerCase();
    };

    return artifacts.reduce((groups, artifact) => {
      const fileName = artifact.name.split('/').pop() || artifact.name;
      const baseName = normalizeKey(fileName);
      
      if (!groups[baseName]) {
        groups[baseName] = [];
      }
      groups[baseName].push(artifact);
      return groups;
    }, {} as Record<string, ApprovedArtifact[]>);
  }, [artifacts]);

  // Helper: find a matching PNG across ALL artifacts for a drawio file
  const findMatchingImage = (drawioArtifact: ApprovedArtifact): ApprovedArtifact | undefined => {
    // First: check if there's a PNG with the same path but different extension
    const drawioPath = drawioArtifact.name.replace(/\.drawio$/i, '');
    const pathNormalized = drawioPath.replace(/[-_]+/g, '_').toLowerCase();
    
    return artifacts.find(a => {
      if (!a.name.endsWith('.png') && !a.name.endsWith('.svg')) return false;
      const aPath = a.name.replace(/\.(png|svg)$/i, '').replace(/[-_]+/g, '_').toLowerCase();
      return aPath === pathNormalized;
    });
  };

  // Filter and sort artifacts
  const filteredAndSortedGroups = useMemo(() => {
    let groups = Object.entries(groupedArtifacts).map(([name, arts]) => ({ name, artifacts: arts }));

    // Remove standalone PNG/SVG groups if a matching drawio group exists
    const drawioGroups = groups.filter(g => g.artifacts.some(a => a.name.endsWith('.drawio')));
    const drawioNormalizedKeys = new Set(
      drawioGroups.flatMap(g => 
        g.artifacts
          .filter(a => a.name.endsWith('.drawio'))
          .map(a => a.name.replace(/\.drawio$/i, '').replace(/[-_]+/g, '_').toLowerCase())
      )
    );
    groups = groups.filter(g => {
      // Keep if group has a .drawio file or non-image file
      if (g.artifacts.some(a => a.name.endsWith('.drawio') || a.name.endsWith('.pptx') || a.name.endsWith('.ppt') || a.name.endsWith('.pdf') || a.name.endsWith('.docx'))) {
        return true;
      }
      // If group is only images, check if a matching drawio group already claims them
      const isOnlyImages = g.artifacts.every(a => a.name.endsWith('.png') || a.name.endsWith('.svg'));
      if (isOnlyImages) {
        return !g.artifacts.some(a => {
          const normalized = a.name.replace(/\.(png|svg)$/i, '').replace(/[-_]+/g, '_').toLowerCase();
          return drawioNormalizedKeys.has(normalized);
        });
      }
      return true;
    });

    // Apply search filter
    if (searchQuery) {
      groups = groups.filter(group => 
        group.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply type filter
    if (filterType !== 'all') {
      groups = groups.filter(group => 
        group.artifacts.some(art => getArtifactType(art) === filterType)
      );
    }

    // Apply sorting
    groups.sort((a, b) => {
      const primaryA = a.artifacts[0];
      const primaryB = b.artifacts[0];

      switch (sortBy) {
        case 'newest':
          return new Date(primaryB.last_modified).getTime() - new Date(primaryA.last_modified).getTime();
        case 'oldest':
          return new Date(primaryA.last_modified).getTime() - new Date(primaryB.last_modified).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        case 'size':
          return primaryB.size - primaryA.size;
        default:
          return 0;
      }
    });

    return groups;
  }, [groupedArtifacts, searchQuery, filterType, sortBy]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedGroups.length / itemsPerPage);
  const paginatedGroups = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredAndSortedGroups.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedGroups, currentPage, itemsPerPage]);

  const startResult = filteredAndSortedGroups.length === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
  const endResult = Math.min(currentPage * itemsPerPage, filteredAndSortedGroups.length);

  useEffect(() => {
    fetchApprovedDecks();
  }, []);

  const fetchApprovedDecks = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/agent/approved-decks')
     // ("https://ca-optistudio-eu2-dev-001.salmonpebble-d7c05023.eastus2.azurecontainerapps.io/api/agent/approved-decks");
;
      const data = await response.json();
      
      if (data.success) {
        setArtifacts(data.artifacts || []);
      } else {
        setError(data.error || 'Failed to load approved decks');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching approved decks:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const getFileIcon = (contentType: string | null, fileName: string) => {
    if (contentType?.includes('pdf') || fileName.endsWith('.pdf')) {
      return <PictureAsPdfIcon sx={{ fontSize: 40, color: '#d32f2f' }} />;
    }
    if (contentType?.includes('presentation') || fileName.endsWith('.pptx') || fileName.endsWith('.ppt')) {
      return <SlideshowIcon sx={{ fontSize: 40, color: '#c62828' }} />;
    }
    if (contentType?.includes('word') || fileName.endsWith('.docx') || fileName.endsWith('.doc')) {
      return <DescriptionIcon sx={{ fontSize: 40, color: '#666' }} />;
    }
    if (contentType?.includes('spreadsheet') || fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      return <TableChartIcon sx={{ fontSize: 40, color: '#1b5e20' }} />;
    }
    if (fileName.endsWith('.drawio') || contentType?.includes('xml')) {
      return <AccountTreeIcon sx={{ fontSize: 40, color: '#c62828' }} />;
    }
    if (fileName.endsWith('.png') || fileName.endsWith('.jpg') || fileName.endsWith('.svg') || contentType?.includes('image')) {
      return <ImageIcon sx={{ fontSize: 40, color: '#999' }} />;
    }
    return <FolderIcon sx={{ fontSize: 40, color: '#757575' }} />;
  };

  const BACKEND = 'http://localhost:8000';

  const handleOpenDrawio = (artifact: ApprovedArtifact) => {
    const blobName = artifact.name;
    const title = blobName.split('/').pop() || 'diagram.drawio';
    // Fetch via backend proxy to avoid CORS on Azure Blob Storage
    fetch(`${BACKEND}/api/agent/artifact-proxy/${encodeURIComponent(blobName)}`)
      .then(res => {
        if (!res.ok) throw new Error(`Proxy returned ${res.status}`);
        return res.text();
      })
      .then(xml => {
        const encoded = encodeURIComponent(xml);
        const drawioUrl = `https://app.diagrams.net/?title=${encodeURIComponent(title)}#R${encoded}`;
        window.open(drawioUrl, '_blank');
      })
      .catch(err => {
        console.error('Failed to open draw.io via proxy:', err);
        // Last-resort: open the SAS URL directly
        window.open(artifact.url, '_blank');
      });
  };

  const handlePreview = (artifact: ApprovedArtifact) => {
    window.open(artifact.url, '_blank');
  };

  const handlePptPreview = (artifact: ApprovedArtifact) => {
    setPptPreview({ open: true, artifact });
  };

  const handleDownload = (artifact: ApprovedArtifact) => {
    const link = document.createElement('a');
    link.href = artifact.url;
    link.download = artifact.name.split('/').pop() || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getCategoryTag = (groupArtifacts: ApprovedArtifact[]): string => {
    const primary = groupArtifacts[0];
    const fileName = primary.name.toLowerCase();
    const hasDrawio = groupArtifacts.some(a => a.name.endsWith('.drawio'));
    
    if (fileName.includes('architecture') || hasDrawio) return 'Architecture Diagram';
    if (fileName.includes('solution') || fileName.includes('deck') || fileName.includes('presales')) return 'Presentation';
    if (fileName.includes('mvp')) return 'MVP Proposal';
    if (fileName.includes('cost') || groupArtifacts.some(a => a.name.toLowerCase().endsWith('.xlsx'))) return 'Cost Report';
    if (fileName.includes('dfd') || fileName.includes('dataflow')) return 'Data Flow Diagram';
    return 'Document';
  };

  const renderArtifactCard = (groupArtifacts: ApprovedArtifact[], mode: 'grid' | 'list') => {
    const primary = groupArtifacts[0];
    const fileName = primary.name.split('/').pop() || primary.name;
    const drawioArtifact = groupArtifacts.find(a => a.name.endsWith('.drawio'));
    // Look for image in group first, then search all artifacts
    let imageArtifact = groupArtifacts.find(a => a.name.endsWith('.png') || a.name.endsWith('.svg'));
    if (!imageArtifact && drawioArtifact) {
      imageArtifact = findMatchingImage(drawioArtifact);
    }
    const hasDrawio = !!drawioArtifact;
    const hasImage = !!imageArtifact;
    const isPpt = fileName.endsWith('.pptx') || fileName.endsWith('.ppt') || primary.content_type?.includes('presentation');
    const type = getArtifactType(primary);
    const category = getCategoryTag(groupArtifacts);

    const date = new Date(primary.last_modified);
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
    const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    if (mode === 'list') {
      return (
        <div style={{
          background: 'white',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          marginBottom: '12px',
          transition: 'box-shadow 0.2s',
          cursor: 'pointer'
        }}
        onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'}
        onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
        >
          {getFileIcon(primary.content_type, primary.name)}
          <div style={{ flex: 1, minWidth: 0 }}>
            <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>{fileName}</h4>
            <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
              {type === 'diagram' ? 'Draw.io Diagram' : type === 'presentation' ? 'Document' : 'Document'}
            </p>
            {primary.created_by && (
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#888' }}>Created by: <strong>{primary.created_by}</strong></p>
            )}
            {primary.approved_by && (
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#888' }}>Approved by: <strong>{primary.approved_by}</strong></p>
            )}
          </div>
          <div style={{ fontSize: '13px', color: '#666', textAlign: 'right' }}>
            <div>{formatFileSize(primary.size)}</div>
            <div style={{ fontSize: '12px', color: '#999' }}>{dateStr}</div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {type === 'diagram' && hasImage && imageArtifact && (
              <button
                onClick={(e) => { e.stopPropagation(); window.open(imageArtifact.url, '_blank'); }}
                style={{
                  padding: '8px 16px',
                  background: '#c62828',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                View Image
              </button>
            )}
            {type === 'diagram' && hasDrawio && drawioArtifact && (
              <button
                onClick={(e) => { e.stopPropagation(); handleOpenDrawio(drawioArtifact); }}
                style={{
                  padding: '8px 16px',
                  background: hasImage ? 'white' : '#c62828',
                  color: hasImage ? '#c62828' : 'white',
                  border: hasImage ? '1px solid #c62828' : 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                View in Draw.io
              </button>
            )}
            {type === 'spreadsheet' && (
              <button
                onClick={(e) => { e.stopPropagation(); window.open(`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(primary.url)}`, '_blank'); }}
                style={{
                  padding: '8px 16px',
                  background: '#1b5e20',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                Preview Document
              </button>
            )}
            {type === 'presentation' && (
              <button
                onClick={(e) => { e.stopPropagation(); handlePptPreview(primary); }}
                style={{
                  padding: '8px 16px',
                  background: '#c62828',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                Preview Presentation
              </button>
            )}
          </div>
        </div>
      );
    }

    // Grid mode
    return (
      <div style={{
        background: 'white',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        display: 'flex',
        flexDirection: 'column',
      }}
      onMouseEnter={(e) => { 
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
      }}
      onMouseLeave={(e) => { 
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
      >
        {/* Fixed-height image area — always rendered for consistent card size */}
        <div style={{
          background: '#f9f9f9',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '180px',
          overflow: 'hidden',
          cursor: type === 'diagram' && hasImage && imageArtifact ? 'pointer' : 'default',
          flexShrink: 0
        }}
        onClick={() => type === 'diagram' && hasImage && imageArtifact && window.open(imageArtifact.url, '_blank')}
        >
          {type === 'diagram' && hasImage && imageArtifact ? (
            <img
              src={imageArtifact.url}
              alt={fileName}
              style={{
                maxWidth: '100%',
                maxHeight: '180px',
                objectFit: 'contain',
                display: 'block'
              }}
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', color: '#ccc' }}>
              {getFileIcon(primary.content_type, primary.name)}
              <span style={{ fontSize: '12px', color: '#bbb' }}>
                {type === 'presentation' ? 'Presentation' : type === 'diagram' ? 'Diagram' : 'Document'}
              </span>
            </div>
          )}
        </div>
        
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '12px' }}>
          {getFileIcon(primary.content_type, primary.name)}
          <div style={{ marginLeft: '12px', flex: 1, minWidth: 0 }}>
            <h4 style={{ 
              margin: 0, 
              fontSize: '15px', 
              fontWeight: 600,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              marginBottom: '4px'
            }}>
              {fileName}
            </h4>
            <p style={{ 
              margin: 0, 
              fontSize: '13px', 
              color: '#666',
            }}>
              {type === 'diagram' ? 'Draw.io Diagram' : type === 'presentation' ? 'Document' : 'Document'}
            </p>
          </div>
        </div>
        
        <div style={{ 
          display: 'flex', 
          gap: '12px', 
          fontSize: '13px', 
          color: '#666',
          marginBottom: '12px',
          paddingBottom: '12px',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <FolderIcon sx={{ fontSize: 16 }} />
            <span>{formatFileSize(primary.size)}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>📅</span>
            <span>{dateStr}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>🕐</span>
            <span>{timeStr}</span>
          </div>
        </div>

        {(primary.created_by || primary.approved_by) && (
          <div style={{
            fontSize: '12px',
            color: '#666',
            marginBottom: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}>
            {primary.created_by && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>👤</span>
                <span>Created by: <strong>{primary.created_by}</strong></span>
              </div>
            )}
            {primary.approved_by && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>✅</span>
                <span>Approved by: <strong>{primary.approved_by}</strong></span>
              </div>
            )}
          </div>
        )}

        <div style={{ marginBottom: '12px' }}>
          <span style={{
            display: 'inline-block',
            padding: '4px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 500,
            background: category.includes('Diagram') ? '#ffebee' : 
                       category === 'Presentation' ? '#fff3e0' :
                       category === 'MVP Proposal' ? '#ffebee' :
                       category === 'Cost Report' ? '#e8f5e9' : '#f5f5f5',
            color: category.includes('Diagram') ? '#c62828' : 
                   category === 'Presentation' ? '#e65100' :
                   category === 'MVP Proposal' ? '#c62828' :
                   category === 'Cost Report' ? '#1b5e20' : '#666'
          }}>
            {category}
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
          {type === 'diagram' && hasImage && imageArtifact && (
            <button
              onClick={() => window.open(imageArtifact.url, '_blank')}
              style={{
                padding: '12px',
                background: '#c62828',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#8e0000'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#c62828'; }}
            >
              <ImageIcon sx={{ fontSize: 18 }} />
              View Image
            </button>
          )}
          
          {type === 'diagram' && hasDrawio && drawioArtifact && (
            <button
              onClick={() => handleOpenDrawio(drawioArtifact)}
              style={{
                padding: '12px',
                background: hasImage ? 'white' : '#c62828',
                color: hasImage ? '#c62828' : 'white',
                border: hasImage ? '1px solid #c62828' : 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => { 
                if (!hasImage) {
                  e.currentTarget.style.background = '#8e0000'; 
                } else {
                  e.currentTarget.style.background = '#ffebee';
                }
              }}
              onMouseLeave={(e) => { 
                if (!hasImage) {
                  e.currentTarget.style.background = '#c62828'; 
                } else {
                  e.currentTarget.style.background = 'white';
                }
              }}
            >
              <EditIcon sx={{ fontSize: 18 }} />
              View in Draw.io
            </button>
          )}
          
          {type === 'spreadsheet' && (
            <button
              onClick={() => window.open(`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(primary.url)}`, '_blank')}
              style={{
                padding: '12px',
                background: '#1b5e20',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#145214'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#1b5e20'; }}
            >
              <VisibilityIcon sx={{ fontSize: 18 }} />
              Preview Document
            </button>
          )}
          {type === 'presentation' && isPpt ? (
            <button
              onClick={() => handlePptPreview(primary)}
              style={{
                padding: '12px',
                background: '#c62828',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#8e0000'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#c62828'; }}
            >
              <VisibilityIcon sx={{ fontSize: 18 }} />
              Preview Presentation
            </button>
          ) : type === 'document' && (
            <button
              onClick={() => handlePreview(primary)}
              style={{
                padding: '12px',
                background: '#c62828',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#8e0000'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#c62828'; }}
            >
              <VisibilityIcon sx={{ fontSize: 18 }} />
              View Document
            </button>
          )}
        </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa', padding: '24px' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '32px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button 
            onClick={() => navigate('/dashboard')} 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'none',
              border: 'none',
              color: '#c62828',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              padding: 0
            }}
          >
            <ArrowBackIcon />
            Back to Dashboard
          </button>
          <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 700, color: '#1a1a1a' }}>Approved Decks</h1>
        </div>
        <span className="role-badge" style={{
          background: '#c62828',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {user?.role}
        </span>
      </header>

      {/* Info Section */}
      <div style={{ 
        background: 'white', 
        padding: '24px', 
        borderRadius: '8px', 
        marginBottom: '24px',
        border: '1px solid #e0e0e0'
      }}>
        <h2 style={{ margin: 0, marginBottom: '8px', fontSize: '18px', fontWeight: 600 }}>
          Approved Presentations & Documents
        </h2>
        <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
          Browse and preview all approved decks and documents. Click on any item to view it directly in your browser.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px' }}>
          <p style={{ color: '#666' }}>Loading approved decks...</p>
        </div>
      ) : error ? (
        <div style={{ 
          background: '#ffebee', 
          color: '#c62828', 
          padding: '16px', 
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ffcdd2'
        }}>
          <strong>Error:</strong> {error}
        </div>
      ) : artifacts.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          background: 'white',
          borderRadius: '8px',
          border: '1px solid #e0e0e0'
        }}>
          <SlideshowIcon sx={{ fontSize: 80, color: '#bdbdbd', mb: 2 }} />
          <h3 style={{ color: '#757575', marginBottom: '8px' }}>No Approved Decks Yet</h3>
          <p style={{ color: '#9e9e9e', margin: 0 }}>
            Approved presentations will appear here once they are reviewed by an admin.
          </p>
        </div>
      ) : (
        <>
          {/* Search and Filters Bar */}
          <div style={{
            display: 'flex',
            gap: '16px',
            marginBottom: '24px',
            alignItems: 'center',
            flexWrap: 'wrap'
          }}>
            <div style={{
              flex: 1,
              minWidth: '300px',
              position: 'relative'
            }}>
              <SearchIcon style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#999',
                fontSize: '20px'
              }} />
              <input
                type="text"
                placeholder="Search decks..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 42px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#c62828'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              style={{
                padding: '10px 20px',
                background: showFilters ? '#c62828' : 'white',
                color: showFilters ? 'white' : '#333',
                border: '1px solid ' + (showFilters ? '#c62828' : '#ddd'),
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
            >
              <FilterListIcon sx={{ fontSize: 18 }} />
              Filters
            </button>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div style={{
              background: 'white',
              padding: '16px',
              borderRadius: '8px',
              marginBottom: '24px',
              border: '1px solid #e0e0e0',
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => { setFilterType('all'); setCurrentPage(1); }}
                style={{
                  padding: '8px 16px',
                  background: filterType === 'all' ? '#c62828' : 'white',
                  color: filterType === 'all' ? 'white' : '#666',
                  border: '1px solid ' + (filterType === 'all' ? '#c62828' : '#ddd'),
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'all 0.2s'
                }}
              >
                All Types
              </button>
              <button
                onClick={() => { setFilterType('presentation'); setCurrentPage(1); }}
                style={{
                  padding: '8px 16px',
                  background: filterType === 'presentation' ? '#c62828' : 'white',
                  color: filterType === 'presentation' ? 'white' : '#666',
                  border: '1px solid ' + (filterType === 'presentation' ? '#c62828' : '#ddd'),
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'all 0.2s'
                }}
              >
                Presentations
              </button>
              <button
                onClick={() => { setFilterType('diagram'); setCurrentPage(1); }}
                style={{
                  padding: '8px 16px',
                  background: filterType === 'diagram' ? '#c62828' : 'white',
                  color: filterType === 'diagram' ? 'white' : '#666',
                  border: '1px solid ' + (filterType === 'diagram' ? '#c62828' : '#ddd'),
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'all 0.2s'
                }}
              >
                Diagrams
              </button>
              <button
                onClick={() => { setFilterType('document'); setCurrentPage(1); }}
                style={{
                  padding: '8px 16px',
                  background: filterType === 'document' ? '#c62828' : 'white',
                  color: filterType === 'document' ? 'white' : '#666',
                  border: '1px solid ' + (filterType === 'document' ? '#c62828' : '#ddd'),
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'all 0.2s'
                }}
              >
                Documents
              </button>
            </div>
          )}

          {/* View Controls and Sort */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Showing {startResult} to {endResult} of {filteredAndSortedGroups.length} results
            </div>
            
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '4px', background: 'white', padding: '4px', borderRadius: '6px', border: '1px solid #ddd' }}>
                <button
                  onClick={() => setViewMode('grid')}
                  style={{
                    padding: '8px 12px',
                    background: viewMode === 'grid' ? '#f5f5f5' : 'transparent',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    color: viewMode === 'grid' ? '#c62828' : '#666'
                  }}
                >
                  <GridViewIcon sx={{ fontSize: 20 }} />
                  <span style={{ marginLeft: '6px', fontSize: '13px', fontWeight: 500 }}>Grid</span>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  style={{
                    padding: '8px 12px',
                    background: viewMode === 'list' ? '#f5f5f5' : 'transparent',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    color: viewMode === 'list' ? '#c62828' : '#666'
                  }}
                >
                  <ViewListIcon sx={{ fontSize: 20 }} />
                  <span style={{ marginLeft: '6px', fontSize: '13px', fontWeight: 500 }}>List</span>
                </button>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '14px', color: '#666' }}>Sort by</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  style={{
                    padding: '8px 12px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    outline: 'none',
                    background: 'white'
                  }}
                >
                  <option value="newest">Newest</option>
                  <option value="oldest">Oldest</option>
                  <option value="name">Name</option>
                  <option value="size">Size</option>
                </select>
              </div>
            </div>
          </div>

          {/* Artifacts Grid/List */}
          {filteredAndSortedGroups.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '60px 20px',
              background: 'white',
              borderRadius: '8px',
              border: '1px solid #e0e0e0'
            }}>
              <SearchIcon sx={{ fontSize: 80, color: '#bdbdbd', mb: 2 }} />
              <h3 style={{ color: '#757575', marginBottom: '8px' }}>No Results Found</h3>
              <p style={{ color: '#9e9e9e', margin: 0 }}>
                Try adjusting your search or filters
              </p>
            </div>
          ) : (
            <div style={viewMode === 'grid' ? {
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '20px',
              marginBottom: '32px'
            } : {
              marginBottom: '32px'
            }}>
              {paginatedGroups.map((group, index) => 
                <div key={index}>
                  {renderArtifactCard(group.artifacts, viewMode)}
                </div>
              )}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '20px 0'
            }}>
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                style={{
                  padding: '8px 16px',
                  background: 'white',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                  opacity: currentPage === 1 ? 0.5 : 1,
                  fontSize: '14px'
                }}
              >
                &lt; Previous
              </button>
              
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter(page => {
                    if (totalPages <= 7) return true;
                    if (page === 1 || page === totalPages) return true;
                    if (page >= currentPage - 1 && page <= currentPage + 1) return true;
                    return false;
                  })
                  .map((page, index, array) => {
                    if (index > 0 && page - array[index - 1] > 1) {
                      return (
                        <span key={`ellipsis-${page}`}>
                          <span style={{ padding: '8px 4px', color: '#999' }}>...</span>
                          <button
                            onClick={() => setCurrentPage(page)}
                            style={{
                              padding: '8px 12px',
                              background: currentPage === page ? '#c62828' : 'white',
                              color: currentPage === page ? 'white' : '#333',
                              border: '1px solid ' + (currentPage === page ? '#c62828' : '#ddd'),
                              borderRadius: '6px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              fontWeight: currentPage === page ? 600 : 400,
                              minWidth: '40px'
                            }}
                          >
                            {page}
                          </button>
                        </span>
                      );
                    }
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        style={{
                          padding: '8px 12px',
                          background: currentPage === page ? '#c62828' : 'white',
                          color: currentPage === page ? 'white' : '#333',
                          border: '1px solid ' + (currentPage === page ? '#c62828' : '#ddd'),
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: currentPage === page ? 600 : 400,
                          minWidth: '40px'
                        }}
                      >
                        {page}
                      </button>
                    );
                  })}
              </div>
              
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                style={{
                  padding: '8px 16px',
                  background: 'white',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                  opacity: currentPage === totalPages ? 0.5 : 1,
                  fontSize: '14px'
                }}
              >
                Next &gt;
              </button>

              <div style={{ fontSize: '14px', color: '#666', marginLeft: '16px' }}>
                Showing {startResult} to {endResult} of {filteredAndSortedGroups.length} results
              </div>
            </div>
          )}
        </>
      )}

      {/* PPT Preview Modal */}
      {pptPreview.open && pptPreview.artifact && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            padding: '20px'
          }}
          onClick={() => setPptPreview({ open: false, artifact: null })}
        >
          <div
            style={{
              background: 'white',
              borderRadius: '8px',
              padding: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '12px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: 0, fontSize: '18px' }}>
              {pptPreview.artifact.name.split('/').pop()}
            </h3>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <button
                onClick={() => handleDownload(pptPreview.artifact!)}
                style={{
                  padding: '8px 16px',
                  background: '#c62828',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: 500
                }}
              >
                <DownloadIcon sx={{ fontSize: 18 }} />
                Download
              </button>
              <button
                onClick={() => setPptPreview({ open: false, artifact: null })}
                style={{
                  padding: '8px',
                  background: '#757575',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <CloseIcon />
              </button>
            </div>
          </div>
          <div
            style={{
              flex: 1,
              background: 'white',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <iframe
              src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(pptPreview.artifact.url)}`}
              style={{
                width: '100%',
                height: '100%',
                border: 'none'
              }}
              title="PowerPoint Preview"
            />
          </div>
        </div>
      )}
    </div>
  );
}
