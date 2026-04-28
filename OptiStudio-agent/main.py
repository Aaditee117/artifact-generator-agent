"""OptiStudio Agent API — FastAPI server that React frontend calls directly.
Orchestrates artifact reading, LLM analysis, clarification, and generation.
Supports phase-based artifact generation (POC vs MVP).
Run with: python main.py
Listens on port 8000.
"""

import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
import uvicorn

from config import settings
from utils.blob_storage import (
    download_blob, 
    build_session_folder, 
    copy_blob_to_approved, 
    upload_bytes,
    list_approved_artifacts,
    get_approved_artifact_url,
)
from fastapi import UploadFile, File, Form

from utils.document_reader import extract_text
from utils.prompts import (
    SYSTEM_PROMPT,
    CLARIFICATION_PROMPT,
    COST_REPORT_CLARIFICATION_PROMPT,
    INTENT_RECOGNITION_PROMPT,
    PHASE_SELECTION_PROMPT,
    PHASE_TYPE_POC,
    PHASE_TYPE_MVP,
    get_phase_context,
    get_architecture_prompt,
    get_ppt_prompt,
    get_cost_report_prompt,
)
from utils.cosmos_service import (
    save_extracted_text,
    get_extracted_text,
    save_conversation_message,
    get_conversation_history,
    save_generated_prompt,
    get_generated_prompt,
    save_session_state,
    get_session_state,
    save_generated_artifact,
    get_session_artifacts,
    get_cosmos_container,
)
from datetime import datetime, timezone
from tools.architecture_tool import generate_architecture_diagram
from tools.dfd_tool import generate_dfd
from tools.ppt_tool import generate_presales_ppt
from tools.cost_report_tool import generate_cost_report
from tools.drawio_tool import generate_drawio_architecture, save_drawio_diagram


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"OptiStudio Agent API running on http://localhost:{settings.API_PORT}")
    yield


