🧠 CONTRIBUTING.md — PeaceBot AI (Winter of Code Social)

# 🤖 Contributing to PeaceBot AI

Welcome to **PeaceBot AI**, a chatbot project under **Winter of Code Social (WOCS)**!  
We’re thrilled to have you here. This guide will walk you through contributing effectively, following Code Social’s open-source standards.

---

## 🌱 About the Project
PeaceBot AI aims to promote **peaceful dialogue, positivity, and mindfulness through AI-driven chat interactions**.  
The project uses **Python, NLP models, and Flask** for backend development, with potential integrations for **sentiment analysis** and **emotion-aware responses**.

---

## 🚀 Getting Started

### 1. Fork the Repository
Click **Fork** on the top-right of this page to create your own copy under your GitHub account.

### 2. Clone Your Fork
```bash
git clone https://github.com/<your-username>/peacebot-ai.git
cd peacebot-ai

3. Set Up the Project

Install dependencies:

pip install -r requirements.txt

Run the app locally:

python app.py


---

🌿 Branch Workflow

1. Create a New Branch

Create a feature branch for your changes:

git checkout -b feature/<your-feature-name>

Example:

git checkout -b feature/add-intent-detection

2. Make Your Changes

Follow the coding and documentation standards mentioned below.

3. Commit Your Changes

Use clear and conventional commit messages:

git add .
git commit -m "feat: add NLP-based emotion detection"

Commit message prefixes:

feat: → new feature

fix: → bug fix

docs: → documentation only

style: → code formatting or lint fixes

refactor: → code restructuring

test: → adding/modifying tests


4. Push and Open a Pull Request

git push origin feature/<your-feature-name>

Then go to your fork on GitHub → click Compare & Pull Request → fill in the PR details.


---

🧩 Pull Request Guidelines

One feature/fix per PR.

Include a detailed description of what your PR does.

Link any related issues using:

Closes #<issue-number>

Ensure labels are correctly added before merge:

wocs

level 1 / level 2 / level 3



⚠️ PRs merged without correct labels may not earn WOCS points.


---

🧠 Coding Standards

Aspect	Guideline

Language	Python (Flask, NLP)
Indentation	4 spaces
Naming	snake_case for variables, PascalCase for classes
Docstrings	Use triple quotes for all functions/classes
Commenting	Explain logic, not obvious syntax
Imports	Group by standard, third-party, and local


Example Function:

def generate_response(user_input: str) -> str:
    """
    Generate a context-aware response to user input using NLP.
    """
    sentiment = analyze_sentiment(user_input)
    return compose_reply(sentiment)


---

🐞 Reporting Issues

Use the Issues tab and follow this format:

Title: [Bug] PeaceBot doesn’t detect greeting properly
Description:

Steps to reproduce

Expected vs actual result

Logs or screenshots (if any)

Environment (OS, Python version)


Apply appropriate labels:

bug

enhancement

documentation

help wanted

good first issue



---

🧾 WOCS Contribution Points

Level	Description	Points

Level 1	Minor fix or doc update	2
Level 2	Medium feature or major refactor	5
Level 3	Complex module or multi-file feature	11


Points are awarded after PR merge by mentors/admins.


---

💬 Communication & Support

Join the Code Social Discord: discord.gg/MSTNyRSPYW

Tag @Team | Arushi or @Team | Rizwan for help

Email: codesocialcommunity@gmail.com



---

🌟 Best Practices

1. Comment before working on an issue to avoid duplication.


2. Keep PRs small and focused.


3. Always sync your fork before new work:

git pull upstream main


4. Respect community guidelines — PeaceBot AI stands for positivity 💫.




---

🏆 Sharing Your Journey

Follow the Code Social principle: “Learn. Build. Share.”

Post your progress on LinkedIn using:

#CodeSocial #WinterOfCode #OpenSource #LearnBuildShare

Mention your mentor, tag Code Social, and include screenshots of your work.

Use the provided templates from the CodeSocial LinkedIn Kit.



---

🙏 Thank You

Every contribution matters — whether it’s a small doc fix or a big NLP feature.
By contributing to PeaceBot AI, you’re helping build a more mindful and positive open-source space.

Happy coding 💙