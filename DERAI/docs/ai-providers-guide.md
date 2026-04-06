# AI Providers & Model Selection Guide

## Overview

DERAI supports **6 AI providers** for document classification and structured data extraction.
Each provider offers multiple models that can be selected at runtime via the UI or API.

| Provider | Models | Requires API Key | Endpoint |
|----------|--------|-------------------|----------|
| **OpenAI** | 7 | Yes | `https://api.openai.com/v1` |
| **GitHub Copilot (Models API)** | 12 | Yes (GitHub PAT) | `https://models.inference.ai.azure.com` |
| **Anthropic Claude** | 6 | Yes | `https://api.anthropic.com` |
| **Google Gemini** | 6 | Yes | `https://generativelanguage.googleapis.com` |
| **DeepSeek** | 2 | Yes | `https://api.deepseek.com` |
| **Regex Only** | 1 | No | N/A (local) |

---

## Strategy & Approach

### Why Multi-Provider?

1. **Cost optimization** — Use cheaper models (GPT-4o-mini, Gemini Flash) for simple docs, powerful models (GPT-4o, Claude Opus) for complex ones
2. **Resilience** — If one provider is down or rate-limited, switch to another
3. **Comparison** — Evaluate extraction quality across providers for the same document
4. **Compliance** — Some organizations restrict which AI providers can be used
5. **Fallback** — Regex-only mode works without any API key for basic extraction

### Architecture Decision

- **Runtime selection**: Provider and model are chosen per-request, not globally
- **OpenAI-compatible pattern**: GitHub Copilot and DeepSeek both use OpenAI-compatible APIs, reducing integration code
- **Graceful degradation**: If AI fails, regex fallback extracts basic fields

---

## Provider Details & Available Models

### 1. OpenAI

| Model | Best For | Context Window |
|-------|----------|----------------|
| `gpt-4o` | Best quality, multimodal | 128K |
| `gpt-4o-mini` | Fast, cheap, good quality | 128K |
| `gpt-4-turbo` | High quality with vision | 128K |
| `gpt-4` | Original GPT-4 | 8K |
| `gpt-3.5-turbo` | Fastest, cheapest | 16K |
| `o1-preview` | Advanced reasoning | 128K |
| `o1-mini` | Reasoning, cost-effective | 128K |

**Default model**: `gpt-4o`

### 2. GitHub Copilot (Models API)

Uses Azure AI Inference endpoint with a GitHub Personal Access Token.
Offers models from multiple providers through a single API key.

| Model | Publisher | Best For |
|-------|-----------|----------|
| `gpt-4o` | OpenAI | Best quality |
| `gpt-4o-mini` | OpenAI | Fast & cheap |
| `gpt-4-turbo` | OpenAI | High quality |
| `o1-preview` | OpenAI | Reasoning |
| `o1-mini` | OpenAI | Reasoning (cheap) |
| `Mistral-large-2411` | Mistral AI | Strong multilingual |
| `Mistral-small` | Mistral AI | Fast & efficient |
| `Meta-Llama-3.1-405B-Instruct` | Meta | Largest open model |
| `Meta-Llama-3.1-70B-Instruct` | Meta | Good balance |
| `Phi-3.5-mini-instruct` | Microsoft | Small & fast |
| `AI21-Jamba-1.5-Large` | AI21 Labs | Long context |
| `Cohere-command-r-plus-08-2024` | Cohere | RAG-optimized |

**Default model**: `gpt-4o`

### 3. Anthropic Claude

| Model | Best For | Context Window |
|-------|----------|----------------|
| `claude-sonnet-4-20250514` | Best balance (latest) | 200K |
| `claude-opus-4-20250514` | Highest quality (latest) | 200K |
| `claude-3-5-sonnet-20241022` | Previous best balance | 200K |
| `claude-3-5-haiku-20241022` | Fast & cheap | 200K |
| `claude-3-opus-20240229` | Previous highest quality | 200K |
| `claude-3-haiku-20240307` | Fastest | 200K |

**Default model**: `claude-sonnet-4-20250514`

### 4. Google Gemini

| Model | Best For | Context Window |
|-------|----------|----------------|
| `gemini-1.5-pro` | Best quality | 2M |
| `gemini-1.5-flash` | Fast & efficient | 1M |
| `gemini-1.5-flash-8b` | Ultra-fast, cheapest | 1M |
| `gemini-2.0-flash` | Next-gen fast | 1M |
| `gemini-2.0-flash-lite` | Next-gen ultra-fast | 1M |
| `gemini-pro` | Original Gemini | 32K |

**Default model**: `gemini-1.5-pro`

### 5. DeepSeek