app = FastAPI(title="OptiStudio Agent API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://proud-mud-0633ce80f.2.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Endpoints ──────────────────────────────────────────────────

# Upload user artifact to the 'artifacts' container
@app.post("/api/agent/upload-artifact")
async def upload_user_artifact(
    file: UploadFile = File(...),
    session_title: str = Form(...),
    session_id: str = Form(...),
    author_name: str = Form(None)
):
    """Upload a user artifact to the 'artifacts' container and return its blob URL and storage path."""
    try:
        # Read file bytes
        file_bytes = await file.read()
        # Build session folder for organization
        session_folder = build_session_folder(session_title, session_id) if session_title else None
        # Use 'uploaded' subfolder for user uploads
        url, storage_path = await upload_bytes(
            file_bytes,
            file.filename,
            file.content_type or "application/octet-stream",
            session_folder=session_folder,
            subfolder="uploaded",
            container_name="artifacts"
        )
        return {
            "success": True,
            "url": url,
            "storage_path": storage_path,
            "file_name": file.filename,
            "content_type": file.content_type,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
from utils.document_reader import extract_text
from utils.prompts import (
    SYSTEM_PROMPT,
    CLARIFICATION_PROMPT,
    COST_REPORT_CLARIFICATION_PROMPT,
    INTENT_RECOGNITION_PROMPT,
    PHASE_SELECTION_PROMPT,
    PHASE_TYPE_POC,
    PHASE_TYPE_MVP,
    get_phase_context,
    get_architecture_prompt,
    get_ppt_prompt,
    get_cost_report_prompt,
)
from utils.cosmos_service import (
    save_extracted_text,
    get_extracted_text,
    save_conversation_message,
    get_conversation_history,
    save_generated_prompt,
    get_generated_prompt,
    save_session_state,
    get_session_state,
    save_generated_artifact,
    get_session_artifacts,
    get_cosmos_container,
)
from datetime import datetime, timezone
from tools.architecture_tool import generate_architecture_diagram
from tools.dfd_tool import generate_dfd
from tools.ppt_tool import generate_presales_ppt
from tools.cost_report_tool import generate_cost_report
from tools.drawio_tool import generate_drawio_architecture, save_drawio_diagram


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"OptiStudio Agent API running on http://localhost:{settings.API_PORT}")
    yield


app = FastAPI(title="OptiStudio Agent API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://proud-mud-0633ce80f.2.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ──────────────────────────────────

class ArtifactRef(BaseModel):
    storage_path: str
    file_name: str
    category: str = "Document"


class ClarifyRequest(BaseModel):
    session_id: str
    action: str  # architecture_diagram | dfd | presales_ppt
    artifacts: list[ArtifactRef]
    instructions: str = ""
    session_title: str = ""


class GenerateRequest(BaseModel):
    session_id: str
    action: str
    artifacts: list[ArtifactRef]
    instructions: str = ""
    answers: dict[str, str] = {}
    previous_prompt: str | None = None  # for re-generation / editing
    phase_type: str | None = None  # 'poc' or 'mvp' - determines artifact generation style
    session_title: str = ""
    author_name: str | None = None


class FeedbackRequest(BaseModel):
    session_id: str
    action: str
    feedback: str  # approved | changes_needed
    change_instructions: str = ""
    previous_prompt: str | None = None
    artifacts: list[ArtifactRef] = []
    phase_type: str | None = None
    session_title: str = ""
    author_name: str | None = None


class ProcessArtifactsRequest(BaseModel):
    session_id: str
    artifacts: list[ArtifactRef]
    session_title: str = ""
    author_name: str | None = None


class ProcessArtifactsWithPhaseRequest(BaseModel):
    """Request for processing artifacts with phase selection (POC/MVP)."""
    session_id: str
    artifacts: list[ArtifactRef]
    phase_type: str  # 'poc' or 'mvp'
    author_name: str | None = None


class GenerateAllArtifactsRequest(BaseModel):
    """Generate all artifacts (architecture, DFD, PPT, cost report) for selected phase."""
    session_id: str
    artifacts: list[ArtifactRef]
    phase_type: str  # 'poc' or 'mvp'
    instructions: str = ""
    session_title: str = ""
    author_name: str | None = None


class IntentRequest(BaseModel):
    session_id: str
    message: str


class SessionStateRequest(BaseModel):
    session_id: str


# ── Helpers ────────────────────────────────────────────────────

def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


async def _extract_all_context(artifacts: list[ArtifactRef]) -> tuple[str, list[str]]:
    """Download and extract text from all artifacts.
    Returns (context_text, list_of_errors)
    """
    parts = []
    errors = []
    for art in artifacts:
        try:
            data = await download_blob(art.storage_path)
            text = await extract_text(data, art.file_name)
            parts.append(f"--- {art.file_name} ({art.category}) ---\n{text}")
        except Exception as e:
            error_msg = f"Failed to read {art.file_name} from path '{art.storage_path}': {str(e)}"
            errors.append(error_msg)
            parts.append(f"--- {art.file_name} --- [ERROR: {str(e)}]")

    context = "\n\n".join(parts) if parts else "[No artifacts provided]"
    return context, errors


async def _extract_and_save_context(session_id: str, artifacts: list[ArtifactRef]) -> str:
    """Extract text from artifacts and save to Cosmos DB."""
    # Check if we already have extracted text
    existing = await get_extracted_text(session_id)
    if existing:
        return existing

    context, errors = await _extract_all_context(artifacts)

    # Log errors but still save what we could extract
    if errors:
        print(f"Errors during artifact extraction for session {session_id}:")
        for err in errors:
            print(f"  - {err}")

    # Save to Cosmos DB
    artifact_list = [
        {"file_name": a.file_name, "category": a.category, "storage_path": a.storage_path}
        for a in artifacts
    ]
    await save_extracted_text(session_id, artifact_list, context)

    return context


_ACTION_LABELS = {
    "architecture_diagram": "architecture diagram",
    "dfd": "data flow diagram (DFD Level 0 and Level 1)",
    "presales_ppt": "presales proposal PPT (10 slides)",
    "cost_report": "Azure cost estimate report (Excel)",
}


# ── Endpoints ──────────────────────────────────────────────────

@app.post("/api/agent/clarify")
async def get_clarification_questions(req: ClarifyRequest):
    """Analyze artifacts and return clarification questions before generation."""
    context, extraction_errors = await _extract_all_context(req.artifacts)

    # If all artifacts failed to extract, return error immediately
    if extraction_errors and "[No artifacts provided]" in context:
        return {
            "success": False,
            "error": "Failed to read uploaded artifacts from storage",
            "details": extraction_errors,
            "project_summary": "",
            "questions": []
        }

    # Check if context has actual content (not just error messages)
    if context.count("[ERROR:") >= len(req.artifacts) or "[No artifacts provided]" in context:
        return {
            "success": False,
            "error": "No valid artifact content could be extracted",
            "details": extraction_errors,
            "project_summary": "",
            "questions": []
        }

    label = _ACTION_LABELS.get(req.action, req.action)

    client = _get_chat_client()

    # Use cost-report-specific clarification for cost_report action
    if req.action == "cost_report":
        prompt = COST_REPORT_CLARIFICATION_PROMPT
    else:
        prompt = CLARIFICATION_PROMPT.format(artifact_type=label)

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Artifacts:\n{context}\n\nUser instructions: {req.instructions}\n\n{prompt}"},
        ],
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        result = {"project_summary": "", "questions": []}

    return {
        "success": True,
        "project_summary": result.get("project_summary", ""),
        "questions": result.get("questions", []),
        "warnings": extraction_errors if extraction_errors else None,
    }


@app.post("/api/agent/generate")
async def generate(req: GenerateRequest):
    """Generate the requested artifact (architecture diagram, DFD, or PPT)."""
    # Update session state
    await save_session_state(req.session_id, "generating", {"action": req.action})

    # Build session folder for organized blob storage
    session_folder = build_session_folder(req.session_title, req.session_id) if req.session_title else None

    # Save user request as conversation message
    await save_conversation_message(
        session_id=req.session_id,
        role="user",
        content=f"Generate {req.action}: {req.instructions}" if req.instructions else f"Generate {req.action}",
        metadata={"action": req.action, "answers": req.answers, "author_name": req.author_name}
    )

    context, extraction_errors = await _extract_all_context(req.artifacts)

    # Check for critical extraction failures
    if extraction_errors and "[No artifacts provided]" in context:
        await save_session_state(req.session_id, "error", {"error": "Failed to read artifacts"})
        return {
            "success": False,
            "error": "Failed to read uploaded artifacts from storage",
            "details": extraction_errors
        }

    answers_str = "\n".join(f"Q: {k}\nA: {v}" for k, v in req.answers.items()) if req.answers else ""
    instructions = req.instructions

    # Get previous prompt if editing
    if req.previous_prompt:
        instructions += f"\n\nPrevious prompt (use as base for consistency):\n{req.previous_prompt}"
    else:
        # Check if we have a saved prompt for this action
        saved_prompt = await get_generated_prompt(req.session_id, req.action)
        if saved_prompt and saved_prompt.get("prompt"):
            instructions += f"\n\nPrevious prompt (use as base for consistency):\n{saved_prompt.get('prompt')}"

    try:
        if req.action == "architecture_diagram":
            result = await generate_architecture_diagram(context, instructions, answers_str, phase_type=req.phase_type, session_folder=session_folder)

            # Save the prompt to Cosmos for reproducibility
            if result.get("dalle_prompt"):
                await save_generated_prompt(
                    session_id=req.session_id,
                    action=req.action,
                    prompt=result.get("dalle_prompt"),
                    context_summary=context[:500] + "..." if len(context) > 500 else context,
                    generated_url=result.get("dalle_url")
                )

            # Save generated artifacts
            if result.get("dalle_url"):
                await save_generated_artifact(
                    session_id=req.session_id,
                    action=req.action,
                    artifact_type="ai_visualization",
                    blob_url=result.get("dalle_url"),
                    storage_path=result.get("dalle_storage_path", ""),
                    prompt_used=result.get("dalle_prompt"),
                    context_summary="AI-generated architecture visualization based on project artifacts",
                    author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                )

            if result.get("diagrams_lib_url"):
                await save_generated_artifact(
                    session_id=req.session_id,
                    action=req.action,
                    artifact_type="technical_diagram",
                    blob_url=result.get("diagrams_lib_url"),
                    storage_path=result.get("diagrams_lib_storage_path", ""),
                    context_summary="Technical architecture diagram with Azure icons",
                    author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                )

            # Save assistant response
            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated architecture diagram for your project.",
                metadata={
                    "action": req.action,
                    "dalle_url": result.get("dalle_url"),
                    "diagrams_lib_url": result.get("diagrams_lib_url")
                }
            )

            await save_session_state(req.session_id, "ready", {"last_action": req.action})

            return {
                "success": True,
                "type": "architecture_diagram",
                "images": [
                    {"label": "Technical Diagram (Azure Icons)", "url": result.get("diagrams_lib_url")},
                    {"label": "AI-Generated Visualization", "url": result.get("dalle_url")},
                ],
                "dalle_prompt": result.get("dalle_prompt"),
                "context_summary": f"Architecture diagram generated based on {len(req.artifacts)} artifact(s). The design includes the key components and their interactions as extracted from your project documents.",
                "errors": [v for k, v in result.items() if k.endswith("_error")],
            }

        elif req.action == "dfd":
            from tools.dfd_tool import generate_dfd
            result = await generate_dfd(context, instructions, answers_str, session_folder=session_folder)

            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated Data Flow Diagram (interactive graph format) for your project.",
                metadata={"action": req.action}
            )

            await save_session_state(req.session_id, "ready", {"last_action": req.action})

            return {
                "success": True,
                "type": "dfd",
                "graph": result.get("graph"),
                "project_name": result.get("project_name"),
                "context_summary": "Unified interactive Data Flow Diagram.",
                "errors": result.get("errors", []),
            }


        elif req.action == "presales_ppt":
            # Always generate draw.io diagram and render to PNG for PPT embedding
            try:
                print("🔄 Forcing generation of draw.io architecture diagram for PPT...")
                drawio_result = await generate_drawio_architecture(
                    context,
                    instructions,
                    answers_str,
                    phase_type=req.phase_type,
                    session_folder=session_folder
                )
                drawio_xml = drawio_result.get("xml", "")
                arch_image = None
                if drawio_result.get("blob_url"):
                    await save_generated_artifact(
                        session_id=req.session_id,
                        action="drawio_diagram",
                        artifact_type="xml",
                        blob_url=drawio_result["blob_url"],
                        storage_path=drawio_result.get("storage_path", ""),
                        context_summary=f"Draw.io architecture diagram for {drawio_result.get('project_name')}",
                        author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                    )
                    print(f"✅ Draw.io XML saved: {drawio_result.get('edit_url')}")

                # Render draw.io XML to PNG for PPT embedding
                if drawio_xml:
                    from utils.diagram_renderer import render_drawio_xml_to_png
                    from tools.architecture_tool import save_architecture_image
                    arch_name = drawio_result.get("project_name", "Architecture")
                    print("🎨 Rendering draw.io diagram to PNG for PPT...")
                    arch_image = await render_drawio_xml_to_png(drawio_xml)
                    print(f"✅ Draw.io PNG rendered ({len(arch_image)} bytes)")
                    upload_result = await save_architecture_image(
                        arch_image, arch_name, session_folder=session_folder
                    )
                    if upload_result.get("url"):
                        await save_generated_artifact(
                            session_id=req.session_id,
                            action="architecture_diagram",
                            artifact_type="png",
                            blob_url=upload_result["url"],
                            storage_path=upload_result.get("storage_path", ""),
                            context_summary=f"Draw.io architecture PNG for {arch_name}",
                            author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                        )
                        print(f"✅ Draw.io PNG saved to blob: {upload_result['url']}")
                else:
                    print("❌ No draw.io XML generated for architecture diagram.")
            except Exception as e:
                print(f"⚠️ Could not generate draw.io architecture diagram: {e}")
                import traceback
                traceback.print_exc()
                arch_image = None

            result = await generate_presales_ppt(
                context, instructions, answers_str,
                arch_image=arch_image,
                session_folder=session_folder,
                phase_type=req.phase_type
            )

            # Save PPT content as prompt for editing
            content = result.get("content", {})
            await save_generated_prompt(
                session_id=req.session_id,
                action=req.action,
                prompt=json.dumps(content, indent=2),
                context_summary="Presentation content structure",
                generated_url=result.get("ppt_url")
            )

            if result.get("ppt_url"):
                await save_generated_artifact(
                    session_id=req.session_id,
                    action=req.action,
                    artifact_type="pptx",
                    blob_url=result.get("ppt_url"),
                    storage_path=result.get("storage_path", ""),
                    context_summary="Presales presentation deck with project overview, scope, timeline, and next steps",
                    author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                )

            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated presales presentation deck for your project.",
                metadata={"action": req.action, "ppt_url": result.get("ppt_url")}
            )

            await save_session_state(req.session_id, "ready", {"last_action": req.action})

            return {
                "success": True,
                "type": "presales_ppt",
                "ppt_url": result.get("ppt_url"),
                "content_summary": content,
                "context_summary": "Presentation includes: Our Understanding, Objectives, Scope, High Level Design, Prerequisites, Definition of Done, Out of Scope, Timeline & Cost, and Next Steps.",
            }

        elif req.action == "cost_report":
            result = await generate_cost_report(
                context, 
                instructions, 
                answers_str, 
                phase_type=req.phase_type or "both", # Fallback to BOTH if phase not specified
                session_folder=session_folder
            )

            # Save cost report artifact to Cosmos so it appears in Admin Approve and Approved Decks
            if result.get("excel_url"):
                await save_generated_artifact(
                    session_id=req.session_id,
                    action=req.action,
                    artifact_type="xlsx",
                    blob_url=result.get("excel_url"),
                    storage_path=result.get("storage_path", ""),
                    context_summary="Azure cost estimate report with environment breakdowns and recommendations",
                    author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
                )

            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated Azure cost estimate report.",
                metadata={"action": req.action, "excel_url": result.get("excel_url")}
            )

            await save_session_state(req.session_id, "ready", {"last_action": req.action})

            return {
                "success": True,
                "type": "cost_report",
                "excel_url": result.get("excel_url"),
                "cost_summary": result.get("cost_data", {}).get("summary", {}),
                "context_summary": "Azure cost estimate with development and production environment breakdowns.",
            }

        else:
            raise HTTPException(400, f"Unknown action: {req.action}")

    except Exception as e:
        await save_session_state(req.session_id, "error", {"error": str(e), "action": req.action})
        return {"success": False, "error": str(e)}


