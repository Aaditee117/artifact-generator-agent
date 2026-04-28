"""Azure Blob Storage upload/download helpers."""

import re
import uuid
import logging
from urllib.parse import unquote
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceExistsError
from datetime import datetime, timedelta, timezone
from config import settings

logger = logging.getLogger(__name__)


def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(settings.AZURE_BLOB_CONNECTION_STRING)


def _ensure_container(client: BlobServiceClient, container_name: str):
    """Create a container if it does not exist."""
    container = client.get_container_client(container_name)
    try:
        container.create_container()
    except ResourceExistsError:
        # Container already exists, this is expected
        pass
    except Exception as e:
        logging.error(f"Failed to create container '{container_name}': {type(e).__name__}: {e}")
        raise
    return container


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:80] if text else 'untitled'


def build_session_folder(session_title: str, session_id: str) -> str:
    """Build the unique folder name for a session: {slug}_{short-id}."""
    slug = slugify(session_title or "untitled")
    short_id = session_id[:8] if len(session_id) >= 8 else session_id
    return f"{slug}_{short_id}"


def _generate_sas_url(client: BlobServiceClient, container_name: str, storage_path: str, blob_client) -> str:
    """Generate a SAS URL for a blob."""
    sas_token = generate_blob_sas(
        account_name=client.account_name,
        container_name=container_name,
        blob_name=storage_path,
        account_key=client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    return f"{blob_client.url}?{sas_token}"


import asyncio

async def upload_bytes(
    data: bytes,
    file_name: str,
    content_type: str,
    session_folder: str | None = None,
    subfolder: str = "generated",
    container_name: str | None = None,
) -> tuple[str, str]:
    """Upload bytes to Azure Blob Storage. Offloads blocking upload to a thread."""
    client = get_blob_service_client()
    target_container = container_name or settings.AZURE_BLOB_CONTAINER
    container = _ensure_container(client, target_container)

    if session_folder:
        storage_path = f"{session_folder}/{subfolder}/{file_name}"
    else:
        storage_path = f"generated/{uuid.uuid4()}/{file_name}"

    blob_client = container.get_blob_client(storage_path)

    def _upload():
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

    await asyncio.to_thread(_upload)

    sas_url = _generate_sas_url(client, target_container, storage_path, blob_client)
    return sas_url, storage_path


async def copy_blob_to_approved(storage_path: str, metadata: dict | None = None) -> tuple[str, str]:
    """
    Copy a blob from the artifacts container to artifacts-approved.

    Returns (sas_url, new_storage_path) in the approved container.

    Note:
        start_copy_from_url() initiates a server-side async copy; returning a SAS URL immediately can yield a URL to a blob that is still in pending copy status.
        Consider polling get_blob_properties().copy.status until success (or failing on failed/aborted) before returning, or document that callers must handle eventual consistency.
    """
    client = get_blob_service_client()
    src_container = client.get_container_client(settings.AZURE_BLOB_CONTAINER)
    dst_container = _ensure_container(client, settings.AZURE_BLOB_APPROVED_CONTAINER)

    src_blob = src_container.get_blob_client(storage_path)
    dst_blob = dst_container.get_blob_client(storage_path)

    # Pass metadata (approved_by, created_by) directly to the copy operation
    safe_metadata = {k: str(v) for k, v in metadata.items()} if metadata else None
    dst_blob.start_copy_from_url(src_blob.url, metadata=safe_metadata)
    sas_url = _generate_sas_url(client, settings.AZURE_BLOB_APPROVED_CONTAINER, storage_path, dst_blob)
    return sas_url, storage_path


import asyncio

async def download_blob(storage_path: str, container_name: str | None = None) -> bytes:
    """Download a blob by its storage path. Offloads blocking I/O to a thread and uses structured logging."""
    decoded_path = unquote(storage_path)
    target_container = container_name or settings.AZURE_BLOB_CONTAINER

    logger.info(f"Attempting to download blob: original path='%s', decoded path='%s', container='%s'", storage_path, decoded_path, target_container)

    client = get_blob_service_client()
    container = client.get_container_client(target_container)
    blob_client = container.get_blob_client(decoded_path)

    # Avoid logging blob_client.url in production for security reasons

    def _download():
        try:
            data = blob_client.download_blob().readall()
            logger.info(f"Downloaded %d bytes from blob '%s' in container '%s'", len(data), decoded_path, target_container)
            return data
        except Exception as e:
            logger.error(f"Download failed for blob '%s' in container '%s': %s: %s", decoded_path, target_container, type(e).__name__, e)
            raise

    return await asyncio.to_thread(_download)



async def list_approved_artifacts() -> list[dict]:
    """
    List all approved artifacts from the artifacts-approved container.

    Returns list of dicts with:
      - name: blob name/path
      - size: file size in bytes
      - last_modified: datetime
      - content_type: MIME type
      - url: SAS URL for direct access/preview

    This function offloads all blocking Azure SDK calls to a thread to avoid blocking the event loop.
    """
    import concurrent.futures
    client = get_blob_service_client()
    container = client.get_container_client(settings.AZURE_BLOB_APPROVED_CONTAINER)

    def _list_blobs_and_metadata():
        artifacts = []
        try:
            blob_list = list(container.list_blobs(include=['metadata']))
            for blob in blob_list:
                blob_client = container.get_blob_client(blob.name)
                try:
                    props = blob_client.get_blob_properties()
                    content_type = props.content_settings.content_type if props.content_settings else None
                except Exception:
                    content_type = None
                sas_url = _generate_sas_url(
                    client,
                    settings.AZURE_BLOB_APPROVED_CONTAINER,
                    blob.name,
                    blob_client
                )
                blob_metadata = blob.metadata or {}
                artifacts.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "content_type": content_type,
                    "url": sas_url,
                    "approved_by": blob_metadata.get("approved_by"),
                    "created_by": blob_metadata.get("created_by"),
                })
        except Exception as e:
            logging.error(f"Failed to list approved artifacts: {e}")
            raise
        return artifacts

    return await asyncio.to_thread(_list_blobs_and_metadata)


async def get_approved_artifact_url(blob_name: str) -> str:
    """Get SAS URL for a specific approved artifact for preview/download."""
    client = get_blob_service_client()
    container = client.get_container_client(settings.AZURE_BLOB_APPROVED_CONTAINER)
    blob_client = container.get_blob_client(blob_name)
    
    # Check if blob exists (offload to thread)
    from azure.core.exceptions import ResourceNotFoundError
    import asyncio
    def _check_exists():
        try:
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
    exists = await asyncio.to_thread(_check_exists)
    if not exists:
        raise FileNotFoundError(f"Approved artifact not found: {blob_name}")

    sas_url = _generate_sas_url(
        client, 
        settings.AZURE_BLOB_APPROVED_CONTAINER, 
        blob_name, 
        blob_client
    )
    return sas_url
