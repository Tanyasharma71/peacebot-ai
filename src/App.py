import os
import sys
import json

from datetime import date, datetime, UTC
from flask import Flask, render_template_string, request, jsonify, send_from_directory, make_response
from flask.cli import load_dotenv
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.logger_config import get_logger
from utils.config_loader import get, getboolean, getint
from utils.request_id_context import set_request_id, clear_request_id
from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive
# shutdown logging
import atexit
import time

# ------------------------------------------
# Logging + Config
# ------------------------------------------
logger = get_logger(__name__)
load_dotenv()

app = Flask(__name__)
responder = PeacebotResponder()

debug = getboolean("flask", "debug", fallback=True)
port = getint("flask", "port", fallback=5000)

# ------------------------------------------
# Paths and Files
# ------------------------------------------
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

MOOD_FILE = os.path.join(DATA_DIR, "mood_logs.json")
GRATITUDE_FILE = os.path.join(DATA_DIR, "gratitude_log.json")

for file_path in [MOOD_FILE, GRATITUDE_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "Index.html")

GRATITUDE_KEYWORDS = {"gratitude", "thanks", "thank you"}

# ------------------------------------------
# Load template
# ------------------------------------------
try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        INDEX_TEMPLATE = f.read()
    logger.info("Loaded index template successfully", extra={"template_path": TEMPLATE_PATH})
except FileNotFoundError:
    logger.error("Template file not found", extra={"template_path": TEMPLATE_PATH})
    INDEX_TEMPLATE = "<html><body><h1>Template not found</h1></body></html>"

def _safe_end_log():
    """
    Safely log the end of execution without raising errors
    if handlers are already closed during interpreter shutdown.
    """
    try:
        # Iterate over all logger handlers
        for handler in getattr(logger, "handlers", []):
            if hasattr(handler, "stream") and handler.stream and not handler.stream.closed:
                # Log only if the stream is still open
                logger.info("=" * 20 + " END LOG " + "=" * 20)
                break
    except Exception:
        # Swallow all exceptions to prevent shutdown errors
        pass

# ------------------------------------------
# Routes
# ------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    user_message = None
    bot_reply = None

    if request.method == "POST":
        user_message = (request.form.get("message") or "").strip()
        logger.info("Received message", extra={"message": user_message, "remote": request.remote_addr})

        if not user_message:
            bot_reply = "Please enter a message so I can help you 🙂"
        elif user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)

            if not bot_reply or not bot_reply.strip():
                bot_reply = (
                    "I'm not sure I understood that. "
                    "Could you try rephrasing your question?"
                )

            logger.info("Generated chat reply", extra={"reply": bot_reply})

    return render_template_string(
        INDEX_TEMPLATE,
        user_message=user_message,
        bot_reply=bot_reply
    )