@app.post("/api/agent/feedback")
async def handle_feedback(req: FeedbackRequest):
    """Handle 'This is good' or 'Need changes' feedback."""
    if req.feedback == "approved":
        # Save conversation message
        await save_conversation_message(
            session_id=req.session_id,
            role="user",
            content=f"Approved the generated {req.action}",
            metadata={"action": req.action, "feedback": "approved"}
        )
        return {"success": True, "message": "Great! The artifact has been finalized."}

    if req.feedback == "changes_needed":
        # Save conversation message with change instructions
        await save_conversation_message(
            session_id=req.session_id,
            role="user",
            content=f"Requested changes to {req.action}: {req.change_instructions}",
            metadata={"action": req.action, "feedback": "changes_needed"}
        )

        # Re-generate with change instructions appended
        gen_req = GenerateRequest(
            session_id=req.session_id,
            action=req.action,
            artifacts=req.artifacts,
            instructions=req.change_instructions,
            previous_prompt=req.previous_prompt,
            session_title=req.session_title,
            phase_type=req.phase_type,
            author_name=req.author_name,
        )
        return await generate(gen_req)

    raise HTTPException(400, "feedback must be 'approved' or 'changes_needed'")


@app.post("/api/agent/process-artifacts")
async def process_artifacts(req: ProcessArtifactsRequest):
    """Process uploaded artifacts: extract text and save to Cosmos DB."""
    try:
        # Update session state to processing
        await save_session_state(
            session_id=req.session_id,
            state="processing_artifacts",
            processing_details={"artifact_count": len(req.artifacts)}
        )

        # Extract text from all artifacts
        context = await _extract_and_save_context(req.session_id, req.artifacts)

        # Save conversation message about artifact upload
        artifact_names = [a.file_name for a in req.artifacts]
        await save_conversation_message(
            session_id=req.session_id,
            role="user",
            content=f"Uploaded artifacts: {', '.join(artifact_names)}",
            artifacts=[{"fileName": a.file_name, "category": a.category} for a in req.artifacts],
            metadata={"author_name": req.author_name}
        )

        # Update session state to ready
        await save_session_state(
            session_id=req.session_id,
            state="ready",
            processing_details={
                "artifact_count": len(req.artifacts),
                "text_length": len(context),
                "artifacts": artifact_names
            }
        )

        # Generate a brief summary of the artifacts
        client = _get_chat_client()
        summary_response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide a brief 2-3 sentence summary of the project based on the artifacts."},
                {"role": "user", "content": f"Artifacts:\n{context[:4000]}..."}  # Truncate for summary
            ],
            max_completion_tokens=150
        )
        summary = summary_response.choices[0].message.content

        return {
            "success": True,
            "state": "ready",
            "artifact_count": len(req.artifacts),
            "summary": summary,
            "message": "Artifacts processed successfully. You can now generate architecture diagrams or presentation decks.",
            "phase_selection_prompt": PHASE_SELECTION_PROMPT,
            "available_phases": [
                {"id": "poc", "name": "POC (Proof of Concept)", "description": "Technical feasibility validation, 1-3 months"},
                {"id": "mvp", "name": "MVP (Minimum Viable Product)", "description": "Production-ready launch, 3-6 months"}
            ]
        }
    except Exception as e:
        await save_session_state(req.session_id, "error", {"error": str(e)})
        return {"success": False, "error": str(e)}


