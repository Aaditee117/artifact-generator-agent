"""Azure Cost Report generation tool — produces Excel (.xlsx) file.

Supports three phase types:
- POC (Proof of Concept): Minimal architecture, free/basic tiers
- MVP (Minimum Viable Product): Production-ready architecture
- BOTH: Side-by-side comparison of POC and MVP
"""

import json
from openai import AzureOpenAI
from config import settings
from utils.prompts import (
    get_cost_report_prompt,
    PHASE_SELECTION_PROMPT,
    PHASE_TYPE_POC,
    PHASE_TYPE_MVP,
    PHASE_TYPE_BOTH,
)
from utils.cost_report_generator import generate_cost_excel
from utils.blob_storage import upload_bytes


def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


def get_phase_selection_message() -> str:
    """Return the phase selection prompt to show to users after artifact processing."""
    return PHASE_SELECTION_PROMPT


def parse_phase_selection(user_input: str) -> str:
    """Parse user's phase selection input.

    Args:
        user_input: User's response (e.g., "POC", "MVP", "BOTH", "1", "2", "3")

    Returns:
        Normalized phase type: 'poc', 'mvp', or 'both'
    """
    user_input = user_input.strip().lower()

    # Handle numeric selections
    if user_input in ("1", "poc", "proof of concept"):
        return PHASE_TYPE_POC
    elif user_input in ("2", "mvp", "minimum viable product"):
        return PHASE_TYPE_MVP
    elif user_input in ("3", "both", "comparison", "compare"):
        return PHASE_TYPE_BOTH
    else:
        # Default to both if unclear
        return PHASE_TYPE_BOTH


async def generate_cost_report(
    context: str,
    instructions: str,
    answers: str = "",
    phase_type: str = PHASE_TYPE_BOTH,
    session_folder: str | None = None,
) -> dict:
    """Analyze context and generate an Azure cost estimate Excel report.

    Args:
        context: Project artifacts and context
        instructions: User instructions
        answers: Clarification answers
        phase_type: 'poc', 'mvp', or 'both' (default: 'both')

    Returns:
        Dict with the Excel download URL, cost data, and phase type.
    """
    client = _get_chat_client()

    # Get the appropriate prompt based on phase selection
    prompt_template = get_cost_report_prompt(phase_type)
    prompt = prompt_template.format(
        context=context, instructions=instructions, answers=answers,
    )

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    cost_data = json.loads(response.choices[0].message.content)

    # Generate Excel report
    excel_bytes = generate_cost_excel(cost_data)

    # Create filename based on phase type
    base_name = cost_data.get("report_title", "Azure_Cost_Estimate").replace(" ", "_").replace("—", "-")
    phase_suffix = {
        PHASE_TYPE_POC: "_POC",
        PHASE_TYPE_MVP: "_MVP",
        PHASE_TYPE_BOTH: "_POC_MVP_Comparison",
    }.get(phase_type, "")
    file_name = f"{base_name}{phase_suffix}.xlsx"

    url, storage_path = await upload_bytes(
        excel_bytes,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        session_folder=session_folder,
        subfolder="generated",
    )

    return {
        "excel_url": url,
        "storage_path": storage_path,
        "cost_data": cost_data,
        "phase_type": phase_type,
        "phase_label": {
            PHASE_TYPE_POC: "POC (Proof of Concept)",
            PHASE_TYPE_MVP: "MVP (Minimum Viable Product)",
            PHASE_TYPE_BOTH: "POC & MVP Comparison",
        }.get(phase_type, phase_type),
    }


async def generate_poc_cost_report(
    context: str,
    instructions: str,
    answers: str = "",
    session_folder: str | None = None,
) -> dict:
    """Generate a POC (Proof of Concept) cost report."""
    return await generate_cost_report(context, instructions, answers, PHASE_TYPE_POC, session_folder)


async def generate_mvp_cost_report(
    context: str,
    instructions: str,
    answers: str = "",
    session_folder: str | None = None,
) -> dict:
    """Generate an MVP (Minimum Viable Product) cost report."""
    return await generate_cost_report(context, instructions, answers, PHASE_TYPE_MVP, session_folder)


async def generate_comparison_cost_report(
    context: str,
    instructions: str,
    answers: str = "",
    session_folder: str | None = None,
) -> dict:
    """Generate a comparison report with both POC and MVP."""
    return await generate_cost_report(context, instructions, answers, PHASE_TYPE_BOTH, session_folder)
