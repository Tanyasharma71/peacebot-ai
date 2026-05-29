
# 🕊️ Peacebot-AI — Your Friendly Mental Health Companion  

![GitHub Repo stars](https://img.shields.io/github/stars/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/Tanyasharma71/peacebot-ai?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/Tanyasharma71/peacebot-ai?style=for-the-badge)
![License](https://img.shields.io/github/license/Tanyasharma71/peacebot-ai?style=for-the-badge)


# 📑 **Table of Contents**

* [🧘‍♀️ Introduction](#🧘‍♀️-introduction)
* [💡 Key Features](#💡-key-features)
* [🧰 Tech Stack](#🧰-tech-stack)
* [🗂️ Project Structure](#🗂️-project-structure)
* [🚀 Quickstart](#🚀-quickstart)

  * [1️⃣ Create and activate a virtual environment](#1️⃣-create-and-activate-a-virtual-environment)
  * [2️⃣ Install dependencies](#2️⃣-install-dependencies)
  * [3️⃣ Configure your API key](#3️⃣-configure-your-api-key)
  * [4️⃣ Run the App](#4️⃣-run-the-app)
  * [5️⃣ API Usage](#5️⃣-api-usage)
* [🧩 Configuration (peacebot.ini)](#🧩-configuration-peacebotini)
* [🔄 Logging Example](#🔄-logging-example)
* [🌱 Future Scope](#🌱-future-scope)
* [🤝 Contributing](#🤝-contributing)
* [📑 Contribution Guidelines](#📑-contribution-guidelines)
* [🧡 Contributing is Fun!](#🧡-contributing-is-fun)
* [👥 Contributors](#👥-contributors)
* [🧪 Running the Test Suite](#🧪-running-the-test-suite)

  * [1️⃣ Run All Tests](#1️⃣-run-all-tests)
  * [2️⃣ Run a Specific Test File](#2️⃣-run-a-specific-test-file)
  * [3️⃣ Expected Output](#3️⃣-expected-output)
* [📄 License](#📄-license)
* [💬 A Final Note](#💬-a-final-note)

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

# 🧠 Project Structure — PeaceBot AI

This document describes the overall directory and file structure of the **PeaceBot AI** project,  
providing an overview of what each file and folder does.

---

## 📁 Root Directory Overview

```bash 
peacebot-ai/
│
├── config/                     # Configuration files for application setup
│   └── config.ini              # Stores app-level configurations and environment variables
│
├── docs/                       # Documentation folder (API references, guides, etc.)
│
├── src/                        # Core source code for PeaceBot AI
│   ├── data/                   # Contains datasets or data processing modules
│   ├── utils/                  # Utility functions and helper scripts
│   │   ├── __init__.py         # Marks 'utils' as a Python package
│   │   ├── config_loader.py    # Handles reading and parsing of configuration files
│   │   ├── logger_config.py    # Configures logging for debugging and monitoring
│   │   └── retry_utils.py      # Implements retry logic for failed API or network calls
│   │
│   ├── App.py                  # Main application entry file or Flask/FastAPI runner
│   ├── Gratitude.py            # Handles gratitude or response generation module
│   ├── peacebot.py             # Main PeaceBot logic or chatbot controller
│   ├── __init__.py             # Initializes the source package
│   └── entry_points.txt        # Defines CLI or app entry points for execution
│
├── static/                     # Static files (HTML, CSS, JS, images)
│   ├── Index.html              # Main web interface for PeaceBot
│   ├── logo.svg                # Project or app logo
│
├── .gitignore                  # Specifies files/folders to ignore in Git commits
│
├── CONTRIBUTING.md             # Guidelines for new contributors
│
├── LICENSE.md                  # Project license (e.g., MIT, AGPL, etc.)
│
├── README.md                   # Main project documentation (overview, usage, setup)
│
├── Requirement.txt             # Python dependencies for installing the project
│
└── config.ini                  # Global configuration file (if outside `config/`)
```
---

## 🚀 Usage Note

To run the project locally:

```bash
# Clone the repository
git clone https://github.com/Tanyasharma71/peacebot-ai.git
cd peacebot-ai

# Install dependencies
pip install -r Requirement.txt

# Run the application
python src/App.py

---

## 🚀 Quickstart  

### 1️⃣ Create and activate a virtual environment  

#### Windows PowerShel
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



---

## 📑 Contribution Guidelines

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212747903-e9bdf048-2dc8-41f9-b973-0e72ff07bfba.gif" width="400">
</div>

- ⭐ **Star** the repository to show your support.  
- 🍴 **Fork** the repo and create a new branch for your feature, fix, or idea.  
- 💻 **Make your changes** — code, design, documentation, anything that improves the project!  
- ✅ **Commit** your updates with a meaningful message.  
- 🔁 **Create a Pull Request** — our team will review, suggest, and merge if all looks great.  
- 🖼️ Add screenshots or demo links if applicable.  

For more detailed steps, see the [**CONTRIBUTING.md**](https://github.com/Tanyasharma71/peacebot-ai/blob/main/CONTRIBUTING.md) file.

---

## 🧡 Contributing is Fun!

We welcome **all contributions and ideas** — whether it's:
- A new feature ✨  
- UI/UX improvements 🎨  
- Bug fixes 🐛  
- or Documentation updates 📘  

Your voice matters!  
Feel free to open issues, start discussions, or reach out with feedback 💬

---

## 👥 Contributors

Thanks to these wonderful people for contributing to **PeaceBot-AI** 💖

[![Contributors](https://contrib.rocks/image?repo=Tanyasharma71/peacebot-ai)](https://github.com/Tanyasharma71/peacebot-ai/graphs/contributors)

<p align="center">
  <a href="https://github.com/Tanyasharma71/peacebot-ai/graphs/contributors">
    <img 
      src="https://api.vaunt.dev/v1/github/entities/Tanyasharma71/repositories/peacebot-ai/contributors?format=svg&limit=54" 
      width="900" 
      height="400" 
      alt="Contributors Graph by Vaunt.dev" 
    />
  </a>
</p>



---

### 🧪 Running the Test Suite

Peacebot now includes a robust test suite for its core backend utilities and tracing middleware.

#### 1️⃣ Run All Tests

From your project root:

    pytest -v

#### 2️⃣ Run a Specific Test File

For example, to only test the retry utility:

    pytest tests/test_retry_utils.py -v

#### 3️⃣ ✅ Expected Output

    ===================== test session starts =====================
    collected 9 items

    tests/test_request_id_context.py ....                      [ 25%]
    tests/test_logger_config.py ....                           [ 50%]
    tests/test_retry_utils.py ....                             [ 75%]
    tests/test_decorators.py ....                              [100%]

    ====================== 9 passed in 1.52s ======================


---

### 📄 License
This project is licensed under the MIT License.
See the `LICENSE` file for details.

### 💬 A Final Note
🧘‍♀️ PeaceBot-AI — Because everyone deserves a moment of peace.<br>
“The greatest weapon against stress is our ability to choose one thought over another.” — William James

⭐ If you find this project helpful, consider giving it a star on GitHub!

