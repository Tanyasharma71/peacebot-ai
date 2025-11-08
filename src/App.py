import os
import json
import logging
from datetime import date
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from dotenv import load_dotenv

from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive

# -------------------------------------------------
# Logging Configuration
# -------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)
responder = PeacebotResponder()

# -------------------------------------------------
# Paths (for static-based structure)
# -------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

INDEX_HTML = os.path.join(STATIC_DIR, "Index.html")
MOOD_FILE = os.path.join(DATA_DIR, "mood_logs.json")
GRATITUDE_FILE = os.path.join(DATA_DIR, "gratitude_log.json")

# Initialize JSON data files
for file_path in [MOOD_FILE, GRATITUDE_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

GRATITUDE_KEYWORDS = {"gratitude", "thanks", "thank you"}

# -------------------------------------------------
# Load Index Template
# -------------------------------------------------
try:
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        INDEX_TEMPLATE = f.read()
except FileNotFoundError:
    INDEX_TEMPLATE = "<h1>Peacebot-AI</h1><p>Index.html not found</p>"

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    """Main chat interface."""
    user_message, bot_reply = None, None
    if request.method == "POST":
        user_message = (request.form.get("message") or "").strip()
        if user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)
    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (like logo.svg)."""
    return send_from_directory(STATIC_DIR, filename)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for chat messages."""
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message required"}), 400

    if message.lower() in GRATITUDE_KEYWORDS:
        reply = log_gratitude_interactive_safe()
        return jsonify({"reply": reply, "type": "gratitude"})

    reply = responder.generate_response(message)
    return jsonify({"reply": reply, "type": "chat"})


# -------------------------------------------------
# Mood Tracker Routes
# -------------------------------------------------
@app.route("/mood")
def mood_page():
    """Web interface for mood tracking."""
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
        datasets:[{label:'Mood Trend',data:values,borderColor:'blue'}]}});
    }
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
    """Return saved moods."""
    with open(MOOD_FILE) as f:
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
    with open(MOOD_FILE, "r+") as f:
        logs = json.load(f)
        logs.append(entry)
        f.seek(0)
        json.dump(logs, f, indent=2)
    return jsonify({"status": "success"}), 201


# -------------------------------------------------
# Gratitude Helper
# -------------------------------------------------
def log_gratitude_interactive_safe():
    """Non-blocking gratitude log."""
    try:
        items = [
            "Something I'm grateful for",
            "A person who made me smile",
            "A small win from today"
        ]
        log_gratitude_noninteractive(items)
        return "🌸 Let's take a moment to reflect — what are 3 things you're grateful for today?"
    except Exception as e:
        logger.error(f"Gratitude logging error: {e}")
        return "Couldn't save gratitude, but it's still a good time to reflect 💭"

# -------------------------------------------------
# Run App
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
