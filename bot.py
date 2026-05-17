import asyncio
import logging
import os
from supabase import create_client
from flask import Flask
from threading import Thread

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

# =========================
# CONFIG
# =========================
OWNER_ID = 7354394647
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# FLASK KEEP ALIVE
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Alive"

PORT = int(os.environ.get("PORT", 10000))

def run_web():
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# =========================
# IMAGE
# =========================

PHOTO_URL = "https://i.ibb.co/5XkMbSLp/x.jpg"

# =========================
# START COMMAND
# =========================

@dp.message(F.text == "/start")
async def start_cmd(message: Message):

    supabase.table("users").upsert({
        "user_id": message.from_user.id
    }).execute()

    caption = """
🔥 PREMIUM 18+ CONTENT 😘🔥

1. Indian Desi Videos - 10000+
2. Couple Videos - 5000+
3. Amateur Videos - 3000+
4. HD Collection - 7000+

😍 Lifetime Access
😍 Premium Collection
😍 Total 50000+ Videos

AT ------------>> ₹57/- 💋

Instant Access Available For You 🌚
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="UNLOCK 💎",
                    callback_data="unlock"
                ),

                InlineKeyboardButton(
                    text="DEMO 😋",
                    callback_data="demo"
                )
            ],

            [
                InlineKeyboardButton(
                    text="PROOF 😊",
                    callback_data="proof"
                ),

                InlineKeyboardButton(
                    text="SUPPORT ❤️",
                    callback_data="support"
                )
            ]
        ]
    )

    await message.answer_photo(
        photo=PHOTO_URL,
        caption=caption,
        reply_markup=keyboard
    )

# =========================
# BUTTONS
# =========================

@dp.callback_query(F.data == "unlock")
async def unlock(callback: CallbackQuery):

    await callback.message.answer(
        "💎 Payment system later add kar sakte ho."
    )

    await callback.answer()


@dp.callback_query(F.data == "demo")
async def demo(callback: CallbackQuery):

    await callback.message.answer(
        "😋 Demo links/videos later yaha add karo."
    )

    await callback.answer()


@dp.callback_query(F.data == "proof")
async def proof(callback: CallbackQuery):

    await callback.message.answer(
        "😊 Proofs later yaha add karo."
    )

    await callback.answer()


@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):

    await callback.message.answer(
        "❤️ Support username later yaha add karo."
    )

    await callback.answer()
# =========================
# ANONYMOUS CHAT
# =========================

# =========================
# ANONYMOUS CHAT
# =========================

@dp.message()
async def anonymous_chat(message: Message):

    # ignore commands
    if message.text and message.text.startswith("/"):
        return

    # OWNER REPLY SYSTEM
    if message.from_user.id == OWNER_ID:

        if message.reply_to_message:

            try:
                original_user_id = int(
                    message.reply_to_message.text.split("USER_ID: ")[1].split("\n")[0]
                )

                if message.text:
                    await bot.send_message(
                        chat_id=original_user_id,
                        text=f"📩 Anonymous Reply:\n\n{message.text}"
                    )

                else:
                    await message.copy_to(chat_id=original_user_id)

                await message.answer("✅ Reply Sent")

            except:
                pass

        return

    # USER MESSAGE TYPE
    if message.text:
        text = message.text

    elif message.photo:
        text = "📷 Photo"

    elif message.video:
        text = "🎥 Video"

    elif message.document:
        text = "📁 Document"

    elif message.audio:
        text = "🎵 Audio"

    elif message.voice:
        text = "🎤 Voice"

    elif message.sticker:
        text = "😂 Sticker"

    else:
        text = "📦 Unsupported Message"

    username = message.from_user.username or "No Username"

    owner_text = f"""
USER_ID: {message.from_user.id}

👤 @{username}

💬 Message:
{text}
"""

    await bot.send_message(
        chat_id=OWNER_ID,
        text=owner_text
    )

    await message.forward(chat_id=OWNER_ID)

@dp.message(F.text == "/users")
async def total_users(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    data = supabase.table("users").select("*").execute()

    total = len(data.data)

    await message.answer(
        f"👥 Total Users: {total}"
    )
# =========================
# MAIN
# =========================

async def main():

    keep_alive()

    await bot.delete_webhook(drop_pending_updates=True)

    print("Bot Started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
