/**
 * DrawioEditor — Embeds draw.io in an iframe for editing architecture diagrams.
 *
 * Uses draw.io's postMessage embed API:
 * - Sends XML to draw.io for editing
 * - Receives save/export events back
 * - Supports PNG export for PPT embedding
 *
 * @see https://www.drawio.com/doc/faq/embed-mode
 */
import { useEffect, useRef, useCallback, useState } from 'react';

interface DrawioEditorProps {
  /** The draw.io XML content to load into the editor */
  xml: string;
  /** Called when the user clicks save in draw.io */
  onSave: (xml: string, imageData?: string) => void;
  /** Called when the user closes the editor */
  onClose: () => void;
  /** Title shown in the header */
  title?: string;
}

const DRAWIO_EMBED_URL = 'https://embed.diagrams.net/?embed=1&proto=json&spin=1&libraries=1&saveAndExit=1&noSaveBtn=0&noExitBtn=0';

export default function DrawioEditor({ xml, onSave, onClose, title = 'Architecture Diagram' }: DrawioEditorProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const xmlRef = useRef(xml);

  // Keep ref current so the message handler always has latest xml
  xmlRef.current = xml;

  const handleMessage = useCallback((evt: MessageEvent) => {
    // Only accept messages from draw.io
    if (evt.origin !== 'https://embed.diagrams.net') return;

    let msg: { event: string; xml?: string; data?: string; format?: string };
    try {
      msg = typeof evt.data === 'string' ? JSON.parse(evt.data) : evt.data;
    } catch {
      return;
    }

    if (!msg || !msg.event) return;

    switch (msg.event) {
      case 'init':
        // draw.io iframe is ready — send the XML to load
        setIsLoaded(true);
        iframeRef.current?.contentWindow?.postMessage(
          JSON.stringify({ action: 'load', xml: xmlRef.current, autosave: 0 }),
          'https://embed.diagrams.net'
        );
        break;

      case 'save':
        // User clicked save — request an export (PNG) along with the XML
        setIsSaving(true);
        // First, get the XML from the save event
        if (msg.xml) {
          // Request a PNG export so we can store it for PPT embedding
          iframeRef.current?.contentWindow?.postMessage(
            JSON.stringify({ action: 'export', format: 'png', scale: 2, background: '#ffffff', xml: msg.xml }),
            'https://embed.diagrams.net'
          );
          // Store the XML temporarily for the export callback
          xmlRef.current = msg.xml;
        }
        break;

      case 'export':
        // Received the exported image data
        setIsSaving(false);
        onSave(xmlRef.current, msg.data || undefined);
        break;

      case 'exit':
        // User clicked the exit button
        onClose();
        break;

      default:
        break;
    }
  }, [onSave, onClose]);

  useEffect(() => {
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [handleMessage]);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1100,
      display: 'flex',
      flexDirection: 'column',
      background: '#fff',
    }}>
      {/* Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 16px',
        borderBottom: '1px solid #e0e0e0',
        background: '#f5f5f5',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 20 }}>🏗️</span>
          <span style={{ fontWeight: 600, fontSize: 15, color: '#333' }}>{title}</span>
          {isSaving && (
            <span style={{ fontSize: 12, color: '#f59e0b', fontWeight: 500 }}>Saving...</span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => {
              // Request XML from draw.io before closing
              iframeRef.current?.contentWindow?.postMessage(
                JSON.stringify({ action: 'export', format: 'png', scale: 2, background: '#ffffff' }),
                'https://embed.diagrams.net'
              );
            }}
            style={{
              padding: '6px 16px',
              borderRadius: 6,
              border: 'none',
              background: '#c62828',
              color: '#fff',
              fontWeight: 600,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Save & Close
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '6px 16px',
              borderRadius: 6,
              border: '1px solid #ddd',
              background: '#fff',
              color: '#555',
              fontWeight: 500,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
        </div>
      </div>

      {/* Loading indicator */}
      {!isLoaded && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 40,
          color: '#666',
          fontSize: 14,
        }}>
          Loading architecture diagram editor...
        </div>
      )}

      {/* draw.io iframe */}
      <iframe
        ref={iframeRef}
        src={DRAWIO_EMBED_URL}
        style={{
          flex: 1,
          border: 'none',
          width: '100%',
          display: isLoaded ? 'block' : 'none',
        }}
        title="Architecture Diagram Editor"
      />
    </div>
  );
}
