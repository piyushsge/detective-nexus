import logging
import time
import re
from typing import Tuple, Optional
from google import genai
from google.genai import errors, types

from detective_nexus import config

logger = logging.getLogger(__name__)

class NexusGeminiClient:
    """
    Forensic Gemini API client abstraction for Detective Nexus.
    Enforces secret isolation, dynamic retry delays, error recovery, and clean diagnostics.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or config.GEMINI_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

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
            client = genai.Client(api_key=self.api_key)
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
            return False, "🔴 CONNECTION FAILED", f"Gemini API Error: {type(exc).__name__}: {str(exc)}"

    def generate(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> Tuple[bool, str]:
        """
        Executes query against Gemini with automatic exponential backoff for rate limits.
        Returns (success, text_or_error).
        """
        if not self.is_configured():
            return False, "GEMINI_API_KEY_NOT_CONFIGURED"

        delay = 2.0
        for attempt in range(1, max_retries + 1):
            try:
                client = genai.Client(api_key=self.api_key)
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
                    return True, response.text.strip()
                return False, "Empty response from Gemini."

            except errors.ServerError as exc:
                logger.warning("Gemini ServerError (attempt %d/%d): %s", attempt, max_retries, exc)
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    return False, f"Gemini ServerError: {str(exc)}"

            except errors.ClientError as exc:
                err_msg = str(exc)
                logger.error("Gemini ClientError (attempt %d/%d): %s", attempt, max_retries, exc)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if attempt < max_retries:
                        match = re.search(r"retry in\s+([\d\.]+)\s*s", err_msg, re.IGNORECASE)
                        wait_sec = float(match.group(1)) + 1.0 if match else (delay * 2.0)
                        logger.info("Rate limit hit. Pausing %.1fs before retry...", wait_sec)
                        time.sleep(wait_sec)
                        delay *= 2.0
                        continue
                return False, f"Gemini ClientError: {str(exc)}"

            except Exception as exc:
                logger.error("Unexpected error in Gemini client: %s", type(exc).__name__)
                return False, f"Gemini Error ({type(exc).__name__}): {str(exc)}"

        return False, "Exceeded maximum retry attempts connecting to Gemini."

# Singleton instance
_client_instance: Optional[NexusGeminiClient] = None

def get_client() -> NexusGeminiClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = NexusGeminiClient()
    return _client_instance
