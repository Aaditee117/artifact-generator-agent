/**
 * Hook for exporting architecture diagrams
 * Handles PNG/SVG export and upload to backend
 */

import { useCallback, useState } from 'react';
import { toPng, toSvg } from 'html-to-image';
import api from '../services/api';

interface ExportResult {
  url: string;
  storagePath: string;
}

interface UseArchitectureExportReturn {
  exportToPng: (element: HTMLElement) => Promise<Blob>;
  exportToSvg: (element: HTMLElement) => Promise<string>;
  uploadImage: (blob: Blob, projectName: string) => Promise<ExportResult>;
  downloadPng: (element: HTMLElement, filename: string) => Promise<void>;
  downloadSvg: (element: HTMLElement, filename: string) => Promise<void>;
  isExporting: boolean;
  error: string | null;
}

export function useArchitectureExport(): UseArchitectureExportReturn {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Export element to PNG blob
   */
  const exportToPng = useCallback(async (element: HTMLElement): Promise<Blob> => {
    setIsExporting(true);
    setError(null);

    try {
      const dataUrl = await toPng(element, {
        backgroundColor: '#ffffff',
        quality: 1,
        pixelRatio: 2,
        cacheBust: true,
      });

      const response = await fetch(dataUrl);
      const blob = await response.blob();

      return blob;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to export PNG';
      setError(message);
      throw new Error(message);
    } finally {
      setIsExporting(false);
    }
  }, []);

  /**
   * Export element to SVG string
   */
  const exportToSvg = useCallback(async (element: HTMLElement): Promise<string> => {
    setIsExporting(true);
    setError(null);

    try {
      const dataUrl = await toSvg(element, {
        backgroundColor: '#ffffff',
        cacheBust: true,
      });

      return dataUrl;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to export SVG';
      setError(message);
      throw new Error(message);
    } finally {
      setIsExporting(false);
    }
  }, []);

  /**
   * Upload PNG blob to backend for storage
   */
  const uploadImage = useCallback(async (blob: Blob, projectName: string): Promise<ExportResult> => {
    setIsExporting(true);
    setError(null);

    try {
      // Convert blob to base64
      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          const result = reader.result as string;
          // Remove data URL prefix
          const base64 = result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
      });
      reader.readAsDataURL(blob);

      const base64Data = await base64Promise;

      // Upload to backend
      const response = await api.post('/api/agent/architecture/upload', {
        imageData: base64Data,
        projectName: projectName,
        contentType: 'image/png',
      });

      return {
        url: response.data.url,
        storagePath: response.data.storagePath,
      };
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to upload image';
      setError(message);
      throw new Error(message);
    } finally {
      setIsExporting(false);
    }
  }, []);

  /**
   * Download PNG locally
   */
  const downloadPng = useCallback(async (element: HTMLElement, filename: string): Promise<void> => {
    const blob = await exportToPng(element);
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = url;
    link.click();

    URL.revokeObjectURL(url);
  }, [exportToPng]);

  /**
   * Download SVG locally
   */
  const downloadSvg = useCallback(async (element: HTMLElement, filename: string): Promise<void> => {
    const dataUrl = await exportToSvg(element);

    const link = document.createElement('a');
    link.download = `${filename}.svg`;
    link.href = dataUrl;
    link.click();
  }, [exportToSvg]);

  return {
    exportToPng,
    exportToSvg,
    uploadImage,
    downloadPng,
    downloadSvg,
    isExporting,
    error,
  };
}
