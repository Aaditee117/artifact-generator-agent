import axios from 'axios';

const agentApi = axios.create({
  baseURL:  'http://localhost:8000/api/agent', 
  //'https://ca-optistudio-eu2-dev-001.salmonpebble-d7c05023.eastus2.azurecontainerapps.io/api/agent',
 
  headers: { 'Content-Type': 'application/json' },
});

// Shared types for admin session/artifact info
export interface ArtifactInfo {
  action: string;
  artifactType: string;
  blobUrl: string;
  storagePath: string;
  contextSummary: string;
  version: number;
  updatedAt: string;
  approvalStatus: string;
}

export interface SessionInfo {
  session_id: string;
  title?: string;
  artifacts: ArtifactInfo[];
  latest_update: string;
  author_name?: string;
}

export interface ArtifactRef {
  storage_path: string;
  file_name: string;
  category: string;
}

export interface ClarifyQuestion {
  id: string;
  question: string;
  why: string;
  default: string;
}

export interface ClarifyResponse {
  success: boolean;
  project_summary: string;
  questions: ClarifyQuestion[];
  error?: string;
  details?: string[];
  warnings?: string[];
}

export interface GenerateImage {
  label: string;
  url: string | null;
}

export interface GenerateResponse {
  success: boolean;
  type: string;
  images?: GenerateImage[];
  ppt_url?: string;
  excel_url?: string;
  dalle_prompt?: string;
  dalle_prompts?: Record<string, string>;
  cost_summary?: Record<string, number>;
  content_summary?: Record<string, unknown>;
  context_summary?: string;
  errors?: string[];
  error?: string;
}

export interface FeedbackResponse {
  success: boolean;
  message?: string;
  // If changes_needed, returns the same shape as GenerateResponse
  type?: string;
  images?: GenerateImage[];
  ppt_url?: string;
  excel_url?: string;
}

export interface ProcessArtifactsResponse {
  success: boolean;
  state: string;
  artifact_count: number;
  summary: string;
  message: string;
  error?: string;
}

export interface IntentResponse {
  success: boolean;
  intent: string;
  action: string;
  target: string | null;
  mapped_action: string | null;
  confidence: number;
  extracted_instructions: string;
  is_edit: boolean;
  has_artifacts: boolean;
  previous_generations: string[];
  error?: string;
}

export interface SessionStateResponse {
  success: boolean;
  state: string;
  processingDetails: Record<string, unknown>;
}

export interface GeneratedArtifact {
  action: string;
  artifactType: string;
  blobUrl: string;
  contextSummary: string;
  promptUsed: string;
  version: number;
  updatedAt: string;
}

export interface SessionArtifactsResponse {
  success: boolean;
  artifacts: GeneratedArtifact[];
}

export interface ConversationMessage {
  id: string;
  role: string;
  content: string;
  createdAt: string;
  metadata: Record<string, unknown>;
}

export interface ConversationHistoryResponse {
  success: boolean;
  messages: ConversationMessage[];
}

export interface SessionContextResponse {
  success: boolean;
  hasContext: boolean;
  extractedText: string | null;
  state: string;
  processingDetails: Record<string, unknown>;
  conversationHistory: ConversationMessage[];
  generatedArtifacts: GeneratedArtifact[];
}

// Architecture Graph Types
export interface ArchitectureGroup {
  id: string;
  label: string;
  color?: string;
  position?: { x: number; y: number };
  width?: number;
  height?: number;
}

export interface ArchitectureNode {
  id: string;
  label: string;
  technology: string;
  tooltip: string;
  group: string;
  icon: string;
  position?: { x: number; y: number };
  type?: string;
}

export interface ArchitectureEdge {
  source: string;
  target: string;
  label: string;
  protocol: string;
}

export interface ArchitectureGraph {
  groups: ArchitectureGroup[];
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
}

export interface ArchitectureResponse {
  success: boolean;
  project_name: string;
  architecture_style: string;
  graph: ArchitectureGraph;
  error?: string;
}

export interface ArchitectureUploadResponse {
  success: boolean;
  url: string;
  storage_path: string;
  error?: string;
}

export interface DrawioGenerateResponse {
  success: boolean;
  project_name: string;
  title: string;
  xml: string;
  edit_url: string;
  embed_url: string;
  blob_url?: string;
  node_count: number;
  edge_count: number;
  error?: string;
}

