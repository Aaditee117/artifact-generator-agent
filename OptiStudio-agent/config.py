import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_IMAGE_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT", "FLUX.1-Kontext-pro")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_BLOB_CONNECTION_STRING: str = os.getenv("AZURE_BLOB_CONNECTION_STRING", "")
    AZURE_BLOB_CONTAINER: str = os.getenv("AZURE_BLOB_CONTAINER", "artifacts-generated")
    AZURE_BLOB_APPROVED_CONTAINER: str = os.getenv("AZURE_BLOB_APPROVED_CONTAINER", "artifacts-approved")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8001"))
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Cosmos DB settings
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "OptiStudioDb")
    COSMOS_CONTAINER: str = os.getenv("COSMOS_CONTAINER", "chat-sessions")

    # SQL DB
    DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING", "Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=OptiStudioDb;Trusted_Connection=yes;")


settings = Settings()