| Model | Best For | Context Window |
|-------|----------|----------------|
| `deepseek-chat` | General chat & extraction | 64K |
| `deepseek-reasoner` | Complex reasoning tasks | 64K |

**Default model**: `deepseek-chat`  
**Note**: DeepSeek uses an OpenAI-compatible API at `https://api.deepseek.com`.

### 6. Regex Only

| Model | Description |
|-------|-------------|
| `regex` | Pattern-matching extraction without AI |

No API key needed. Useful for testing or when AI is not required.

---

## Generating API Keys

### OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** → **Create new secret key**
4. Copy the key (starts with `sk-`)
5. Add billing: **Settings** → **Billing** → Add payment method
6. Set in `.env`: `OPENAI_API_KEY=sk-your-key-here`

### GitHub Copilot (Personal Access Token)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scopes: `copilot` (or use fine-grained tokens with Copilot access)
4. Copy the token (starts with `ghp_`)
5. Requires: Active GitHub Copilot subscription (Individual, Business, or Enterprise)
6. Set in `.env`: `GITHUB_TOKEN=ghp_your-token-here`

### Anthropic Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-`)
5. Add credits: **Settings** → **Billing** → Add payment method
6. Set in `.env`: `ANTHROPIC_API_KEY=sk-ant-your-key-here`

### Google Gemini API Key

1. Go to [aistudio.google.com](https://aistudio.google.com/)
2. Sign in with Google account
3. Click **Get API Key** → **Create API key**
4. Select or create a Google Cloud project
5. Copy the key
6. Set in `.env`: `GOOGLE_API_KEY=your-key-here`

### DeepSeek API Key

1. Go to [platform.deepseek.com](https://platform.deepseek.com/)
2. Sign up or log in
3. Navigate to **API Keys** → **Create new key**
4. Copy the key
5. Add credits: **Top Up** in the billing section
6. Set in `.env`: `DEEPSEEK_API_KEY=your-key-here`

---

## Configuration

### Environment Variables (`.env`)

```bash
# Choose default provider
AI_PROVIDER=openai   # openai | github_copilot | anthropic | google_gemini | deepseek | regex_only

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# GitHub Copilot
GITHUB_TOKEN=ghp_...
GITHUB_COPILOT_MODEL=gpt-4o

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Google Gemini
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-1.5-pro

# DeepSeek
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-chat
```

### Selecting Provider & Model in the UI

1. Open the DERAI dashboard at `http://localhost:3000`
2. In the upload form, select an **AI Provider** from the dropdown
   - Green checkmark = API key configured
   - Grey icon = API key not set
   - Badge shows number of available models
3. Select an **AI Model** from the second dropdown
   - Models update automatically based on selected provider
   - Default model is marked with a "default" badge
4. Upload a PDF and process — the selected provider/model will be used

### Selecting Provider & Model via API

```bash
curl -X POST http://localhost:8000/api/v1/upload-and-process \
  -F "file=@document.pdf" \
  -F "account_number=ACC001" \
  -F "document_type=bank_statement" \
  -F "extraction_engine=pdfminer" \
  -F "ai_provider=github_copilot" \
  -F "ai_model=Meta-Llama-3.1-405B-Instruct"
```

### Checking Provider Status via API

```bash
curl http://localhost:8000/api/v1/ai-providers
```

Returns:
```json
{
  "current_provider": "openai",
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "configured": true,
      "model": "gpt-4o",
      "available_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", ...]
    },
    ...
  ]
}
```

---

## How It Works Internally

### Request Flow

```
UI (FileUploadForm) 
  → POST /api/v1/upload-and-process (ai_provider, ai_model in FormData)
    → process.py (extracts form params)
      → orchestrator.py (passes ai_provider, ai_model)
        → ai_classification_service.py
          → _get_provider_config(provider, model_override=ai_model)
          → Calls the appropriate provider method:
              _call_openai() / _call_github_copilot() / _call_anthropic() 
              / _call_google_gemini() / _call_deepseek() / _regex_fallback()
```

### Provider Configuration Resolution

1. If `ai_provider` is passed in the request, it overrides `AI_PROVIDER` from `.env`
2. If `ai_model` is passed, it overrides the default model for that provider
3. If API key is missing for the selected provider, an error is returned
4. Regex-only never requires an API key

### Adding a New Provider

1. Add config vars to `config.py` (api_key, model)
2. Add provider entry in `ai_config.py` (`PROVIDER_MODELS` dict + provider status)
3. Add call method in `ai_classification_service.py` (`_call_new_provider`)
4. Add to routing in `classify()` method
5. Update `.env.example`, `docker-compose.yml`
6. Add to `types/index.ts` AIProvider enum