export interface DrawioSaveResponse {
  success: boolean;
  xml_url?: string;
  image_url?: string;
  xml_storage_path?: string;
  image_storage_path?: string;
  error?: string;
}

export const agentService = {
  clarify: (data: {
    session_id: string;
    action: string;
    artifacts: ArtifactRef[];
    instructions: string;
    session_title?: string;
  }) => agentApi.post<ClarifyResponse>('/clarify', data),

  generate: (data: {
    session_id: string;
    action: string;
    artifacts: ArtifactRef[];
    instructions: string;
    answers: Record<string, string>;
    previous_prompt?: string;
    session_title?: string;
    phase_type?: string;
    author_name?: string;
  }) => agentApi.post<GenerateResponse>('/generate', data),

  feedback: (data: {
    session_id: string;
    action: string;
    feedback: 'approved' | 'changes_needed';
    change_instructions: string;
    previous_prompt?: string;
    artifacts: ArtifactRef[];
    session_title?: string;
    phase_type?: string;
  }) => agentApi.post<FeedbackResponse>('/feedback', data),

  // New endpoints for artifact processing
  processArtifacts: (data: {
    session_id: string;
    artifacts: ArtifactRef[];
    session_title?: string;
    author_name?: string;
  }) => agentApi.post<ProcessArtifactsResponse>('/process-artifacts', data),

  recognizeIntent: (data: {
    session_id: string;
    message: string;
  }) => agentApi.post<IntentResponse>('/recognize-intent', data),

  getSessionState: (sessionId: string) =>
    agentApi.get<SessionStateResponse>(`/session/${sessionId}/state`),

  getSessionArtifacts: (sessionId: string) =>
    agentApi.get<SessionArtifactsResponse>(`/session/${sessionId}/artifacts`),

  getConversationHistory: (sessionId: string) =>
    agentApi.get<ConversationHistoryResponse>(`/session/${sessionId}/history`),

  getSessionContext: (sessionId: string) =>
    agentApi.get<SessionContextResponse>(`/session/${sessionId}/context`),

  // Architecture diagram endpoints
  generateArchitecture: (data: {
    session_id: string;
    artifacts: ArtifactRef[];
    instructions: string;
    answers?: Record<string, string>;
    session_title?: string;
    phase_type?: string;
    action?: string;
  }) => agentApi.post<ArchitectureResponse>('/architecture/generate', data),

  uploadArchitectureImage: (data: {
    imageData: string; // base64 encoded PNG
    projectName: string;
    contentType: string;
    sessionId?: string;
    sessionTitle?: string;
  }) => agentApi.post<ArchitectureUploadResponse>('/architecture/upload', data),

  // Draw.io diagram endpoints
  generateDrawio: (data: {
    session_id: string;
    artifacts: ArtifactRef[];
    instructions: string;
    answers?: Record<string, string>;
    session_title?: string;
    phase_type?: string;
  }) => agentApi.post<DrawioGenerateResponse>('/drawio/generate', data),

  saveDrawio: (data: {
    session_id: string;
    xml: string;
    project_name: string;
    session_title?: string;
    image_data?: string;  // base64 encoded PNG/SVG
    export_format?: string;
  }) => agentApi.post<DrawioSaveResponse>('/drawio/save', data),

  // Admin approval endpoints
  adminListSessions: () =>
    agentApi.get<{ success: boolean; sessions: SessionInfo[] }>('/admin/sessions'),

  adminApprove: (data: {
    session_id: string;
    action: string;
    artifact_type: string;
    approved_by?: string;
  }) => agentApi.post<{ success: boolean; message: string; approved_url?: string }>('/admin/approve', data),

  adminReject: (data: {
    session_id: string;
    action: string;
    artifact_type: string;
    reason: string;
  }) => agentApi.post<{ success: boolean; message: string }>('/admin/reject', data),

  adminChat: (data: { message: string, history?: { role: string; content: string }[] }) => 
    agentApi.post<{ success: boolean; response: string; sql_query: string; error?: string }>('/admin-chat', data),

  unifiedChat: (data: { session_id: string; message: string; is_admin: boolean; history?: { role: string; content: string }[] }) =>
    agentApi.post<{ 
      success: boolean; 
      response: string; 
      raw_query_executed: string | null; 
      error?: string;
      trigger_action?: string;
      extracted_instructions?: string;
      confidence?: number;
    }>('/unified-chat', data),
}

