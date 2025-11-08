import os
import json
import logging
from datetime import date
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from dotenv import load_dotenv

from peacebot import PeacebotResponder
from Gratitude import log_gratitude_noninteractive

# ---------------------------------------------------------------------
# 🧠 Setup and Configuration
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
responder = PeacebotResponder()

# Constants
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "Index.html")
GRATITUDE_KEYWORDS = {"gratitude", "thanks", "thank you"}

# ---------------------------------------------------------------------
# 🌿 Mood Tracker Setup
# ---------------------------------------------------------------------
os.makedirs("data", exist_ok=True)
MOOD_FILE = os.path.join("data", "mood_logs.json")
if not os.path.exists(MOOD_FILE):
    with open(MOOD_FILE, "w") as f:
        json.dump([], f)

# ---------------------------------------------------------------------
# 🌸 Template Loading
# ---------------------------------------------------------------------
try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        INDEX_TEMPLATE = f.read()
except FileNotFoundError:
    logger.error(f"Template file not found: {TEMPLATE_PATH}")
    INDEX_TEMPLATE = "<html><body><h1>Template not found</h1></body></html>"

# ---------------------------------------------------------------------
# 💬 Peacebot Chat Routes
# ---------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    """Main chatbot route for web interface."""
    user_message = None
    bot_reply = None

    if request.method == "POST":
        user_message = (request.form.get("message") or "").strip()
        if user_message.lower() in GRATITUDE_KEYWORDS:
            bot_reply = log_gratitude_interactive_safe()
        else:
            bot_reply = responder.generate_response(user_message)

    return render_template_string(INDEX_TEMPLATE, user_message=user_message, bot_reply=bot_reply)


@app.get("/static/<path:filename>")
def static_assets(filename: str):
    """Serve static assets."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        logger.warning(f"Static directory not found: {static_dir}")
        return jsonify({"error": "Static directory not found"}), 404
    return send_from_directory(static_dir, filename)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for chat interactions."""
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
        logger.error(f"Error in api_chat: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500


# ---------------------------------------------------------------------
# 🧘‍♀️ Mood Tracker Routes
# ---------------------------------------------------------------------
@app.route("/api/moodlog", methods=["POST"])
def add_mood():
    """Add a new mood entry (POST)."""
    try:
        data = request.get_json(force=True)
        mood_entry = {
            "date": data.get("date", str(date.today())),
            "mood": data.get("mood", "Neutral"),
            "note": data.get("note", "")
        }

        with open(MOOD_FILE, "r") as f:
            logs = json.load(f)
        logs.append(mood_entry)
        with open(MOOD_FILE, "w") as f:
            json.dump(logs, f, indent=2)

        logger.info(f"Mood logged: {mood_entry}")
        return jsonify({"status": "success", "entry": mood_entry}), 201

    except Exception as e:
        logger.error(f"Error adding mood: {e}")
        return jsonify({"error": "Failed to log mood"}), 500


@app.route("/api/moodlog", methods=["GET"])
def get_moods():
    """Fetch all stored mood entries (GET)."""
    try:
        with open(MOOD_FILE, "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Error loading moods: {e}")
        return jsonify({"error": "Failed to load mood logs"}), 500


@app.route("/mood")
def mood_page():
    """Serve the Mood Tracker web page."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Peacebot-AI | Mood Tracker</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f7fa; }
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
            <label for="date">Date:</label>
            <input type="date" id="date" required>

            <label for="mood">Mood:</label>
            <select id="mood">
                <option>Happy</option>
                <option>Neutral</option>
                <option>Sad</option>
                <option>Anxious</option>
                <option>Angry</option>
            </select>

            <label for="note">Notes:</label>
            <textarea id="note" rows="3" placeholder="Optional..."></textarea>

            <button type="submit">Log Mood</button>
        </form>

        <h2>📊 Mood History</h2>
        <canvas id="moodChart" width="400" height="200"></canvas>

        <script>
            async function loadMoods() {
                const res = await fetch("/api/moodlog");
                const data = await res.json();
                drawChart(data);
            }

            function drawChart(data) {
                const ctx = document.getElementById("moodChart");
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
                        datasets: [{
                            label: "Mood Trend",
                            data: values,
                            borderColor: "rgba(75,192,192,1)",
                            fill: false
                        }]
                    },
                    options: { scales: { y: { min: 0, max: 5, ticks: { stepSize: 1 } } } }
                });
            }

            document.getElementById("moodForm").addEventListener("submit", async (e) => {
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
                loadMoods();
            });

            window.onload = () => {
                document.getElementById("date").valueAsDate = new Date();
                loadMoods();
            };
        </script>
    </body>
    </html>
    """
    return html


# ---------------------------------------------------------------------
# 🌼 Gratitude Helper
# ---------------------------------------------------------------------
def log_gratitude_interactive_safe() -> str:
    """Safe non-blocking gratitude logger for web usage."""
    try:
        placeholder_items = [
            "Something I'm grateful for today",
            "A person who made me smile",
            "A moment of peace I experienced"
        ]
        log_gratitude_noninteractive(placeholder_items)
        logger.info("Gratitude placeholder saved successfully")
        return ("Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
                "If you want to save them, use the CLI tool later or add a web form here.")
    except Exception as e:
        logger.error(f"Error saving gratitude placeholder: {str(e)}")
        return ("Let's do a quick gratitude practice: think of 3 small things you're grateful for. "
                "I couldn't save them right now, but reflecting is still powerful.")


# ---------------------------------------------------------------------
# ⚠️ Error Handlers
# ---------------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------
# 🚀 Run the Server
# ---------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    logger.info(f"Starting Peacebot server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
