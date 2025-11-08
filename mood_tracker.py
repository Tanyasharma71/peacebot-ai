import json, os
from datetime import date
from flask import Blueprint, request, jsonify

bp = Blueprint("mood_tracker", __name__)
DATA_FILE = os.path.join("data", "mood_logs.json")

# ensure file exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def _load_logs():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def _save_logs(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@bp.route("/api/moodlog", methods=["POST"])
def add_mood():
    payload = request.get_json(force=True)
    mood_entry = {
        "date": payload.get("date", str(date.today())),
        "mood": payload.get("mood", "Neutral"),
        "note": payload.get("note", "")
    }
    logs = _load_logs()
    logs.append(mood_entry)
    _save_logs(logs)
    return jsonify({"status": "success", "message": "Mood logged", "entry": mood_entry}), 201

@bp.route("/api/moodlog", methods=["GET"])
def get_moods():
    logs = _load_logs()
    return jsonify(logs)
