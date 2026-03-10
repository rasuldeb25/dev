# 🤖 Linguist Buddy AI

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![Groq API](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com/)
[![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-API-blue.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Linguist Buddy AI** is an advanced, AI-powered Telegram bot acting as your personal linguistics tutor and IELTS speaking partner. Powered by modern LLMs through Groq and Google Gemini, it helps users practice languages, understand documents, and improve their communication skills.

---

## ✨ Features

*   **🎤 IELTS Speaking Partner:** Send a voice note, and the bot will transcribe it, evaluate your speech (Fluency, Vocabulary, Grammar, Pronunciation), and provide a band score.
*   **📚 Document Analyst:** Upload PDF, DOCX, or TXT files. The bot reads, remembers the context, and answers your questions about the uploaded document.
*   **💬 Smart Chat:** Engage in natural text conversations for grammar explanations, translations, or writing corrections.
*   **🧠 Intelligent Memory:** Remembers recent chat history and active document context to provide continuous and relevant conversational experiences.
*   **🔄 Hybrid Engine:** Seamlessly switch between cutting-edge AI models (Google Gemini and Groq's Llama 3 / Qwen) for optimal performance and reliability.
*   **🧹 Memory Control:** Users can clear their document context anytime with simple commands.
*   **📊 Admin Dashboard:** Special admin commands for checking user statistics and broadcasting messages to all subscribers.

---

## 🛠️ Technology Stack

*   **Language:** [Python 3.8+](https://www.python.org/)
*   **Bot Framework:** [python-telegram-bot](https://python-telegram-bot.org/)
*   **AI Engines:**
    *   [Groq API](https://groq.com/) (Llama 3, Qwen, Whisper)
    *   [Google Gemini API](https://ai.google.dev/) (Gemini 3 Flash)
*   **Document Parsing:** `pypdf`, `python-docx`
*   **Database:** SQLite (for chat history and document storage)
*   **Environment Management:** `python-dotenv`

---

## 🚀 Getting Started

### Prerequisites

You will need the following API keys:
1.  **Telegram Bot Token:** Obtain from [BotFather](https://t.me/botfather) on Telegram.
2.  **Groq API Key:** Obtain from the [Groq Console](https://console.groq.com/).
3.  **Gemini API Key:** Obtain from [Google AI Studio](https://aistudio.google.com/).

### Installation

1.  **Clone the repository (or navigate to the directory):**
    ```bash
    cd linguistBuddyAi
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    *(Assuming a `requirements.txt` file exists; otherwise install the packages manually)*
    ```bash
    pip install python-telegram-bot groq google-genai pypdf python-docx python-dotenv
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `linguistBuddyAi` directory and add your API keys:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
    GROQ_API_KEY=your_groq_api_key_here
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

5.  **Run the bot:**
    You can run either the main version or the hybrid V2 version:
    ```bash
    # Run Version 2 (Recommended for Groq & SQLite memory)
    python linguistV2.py

    # Or run the Hybrid version (Gemini + Groq)
    python linguist.py
    ```

---

## 🎮 Usage Guide

Once the bot is running, find it on Telegram and start chatting:

*   **`/start`** - Initializes the bot and shows the main menu or engine switch options.
*   **`/clear`** - Clears the currently stored document from the bot's memory.
*   **Send a Voice Note** - Automatically triggers the IELTS speaking partner feature.
*   **Upload a File (.pdf, .docx, .txt)** - The bot will read the document and wait for your questions.
*   **Send a Text Message** - Standard smart chat functionality.

### Admin Commands
*(Requires setting your Telegram User ID as `ADMIN_ID` in the code)*
*   **`/stats`** - View the total number of bot subscribers.
*   **`/broadcast [message]`** - Send an announcement to all registered users.

---

## 📝 File Structure

*   `linguistV2.py` - Main bot script featuring SQLite integration, document parsing, and Groq fallback chain.
*   `linguist.py` - Alternative bot script featuring a hybrid Google Gemini & Groq setup.
*   `bot_memory.db` / `bot_data.json` - Automatically generated storage files for user data and contexts.
*   Other backup and utility scripts (`gemini_bak_up.py`, `groq_list_models.py`, etc.).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📄 License

This project is licensed under the MIT License.
