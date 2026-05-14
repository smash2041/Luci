import asyncio
import logging
import os

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

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
# MAIN
# =========================

async def main():

    keep_alive()

    await bot.delete_webhook(drop_pending_updates=True)

    print("Bot Started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
