# bot.py
import asyncio, os, re, time, html
from contextlib import suppress
from typing import Set, Tuple

from fastapi import FastAPI
import uvicorn

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

# ---------- Config ----------
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("Set BOT_TOKEN env var")

PORT = int(os.getenv("PORT", "8000"))
STARTED_AT = time.monotonic()

# ---------- Aiogram setup ----------
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ---------- Helpers ----------
MENTION_RE = re.compile(r'@([A-Za-z0-9_]{5,32})')
TME_RE = re.compile(r'(?:https?://)?(?:t\.me|telegram\.me)/([A-Za-z0-9_]{5,32}|c/\d+/\d+|\+[\w-]+)')

def secs_to_hms(s: float) -> str:
    s = int(s)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_usernames(text: str, entities) -> Set[str]:
    found: Set[str] = set()

    if entities:
        for e in entities:
            if e.type in {"mention", "text_mention", "url", "text_link"}:
                chunk = e.extract_from(text or "")
                for m in MENTION_RE.findall(chunk):
                    found.add(m)
                for m in TME_RE.findall(chunk):
                    found.add(m)

    for m in MENTION_RE.findall(text or ""):
        found.add(m)
    for m in TME_RE.findall(text or ""):
        found.add(m)

    normalized: Set[str] = set()
    for token in found:
        token = token.lstrip("@")
        if token.startswith("c/"):  # t.me/c/<num>/<msg>
            try:
                numeric = int(token.split("/")[1])
                normalized.add(f"c/{numeric}")  # special marker
            except Exception:
                pass
        elif token.startswith("+"):  # invite links can't be resolved by Bot API
            normalized.add(token)
        else:
            normalized.add(token)
    return normalized

async def try_resolve_username(u: str) -> Tuple[str, str]:
    try:
        chat = await bot.get_chat(u)
        ctype = chat.type.value if hasattr(chat.type, "value") else str(chat.type)
        title = chat.title or (f"@{chat.username}" if getattr(chat, "username", None) else "User/Chat")
        return (html.escape(title) + f" ({ctype})", str(chat.id))
    except TelegramBadRequest as e:
        return (f"@{u}", f"❌ cannot resolve: {html.escape(str(e))}")
    except Exception as e:
        return (f"@{u}", f"❌ error: {html.escape(str(e))}")

def fmt_forward_info(m: Message) -> str | None:
    if not (m.forward_from or m.forward_from_chat or m.forward_sender_name):
        return None
    lines = ["<b>Forward info</b>"]
    if m.forward_from:
        u = m.forward_from
        name = html.escape(" ".join(x for x in [u.first_name, u.last_name] if x) or "(no name)")
        username = f" @{u.username}" if u.username else ""
        lines.append(f"• From user: <code>{u.id}</code> — {name}{username}")
    if m.forward_from_chat:
        ch = m.forward_from_chat
        ctype = ch.type.value if hasattr(ch.type, "value") else str(ch.type)
        title = html.escape(ch.title or ch.username or "(no title)")
        lines.append(f"• From {ctype}: <code>{ch.id}</code> — {title}")
    if m.forward_sender_name and not m.forward_from:
        lines.append("• From: " + html.escape(m.forward_sender_name) + " (ID hidden by privacy)")
    if m.forward_from_message_id:
        lines.append(f"• Original msg id: <code>{m.forward_from_message_id}</code>")
    return "\n".join(lines)

def fmt_chat_id_block(m: Message) -> str:
    kind = m.chat.type.value if hasattr(m.chat.type, "value") else str(m.chat.type)
    bits = [f"<b>Chat</b>: <code>{m.chat.id}</code> ({kind})"]
    if m.chat.title and m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        bits.append(f"<b>Title</b>: {html.escape(m.chat.title)}")
    return "\n".join(bits)

# ---------- Handlers ----------
@router.message(F.text == "/start")
async def start_cmd(m: Message):
    me = await bot.get_me()
    await m.reply(
        "👋 Send me:\n"
        "• Any <b>forwarded</b> message (user/group/channel)\n"
        "• Any <b>@username</b> or <b>t.me/...</b> link\n\n"
        "I’ll reply with the corresponding <b>ID</b>.\n\n"
        f"Bot: <b>@{me.username}</b>"
    )

@router.message(F.text.in_({"/ping", "/status"}))
async def ping_cmd(m: Message):
    uptime = secs_to_hms(time.monotonic() - STARTED_AT)
    await m.reply(f"🏓 Pong! Uptime: <b>{uptime}</b>")

@router.message()
async def any_message(m: Message):
    pieces: list[str] = []

    # A) Forward info
    fwd = fmt_forward_info(m)
    if fwd:
        pieces.append(fwd)

    # B) Username / t.me resolver
    usernames = parse_usernames(m.text or "", m.entities)
    if usernames:
        pieces.append("<b>Resolutions</b>")
        for u in sorted(usernames):
            if u.startswith("c/"):
                num = int(u.split("/")[1])
                pieces.append(f"• t.me/c link → inferred chat_id: <code>{-100 * num}</code> (title not available via Bot API)")
            elif u.startswith("+"):
                pieces.append(f"• invite link (<code>{html.escape(u)}</code>) → cannot resolve to ID via Bot API")
            else:
                title, cid = await try_resolve_username(u)
                pieces.append(f"• {title}: <code>{cid}</code>")

    # C) Always include current chat & sender id
    pieces.append(fmt_chat_id_block(m))
    pieces.append(f"<b>Your user id</b>: <code>{m.from_user.id}</code>")

    if m.forward_sender_name and not m.forward_from:
        pieces.append("ℹ️ Sender’s ID is hidden by their forward-privacy; Telegram does not provide it to bots.")

    await m.reply("\n".join(pieces))

# ---------- FastAPI app (for uptime ping) ----------
app = FastAPI()
_bot_task: asyncio.Task | None = None

@app.get("/")
async def root():
    return {"ok": True}

@app.get("/healthz")
async def healthz():
    return {"ok": True, "uptime": secs_to_hms(time.monotonic() - STARTED_AT)}

@app.on_event("startup")
async def on_startup():
    # Start polling in the background; keep FastAPI running for /healthz
    # Limit updates to what we use (reduces bandwidth & CPU)
    allowed = dp.resolve_used_update_types()
    # Long-polling timeout keeps requests sparse & efficient
    global _bot_task
    _bot_task = asyncio.create_task(dp.start_polling(bot, allowed_updates=allowed, polling_timeout=50))

@app.on_event("shutdown")
async def on_shutdown():
    global _bot_task
    if _bot_task:
        _bot_task.cancel()
        with suppress(asyncio.CancelledError):
            await _bot_task

if __name__ == "__main__":
    # Local: python bot.py
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT)
