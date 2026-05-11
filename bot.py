from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from flask import Flask
from threading import Thread

import os
import logging

# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)

# =========================
# BOT CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =========================
# FLASK KEEP ALIVE
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# =========================
# PHOTO
# =========================

PHOTO_URL = "https://i.ibb.co/5XkMbSLp/x.jpg"

# =========================
# START COMMAND
# =========================

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):

    caption = """
🔥 PREMIUM 18+ CONTENT 🔥

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

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="UNLOCK 💎",
            callback_data="unlock"
        ),

        InlineKeyboardButton(
            text="DEMO 😋",
            callback_data="demo"
        ),

        InlineKeyboardButton(
            text="PROOF 😊",
            callback_data="proof"
        ),

        InlineKeyboardButton(
            text="SUPPORT ❤️",
            callback_data="support"
        )
    )

    await message.answer_photo(
        photo=PHOTO_URL,
        caption=caption,
        reply_markup=keyboard
    )

# =========================
# BUTTON FUNCTIONS
# =========================

@dp.callback_query_handler(lambda c: c.data == "unlock")
async def unlock_button(callback: CallbackQuery):

    await callback.message.answer(
        "💎 Payment system later yaha add kar sakte ho."
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "demo")
async def demo_button(callback: CallbackQuery):

    await callback.message.answer(
        "😋 Demo links/videos later yaha add karo."
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "proof")
async def proof_button(callback: CallbackQuery):

    await callback.message.answer(
        "😊 Payment proofs later yaha add karo."
    )

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "support")
async def support_button(callback: CallbackQuery):

    await callback.message.answer(
        "❤️ Support username later yaha add karo."
    )

    await callback.answer()

# =========================
# RUN BOT
# =========================

if __name__ == "__main__":

    keep_alive()

    print("Bot Running...")

    executor.start_polling(dp, skip_updates=True)
