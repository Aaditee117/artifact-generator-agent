"""Image generation via Azure OpenAI (supports DALL-E 3 and FLUX models)."""

import base64
import httpx
import logging
logger = logging.getLogger(__name__)
from openai import AzureOpenAI
from config import settings

# Set to True to log sensitive prompt details for debugging only
DEBUG_IMAGE_GEN = False


def _get_client():
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


async def generate_image(prompt, size="1024x1024"):
    """Generate an image. Works with DALL-E 3 and FLUX models.
    Returns (image_bytes, prompt_used).
    """
    client = _get_client()
    model = settings.AZURE_OPENAI_IMAGE_DEPLOYMENT

    logger.info(f"Generating image with model: {model}")
    logger.info(f"Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    logger.info(f"API Version: {settings.AZURE_OPENAI_API_VERSION}")
    logger.info(f"Prompt length: {len(prompt)} characters")
    if DEBUG_IMAGE_GEN:
        logger.debug(f"Prompt preview: {prompt[:200]}...")
    else:
        logger.debug("Prompt preview: [REDACTED]")

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size,
        )
        logger.info("Image generation API call successful")
        logger.info(f"Response data count: {len(response.data) if response.data else 0}")
    except Exception as e:
        logger.error(f"Image generation API error: {type(e).__name__}: {e}")
        # Check if this is a deployment not found error
        error_str = str(e).lower()
        if "deployment" in error_str or "not found" in error_str:
            logger.error(f"TIP: Check that '{model}' is a valid deployment name in your Azure AI Foundry")
        raise RuntimeError(f"Image generation failed: {e}") from e

    if not response.data or len(response.data) == 0:
        logger.error("No images returned from API")
        raise RuntimeError("Image generation returned no results")

    image_data = response.data[0]
    prompt_used = getattr(image_data, 'revised_prompt', None) or prompt

    # Handle both response formats: URL (DALL-E 3) and b64_json (FLUX)
    image_url = getattr(image_data, 'url', None)
    b64_json = getattr(image_data, 'b64_json', None)

    if b64_json:
        # FLUX models return base64-encoded image data
        logger.info(f"Received base64-encoded image data ({len(b64_json)} chars)")
        img_bytes = base64.b64decode(b64_json)
        logger.info(f"Decoded {len(img_bytes)} bytes")
        return img_bytes, prompt_used

    if image_url:
        logger.info(f"Image URL received: {image_url[:100]}...")
        logger.info("Image generated, downloading from URL...")

        async with httpx.AsyncClient(timeout=60) as http:
            img_response = await http.get(image_url)
            img_response.raise_for_status()

        logger.info(f"Downloaded {len(img_response.content)} bytes")
        return img_response.content, prompt_used

    # Neither URL nor b64_json available
    logger.error("No image data in API response (neither url nor b64_json)")
    logger.error(f"Full response.data[0]: {image_data}")
    raise RuntimeError("Image generation returned no image data (neither url nor b64_json)")

