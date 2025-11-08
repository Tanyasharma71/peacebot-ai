import os
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


class PeacebotResponder:
    """Generates supportive chatbot responses.

    Uses OpenAI if an API key is present, otherwise falls back to a
    lightweight, rule-based responder to ensure the app runs out of the box.
    """

    # Constants for crisis detection
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
        """Initialize the PeacebotResponder with OpenAI configuration if available."""
        self._openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
        self._openai_available = False
        self._client = None
        self._sdk_mode = "none"

        self._initialize_openai()

    def _initialize_openai(self) -> None:
        """Initialize OpenAI client with proper error handling."""
        if not self._openai_api_key:
            logger.info("No OpenAI API key found. Using local responses.")
            return

        # Try newer SDK style (openai>=1.0)
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=self._openai_api_key)
            self._openai_available = True
            self._sdk_mode = "new"
            logger.info("OpenAI client initialized successfully (new SDK)")
            return
        except ImportError:
            logger.debug("New OpenAI SDK not available, trying legacy SDK")
        except Exception as e:
            logger.error(f"Error initializing new OpenAI SDK: {str(e)}")

        # Try legacy SDK style (openai<1.0)
        try:
            import openai

            openai.api_key = self._openai_api_key
            self._client = openai
            self._openai_available = True
            self._sdk_mode = "legacy"
            logger.info("OpenAI client initialized successfully (legacy SDK)")
        except ImportError:
            logger.warning("OpenAI SDK not installed. Using local responses.")
        except Exception as e:
            logger.error(f"Error initializing legacy OpenAI SDK: {str(e)}")

    def generate_response(self, user_message: str) -> str:
        """Return a supportive response. Prefer OpenAI if configured.
        
        Args:
            user_message: The user's input message
            
        Returns:
            A supportive response string
        """
        sanitized_message = (user_message or "").strip()
        if not sanitized_message:
            return "I'm here with you. Tell me what's on your mind."

        if self._openai_available and self._client is not None:
            try:
                return self._generate_with_openai(sanitized_message)
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}. Falling back to local responses.")
                # Fall back gracefully if API errors out

        return self._generate_locally(sanitized_message)

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI API.
        
        Args:
            prompt: The user's message
            
        Returns:
            AI-generated response
            
        Raises:
            Exception: If API call fails
        """
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini" if self._sdk_mode == "new" else "gpt-3.5-turbo")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ]

        if self._sdk_mode == "new":
            # openai>=1.0 style
            completion = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )
            return (completion.choices[0].message.content or "").strip()

        if self._sdk_mode == "legacy":
            # openai<1.0 style
            completion = self._client.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )
            return (completion["choices"][0]["message"]["content"] or "").strip()

        # Should not reach here, but safe fallback
        return self._generate_locally(prompt)

    def _generate_locally(self, prompt: str) -> str:
        """Generate response using rule-based logic.
        
        Args:
            prompt: The user's message
            
        Returns:
            Rule-based response
        """
        lowered = prompt.lower()

        # Check for crisis markers first (highest priority)
        if any(marker in lowered for marker in self.CRISIS_MARKERS):
            logger.warning("Crisis marker detected in user message")
            return self.CRISIS_RESPONSE

        # Check for anxiety-related keywords
        if any(word in lowered for word in ["anxious", "anxiety", "overwhelmed", "panic", "worried"]):
            return self.ANXIETY_RESPONSE

        # Check for sadness-related keywords
        if any(word in lowered for word in ["sad", "down", "lonely", "depressed", "hopeless"]):
            return self.SADNESS_RESPONSE

        # Check for anger-related keywords
        if any(word in lowered for word in ["angry", "frustrated", "irritated", "mad", "furious"]):
            return self.ANGER_RESPONSE

        # Default supportive response
        return self.DEFAULT_RESPONSE
