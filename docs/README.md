# Peacebot-AI your friendly mental health campanion 
peacebot ai is an intelligent empathetic chatbot built to offer emotional support , motivational message and mindfulness guidance 
 Peacebot AI* is an AI-powered mental health chatbot designed to provide empathetic support, stress-relief conversations, and helpful resources to individuals experiencing emotional distress. Built with a user-centric approach, Peacebot aims to offer a safe, non-judgmental space for mental wellness conversations.

 💡 Key Features

 💬 Conversational support for stress, anxiety, and loneliness  
 🧠 Natural Language Understanding using OpenAI's API  
 📚 Personalized mental health tips and coping strategies  
 🔒 Privacy-focused and respectful interactions  
 🕒 Always available for support, anytime, anywhere  

 🧰 Tech Stack

 Language:* Python  
 AI Integration:* OpenAI GPT (via API)  
 Backend:* Flask (for API server)  
 Frontend :* HTML/CSS/JavaScript  
 Version Control:* Git & GitHub  

## Quickstart

1. Create and activate a virtual environment
   - Windows PowerShell
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`

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
- Type "gratitude" to try the gratitude flow in the UI.

### Branding
- Replace `static/logo.svg` with your own logo (keep the filename) or update the `<img src="/static/logo.svg">` in `Index.html`.
- Brand colors are controlled via CSS variables in `Index.html` under `:root`:
  - `--primary` (soft blue), `--accent` (mint green), `--bot` and `--user` bubble colors.
- Dark theme values are defined under `body[data-theme="dark"]`. Adjust as needed.
  
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