@app.post("/api/agent/select-phase")
async def select_phase_and_generate(req: GenerateAllArtifactsRequest):
    """
    After artifact upload, user selects POC or MVP phase.
    This endpoint generates ALL deliverables for the selected phase:
    - Architecture Diagram (tailored for POC/MVP)
    - Data Flow Diagrams (same for both)
    - Presales Presentation (tailored for POC/MVP)
    - Azure Cost Report (tailored for POC/MVP)
    """
    phase_type = req.phase_type.lower()
    if phase_type not in [PHASE_TYPE_POC, PHASE_TYPE_MVP]:
        raise HTTPException(400, f"Invalid phase_type: {phase_type}. Must be 'poc' or 'mvp'")

    phase_label = "POC (Proof of Concept)" if phase_type == PHASE_TYPE_POC else "MVP (Minimum Viable Product)"

    # Update session state
    await save_session_state(
        req.session_id,
        "generating_all",
        {"phase_type": phase_type, "phase_label": phase_label}
    )

    # Save phase selection message
    await save_conversation_message(
        session_id=req.session_id,
        role="user",
        content=f"Selected phase: {phase_label}",
        metadata={"action": "phase_selection", "phase_type": phase_type, "author_name": req.author_name}
    )

    # Extract context
    context, extraction_errors = await _extract_all_context(req.artifacts)
    if "[No artifacts provided]" in context:
        return {"success": False, "error": "No valid artifacts to process"}

    # Build session folder for organized blob storage
    session_folder = build_session_folder(req.session_title, req.session_id) if req.session_title else None

    # Add phase context to instructions
    phase_context = get_phase_context(phase_type)
    instructions = f"{req.instructions}\n\n{phase_context}" if req.instructions else phase_context

    results = {
        "success": True,
        "phase_type": phase_type,
        "phase_label": phase_label,
        "artifacts": {},
        "errors": []
    }

    # 1. Generate Architecture Diagram via draw.io (phase-aware)
    arch_image = None
    try:
        # Generate draw.io XML architecture diagram
        drawio_result = await generate_drawio_architecture(
            context, instructions, "", phase_type=phase_type, session_folder=session_folder
        )
        drawio_xml = drawio_result.get("xml", "")
        arch_name = drawio_result.get("project_name", "Architecture")

        if drawio_result.get("blob_url"):
            await save_generated_artifact(
                session_id=req.session_id,
                action=f"drawio_diagram_{phase_type}",
                artifact_type="xml",
                blob_url=drawio_result["blob_url"],
                storage_path=drawio_result.get("storage_path", ""),
                context_summary=f"{phase_label} draw.io architecture diagram",
                author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
            )

        # Render draw.io XML to PNG for PPT embedding
        if drawio_xml:
            from utils.diagram_renderer import render_drawio_xml_to_png
            from tools.architecture_tool import save_architecture_image
            print(f"🎨 Rendering draw.io diagram to PNG for PPT...")
            arch_image = await render_drawio_xml_to_png(drawio_xml)
            print(f"✅ Draw.io PNG rendered ({len(arch_image)} bytes)")

            upload_result = await save_architecture_image(
                arch_image, arch_name, session_folder=session_folder
            )
            results["artifacts"]["architecture_diagram"] = {
                "success": True,
                "images": [
                    {"label": "Architecture Diagram", "url": upload_result.get("url")},
                ],
                "edit_url": drawio_result.get("edit_url"),
            }
            await save_generated_artifact(
                session_id=req.session_id,
                action=f"architecture_diagram_{phase_type}",
                artifact_type="png",
                blob_url=upload_result.get("url"),
                storage_path=upload_result.get("storage_path", ""),
                context_summary=f"{phase_label} architecture diagram (draw.io)",
                author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
            )
        else:
            results["artifacts"]["architecture_diagram"] = {"success": False, "error": "No draw.io XML generated"}
    except Exception as e:
        results["artifacts"]["architecture_diagram"] = {"success": False, "error": str(e)}
        results["errors"].append(f"Architecture: {str(e)}")

    # 2. Generate DFD (same for POC and MVP)
    try:
        dfd_result = await generate_dfd(context, instructions, "", session_folder=session_folder)
        results["artifacts"]["dfd"] = {
            "success": True,
            "images": [], # Images removed, graph used instead
            "graph": dfd_result.get("graph"),
        }
    except Exception as e:
        results["artifacts"]["dfd"] = {"success": False, "error": str(e)}
        results["errors"].append(f"DFD: {str(e)}")

    # 3. Generate PPT (phase-aware)
    try:
        ppt_result = await generate_presales_ppt(
            context, instructions, "", 
            arch_image=arch_image,  # Always pass the generated PNG
            dfd_image=None,         # Never pass DFD image
            phase_type=phase_type, 
            session_folder=session_folder
        )
        results["artifacts"]["presales_ppt"] = {
            "success": True,
            "ppt_url": ppt_result.get("ppt_url"),
            "content_summary": ppt_result.get("content", {}),
        }
        await save_generated_artifact(
            session_id=req.session_id,
            action=f"presales_ppt_{phase_type}",
            artifact_type="pptx",
            blob_url=ppt_result.get("ppt_url"),
            storage_path=ppt_result.get("storage_path", ""),
            context_summary=f"{phase_label} presales presentation",
            author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
        )
    except Exception as e:
        results["artifacts"]["presales_ppt"] = {"success": False, "error": str(e)}
        results["errors"].append(f"PPT: {str(e)}")

    # 4. Generate Cost Report (phase-aware)
    try:
        cost_result = await generate_cost_report(
            context, instructions, "", phase_type=phase_type, session_folder=session_folder
        )
        results["artifacts"]["cost_report"] = {
            "success": True,
            "excel_url": cost_result.get("excel_url"),
            "cost_summary": cost_result.get("cost_data", {}).get("summary", {}),
            "phase_label": cost_result.get("phase_label"),
        }
        await save_generated_artifact(
            session_id=req.session_id,
            action=f"cost_report_{phase_type}",
            artifact_type="xlsx",
            blob_url=cost_result.get("excel_url"),
            storage_path=cost_result.get("storage_path", ""),
            context_summary=f"{phase_label} Azure cost report",
            author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
        )
    except Exception as e:
        results["artifacts"]["cost_report"] = {"success": False, "error": str(e)}
        results["errors"].append(f"Cost Report: {str(e)}")

    # Save assistant response
    successful_artifacts = [k for k, v in results["artifacts"].items() if v.get("success")]
    await save_conversation_message(
        session_id=req.session_id,
        role="assistant",
        content=f"Generated {len(successful_artifacts)} artifacts for {phase_label}: {', '.join(successful_artifacts)}",
        metadata={"action": "generate_all", "phase_type": phase_type, "artifacts": successful_artifacts}
    )

    # Update session state
    await save_session_state(req.session_id, "ready", {
        "last_action": "generate_all",
        "phase_type": phase_type,
        "artifacts_generated": successful_artifacts
    })

    return results


