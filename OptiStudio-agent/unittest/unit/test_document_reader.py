"""
Unit Tests for Document Reader Module
Using AAA (Arrange, Act, Assert) Pattern

Tests cover:
- extract_text (txt, docx, pdf, pptx)
- _extract_pdf_text
- _extract_pptx_text
- Unsupported file types
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import io


class TestExtractTextTxt:
    """Unit tests for extracting text from TXT files."""

    @pytest.mark.asyncio
    async def test_extract_text_txt_simple(self):
        """Test extracting text from simple TXT file."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b"Hello, this is a test document."
        file_name = "test.txt"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert result == "Hello, this is a test document."

    @pytest.mark.asyncio
    async def test_extract_text_txt_with_newlines(self):
        """Test extracting text from TXT file with newlines."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b"Line 1\nLine 2\nLine 3"
        file_name = "multiline.txt"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    @pytest.mark.asyncio
    async def test_extract_text_txt_unicode(self):
        """Test extracting text from TXT file with unicode."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = "Hello 世界 🌍".encode("utf-8")
        file_name = "unicode.txt"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Hello" in result
        assert "世界" in result

    @pytest.mark.asyncio
    async def test_extract_text_txt_empty(self):
        """Test extracting text from empty TXT file."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b""
        file_name = "empty.txt"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert result == ""


class TestExtractTextDocx:
    """Unit tests for extracting text from DOCX files."""

    @pytest.mark.asyncio
    @patch('utils.document_reader.Document')
    async def test_extract_text_docx_simple(self, mock_document):
        """Test extracting text from simple DOCX file."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph"
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_para1, mock_para2]
        mock_document.return_value = mock_doc_instance
        
        file_bytes = b"fake docx content"
        file_name = "test.docx"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "First paragraph" in result
        assert "Second paragraph" in result

    @pytest.mark.asyncio
    @patch('utils.document_reader.Document')
    async def test_extract_text_docx_empty_paragraphs(self, mock_document):
        """Test extracting text from DOCX with empty paragraphs."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_para1 = MagicMock()
        mock_para1.text = "Content paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "   "  # Whitespace only
        mock_para3 = MagicMock()
        mock_para3.text = ""  # Empty
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_para1, mock_para2, mock_para3]
        mock_document.return_value = mock_doc_instance
        
        file_bytes = b"fake docx content"
        file_name = "test.docx"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Content paragraph" in result
        # Empty paragraphs should be filtered out
        assert result.strip() == "Content paragraph"


class TestExtractTextPdf:
    """Unit tests for extracting text from PDF files."""

    @pytest.mark.asyncio
    @patch('pdfplumber.open')
    async def test_extract_text_pdf_single_page(self, mock_pdfplumber_open):
        """Test extracting text from single-page PDF."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF page content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber_open.return_value = mock_pdf
        
        file_bytes = b"fake pdf content"
        file_name = "test.pdf"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "PDF page content" in result

    @pytest.mark.asyncio
    @patch('pdfplumber.open')
    async def test_extract_text_pdf_multiple_pages(self, mock_pdfplumber_open):
        """Test extracting text from multi-page PDF."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber_open.return_value = mock_pdf
        
        file_bytes = b"fake pdf content"
        file_name = "document.pdf"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Page 1 content" in result
        assert "Page 2 content" in result


class TestExtractTextPdfFallback:
    """Test fallback to PyPDF2 when pdfplumber returns no text."""

    @pytest.mark.asyncio
    @patch('utils.document_reader._extract_pdf_text_pypdf2', new_callable=AsyncMock)
    @patch('pdfplumber.open')
    async def test_pdfplumber_empty_pages_fallbacks_to_pypdf2(self, mock_pdfplumber_open, mock_pypdf2):
        from utils.document_reader import extract_text
        # Arrange
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = None
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = ""
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber_open.return_value = mock_pdf
        mock_pypdf2.return_value = "[PyPDF2 fallback result]"
        file_bytes = b"fake pdf content"
        file_name = "test.pdf"
        # Act
        result = await extract_text(file_bytes, file_name)
        # Assert
        assert result == "[PyPDF2 fallback result]"
        assert mock_pypdf2.called


class TestExtractTextPptx:
    """Unit tests for extracting text from PPTX files."""

    @pytest.mark.asyncio
    @patch('utils.document_reader.Presentation')
    async def test_extract_text_pptx_simple(self, mock_presentation):
        """Test extracting text from simple PPTX file."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_shape = MagicMock()
        mock_shape.text = "Slide content"
        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        mock_prs = MagicMock()
        mock_prs.slides = [mock_slide]
        mock_presentation.return_value = mock_prs
        
        file_bytes = b"fake pptx content"
        file_name = "test.pptx"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Slide content" in result
        assert "Slide 1" in result

    @pytest.mark.asyncio
    @patch('utils.document_reader.Presentation')
    async def test_extract_text_pptx_multiple_slides(self, mock_presentation):
        """Test extracting text from multi-slide PPTX."""
        # Arrange
        from utils.document_reader import extract_text
        
        mock_shape1 = MagicMock()
        mock_shape1.text = "First slide content"
        mock_slide1 = MagicMock()
        mock_slide1.shapes = [mock_shape1]
        
        mock_shape2 = MagicMock()
        mock_shape2.text = "Second slide content"
        mock_slide2 = MagicMock()
        mock_slide2.shapes = [mock_shape2]
        
        mock_prs = MagicMock()
        mock_prs.slides = [mock_slide1, mock_slide2]
        mock_presentation.return_value = mock_prs
        
        file_bytes = b"fake pptx content"
        file_name = "presentation.pptx"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "First slide content" in result
        assert "Second slide content" in result
        assert "Slide 1" in result
        assert "Slide 2" in result


class TestExtractTextUnsupported:
    """Unit tests for unsupported file types."""

    @pytest.mark.asyncio
    async def test_extract_text_unsupported_extension(self):
        """Test extracting text from unsupported file type."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b"binary content"
        file_name = "image.png"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Unsupported file type" in result
        assert ".png" in result

    @pytest.mark.asyncio
    async def test_extract_text_no_extension(self):
        """Test extracting text from file without extension."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b"content"
        file_name = "noextension"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Unsupported file type" in result

    @pytest.mark.asyncio
    async def test_extract_text_exe_file(self):
        """Test extracting text from executable file."""
        # Arrange
        from utils.document_reader import extract_text
        file_bytes = b"MZ executable header"
        file_name = "program.exe"
        
        # Act
        result = await extract_text(file_bytes, file_name)
        
        # Assert
        assert "Unsupported file type" in result
        assert ".exe" in result
