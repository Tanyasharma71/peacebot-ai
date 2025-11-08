import os
import json
import logging
from datetime import date
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from dotenv import load_dotenv

from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment setup
load_dotenv()
app = Flask(__name__)
responder = PeacebotResponder()

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # go up from src/peacebot/
TEMPLATE_PATH = os.path.join(BASE_DIR, "static", "Index.html")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
MOOD_FILE = os.path.join(DATA_DIR, "mood_logs.json")
if not os.path.exists(MOOD_FILE):
    with open(MOOD_FILE, "w") as f:
        json.dump([], f)

GRATITUDE_KEYWORDS = {"gratitude", "thanks", "thank you"}

# Load main page template
try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        INDEX_TEMPLATE = f.read()
except FileNotFoundError:
    logger.error(f"Template not found at {TEMPLATE_PATH}")
    INDEX_TEMPLATE = "<h1>Peacebot-AI</h1><p>Index.html missing</p>"

# ----------------------------------------------------------------
# 💬 Peacebot Chat Route
# ----------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    user_message = None
    bot_reply = None
    if request.method == "POST":
        user_message = (request.form.get("message") or "").strip()
        if user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)
    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        if not message:
            return jsonify({"error": "message is required"}), 400

        if message.lower() in GRATITUDE_KEYWORDS:
            reply = log_gratitude_interactive_safe()
            return jsonify({"reply": reply, "type": "gratitude"})

        reply = responder.generate_response(message)
        return jsonify({"reply": reply, "type": "chat"})
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat processing failed"}), 500

# ----------------------------------------------------------------
# 🧘‍♀️ Mood Tracker Endpoints
# ----------------------------------------------------------------
@app.route("/api/moodlog", methods=["POST"])
def add_mood():
    """Add a new mood entry"""
    try:
        data = request.get_json(force=True)
        entry = {
            "date": data.get("date", str(date.today())),
            "mood": data.get("mood", "Neutral"),
            "note": data.get("note", "")
        }
        with open(MOOD_FILE, "r") as f:
            logs = json.load(f)
        logs.append(entry)
        with open(MOOD_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        return jsonify({"status": "success", "entry": entry}), 201
    except Exception as e:
        logger.error(f"Error saving mood: {e}")
        return jsonify({"error": "Could not save mood"}), 500

@app.route("/api/moodlog", methods=["GET"])
def get_moods():
    """Return all logged moods"""
    try:
        with open(MOOD_FILE, "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Error reading mood logs: {e}")
        return jsonify({"error": "Could not read mood logs"}), 500

@app.route("/mood")
def mood_page():
    """Simple embedded HTML for mood tracker"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <title>Peacebot-AI Mood Tracker</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f7fa; }
            h1 { color: #333; }
            form { background: #fff; padding: 20px; border-radius: 10px; width: 350px; margin-bottom: 30px; }
            input, select, textarea, button { width: 100%; margin-bottom: 10px; padding: 8px; border-radius: 5px; border: 1px solid #ccc; }
            button { background: #007bff; color: #fff; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            canvas { background: #fff; padding: 10px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>🧘‍♀️ Peacebot-AI Mood Tracker</h1>
        <form id="moodForm">
            <label>Date:</label>
            <input type="date" id="date" required>
            <label>Mood:</label>
            <select id="mood">
                <option>Happy</option>
                <option>Neutral</option>
                <option>Sad</option>
                <option>Anxious</option>
                <option>Angry</option>
            </select>
            <label>Notes:</label>
            <textarea id="note" rows="3" placeholder="Optional"></textarea>
            <button type="submit">Log Mood</button>
        </form>
        <h2>📊 Mood History</h2>
        <canvas id="chart" width="400" height="200"></canvas>
        <script>
            async function loadData() {
                const res = await fetch("/api/moodlog");
                const data = await res.json();
                drawChart(data);
            }
            function drawChart(data) {
                const ctx = document.getElementById("chart");
                const labels = data.map(d => d.date);
                const values = data.map(d => {
                    switch (d.mood) {
                        case "Happy": return 5;
                        case "Neutral": return 3;
                        case "Sad": return 2;
                        case "Anxious": return 1;
                        case "Angry": return 0;
                        default: return 3;
                    }
                });
                new Chart(ctx, {
                    type: "line",
                    data: {
                        labels,
                        datasets: [{ label: "Mood Trend", data: values, borderColor: "rgb(54,162,235)", fill: false }]
                    },
                    options: { scales: { y: { min: 0, max: 5, ticks: { stepSize: 1 } } } }
                });
            }
            document.getElementById("moodForm").addEventListener("submit", async e => {
                e.preventDefault();
                const payload = {
                    date: document.getElementById("date").value,
                    mood: document.getElementById("mood").value,
                    note: document.getElementById("note").value
                };
                await fetch("/api/moodlog", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                alert("Mood logged!");
                loadData();
            });
            window.onload = () => {
                document.getElementById("date").valueAsDate = new Date();
                loadData();
            };
        </script>
    </body>
    </html>
    """
    return html

# ----------------------------------------------------------------
# 🌼 Gratitude Helper
# ----------------------------------------------------------------
def log_gratitude_interactive_safe() -> str:
    try:
        items = ["Something I'm grateful for", "A person who made me smile", "A peaceful moment"]
        log_gratitude_noninteractive(items)
        return "Let's do a quick gratitude practice: think of 3 things you're grateful for today 💫"
    except Exception as e:
        logger.error(f"Error saving gratitude: {e}")
        return "Gratitude practice failed, but take a moment to reflect 🌸"

# ----------------------------------------------------------------
# 🧱 Run App
# ----------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    logger.info(f"Running Peacebot on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
