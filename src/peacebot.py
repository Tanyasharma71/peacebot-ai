import os
import sys
from typing import Optional


# Ensure utils path is available for logger import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.config_loader import get 
from utils.logger_config import get_logger
from utils.retry_utils import retry
from utils.decorators import safe_execution


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------
logger = get_logger(__name__) 


class PeacebotResponder:
    logger.info(f'{"=" * 20} START LOG {"=" * 18}')
    logger.info("Peacebot initialized successfully.")
    """Generates supportive chatbot responses.

    Uses OpenAI if an API key is present, otherwise falls back to a
    lightweight, rule-based responder to ensure the app runs out of the box.
    """

    # Crisis detection markers
    CRISIS_MARKERS = [
        "suicide",
        "kill myself",
        "end my life",
        "hurt myself",
        "self harm",
        "harm myself",
    ]

    # Response templates
    CRISIS_RESPONSE = (
        "I'm really sorry you're feeling this way. You matter and you deserve support. "
        "If you're in immediate danger, please contact local emergency services now. "
        "You can also reach out to your local crisis line. If you're in the U.S., call or text 988 for the Suicide & Crisis Lifeline. "
        "If you'd like, we can take a slow breath together: inhale for 4, hold for 4, exhale for 6."
    )

    ANXIETY_RESPONSE = (
        "Anxiety can feel heavy. You're not alone. "
        "Try a 4-7-8 breath: inhale 4s, hold 7s, exhale 8s. "
        "What small, kind thing could you do for yourself in the next 10 minutes?"
    )

    SADNESS_RESPONSE = (
        "I'm with you. Those feelings are valid. "
        "If it helps, write down one worry and one thing you can control today. "
        "A brief walk or a warm drink might offer a little relief."
    )

    ANGER_RESPONSE = (
        "It makes sense to feel upset. Your feelings matter. "
        "Try a quick reset: unclench your jaw, drop your shoulders, exhale slowly. "
        "Would you like a short grounding exercise?"
    )

    DEFAULT_RESPONSE = (
        "Thank you for sharing. I'm here to listen. "
        "Could you tell me a bit more about what you're experiencing right now? "
        "If you want, we can try a brief grounding exercise together."
    )

    SYSTEM_INSTRUCTIONS = (
        "You are Peacebot, an empathetic, supportive mental-wellbeing assistant. "
        "Your style is warm, validating, and practical. Keep responses short (2-5 sentences), "
        "offer one actionable suggestion when helpful, and avoid medical diagnoses. "
        "If the user expresses intent to harm themselves or others, provide crisis resources in a gentle, non-judgmental way."
    )

    def __init__(self) -> None:
        """Initialize PeacebotResponder and detect OpenAI configuration."""
        # self._openai_api_key = get("api", "openai_key", fallback=os.getenv("OPENAI_API_KEY"))
        self._openai_api_key = get("api","openai_key",fallback=os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY"))
        self._openai_model = get("api", "openai_model", fallback="gpt-4o-mini")
        self._sdk_mode = get("api", "sdk_mode", fallback="auto")
        self._openai_available = False
        self._client = None
        self.CRISIS_MARKERS = self.CRISIS_MARKERS or []
        logger.debug("PeacebotResponder initialization started.")
        self._initialize_openai()

    @safe_execution(reraise=False)
    def _initialize_openai(self) -> None:
        """Initialize OpenAI client with fallback handling."""
        if not self._openai_api_key:
            logger.info("No OpenAI API key found. Using local responses.")
            return

        try:
            # Try newer OpenAI SDK (>=1.0)
            from openai import OpenAI
            self._client = OpenAI(api_key=self._openai_api_key)
            self._openai_available = True
            self._sdk_mode = "new"
            logger.info("OpenAI client initialized (new SDK).")
            return
        except ImportError:
            logger.debug("New OpenAI SDK not found, trying legacy version.")
        except Exception as e:
            logger.error(f"Error initializing new OpenAI SDK: {str(e)}")

        try:
            # Try legacy OpenAI SDK (<1.0)
            import openai
            openai.api_key = self._openai_api_key
            self._client = openai
            self._openai_available = True
            self._sdk_mode = "legacy"
            logger.info("OpenAI client initialized (legacy SDK).")
        except ImportError:
            logger.warning("OpenAI SDK not installed. Using local responses.")
        except Exception as e:
            logger.error(f"Error initializing legacy OpenAI SDK: {str(e)}")

    def generate_response(self, user_message: str) -> str:
        """Return a supportive response; use OpenAI if configured."""
        sanitized_message = (user_message or "").strip()
        logger.debug(f"User message received: {sanitized_message}")

        if not sanitized_message:
            logger.info("Empty message received; returning comfort prompt.")
            return "I'm here with you. Tell me what's on your mind."

        if self._openai_available and self._client is not None:
            try:
                logger.debug("Generating response via OpenAI API.")
                return self._generate_with_openai(sanitized_message)
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}. Falling back to local generation.")

        logger.debug("Using local rule-based response generation.")
        return self._generate_locally(sanitized_message)

    @safe_execution(reraise=True)
    @retry(max_retries=3, base_delay=2)
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini" if self._sdk_mode == "new" else "gpt-3.5-turbo"
        )
        truncated_prompt = (prompt[:100] + "...") if len(prompt) > 100 else prompt
        logger.debug(f"Prompt sent to OpenAI (truncated): {truncated_prompt}")

        messages = [
            {"role": "system", "content": self.SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ]

        try:
            if self._sdk_mode == "new":
                completion = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300,
                )
                response = completion.choices[0].message.content.strip()
            elif self._sdk_mode == "legacy":
                completion = self._client.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300,
                )
                response = completion["choices"][0]["message"]["content"].strip()
            else:
                logger.warning("Unknown SDK mode. Falling back to local response.")
                return self._generate_locally(prompt)

            truncated_response = (response[:100] + "...") if len(response) > 100 else response
            logger.info(f"OpenAI response generated (truncated): {truncated_response}")
            return response

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    @safe_execution(reraise=False, fallback_value="I'm here to help you.")
    def _generate_locally(self, prompt: str) -> str:
        """Generate response using rule-based keyword detection."""
        lowered = prompt.lower()
        logger.debug(f"Processing message locally: {lowered}")

        if any(marker in lowered for marker in self.CRISIS_MARKERS):
            logger.warning("Crisis marker detected in message.")
            return self.CRISIS_RESPONSE
        if any(word in lowered for word in ["anxious", "anxiety", "overwhelmed", "panic", "worried"]):
            logger.info("Anxiety-related message detected.")
            return self.ANXIETY_RESPONSE
        if any(word in lowered for word in ["sad", "down", "lonely", "depressed", "hopeless"]):
            logger.info("Sadness-related message detected.")
            return self.SADNESS_RESPONSE
        if any(word in lowered for word in ["angry", "frustrated", "irritated", "mad", "furious"]):
            logger.info("Anger-related message detected.")
            return self.ANGER_RESPONSE

        logger.info("Default response used (no keyword match).")
        return self.DEFAULT_RESPONSE

