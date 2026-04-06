"""AI-powered document classification and structured data extraction."""

import json
import logging
import re
from typing import Any

from app.config import settings
from app.models.enums import DocumentType

logger = logging.getLogger(__name__)

# Wealth management statement prompt — detailed field extraction
WEALTH_STATEMENT_PROMPT = """You are a financial document parser specializing in Wealth Management account statements.
Extract ALL structured data from this Wealth Services Account Statement.

Return a JSON object with these EXACT fields (use null if not found):

**Account Information:**
- account_number (string, e.g. "1002960")
- account_name (string, the client/account holder name)
- period_start (string, YYYY-MM-DD format — the FROM date of the statement period)
- period_end (string, YYYY-MM-DD format — the TO date of the statement period)
- product (string, always "wealth_management" for this type)
- branding (string, the bank/institution name e.g. "First United Bank & Trust")

**Account Summary / Financial Values:**
- starting_value (number, the Starting Value / Beginning Market Value)
- ending_value (number, the Ending Value / Ending Market Value before accruals)
- deposits_withdrawals (number, net deposits minus withdrawals)
- dividends_interest (number, total dividends and interest earned)
- change_in_value_of_investments (number, unrealized gain/loss for the period)
- total_ending_value (number, Total Ending Value INCLUDING accruals)
- total_accruals (number, total accrued income)

**Asset Composition (from the pie chart / asset allocation section):**
- cash_value (number, cash market value)
- cash_pct (number, cash percentage of portfolio)
- equity_value (number, equity/stock market value)
- equity_pct (number, equity percentage)
- fixed_income_value (number, fixed income/bond market value)
- fixed_income_pct (number, fixed income percentage)
- accruals_value (number, accruals market value)
- accruals_pct (number, accruals percentage)

**Realized Gain/Loss Summary:**
- realized_gain_loss_short_term_period (number, short-term gain/loss for the period)
- realized_gain_loss_short_term_ytd (number, short-term gain/loss year-to-date)
- realized_gain_loss_long_term_period (number, long-term gain/loss for the period)
- realized_gain_loss_long_term_ytd (number, long-term gain/loss year-to-date)

IMPORTANT:
- Parse dollar amounts by removing $ and commas, preserve negative signs
- Percentages should be numbers without % sign (e.g. 54 not "54%")
- Dates in the PDF may be MM/DD/YYYY — convert to YYYY-MM-DD
- If a value shows as "-" or blank, use 0.0

Document text:
{text}

Return ONLY valid JSON, no explanation."""


# Prompt templates per document type
PROMPT_TEMPLATES: dict[DocumentType, str] = {
    DocumentType.STATEMENT: WEALTH_STATEMENT_PROMPT,

    DocumentType.LETTER: """You are a financial document parser. Extract structured data from this LETTER.

Return a JSON object with these fields (use null if not found):
- account_number (string)
- letter_date (string, YYYY-MM-DD)
- letter_type (string)
- recipient_name (string)
- subject (string)
- key_details (object with relevant key-value pairs)

Document text:
{text}

Return ONLY valid JSON, no explanation.""",

    DocumentType.CONFIRM: """You are a financial document parser. Extract structured data from this trade/transaction CONFIRMATION.

Return a JSON object with these fields (use null if not found):
- account_number (string)
- confirm_date (string, YYYY-MM-DD)
- trade_date (string, YYYY-MM-DD)
- settlement_date (string, YYYY-MM-DD)
- confirm_type (string)
- security_name (string)
- symbol (string)
- quantity (number)
- price (number)
- net_amount (number)
- product (string)
- branding (string)

Document text:
{text}

Return ONLY valid JSON, no explanation.""",
}


