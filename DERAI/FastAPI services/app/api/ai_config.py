"""AI provider configuration endpoint — /ai-providers."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["AI Configuration"])


# ── Available models per provider ──
PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini",
    ],
    "github_copilot": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "o1-preview",
        "o1-mini",
        "Mistral-large-2411",
        "Mistral-small",
        "Meta-Llama-3.1-405B-Instruct",
        "Meta-Llama-3.1-70B-Instruct",
        "Phi-3.5-mini-instruct",
        "AI21-Jamba-1.5-Large",
        "Cohere-command-r-plus-08-2024",
    ],
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ],
    "google_gemini": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-pro",
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    "regex_only": [
        "regex",
    ],
}


class AIProviderStatus(BaseModel):
    """Status of a single AI provider."""
    id: str
    name: str
    configured: bool
    model: str
    available_models: list[str]


class AIProvidersResponse(BaseModel):
    """Response listing all available AI providers."""
    current_provider: str
    providers: list[AIProviderStatus]


@router.get("/ai-providers", response_model=AIProvidersResponse)
async def get_ai_providers() -> AIProvidersResponse:
    """List available AI providers, their configuration status, and available models."""
    providers = [
        AIProviderStatus(
            id="openai",
            name="OpenAI",
            configured=bool(settings.openai_api_key),
            model=settings.openai_model,
            available_models=PROVIDER_MODELS["openai"],
        ),
        AIProviderStatus(
            id="github_copilot",
            name="GitHub Copilot (Models API)",
            configured=bool(settings.github_token),
            model=settings.github_model,
            available_models=PROVIDER_MODELS["github_copilot"],
        ),
        AIProviderStatus(
            id="anthropic",
            name="Anthropic Claude",
            configured=bool(settings.anthropic_api_key),
            model=settings.anthropic_model,
            available_models=PROVIDER_MODELS["anthropic"],
        ),
        AIProviderStatus(
            id="google_gemini",
            name="Google Gemini",
            configured=bool(settings.google_api_key),
            model=settings.google_model,
            available_models=PROVIDER_MODELS["google_gemini"],
        ),
        AIProviderStatus(
            id="deepseek",
            name="DeepSeek",
            configured=bool(settings.deepseek_api_key),
            model=settings.deepseek_model,
            available_models=PROVIDER_MODELS["deepseek"],
        ),
        AIProviderStatus(
            id="regex_only",
            name="Regex Only (no AI)",
            configured=True,
            model="regex",
            available_models=PROVIDER_MODELS["regex_only"],
        ),
    ]
    return AIProvidersResponse(
        current_provider=settings.ai_provider,
        providers=providers,
    )
