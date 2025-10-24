import os
from typing import Optional


class PeacebotResponder:
    """Generates supportive chatbot responses.

    Uses OpenAI if an API key is present, otherwise falls back to a
    lightweight, rule-based responder to ensure the app runs out of the box.
    """

    def __init__(self) -> None:
        self._openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
        self._openai_available = False

        # Lazy import to avoid hard dependency when running without OpenAI
        try:
            # Newer SDK style (openai>=1.0)
            from openai import OpenAI  # type: ignore

            self._client = OpenAI(api_key=self._openai_api_key)
            self._openai_available = bool(self._openai_api_key)
            self._sdk_mode = "new"
        except Exception:
            try:
                # Legacy SDK style (openai<1.0)
                import openai  # type: ignore

                openai.api_key = self._openai_api_key
                self._client = openai
                self._openai_available = bool(self._openai_api_key)
                self._sdk_mode = "legacy"
            except Exception:
                self._client = None
                self._sdk_mode = "none"

    def generate_response(self, user_message: str) -> str:
        """Return a supportive response. Prefer OpenAI if configured."""
        sanitized_message = (user_message or "").strip()
        if not sanitized_message:
            return "I'm here with you. Tell me what's on your mind."

        if self._openai_available and self._client is not None:
            try:
                return self._generate_with_openai(sanitized_message)
            except Exception:
                # Fall back gracefully if API errors out
                pass

        return self._generate_locally(sanitized_message)

    def _generate_with_openai(self, prompt: str) -> str:
        system_instructions = (
            "You are Peacebot, an empathetic, supportive mental-wellbeing assistant. "
            "Your style is warm, validating, and practical. Keep responses short (2-5 sentences), "
            "offer one actionable suggestion when helpful, and avoid medical diagnoses. "
            "If the user expresses intent to harm themselves or others, provide crisis resources in a gentle, non-judgmental way."
        )

        if self._sdk_mode == "new":
            # openai>=1.0 style
            completion = self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return (completion.choices[0].message.content or "").strip()

        if self._sdk_mode == "legacy":
            # openai<1.0 style
            completion = self._client.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return (completion["choices"][0]["message"]["content"] or "").strip()

        # Should not reach here, but safe fallback
        return self._generate_locally(prompt)

    def _generate_locally(self, prompt: str) -> str:
        lowered = prompt.lower()

        crisis_markers = [
            "suicide",
            "kill myself",
            "end my life",
            "hurt myself",
            "self harm",
            "harm myself",
        ]

        if any(marker in lowered for marker in crisis_markers):
            return (
                "I'm really sorry you're feeling this way. You matter and you deserve support. "
                "If you're in immediate danger, please contact local emergency services now. "
                "You can also reach out to your local crisis line. If you're in the U.S., call or text 988 for the Suicide & Crisis Lifeline. "
                "If you'd like, we can take a slow breath together: inhale for 4, hold for 4, exhale for 6."
            )

        if any(word in lowered for word in ["anxious", "anxiety", "overwhelmed", "panic"]):
            return (
                "Anxiety can feel heavy. You're not alone. "
                "Try a 4-7-8 breath: inhale 4s, hold 7s, exhale 8s. "
                "What small, kind thing could you do for yourself in the next 10 minutes?"
            )

        if any(word in lowered for word in ["sad", "down", "lonely", "depressed"]):
            return (
                "I'm with you. Those feelings are valid. "
                "If it helps, write down one worry and one thing you can control today. "
                "A brief walk or a warm drink might offer a little relief."
            )

        if any(word in lowered for word in ["angry", "frustrated", "irritated", "mad"]):
            return (
                "It makes sense to feel upset. Your feelings matter. "
                "Try a quick reset: unclench your jaw, drop your shoulders, exhale slowly. "
                "Would you like a short grounding exercise?"
            )

        return (
            "Thank you for sharing. I'm here to listen. "
            "Could you tell me a bit more about what you're experiencing right now? "
            "If you want, we can try a brief grounding exercise together."
        )


