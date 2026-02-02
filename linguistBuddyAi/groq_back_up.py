import os
import json
import logging
import io
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CLIENTS ---
gemini_client = genai.Client(api_key=GEMINI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# --- SYSTEM PROMPT (SHARED) ---
SYSTEM_PROMPT = (
    "You are a friendly, human-like AI Tutor.\n"
    "PROTOCOL:\n"
    "1. TEXT INPUT -> Act as a Linguistics Tutor.\n"
    "2. AUDIO INPUT -> Act as an IELTS Speaking Partner.\n"
    "   - Question/Command: Answer naturally.\n"
    "   - Speech/Answer: Grade it (Fluency, Vocab, Grammar, Pronunciation) + Band Score.\n"
    "FORMATTING:\n"
    "- Use standard Markdown.\n"
    "- Wrap code in triple backticks (```).\n"
    "- Do NOT explain your logic. Be conversational."
)

# --- HELPER: SAFE MARKDOWN ---
def safe_escape(text):
    if not text: return ""
    parts = text.split("```")
    final = ""
    for i, part in enumerate(parts):
        if i % 2 == 0:
            for char in r"_*[]()~>#+-=|{}.!":
                part = part.replace(char, "\\" + char)
            final += part
        else:
            final += f"```\n{part}\n```"
    return final

# --- DATA MANAGER ---
DATA_FILE = "bot_data.json"
class DataManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self):
        default = {"users": {}, "history": {}}
        if not os.path.exists(self.filename): return default
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except: return default

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def set_model(self, user_id, model_name):
        self.data["users"][str(user_id)] = model_name
        self.save_data()

    def get_model(self, user_id):
        return self.data["users"].get(str(user_id), "gemini") # Default to Gemini

db = DataManager(DATA_FILE)

# --- UI HELPER ---
def get_keyboard(current_model):
    if current_model == "gemini":
        btn_text = "🔄Switch to Groq (Llama 3)"
    else:
        btn_text = "🔄Switch to Gemini (Google)"
    
    return ReplyKeyboardMarkup(
        [[KeyboardButton(btn_text)]], 
        resize_keyboard=True, 
        persistent=True
    )

# --- LOGIC: GEMINI ---
async def run_gemini(user_content, history):
    # Convert history to Gemini format
    api_history = []
    # (Simplified history handling for stability)
    
    # Generate
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Content(role="user", parts=user_content)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7
        )
    )
    return response.text

# --- LOGIC: GROQ ---
async def run_groq(text_input, audio_bytes=None):
    # 1. Handle Audio (Whisper)
    if audio_bytes:
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.name = "voice.ogg"
        transcription = groq_client.audio.transcriptions.create(
            file=audio_buffer,
            model="whisper-large-v3-turbo",
            response_format="text"
        )
        text_input = f"{transcription}"

    # 2. Handle Text (Llama 3)
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text_input}
        ],
        temperature=0.7
    )
    return completion.choices[0].message.content

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    curr_model = db.get_model(user_id)
    await update.message.reply_text(
        f"Hello! I am ready.\nCurrent Engine: **{curr_model.upper()}**",
        reply_markup=get_keyboard(curr_model),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    curr_model = db.get_model(user_id)

    # 1. HANDLE SWITCH BUTTON
    if text and "Switch to" in text:
        new_model = "groq" if curr_model == "gemini" else "gemini"
        db.set_model(user_id, new_model)
        
        await update.message.reply_text(
            f"✅ Switched to **{new_model.upper()}** engine.",
            reply_markup=get_keyboard(new_model),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # 2. PREPARE INPUTS
    gemini_content = []
    groq_audio_bytes = None
    groq_text = ""

    if update.message.voice:
        # Show "Recording" status
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
        
        new_file = await context.bot.get_file(update.message.voice.file_id)
        file_bytes = await new_file.download_as_bytearray()
        
        # Prepare for Gemini
        gemini_content.append(types.Part.from_bytes(data=bytes(file_bytes), mime_type="audio/ogg"))
        gemini_content.append(types.Part.from_text(text="[Audio Context]"))
        
        # Prepare for Groq
        groq_audio_bytes = bytes(file_bytes)
        
    elif text:
        gemini_content.append(types.Part.from_text(text=text))
        groq_text = text
    else:
        return

    # 3. EXECUTE BASED ON MODEL
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        raw_reply = ""
        
        if curr_model == "gemini":
            try:
                raw_reply = await run_gemini(gemini_content, [])
            except Exception as e:
                if "429" in str(e):
                    await update.message.reply_text("⚠️ Gemini Limit Reached! Switching to Groq...")
                    db.set_model(user_id, "groq")
                    raw_reply = await run_groq(groq_text, groq_audio_bytes)
                else:
                    raise e
                    
        elif curr_model == "groq":
            raw_reply = await run_groq(groq_text, groq_audio_bytes)

        # 4. REPLY
        safe_reply = safe_escape(raw_reply)
        await update.message.reply_text(safe_reply, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN missing.")
        exit(1)
        
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
    
    print("Hybrid Bot Running...")
    application.run_polling()
