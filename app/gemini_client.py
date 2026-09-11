"""
Gemini Client Module for AI Mystery Detective Team.

Responsibilities:
- Isolate all communication with Google Gemini API using the official google-genai SDK.
- Create the client securely using the API key loaded from environment configuration.
- Execute real test queries to verify connectivity.
- Return user-friendly status and diagnostic responses without exposing secrets.
"""

import sys
import logging
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from google import genai
from google.genai import errors, types

# Configure safe local logging
logger = logging.getLogger(__name__)


def generate_content(system_instruction: str, user_prompt: str) -> tuple[bool, str]:
    """
    Sends a structured prompt to the Gemini model with system instructions.

    Args:
        system_instruction (str): The role, rules, and constraints for the model.
        user_prompt (str): The contextual case data and task instructions.

    Returns:
        tuple[bool, str]: (success, text_response_or_error_message)
        Never exposes the API key or secret tokens.
    """
    is_valid, config_message = config.validate_config()
    if not is_valid:
        return False, f"Configuration Error: {config_message}"

    import time
    import re

    max_retries = 4
    delay = 3.0

    for attempt in range(1, max_retries + 1):
        try:
            client = genai.Client(api_key=config.GEMINI_API_KEY)
            gen_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=user_prompt,
                config=gen_config
            )

            if response and response.text:
                return True, response.text.strip()
            else:
                return False, f"Received empty response from Gemini model '{config.GEMINI_MODEL}'."

        except errors.ServerError as exc:
            logger.warning("Gemini ServerError on attempt %d/%d: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
            else:
                return False, f"Gemini API ServerError (Demand Spike): {exc.message if hasattr(exc, 'message') else str(exc)}"
        except errors.ClientError as exc:
            error_str = str(exc)
            logger.error("Gemini API ClientError on attempt %d/%d: %s", attempt, max_retries, exc)
            # Handle rate-limiting (429 Resource Exhausted) with dynamic wait
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries:
                    # Try to extract retry delay from error message (e.g. 'retry in 10.5s')
                    match = re.search(r"retry in\s+([\d\.]+)\s*s", error_str, re.IGNORECASE)
                    wait_time = float(match.group(1)) + 1.0 if match else (delay * 2.0)
                    logger.info("429 Rate limit encountered. Waiting %.1f seconds before retry...", wait_time)
                    time.sleep(wait_time)
                    delay *= 2.0
                    continue
            return False, f"Gemini API ClientError: {exc.message if hasattr(exc, 'message') else str(exc)}"
        except errors.APIError as exc:
            logger.error("Gemini APIError: %s", exc)
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
            else:
                return False, f"Gemini API communication failure: {exc.message if hasattr(exc, 'message') else str(exc)}"
        except Exception as exc:
            logger.error("Unexpected error querying Gemini: %s", type(exc).__name__)
            return False, f"Unexpected Gemini error: {type(exc).__name__}: {str(exc)}"

    return False, "Failed to connect to Gemini after multiple retry attempts."



def test_gemini_connection() -> tuple[str, str]:
    """
    Tests live connectivity to the Gemini API using the configured model and key.

    Returns:
        tuple[str, str]: (status_badge, diagnostic_message)
        - status_badge: formatted status string (e.g. 🟢, 🔴, 🟠)
        - diagnostic_message: safe message detailing the result or instructions
    """
    # 1. Validate environment configuration
    is_valid, config_message = config.validate_config()
    if not is_valid:
        return "🟠 GEMINI_API_KEY is missing", (
            f"Configuration Issue:\n{config_message}\n\n"
            "Please create or update your .env file with a valid Gemini API key:\n"
            "GEMINI_API_KEY=your_actual_key_here\n"
            "GEMINI_MODEL=gemini-3.8-flash"
        )

    # 2. Initialize the official Gemini client
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as exc:
        logger.error("Failed to instantiate Gemini client: %s", type(exc).__name__)
        return (
            "🔴 Gemini connection failed",
            f"Failed to initialize Gemini client.\nDetails: {type(exc).__name__}: {str(exc)}"
        )

    # 3. Send a REAL test prompt to Gemini
    test_prompt = "Reply with exactly: GEMINI CONNECTION OK"
    model_name = config.GEMINI_MODEL

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=test_prompt
        )

        if response and response.text:
            cleaned_response = response.text.strip()
            diagnostic = (
                f"Gemini response:\n{cleaned_response}\n\n"
                f"Active Model: {model_name}\n"
                f"Connection: Active & Verified"
            )
            return "🟢 Gemini connection successful", diagnostic
        else:
            return (
                "🔴 Gemini connection failed",
                f"Received empty response from model '{model_name}'."
            )

    except errors.ClientError as exc:
        logger.error("Gemini API ClientError: %s", exc)
        return (
            "🔴 Gemini connection failed",
            (
                "Gemini API Error (Client Error):\n"
                "Please verify that your GEMINI_API_KEY is valid and has access to "
                f"model '{model_name}'.\n"
                f"Message: {exc.message if hasattr(exc, 'message') else str(exc)}"
            )
        )
    except errors.ServerError as exc:
        logger.error("Gemini API ServerError: %s", exc)
        return (
            "🔴 Gemini connection failed",
            (
                "Google Gemini service temporary issue (Server Error).\n"
                "Please try again in a few moments.\n"
                f"Message: {exc.message if hasattr(exc, 'message') else str(exc)}"
            )
        )
    except errors.APIError as exc:
        logger.error("Gemini APIError: %s", exc)
        return (
            "🔴 Gemini connection failed",
            (
                "Gemini API communication failure.\n"
                f"Message: {exc.message if hasattr(exc, 'message') else str(exc)}"
            )
        )
    except Exception as exc:
        logger.error("Unexpected error connecting to Gemini: %s", type(exc).__name__)
        return (
            "🔴 Gemini connection failed",
            (
                "Gemini connection failed. Please verify your GEMINI_API_KEY and internet connection.\n"
                f"Error: {type(exc).__name__}"
            )
        )
