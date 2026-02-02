import os
import json
import logging
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 123456789  # <--- REPLACE WITH YOUR ID

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=API_KEY)

# --- SYSTEM INSTRUCTION (SINGLE & POWERFUL) ---
SYSTEM_PROMPT = (
    "You are an advanced AI Tutor.\n"
    "PROTOCOL:\n"
    "1. TEXT INPUT -> Act as Linguistics Tutor. Answer concisely.\n"
    "2. AUDIO INPUT -> Act as IELTS Examiner.\n"
    "   - If user asks a question: Answer it. DO NOT GRADE.\n"
    "   - If user gives a speech: Grade it (Fluency, Vocab, Grammar, Pronunciation) + Band Score.\n"
    "FORMATTING: Use plain text. Use UPPERCASE for headers. Use emojis."
)

# --- HELPER: CLEAN TEXT ---
def clean_text(text):
    """Removes Markdown symbols that look bad in plain text."""
    if not text: return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)     # Remove italic
    text = re.sub(r'#{1,6}\s?', '', text)        # Remove headers
    return text

# --- DATA MANAGER (ROBUST) ---
DATA_FILE = "bot_data.json"
class DataManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self):
        # Auto-create fresh structure if missing or corrupt
        default_data = {"users": [], "history": {}}
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Check if 'history' key exists, if not (old version), reset it
                    if "history" not in data:
                        return default_data
                    return data
            except:
                return default_data
        return default_data

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_user(self, user_id):
        if user_id not in self.data["users"]:
            self.data["users"].append(user_id)
            self.save_data()

    def update_history(self, user_id, role, text):
        key = str(user_id)
        if key not in self.data["history"]:
            self.data["history"][key] = []
        self.data["history"][key].append({"role": role, "parts": [{"text": text}]})
        # Keep last 10 turns to save tokens
        if len(self.data["history"][key]) > 10:
            self.data["history"][key] = self.data["history"][key][-10:]
        self.save_data()

    def get_history(self, user_id):
        return self.data["history"].get(str(user_id), [])

db = DataManager(DATA_FILE)

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id)
    await update.message.reply_text(
        f"Hello {user.first_name}! \n\n"
        "📝 Send Text for Linguistics help.\n"
        "🎤 Send Voice for IELTS evaluation.\n\n"
        "I'm ready!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_content = []
    
    # 1. Detect Input
    if update.message.voice:
        status_msg = await update.message.reply_text("🎧 Processing...")
        
        # Download Audio to MEMORY (RAM) not DISK
        new_file = await context.bot.get_file(update.message.voice.file_id)
        
        # We download as bytearray
        audio_bytes = await new_file.download_as_bytearray()
        
        # Convert to Gemini Part directly (No disk usage)
        user_content.append(types.Part.from_bytes(data=bytes(audio_bytes), mime_type="audio/ogg"))
        user_content.append(types.Part.from_text(text="[Audio Context]"))
        
        await status_msg.delete()

    elif update.message.text:
        user_content.append(types.Part.from_text(text=update.message.text))
    else:
        return

    # 2. Call Gemini
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Load History
        chat_history = db.get_history(user_id)
        api_history = []
        for turn in chat_history:
            api_history.append(types.Content(
                role=turn["role"], 
                parts=[types.Part.from_text(text=turn["parts"][0]["text"])]
            ))

        # Generate Response
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=api_history + [types.Content(role="user", parts=user_content)],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )
        
        # 3. Clean & Reply
        raw_reply = response.text
        clean_reply = clean_text(raw_reply)
        
        # Save History
        log_text = update.message.text if update.message.text else "[Audio Message]"
        db.update_history(user_id, "user", log_text)
        db.update_history(user_id, "model", clean_reply)
        
        await update.message.reply_text(clean_reply)

    except Exception as e:
        logger.error(f"GenAI Error: {e}")
        # Reset history on error (often fixes 'stuck' chats)
        if "history" in str(e):
             db.data["history"][str(user_id)] = []
             db.save_data()
             await update.message.reply_text("⚠️ Memory Reset. Please try again.")
        else:
             await update.message.reply_text(f"⚠️ Error: {str(e)}")

# --- BROADCAST ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg: return
    for uid in db.data["users"]:
        try: await context.bot.send_message(chat_id=uid, text=f"📢 {msg}")
        except: pass
    await update.message.reply_text("Broadcast sent.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
    
    print("Bot is running...")
    application.run_polling()