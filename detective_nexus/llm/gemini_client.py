import logging
import time
import re
import hashlib
import threading
from typing import Tuple, Optional, Dict
from google import genai
from google.genai import errors, types

from detective_nexus import config

logger = logging.getLogger(__name__)

# High-performance in-memory cache for LLM responses
_CACHE_LOCK = threading.Lock()
_CACHE: Dict[str, Tuple[float, str]] = {}
CACHE_TTL = 900  # 15 minutes
MAX_CACHE_SIZE = 256

class NexusGeminiClient:
    """
    Forensic Gemini API client abstraction for Detective Nexus.
    Optimized for high-speed throughput with:
    - Connection pooling (persistent genai.Client session)
    - In-memory response caching (SHA-256 keyed)
    - Low-latency backoff retries
    - Clean diagnostics and error recovery
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or config.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        self._cached_api_key: Optional[str] = None

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def _get_genai_client(self) -> genai.Client:
        """Returns reusable singleton genai.Client to maintain HTTP keep-alive connection pools."""
        if self._client is None or self._cached_api_key != self.api_key:
            self._client = genai.Client(api_key=self.api_key)
            self._cached_api_key = self.api_key
        return self._client

    def test_connection(self) -> Tuple[bool, str, str]:
        """
        Sends an operational diagnostic ping to Google Gemini.
        Returns (success, badge, message).
        """
        if not self.is_configured():
            return False, "🟠 GEMINI_API_KEY NOT CONFIGURED", (
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.\n"
                "System will operate in high-fidelity forensic demo mode."
            )

        try:
            client = self._get_genai_client()
            test_prompt = "Reply with exactly: DETECTIVE NEXUS ONLINE"
            response = client.models.generate_content(
                model=self.model,
                contents=test_prompt
            )
            if response and response.text:
                return True, "🟢 GEMINI FORENSIC ENGINE ONLINE", (
                    f"Connection verified.\n"
                    f"Model: {self.model}\n"
                    f"Response: {response.text.strip()}"
                )
            return False, "🔴 EMPTY RESPONSE", f"No response text received from {self.model}."
        except Exception as exc:
            # Invalidate cached client in case of auth/connection stale state
            self._client = None
            return False, "🔴 CONNECTION FAILED", f"Gemini API Error: {type(exc).__name__}: {str(exc)}"

    def generate(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> Tuple[bool, str]:
        """
        Executes query against Gemini with connection pooling and in-memory caching.
        Returns (success, text_or_error).
        """
        if not self.is_configured():
            return False, "GEMINI_API_KEY_NOT_CONFIGURED"

        # 1. Check in-memory response cache
        cache_key = hashlib.sha256(
            f"{self.model}:{temperature}:{system_instruction[:500]}:{user_prompt}".encode("utf-8")
        ).hexdigest()

        with _CACHE_LOCK:
            if cache_key in _CACHE:
                cached_time, cached_val = _CACHE[cache_key]
                if time.time() - cached_time < CACHE_TTL:
                    logger.debug("Fast-cache hit for Gemini prompt (%s)", cache_key[:8])
                    return True, cached_val

        delay = 0.75  # Low latency backoff start
        for attempt in range(1, max_retries + 1):
            try:
                client = self._get_genai_client()
                gen_config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature
                )
                response = client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config=gen_config
                )
                if response and response.text:
                    cleaned_text = response.text.strip()
                    # Store in fast cache
                    with _CACHE_LOCK:
                        if len(_CACHE) >= MAX_CACHE_SIZE:
                            # Prune oldest 25% entries
                            sorted_keys = sorted(_CACHE.keys(), key=lambda k: _CACHE[k][0])
                            for k in sorted_keys[:MAX_CACHE_SIZE // 4]:
                                _CACHE.pop(k, None)
                        _CACHE[cache_key] = (time.time(), cleaned_text)
                    return True, cleaned_text

                return False, "Empty response from Gemini."

            except errors.ServerError as exc:
                logger.warning("Gemini ServerError (attempt %d/%d): %s", attempt, max_retries, exc)
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 1.8
                else:
                    return False, f"Gemini ServerError: {str(exc)}"

            except errors.ClientError as exc:
                err_msg = str(exc)
                logger.error("Gemini ClientError (attempt %d/%d): %s", attempt, max_retries, exc)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if attempt < max_retries:
                        match = re.search(r"retry in\s+([\d\.]+)\s*s", err_msg, re.IGNORECASE)
                        wait_sec = float(match.group(1)) + 0.5 if match else (delay * 1.5)
                        logger.info("Rate limit hit. Pausing %.1fs before retry...", wait_sec)
                        time.sleep(wait_sec)
                        delay *= 1.8
                        continue
                return False, f"Gemini ClientError: {str(exc)}"

            except Exception as exc:
                logger.error("Unexpected error in Gemini client: %s", type(exc).__name__)
                self._client = None  # Reset client connection on unexpected socket error
                return False, f"Gemini Error ({type(exc).__name__}): {str(exc)}"

        return False, "Exceeded maximum retry attempts connecting to Gemini."

# Singleton instance
_client_instance: Optional[NexusGeminiClient] = None

def get_client() -> NexusGeminiClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = NexusGeminiClient()
    return _client_instance