@app.post("/api/agent/recognize-intent")
async def recognize_intent(req: IntentRequest):
    """Recognize user intent from their message."""
    try:
        # Get session context
        session_state = await get_session_state(req.session_id)
        session_artifacts = await get_session_artifacts(req.session_id)

        has_artifacts = session_state and session_state.get("state") == "ready"
        previous_generations = [a.get("action") for a in session_artifacts] if session_artifacts else []

        client = _get_chat_client()
        prompt = INTENT_RECOGNITION_PROMPT.format(
            message=req.message,
            has_artifacts=has_artifacts,
            previous_generations=previous_generations
        )

        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Map intent to action
        action_map = {
            "generate_architecture": "architecture_diagram",
            "generate_dfd": "dfd",
            "generate_ppt": "presales_ppt",
            "generate_cost": "cost_report",
            "edit_architecture": "architecture_diagram",
            "edit_dfd": "dfd",
            "edit_ppt": "presales_ppt",
            "edit_cost": "cost_report"
        }

        mapped_action = action_map.get(result.get("intent"), None)

        return {
            "success": True,
            "intent": result.get("intent"),
            "action": result.get("action"),
            "target": result.get("target"),
            "mapped_action": mapped_action,
            "confidence": result.get("confidence", 0),
            "extracted_instructions": result.get("extracted_instructions", ""),
            "is_edit": result.get("action") == "edit",
            "has_artifacts": has_artifacts,
            "previous_generations": previous_generations
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "intent": "unknown"
        }


@app.get("/api/agent/session/{session_id}/state")
async def get_session_processing_state(session_id: str):
    """Get the current processing state of a session."""
    state = await get_session_state(session_id)
    if state:
        return {
            "success": True,
            "state": state.get("state", "idle"),
            "processingDetails": state.get("processingDetails", {})
        }
    return {
        "success": True,
        "state": "idle",
        "processingDetails": {}
    }


@app.get("/api/agent/session/{session_id}/artifacts")
async def get_session_generated_artifacts(session_id: str):
    """Get all generated artifacts for a session."""
    artifacts = await get_session_artifacts(session_id)
    return {
        "success": True,
        "artifacts": [
            {
                "action": a.get("action"),
                "artifactType": a.get("artifactType"),
                "blobUrl": a.get("blobUrl"),
                "contextSummary": a.get("contextSummary"),
                "promptUsed": a.get("promptUsed"),
                "version": a.get("version", 1),
                "updatedAt": a.get("updatedAt")
            }
            for a in artifacts
        ]
    }


@app.get("/api/agent/session/{session_id}/history")
async def get_session_conversation_history(session_id: str):
    """Get conversation history for a session."""
    history = await get_conversation_history(session_id)
    return {
        "success": True,
        "messages": [
            {
                "id": m.get("id"),
                "role": m.get("role"),
                "content": m.get("content"),
                "createdAt": m.get("createdAt"),
                "metadata": m.get("metadata", {})
            }
            for m in history
        ]
    }


@app.get("/api/agent/session/{session_id}/context")
async def get_session_full_context(session_id: str):
    """Get full session context: extracted text + conversation history + generated artifacts.

    Used by the frontend to restore full context when loading a chat session.
    """
    extracted_text = await get_extracted_text(session_id)
    history = await get_conversation_history(session_id)
    artifacts = await get_session_artifacts(session_id)
    state = await get_session_state(session_id)

    return {
        "success": True,
        "hasContext": extracted_text is not None,
        "extractedText": extracted_text,
        "state": state.get("state", "idle") if state else "idle",
        "processingDetails": state.get("processingDetails", {}) if state else {},
        "conversationHistory": [
            {
                "id": m.get("id"),
                "role": m.get("role"),
                "content": m.get("content"),
                "createdAt": m.get("createdAt"),
                "metadata": m.get("metadata", {})
            }
            for m in history
        ],
        "generatedArtifacts": [
            {
                "action": a.get("action"),
                "artifactType": a.get("artifactType"),
                "blobUrl": a.get("blobUrl"),
                "storagePath": a.get("storagePath"),
                "contextSummary": a.get("contextSummary"),
                "version": a.get("version", 1),
                "updatedAt": a.get("updatedAt")
            }
            for a in artifacts
        ],
    }


# ── Architecture Diagram Endpoints (React Flow) ────────────────


class ArchitectureGenerateRequest(BaseModel):
    session_id: str
    artifacts: list[ArtifactRef]
    instructions: str = ""
    answers: dict[str, str] = {}
    session_title: str = ""
    phase_type: str | None = None
    action: str = "architecture_diagram"


class ArchitectureUploadRequest(BaseModel):
    imageData: str  # base64 encoded PNG
    projectName: str
    contentType: str = "image/png"
    sessionId: str = ""
    sessionTitle: str = ""


@app.post("/api/agent/architecture/generate")
async def generate_architecture_graph(req: ArchitectureGenerateRequest):
    """Generate architecture diagram as graph data for React Flow rendering.

    Returns nodes, edges, and groups that the frontend will render
    using React Flow. User can then edit, drag nodes, and export as PNG.
    """
    try:
        await save_session_state(req.session_id, "generating", {"action": "architecture_diagram"})

        # Extract context from artifacts
        context = await _extract_and_save_context(req.session_id, req.artifacts)

        # Format answers
        answers_str = "\n".join(f"Q: {k}\nA: {v}" for k, v in req.answers.items()) if req.answers else ""

        # Generate graph using LLM
        if getattr(req, "action", "architecture_diagram") == "dfd":
            from tools.dfd_tool import generate_dfd
            result = await generate_dfd(
                context=context,
                instructions=req.instructions,
                answers=answers_str,
            )
            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated unified Data Flow Diagram for {result.get('project_name')}. You can now edit the diagram and export it.",
                metadata={"action": "dfd"}
            )
        else:
            result = await generate_architecture_diagram(
                context=context,
                instructions=req.instructions,
                answers=answers_str,
                phase_type=req.phase_type
            )
            await save_conversation_message(
                session_id=req.session_id,
                role="assistant",
                content=f"Generated architecture diagram for {result.get('project_name')}. You can now edit the diagram and export it.",
                metadata={"action": "architecture_diagram", "style": result.get("architecture_style")}
            )

        await save_session_state(req.session_id, "ready", {"last_action": "architecture_diagram"})

        return {
            "success": True,
            "project_name": result.get("project_name", "Architecture"),
            "architecture_style": result.get("architecture_style", "hybrid"),
            "graph": result.get("graph", {"groups": [], "nodes": [], "edges": []}),
        }

    except Exception as e:
        await save_session_state(req.session_id, "error", {"error": str(e), "action": "architecture_diagram"})
        return {"success": False, "error": str(e)}


