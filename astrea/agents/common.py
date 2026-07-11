"""Shared agent initialisation helpers.

Every per-agent module imports from here so settings are resolved once and the
LLM/tooling setup is consistent across agents.
"""
import asyncio
import logging
import os
from typing import Any, AsyncGenerator

import litellm
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

from astrea.config import get_settings
from astrea.hitl.handler import ConsoleHITLHandler, DelegatingHITLHandler

settings = get_settings()

_logger = logging.getLogger(__name__)

# Transient upstream failures (provider hiccups, rate limits, 5xx) that are worth
# retrying. OpenRouter wraps a flaky underlying provider as a BadRequestError with
# "Provider returned error", which litellm's own num_retries does NOT retry — so
# we retry around the whole model call ourselves.
_RETRYABLE_SUBSTRINGS = (
    "provider returned error",
    "rate limit",
    "ratelimit",
    "overloaded",
    "service unavailable",
    "temporarily unavailable",
    "timeout",
    "timed out",
    "502",
    "503",
    "504",
    "529",
)
_RETRYABLE_TYPES = (
    "RateLimitError",
    "Timeout",
    "APIConnectionError",
    "ServiceUnavailableError",
    "InternalServerError",
    "APIError",
)
_LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))


def _is_transient(err: Exception) -> bool:
    if type(err).__name__ in _RETRYABLE_TYPES:
        return True
    msg = str(err).lower()
    return any(s in msg for s in _RETRYABLE_SUBSTRINGS)


class RetryingLiteLlm(LiteLlm):
    """LiteLlm that retries the whole call on transient upstream errors.

    Only retries when nothing has been yielded yet (so a partial stream is never
    duplicated) and only for transient errors; everything else propagates.
    """

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        attempt = 0
        while True:
            yielded = False
            try:
                async for resp in super().generate_content_async(llm_request, stream=stream):
                    yielded = True
                    yield resp
                return
            except Exception as err:  # noqa: BLE001 — classify then re-raise
                attempt += 1
                if yielded or attempt > _LLM_MAX_RETRIES or not _is_transient(err):
                    raise
                delay = min(1.5 ** attempt, 8.0)
                _logger.warning(
                    "Transient LLM error (attempt %d/%d), retrying in %.1fs: %s",
                    attempt, _LLM_MAX_RETRIES, delay, err,
                )
                await asyncio.sleep(delay)

MODEL = settings.llm.main_model or "openai/gpt-4o-mini"
litellm.api_key = settings.llm.openai_api_key
# Silence litellm's "Provider List: https://docs.litellm.ai/docs/providers" spam.
# It fires when litellm can't map a model prefix (e.g. "qwen/...") to a known
# provider during cost/token bookkeeping — harmless, but it floods the console.
litellm.suppress_debug_info = True

# Litellm's per-provider clients read a provider-specific env var (e.g.
# DEEPSEEK_API_KEY) — they do NOT fall back to the global `litellm.api_key` set
# above. The project keeps a single key in LLM__OPENAI_API_KEY, so mirror it
# into whichever provider env var the configured model prefix actually uses.
# This saves operators from duplicating the same key under multiple names in
# .env. Never overrides a variable that was set explicitly (e.g. in the shell).
_PROVIDER_KEY_ENV = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "azure": "AZURE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "together_ai": "TOGETHERAI_API_KEY",
}


def _mirror_provider_key(model: str, key: str | None) -> None:
    prov = model.split("/", 1)[0] if "/" in model else None
    env_var = _PROVIDER_KEY_ENV.get(prov) if prov else None
    if env_var and key and not os.environ.get(env_var):
        os.environ[env_var] = key


_mirror_provider_key(MODEL, settings.llm.openai_api_key)

hitl_enabled = settings.hitl.enabled
hitl_handler = DelegatingHITLHandler(ConsoleHITLHandler()) if hitl_enabled else None

# The CoderAgent runs on a dedicated (stronger) model — its multi-step tool-use
# benefits from more capability. Falls back to the main model when unset.
#
# Routing mirrors the other agents exactly: the provider prefix in the model
# string (e.g. "openrouter/qwen/...") selects the provider/base-URL, and the
# global `litellm.api_key` (set above) carries the key. We deliberately do NOT
# pass `api_base` here — doing so makes litellm strip the provider prefix, fail
# to re-infer the provider, and spam "Provider List: ..." warnings.
CODER_MODEL = settings.llm.coder_model or MODEL
_mirror_provider_key(CODER_MODEL, settings.llm.openai_api_key)


def make_llm(model: str = MODEL) -> LiteLlm:
    """Return a (retry-wrapped) LiteLlm for the main model (or an override)."""
    return RetryingLiteLlm(model=model)


def make_coder_llm() -> LiteLlm:
    """Return a (retry-wrapped) LiteLlm for the dedicated coder model."""
    return RetryingLiteLlm(model=CODER_MODEL)
