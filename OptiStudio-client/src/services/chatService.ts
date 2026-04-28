import api from './api';

export interface ChatGroupDto {
  id: string;
  name: string;
  createdAt: string;
  sessionCount: number;
}

export interface ChatSessionDto {
  id: string;
  title: string;
  chatGroupId?: string;
  chatGroupName?: string;
  createdAt: string;
  updatedAt?: string;
  lastMessagePreview?: string;
}

export interface ArtifactDto {
  id: string;
  fileName?: string;
  fileType?: string;
  category: string;
  fileSizeBytes?: number;
  blobUrl?: string;
  storagePath?: string;  // Raw storage path without URL encoding
  version: number;
  chatMessageId: string;
  uploadedByUserId: string;
  uploadedByUserName: string;
  createdAt: string;
}

export interface ChatMessageDto {
  id: string;
  content?: string;
  senderType: 'User' | 'Assistant';
  chatSessionId: string;
  userId?: string;
  userName?: string;
  createdAt: string;
  artifacts: ArtifactDto[];
  metadata?: Record<string, any>;
}

export interface ChatGroupResponse { success: boolean; message: string; group?: ChatGroupDto; }
export interface ChatGroupListResponse { success: boolean; message: string; groups: ChatGroupDto[]; }
export interface ChatSessionResponse { success: boolean; message: string; session?: ChatSessionDto; }
export interface ChatSessionListResponse { success: boolean; message: string; sessions: ChatSessionDto[]; }
export interface SendMessageResponse { success: boolean; message: string; chatMessage?: ChatMessageDto; errors: string[]; }
export interface ChatMessageListResponse { success: boolean; message: string; messages: ChatMessageDto[]; }

export const chatService = {
  // Sessions
  createSession: (chatGroupId?: string) =>
    api.post<ChatSessionResponse>('/chat/sessions', { chatGroupId: chatGroupId ?? null }),

  getSessions: () =>
    api.get<ChatSessionListResponse>('/chat/sessions'),

  renameSession: (id: string, name: string) =>
    api.put<ChatSessionResponse>(`/chat/sessions/${id}/rename`, { name }),

  moveSession: (id: string, chatGroupId: string | null) =>
    api.put<ChatSessionResponse>(`/chat/sessions/${id}/move`, { chatGroupId }),

  deleteSession: (id: string) =>
    api.delete<ChatSessionResponse>(`/chat/sessions/${id}`),

  // Messages
  sendMessage: (
    sessionId: string,
    content: string,
    files: File[],
    categories: string[]
  ) => {
    const form = new FormData();
    if (content.trim()) form.append('content', content.trim());
    files.forEach(f => form.append('files', f));
    if (categories.length) form.append('categories', categories.join(','));
    return api.post<SendMessageResponse>(
      `/chat/sessions/${sessionId}/messages`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  },

  getMessages: (sessionId: string) =>
    api.get<ChatMessageListResponse>(`/chat/sessions/${sessionId}/messages`),

  // Groups
  createGroup: (name: string) =>
    api.post<ChatGroupResponse>('/chat/groups', { name }),

  getGroups: () =>
    api.get<ChatGroupListResponse>('/chat/groups'),

  renameGroup: (id: string, name: string) =>
    api.put<ChatGroupResponse>(`/chat/groups/${id}`, { name }),

  deleteGroup: (id: string) =>
    api.delete<ChatGroupResponse>(`/chat/groups/${id}`),

  // Artifact download
  getArtifactDownloadUrl: (artifactId: string) =>
    api.get<{ success: boolean; url: string; fileName: string }>(`/chat/artifacts/${artifactId}/url`),
};
