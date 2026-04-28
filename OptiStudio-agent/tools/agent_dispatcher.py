
import json
from typing import Optional
from config import settings
from tools.rag_tool import query_unstructured_data

"""
AGENT_TOOLS defines the list of tools/functions that the agent can call.
Currently, only 'query_unstructured_data' is exposed. This is intentional:
- All references to other tools (e.g., get_database_schema, execute_admin_sql) must be removed from tests and callers for consistency.
- If additional tools are needed in the future, add them here and implement their handling in dispatch_tool_call.
"""
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_unstructured_data",
            "description": "Call this to retrieve information from unstructured project and architectural documents via Semantic RAG search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "The natural language search query to run against the unstructured document repository."
                    }
                },
                "required": ["search_query"]
            }
        }
    }
]

async def dispatch_tool_call(tool_name: str, arguments: str) -> tuple[str, Optional[str], Optional[str]]:
    """Executes a tool call and returns (string_result_for_llm, raw_sql_if_any, raw_toon_if_any)"""
    try:
        args = json.loads(arguments)
        
        if tool_name == "query_unstructured_data":
            search_query = args.get("search_query", "")
            res = await query_unstructured_data(search_query, "Agent Loop")
            # For RAG, the response is just english text.
            if res.get("success"):
                return res.get("response", ""), None, None
            else:
                return f"RAG Error: {res.get('error')}", None, None
                
        else:
            return f"Unknown tool: {tool_name}", None, None
    except Exception as e:
        return f"Tool Parsing Error: {str(e)}", None, None
