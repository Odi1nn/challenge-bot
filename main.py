import os
import sqlite3
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
DB_PATH    = os.getenv("DB_PATH", "progress.db")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                date      TEXT PRIMARY KEY,
                completed INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS lives (
                id    INTEGER PRIMARY KEY DEFAULT 1,
                count INTEGER DEFAULT 3
            )
        """)
        c.execute("INSERT OR IGNORE INTO lives (id, count) VALUES (1, 3)")
        c.commit()

def get_progress() -> dict:
    with get_db() as c:
        rows = c.execute("SELECT date, completed FROM progress").fetchall()
    return {r[0]: bool(r[1]) for r in rows}

def toggle_day(date: str) -> bool:
    with get_db() as c:
        c.execute("INSERT OR IGNORE INTO progress (date, completed) VALUES (?, 0)", (date,))
        c.execute("UPDATE progress SET completed = 1 - completed WHERE date = ?", (date,))
        c.commit()
        val = c.execute("SELECT completed FROM progress WHERE date = ?", (date,)).fetchone()[0]
    return bool(val)

def get_lives() -> int:
    with get_db() as c:
        row = c.execute("SELECT count FROM lives WHERE id = 1").fetchone()
    return row[0] if row else 3

def use_life() -> int:
    with get_db() as c:
        c.execute("UPDATE lives SET count = MAX(0, count - 1) WHERE id = 1")
        c.commit()
        count = c.execute("SELECT count FROM lives WHERE id = 1").fetchone()[0]
    return count

def restore_life() -> int:
    with get_db() as c:
        c.execute("UPDATE lives SET count = MIN(3, count + 1) WHERE id = 1")
        c.commit()
        count = c.execute("SELECT count FROM lives WHERE id = 1").fetchone()[0]
    return count

# ─────────────────────────────────────────
# Telegram bot handlers
# ─────────────────────────────────────────
bot_app: Application | None = None

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "📊 Открыть трекер",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])
    await update.message.reply_text(
        "🚀 *Челлендж: Путь к iPad!*\n\n"
        "Нажми кнопку ниже, чтобы открыть трекер 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def cmd_progress(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prog  = get_progress()
    done  = sum(1 for v in prog.values() if v)
    total = 43
    lives = get_lives()
    pct   = int(done / total * 100)
    filled = done * 20 // total
    bar   = "█" * filled + "░" * (20 - filled)
    hearts = "❤️" * lives + "🖤" * (3 - lives)
    await update.message.reply_text(
        f"📊 *Прогресс челленджа*\n\n"
        f"`{bar}`\n"
        f"✅ Выполнено: *{done} / {total}* ({pct}%)\n"
        f"Жизни: {hearts}\n\n"
        f"{'🏆 Так держать, молодец!' if done > 0 else '👀 Пока ни одного дня. Начинаем!'}",
        parse_mode="Markdown"
    )

async def cmd_lives(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lives = get_lives()
    hearts = "❤️" * lives + "🖤" * (3 - lives)
    await update.message.reply_text(
        f"Жизней осталось: {hearts} (*{lives}*/3)",
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app
    init_db()
    if BOT_TOKEN:
        bot_app = Application.builder().token(BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start",    cmd_start))
        bot_app.add_handler(CommandHandler("progress", cmd_progress))
        bot_app.add_handler(CommandHandler("lives",    cmd_lives))
        await bot_app.initialize()
        log.info("✅ Bot initialized")
    else:
        log.warning("⚠️  BOT_TOKEN not set — bot disabled")
    yield
    if bot_app:
        await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

# ── Telegram webhook ──
@app.post("/webhook")
async def webhook(request: Request):
    if not bot_app:
        return JSONResponse({"ok": False, "error": "Bot not configured"}, status_code=503)
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

# ── Progress API ──
@app.get("/api/progress")
async def api_progress():
    return {"progress": get_progress(), "lives": get_lives(), "total": 43}

@app.post("/api/toggle/{date}")
async def api_toggle(date: str):
    completed = toggle_day(date)
    prog = get_progress()
    done = sum(1 for v in prog.values() if v)
    return {"date": date, "completed": completed, "done": done, "total": 43}

@app.post("/api/life/use")
async def api_use_life():
    return {"lives": use_life()}

@app.post("/api/life/restore")
async def api_restore_life():
    return {"lives": restore_life()}

# ── Serve Mini App (must be last) ──
app.mount("/", StaticFiles(directory="static", html=True), name="static")