class AIClassificationService:
    """Uses an LLM to classify and extract structured data from document text.

    Supports multiple AI providers: openai, github_copilot, anthropic, google_gemini, regex_only.
    The provider can be overridden per-request via the `ai_provider` parameter.
    """

    # Provider display names
    PROVIDER_NAMES = {
        "openai": "OpenAI",
        "github_copilot": "GitHub Copilot (Models API)",
        "anthropic": "Anthropic Claude",
        "google_gemini": "Google Gemini",
        "deepseek": "DeepSeek",
        "regex_only": "Regex Only (no AI)",
    }

    def _get_provider_config(self, provider: str | None = None, model_override: str | None = None) -> dict[str, Any]:
        """Return (provider_key, model_name, api_key) for the selected provider."""
        p = (provider or settings.ai_provider).lower().strip()
        configs = {
            "openai": ("openai", settings.openai_model, settings.openai_api_key),
            "github_copilot": ("github_copilot", settings.github_model, settings.github_token),
            "anthropic": ("anthropic", settings.anthropic_model, settings.anthropic_api_key),
            "google_gemini": ("google_gemini", settings.google_model, settings.google_api_key),
            "deepseek": ("deepseek", settings.deepseek_model, settings.deepseek_api_key),
            "regex_only": ("regex_only", "regex", ""),
        }
        if p not in configs:
            p = "openai"  # default
        key, model, api_key = configs[p]
        # Allow per-request model override
        if model_override and model_override.strip():
            model = model_override.strip()
        return {"provider": key, "model": model, "api_key": api_key}

    async def classify(
        self,
        extracted_text: str,
        document_type: DocumentType,
        ai_provider: str | None = None,
        ai_model: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Send extracted text to LLM for structured data extraction.

        Falls back to regex-based extraction if AI is unavailable.
        Returns (structured_data, ai_details_dict).
        """
        pcfg = self._get_provider_config(ai_provider, model_override=ai_model)
        provider = pcfg["provider"]
        model_name = pcfg["model"]
        api_key = pcfg["api_key"]

        text_chunk = extracted_text[:8000]
        prompt = PROMPT_TEMPLATES[document_type].format(text=text_chunk)

        ai_details: dict[str, Any] = {
            "model_name": model_name,
            "provider": provider,
            "provider_display": self.PROVIDER_NAMES.get(provider, provider),
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_tokens,
            "total_prompt_chars": len(prompt),
            "text_chunk_sent_chars": len(text_chunk),
            "text_chunk_max_chars": 8000,
            "prompt_template_chars": len(PROMPT_TEMPLATES[document_type]),
            "ai_request_prompt": prompt,
            "ai_response_raw": "",
            "method_used": "",
            "response_parse_success": True,
            "error_message": None,
        }

        # ── Regex-only (no AI call) ──
        if provider == "regex_only":
            result = self._regex_fallback(extracted_text, document_type)
            ai_details["method_used"] = "regex_only"
            ai_details["ai_response_raw"] = "(regex-only mode selected — no AI call)"
            return result, ai_details

        # ── Check API key ──
        if not api_key:
            logger.warning("%s API key not configured — using regex fallback", provider)
            result = self._regex_fallback(extracted_text, document_type)
            ai_details["method_used"] = "regex_fallback"
            ai_details["ai_response_raw"] = f"(no API key for {provider} — regex fallback)"
            ai_details["error_message"] = f"No API key configured for {self.PROVIDER_NAMES.get(provider, provider)}. Set the key in .env and restart."
            return result, ai_details

        # ── Call the selected AI provider ──
        try:
            if provider == "openai":
                result, raw = await self._call_openai(prompt, api_key, model_name)
            elif provider == "github_copilot":
                result, raw = await self._call_github_copilot(prompt, api_key, model_name)
            elif provider == "anthropic":
                result, raw = await self._call_anthropic(prompt, api_key, model_name)
            elif provider == "google_gemini":
                result, raw = await self._call_google_gemini(prompt, api_key, model_name)
            elif provider == "deepseek":
                result, raw = await self._call_deepseek(prompt, api_key, model_name)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            ai_details["method_used"] = f"{provider}_api"
            ai_details["ai_response_raw"] = raw
            return result, ai_details

        except Exception as e:
            error_str = str(e)
            logger.error("AI classification failed (%s): %s — falling back to regex", provider, error_str)
            result = self._regex_fallback(extracted_text, document_type)
            ai_details["method_used"] = "regex_fallback"
            ai_details["ai_response_raw"] = f"(AI failed: {error_str})"
            ai_details["response_parse_success"] = False

            # Parse known error types for clear user messaging
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                ai_details["error_message"] = f"Rate limit / quota exceeded on {self.PROVIDER_NAMES.get(provider, provider)}. Check your billing at the provider dashboard."
            elif "401" in error_str or "auth" in error_str.lower() or "invalid" in error_str.lower():
                ai_details["error_message"] = f"Authentication failed for {self.PROVIDER_NAMES.get(provider, provider)}. Check your API key."
            elif "timeout" in error_str.lower():
                ai_details["error_message"] = f"Request timed out for {self.PROVIDER_NAMES.get(provider, provider)}. Try again."
            else:
                ai_details["error_message"] = f"AI call failed: {error_str}"

            return result, ai_details

    # ── Provider implementations ─────────────────────────────────────

    async def _call_openai(self, prompt: str, api_key: str, model: str) -> tuple[dict[str, Any], str]:
        """Call OpenAI chat completion API."""
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content), content

    async def _call_github_copilot(self, prompt: str, token: str, model: str) -> tuple[dict[str, Any], str]:
        """Call GitHub Models API (OpenAI-compatible endpoint using GitHub PAT)."""
        import openai
        client = openai.AsyncOpenAI(
            api_key=token,
            base_url="https://models.inference.ai.azure.com",
        )
        response = await client.chat.completions.create(
            model=model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content), content

    async def _call_anthropic(self, prompt: str, api_key: str, model: str) -> tuple[dict[str, Any], str]:
        """Call Anthropic Claude API."""
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": settings.ai_max_tokens,
                    "temperature": settings.ai_temperature,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["content"][0]["text"]
            # Extract JSON from response (Claude may wrap in markdown)
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group()), content
            return json.loads(content), content

    async def _call_google_gemini(self, prompt: str, api_key: str, model: str) -> tuple[dict[str, Any], str]:
        """Call Google Gemini API."""
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": settings.ai_temperature,
                        "maxOutputTokens": settings.ai_max_tokens,
                        "responseMimeType": "application/json",
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(content), content

    async def _call_deepseek(self, prompt: str, api_key: str, model: str) -> tuple[dict[str, Any], str]:
        """Call DeepSeek API (OpenAI-compatible endpoint)."""
        import openai
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        response = await client.chat.completions.create(
            model=model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content), content

    # --- Full schema definitions per document type (ensures null defaults) ---
    STATEMENT_SCHEMA: dict[str, Any] = {
        "account_number": None, "account_name": None,
        "period_start": None, "period_end": None,
        "product": "wealth_management", "branding": None,
        "starting_value": None, "ending_value": None,
        "deposits_withdrawals": None, "dividends_interest": None,
        "change_in_value_of_investments": None,
        "total_ending_value": None, "total_accruals": None,
        "cash_value": None, "cash_pct": None,
        "equity_value": None, "equity_pct": None,
        "fixed_income_value": None, "fixed_income_pct": None,
        "accruals_value": None, "accruals_pct": None,
        "realized_gain_loss_short_term_period": None,
        "realized_gain_loss_short_term_ytd": None,
        "realized_gain_loss_long_term_period": None,
        "realized_gain_loss_long_term_ytd": None,
    }

    LETTER_SCHEMA: dict[str, Any] = {
        "account_number": None, "letter_date": None,
        "letter_type": None, "recipient_name": None,
        "subject": None, "key_details": None,
    }

    CONFIRM_SCHEMA: dict[str, Any] = {
        "account_number": None, "confirm_date": None,
        "trade_date": None, "settlement_date": None,
        "confirm_type": None, "security_name": None,
        "symbol": None, "quantity": None, "price": None,
        "net_amount": None, "product": None, "branding": None,
    }

    def _regex_fallback(
        self, text: str, document_type: DocumentType
    ) -> dict[str, Any]:
        """Regex extraction when AI is not available.

        Always returns the full schema for the document type, with null
        for any field that could not be matched — matching the AI output shape.
        """
        logger.info("Regex fallback: doc_type=%s, text_len=%d", document_type.value, len(text))

        if document_type == DocumentType.LETTER:
            return self._regex_letter(text)
        if document_type == DocumentType.CONFIRM:
            return self._regex_confirm(text)
        return self._regex_statement(text)

    # ── helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_dollar(raw: str) -> float | None:
        """Parse a dollar string like '-$45,617.10' into a float."""
        cleaned = raw.replace(",", "").replace("$", "").strip()
        if not cleaned or cleaned == "-":
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _find_account_number(text: str) -> str | None:
        match = re.search(r"(?:Account\s*(?:Number|#|No\.?|:)\s*)(\d{3,10})", text, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r"(\d{3})[-\s](\d{6})", text)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        return None

    @staticmethod
    def _find_dates(text: str) -> list[str]:
        """Return all dates found in the text (MM/DD/YYYY or YYYY-MM-DD)."""
        return re.findall(r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}", text)

    # ── Statement regex ─────────────────────────────────────────────

    def _regex_statement(self, text: str) -> dict[str, Any]:
        result = dict(self.STATEMENT_SCHEMA)  # start with full null schema

        result["account_number"] = self._find_account_number(text)

        # Dates
        dates = self._find_dates(text)
        if len(dates) >= 2:
            result["period_start"] = dates[0]
            result["period_end"] = dates[1]
        elif len(dates) == 1:
            result["period_start"] = dates[0]

        # Account name
        match = re.search(r"Account\s+Name\s*:?\s*(.+)", text, re.IGNORECASE)
        if match:
            result["account_name"] = match.group(1).strip()

        # Branding
        match = re.search(
            r"^(First United Bank\s*&\s*Trust|[\w ]+Bank\s*&\s*Trust)\s*$",
            text, re.IGNORECASE | re.MULTILINE,
        )
        if match:
            result["branding"] = match.group(1).strip()

        # Financial values (handles negative values like -$45,617.10)
        for label, key in [
            (r"Starting\s+Value", "starting_value"),
            (r"Ending\s+Value", "ending_value"),
            (r"Deposits.*?Withdrawals", "deposits_withdrawals"),
            (r"Dividends.*?Interest", "dividends_interest"),
            (r"Change\s+in\s+Value", "change_in_value_of_investments"),
            (r"Total\s+Ending\s+Value", "total_ending_value"),
            (r"Total\s+Accruals", "total_accruals"),
        ]:
            match = re.search(
                rf"{label}\s*[\$:]?\s*(-?\$?-?[\d,]+\.?\d*)", text, re.IGNORECASE,
            )
            if match:
                result[key] = self._parse_dollar(match.group(1))

        # Realized gain/loss
        for label, key in [
            (r"Short\s+Term\s+Period", "realized_gain_loss_short_term_period"),
            (r"Short\s+Term\s+YTD", "realized_gain_loss_short_term_ytd"),
            (r"Long\s+Term\s+Period", "realized_gain_loss_long_term_period"),
            (r"Long\s+Term\s+YTD", "realized_gain_loss_long_term_ytd"),
        ]:
            match = re.search(
                rf"{label}\s*:?\s*(-?\$?-?[\d,]+\.?\d*)", text, re.IGNORECASE,
            )
            if match:
                result[key] = self._parse_dollar(match.group(1))

        # Asset composition
        for asset, prefix in [
            ("Cash", "cash"), ("Equity", "equity"),
            (r"Fixed\s+Income", "fixed_income"), ("Accruals", "accruals"),
        ]:
            match = re.search(
                rf"{asset}\s+\$?([\d,]+\.?\d*)\s+(\d+\.?\d*)%", text, re.IGNORECASE,
            )
            if match:
                val = self._parse_dollar(match.group(1))
                if val is not None:
                    result[f"{prefix}_value"] = val
                try:
                    result[f"{prefix}_pct"] = float(match.group(2))
                except ValueError:
                    pass

        return result

    # ── Letter regex ────────────────────────────────────────────────

    def _regex_letter(self, text: str) -> dict[str, Any]:
        result = dict(self.LETTER_SCHEMA)

        result["account_number"] = self._find_account_number(text)

        dates = self._find_dates(text)
        if dates:
            result["letter_date"] = dates[0]

        # Recipient — look for Dear <Name> or To: <Name>
        match = re.search(r"(?:Dear|To:?)\s+(.+)", text, re.IGNORECASE)
        if match:
            result["recipient_name"] = match.group(1).strip().rstrip(",")

        # Subject line
        match = re.search(r"(?:Subject|Re|RE):?\s+(.+)", text, re.IGNORECASE)
        if match:
            result["subject"] = match.group(1).strip()

        # Letter type heuristic
        text_lower = text.lower()
        if "confirmation" in text_lower:
            result["letter_type"] = "confirmation"
        elif "notice" in text_lower:
            result["letter_type"] = "notice"
        elif "welcome" in text_lower:
            result["letter_type"] = "welcome"
        elif "closing" in text_lower or "termination" in text_lower:
            result["letter_type"] = "closing"
        else:
            result["letter_type"] = "general"

        return result

    # ── Confirm regex ───────────────────────────────────────────────

    def _regex_confirm(self, text: str) -> dict[str, Any]:
        result = dict(self.CONFIRM_SCHEMA)

        result["account_number"] = self._find_account_number(text)

        dates = self._find_dates(text)
        if len(dates) >= 3:
            result["confirm_date"] = dates[0]
            result["trade_date"] = dates[1]
            result["settlement_date"] = dates[2]
        elif len(dates) == 2:
            result["trade_date"] = dates[0]
            result["settlement_date"] = dates[1]
        elif len(dates) == 1:
            result["trade_date"] = dates[0]

        # Security name — look for patterns like "BOUGHT 100 SHARES OF APPLE INC"
        match = re.search(
            r"(?:BOUGHT|SOLD|BUY|SELL)\s+[\d,.]+\s+(?:SHARES?\s+(?:OF\s+)?)?(.+?)(?:\s+at|\s+@|\s*$)",
            text, re.IGNORECASE,
        )
        if match:
            result["security_name"] = match.group(1).strip()

        # Symbol — ticker-like uppercase 1-5 chars
        match = re.search(r"\b([A-Z]{1,5})\b.*?(?:symbol|ticker)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"(?:symbol|ticker)\s*:?\s*([A-Z]{1,5})\b", text, re.IGNORECASE)
        if match:
            result["symbol"] = match.group(1)

        # Quantity
        match = re.search(r"(?:Quantity|Shares|Qty)\s*:?\s*([\d,.]+)", text, re.IGNORECASE)
        if match:
            result["quantity"] = self._parse_dollar(match.group(1))

        # Price
        match = re.search(r"(?:Price|at|@)\s*:?\s*\$?([\d,.]+)", text, re.IGNORECASE)
        if match:
            result["price"] = self._parse_dollar(match.group(1))

        # Net amount
        match = re.search(r"(?:Net\s+Amount|Total|Amount\s+Due)\s*:?\s*\$?([\d,.]+)", text, re.IGNORECASE)
        if match:
            result["net_amount"] = self._parse_dollar(match.group(1))

        # Confirm type heuristic
        text_lower = text.lower()
        if "buy" in text_lower or "bought" in text_lower or "purchase" in text_lower:
            result["confirm_type"] = "buy"
        elif "sell" in text_lower or "sold" in text_lower:
            result["confirm_type"] = "sell"
        elif "dividend" in text_lower:
            result["confirm_type"] = "dividend"
        elif "transfer" in text_lower:
            result["confirm_type"] = "transfer"

        # Branding
        match = re.search(
            r"^(First United Bank\s*&\s*Trust|[\w ]+Bank\s*&\s*Trust)\s*$",
            text, re.IGNORECASE | re.MULTILINE,
        )
        if match:
            result["branding"] = match.group(1).strip()

        return result
