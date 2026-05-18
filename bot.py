import asyncio
import logging
import os

from datetime import datetime
from threading import Thread
from zoneinfo import ZoneInfo
from flask import Flask
from supabase import create_client
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

demo_mode = False
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

scheduler = AsyncIOScheduler()

save_mode = False
scheduled_time = None

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

    posts = supabase.table("demo_posts").select("*").limit(5).execute().data

    if not posts:
        await callback.message.answer("❌ No demo posts available")
        await callback.answer()
        return

    for post in posts:

        try:

            if post["media_type"] == "photo":
                await bot.send_photo(
                    chat_id=callback.from_user.id,
                    photo=post["file_id"],
                    caption=post["caption"]
                )

            elif post["media_type"] == "video":
                await bot.send_video(
                    chat_id=callback.from_user.id,
                    video=post["file_id"],
                    caption=post["caption"]
                )

            elif post["media_type"] == "document":
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document=post["file_id"],
                    caption=post["caption"]
                )

        except:
            pass

    await callback.answer("📤 Demo sent")


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
# TOTAL USERS
# =========================

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
# COMMANDS
# =========================
@dp.message(F.text == "/resetdemo")
async def reset_demo(message: Message):

    global demo_mode

    if message.from_user.id != OWNER_ID:
        return

    demo_mode = False   # 🔥 THIS IS THE MISSING PART

    supabase.table("demo_posts").delete().neq("id", 0).execute()

    await message.answer("🗑 Demo cleared + Demo mode OFF")

@dp.message(F.text == "/adddemo")
async def add_demo(message: Message):

    global demo_mode

    if message.from_user.id != OWNER_ID:
        return

    demo_mode = True

    await message.answer(
        "📥 Demo mode ON\n\nAb photo/video/document bhejo, wo Supabase me save ho jayega."
    )

@dp.message(F.text == "/addpost")
async def add_post(message: Message):

    global save_mode

    if message.from_user.id != OWNER_ID:
        return

    save_mode = True

    await message.answer(
        "📥 Send Posts Now\n\nPhoto / Video / Document"
    )

# =========================
# SEND ALL
# =========================

@dp.message(F.text == "/sendall")
async def send_all(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    posts = supabase.table("post_queue").select("*").execute().data
    users = supabase.table("users").select("*").execute().data

    if not posts:
        await message.answer("❌ No Posts Found")
        return

    delivered_users = 0
    failed_users = 0

    status = await message.answer("📤 Broadcast started...")

    for user in users:

        user_id = user["user_id"]

        # ✅ OWNER SKIP (IMPORTANT)
        if user_id == OWNER_ID:
            continue

        success_for_user = False

        for post in posts:

            try:

                if post["media_type"] == "photo":
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=post["file_id"],
                        caption=post["caption"]
                    )

                elif post["media_type"] == "video":
                    await bot.send_video(
                        chat_id=user_id,
                        video=post["file_id"],
                        caption=post["caption"]
                    )

                elif post["media_type"] == "document":
                    await bot.send_document(
                        chat_id=user_id,
                        document=post["file_id"],
                        caption=post["caption"]
                    )

                success_for_user = True

                await asyncio.sleep(0.05)

            except:
                pass

        if success_for_user:
            delivered_users += 1
        else:
            failed_users += 1

    # clean posts
    supabase.table("post_queue").delete().neq("id", 0).execute()

    await status.edit_text(
        f"✅ Broadcast Done\n\n"
        f"👥 Delivered Users: {delivered_users}\n"
        f"❌ Failed Users: {failed_users}"
    )

# =========================
# SCHEDULE
# =========================

@dp.message(F.text.startswith("/schedule"))
async def schedule_post(message: Message):

    global scheduled_time

    if message.from_user.id != OWNER_ID:
        return

    try:

        scheduled_time = message.text.split(" ")[1]

        await message.answer(
            f"⏰ Scheduled For {scheduled_time}"
        )

    except:

        await message.answer(
            "Usage:\n/schedule 18:30"
        )

# =========================
# AUTO BROADCAST
# =========================

async def auto_broadcast():

    global scheduled_time

    if not scheduled_time:
        return

    current_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%H:%M")

    print(f"SCHEDULED => {scheduled_time}")
    print(f"CURRENT => {current_time}")

    if current_time != scheduled_time:
        return

    posts = supabase.table("post_queue").select("*").execute().data
    users = supabase.table("users").select("*").execute().data

    if not posts or not users:
        return

    delivered_users = 0
    failed_users = 0

    for user in users:

        user_id = user["user_id"]

        # ✅ OWNER SKIP
        if user_id == OWNER_ID:
            continue

        success_for_user = False

        for post in posts:

            try:

                if post["media_type"] == "photo":
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=post["file_id"],
                        caption=post["caption"]
                    )

                elif post["media_type"] == "video":
                    await bot.send_video(
                        chat_id=user_id,
                        video=post["file_id"],
                        caption=post["caption"]
                    )

                elif post["media_type"] == "document":
                    await bot.send_document(
                        chat_id=user_id,
                        document=post["file_id"],
                        caption=post["caption"]
                    )

                success_for_user = True

                await asyncio.sleep(0.05)

            except:
                pass

        if success_for_user:
            delivered_users += 1
        else:
            failed_users += 1

    # clean posts after successful broadcast
    supabase.table("post_queue").delete().neq("id", 0).execute()

    await bot.send_message(
        OWNER_ID,
        f"⏰ Scheduled Broadcast Done\n\n"
        f"👥 Delivered Users: {delivered_users}\n"
        f"❌ Failed Users: {failed_users}"
    )

    scheduled_time = None

# =========================
# ANONYMOUS CHAT
# =========================

@dp.message()
async def anonymous_chat(message: Message):

    global save_mode, demo_mode

    # ignore commands
    if message.text and message.text.startswith("/"):
        return

    # =========================
    # SAVE POSTS (BROADCAST)
    # =========================
    if message.from_user.id == OWNER_ID and save_mode:

        file_id = None
        media_type = None

        if message.photo:
            file_id = message.photo[-1].file_id
            media_type = "photo"

        elif message.video:
            file_id = message.video.file_id
            media_type = "video"

        elif message.document:
            file_id = message.document.file_id
            media_type = "document"

        else:
            await message.answer("❌ Send Photo / Video / Document")
            return

        supabase.table("post_queue").insert({
            "file_id": file_id,
            "caption": message.caption or "",
            "media_type": media_type
        }).execute()

        await message.answer("✅ Post Saved")

        return

    # =========================
    # SAVE DEMO POSTS (FIXED)
    # =========================
    if message.from_user.id == OWNER_ID and demo_mode:

        file_id = None
        media_type = None

        if message.photo:
            file_id = message.photo[-1].file_id
            media_type = "photo"

        elif message.video:
            file_id = message.video.file_id
            media_type = "video"

        elif message.document:
            file_id = message.document.file_id
            media_type = "document"

        else:
            await message.answer("❌ Send Photo / Video / Document")
            return

        supabase.table("demo_posts").insert({
            "file_id": file_id,
            "media_type": media_type,
            "caption": message.caption or ""
        }).execute()

        await message.answer("✅ Demo Saved")

        return

    # =========================
    # OWNER REPLY SYSTEM
    # =========================
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

    # =========================
    # USER MESSAGE TYPE
    # =========================
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
# =========================
# MAIN
# =========================

async def main():

    keep_alive()

    scheduler.add_job(
        auto_broadcast,
        "interval",
        minutes=1
    )

    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)

    print("Bot Started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
