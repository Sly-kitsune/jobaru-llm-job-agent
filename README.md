# Jobaru 🤖💼
**The Autonomous AI Job Application Agent**

Jobaru is a smart, local-first AI agent that helps you find and apply to jobs on LinkedIn automatically. It uses **Ollama** (local LLMs) to analyze your resume, match it with job descriptions, and even draft cover letters for you.

## 🚀 Features

*   **resume Analysis**: Auto-detects the best job roles for you based on your resume.
*   **Smart Search**: Scrapes LinkedIn for the freshest jobs (Past 24h) and filters out duplicates.
*   **Auto-Apply**: Can click "Easy Apply" and fill out forms for you.
*   **Human-in-the-Loop**: Safely pauses for critical steps (Review/Submit) or tricky questions (why do you fit?) so you never send a bad application.
*   **Privacy First**: Runs locally on your machine. Your resume and data never leave your computer (except to apply!).

## 🛠️ Prerequisites

1.  **Python 3.10+** installed.
2.  **Google Chrome** installed.
3.  **Ollama** installed and running (for AI features).
    *   Download from [ollama.com](https://ollama.com).
    *   Run `ollama pull mistral` (or your preferred model).

## 📦 Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/jobaru.git
    cd jobaru
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Usage

1.  **Prepare your Resume**: Have your `Resume.pdf` or `resume.txt` ready.
2.  **Start the Agent**:
    ```bash
    python main.py
    ```
3.  **Follow the Wizard**:
    *   The agent will ask for your resume and target role.
    *   It can optionally analyze your resume to suggest roles!
4.  **Login**: A browser will open. Log in to LinkedIn manually when prompted.
5.  **Watch it Go**: The agent will start hunting for jobs.

## ⚠️ Disclaimer

This tool is for educational purposes. Use responsibly. Automated scraping/applying may violate LinkedIn's Terms of Service. The authors are not responsible for any account restrictions.

## 🤝 Contributing

Feel free to fork and submit PRs!
