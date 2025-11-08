class PeacebotResponder:
    """Simple AI responder for emotional support."""

    def generate_response(self, message: str) -> str:
        msg = message.lower()
        if "stress" in msg:
            return "Take a deep breath 🌿. Maybe listen to calm music."
        elif "sad" in msg:
            return "I'm here for you 💙. Think of one thing that made you smile today."
        elif "happy" in msg:
            return "That’s amazing! Keep sharing your positivity ✨"
        elif "lonely" in msg:
            return "You’re never alone 🌻. Would you like a motivational quote?"
        else:
            return "Tell me more about how you’re feeling 💬"
