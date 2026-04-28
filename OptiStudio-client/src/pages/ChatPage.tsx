import VisibilityIcon from '@mui/icons-material/Visibility';
import { useState, useEffect, useRef, useCallback, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  chatService,
  type ChatSessionDto,
  type ChatGroupDto,
  type ChatMessageDto,
  type ArtifactDto,
} from '../services/chatService';
import {
  agentService,
  type ArtifactRef,
  type ClarifyQuestion,
  type GenerateImage,
  type ArchitectureGraph,
} from '../services/agentService';

// Lazy load ArchitectureDiagram to prevent build errors if React Flow has issues
const ArchitectureDiagram = lazy(() => import('../components/ArchitectureDiagram'));
const DrawioEditor = lazy(() => import('../components/DrawioEditor'));

import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import DescriptionIcon from '@mui/icons-material/Description';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import CallSplitIcon from '@mui/icons-material/CallSplit';
import SlideshowIcon from '@mui/icons-material/Slideshow';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import DownloadIcon from '@mui/icons-material/Download';
import BuildIcon from '@mui/icons-material/Build';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import RefreshIcon from '@mui/icons-material/Refresh';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import CheckIcon from '@mui/icons-material/Check';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import SaveIcon from '@mui/icons-material/Save';

import { ToonRenderer } from '../components/ToonRenderer';

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.txt', '.jpg', '.jpeg', '.png'];
const ARTIFACT_CATEGORIES = ['Document', 'MeetingTranscript', 'EmailThread', 'PMInstruction'];