@app.route("/static/<path:filename>")
def static_assets(filename: str):
    """Serve static assets."""
    if not os.path.exists(STATIC_DIR):
        return jsonify({"error": "Static directory not found"}), 404
    return send_from_directory(STATIC_DIR, filename)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for chat."""
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()

        if not message:
            return jsonify({
                "reply": "Please enter a message before sending.",
                "type": "validation_error"
            }), 400

        logger.info("Received API message", extra={"user_message": message, "remote": request.remote_addr})

        if message.lower() in GRATITUDE_KEYWORDS:
            reply = log_gratitude_interactive_safe()
            return jsonify({"reply": reply, "type": "gratitude"})

        reply = responder.generate_response(message)

        if not reply or not reply.strip():
            reply = (
                "I'm not sure I understood that. "
                "Could you try rephrasing your question?"
            )

        logger.info("Generated API chat reply", extra={"reply": reply})
        return jsonify({"reply": reply, "type": "chat"})

    except Exception as e:
        logger.exception(f"Error in api_chat: {e}")
        return jsonify({
            "reply": "Sorry, something went wrong on my side. Please try again later.",
            "type": "server_error"
        }), 500


# ------------------------------------------
# Mood Tracker Routes
# ------------------------return js------------------
@app.route("/mood")
def mood_page():
    html = """
    <html><head><title>Mood Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
    <body style='font-family:Arial;background:#f7fafc;padding:40px'>
    <h1>🧘 Peacebot Mood Tracker</h1>
    <form id='moodForm'>
        <input type='date' id='date'><br>
        <select id='mood'>
            <option>Happy</option><option>Neutral</option>
            <option>Sad</option><option>Anxious</option><option>Angry</option>
        </select><br>
        <textarea id='note' rows='3' placeholder='Notes...'></textarea><br>
        <button>Save Mood</button>
    </form>
    <canvas id='chart' width='400' height='200'></canvas>
    <script>
    async function refresh(){
        const res=await fetch('/api/moodlog');
        const data=await res.json();
        const ctx=document.getElementById('chart');
        const labels=data.map(d=>d.date);
        const values=data.map(d=>{
            if(d.mood==='Happy')return 5;
            if(d.mood==='Neutral')return 3;
            if(d.mood==='Sad')return 2;
            if(d.mood==='Anxious')return 1;
            if(d.mood==='Angry')return 0;
            return 3;
        });
        new Chart(ctx,{type:'line',data:{labels,
        datasets:[{label:'Mood Trend',data:values,borderColor:'blue'}]}}); }
    document.getElementById('moodForm').addEventListener('submit',async e=>{
        e.preventDefault();
        await fetch('/api/moodlog',{method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            date:document.getElementById('date').value,
            mood:document.getElementById('mood').value,
            note:document.getElementById('note').value
        })});
        alert('Mood saved!');refresh();
    });
    window.onload=()=>{document.getElementById('date').valueAsDate=new Date();refresh();};
    </script></body></html>
    """
    return html

@app.route("/api/moodlog", methods=["GET"])
def get_moods():
    """Return mood logs."""
    with open(MOOD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/moodlog", methods=["POST"])
def save_mood():
    """Save a mood entry."""
    data = request.get_json(force=True)
    entry = {
        "date": data.get("date", str(date.today())),
        "mood": data.get("mood", "Neutral"),
        "note": data.get("note", "")
    }
    with open(MOOD_FILE, "r+", encoding="utf-8") as f:
        logs = json.load(f)
        logs.append(entry)
        f.seek(0)
        json.dump(logs, f, indent=2)
    return jsonify({"status": "success"}), 201

# ------------------------------------------
# Gratitude Helper
# ------------------------------------------
def log_gratitude_interactive_safe():
    try:
        placeholder_items = [
            "Something I'm grateful for today",
            "A person who made me smile",
            "A small win from today"
        ]
        log_gratitude_noninteractive(placeholder_items)
        logger.info("Saved gratitude placeholder", extra={"gratitude_items": placeholder_items})
        return "🌸 Let's take a moment to reflect — what are 3 things you're grateful for today?"
    except Exception as e:
        logger.error(f"Gratitude logging error: {e}")
        return "Couldn't save gratitude, but it's still a good time to reflect 💭"

# ------------------------------------------
# Error Handlers
# ------------------------------------------
@app.errorhandler(404)
def not_found(error):
    logger.warning("404 Not Found", extra={"path": request.path})
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


@app.route("/healthz/llm", methods=["GET"])
def health_llm():
    """
    Simple health check endpoint for Peacebot LLM pipeline.
    Returns model info, latency, and availability status.
    """
    start_time = time.time()
    status = "healthy"
    model_name = getattr(responder, "_openai_model", "local-rule-based")
    sdk_mode = getattr(responder, "_sdk_mode", "unknown")

    try:
        # Try a minimal generation to confirm model availability
        responder.generate_response("ping")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status = "unhealthy"

    latency_ms = round((time.time() - start_time) * 1000, 2)

    result = {
        "status": status,
        "latency_ms": latency_ms,
        "model": model_name,
        "sdk_mode": sdk_mode,
        # "timestamp": datetime.utcnow().isoformat() + "Z"
        "timestamp": datetime.now(UTC).isoformat()
    }

    response = make_response(jsonify(result), 200 if status == "healthy" else 503)
    response.headers["X-Model-Version"] = model_name
    response.headers["X-Latency-MS"] = str(latency_ms)
    return response


# ------------------------------------------
# Run
# ------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 49)
    logger.info("Peacebot server starting", extra={"port": port, "debug": debug})
    logger.info("=" * 49)

    try:
        set_request_id()
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        clear_request_id()
        logger.warning("Peacebot server stopped by user (Ctrl+C)")
    except Exception as e:
        clear_request_id()
        logger.error(f"Peacebot server crashed: {e}")
    finally:
        clear_request_id()
        logger.info("=" * 49)
        logger.info("Peacebot server closed")
        logger.info("=" * 49)
        # atexit.register(lambda: logger.info(f'{"=" * 10} END LOG {"=" * 10} '))

        atexit.register(_safe_end_log)