import asyncio
from openai import AzureOpenAI, APIConnectionError, RateLimitError
from config import settings
from utils.cosmos_service import get_all_extracted_texts


# Lazy-initialize the AzureOpenAI client for better testability and flexibility
_client = None
def _get_client():
    global _client
    if _client is None:
        _client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
    return _client

async def query_unstructured_data(query: str, request_intent: str) -> dict:
    """
    Retrieves extracted text from all available project documents in Cosmos DB 
    and uses Azure OpenAI to formulate an answer mapping exactly from the documents.
    """
    try:
        # 1. Fetch all documents from Cosmos DB
        all_docs = await get_all_extracted_texts()
        
        if not all_docs:
            return {"success": True, "response": "No unstructured documents found in the repository. Please upload presales or architecture documents first."}
        
        # 2. Compile context
        # For MVP, combining them. GPT-4o 128k context can effortlessly handle this.
        context_blocks = []
        for doc in all_docs:
            artifacts = doc.get("artifacts", [])
            filenames = ", ".join([a.get("fileName", "Unknown") for a in artifacts])
            text = doc.get("extractedText", "")
            if text:
                context_blocks.append(f"--- SOURCE DOCUMENT(S): {filenames} (Session {doc.get('sessionId')}) ---\n{text}")
                
        full_context = "\n\n".join(context_blocks)
        
        # Guard against massive token overflow (roughly 100k tokens)
        if len(full_context) > 300000:
            full_context = full_context[:300000] + "... [TRUNCATED]"

        # 3. Ask LLM to answer the user based on the context
        rag_prompt = f"""You are an enterprise knowledge assistant analyzing internal presales and project documents.
Use ONLY the provided document context below to answer the user's question accurately.
If the answer is not contained in the context, explicitly say that you do not have that information in the unstructured repository.
When providing information, briefly cite the source file name it was found in so the user trusts the data.

--- USER QUESTION ---
{query}

--- REPOSITORY CONTEXT ---
{full_context}
"""

        max_retries = 3
        response = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = _get_client().chat.completions.create(
                    model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                    messages=[{"role": "user", "content": rag_prompt}],
                    temperature=0.3
                )
                break
            except (APIConnectionError, RateLimitError) as e:
                last_error = e
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_error = e
                break
                
        if not response:
            error_msg = f"Azure OpenAI RAG Error: {str(last_error)}" if last_error else "Failed to generate RAG summary."
            return {"success": False, "error": error_msg}
            
        answer = response.choices[0].message.content
        
        return {
            "success": True,
            "response": answer,
            "intent": request_intent
        }
    except Exception as e:
        return {"success": False, "error": f"RAG Retrieval Error: {str(e)}"}