export default function ChatPage() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState<ChatSessionDto[]>([]);
  const [groups, setGroups] = useState<ChatGroupDto[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageDto[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  // Input state
  const [inputText, setInputText] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [fileCategories, setFileCategories] = useState<string[]>([]);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState('');

  // Artifact processing state
  const [processingArtifacts, setProcessingArtifacts] = useState(false);
  const [sessionState, setSessionState] = useState<string>('idle');
  const [artifactSummary, setArtifactSummary] = useState<string>('');

  // Inline rename/edit state
  const [renamingSessionId, setRenamingSessionId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  // Agent generation state
  const [agentLoading, setAgentLoading] = useState(false);
  const [showClarifyModal, setShowClarifyModal] = useState(false);
  const [clarifyAction, setClarifyAction] = useState('');
  const [clarifyQuestions, setClarifyQuestions] = useState<ClarifyQuestion[]>([]);
  const [clarifyAnswers, setClarifyAnswers] = useState<Record<string, string>>({});
  const [clarifyProjectSummary, setClarifyProjectSummary] = useState('');
  const [generatedResults, setGeneratedResults] = useState<{ 
    images?: GenerateImage[]; 
    pptUrl?: string; 
    excelUrl?: string; 
    dallePrompt?: string; 
    dallePrompts?: Record<string, string>; 
    contextSummary?: string;
    action?: string 
  } | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [changeInstructions, setChangeInstructions] = useState('');
  const [showPromptDetails, setShowPromptDetails] = useState(false);
  const [renamingGroupId, setRenamingGroupId] = useState<string | null>(null);
  const [renameGroupValue, setRenameGroupValue] = useState('');
  const [newGroupName, setNewGroupName] = useState('');
  const [showNewGroup, setShowNewGroup] = useState(false);

  // Architecture diagram state (React Flow)
  const [architectureGraph, setArchitectureGraph] = useState<ArchitectureGraph | null>(null);
  const [architectureProjectName, setArchitectureProjectName] = useState('');
  const [showArchitectureModal, setShowArchitectureModal] = useState(false);
  const [architectureSaving, setArchitectureSaving] = useState(false);
  const [generationPhase, setGenerationPhase] = useState<'mvp' | 'poc'>('mvp');

  // Draw.io editor state
  const [drawioXml, setDrawioXml] = useState<string | null>(null);
  const [drawioProjectName, setDrawioProjectName] = useState('');
  const [showDrawioEditor, setShowDrawioEditor] = useState(false);


  // Drag and drop state
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSession = sessions.find(s => s.id === activeSessionId);

  useEffect(() => { loadSidebarData(); }, []);
  useEffect(() => {
    if (activeSessionId) {
      loadMessagesAndContext(activeSessionId);
    }
    else {
      setMessages([]);
      setSessionState('idle');
      setArtifactSummary('');
    }
  }, [activeSessionId]);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSidebarData = async () => {
    try {
      const [sessionsRes, groupsRes] = await Promise.all([
        chatService.getSessions(),
        chatService.getGroups(),
      ]);
      if (sessionsRes.data.success) setSessions(sessionsRes.data.sessions);
      if (groupsRes.data.success) setGroups(groupsRes.data.groups);
    } catch { /* silently fail */ }
  };


  /** Load SQL messages + Cosmos context and merge them into a single timeline. */
  const loadMessagesAndContext = async (sessionId: string) => {
    setLoadingMessages(true);
    try {
      const [msgRes, ctxRes] = await Promise.all([
        chatService.getMessages(sessionId),
        agentService.getSessionContext(sessionId).catch(() => null),
      ]);

      const sqlMessages: ChatMessageDto[] = msgRes.data.success ? msgRes.data.messages : [];

      // Build a set of IDs already present from SQL to avoid duplicates
      const sqlIds = new Set(sqlMessages.map(m => m.id));

      // Convert Cosmos conversation_message docs into ChatMessageDto-shaped objects
      const agentMessages: ChatMessageDto[] = [];
      if (ctxRes?.data?.success && ctxRes.data.conversationHistory) {
        for (const cm of ctxRes.data.conversationHistory) {
          // Only include assistant messages (user messages are already in SQL)
          if (cm.role !== 'assistant') continue;
          if (sqlIds.has(cm.id)) continue;
          agentMessages.push({
            id: cm.id,
            content: cm.content,
            senderType: 'Assistant',
            chatSessionId: sessionId,
            createdAt: cm.createdAt,
            artifacts: [],
          });
        }
      }

      // Merge and sort by timestamp
      const merged = [...sqlMessages, ...agentMessages].sort(
        (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      );
      setMessages(merged);

      // Restore session state from context
      if (ctxRes?.data?.success) {
        setSessionState(ctxRes.data.state || 'idle');
        if (ctxRes.data.processingDetails?.artifact_count) {
          setArtifactSummary(`${ctxRes.data.processingDetails.artifact_count} artifact(s) processed`);
        } else if (ctxRes.data.hasContext) {
          setArtifactSummary('Artifacts previously processed');
          if (ctxRes.data.state === 'idle') setSessionState('ready');
        }
      }
    } catch {
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleNewChat = async (groupId?: string) => {
    try {
      const res = await chatService.createSession(groupId);
      if (res.data.success && res.data.session) {
        await loadSidebarData();
        setActiveSessionId(res.data.session.id);
        setSessionState('idle');
        setArtifactSummary('');
      }
    } catch { /* ignore */ }
  };

  const handleSend = async () => {
    if (!activeSessionId) return;
    if (!inputText.trim() && selectedFiles.length === 0) return;
    if (processingArtifacts) return; // Block sending during processing

    setSending(true);
    setSendError('');

    const hasNewFiles = selectedFiles.length > 0;

    try {
      const res = await chatService.sendMessage(activeSessionId, inputText, selectedFiles, fileCategories);
      if (res.data.success && res.data.chatMessage) {
        setMessages(prev => [...prev, res.data.chatMessage!]);
        setInputText('');
        setSelectedFiles([]);
        setFileCategories([]);
        if (fileInputRef.current) fileInputRef.current.value = '';

        // --- Update session title immediately if first message is file-only ---
        if (
          hasNewFiles &&
          !inputText.trim() &&
          activeSession &&
          activeSession.title === "New Chat" &&
          selectedFiles.length > 0
        ) {
          const fileName = selectedFiles[0].name;
          const nameWithoutExt = fileName.replace(/\.[^/.]+$/, "");
          const newTitle = nameWithoutExt.length <= 60 ? nameWithoutExt : nameWithoutExt.slice(0, 60) + "…";
          setSessions(prev =>
            prev.map(s =>
              s.id === activeSessionId ? { ...s, title: newTitle } : s
            )
          );
        }

        // If files were uploaded, process them
        if (hasNewFiles && res.data.chatMessage.artifacts.length > 0) {
          await processUploadedArtifacts(activeSessionId, res.data.chatMessage.artifacts);
        } else if (inputText.trim()) {
          // If no files were uploaded AND text was provided, ask the unified chatbot!
          try {
            const recentHistory = messages
              .slice(-10)
              .filter(m => m.content && !m.metadata?.isToon && !m.content.includes("Executing SQL:"))
              .map(m => ({ 
                role: m.senderType === 'User' ? 'user' : 'assistant', 
                content: m.content || ''
              }));

            const chatRes = await agentService.unifiedChat({
              session_id: activeSessionId,
              message: inputText,
              is_admin: hasRole('Admin'),
              history: recentHistory
            });

            if (chatRes.data.success) {
              let rawText = chatRes.data.response || 'No response from the agent.';
              if (chatRes.data.raw_query_executed) {
                rawText = `Executing SQL:\n${chatRes.data.raw_query_executed}\n\n${rawText}`;
              }
              const isToon = rawText.includes(']{') && rawText.includes('}:');

              const assistantMessage: ChatMessageDto = {
                id: `assistant-chat-${Date.now()}`,
                content: rawText,
                senderType: 'Assistant',
                chatSessionId: activeSessionId,
                createdAt: new Date().toISOString(),
                artifacts: [],
                metadata: { isToon }
              };
              setMessages(prev => [...prev, assistantMessage]);

              // Check if the chatbot detected a generation intent - auto-trigger the action!
              if (chatRes.data.trigger_action && sessionState === 'ready') {
                const action = chatRes.data.trigger_action;

                // Add a small delay for UX, then trigger the generation
                setTimeout(() => {
                  handleGenerateClick(action);
                }, 500);
              } else if (chatRes.data.trigger_action && sessionState !== 'ready') {
                // User wants to generate but no artifacts uploaded yet
                const noArtifactsMsg: ChatMessageDto = {
                  id: `assistant-hint-${Date.now()}`,
                  content: `📁 **Please upload project artifacts first!**\n\nTo generate artifacts, I need context about your project. Please upload documents like:\n- Requirements documents\n- Meeting transcripts\n- Email threads\n- Technical specifications\n\nOnce uploaded, I'll be able to generate the requested artifacts for you.`,
                  senderType: 'Assistant',
                  chatSessionId: activeSessionId,
                  createdAt: new Date().toISOString(),
                  artifacts: []
                };
                setMessages(prev => [...prev, noArtifactsMsg]);
              }
            } else {
              setSendError(chatRes.data.error || 'Failed to get a response from the AI.');
            }
          } catch (agentErr: any) {
            setSendError(agentErr.response?.data?.error || 'Failed to connect to the unified intelligence agent.');
          }
        }

        // Update session title in sidebar if auto-renamed
        await loadSidebarData();
      }
      if (res.data.errors?.length) setSendError(res.data.errors.join('; '));
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string } } };
      setSendError(e.response?.data?.message || 'Failed to send message.');
    } finally { setSending(false); }
  };

  const processUploadedArtifacts = async (sessionId: string, artifacts: ArtifactDto[]) => {
    setProcessingArtifacts(true);
    setSessionState('processing_artifacts');

    try {
      const artifactRefs: ArtifactRef[] = artifacts.map(a => ({
        storage_path: a.blobUrl?.split('/artifacts/')[1]?.split('?')[0] || '',
        file_name: a.fileName ?? 'file',
        category: a.category
      }));

      const res = await agentService.processArtifacts({
        session_id: sessionId,
        artifacts: artifactRefs,
        session_title: activeSession?.title,
        author_name: user?.name || undefined,
      });

      if (res.data.success) {
        setSessionState('ready');
        setArtifactSummary(res.data.summary || `${artifacts.length} artifact(s) processed`);

        // Add assistant message about processing completion
        const assistantMessage: ChatMessageDto = {
          id: `assistant-${Date.now()}`,
          content: `**Artifacts processed successfully!**\n\n${res.data.summary}\n\nYou can now:\n- Generate an **Architecture Diagram**\n- Generate a **Data Flow Diagram**\n- Generate a **Presales Presentation**\n- Generate an **Azure Cost Report**\n\nUse the buttons below or type your request in the chat.`,
          senderType: 'Assistant',
          chatSessionId: sessionId,
          createdAt: new Date().toISOString(),
          artifacts: []
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        setSessionState('error');
        setSendError(res.data.error || 'Failed to process artifacts');
      }
    } catch {
      setSessionState('error');
      setSendError('Failed to process artifacts');
    } finally {
      setProcessingArtifacts(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFilesSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).filter(f => {
      const ext = '.' + f.name.split('.').pop()?.toLowerCase();
      return ALLOWED_EXTENSIONS.includes(ext);
    });
    setSelectedFiles(prev => [...prev, ...files]);
    setFileCategories(prev => [...prev, ...files.map(() => 'Document')]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setFileCategories(prev => prev.filter((_, i) => i !== index));
  };

  const addFiles = useCallback((fileList: FileList | File[]) => {
    const files = Array.from(fileList).filter(f => {
      const ext = '.' + f.name.split('.').pop()?.toLowerCase();
      return ALLOWED_EXTENSIONS.includes(ext);
    });
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
      setFileCategories(prev => [...prev, ...files.map(() => 'Document')]);
    }
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current += 1;
    if (e.dataTransfer.types.includes('Files')) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current -= 1;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  }, [addFiles]);

  const autoResizeTextarea = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }, []);

  // Session actions
  const handleRenameSession = async (id: string) => {
    if (!renameValue.trim()) { setRenamingSessionId(null); return; }
    await chatService.renameSession(id, renameValue.trim());
    setRenamingSessionId(null);
    await loadSidebarData();
  };

  const handleDeleteSession = async (id: string) => {
    if (!confirm('Delete this chat?')) return;
    await chatService.deleteSession(id);
    if (activeSessionId === id) { setActiveSessionId(null); setMessages([]); }
    await loadSidebarData();
  };

  const handleMoveSession = async (sessionId: string, groupId: string | null) => {
    await chatService.moveSession(sessionId, groupId);
    await loadSidebarData();
  };

  // Group actions
  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) return;
    await chatService.createGroup(newGroupName.trim());
    setNewGroupName('');
    setShowNewGroup(false);
    await loadSidebarData();
  };

  const handleRenameGroup = async (id: string) => {
    if (!renameGroupValue.trim()) { setRenamingGroupId(null); return; }
    await chatService.renameGroup(id, renameGroupValue.trim());
    setRenamingGroupId(null);
    await loadSidebarData();
  };

  const handleDeleteGroup = async (id: string) => {
    if (!confirm('Delete this group? Chats will become ungrouped.')) return;
    await chatService.deleteGroup(id);
    await loadSidebarData();
  };

  // ── Agent Generation Handlers ───────────────────────────────

  const getSessionArtifacts = (): ArtifactRef[] => {
    const artifacts: ArtifactRef[] = [];
    for (const msg of messages) {
      for (const a of msg.artifacts) {
        let storagePath = a.storagePath;

        // Fallback: extract from blobUrl and decode it properly
        if (!storagePath && a.blobUrl) {
          const extracted = a.blobUrl.split('/artifacts/')[1]?.split('?')[0] || '';
          // Decode the URL-encoded path to get the raw storage path
          try {
            storagePath = decodeURIComponent(extracted);
          } catch {
            storagePath = extracted;
          }
        }

        if (storagePath) {
          artifacts.push({ 
            storage_path: storagePath, 
            file_name: a.fileName ?? 'file', 
            category: a.category 
          });
        }
      }
    }
    return artifacts;
  };

  const handleGenerateClick = async (action: string) => {
    if (!activeSessionId) return;
    setAgentLoading(true);
    setClarifyAction(action);
    setGeneratedResults(null);
    setShowFeedback(false);
    setSendError('');

    // Handle DFD with React Flow
    if (action === 'dfd') {
      try {
        const res = await agentService.generateArchitecture({
          session_id: activeSessionId,
          artifacts: getSessionArtifacts(),
          instructions: inputText,
          session_title: activeSession?.title,
          phase_type: generationPhase,
          action: action,
        });

        if (res.data.success && res.data.graph) {
          setArchitectureGraph(res.data.graph);
          setArchitectureProjectName(res.data.project_name || 'DFD');
          setShowArchitectureModal(true);

          const agentMsg: ChatMessageDto = {
            id: `agent-arch-${Date.now()}`,
            content: `🏗 **Data Flow Diagram generated for ${res.data.project_name || 'your project'}!**\n\nYou can drag nodes to rearrange, then click "Save & Use in PPT" to finalize.`,
            senderType: 'Assistant',
            chatSessionId: activeSessionId,
            createdAt: new Date().toISOString(),
            artifacts: [],
          };
          setMessages(prev => [...prev, agentMsg]);
        } else {
          setSendError(res.data.error || 'Failed to generate Data Flow Diagram');
        }
      } catch (err) {
        const e = err as { response?: { data?: { error?: string } } };
        setSendError(e.response?.data?.error || 'Failed to generate Data Flow Diagram');
      } finally {
        setAgentLoading(false);
      }
      return;
    }

    // Handle architecture diagram via draw.io
    if (action === 'architecture_diagram') {
      try {
        const res = await agentService.generateDrawio({
          session_id: activeSessionId,
          artifacts: getSessionArtifacts(),
          instructions: inputText,
          session_title: activeSession?.title,
          phase_type: generationPhase,
        });

        if (res.data.success && res.data.xml) {
          setDrawioXml(res.data.xml);
          setDrawioProjectName(res.data.project_name || 'Architecture');
          setShowDrawioEditor(true);

          const agentMsg: ChatMessageDto = {
            id: `agent-arch-${Date.now()}`,
            content: `🏗 **Architecture diagram generated for ${res.data.project_name || 'your project'}!**\n\nThe diagram is now open for editing. You can:\n- Drag and rearrange components\n- Add or remove services\n- Edit labels and connections\n\nClick **Save & Close** when done to save to storage.`,
            senderType: 'Assistant',
            chatSessionId: activeSessionId,
            createdAt: new Date().toISOString(),
            artifacts: [],
          };
          setMessages(prev => [...prev, agentMsg]);
        } else {
          setSendError(res.data.error || 'Failed to generate architecture diagram');
        }
      } catch (err) {
        const e = err as { response?: { data?: { error?: string } } };
        setSendError(e.response?.data?.error || 'Failed to generate architecture diagram');
      } finally {
        setAgentLoading(false);
      }
      return;
    }

    // For other actions, use clarification flow
    try {
      const res = await agentService.clarify({
        session_id: activeSessionId,
        action,
        artifacts: getSessionArtifacts(),
        instructions: inputText,
        session_title: activeSession?.title,
      });

      // Check for artifact extraction errors
      if (!res.data.success) {
        const errorDetails = res.data.details?.join('\n') || res.data.error || 'Failed to read artifacts';
        setSendError(`❌ Artifact Error: ${errorDetails}\n\nPlease check:\n• Files were uploaded successfully to blob storage\n• Storage paths are correct\n• Azure Blob connection is working`);
        setAgentLoading(false);
        return;
      }

      // Show warnings if some artifacts failed but others succeeded
      if (res.data.warnings && res.data.warnings.length > 0) {
        console.warn('Artifact extraction warnings:', res.data.warnings);
        setSendError(`⚠️ Some artifacts couldn't be read:\n${res.data.warnings.join('\n')}`);
      }

      if (res.data.success && res.data.questions.length > 0) {
        setClarifyQuestions(res.data.questions);
        setClarifyProjectSummary(res.data.project_summary);
        setClarifyAnswers(Object.fromEntries(res.data.questions.map(q => [q.id, ''])));
        setShowClarifyModal(true);
      } else {
        await runGenerate(action, {});
      }
    } catch (err) {
      const e = err as { response?: { data?: { error?: string; details?: string[] } } };
      const errorMsg = e.response?.data?.error || 'Failed to analyze artifacts.';
      const details = e.response?.data?.details?.join('\n') || '';
      setSendError(details ? `${errorMsg}\n\n${details}` : errorMsg);
    } finally {
      setAgentLoading(false);
    }
  };

  const runGenerate = async (action: string, answers: Record<string, string>, prevPrompt?: string) => {
    if (!activeSessionId) return;
    setAgentLoading(true);
    setShowClarifyModal(false);
    try {
      const res = await agentService.generate({
        session_id: activeSessionId,
        action,
        artifacts: getSessionArtifacts(),
        instructions: inputText,
        answers,
        previous_prompt: prevPrompt,
        session_title: activeSession?.title,
        phase_type: generationPhase,
        author_name: user?.name || undefined,
      });
      if (res.data.success) {
        setGeneratedResults({
          images: res.data.images,
          pptUrl: res.data.ppt_url,
          excelUrl: res.data.excel_url,
          dallePrompt: res.data.dalle_prompt,
          dallePrompts: res.data.dalle_prompts,
          contextSummary: res.data.context_summary,
          action,
        });
        setShowFeedback(true);
        setShowPromptDetails(false);

        // Add assistant message summarising what was generated
        const parts: string[] = [];
        const actionLabel = action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        parts.push(`🤖 **${actionLabel} generated!**`);
        if (res.data.context_summary) parts.push(res.data.context_summary);
        if (res.data.images?.length) {
          res.data.images.filter(i => i.url).forEach(img => {
            parts.push(`📎 [${img.label}](${img.url})`);
          });
        }
        if (res.data.ppt_url) parts.push(`📎 [Download Presentation](${res.data.ppt_url})`);
        if (res.data.excel_url) parts.push(`📎 [Download Cost Report](${res.data.excel_url})`);

        const agentMsg: ChatMessageDto = {
          id: `agent-gen-${Date.now()}`,
          content: parts.join('\n\n'),
          senderType: 'Assistant',
          chatSessionId: activeSessionId,
          createdAt: new Date().toISOString(),
          artifacts: [],
        };
        setMessages(prev => [...prev, agentMsg]);
      } else {
        setSendError(res.data.error || 'Generation failed.');
      }
    } catch {
      setSendError('Generation request failed.');
    } finally {
      setAgentLoading(false);
    }
  };

  const handleFeedback = async (approved: boolean) => {
    if (!activeSessionId || !generatedResults) return;
    if (approved) {
      setShowFeedback(false);
      return;
    }
    if (!changeInstructions.trim()) return;
    setAgentLoading(true);
    try {
      const prevPrompt = generatedResults.dallePrompt || Object.values(generatedResults.dallePrompts || {})[0] || '';
      const res = await agentService.feedback({
        session_id: activeSessionId,
        action: generatedResults.action || clarifyAction,
        feedback: 'changes_needed',
        change_instructions: changeInstructions,
        previous_prompt: prevPrompt,
        artifacts: getSessionArtifacts(),
        session_title: activeSession?.title,
        phase_type: generationPhase,
      });
      if (res.data.success && (res.data.images || res.data.ppt_url || res.data.excel_url)) {
        setGeneratedResults({
          images: res.data.images,
          pptUrl: res.data.ppt_url,
          excelUrl: res.data.excel_url,
          action: generatedResults.action,
        });
        setChangeInstructions('');

        // Add assistant message about regenerated results
        const parts: string[] = ['🔄 **Regenerated based on your feedback!**'];
        if (res.data.images?.length) {
          res.data.images.filter(i => i.url).forEach(img => {
            parts.push(`📎 [${img.label}](${img.url})`);
          });
        }
        if (res.data.ppt_url) parts.push(`📎 [Download Presentation](${res.data.ppt_url})`);
        if (res.data.excel_url) parts.push(`📎 [Download Cost Report](${res.data.excel_url})`);

        const agentMsg: ChatMessageDto = {
          id: `agent-regen-${Date.now()}`,
          content: parts.join('\n\n'),
          senderType: 'Assistant',
          chatSessionId: activeSessionId,
          createdAt: new Date().toISOString(),
          artifacts: [],
        };
        setMessages(prev => [...prev, agentMsg]);
      }
    } catch {
      setSendError('Feedback request failed.');
    } finally {
      setAgentLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Handle architecture diagram PNG export and upload
  const handleArchitectureExport = async (blob: Blob) => {
    if (!activeSessionId) return;
    setArchitectureSaving(true);

    try {
      // Convert blob to base64
      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          const result = reader.result as string;
          const base64 = result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
      });
      reader.readAsDataURL(blob);
      const base64Data = await base64Promise;

      // Upload to backend
      const res = await agentService.uploadArchitectureImage({
        imageData: base64Data,
        projectName: architectureProjectName,
        contentType: 'image/png',
        sessionId: activeSessionId,
        sessionTitle: activeSession?.title,
      });

      if (res.data.success) {
        // Add message about saved architecture
        const assistantMessage: ChatMessageDto = {
          id: `assistant-arch-${Date.now()}`,
          content: `✅ **Architecture diagram saved!**\n\nThe diagram has been uploaded to storage and is ready for use in presentations.\n\n[Download Architecture Diagram](${res.data.url})`,
          senderType: 'Assistant',
          chatSessionId: activeSessionId,
          createdAt: new Date().toISOString(),
          artifacts: []
        };
        setMessages(prev => [...prev, assistantMessage]);
        setShowArchitectureModal(false);
        setArchitectureGraph(null);
      } else {
        setSendError(res.data.error || 'Failed to save architecture diagram');
      }
    } catch {
      setSendError('Failed to upload architecture diagram');
    } finally {
      setArchitectureSaving(false);
    }
  };

  const handleDrawioSave = async (xml: string, imageData?: string) => {
    if (!activeSessionId) return;


    try {
      const res = await agentService.saveDrawio({
        session_id: activeSessionId,
        xml,
        project_name: drawioProjectName,
        session_title: activeSession?.title,
        image_data: imageData || undefined,
        export_format: imageData ? 'png' : 'xml',
      });

      if (res.data.success) {
        const links: string[] = [];
        if (res.data.xml_url) links.push(`[Download Draw.io XML](${res.data.xml_url})`);
        if (res.data.image_url) links.push(`[Download Architecture PNG](${res.data.image_url})`);

        const assistantMessage: ChatMessageDto = {
          id: `assistant-arch-save-${Date.now()}`,
          content: `✅ **Architecture diagram saved!**\n\nThe diagram has been saved to storage.${
            res.data.image_url ? ' The exported image is ready for use in presentations.' : ''
          }\n\n${links.join(' · ')}`,
          senderType: 'Assistant',
          chatSessionId: activeSessionId,
          createdAt: new Date().toISOString(),
          artifacts: [],
        };
        setMessages(prev => [...prev, assistantMessage]);
        setShowDrawioEditor(false);
        setDrawioXml(null);
      } else {
        setSendError(res.data.error || 'Failed to save architecture diagram');
      }
    } catch {
      setSendError('Failed to save architecture diagram');
    } finally {

    }
  };

  const ungroupedSessions = sessions.filter(s => !s.chatGroupId);

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    if (bytes < 1024 * 1024) return ` · ${(bytes / 1024).toFixed(0)}KB`;
    return ` · ${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  return (
    <div className="chat-layout">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="chat-sidebar">
        <div className="chat-sidebar-header">
          <img
            src="https://www.optimusinfo.com/wp-content/uploads/2014/11/optimusinfologo.png"
            alt="OptiStudio"
            className="chat-sidebar-logo"
          />
          <button className="btn-new-chat" onClick={() => handleNewChat()}>
            <EditIcon style={{ fontSize: 18, marginRight: 6 }} /> New Chat
          </button>
        </div>

        <div className="chat-sidebar-scroll">
          {/* Groups */}
          {groups.map(group => (
            <div key={group.id} className="chat-group-item">
              <div className="chat-group-header">
                <ExpandMoreIcon style={{ fontSize: 18, marginRight: 6 }} />
                {renamingGroupId === group.id ? (
                  <input
                    className="chat-inline-edit"
                    value={renameGroupValue}
                    autoFocus
                    onChange={e => setRenameGroupValue(e.target.value)}
                    onBlur={() => handleRenameGroup(group.id)}
                    onKeyDown={e => { if (e.key === 'Enter') handleRenameGroup(group.id); if (e.key === 'Escape') setRenamingGroupId(null); }}
                  />
                ) : (
                  <span style={{ flex: 1 }}>{group.name}</span>
                )}
                <div className="chat-group-actions">
                  <button
                    className="chat-session-action-btn"
                    title="Add chat to group"
                    onClick={() => handleNewChat(group.id)}
                  ><AddIcon style={{ fontSize: 16 }} /></button>
                  <button
                    className="chat-session-action-btn"
                    title="Rename group"
                    onClick={() => { setRenamingGroupId(group.id); setRenameGroupValue(group.name); }}
                  ><EditIcon style={{ fontSize: 16 }} /></button>
                  <button
                    className="chat-session-action-btn"
                    title="Delete group"
                    onClick={() => handleDeleteGroup(group.id)}
                  ><DeleteIcon style={{ fontSize: 16 }} /></button>
                </div>
              </div>
              {sessions.filter(s => s.chatGroupId === group.id).map(s => (
                <SessionItem
                  key={s.id}
                  session={s}
                  active={activeSessionId === s.id}
                  renamingId={renamingSessionId}
                  renameValue={renameValue}
                  groups={groups}
                  onSelect={() => setActiveSessionId(s.id)}
                  onRenameStart={() => { setRenamingSessionId(s.id); setRenameValue(s.title); }}
                  onRenameChange={setRenameValue}
                  onRenameSubmit={() => handleRenameSession(s.id)}
                  onRenameCancel={() => setRenamingSessionId(null)}
                  onDelete={() => handleDeleteSession(s.id)}
                  onMove={(gid) => handleMoveSession(s.id, gid)}
                />
              ))}
            </div>
          ))}

          {/* Ungrouped */}
          {ungroupedSessions.length > 0 && (
            <>
              <div className="chat-section-label">Chats</div>
              {ungroupedSessions.map(s => (
                <SessionItem
                  key={s.id}
                  session={s}
                  active={activeSessionId === s.id}
                  renamingId={renamingSessionId}
                  renameValue={renameValue}
                  groups={groups}
                  onSelect={() => setActiveSessionId(s.id)}
                  onRenameStart={() => { setRenamingSessionId(s.id); setRenameValue(s.title); }}
                  onRenameChange={setRenameValue}
                  onRenameSubmit={() => handleRenameSession(s.id)}
                  onRenameCancel={() => setRenamingSessionId(null)}
                  onDelete={() => handleDeleteSession(s.id)}
                  onMove={(gid) => handleMoveSession(s.id, gid)}
                />
              ))}
            </>
          )}

          {/* Create group */}
          <div className="chat-section-label">
            Groups
            <button onClick={() => setShowNewGroup(v => !v)} title="New group"><AddIcon style={{ fontSize: 16, verticalAlign: 'middle' }} /></button>
          </div>
          {showNewGroup && (
              <div style={{ padding: '4px 12px 8px', display: 'flex', gap: '6px' }}>
              <input
                className="chat-inline-edit"
                placeholder="Group name"
                value={newGroupName}
                autoFocus
                onChange={e => setNewGroupName(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleCreateGroup(); if (e.key === 'Escape') setShowNewGroup(false); }}
              />
              <button onClick={handleCreateGroup} className="chat-session-action-btn" style={{ color: '#10a37f' }}><CheckIcon style={{ fontSize: 14 }} /></button>
            </div>
          )}

          {/* Approve Decks — Admin only */}
          {hasRole('Admin') && (
            <div style={{ padding: '12px 12px 4px' }}>
              <button
                onClick={() => navigate('/admin/approve')}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  border: '1.5px solid #16a34a',
                  background: '#f0fdf4',
                  color: '#15803d',
                  fontWeight: 600,
                  fontSize: 13,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <CheckCircleOutlineIcon style={{ fontSize: 18 }} />
                Approve Decks
              </button>
            </div>
          )}
        </div>

        <div className="chat-sidebar-footer">
          <div className="chat-user-info">
            <div className="chat-user-avatar">
              {(user?.name || '?').charAt(0).toUpperCase()}
            </div>
            <span style={{ fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 140 }}>
              {user?.name}
            </span>
          </div>
          <button className="btn-sidebar-logout" onClick={handleLogout} title="Sign out"><PowerSettingsNewIcon /></button>
        </div>
      </aside>

      {/* ── Main Area ────────────────────────────────────────── */}
      <main
        className="chat-main"
        onDragEnter={activeSessionId && !processingArtifacts ? handleDragEnter : undefined}
        onDragOver={activeSessionId && !processingArtifacts ? handleDragOver : undefined}
        onDragLeave={activeSessionId && !processingArtifacts ? handleDragLeave : undefined}
        onDrop={activeSessionId && !processingArtifacts ? handleDrop : undefined}
      >
        {/* Drag & Drop Overlay */}
        {isDragging && (
          <div className="drag-drop-overlay">
            <div className="drag-drop-content">
              <CloudUploadIcon style={{ fontSize: 48, color: '#c62828' }} />
              <p>Drop files here to upload</p>
              <span>{ALLOWED_EXTENSIONS.join(', ')}</span>
            </div>
          </div>
        )}
        <div className="chat-main-header">
          <button
            onClick={() => navigate('/dashboard')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, color: 'var(--text-light)' }}
          >
            ← Dashboard
          </button>
          <span className="chat-main-title">
            {activeSession ? activeSession.title : 'Presales Chat'}
          </span>
        </div>

        {/* Messages */}
        <div className="chat-messages-area">
          {!activeSessionId ? (
            <div className="chat-empty-state">
              <ChatBubbleOutlineIcon style={{ fontSize: 48 }} />
              <h2>Presales Workspace</h2>
              <p>Start a new chat or select one from the sidebar.<br />Upload artifacts and provide instructions to generate presales decks.</p>
              <button className="btn-primary" style={{ width: 'auto', padding: '10px 24px' }} onClick={() => handleNewChat()}>
                Start New Chat
              </button>
            </div>
          ) : loadingMessages ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <div className="loading-spinner" />
            </div>
          ) : messages.length === 0 ? (
            <div className="chat-empty-state">
              <DescriptionIcon style={{ fontSize: 40 }} />
              <p>Send a message or upload artifacts to get started.</p>
            </div>
          ) : (
            messages.map(msg => {
              const isUser = msg.senderType === 'User';
              const bubbleBg = isUser ? '#c62828' : '#f0f0f0';
              const textColor = isUser ? '#ffffff' : '#1a1a1a';
              return (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                    padding: '8px 24px',
                    gap: '12px',
                    maxWidth: '820px',
                    width: '100%',
                    margin: '0 auto',
                    alignItems: 'flex-start',
                  }}
                >
                  {/* Avatar */}
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: '50%',
                      background: isUser ? '#c62828' : '#10a37f',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontSize: 14,
                      flexShrink: 0,
                    }}
                  >
                    {isUser ? (user?.name || 'U').charAt(0).toUpperCase() : <SmartToyIcon style={{ fontSize: 18 }} />}
                  </div>

                  {/* Bubble — always rendered with solid background */}
                  <div style={{ maxWidth: 'calc(100% - 48px)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div
                      style={{
                        padding: '10px 16px',
                        borderRadius: 12,
                        background: bubbleBg,
                        color: textColor,
                        fontSize: 14.5,
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        borderBottomRightRadius: isUser ? 4 : 12,
                        borderBottomLeftRadius: isUser ? 12 : 4,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 8,
                      }}
                    >
                      {/* Text */}
                      {msg.content && (
                        msg.senderType === 'Assistant' && msg.metadata?.isToon 
                          ? <ToonRenderer text={msg.content} /> 
                          : <span>{msg.content}</span>
                      )}

                      {/* Attachments — inside the bubble so they inherit its background */}
                      {msg.artifacts.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: msg.content ? 4 : 0 }}>
                          {msg.artifacts.map(a => (
                            <div
                              key={a.id}
                              title="Click to download"
                              onClick={async () => {
                                try {
                                  const res = await chatService.getArtifactDownloadUrl(a.id);
                                  if (res.data.success) window.open(res.data.url, '_blank');
                                } catch {
                                  alert('Could not generate download link.');
                                }
                              }}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                background: isUser ? 'rgba(0,0,0,0.18)' : 'rgba(0,0,0,0.08)',
                                color: textColor,
                                padding: '5px 10px',
                                borderRadius: 8,
                                fontSize: 12.5,
                                cursor: 'pointer',
                                border: `1px solid ${isUser ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.12)'}`,
                              }}
                            >
                              <AttachFileIcon style={{ fontSize: 16 }} />
                              <span style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {a.fileName ?? 'File'}{formatFileSize(a.fileSizeBytes)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Meta */}
                    <div style={{ fontSize: 11, color: '#999', textAlign: isUser ? 'right' : 'left', paddingInline: 4 }}>
                      {msg.userName ?? 'Assistant'} · {formatTime(msg.createdAt)}
                    </div>
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        {activeSessionId && (
          <div className="chat-input-area">
            <div className="chat-input-wrapper">
              {/* Processing Indicator */}
              {processingArtifacts && (
                <div style={{
                  background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                  border: '1px solid #f59e0b',
                  borderRadius: 8,
                  padding: '12px 16px',
                  marginBottom: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <div className="loading-spinner" style={{ width: 20, height: 20 }} />
                  <div>
                    <strong style={{ color: '#92400e' }}>Processing artifacts...</strong>
                    <p style={{ margin: 0, fontSize: 12, color: '#b45309' }}>
                      Extracting text and preparing for generation. Please wait.
                    </p>
                  </div>
                </div>
              )}

              {/* Session Ready Indicator */}
              {sessionState === 'ready' && artifactSummary && !processingArtifacts && (
                <div style={{
                  background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
                  border: '1px solid #10b981',
                  borderRadius: 8,
                  padding: '10px 14px',
                  marginBottom: 10,
                  fontSize: 13,
                  color: '#065f46'
                }}>
                  ✅ <strong>Ready to generate!</strong> {artifactSummary}
                </div>
              )}

              {sendError && (
                <p style={{ color: '#dc3545', fontSize: 13, marginBottom: 6 }}>⚠ {sendError}</p>
              )}

              {selectedFiles.length > 0 && (
                <div className="chat-file-previews">
                  {selectedFiles.map((file, i) => (
                    <div key={i} className="chat-file-preview">
                      <AttachFileIcon style={{ fontSize: 16 }} />
                      <span style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 12.5 }}>
                        {file.name}
                      </span>
                      <select
                        value={fileCategories[i]}
                        onChange={e => setFileCategories(prev => { const n = [...prev]; n[i] = e.target.value; return n; })}
                      >
                        {ARTIFACT_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                      <button className="chat-file-remove" onClick={() => removeFile(i)}><CloseIcon style={{ fontSize: 14 }} /></button>
                    </div>
                  ))}
                </div>
              )}

              <div className="chat-input-box">
                <button
                  className="btn-attach"
                  onClick={() => fileInputRef.current?.click()}
                  title="Attach files"
                  disabled={processingArtifacts}
                >
                  <AttachFileIcon />
                </button> 
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept={ALLOWED_EXTENSIONS.join(',')}
                  style={{ display: 'none' }}
                  onChange={handleFilesSelected}
                />
                <textarea
                  ref={textareaRef}
                  className="chat-textarea"
                  placeholder={processingArtifacts ? "Processing artifacts... please wait" : "Message OptiStudio…"}
                  value={inputText}
                  rows={1}
                  disabled={processingArtifacts}
                  onChange={e => { setInputText(e.target.value); autoResizeTextarea(); }}
                  onKeyDown={handleKeyDown}
                  style={{ opacity: processingArtifacts ? 0.6 : 1 }}
                />
                <button
                  className="btn-send"
                  onClick={handleSend}
                  disabled={sending || processingArtifacts || (!inputText.trim() && selectedFiles.length === 0)}
                  title="Send (Enter)"
                >
                  {sending ? '…' : <SendIcon style={{ transform: 'rotate(-45deg)', fontSize: 16 }} />}
                </button> 
              </div>
              <p style={{ fontSize: 11.5, color: '#aaa', marginTop: 6, textAlign: 'center' }}>
                Shift+Enter for new line · Max 15 MB per file · 50 MB total
              </p>

              {/* ── Generation Buttons — only after artifacts are ready ── */}
              {sessionState === 'ready' && !processingArtifacts && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 10, alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#f5f5f5', padding: '4px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#666', padding: '0 8px' }}>Target:</span>
                  <button 
                    onClick={() => setGenerationPhase('mvp')}
                    style={{
                      padding: '4px 12px', borderRadius: '6px', fontSize: 13, fontWeight: 600, border: 'none',
                      background: generationPhase === 'mvp' ? '#c62828' : 'transparent',
                      color: generationPhase === 'mvp' ? '#fff' : '#666',
                      cursor: 'pointer', transition: 'all 0.2s'
                    }}
                  >MVP</button>
                  <button 
                    onClick={() => setGenerationPhase('poc')}
                    style={{
                      padding: '4px 12px', borderRadius: '6px', fontSize: 13, fontWeight: 600, border: 'none',
                      background: generationPhase === 'poc' ? '#c62828' : 'transparent',
                      color: generationPhase === 'poc' ? '#fff' : '#666',
                      cursor: 'pointer', transition: 'all 0.2s'
                    }}
                  >POC</button>
                </div>
                <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                  {['architecture_diagram', 'dfd', 'presales_ppt', 'cost_report'].map(action => (
                    <button
                    key={action}
                    onClick={() => handleGenerateClick(action)}
                    disabled={agentLoading}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 8,
                      border: '1.5px solid #c62828',
                      background: agentLoading ? '#eee' : '#fff',
                      color: '#c62828',
                      fontWeight: 600,
                      fontSize: 13,
                      cursor: agentLoading ? 'not-allowed' : 'pointer',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={e => { if (!agentLoading) (e.target as HTMLElement).style.background = '#fef2f2'; }}
                    onMouseLeave={e => { (e.target as HTMLElement).style.background = agentLoading ? '#eee' : '#fff'; }}
                  >
                    {action === 'architecture_diagram' && (<><AccountTreeIcon style={{ fontSize: 16, marginRight: 8 }} />Architecture Diagram</>)}
                    {action === 'dfd' && (<><CallSplitIcon style={{ fontSize: 16, marginRight: 8 }} />Data Flow Diagram</>)}
                    {action === 'presales_ppt' && (<><SlideshowIcon style={{ fontSize: 16, marginRight: 8 }} />Presales PPT</>)}
                    {action === 'cost_report' && (<><AttachMoneyIcon style={{ fontSize: 16, marginRight: 8 }} />Azure Cost Report</>)}
                  </button>
                ))}
                </div>
              </div>
              )}

              {/* Show buttons even if no artifacts but messages exist - for demo */}
              {sessionState !== 'ready' && messages.length > 0 && messages.some(m => m.artifacts.length > 0) && !processingArtifacts && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 10, alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#f5f5f5', padding: '4px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#666', padding: '0 8px' }}>Target:</span>
                  <button 
                    onClick={() => setGenerationPhase('mvp')}
                    style={{
                      padding: '4px 12px', borderRadius: '6px', fontSize: 13, fontWeight: 600, border: 'none',
                      background: generationPhase === 'mvp' ? '#c62828' : 'transparent',
                      color: generationPhase === 'mvp' ? '#fff' : '#666',
                      cursor: 'pointer', transition: 'all 0.2s'
                    }}
                  >MVP</button>
                  <button 
                    onClick={() => setGenerationPhase('poc')}
                    style={{
                      padding: '4px 12px', borderRadius: '6px', fontSize: 13, fontWeight: 600, border: 'none',
                      background: generationPhase === 'poc' ? '#c62828' : 'transparent',
                      color: generationPhase === 'poc' ? '#fff' : '#666',
                      cursor: 'pointer', transition: 'all 0.2s'
                    }}
                  >POC</button>
                </div>
                <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                  {['architecture_diagram', 'dfd', 'presales_ppt', 'cost_report'].map(action => (
                    <button
                    key={action}
                    onClick={() => handleGenerateClick(action)}
                    disabled={agentLoading}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 8,
                      border: '1.5px solid #c62828',
                      background: agentLoading ? '#eee' : '#fff',
                      color: '#c62828',
                      fontWeight: 600,
                      fontSize: 13,
                      cursor: agentLoading ? 'not-allowed' : 'pointer',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={e => { if (!agentLoading) (e.target as HTMLElement).style.background = '#fef2f2'; }}
                    onMouseLeave={e => { (e.target as HTMLElement).style.background = agentLoading ? '#eee' : '#fff'; }}
                  >
                    {action === 'architecture_diagram' && (<><AccountTreeIcon style={{ fontSize: 16, marginRight: 8 }} />Architecture Diagram</>)}
                    {action === 'dfd' && (<><CallSplitIcon style={{ fontSize: 16, marginRight: 8 }} />Data Flow Diagram</>)}
                    {action === 'presales_ppt' && (<><SlideshowIcon style={{ fontSize: 16, marginRight: 8 }} />Presales PPT</>)}
                    {action === 'cost_report' && (<><AttachMoneyIcon style={{ fontSize: 16, marginRight: 8 }} />Azure Cost Report</>)}
                  </button>
                ))}
                </div>
              </div>
              )}

              {agentLoading && (
                <p style={{ fontSize: 12, color: '#c62828', textAlign: 'center', marginTop: 6, fontWeight: 500 }}>
                  <HourglassEmptyIcon style={{ verticalAlign: 'middle', marginRight: 6 }} /> Generating… this may take 30-60 seconds
                </p>
              )}
            </div>
          </div>
        )}

        {/* ── Generated Results + Feedback ────────────────────── */}
        {generatedResults && showFeedback && (
          <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              background: '#fff', borderRadius: 12, padding: 24, maxWidth: 900, width: '95%',
              maxHeight: '90vh', overflowY: 'auto', boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
            }}>
              <h3 style={{ margin: '0 0 8px', color: '#333' }}>Generated Results</h3>

              {/* Context Summary */}
              {generatedResults.contextSummary && (
                <div style={{
                  background: '#f0fdf4',
                  border: '1px solid #86efac',
                  borderRadius: 8,
                  padding: '12px 16px',
                  marginBottom: 16,
                  fontSize: 13,
                  color: '#166534',
                  lineHeight: 1.5
                }}>
                  <strong>📋 What was generated:</strong>
                  <p style={{ margin: '6px 0 0' }}>{generatedResults.contextSummary}</p>
                </div>
              )}

              {/* Images with thumbnails */}
              {generatedResults.images?.filter(i => i.url).map((img, idx) => (
                <div key={idx} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <p style={{ fontWeight: 600, fontSize: 14, color: '#333', margin: 0 }}>{img.label}</p>
                    <a
                      href={img.url!}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4,
                        padding: '6px 12px',
                        background: '#c62828',
                        color: '#fff',
                        borderRadius: 6,
                        textDecoration: 'none',
                        fontSize: 12,
                        fontWeight: 600
                      }}
                    >
                      <DownloadIcon style={{ marginRight: 6 }} />Download
                    </a>
                  </div>
                  <img
                    src={img.url!}
                    alt={img.label}
                    style={{ maxWidth: '100%', maxHeight: 400, borderRadius: 8, border: '1px solid #eee', cursor: 'pointer' }}
                    onClick={() => window.open(img.url!, '_blank')}
                    title="Click to view full size"
                  />
                </div>
              ))}

              {/* PPT download */}
              {generatedResults.pptUrl && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 16,
                    padding: 16,
                    background: '#fef2f2',
                    borderRadius: 8,
                    border: '1px solid #fecaca'
                  }}>
                    <SlideshowIcon style={{ fontSize: 48 }} />
                    <div style={{ flex: 1 }}>
                      <p style={{ margin: 0, fontWeight: 600, color: '#333' }}>Presales Presentation</p>
                      <p style={{ margin: '4px 0 0', fontSize: 12, color: '#666' }}>
                        PowerPoint presentation with all sections generated from your artifacts
                      </p>
                    </div>
                    <a
                      href={generatedResults.pptUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex', alignItems: 'center', gap: 8,
                        padding: '10px 20px', background: '#c62828', color: '#fff',
                        borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 14,
                      }}
                    >
                      <DownloadIcon style={{ marginRight: 8 }} />Download PPT
                    </a>
                  </div>
                </div>
              )}

              {/* Excel preview + download */}
              {generatedResults.excelUrl && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 16,
                    padding: 16,
                    background: '#f0fdf4',
                    borderRadius: 8,
                    border: '1px solid #86efac'
                  }}>
                    <AttachMoneyIcon style={{ fontSize: 48 }} />
                    <div style={{ flex: 1 }}>
                      <p style={{ margin: 0, fontWeight: 600, color: '#333' }}>Azure Cost Report</p>
                      <p style={{ margin: '4px 0 0', fontSize: 12, color: '#666' }}>
                        Detailed cost estimate with environment breakdowns and recommendations
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <a
                        href={`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(generatedResults.excelUrl)}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: 8,
                          padding: '10px 20px', background: '#fff', color: '#1b5e20',
                          borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 14,
                          border: '1.5px solid #1b5e20',
                        }}
                      >
                        <VisibilityIcon style={{ fontSize: 18 }} />Preview
                      </a>
                      <a
                        href={generatedResults.excelUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: 8,
                          padding: '10px 20px', background: '#1b5e20', color: '#fff',
                          borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 14,
                        }}
                      >
                        <DownloadIcon style={{ marginRight: 8 }} />Download Excel
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* Collapsible Prompt Details */}
              {(generatedResults.dallePrompt || generatedResults.dallePrompts) && (
                <div style={{ marginBottom: 16 }}>
                  <button
                    onClick={() => setShowPromptDetails(!showPromptDetails)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      background: 'none',
                      border: '1px solid #ddd',
                      borderRadius: 6,
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: 13,
                      color: '#666',
                      width: '100%',
                      justifyContent: 'space-between'
                    }}
                  >
                    <span><BuildIcon style={{ fontSize: 16, marginRight: 6 }} /> Technical Details (Prompt Used)</span>
                    <span>{showPromptDetails ? '▲' : '▼'}</span>
                  </button>

                  {showPromptDetails && (
                    <div style={{
                      marginTop: 8,
                      padding: 12,
                      background: '#f8f9fa',
                      borderRadius: 6,
                      border: '1px solid #e9ecef',
                      maxHeight: 300,
                      overflowY: 'auto'
                    }}>
                      <p style={{ margin: '0 0 8px', fontSize: 11, color: '#666' }}>
                        This prompt was used to generate the image. Save it to regenerate identical results.
                      </p>
                      {generatedResults.dallePrompt && (
                        <pre style={{
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          fontSize: 11,
                          color: '#333',
                          fontFamily: 'monospace'
                        }}>
                          {generatedResults.dallePrompt}
                        </pre>
                      )}
                      {generatedResults.dallePrompts && Object.entries(generatedResults.dallePrompts).map(([key, prompt]) => (
                        <div key={key} style={{ marginTop: 12 }}>
                          <strong style={{ fontSize: 11, color: '#666' }}>{key.toUpperCase()}:</strong>
                          <pre style={{
                            margin: '4px 0 0',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            fontSize: 11,
                            color: '#333',
                            fontFamily: 'monospace'
                          }}>
                            {prompt}
                          </pre>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Feedback buttons */}
              <div style={{ display: 'flex', gap: 10, marginTop: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                <button
                  onClick={() => handleFeedback(true)}
                  style={{
                    padding: '10px 20px', borderRadius: 8, border: 'none',
                    background: '#16a34a', color: '#fff', fontWeight: 600, cursor: 'pointer',
                  }}
                >
                  ✓ This is Good
                </button>
                <div style={{ flex: 1, display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    placeholder="Describe changes needed…"
                    value={changeInstructions}
                    onChange={e => setChangeInstructions(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleFeedback(false); }}
                    style={{
                      flex: 1, padding: '10px 12px', borderRadius: 8,
                      border: '1.5px solid #ddd', fontSize: 13, outline: 'none',
                    }}
                  />
                  <button
                    onClick={() => handleFeedback(false)}
                    disabled={!changeInstructions.trim() || agentLoading}
                    style={{
                      padding: '10px 16px', borderRadius: 8, border: 'none',
                      background: '#c62828', color: '#fff', fontWeight: 600, cursor: 'pointer',
                      opacity: !changeInstructions.trim() || agentLoading ? 0.5 : 1,
                    }}
                  >
                    {agentLoading ? <HourglassEmptyIcon style={{ fontSize: 16 }} /> : (<><RefreshIcon style={{ fontSize: 16, marginRight: 8 }} />Regenerate</>)}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Clarification Modal ─────────────────────────────── */}
        {showClarifyModal && (
          <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              background: '#fff', borderRadius: 12, padding: 24, maxWidth: 600, width: '90%',
              maxHeight: '80vh', overflowY: 'auto', boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
            }}>
              <h3 style={{ margin: '0 0 8px', color: '#333' }}>Clarification Needed</h3>
              {clarifyProjectSummary && (
                <p style={{ fontSize: 13, color: '#666', marginBottom: 16, lineHeight: 1.5 }}>
                  <strong>What I understood:</strong> {clarifyProjectSummary}
                </p>
              )}

              {clarifyQuestions.map(q => (
                <div key={q.id} style={{ marginBottom: 14 }}>
                  <label style={{ fontSize: 13, fontWeight: 600, color: '#333', display: 'block', marginBottom: 4 }}>
                    {q.question}
                  </label>
                  <p style={{ fontSize: 11, color: '#999', margin: '0 0 4px' }}>
                    Default if skipped: {q.default}
                  </p>
                  <input
                    value={clarifyAnswers[q.id] || ''}
                    onChange={e => setClarifyAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                    placeholder={q.default}
                    style={{
                      width: '100%', padding: '8px 10px', borderRadius: 6,
                      border: '1px solid #ddd', fontSize: 13, outline: 'none',
                    }}
                  />
                </div>
              ))}

              <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
                <button
                  onClick={() => setShowClarifyModal(false)}
                  style={{
                    padding: '10px 20px', borderRadius: 8, border: '1px solid #ddd',
                    background: '#fff', color: '#555', cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    const answers: Record<string, string> = {};
                    clarifyQuestions.forEach(q => {
                      answers[q.question] = clarifyAnswers[q.id] || q.default;
                    });
                    runGenerate(clarifyAction, answers);
                  }}
                  disabled={agentLoading}
                  style={{
                    padding: '10px 20px', borderRadius: 8, border: 'none',
                    background: '#c62828', color: '#fff', fontWeight: 600, cursor: 'pointer',
                    opacity: agentLoading ? 0.5 : 1,
                  }}
                >
                  {agentLoading ? <HourglassEmptyIcon style={{ verticalAlign: 'middle', marginRight: 6 }} /> : (<><RocketLaunchIcon style={{ fontSize: 16, marginRight: 8 }} />Generate</>)}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Data Flow Diagram Modal (React Flow) ─────────── */}
        {showArchitectureModal && architectureGraph && (
          <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              background: '#fff', borderRadius: 12, padding: 24, 
              width: '95%', maxWidth: 1200, height: '85vh',
              display: 'flex', flexDirection: 'column', overflow: 'hidden',
              boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
            }}>
              {/* Header */}
              <div style={{ 
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid #eee',
                flexShrink: 0,
              }}>
                <div>
                  <h3 style={{ margin: 0, color: '#333' }}>
                    <AccountTreeIcon style={{ verticalAlign: 'middle', marginRight: 8 }} />
                    {architectureProjectName} - Diagram
                  </h3>
                  <p style={{ margin: '4px 0 0', fontSize: 12, color: '#666' }}>
                    Drag nodes to rearrange • Click to select • Double-click labels to edit
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => {
                      setShowArchitectureModal(false);
                      setArchitectureGraph(null);
                    }}
                    style={{
                      padding: '8px 16px', borderRadius: 6, border: '1px solid #ddd',
                      background: '#fff', color: '#555', cursor: 'pointer', fontSize: 13,
                    }}
                  >
                    <CloseIcon style={{ fontSize: 16, marginRight: 4 }} /> Close
                  </button>
                </div>
              </div>

                            {/* React Flow Diagram */}
                            <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
                              <Suspense fallback={<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>Loading diagram...</div>}>
                                <ArchitectureDiagram
                                  graph={architectureGraph}
                                  projectName={architectureProjectName}
                                  onExportPng={handleArchitectureExport}
                                />
                              </Suspense>
                            </div>

                            {/* Footer Actions */}
                            <div style={{ 
                              display: 'flex', justifyContent: 'flex-end', gap: 10,
                              marginTop: 16, paddingTop: 12, borderTop: '1px solid #eee',
                              flexShrink: 0,
                            }}>
                <button
                  onClick={() => {
                    setShowArchitectureModal(false);
                    setArchitectureGraph(null);
                  }}
                  style={{
                    padding: '10px 20px', borderRadius: 8, border: '1px solid #ddd',
                    background: '#fff', color: '#555', cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    // Trigger export from the ArchitectureDiagram component
                    // The component will call onExportPng with the blob
                    const diagramEl = document.querySelector('.react-flow') as HTMLElement;
                    if (diagramEl) {
                      const { toPng } = await import('html-to-image');
                      const dataUrl = await toPng(diagramEl, { backgroundColor: '#fff', quality: 1, pixelRatio: 2 });
                      const res = await fetch(dataUrl);
                      const blob = await res.blob();
                      handleArchitectureExport(blob);
                    }
                  }}
                  disabled={architectureSaving}
                  style={{
                    padding: '10px 24px', borderRadius: 8, border: 'none',
                    background: '#c62828', color: '#fff', fontWeight: 600, cursor: 'pointer',
                    opacity: architectureSaving ? 0.7 : 1,
                    display: 'flex', alignItems: 'center', gap: 8,
                  }}
                >
                  {architectureSaving ? (
                    <><HourglassEmptyIcon style={{ fontSize: 16 }} /> Saving...</>
                  ) : (
                    <><SaveIcon style={{ fontSize: 16 }} /> Save & Use in PPT</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Draw.io Editor (Full-screen iframe) ─────────────── */}
        {showDrawioEditor && drawioXml && (
          <Suspense fallback={<div style={{ position: 'fixed', inset: 0, zIndex: 1100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff' }}>Loading architecture diagram editor...</div>}>
            <DrawioEditor
              xml={drawioXml}
              title={`${drawioProjectName} - Architecture Diagram`}
              onSave={handleDrawioSave}
              onClose={() => {
                setShowDrawioEditor(false);
                setDrawioXml(null);
              }}
            />
          </Suspense>
        )}
      </main>
    </div>
  );
}

// ── SessionItem component ─────────────────────────────────────
interface SessionItemProps {
  session: ChatSessionDto;
  active: boolean;
  renamingId: string | null;
  renameValue: string;
  groups: ChatGroupDto[];
  onSelect: () => void;
  onRenameStart: () => void;
  onRenameChange: (v: string) => void;
  onRenameSubmit: () => void;
  onRenameCancel: () => void;
  onDelete: () => void;
  onMove: (groupId: string | null) => void;
}

function SessionItem({
  session, active, renamingId, renameValue, groups,
  onSelect, onRenameStart, onRenameChange, onRenameSubmit, onRenameCancel, onDelete, onMove,
}: SessionItemProps) {
  const isRenaming = renamingId === session.id;

  return (
    <div className={`chat-session-item ${active ? 'active' : ''}`} onClick={onSelect}>
      {isRenaming ? (
        <input
          className="chat-inline-edit"
          value={renameValue}
          autoFocus
          onClick={e => e.stopPropagation()}
          onChange={e => onRenameChange(e.target.value)}
          onBlur={onRenameSubmit}
          onKeyDown={e => {
            if (e.key === 'Enter') { e.stopPropagation(); onRenameSubmit(); }
            if (e.key === 'Escape') { e.stopPropagation(); onRenameCancel(); }
          }}
        />
      ) : (
        <span className="chat-session-title">{session.title}</span>
      )}
      <div className="chat-session-actions" onClick={e => e.stopPropagation()}>
        <button className="chat-session-action-btn" title="Rename" onClick={onRenameStart}>✎</button>
        <select
          className="chat-session-action-btn"
          title="Move to group"
          value={session.chatGroupId ?? ''}
          onChange={e => onMove(e.target.value || null)}
          style={{ fontSize: 13 }}
        >
          <option value="">Ungrouped</option>
          {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
        <button className="chat-session-action-btn" title="Delete" onClick={onDelete}>🗑</button>
      </div>
    </div>
  );
}
