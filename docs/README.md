
# 🕊️ Peacebot-AI — Your Friendly Mental Health Companion  

![GitHub Repo stars](https://img.shields.io/github/stars/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/Tanyasharma71/peacebot-ai?style=for-the-badge)
![License](https://img.shields.io/github/license/Tanyasharma71/peacebot-ai?style=for-the-badge)

---

## 🧘‍♀️ Introduction  

**Peacebot-AI** is an **AI-powered mental health chatbot** designed to provide **empathetic conversations**, **stress management tips**, and **mindfulness guidance** to users seeking emotional support.  

It aims to create a **safe, non-judgmental, and supportive environment** through intelligent and compassionate AI-driven dialogue. 🌸  

---

## 💡 Key Features  

- 💬 **Conversational support** for stress, anxiety, and emotional wellness  
- 🧠 **Natural language responses** powered by OpenAI’s GPT models  
- 📚 **Personalized mindfulness & coping strategies**  
- 🔒 **Privacy-first** — no user data storage or profiling  
- 🕒 **Available anytime, anywhere**, for daily motivation and reflection  
- ⚙️ **Modular architecture** for easy customization and expansion  

---

## 🧰 Tech Stack  

| Component | Technology |
|------------|------------|
| **Language** | Python |
| **Backend Framework** | Flask |
| **AI Integration** | OpenAI GPT API |
| **Frontend** | HTML, CSS, JavaScript |
| **Configuration Management** | `configparser`, `.env` support |
| **Logging** | Python `logging` (JSON-structured logs) |
| **Version Control** | Git & GitHub |

---

## 🗂️ Project Structure  

```bash
peacebot-ai/
├── src/
│ ├── app.py # Flask entry point
│ ├── peacebot.py # Core AI response logic
│ ├── utils/
│ │ ├── config_loader.py # Handles .ini config and fallbacks
│ │ ├── logger_config.py # JSON-based structured logging
│ │ ├── retry_utils.py # Retry & exponential backoff logic
│ │ └── init.py
│ ├── templates/
│ │ └── index.html # Frontend chat interface
│ ├── static/
│ │ ├── css/
│ │ │ └── style.css
│ │ └── js/
│ │ └── script.js
│ └── init.py
│
├── gratitude_log.json # Logs user gratitude entries
├── peacebot.ini # Config file (API keys, retry, etc.)
├── requirements.txt # Python dependencies
├── .env # (Optional) API key storage
├── README.md # Project documentation
└── LICENSE # MIT License
```
---

## 🚀 Quickstart  

### 1️⃣ Create and activate a virtual environment  

#### Windows PowerShell
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```
#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Configure your API key
**Option 1 — Using Environment Variable**
```bash
setx OPENAI_API_KEY "your_openai_key_here"
```
**Option 2 — Using .env File**

Create a .env file in the project root:
```bash
OPENAI_API_KEY=your_openai_key_here
```

### 4️⃣ Run the App
```bash
python src/app.py
```

Visit http://127.0.0.1:5000 in your browser.
You can chat with Peacebot directly in the web interface.

### 5️⃣ API Usage

| Method | Endpoint  | Description                                   |
|--------|-----------|-----------------------------------------------|
| POST   | /api/chat | Send a message to Peacebot and receive a response |

**Example Request:**
```bash
{
  "message": "I'm feeling anxious today."
}
```
**Example Response:**
```bash
{
  "response": "I hear you. It sounds like you're having a tough day. Try a short breathing exercise — inhale deeply for 4 seconds..."
}
```
### 🧩 Configuration (peacebot.ini)
Example peacebot.ini:<br>
```bash
[openai]
api_key = your_openai_key_here
model = gpt-3.5-turbo

[retry]
max_retries = 3
base_delay = 2

[logging]
level = INFO
```
### 🔄 Logging Example
Peacebot logs structured information for traceability:
```bash
{"time": "2025-11-08 14:42:01", "level": "INFO", "module": "peacebot", "message": "Response generated successfully"}
{"time": "2025-11-08 14:42:05", "level": "WARNING", "module": "peacebot.retry", "message": "Retry 1/3 for OpenAI request"}
```
### 🌱 Future Scope
- 🧩 Integrate emotion detection using NLP
- 📈 Add mood visualization dashboard
- 🗓️ Implement daily mental wellness check-ins
- 🔐 Optional user authentication for personal sessions
- 💾 Support cloud-based session storage
- 🧠 Add local LLM fallback (offline mode)

### 🤝 Contributing
We welcome all contributions!<br>
Please read the CONTRIBUTING.md file before submitting pull requests.

To suggest new ideas or report bugs:<br>
Open an issue in the Issues tab with descriptive titles and clear acceptance criteria
**Example Issue Ideas**

| ID  | Issue Title               | Summary                                           |
|-----|---------------------------|--------------------------------------------------|
| #2  | Add Config System         | Introduce configparser-based modular configuration |
| #3  | Retry & Failure Handling  | Add exponential backoff for API resilience       |
| #4  | Add Emotion Classification | Use sentiment analysis to tailor responses      |
| #5  | Web Dashboard             | Visualize user moods and gratitude logs          |


### 📄 License
This project is licensed under the MIT License.
See the `LICENSE` file for details.

### 💬 A Final Note
🧘‍♀️ PeaceBot-AI — Because everyone deserves a moment of peace.<br>
“The greatest weapon against stress is our ability to choose one thought over another.” — William James

⭐ If you find this project helpful, consider giving it a star on GitHub!
