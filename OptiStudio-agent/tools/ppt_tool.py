"""Presales PPT generation tool.

Supports phase-aware PPT generation:
- POC: Focus on feasibility, shorter timeline, simpler architecture
- MVP: Full production proposal with timeline, costs, and next steps
"""

import json

import logging

logger = logging.getLogger(__name__)
from openai import AzureOpenAI
from config import settings
from utils.prompts import (
    ENHANCED_PPT_CONTENT_PROMPT,
    PPT_CONTENT_PROMPT,
    get_ppt_prompt,
    PHASE_TYPE_POC,
    PHASE_TYPE_MVP,
)
from utils.ppt_generator import generate_ppt
from utils.blob_storage import upload_bytes, slugify


def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


async def generate_presales_ppt(
    context: str,
    instructions: str,
    answers: str = "",
    arch_image: bytes | None = None,
    dfd_image: bytes | None = None,
    use_enhanced_template: bool = True,
    phase_type: str | None = None,
    session_folder: str | None = None,
) -> dict:
    """Generate a presales PPT with structured sections.

    Args:
        context: Project artifacts content
        instructions: User instructions
        answers: Clarification answers
        arch_image: Architecture diagram image bytes
        dfd_image: DFD image bytes
        use_enhanced_template: Use enhanced PPT template
        phase_type: 'poc' or 'mvp' for phase-specific content

    Returns dict with PPT download URL and the content used.
    """
    client = _get_chat_client()

    # Get phase-appropriate prompt
    if phase_type:
        prompt_template = get_ppt_prompt(phase_type)
        phase_label = "POC" if phase_type == PHASE_TYPE_POC else "MVP"
        print(f"📊 Generating {phase_label} presales presentation...")
    elif use_enhanced_template:
        prompt_template = ENHANCED_PPT_CONTENT_PROMPT
        phase_label = None
    else:
        prompt_template = PPT_CONTENT_PROMPT
        phase_label = None

    prompt = prompt_template.format(
        context=context, instructions=instructions, answers=answers,
    )
    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    # print(f"Reviewed response is as follows:{response} ")
    content = json.loads(response.choices[0].message.content)

    # Print/log the raw LLM content for debugging
    # print("[PPT] Raw LLM content:")
    # print(json.dumps(content, indent=2))

    # Map content to generator format based on phase
    if phase_type == PHASE_TYPE_POC:
        mapped_content = _map_poc_to_standard(content)
    elif phase_type == PHASE_TYPE_MVP:
        mapped_content = _map_mvp_to_standard(content)
    elif use_enhanced_template:
        mapped_content = _map_enhanced_to_standard(content)
    else:
        mapped_content = content

    # Log only summary metadata to avoid leaking sensitive data
    logger.info(
        "[PPT] Mapped content for template: keys=%s, sizes={%s}",
        list(mapped_content.keys()),
        ", ".join(f"{k}: {len(str(v))}" for k, v in mapped_content.items())
    )

    pptx_bytes = generate_ppt(mapped_content, arch_image=arch_image, dfd_image=dfd_image, phase_type=phase_type)

    # Create filename with phase indicator


    # Use slugify to sanitize project_name for safe filenames
    raw_title = mapped_content.get("title_slide", {}).get("title", "presales")
    project_name = slugify(raw_title)
    phase_suffix = f"_{phase_type.upper()}" if phase_type else ""
    file_name = f"{project_name}{phase_suffix}_proposal.pptx"


    url, storage_path = await upload_bytes(
        pptx_bytes,
        file_name,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        session_folder=session_folder,
        subfolder="generated",
    )

    return {
        "ppt_url": url,
        "storage_path": storage_path,
        "content": mapped_content,
        "phase_type": phase_type,
        "phase_label": phase_label,
    }


def _map_poc_to_standard(content: dict) -> dict:
    """Map POC PPT content to the template's 13-slide structure."""
    return {
        "title_slide": content.get("title_slide", {}),
        "our_understanding": content.get("our_understanding", {}),
        "objective": content.get("objective", {}),
        "scope": content.get("scope", {}),
        "high_level_design": content.get("high_level_design", {}),
        "prerequisites": content.get("prerequisites", {}),
        "definition_of_done": content.get("definition_of_done", {}),
        "out_of_scope": content.get("out_of_scope", {}),
        "timeline_cost": content.get("timeline_cost", {}),
        "cost_estimate": content.get("cost_estimate", {}),
        "next_steps": content.get("next_steps", {}),
    }


def _map_mvp_to_standard(content: dict) -> dict:
    """Map MVP PPT content to the template's 13-slide structure."""
    return {
        "title_slide": content.get("title_slide", {}),
        "our_understanding": content.get("our_understanding", {}),
        "objective": content.get("objective", {}),
        "scope": content.get("scope", {}),
        "high_level_design": content.get("high_level_design", {}),
        "prerequisites": content.get("prerequisites", {}),
        "definition_of_done": content.get("definition_of_done", {}),
        "out_of_scope": content.get("out_of_scope", {}),
        "timeline_cost": content.get("timeline_cost", {}),
        "cost_estimate": content.get("cost_estimate", {}),
        "next_steps": content.get("next_steps", {}),
    }


def _map_enhanced_to_standard(content: dict) -> dict:
    """Pass through enhanced content — ENHANCED_PPT_CONTENT_PROMPT already
    outputs the exact keys matching the template's 13-slide structure:
    our_understanding, objective, scope, high_level_design, prerequisites,
    definition_of_done, out_of_scope, timeline_cost, next_steps."""
    return content
