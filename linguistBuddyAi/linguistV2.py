import os
import logging
import io
import asyncio
import re
import sqlite3
import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from groq import Groq
from dotenv import load_dotenv

# --- FILE HANDLING ---
import pypdf
from docx import Document

# --- CONFIGURATION ---
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 1545490936

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CLIENT ---
groq_client = Groq(api_key=GROQ_KEY)

# --- MODELS ---
MODEL_SMART = "llama-3.3-70b-versatile"
MODEL_FAST = "qwen/qwen3-32b"
MODEL_AUDIO = "whisper-large-v3-turbo"

# --- DATABASE MANAGER (SQLite) ---
DB_FILE = "bot_memory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (user_id INTEGER PRIMARY KEY, file_name TEXT, file_content TEXT)''')
    # Admin Table for Subscribers
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers
                 (user_id INTEGER PRIMARY KEY, joined_date DATETIME)''')
    conn.commit()
    conn.close()

def add_subscriber(user_id):
    """Adds a new user to the subscriber list."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers VALUES (?, ?)",
              (user_id, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_all_subscribers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM subscribers")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
              (user_id, role, content, datetime.datetime.now()))
    conn.commit()
    conn.close()

def save_document_context(user_id, file_name, text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?)",
              (user_id, file_name, text))
    conn.commit()
    conn.close()

def clear_document_context(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM documents WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_context(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Get Document
    c.execute("SELECT file_name, file_content FROM documents WHERE user_id=?", (user_id,))
    doc_row = c.fetchone()
    doc_context = ""
    if doc_row:
        doc_context = (
            f"\n<active_document>\n"
            f"FILE NAME: {doc_row[0]}\n"
            f"CONTENT:\n{doc_row[1]}\n"
            f"</active_document>\n"
        )

    # Get Chat History (Last 8)
    c.execute("SELECT role, content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 8", (user_id,))
    rows = c.fetchall()
    history = []
    for row in reversed(rows):
        history.append({"role": row[0], "content": row[1]})

    conn.close()
    return doc_context, history

# --- HELPER: HTML FORMATTER ---
def safe_escape(text):
    if not text: return ""
    def escape_chars(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts = text.split("```")
    final_text = ""
    for i, part in enumerate(parts):
        if i % 2 == 0:
            part = escape_chars(part)
            part = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', part)
            part = re.sub(r'__(.*?)__', r'<i>\1</i>', part)
            part = re.sub(r'#{1,6}\s*(.*?)\n', r'<b>\1</b>\n', part)
            part = re.sub(r'`(.*?)`', r'<code>\1</code>', part)
            final_text += part
        else:
            part = escape_chars(part)
            final_text += f"<pre>{part}</pre>"
    return final_text

# --- FILE EXTRACTORS ---
def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text[:25000]
    except Exception as e:
        return f"[PDF Error: {e}]"

def extract_text_from_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])[:25000]
    except Exception as e:
        return f"[Docx Error: {e}]"

# --- LOGIC: GROQ (WITH FALLBACKS) ---
def _groq_worker(messages, requested_model=MODEL_SMART):
    # The Chain of Command: Try these models in order if one fails
    fallback_chain = [
        requested_model,            # 1. Try what we wanted (usually Llama 70b)
        "qwen/qwen3-32b",           # 2. Backup: Qwen (Smarter than 8b)
        "llama-3.1-8b-instant"      # 3. Emergency: Llama 8b (Fastest, huge limits)
    ]
    
    last_error = None
    
    for model in fallback_chain:
        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            raw_content = completion.choices[0].message.content
            
            # 🧼 CLEANER: Remove <think> blocks (for Qwen/DeepSeek)
            clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            
            # If we had to switch models, add a tiny note so you know
            if model != requested_model:
                clean_content += f"\n\n<i>(⚠️ Note: Llama 70B was busy, so <b>{model}</b> answered this.)</i>"
                
            return clean_content

        except Exception as e:
            # Only switch if it's a Rate Limit (429) or Server Overload (503)
            err_str = str(e)
            if "429" in err_str or "503" in err_str or "rate limit" in err_str.lower():
                print(f"⚠️ Model {model} failed ({err_str}). Switching to backup...")
                last_error = e
                continue # Try the next model in the list
            else:
                raise e # If it's a real code error, stop.
    
    # If all 3 failed
    raise last_error

# --- ADMIN HANDLERS ---

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Check user count."""
    if update.effective_user.id != ADMIN_ID: return # Security Check

    users = get_all_subscribers()
    await update.message.reply_text(f"📊 **Bot Statistics**\n\n👥 Total Users: {len(users)}", parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Send message to all users."""
    if update.effective_user.id != ADMIN_ID: return

    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("⚠️ Usage: /broadcast [Your Message]")
        return

    users = get_all_subscribers()
    success_count = 0

    status_msg = await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **Announcement**\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            success_count += 1
        except Exception:
            pass # User blocked bot

    await status_msg.edit_text(f"✅ Broadcast Complete!\nSent to: {success_count}/{len(users)} users.")

# --- USER HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_subscriber(user.id) # Add to Admin List

    # The Button
    keyboard = [[KeyboardButton("🪄 About Me")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

    await update.message.reply_text(
        f"👋 **Hello, {user.first_name}!**\n\n"
        "I am your AI Language Companion.\n"
        "Tap the button below to see what I can do!",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # --- HANDLE "ABOUT ME" BUTTON ---
    if text == "🪄 About Me":
        await update.message.reply_text(
            "✨ **I am LinguistBot!** Your personal AI tutor.\n\n"
            "Here is how you can use me:\n\n"
            "🎤 **IELTS Speaking Partner**\n"
            "Send me a voice note! I will listen and act as a human examiner (or just chat if you say 'Hi').\n\n"
            "📚 **Document Analyst**\n"
            "Send me a PDF or DOCX file. I will read it, remember it, and answer your questions about it!\n\n"
            "💬 **Smart Chat**\n"
            "Just text me! I can explain grammar, translate, or correct your writing.\n\n"
            "🧹 **Memory Control**\n"
            "Type `/clear` to make me forget the file I read.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # --- NORMAL LOGIC ---
    user_input = ""
    target_model = MODEL_FAST

    system_instruction = (
        "You are a friendly, human-like AI Tutor.\n"
        "PROTOCOL:\n"
        "1. TEXT INPUT -> Act as a helpful Linguistics Tutor.\n"
        "   - Note: If an <active_document> is provided, use it ONLY if the user asks about it. Otherwise, ignore it.\n"
        "2. AUDIO INPUT -> Act as an IELTS Speaking Partner.\n"
        "   - IF USER ASKS A QUESTION OR GREETS (e.g. 'Hi'): Just answer/greet naturally. Do NOT say 'I will answer you'.\n"
        "   - IF USER GIVES A SPEECH: Grade it (Fluency, Vocab, Grammar, Pronunciation) + Band Score.\n"
        "FORMATTING:\n"
        "- Use standard Markdown.\n"
        "- Wrap code in triple backticks (```).\n"
        "- Do NOT explain your internal logic (e.g., never say 'Since you asked...').\n"
        "- Keep it conversational and warm."
    )

    # 1. HANDLE DOCUMENTS
    if update.message.document:
        doc = update.message.document
        file_ext = doc.file_name.split('.')[-1].lower()
        if file_ext not in ['pdf', 'docx', 'txt']:
            await update.message.reply_text("⚠️ Supported: .pdf, .docx, .txt")
            return

        status_msg = await update.message.reply_text(f"📥 Reading {doc.file_name}...")
        new_file = await context.bot.get_file(doc.file_id)
        file_bytes = await new_file.download_as_bytearray()

        extracted_text = ""
        if file_ext == 'pdf':
            extracted_text = extract_text_from_pdf(bytes(file_bytes))
        elif file_ext == 'docx':
            extracted_text = extract_text_from_docx(bytes(file_bytes))
        elif file_ext == 'txt':
            extracted_text = bytes(file_bytes).decode('utf-8')[:25000]

        save_document_context(user_id, doc.file_name, extracted_text)
        user_input = f"I have uploaded a document: {doc.file_name}. Summarize it briefly."
        target_model = MODEL_SMART
        await status_msg.delete()

    # 2. HANDLE AUDIO
    elif update.message.voice:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
        new_file = await context.bot.get_file(update.message.voice.file_id)
        file_bytes = await new_file.download_as_bytearray()

        audio_buffer = io.BytesIO(file_bytes)
        audio_buffer.name = "voice.ogg"

        transcription = await asyncio.to_thread(
            groq_client.audio.transcriptions.create,
            file=audio_buffer,
            model=MODEL_AUDIO,
            response_format="text"
        )
        user_input = f"[USER AUDIO]: \"{transcription}\""
        target_model = MODEL_SMART

    # 3. HANDLE TEXT
    elif update.message.text:
        user_input = update.message.text
        if len(user_input) > 20:
            target_model = MODEL_SMART
    else:
        return

# 4. EXECUTE
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # Save User Message
        save_message(user_id, "user", user_input)

        # Build Context
        doc_context, chat_history = get_context(user_id)

        final_prompt = system_instruction
        if doc_context: final_prompt += doc_context

        messages = [{"role": "system", "content": final_prompt}]
        messages.extend(chat_history)

        # Run AI (The <think> cleaner is inside run_groq/_groq_worker now)
        raw_reply = await run_groq(messages, model=target_model)

        # Save Assistant Message
        save_message(user_id, "assistant", raw_reply)

        # --- CHUNKING LOGIC (Fixes "Message too long" error) ---
        if len(raw_reply) > 4000:
            # Split by lines to avoid cutting words in half
            lines = raw_reply.split('\n')
            chunk = ""
            for line in lines:
                if len(chunk) + len(line) < 4000:
                    chunk += line + "\n"
                else:
                    # Send full chunk
                    await update.message.reply_text(safe_escape(chunk), parse_mode=ParseMode.HTML)
                    chunk = line + "\n"
            # Send remaining chunk
            if chunk:
                await update.message.reply_text(safe_escape(chunk), parse_mode=ParseMode.HTML)
        else:
            # Send normally
            safe_reply = safe_escape(raw_reply)
            model_tag = "Llama 3" if target_model == MODEL_SMART else "Qwen"
            await update.message.reply_text(safe_reply + f"\n\n<i>🧠 {model_tag}</i>", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error: {e}")
        # If the error is still length-related (e.g. one huge line), fallback to simple splitting
        if "Message is too long" in str(e):
             await update.message.reply_text("⚠️ Response was too long. Sending as plain text...")
             # Force split every 4000 chars
             for i in range(0, len(raw_reply), 4000):
                 await update.message.reply_text(raw_reply[i:i+4000])
        else:
             await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_document_context(user_id)
    await update.message.reply_text("🧹 **Memory Wiped!** File forgotten.")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN missing.")
        exit(1)

    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_memory))

    # Admin Commands
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Messages
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    print(f"Bot Running... (Admin + About Me Added)")
    application.run_polling()
