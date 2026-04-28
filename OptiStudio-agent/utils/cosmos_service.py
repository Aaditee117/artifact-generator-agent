"""Azure Cosmos DB service for chat session data persistence."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from config import settings


_client: Optional[CosmosClient] = None
_container = None


def get_cosmos_container():
    """Get or create the Cosmos DB container."""
    global _client, _container
    
    if not settings.COSMOS_ENDPOINT or not settings.COSMOS_KEY:
        return None
    
    if _container is not None:
        return _container
    
    try:
        _client = CosmosClient(settings.COSMOS_ENDPOINT, settings.COSMOS_KEY)
        
        # Create database if not exists
        database = _client.create_database_if_not_exists(id=settings.COSMOS_DATABASE)
        
        # Create container if not exists with partition key on sessionId
        _container = database.create_container_if_not_exists(
            id=settings.COSMOS_CONTAINER,
            partition_key=PartitionKey(path="/sessionId"),
        )
        
        return _container
    except exceptions.CosmosHttpResponseError as e:
        print(f"Cosmos DB error: {e}")
        return None


async def save_extracted_text(session_id: str, artifacts: list, extracted_text: str) -> Optional[str]:
    """Save extracted text from artifacts to Cosmos DB."""
    container = get_cosmos_container()
    if not container:
        return None
    
    doc_id = f"extracted_{session_id}"
    document = {
        "id": doc_id,
        "sessionId": session_id,
        "type": "extracted_text",
        "artifacts": [
            {
                "fileName": a.get("file_name", ""),
                "category": a.get("category", "Document"),
                "storagePath": a.get("storage_path", "")
            }
            for a in artifacts
        ],
        "extractedText": extracted_text,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    
    import asyncio
    try:
        await asyncio.to_thread(container.upsert_item, document)
        return doc_id
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving extracted text: {e}")
        return None


async def get_extracted_text(session_id: str) -> Optional[str]:
    """Get previously extracted text for a session."""
    container = get_cosmos_container()
    if not container:
        return None
    
    doc_id = f"extracted_{session_id}"
    import asyncio
    try:
        item = await asyncio.to_thread(container.read_item, doc_id, session_id)
        return item.get("extractedText")
    except exceptions.CosmosResourceNotFoundError:
        return None
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error reading extracted text: {e}")
        return None


async def get_all_extracted_texts() -> list:
    """Get all extracted texts across the repository for RAG context."""
    container = get_cosmos_container()
    if not container:
        return []
    
    query = "SELECT c.id, c.sessionId, c.artifacts, c.extractedText FROM c WHERE c.type = 'extracted_text'"
    import asyncio
    try:
        items = await asyncio.to_thread(
            lambda: list(container.query_items(query=query, enable_cross_partition_query=True))
        )
        return items
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error querying all extracted texts: {e}")
        return []


async def save_conversation_message(
    session_id: str,
    role: str,
    content: str,
    artifacts: Optional[list] = None,
    metadata: Optional[dict] = None
) -> Optional[str]:
    """Save a conversation message to Cosmos DB."""
    container = get_cosmos_container()
    if not container:
        return None
    
    message_id = str(uuid.uuid4())
    document = {
        "id": message_id,
        "sessionId": session_id,
        "type": "conversation_message",
        "role": role,  # "user" or "assistant"
        "content": content,
        "artifacts": artifacts or [],
        "metadata": metadata or {},
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    import asyncio
    try:
        await asyncio.to_thread(container.create_item, document)
        return message_id
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving conversation message: {e}")
        return None


async def get_conversation_history(session_id: str, limit: int = 50) -> list:
    """Get conversation history for a session."""
    container = get_cosmos_container()
    if not container:
        return []
    
    query = """
    SELECT * FROM c 
    WHERE c.sessionId = @sessionId AND c.type = 'conversation_message'
    ORDER BY c.createdAt ASC
    OFFSET 0 LIMIT @limit
    """
    
    import asyncio
    try:
        items = await asyncio.to_thread(
            lambda: list(container.query_items(
                query=query,
                parameters=[
                    {"name": "@sessionId", "value": session_id},
                    {"name": "@limit", "value": limit}
                ],
                enable_cross_partition_query=False
            ))
        )
        return items
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error getting conversation history: {e}")
        return []


async def save_generated_prompt(
    session_id: str,
    action: str,
    prompt: str,
    context_summary: str = "",
    generated_url: Optional[str] = None
) -> Optional[str]:
    """Save a generated prompt for reproducibility."""
    container = get_cosmos_container()
    if not container:
        return None
    
    # Use a deterministic ID so we can update it
    doc_id = f"prompt_{session_id}_{action}"
    document = {
        "id": doc_id,
        "sessionId": session_id,
        "type": "generated_prompt",
        "action": action,
        "prompt": prompt,
        "contextSummary": context_summary,
        "generatedUrl": generated_url,
        "version": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    
    import asyncio
    try:
        # Try to read existing to increment version
        existing = None
        try:
            existing = await asyncio.to_thread(container.read_item, doc_id, session_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
        
        if existing:
            document["version"] = existing.get("version", 0) + 1
            document["createdAt"] = existing.get("createdAt", document["createdAt"])
            document["previousPrompt"] = existing.get("prompt")
        
        await asyncio.to_thread(container.upsert_item, document)
        return doc_id
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving generated prompt: {e}")
        return None


async def get_generated_prompt(session_id: str, action: str) -> Optional[dict]:
    """Get the latest generated prompt for a session and action."""
    container = get_cosmos_container()
    if not container:
        return None
    
    doc_id = f"prompt_{session_id}_{action}"
    import asyncio
    try:
        item = await asyncio.to_thread(container.read_item, doc_id, session_id)
        return item
    except exceptions.CosmosResourceNotFoundError:
        return None
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error reading generated prompt: {e}")
        return None


async def save_session_state(
    session_id: str,
    state: str,
    processing_details: Optional[dict] = None
) -> Optional[str]:
    """Save session processing state."""
    container = get_cosmos_container()
    if not container:
        return None
    
    doc_id = f"state_{session_id}"
    document = {
        "id": doc_id,
        "sessionId": session_id,
        "type": "session_state",
        "state": state,  # "idle", "processing_artifacts", "ready", "generating"
        "processingDetails": processing_details or {},
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    
    import asyncio
    try:
        await asyncio.to_thread(container.upsert_item, document)
        return doc_id
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving session state: {e}")
        return None


async def get_session_state(session_id: str) -> Optional[dict]:
    """Get session processing state."""
    container = get_cosmos_container()
    if not container:
        return None
    
    doc_id = f"state_{session_id}"
    import asyncio
    try:
        item = await asyncio.to_thread(container.read_item, doc_id, session_id)
        return item
    except exceptions.CosmosResourceNotFoundError:
        return {"state": "idle", "processingDetails": {}}
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error reading session state: {e}")
        return None


async def save_generated_artifact(
    session_id: str,
    action: str,
    artifact_type: str,
    blob_url: str,
    storage_path: str,
    prompt_used: Optional[str] = None,
    context_summary: Optional[str] = None,
    author_name: Optional[str] = None
) -> Optional[str]:
    """Save reference to a generated artifact (image, PPT, etc.)."""
    container = get_cosmos_container()
    if not container:
        return None

    # Use deterministic ID for the latest version
    doc_id = f"artifact_{session_id}_{action}_{artifact_type}"
    document = {
        "id": doc_id,
        "sessionId": session_id,
        "type": "generated_artifact",
        "action": action,
        "artifactType": artifact_type,
        "blobUrl": blob_url,
        "storagePath": storage_path,
        "promptUsed": prompt_used,
        "contextSummary": context_summary,
        "version": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "author_name": author_name or "Unknown"
    }

    import asyncio
    try:
        existing = None
        try:
            existing = await asyncio.to_thread(container.read_item, doc_id, session_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
        
        if existing:
            document["version"] = existing.get("version", 0) + 1
            document["createdAt"] = existing.get("createdAt", document["createdAt"])
        
        await asyncio.to_thread(container.upsert_item, document)
        return doc_id
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving generated artifact: {e}")
        return None


async def get_session_artifacts(session_id: str) -> list:
    """Get all generated artifacts for a session."""
    container = get_cosmos_container()
    if not container:
        return []
    
    query = """
    SELECT * FROM c 
    WHERE c.sessionId = @sessionId AND c.type = 'generated_artifact'
    ORDER BY c.updatedAt DESC
    """
    
    import asyncio
    try:
        items = await asyncio.to_thread(
            lambda: list(container.query_items(
                query=query,
                parameters=[{"name": "@sessionId", "value": session_id}],
                enable_cross_partition_query=False
            ))
        )
        return items
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error getting session artifacts: {e}")
        return []
