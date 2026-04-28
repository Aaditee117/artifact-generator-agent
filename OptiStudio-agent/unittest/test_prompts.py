"""
Unit tests for prompts module.
"""

import pytest
from utils.prompts import (
    PHASE_TYPE_POC,
    PHASE_TYPE_MVP,
    PHASE_TYPE_BOTH,
    get_phase_context,
    get_ppt_prompt,
    get_architecture_prompt,
    get_cost_report_prompt,
    ENHANCED_PPT_CONTENT_PROMPT,
    PPT_CONTENT_PROMPT_POC,
    PPT_CONTENT_PROMPT_MVP,
)


class TestPhaseConstants:
    """Tests for phase type constants."""

    def test_poc_constant(self):
        assert PHASE_TYPE_POC == "poc"

    def test_mvp_constant(self):
        assert PHASE_TYPE_MVP == "mvp"

    def test_both_constant(self):
        assert PHASE_TYPE_BOTH == "both"


class TestGetPhaseContext:
    """Tests for get_phase_context function."""

    def test_poc_context_returns_poc_info(self):
        result = get_phase_context("poc")
        
        assert "POC" in result
        assert "Proof of Concept" in result
        assert "1-3 months" in result

    def test_mvp_context_returns_mvp_info(self):
        result = get_phase_context("mvp")
        
        assert "MVP" in result
        assert "Minimum Viable Product" in result
        assert "3-6 months" in result

    def test_invalid_phase_returns_empty(self):
        result = get_phase_context("invalid")
        assert result == ""

    def test_case_insensitive(self):
        result_lower = get_phase_context("poc")
        result_upper = get_phase_context("POC")
        
        assert result_lower == result_upper


class TestGetPptPrompt:
    """Tests for get_ppt_prompt function."""

    def test_poc_returns_poc_prompt(self):
        result = get_ppt_prompt("poc")
        assert result == PPT_CONTENT_PROMPT_POC

    def test_mvp_returns_mvp_prompt(self):
        result = get_ppt_prompt("mvp")
        assert result == PPT_CONTENT_PROMPT_MVP

    def test_unknown_returns_default(self):
        result = get_ppt_prompt("unknown")
        # Should return the default/legacy prompt
        assert result is not None

    def test_case_insensitive(self):
        result_lower = get_ppt_prompt("poc")
        result_upper = get_ppt_prompt("POC")
        assert result_lower == result_upper


class TestGetArchitecturePrompt:
    """Tests for get_architecture_prompt function."""

    def test_poc_contains_minimal_architecture(self):
        result = get_architecture_prompt("poc")
        
        assert "POC" in result
        assert "MINIMAL" in result or "minimal" in result.lower()
        assert "FREE" in result or "Basic" in result

    def test_mvp_contains_production_ready(self):
        result = get_architecture_prompt("mvp")
        
        assert "MVP" in result
        assert "PRODUCTION" in result or "production" in result.lower()
        assert "Key Vault" in result
        assert "Application Insights" in result


class TestGetCostReportPrompt:
    """Tests for get_cost_report_prompt function."""

    def test_poc_contains_basic_tiers(self):
        result = get_cost_report_prompt("poc")
        
        assert "POC" in result
        assert "Basic" in result or "Free" in result
        assert "1-3 months" in result

    def test_mvp_contains_standard_tiers(self):
        result = get_cost_report_prompt("mvp")
        
        assert "MVP" in result
        assert "Standard" in result
        assert "3-6 months" in result

    def test_both_contains_both_phases(self):
        result = get_cost_report_prompt("both")
        
        assert "POC" in result
        assert "MVP" in result


class TestEnhancedPptPrompt:
    """Tests for ENHANCED_PPT_CONTENT_PROMPT structure."""

    def test_contains_formatting_rules(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        assert "CRITICAL FORMATTING RULES" in prompt

    def test_contains_our_understanding_sections(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        assert "Our Understanding" in prompt
        assert "Current Challenges" in prompt
        assert "AI Opportunity" in prompt

    def test_contains_category_description_format(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        # Should mention the category: description format
        assert "CATEGORY: description" in prompt or "category" in prompt.lower()

    def test_contains_section_description_format(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        # Should mention the section: description format for DoD
        assert "SECTION: description" in prompt or "section" in prompt.lower()

    def test_contains_no_title_repetition_rule(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        # Should mention avoiding title repetition
        assert "NO title" in prompt or "NO \"Problem Statement\"" in prompt

    def test_contains_json_structure(self):
        prompt = ENHANCED_PPT_CONTENT_PROMPT
        
        assert "title_slide" in prompt
        assert "our_understanding" in prompt
        assert "objective" in prompt
        assert "scope" in prompt
        assert "prerequisites" in prompt
        assert "definition_of_done" in prompt
        assert "out_of_scope" in prompt
        assert "timeline_cost" in prompt
        assert "cost_estimate" in prompt
        assert "next_steps" in prompt
