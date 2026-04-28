/**
 * Image Optimization Utilities
 * 
 * Provides functions to optimize and compress images for various use cases:
 * - PPT embedding (smaller file sizes)
 * - High-quality exports (maximum detail)
 * - Web display (balanced quality/size)
 */

export interface ImageOptimizationOptions {
  /** Target maximum width in pixels */
  maxWidth?: number;
  /** Target maximum height in pixels */
  maxHeight?: number;
  /** JPEG quality (0-1), only applies when outputting JPEG */
  quality?: number;
  /** Output format */
  format?: 'png' | 'jpeg' | 'webp';
  /** Whether to preserve transparency (forces PNG if true) */
  preserveTransparency?: boolean;
}

export const ImagePresets = {
  /** High quality for presentations (balanced size/quality) */
  pptEmbed: {
    maxWidth: 1920,
    maxHeight: 1080,
    quality: 0.92,
    format: 'png' as const,
    preserveTransparency: false,
  },
  /** Maximum quality for archival */
  highQuality: {
    maxWidth: 4096,
    maxHeight: 4096,
    quality: 1,
    format: 'png' as const,
    preserveTransparency: true,
  },
  /** Optimized for web display */
  webDisplay: {
    maxWidth: 1200,
    maxHeight: 800,
    quality: 0.85,
    format: 'webp' as const,
    preserveTransparency: false,
  },
  /** Thumbnail for previews */
  thumbnail: {
    maxWidth: 400,
    maxHeight: 300,
    quality: 0.8,
    format: 'jpeg' as const,
    preserveTransparency: false,
  },
};

/**
 * Optimize an image blob with the specified options
 * 
 * @param imageBlob The source image blob
 * @param options Optimization settings
 * @returns Optimized image blob
 */
export async function optimizeImage(
  imageBlob: Blob,
  options: ImageOptimizationOptions = ImagePresets.pptEmbed
): Promise<Blob> {
  const {
    maxWidth = 1920,
    maxHeight = 1080,
    quality = 0.92,
    format = 'png',
    preserveTransparency = false,
  } = options;

  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(imageBlob);

    img.onload = () => {
      URL.revokeObjectURL(url);

      // Calculate new dimensions while preserving aspect ratio
      let width = img.width;
      let height = img.height;

      if (width > maxWidth) {
        height = (height * maxWidth) / width;
        width = maxWidth;
      }
      if (height > maxHeight) {
        width = (width * maxHeight) / height;
        height = maxHeight;
      }

      // Create canvas for resizing
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(width);
      canvas.height = Math.round(height);

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      // Use high-quality interpolation
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      // Fill with white background if not preserving transparency
      if (!preserveTransparency && format !== 'png') {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      // Draw the image
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Determine output mime type
      const actualFormat = preserveTransparency ? 'png' : format;
      const mimeType = actualFormat === 'jpeg' 
        ? 'image/jpeg' 
        : actualFormat === 'webp' 
          ? 'image/webp' 
          : 'image/png';

      // Convert to blob
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create image blob'));
          }
        },
        mimeType,
        quality
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load image'));
    };

    img.src = url;
  });
}

/**
 * Convert a blob to base64 data URL
 */
export function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Convert a data URL to blob
 */
export async function dataUrlToBlob(dataUrl: string): Promise<Blob> {
  const response = await fetch(dataUrl);
  return response.blob();
}

/**
 * Get image dimensions from a blob
 */
export function getImageDimensions(blob: Blob): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(blob);

    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve({ width: img.width, height: img.height });
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load image'));
    };

    img.src = url;
  });
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/**
 * Estimate optimal quality for target file size
 * Iteratively adjusts quality to get close to target size
 */
export async function optimizeForFileSize(
  imageBlob: Blob,
  targetSizeKB: number,
  maxIterations: number = 5
): Promise<Blob> {
  let quality = 0.9;
  let result = imageBlob;
  const targetBytes = targetSizeKB * 1024;

  for (let i = 0; i < maxIterations; i++) {
    result = await optimizeImage(imageBlob, {
      quality,
      format: 'jpeg',
      preserveTransparency: false,
    });

    if (result.size <= targetBytes) {
      return result;
    }

    // Reduce quality proportionally
    quality = quality * (targetBytes / result.size);
    quality = Math.max(0.3, Math.min(0.95, quality)); // Clamp between 0.3 and 0.95
  }

  return result;
}
