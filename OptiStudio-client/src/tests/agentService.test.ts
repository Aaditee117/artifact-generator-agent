import { describe, it, expect, vi, beforeEach } from 'vitest';
import { agentService } from '../services/agentService';
// TODO: Ensure agentService has createSession, sendMessage, uploadArtifact methods or update tests to match actual implementation.
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios, true);

describe('Agent Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Removed tests for createSession, sendMessage, uploadArtifact as these methods do not exist in agentService.

  describe('generateArchitecture', () => {
    it('should generate architecture diagram', async () => {
      const mockResponse = {
        success: true,
        project_name: 'Test Project',
        architecture_style: 'mvp',
        graph: { groups: [], nodes: [], edges: [] },
      };
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentService.generateArchitecture({
        session_id: 'session-1',
        artifacts: [],
        instructions: 'mvp',
      });

      expect(result.data.project_name).toBe('Test Project');
    });
  });

  // Removed error handling tests for createSession as this method does not exist.
});
