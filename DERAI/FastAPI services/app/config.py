"""Application configuration using Pydantic BaseSettings (env-driven)."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """All configuration is read from environment variables / .env file."""

    # --- Application ---
    app_name: str = "DERAI FastAPI Services"
    app_version: str = "1.0.0"
    debug: bool = False

    # --- Security ---
    api_key: str = Field(default="dev-api-key-change-me", description="API key for request authentication")

    # --- External PDF API ---
    pdf_api_base_url: str = "http://localhost:9000/api/v1"
    pdf_api_timeout: int = 30

    # --- Spring Boot service ---
    springboot_url: str = "http://localhost:8080"
    springboot_timeout: int = 30

    # --- AI / LLM ---
    ai_provider: str = "openai"  # openai | github_copilot | anthropic | google_gemini | regex_only
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    github_token: str = ""  # GitHub PAT with copilot scope — uses GitHub Models API
    github_model: str = "gpt-4o"  # model served via GitHub Models endpoint
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    google_api_key: str = ""
    google_model: str = "gemini-1.5-pro"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    ai_temperature: float = 0.0
    ai_max_tokens: int = 4096

    # --- Snowflake (Statements) ---
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_database: str = ""
    snowflake_schema: str = ""
    snowflake_warehouse: str = ""

    # --- DB2 (Letters & Confirms) ---
    db2_host: str = ""
    db2_port: int = 50000
    db2_database: str = ""
    db2_user: str = ""
    db2_password: str = ""

    # --- Azure Document Intelligence (OCR) ---
    azure_doc_endpoint: str = ""
    azure_doc_api_key: str = ""
    azure_doc_model: str = "prebuilt-read"

    # --- Logging ---
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance
settings = Settings()
