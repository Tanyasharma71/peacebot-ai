import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__))) 
from utils.logger_config import get_logger
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from flask.cli import load_dotenv
from dotenv import load_dotenv
from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive

# Configure logging
logger = get_logger(__name__)

load_dotenv()

app = Flask(__name__)
responder = PeacebotResponder()

# Constants
import os
debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "static",
    "Index.html"
)

print(TEMPLATE_PATH)

GRATITUDE_KEYWORDS = {"gratitude", "thanks", "thank you"}

# Read template file once and serve via render_template_string for simplicity
try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        INDEX_TEMPLATE = f.read()
    logger.info("Loaded index template successfully", extra={"template_path": TEMPLATE_PATH})        
except FileNotFoundError:
    logger.error("Template file not found", extra={"template_path": TEMPLATE_PATH})
    INDEX_TEMPLATE = "<html><body><h1>Template not found</h1></body></html>"


@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for web interface."""
    user_message = None
    bot_reply = None

    if request.method == "POST":
        # Support two modes: chat message or quick gratitude log trigger
        user_message = (request.form.get("message") or "").strip()
        logger.info(
            "Received message from web form",
            extra={"remote_addr": request.remote_addr, "message": user_message}
        )
        if user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:            
            bot_reply = responder.generate_response(user_message)
            logger.info(
                "Generated chat reply",
                extra={"reply": bot_reply}
            )

    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)


@app.get("/static/<path:filename>")
def static_assets(filename: str):
    """Serve static assets."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        logger.warning("Static directory not found", extra={"static_dir": static_dir})
        return jsonify({"error": "Static directory not found"}), 404
    return send_from_directory(static_dir, filename)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for chat interactions."""
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        
        if not message:
            logger.warning("Empty message received in API", extra={"remote_addr": request.remote_addr})
            return jsonify({"error": "message is required"}), 400

        logger.info(
            "Received API chat message",
            extra={"remote_addr": request.remote_addr, "message": message}
        )

        if message.lower() in GRATITUDE_KEYWORDS:
            reply = log_gratitude_interactive_safe()
            return jsonify({"reply": reply, "type": "gratitude"})

        reply = responder.generate_response(message)
        logger.info(
            "Generated API chat reply",
            extra={"reply": reply}
        )        
        return jsonify({"reply": reply, "type": "chat"})
    
    except Exception as e:
        logger.error(f"Error in api_chat: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500


def log_gratitude_interactive_safe() -> str:
    """Provide a non-blocking message for web context and persist a placeholder.

    The original log_gratitude function is interactive (CLI input). For web usage,
    we store a placeholder entry and guide the user. This keeps the flow non-blocking.
    """
    try:
        # Create placeholder gratitude entries
        placeholder_items = [
            "Something I'm grateful for today",
            "A person who made me smile",
            "A moment of peace I experienced"
        ]
        
        result = log_gratitude_noninteractive(placeholder_items)
        logger.info(
            "Saved gratitude placeholder",
            extra={"gratitude_items": placeholder_items}
        )        
        logger.info("Gratitude placeholder saved successfully")
        
        return (
            "Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
            "If you want to save them, use the CLI tool later or add a web form here."
        )
    except Exception as e:
        logger.error(f"Error saving gratitude placeholder: {str(e)}")
        return (
            "Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
            "I couldn't save them right now, but reflecting is still powerful."
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning("404 Not Found", extra={"path": request.path, "remote_addr": request.remote_addr})
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    logger.info("=" * 80)
    logger.info("Peacebot server starting", extra={"port": port, "debug": debug})
    logger.info("=" * 80)

    try:
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        logger.warning("Peacebot server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Peacebot server crashed: {e}")
    finally:
        logger.info("=" * 80)
        logger.info("Peacebot server closed")
        logger.info("=" * 80)

