# 🕊️ Peacebot-AI — Your Friendly Mental Health Companion  

![GitHub Repo stars](https://img.shields.io/github/stars/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/Tanyasharma71/peacebot-ai?style=for-the-badge)
![License](https://img.shields.io/github/license/Tanyasharma71/peacebot-ai?style=for-the-badge)

---

## 🧘‍♀️ Introduction  

**Peacebot-AI** is an intelligent, empathetic chatbot built to offer emotional support, motivational messages, and mindfulness guidance.  

It’s an **AI-powered mental health chatbot** designed to provide **empathetic conversations, stress-relief guidance, and helpful resources** to individuals experiencing emotional distress.  

Built with a **user-centric approach**, Peacebot-AI aims to create a **safe, non-judgmental space** for mental wellness conversations. 🌸  

---

## 💡 Key Features  

- 💬 **Conversational support** for stress, anxiety, and loneliness  
- 🧠 **Natural Language Understanding** powered by OpenAI’s GPT API  
- 📚 **Personalized coping strategies** and mental health tips  
- 🔒 **Privacy-focused** — no user profiling or data sharing  
- 🕒 **Always available** for support, anytime, anywhere  

---

## 🧰 Tech Stack  

| Component | Technology Used |
|------------|----------------|
| **Language** | Python |
| **AI Integration** | OpenAI GPT (via API) |
| **Backend** | Flask (REST API Server) |
| **Frontend** | HTML, CSS, JavaScript |
| **Version Control** | Git & GitHub |

---

## 🚀 Quickstart  

### 1️⃣ Create and activate a virtual environment  

#### **Windows PowerShell**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies

   - `pip install -r requirement.txt`

3. (Optional) Set your OpenAI API key to enable AI responses

   - PowerShell: `setx OPENAI_API_KEY "your_key_here"`
   - Or create a `.env` file with `OPENAI_API_KEY=your_key_here`

4. Run the app

   - `python App.py`
   - Open `http://127.0.0.1:5000` in your browser

5. API usage
   - POST `http://127.0.0.1:5000/api/chat` with JSON `{ "message": "your text" }`

Notes

- The app works without an OpenAI key using a rule-based fallback.

🌱 Future Scope
Add data visualization (mood graphs)
Web-based interface using Flask
Emotion detection from user input
Daily mental wellness check-ins
Password protection

---

📄 License
This project is licensed under the MIT License.

🧘‍♀️ PeaceBot AI — Because everyone deserves a moment of peace.

Checkout @CONTRIBUTING.md before getting started for more information
