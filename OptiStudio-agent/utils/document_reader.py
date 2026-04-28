"""Extract text from uploaded documents (DOCX, TXT, PDF, PPTX)."""

import io
from docx import Document
from pptx import Presentation


import asyncio

async def extract_text(file_bytes: bytes, file_name: str) -> str:
    """Extract text content from a file based on its extension. Offloads blocking work to a thread."""
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

    if ext == "txt":
        # Decoding is fast, can run inline
        return file_bytes.decode("utf-8", errors="replace")

    if ext == "docx":
        def _docx_extract():
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        return await asyncio.to_thread(_docx_extract)

    if ext == "pdf":
        return await _extract_pdf_text(file_bytes)

    if ext == "pptx":
        return await _extract_pptx_text(file_bytes)

    return f"[Unsupported file type: .{ext}]"


async def _extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber (better for complex layouts). Offloads to thread."""
    import asyncio
    def _pdfplumber_extract():
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            if text_parts:
                return "\n\n".join(text_parts)
            # Fallback to PyPDF2 if pdfplumber returns empty
            return None
        except ImportError:
            return None
        except Exception as e:
            return f"[Error extracting PDF text: {e}]"

    result = await asyncio.to_thread(_pdfplumber_extract)
    if result is not None and not result.startswith("[Error"):
        return result
    # Fallback to PyPDF2 if needed
    return await _extract_pdf_text_pypdf2(file_bytes)


async def _extract_pdf_text_pypdf2(file_bytes: bytes) -> str:
    """Fallback PDF extraction using PyPDF2. Offloads to thread."""
    import asyncio
    def _pypdf2_extract():
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts) if text_parts else "[No extractable text found in PDF]"
        except Exception as e:
            return f"[Error extracting PDF text: {e}]"
    return await asyncio.to_thread(_pypdf2_extract)


async def _extract_pptx_text(file_bytes: bytes) -> str:
    """Extract text from PowerPoint presentations. Offloads to thread."""
    import asyncio
    def _pptx_extract():
        try:
            prs = Presentation(io.BytesIO(file_bytes))
            text_parts = []
            for slide_num, slide in enumerate(prs.slides, 1):
                slide_text = [f"--- Slide {slide_num} ---"]
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text)
                if len(slide_text) > 1:
                    text_parts.append("\n".join(slide_text))
            return "\n\n".join(text_parts) if text_parts else "[No extractable text found in PPTX]"
        except Exception as e:
            return f"[Error extracting PPTX text: {e}]"
    return await asyncio.to_thread(_pptx_extract)
