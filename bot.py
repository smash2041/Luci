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

# =========================
# CONFIG
# =========================

OWNER_ID = 7354394647

BOT_TOKEN = os.getenv("BOT_TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logging.basicConfig(level=logging.INFO)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

scheduler = AsyncIOScheduler(
    timezone="Asia/Kolkata"
)

# =========================
# CENTRAL BOT STATE
# =========================

BOT_STATE = {
    "mode": "normal",   # normal / demo / save
    "scheduled_time": None,
    "broadcast_running": False
}

broadcast_lock = asyncio.Lock()

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

    try:

        supabase.table("users").upsert({
            "user_id": message.from_user.id
        }).execute()

    except Exception as e:

        print(f"USER SAVE ERROR: {e}")

    caption = """
🔥 PREMIUM 18+ CONTENT 😘🔥

1. Indian Desi 📌Videos - 10000+
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

    try:

        posts = supabase.table(
            "demo_posts"
        ).select("*").limit(5).execute().data

        if not posts:

            await callback.message.answer(
                "❌ No demo posts available"
            )

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

                await asyncio.sleep(0.12)

            except Exception as e:

                print(f"DEMO SEND ERROR: {e}")

        await callback.answer(
            "📤 Demo sent"
        )

    except Exception as e:

        print(f"DEMO ERROR: {e}")

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

    try:

        data = supabase.table(
            "users"
        ).select("*").execute()

        total = len(data.data)

        await message.answer(
            f"👥 Total Users: {total}"
        )

    except Exception as e:

        await message.answer(
            f"❌ Error: {e}"
        )

# =========================
# RESET DEMO
# =========================

@dp.message(F.text == "/resetdemo")
async def reset_demo(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    try:

        posts = supabase.table(
            "demo_posts"
        ).select("*").execute().data

        for post in posts:

            supabase.table(
                "demo_posts"
            ).delete().eq(
                "id",
                post["id"]
            ).execute()

        BOT_STATE["mode"] = "normal"

        await message.answer(
            "🗑 Demo cleared + Demo mode OFF"
        )

    except Exception as e:

        await message.answer(
            f"❌ Error: {e}"
        )

# =========================
# MODE COMMANDS
# =========================

@dp.message(F.text == "/adddemo")
async def add_demo(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    BOT_STATE["mode"] = "demo"

    await message.answer(
        "📥 Demo mode ON\nAb demo posts bhejo"
    )

@dp.message(F.text == "/addpost")
async def add_post(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    BOT_STATE["mode"] = "save"

    await message.answer(
        "📥 Broadcast mode ON\nAb posts bhejo"
    )

@dp.message(F.text == "/normal")
async def normal(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    BOT_STATE["mode"] = "normal"

    BOT_STATE["scheduled_time"] = None

    await message.answer(
        "✅ Fully Normal Mode ON"
    )

# =========================
# SEND ALL
# =========================

@dp.message(F.text == "/sendall")
async def send_all(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    async with broadcast_lock:

        if BOT_STATE["broadcast_running"]:

            await message.answer(
                "⚠️ Broadcast already running"
            )

            return

        BOT_STATE["broadcast_running"] = True

        try:

            posts = supabase.table(
                "post_queue"
            ).select("*").execute().data

            users = supabase.table(
                "users"
            ).select("*").execute().data

            if not posts:

                await message.answer(
                    "❌ No Posts Found"
                )

                return

            delivered_users = 0
            failed_users = 0

            status = await message.answer(
                "📤 Broadcast started..."
            )

            for user in users:

                user_id = user["user_id"]

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

                        await asyncio.sleep(0.12)

                    except Exception as e:

                        print(
                            f"BROADCAST ERROR: {e}"
                        )

                if success_for_user:
                    delivered_users += 1
                else:
                    failed_users += 1

            # SAFE CLEANUP
            for post in posts:

                try:

                    supabase.table(
                        "post_queue"
                    ).delete().eq(
                        "id",
                        post["id"]
                    ).execute()

                except Exception as e:

                    print(
                        f"DELETE ERROR: {e}"
                    )

            BOT_STATE["mode"] = "normal"

            await status.edit_text(
                f"✅ Broadcast Done\n\n"
                f"👥 Delivered Users: {delivered_users}\n"
                f"❌ Failed Users: {failed_users}"
            )

        finally:

            BOT_STATE["broadcast_running"] = False

# =========================
# SCHEDULE
# =========================

@dp.message(F.text.startswith("/schedule"))
async def schedule_post(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    try:

        scheduled = message.text.split(" ")[1]

        hour, minute = map(
            int,
            scheduled.split(":")
        )

        if hour < 0 or hour > 23:
            raise Exception()

        if minute < 0 or minute > 59:
            raise Exception()

        BOT_STATE["scheduled_time"] = scheduled

        await message.answer(
            f"⏰ Scheduled For {scheduled}"
        )

    except:

        await message.answer(
            "Usage:\n/schedule 18:30"
        )

# =========================
# AUTO BROADCAST
# =========================

async def auto_broadcast():

    async with broadcast_lock:

        if BOT_STATE["broadcast_running"]:
            return

        BOT_STATE["broadcast_running"] = True

        try:

            scheduled = BOT_STATE["scheduled_time"]

            if not scheduled:
                return

            current_dt = datetime.now(
                ZoneInfo("Asia/Kolkata")
            )

            current_minutes = (
                current_dt.hour * 60
                + current_dt.minute
            )

            sch_hour, sch_min = map(
                int,
                scheduled.split(":")
            )

            scheduled_minutes = (
                sch_hour * 60
                + sch_min
            )

            # 1 minute tolerance
            if abs(current_minutes - scheduled_minutes) > 1:
                return

            posts = supabase.table(
                "post_queue"
            ).select("*").execute().data

            users = supabase.table(
                "users"
            ).select("*").execute().data

            if not posts:

                BOT_STATE["scheduled_time"] = None

                return

            delivered_users = 0
            failed_users = 0

            for user in users:

                user_id = user["user_id"]

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

                        await asyncio.sleep(0.12)

                    except Exception as e:

                        print(
                            f"SCHEDULE ERROR: {e}"
                        )

                if success_for_user:
                    delivered_users += 1
                else:
                    failed_users += 1

            # SAFE CLEANUP
            for post in posts:

                try:

                    supabase.table(
                        "post_queue"
                    ).delete().eq(
                        "id",
                        post["id"]
                    ).execute()

                except Exception as e:

                    print(
                        f"DELETE ERROR: {e}"
                    )

            BOT_STATE["mode"] = "normal"

            BOT_STATE["scheduled_time"] = None

            await bot.send_message(
                OWNER_ID,
                f"⏰ Scheduled Broadcast Done\n\n"
                f"👥 Delivered Users: {delivered_users}\n"
                f"❌ Failed Users: {failed_users}"
            )

        finally:

            BOT_STATE["broadcast_running"] = False

# =========================
# MAIN CHAT HANDLER
# =========================

@dp.message(~F.text.startswith("/"))
async def anonymous_chat(message: Message):

    # =========================
    # OWNER REPLY SYSTEM
    # =========================

    if (
        message.from_user.id == OWNER_ID
        and message.reply_to_message
    ):

        text = (
            message.reply_to_message.text
            or ""
        )

        if "USER_ID:" not in text:

            await message.answer(
                "❌ Invalid Reply"
            )

            return

        try:

            user_id = int(
                text.split("USER_ID:")[1]
                .split("\n")[0]
                .strip()
            )

            if message.text:

                await bot.send_message(
                    chat_id=user_id,
                    text=f"📩 Admin Reply:\n\n{message.text}"
                )

            else:

                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )

            await message.answer(
                "✅ Sent to user"
            )

        except Exception as e:

            await message.answer(
                f"❌ Failed: {e}"
            )

        return

    # =========================
    # OWNER SAVE BROADCAST POST
    # =========================

    if (
        message.from_user.id == OWNER_ID
        and BOT_STATE["mode"] == "save"
    ):

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

            await message.answer(
                "❌ Send Photo / Video / Document"
            )

            return

        try:

            supabase.table(
                "post_queue"
            ).insert({

                "file_id": file_id,
                "caption": message.caption or "",
                "media_type": media_type

            }).execute()

            await message.answer(
                "✅ Post Saved"
            )

        except Exception as e:

            await message.answer(
                f"❌ Error: {e}"
            )

        return

    # =========================
    # OWNER SAVE DEMO
    # =========================

    if (
        message.from_user.id == OWNER_ID
        and BOT_STATE["mode"] == "demo"
    ):

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

            await message.answer(
                "❌ Send Photo / Video / Document"
            )

            return

        try:

            supabase.table(
                "demo_posts"
            ).insert({

                "file_id": file_id,
                "media_type": media_type,
                "caption": message.caption or ""

            }).execute()

            await message.answer(
                "✅ Demo Saved"
            )

        except Exception as e:

            await message.answer(
                f"❌ Error: {e}"
            )

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

    username = (
        message.from_user.username
        or "No Username"
    )

    owner_text = f"""
USER_ID: {message.from_user.id}

👤 @{username}

💬 Message:
{text}
"""

    try:

        await bot.send_message(
            chat_id=OWNER_ID,
            text=owner_text
        )

        await bot.copy_message(
            chat_id=OWNER_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:

        print(f"FORWARD ERROR: {e}")

# =========================
# MAIN
# =========================

async def main():

    keep_alive()

    scheduler.add_job(
        auto_broadcast,
        "interval",
        seconds=30
    )

    scheduler.start()

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    print("Bot Started")

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
