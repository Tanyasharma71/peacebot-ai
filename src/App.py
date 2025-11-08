import os
import sys
import json
from datetime import date
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from flask.cli import load_dotenv
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.logger_config import get_logger
from utils.config_loader import get, getboolean, getint
from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive

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

        if user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)
            logger.info("Generated chat reply", extra={"reply": bot_reply})

    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)

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
            return jsonify({"error": "message is required"}), 400

        logger.info("Received API message", extra={"message": message, "remote": request.remote_addr})

        if message.lower() in GRATITUDE_KEYWORDS:
            reply = log_gratitude_interactive_safe()
            return jsonify({"reply": reply, "type": "gratitude"})

        reply = responder.generate_response(message)
        logger.info("Generated API chat reply", extra={"reply": reply})
        return jsonify({"reply": reply, "type": "chat"})
    except Exception as e:
        logger.error(f"Error in api_chat: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

# ------------------------------------------
# Mood Tracker Routes
# ------------------------------------------
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

# ------------------------------------------
# Run
# ------------------------------------------
if __name__ == "__main__":
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