@app.post("/api/agent/architecture/upload")
async def upload_architecture_image(req: ArchitectureUploadRequest):
    """Upload the rendered architecture diagram PNG from frontend.

    Frontend renders the React Flow diagram, exports as PNG,
    and sends base64 data here for storage.
    The artifact is also registered in Cosmos DB so that PPT generation
    can find and use it instead of auto-generating via Mermaid.
    """
    try:
        import base64
        from tools.architecture_tool import save_architecture_image

        # Decode base64 image data
        image_bytes = base64.b64decode(req.imageData)

        # Build session folder if session info provided
        session_folder = build_session_folder(req.sessionTitle, req.sessionId) if req.sessionTitle else None

        # Save to blob storage
        result = await save_architecture_image(image_bytes, req.projectName, session_folder=session_folder)

        if result.get("error"):
            return {"success": False, "error": result["error"]}

        # Register the artifact in Cosmos so PPT generation can find it
        if req.sessionId and result.get("url"):
            await save_generated_artifact(
                session_id=req.sessionId,
                action="architecture_diagram",
                artifact_type="png",
                blob_url=result["url"],
                storage_path=result.get("storage_path", ""),
                context_summary=f"User-exported React Flow architecture diagram for {req.projectName}",
                author_name=getattr(req, "author_name", None) or getattr(req, "display_name", None) or "Unknown"
            )

        return {
            "success": True,
            "url": result.get("url"),
            "storage_path": result.get("storage_path"),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ── Draw.io Diagram Endpoints ──────────────────────────────────


class DrawioGenerateRequest(BaseModel):
    session_id: str
    artifacts: list[ArtifactRef]
    instructions: str = ""
    answers: dict[str, str] = {}
    session_title: str = ""
    phase_type: str | None = None


class DrawioSaveRequest(BaseModel):
    session_id: str
    xml: str
    project_name: str = "architecture"
    session_title: str = ""
    image_data: str | None = None  # base64 encoded PNG/SVG export
    export_format: str = "xml"  # xml, png, svg


@app.post("/api/agent/drawio/generate")
async def generate_drawio_diagram_endpoint(req: DrawioGenerateRequest):
    """Generate a draw.io XML architecture diagram via LLM.

    Returns the XML content, edit URL (for opening in draw.io), and embed URL.
    The frontend can either:
    1. Open edit_url in a new tab to redirect to draw.io
    2. Load the XML into an embedded draw.io iframe for inline editing
    """
    try:
        await save_session_state(req.session_id, "generating", {"action": "drawio_diagram"})

        # Extract context from artifacts
        context = await _extract_and_save_context(req.session_id, req.artifacts)

        # Format answers
        answers_str = "\n".join(f"Q: {k}\nA: {v}" for k, v in req.answers.items()) if req.answers else ""

        session_folder = build_session_folder(req.session_title, req.session_id) if req.session_title else None

        result = await generate_drawio_architecture(
            context=context,
            instructions=req.instructions,
            answers=answers_str,
            phase_type=req.phase_type,
            session_folder=session_folder,
        )

        await save_conversation_message(
            session_id=req.session_id,
            role="assistant",
            content=f"Generated draw.io architecture diagram for {result.get('project_name')}. You can now edit it in draw.io and save when done.",
            metadata={"action": "drawio_diagram", "node_count": result.get("node_count"), "edge_count": result.get("edge_count")},
        )

        # Register in Cosmos if we got a blob URL
        if result.get("blob_url"):
            await save_generated_artifact(
                session_id=req.session_id,
                action="drawio_diagram",
                artifact_type="drawio",
                blob_url=result["blob_url"],
                storage_path=result.get("storage_path", ""),
                context_summary=f"Draw.io architecture diagram for {result.get('project_name')}",
                author_name="system",
            )

        # Also register the PNG image as architecture_diagram artifact
        if result.get("image_url"):
            await save_generated_artifact(
                session_id=req.session_id,
                action="architecture_diagram",
                artifact_type="png",
                blob_url=result["image_url"],
                storage_path=result.get("image_storage_path", ""),
                context_summary=f"Architecture diagram image for {result.get('project_name')}",
                author_name="system",
            )

        await save_session_state(req.session_id, "ready", {"last_action": "drawio_diagram"})

        return {
            "success": True,
            "project_name": result.get("project_name", "Architecture"),
            "title": result.get("title", "Architecture Diagram"),
            "xml": result.get("xml", ""),
            "edit_url": result.get("edit_url", ""),
            "embed_url": result.get("embed_url", ""),
            "blob_url": result.get("blob_url"),
            "image_url": result.get("image_url"),
            "node_count": result.get("node_count", 0),
            "edge_count": result.get("edge_count", 0),
        }

    except Exception as e:
        await save_session_state(req.session_id, "error", {"error": str(e), "action": "drawio_diagram"})
        return {"success": False, "error": str(e)}


@app.post("/api/agent/drawio/save")
async def save_drawio_diagram_endpoint(req: DrawioSaveRequest):
    """Save a draw.io diagram (edited XML and optional image export) to blob storage.

    Called when the user finishes editing in draw.io and clicks save.
    The XML is stored in blob storage, and an optional PNG/SVG export is also saved.
    """
    try:
        session_folder = build_session_folder(req.session_title, req.session_id) if req.session_title else None

        # Decode image data if provided
        image_bytes = None
        if req.image_data:
            import base64
            image_bytes = base64.b64decode(req.image_data)

        result = await save_drawio_diagram(
            xml=req.xml,
            project_name=req.project_name,
            session_folder=session_folder,
            export_format=req.export_format,
            image_data=image_bytes,
        )

        # Register artifact in Cosmos
        if result.get("xml_url"):
            await save_generated_artifact(
                session_id=req.session_id,
                action="drawio_diagram",
                artifact_type="drawio",
                blob_url=result["xml_url"],
                storage_path=result.get("xml_storage_path", ""),
                context_summary=f"Draw.io architecture diagram (edited) for {req.project_name}",
                author_name="user",
            )

        # Also register the exported image as architecture_diagram for PPT embedding
        if result.get("image_url"):
            await save_generated_artifact(
                session_id=req.session_id,
                action="architecture_diagram",
                artifact_type="png" if req.export_format != "svg" else "svg",
                blob_url=result["image_url"],
                storage_path=result.get("image_storage_path", ""),
                context_summary=f"Architecture diagram exported from draw.io for {req.project_name}",
                author_name="user",
            )

        await save_conversation_message(
            session_id=req.session_id,
            role="assistant",
            content=f"✅ Draw.io diagram saved for {req.project_name}." + (
                " The exported image is ready for use in presentations." if result.get("image_url") else ""
            ),
            metadata={"action": "drawio_save"},
        )

        return {
            "success": True,
            "xml_url": result.get("xml_url"),
            "image_url": result.get("image_url"),
            "xml_storage_path": result.get("xml_storage_path"),
            "image_storage_path": result.get("image_storage_path"),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Health Check Endpoint ───────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "optistudio-agent"}

# ── Admin Approval Endpoints ─────────────────────────────────


class ApproveArtifactRequest(BaseModel):
    session_id: str
    action: str  # e.g. "architecture_diagram", "presales_ppt", etc.
    artifact_type: str  # e.g. "pptx", "xlsx", "diagram"
    approved_by: str | None = None  # name of the admin who approved


class RejectArtifactRequest(BaseModel):
    session_id: str
    action: str
    artifact_type: str
    reason: str = ""


@app.get("/api/agent/admin/sessions")
async def admin_list_sessions_with_artifacts():
    """Admin: List all sessions that have generated artifacts.

    Returns a list of sessions with their generated artifact summaries
    for admin review/approval.
    """
    container = get_cosmos_container()
    if not container:
        return {"success": False, "error": "Cosmos DB not configured"}

    # Query all generated_artifact docs
    query = """
    SELECT c.sessionId, c.action, c.artifactType, c.blobUrl,
           c.storagePath, c.contextSummary, c.version, c.updatedAt,
           c.approvalStatus, c.author_name
    FROM c
    WHERE c.type = 'generated_artifact'
    ORDER BY c.updatedAt DESC
    """
    try:
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True,
        ))

        # Group by session
        sessions: dict[str, dict] = {}
        for item in items:
            sid = item["sessionId"]
            if sid not in sessions:
                sessions[sid] = {"session_id": sid, "artifacts": [], "latest_update": ""}
            sessions[sid]["artifacts"].append({
                "action": item.get("action"),
                "artifactType": item.get("artifactType"),
                "blobUrl": item.get("blobUrl"),
                "storagePath": item.get("storagePath"),
                "contextSummary": item.get("contextSummary"),
                "version": item.get("version", 1),
                "updatedAt": item.get("updatedAt", ""),
                "approvalStatus": item.get("approvalStatus", "pending"),
                "author_name": item.get("author_name", "Unknown"),
            })
            if item.get("updatedAt", "") > sessions[sid]["latest_update"]:
                sessions[sid]["latest_update"] = item.get("updatedAt", "")

        # Add session title and author_name for each session
        from utils.cosmos_service import get_session_state
        import asyncio
        async def get_title_and_author(sid, session):
            try:
                state = await get_session_state(sid)
                title = state.get("session_title") if state else None
                author = None
                # Fallback: use first artifact's file name and author_name
                artifacts = session.get("artifacts", [])
                if not title and artifacts:
                    file_name = artifacts[0].get("blobUrl") or artifacts[0].get("storagePath")
                    if file_name:
                        import os
                        base = os.path.basename(file_name)
                        name = os.path.splitext(base)[0]
                        title = name
                if artifacts:
                    author = artifacts[0].get("author_name") or "Unknown"
                return title or "Untitled", author or "Unknown"
            except Exception:
                return "Untitled", "Unknown"

        # Gather all titles and authors concurrently
        tasks = [get_title_and_author(sid, session) for sid, session in sessions.items()]
        titles_and_authors = await asyncio.gather(*tasks)
        for (sid, session), (title, author) in zip(sessions.items(), titles_and_authors):
            session["title"] = title
            session["author_name"] = author

        return {
            "success": True,
            "sessions": list(sessions.values()),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/agent/admin/approve")
async def admin_approve_artifact(req: ApproveArtifactRequest):
    """Admin: Approve an artifact and copy it to artifacts-approved container."""
    try:
        container = get_cosmos_container()
        if not container:
            return {"success": False, "error": "Cosmos DB not configured"}

        doc_id = f"artifact_{req.session_id}_{req.action}_{req.artifact_type}"
        item = container.read_item(item=doc_id, partition_key=req.session_id)

        storage_path = item.get("storagePath", "")
        if not storage_path:
            return {"success": False, "error": "No storage path found for artifact"}

        # Gather created_by and approved_by for blob metadata
        created_by = item.get("author_name") or "Unknown"
        approved_by = req.approved_by or "Admin"

        # Copy to approved container with metadata
        approved_url, _ = await copy_blob_to_approved(
            storage_path,
            metadata={"approved_by": approved_by, "created_by": created_by}
        )

        # Update Cosmos document with approval status
        item["approvalStatus"] = "approved"
        item["approvedAt"] = datetime.now(timezone.utc).isoformat()
        item["approvedBlobUrl"] = approved_url
        item["approvedBy"] = approved_by
        container.upsert_item(item)

        return {
            "success": True,
            "message": "Artifact approved and copied to approved container.",
            "approved_url": approved_url,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/agent/admin/reject")
async def admin_reject_artifact(req: RejectArtifactRequest):
    """Admin: Reject an artifact with a reason."""
    try:
        container = get_cosmos_container()
        if not container:
            return {"success": False, "error": "Cosmos DB not configured"}

        doc_id = f"artifact_{req.session_id}_{req.action}_{req.artifact_type}"
        item = container.read_item(item=doc_id, partition_key=req.session_id)

        item["approvalStatus"] = "rejected"
        item["rejectedAt"] = datetime.now(timezone.utc).isoformat()
        item["rejectionReason"] = req.reason
        container.upsert_item(item)

        return {
            "success": True,
            "message": "Artifact rejected.",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/agent/artifact-proxy/{blob_path:path}")
async def proxy_artifact_content(blob_path: str):
    """Proxy blob content through the backend to avoid browser CORS restrictions.

    Used by the frontend to fetch draw.io XML and other artifact content
    without hitting Azure Blob Storage directly (which blocks cross-origin fetch).
    """
    from fastapi.responses import Response as FastAPIResponse
    try:
        data = await download_blob(blob_path, container_name=settings.AZURE_BLOB_APPROVED_CONTAINER)
        if blob_path.endswith(".drawio"):
            media_type = "application/xml"
        elif blob_path.endswith(".png"):
            media_type = "image/png"
        elif blob_path.endswith(".svg"):
            media_type = "image/svg+xml"
        elif blob_path.endswith(".pdf"):
            media_type = "application/pdf"
        else:
            media_type = "application/octet-stream"
        return FastAPIResponse(content=data, media_type=media_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Artifact not found: {blob_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/approved-decks")
async def get_approved_decks():
    """Get all approved decks from artifacts-approved container.
    
    Accessible by Admin, Developer, and Architect roles.
    Returns list of approved artifacts with preview URLs.
    """
    try:
        artifacts = await list_approved_artifacts()
        return {
            "success": True,
            "artifacts": artifacts,
            "count": len(artifacts),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/agent/approved-decks/{blob_path:path}")
async def get_approved_deck_preview(blob_path: str):
    """Get preview URL for a specific approved deck.
    
    Returns a SAS URL that can be used to preview the file directly
    in the browser without downloading.
    """
    try:
        url = await get_approved_artifact_url(blob_path)
        return {
            "success": True,
            "blob_name": blob_path,
            "preview_url": url,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return {"success": False, "error": str(e)}


class UnifiedChatRequest(BaseModel):
    session_id: str
    message: str
    is_admin: bool = False

@app.post("/api/agent/unified-chat")
async def unified_chat(req: UnifiedChatRequest):
    """
    Unified router that directs queries between:
    1. Artifact Generation - Based on natural language intent
    2. Structured Data (SQL) - Admin Only
    3. Unstructured Data (RAG) - Admin Only
    4. Standard generative reply

    Enhanced to support natural language for artifact generation like:
    - "create an architecture diagram"
    - "generate a presentation for this project"
    - "I need a cost estimate"
    - "make a data flow diagram"
    """
    try:
        client = _get_chat_client()

        # 1. Enhanced Intent Routing Classifier with artifact generation support
        router_prompt = f"""You are an intelligent intent router for an enterprise Presales agent.
Analyze the user's message and determine the optimal action.

ARTIFACT GENERATION INTENTS (highest priority):
- If user wants to generate/create/make an architecture diagram, system design, or infrastructure diagram → "GENERATE_ARCHITECTURE"
- If user wants to generate/create/make a data flow diagram, DFD, or flow chart → "GENERATE_DFD"  
- If user wants to generate/create/make a presentation, PPT, slides, or proposal deck → "GENERATE_PPT"
- If user wants to generate/create/make a cost estimate, pricing, budget, or Azure cost report → "GENERATE_COST"
- If user wants to generate all artifacts or a complete package → "GENERATE_ALL"

QUERY INTENTS:
- If user asks about contents inside complex unstructured documents (architectural diagrams, docs, summarize) → "RAG"

OTHER:
- General conversation, greetings, help requests → "GENERAL"

IMPORTANT KEYWORDS TO RECOGNIZE:
- Architecture: "architecture", "system design", "infrastructure", "cloud architecture", "azure architecture", "diagram"
- DFD: "data flow", "dfd", "flow diagram", "data diagram", "level 0", "level 1"
- PPT: "presentation", "ppt", "slides", "deck", "proposal", "powerpoint"
- Cost: "cost", "pricing", "budget", "estimate", "azure cost", "cloud cost", "expenses"
- All: "generate all", "complete package", "everything", "all artifacts"

User Message: "{req.message}"

Return ONLY a JSON object:
{{
    "intent": "GENERATE_ARCHITECTURE" | "GENERATE_DFD" | "GENERATE_PPT" | "GENERATE_COST" | "GENERATE_ALL" | "RAG" | "GENERAL",
    "confidence": 0.0-1.0,
    "extracted_instructions": "any specific instructions from the user message"
}}"""

        route_res = client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[{"role": "user", "content": router_prompt}],
            response_format={"type": "json_object"}
        )
        import json
        intent_data = json.loads(route_res.choices[0].message.content)
        intent = intent_data.get("intent", "GENERAL")
        confidence = intent_data.get("confidence", 0.5)
        extracted_instructions = intent_data.get("extracted_instructions", "")

        # Map generation intents to actions
        generation_intent_map = {
            "GENERATE_ARCHITECTURE": "architecture_diagram",
            "GENERATE_DFD": "dfd",
            "GENERATE_PPT": "presales_ppt",
            "GENERATE_COST": "cost_report",
            "GENERATE_ALL": "generate_all"
        }

        # Handle artifact generation intents
        if intent in generation_intent_map:
            action = generation_intent_map[intent]
            action_labels = {
                "architecture_diagram": "Architecture Diagram",
                "dfd": "Data Flow Diagram",
                "presales_ppt": "Presales Presentation",
                "cost_report": "Azure Cost Report",
                "generate_all": "Complete Artifact Package"
            }

            return {
                "success": True,
                "response": f"I understand you want to generate a **{action_labels.get(action, action)}**. I'll start the generation process now.",
                "raw_query_executed": None,
                "trigger_action": action,
                "extracted_instructions": extracted_instructions,
                "confidence": confidence
            }

        # Guardrail for RAG
        if intent == "RAG" and not req.is_admin:
            return {
                "success": True,
                "response": "Access Denied: Querying global unstructured knowledge repositories is restricted to Admins.\n\nAs a Developer/Architect, you can still upload your own artifacts and generate architecture diagrams and presentations from them directly.",
                "raw_query_executed": None
            }

        # Execute Routing for RAG
        if intent == "RAG":
            from tools.rag_tool import query_unstructured_data
            rag_result = await query_unstructured_data(req.message, "RAG Query")
            if rag_result.get("success"):
                return {
                    "success": True,
                    "response": rag_result.get("response"),
                    "raw_query_executed": None
                }
            else:
                return {"success": False, "error": rag_result.get("error")}

        else:

            # General conversation - provide helpful response
            history = await get_conversation_history(req.session_id)
            previous_context = history[-3:] if history else 'None'
            prev_context_str = str(previous_context)
            general_prompt = f"""You are a helpful Presales assistant for OptiStudio. 
The user has sent a general message. Respond helpfully and conversationally.

If they seem to want to create artifacts but weren't specific, remind them they can:
- Generate Architecture Diagrams (just say "create an architecture diagram")
- Generate Data Flow Diagrams (just say "create a DFD")
- Generate Presales Presentations (just say "generate a presentation")
- Generate Azure Cost Reports (just say "create a cost estimate")

User message: {req.message}

Previous context (if any): {prev_context_str}

Respond naturally and helpfully."""

            general_res = client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a helpful Presales assistant."},
                    {"role": "user", "content": general_prompt}
                ]
            )

            return {
                "success": True,
                "response": general_res.choices[0].message.content,
                "raw_query_executed": None
            }

    except Exception as e:
        return {"success": False, "error": f"Runtime Router Error: {str(e)}"}


@app.post("/api/agent/debug/test-blob")
async def test_blob_access(req: ArtifactRef):
    """Debug endpoint to test blob storage access for a specific artifact."""
    try:
        from utils.blob_storage import get_blob_service_client

        client = get_blob_service_client()
        container = client.get_container_client(settings.AZURE_BLOB_CONTAINER)
        blob_client = container.get_blob_client(req.storage_path)

        # Check if blob exists
        exists = blob_client.exists()

        if not exists:
            # List all blobs to help debug
            all_blobs = list(container.list_blobs())
            return {
                "success": False,
                "error": f"Blob not found at path: {req.storage_path}",
                "container": settings.AZURE_BLOB_CONTAINER,
                "searched_path": req.storage_path,
                "available_blobs_sample": [b.name for b in all_blobs[:10]],
                "total_blobs_in_container": len(all_blobs)
            }

        # Get blob properties
        props = blob_client.get_blob_properties()

        # Try to download
        data = await download_blob(req.storage_path)

        return {
            "success": True,
            "message": "Blob accessible",
            "blob_size": props.size,
            "content_type": props.content_settings.content_type,
            "downloaded_size": len(data),
            "storage_path": req.storage_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "storage_path": req.storage_path,
            "container": settings.AZURE_BLOB_CONTAINER
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=settings.API_PORT, reload=True)
