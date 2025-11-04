import os
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from dotenv import load_dotenv

from peacebot import PeacebotResponder
from Gratitude import log_gratitude


load_dotenv()

app = Flask(__name__)
responder = PeacebotResponder()


# Read template file once and serve via render_template_string for simplicity
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "Index.html")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()


@app.route("/", methods=["GET", "POST"])
def index():
    user_message = None
    bot_reply = None

    if request.method == "POST":
        # Support two modes: chat message or quick gratitude log trigger
        user_message = (request.form.get("message") or "").strip()
        if user_message.lower() in {"gratitude", "thanks", "thank you"}:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)

    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)


@app.get("/static/<path:filename>")
def static_assets(filename: str):
    return send_from_directory(os.path.join(os.path.dirname(__file__), "static"), filename)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    if message.lower() in {"gratitude", "thanks", "thank you"}:
        reply = log_gratitude_interactive_safe()
        return jsonify({"reply": reply})

    reply = responder.generate_response(message)
    return jsonify({"reply": reply})


def log_gratitude_interactive_safe() -> str:
    """Provide a non-blocking message for web context and persist a placeholder.

    The original log_gratitude function is interactive (CLI input). For web usage,
    we store a placeholder entry and guide the user. This keeps the flow non-blocking.
    """
    try:
        # Minimal placeholder entry
        _ = log_gratitude_placeholder()
        return (
            "Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
            "If you want to save them, use the CLI tool later or add a web form here."
        )
    except Exception:
        return (
            "Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
            "I couldn't save them right now, but reflecting is still powerful."
        )


def log_gratitude_placeholder() -> str:
    # Reuse Gratitude.py data file naming
    data_file = os.path.join(os.path.dirname(__file__), "gratitude_log.json")
    try:
        import json
        import datetime

        entry = {
            "timestamp": str(datetime.datetime.now()),
            "gratitude": [
                "placeholder_1",
                "placeholder_2",
                "placeholder_3",
            ],
            "source": "web",
        }
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        data.append(entry)
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return "saved"
    except Exception:
        return "error"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)


