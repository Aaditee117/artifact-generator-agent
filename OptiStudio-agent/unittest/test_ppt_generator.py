"""
Unit tests for PPT Generator.
"""

import pytest
from utils.ppt_generator import (
    _to_plain,
    _to_bulleted,
    FONT,
    BODY_PT,
    HEADING_PT,
    COLOR_BLACK,
)


class TestToPlain:
    """Tests for _to_plain function."""

    def test_empty_section_returns_empty_list(self):
        """Empty section should return empty list."""
        result = _to_plain(None)
        assert result == []

        result = _to_plain({})
        assert result == []

    def test_sections_format_for_our_understanding(self):
        """Should handle sections format for Our Understanding."""
        section = {
            "sections": [
                {"header": "Our Understanding", "points": ["Point 1", "Point 2"]},
                {"header": "Current Challenges", "points": ["Challenge 1"]},
            ]
        }
        
        result = _to_plain(section)
        
        assert "Our Understanding:" in result
        assert "Point 1" in result
        assert "Point 2" in result
        assert "Current Challenges:" in result
        assert "Challenge 1" in result

    def test_items_with_category_format(self):
        """Should handle items with category format for Prerequisites."""
        section = {
            "items": [
                {"category": "Azure Access", "description": "Contributor access"},
                {"category": "DevOps", "description": "GitHub repo ready"},
            ]
        }
        
        result = _to_plain(section)
        
        assert "Azure Access: Contributor access" in result
        assert "DevOps: GitHub repo ready" in result

    def test_items_with_section_format(self):
        """Should handle items with section format for Definition of Done."""
        section = {
            "items": [
                {"section": "Dev Complete", "description": "All features done"},
                {"section": "QA Complete", "description": "Tests passing"},
            ]
        }
        
        result = _to_plain(section)
        
        assert "Dev Complete: All features done" in result
        assert "QA Complete: Tests passing" in result

    def test_items_with_service_format(self):
        """Should handle items with service format for Cost Estimate."""
        section = {
            "items": [
                {"service": "Azure OpenAI", "cost": "$100/mo"},
                {"service": "Storage", "cost": "$50/mo"},
            ]
        }
        
        result = _to_plain(section)
        
        assert "Azure OpenAI: $100/mo" in result
        assert "Storage: $50/mo" in result

    def test_points_format(self):
        """Should handle simple points list."""
        section = {
            "points": ["Point 1", "Point 2", "Point 3"]
        }
        
        result = _to_plain(section)
        
        assert result == ["Point 1", "Point 2", "Point 3"]

    def test_steps_format(self):
        """Should handle numbered steps."""
        section = {
            "steps": ["Step one", "Step two", "Step three"]
        }
        
        result = _to_plain(section)
        
        assert "1. Step one" in result
        assert "2. Step two" in result
        assert "3. Step three" in result

    def test_phases_format(self):
        """Should handle phases for Timeline."""
        section = {
            "phases": [
                {"phase": "Phase 1: Discovery", "duration": "2 weeks"},
                {"phase": "Phase 2: Dev", "duration": "8 weeks"},
            ]
        }
        
        result = _to_plain(section)
        
        # Should contain phase — duration format
        assert any("Phase 1: Discovery" in line and "2 weeks" in line for line in result)

    def test_no_title_repetition(self):
        """Should NOT include title to avoid repetition."""
        section = {
            "title": "Objective",  # This should NOT appear
            "points": ["Objective 1", "Objective 2"]
        }
        
        result = _to_plain(section)
        
        # Title should not be in result (it would cause repetition)
        # Only the points should be present
        assert result == ["Objective 1", "Objective 2"]


class TestToBulleted:
    """Tests for _to_bulleted function."""

    def test_empty_lines_preserved(self):
        """Empty lines should be preserved for spacing."""
        section = {
            "sections": [
                {"header": "Header", "points": ["Point 1"]},
            ]
        }
        
        result = _to_bulleted(section)
        
        # Should have empty strings for spacing
        assert "" in result

    def test_section_headers_no_bullet(self):
        """Section headers (ending with :) should NOT have bullets."""
        section = {
            "sections": [
                {"header": "Our Understanding", "points": ["Point 1"]},
            ]
        }
        
        result = _to_bulleted(section)
        
        # Find the header line
        header_lines = [line for line in result if line.endswith(":")]
        for header in header_lines:
            assert not header.startswith("•"), f"Header should not have bullet: {header}"

    def test_regular_lines_get_bullets(self):
        """Regular lines should get bullet points."""
        section = {
            "points": ["Point 1", "Point 2"]
        }
        
        result = _to_bulleted(section)
        
        for line in result:
            if line and not line.endswith(":"):
                assert line.startswith("•"), f"Regular line should have bullet: {line}"

    def test_numbered_steps_keep_numbers(self):
        """Numbered steps should keep their numbers, no bullets."""
        section = {
            "steps": ["Step one", "Step two"]
        }
        
        result = _to_bulleted(section)
        
        # Should have numbered format, not bullets
        assert any(line.startswith("1.") for line in result)
        assert any(line.startswith("2.") for line in result)


class TestConstants:
    """Tests for style constants."""

    def test_font_is_open_sans(self):
        """Font should be Open Sans from sample.pptx."""
        assert FONT == "Open Sans"

    def test_body_pt_is_13(self):
        """Body text should be 13pt from sample.pptx."""
        # Pt(13) returns EMU value
        from pptx.util import Pt
        assert BODY_PT == Pt(13)

    def test_heading_pt_is_14(self):
        """Heading text should be 14pt from sample.pptx."""
        from pptx.util import Pt
        assert HEADING_PT == Pt(14)

    def test_color_black(self):
        """Default color should be black."""
        from pptx.dml.color import RGBColor
        assert COLOR_BLACK == RGBColor(0, 0, 0)
