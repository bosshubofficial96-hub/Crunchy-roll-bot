#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       🎬 ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ ᴠ200.1 🎬  (FIXED + ENHANCED)          ║
║  ꜰᴜʟʟ ᴘʀᴏᴅᴜᴄᴛɪᴏɴ | 60+ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ | ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ | ᴄᴏᴏᴋɪᴇ ᴀᴜᴛʜ   ║
║  ʀᴇɴᴀᴍᴇ | ᴛʜᴜᴍʙɴᴀɪʟ | ᴄᴜꜱᴛᴏᴍ ᴄᴍᴅꜱ | ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ | 2ɢʙ ꜰɪʟᴇꜱ        ║
║  ꜰᴀꜱᴛ/ꜱʟᴏᴡ ǫᴜᴇᴜᴇ | ɴᴇᴡꜱ | ʀᴇꜰᴇʀʀᴀʟ | ᴄᴏʟᴏᴜʀ ʙᴜᴛᴛᴏɴꜱ | ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ  ║
║  @ꜰᴜɴɴʏᴛᴀᴍɪʟᴀɴ ꜱᴜᴘᴘᴏʀᴛ                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

FIXES APPLIED (v200.1):
  [FIX-01] Critical IndentationError — all module-level code was indented 2 extra
           spaces (lines 39-232 in original). Fixed to proper module scope.
  [FIX-02] Missing CrunchyBot.run() method — __main__ called bot.run() which did
           not exist, causing AttributeError on every startup.
  [FIX-03] Em.UNBAN missing — cmd_unban referenced Em.UNBAN but it was never
           declared in the Em class. Added.
  [FIX-04] Missing admin panel callback branches — adm_broadcast_menu, adm_premium,
           adm_settings, adm_cmds, adm_auth, adm_news, adm_logs all silently fell
           through to the unknown-callback logger. Implemented properly.
  [FIX-05] get_user_by_ref_code() missing in Database — cmd_start called it,
           causing AttributeError for every /start with a referral link.
  [FIX-06] Fragile build_app monkey-patch chain — replaced with a single clean
           build_app that registers all handlers in one place.
  [FIX-07] Welcome image never sent — /start had no photo support.
           Admin can now set a welcome image via /setwelcomeimage.
  [FIX-08] Config.SUBSCRIPTION_FEATURES used sc() before sc() was guaranteed
           to be importable — moved sc() definition above Config class.
  [FIX-09] Several bare except: clauses swallowed all exceptions silently —
           narrowed to Exception where safe.

ENHANCEMENTS (v200.1):
  [NEW-01] 60+ colour-coded inline buttons across all menus
  [NEW-02] Custom welcome image support with /setwelcomeimage (admin)
  [NEW-03] Rich admin panel with 20+ action buttons, colour badges, live stats
  [NEW-04] /welcomepreview command so admin can preview welcome screen
  [NEW-05] Button colour system — 4 colour themes per button category
  [NEW-06] Admin quick-action row: maintenance toggle, clear queue, vacuum DB
  [NEW-07] /botinfo command showing all bot stats at a glance
"""

import asyncio
import json
import logging
import logging.handlers
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
import shutil
import hashlib
import secrets
import random
import string
import textwrap
import traceback
import zipfile
import io
import http.cookiejar
import pickle
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# ─────────────────────────── TELEGRAM IMPORTS ────────────────────────────────
try:
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup,
        LabeledPrice, BotCommand, InputFile, InputMediaPhoto,
        ReplyKeyboardMarkup, KeyboardButton, ChatPermissions,
        MessageEntity
    )
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, MessageHandler,
        filters, ContextTypes, PreCheckoutQueryHandler, ConversationHandler,
        JobQueue, InlineQueryHandler
    )
    from telegram.constants import ParseMode, ChatType
    from telegram.error import TelegramError, BadRequest, RetryAfter, Forbidden
    import telegram
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install 'python-telegram-bot[job-queue]'")
    sys.exit(1)

# ─────────────────────────── MT-PROTO (2GB) ──────────────────────────────────
try:
    from pyrogram import Client as PyroClient
    from pyrogram.enums import ParseMode as PyroParseMode
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False

# ─────────────────────────── AIOHTTP (downloads) ─────────────────────────────
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# ─────────────────────────── LOGGING ─────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            "logs/bot.log", maxBytes=10_485_760, backupCount=5, encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1: ꜱᴍᴀʟʟ ᴄᴀᴘꜱ ᴄᴏɴᴠᴇʀᴛᴇʀ
# ══════════════════════════════════════════════════════════════════════════════

_SC_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)

def sc(text: str) -> str:
    """Convert text to ꜱᴍᴀʟʟ ᴄᴀᴘꜱ unicode font."""
    return text.lower().translate(_SC_MAP)

def SC(text: str) -> str:
    """Convert text to ꜱᴍᴀʟʟ ᴄᴀᴘꜱ preserving numbers/symbols."""
    result = []
    for ch in text:
        if ch.isalpha():
            result.append(ch.lower().translate(_SC_MAP))
        else:
            result.append(ch)
    return "".join(result)

def escape_html(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024**2):.2f} MB"
    return f"{size_bytes / (1024**3):.2f} GB"

def format_duration_human(seconds: int) -> str:
    seconds = int(seconds or 0)
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"

def safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        return default

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2: ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ
# ══════════════════════════════════════════════════════════════════════════════

class Config:
    """ᴍᴀꜱᴛᴇʀ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ — ᴀʟʟ ᴠᴀʟᴜᴇꜱ ꜰʀᴏᴍ ᴇɴᴠ ᴠᴀʀꜱ"""

    BOT_TOKEN        = os.getenv("BOT_TOKEN", "8320812013:AAG_IhbQE1e1ax6uZaSWZrbWo5A3sYYUg5Y")
    ADMIN_IDS        = [int(x) for x in os.getenv("ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
    SUPER_ADMIN_IDS  = [int(x) for x in os.getenv("SUPER_ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
    MOD_IDS          = [int(x) for x in os.getenv("MOD_IDS", "8525952693").split(",") if x.strip().isdigit()]
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@funnytamilan")
    SUPPORT_CHANNEL  = os.getenv("SUPPORT_CHANNEL", "https://t.me/funnytamilan")

    # ── MTProto ───────────────────────────────────────────────────────────────
    API_ID           = int(os.getenv("API_ID", "27806628") or "0")
    API_HASH         = os.getenv("API_HASH", "25d88301e886b82826a525b7cf52e090")
    USE_MT_PROTO     = os.getenv("USE_MT_PROTO", "False").lower() == "true"

    # ── Auth Group / Force-sub ─────────────────────────────────────────────
    AUTH_GROUP_ID    = int(os.getenv("AUTH_GROUP_ID", "0") or "0")
    AUTH_GROUP_LINK  = os.getenv("AUTH_GROUP_LINK", "")
    AUTH_CHANNEL_ID  = int(os.getenv("AUTH_CHANNEL_ID", "0") or "0")
    AUTH_CHANNEL_LINK= os.getenv("AUTH_CHANNEL_LINK", "")
    FORCE_SUB_ENABLED= os.getenv("FORCE_SUB_ENABLED", "False").lower() == "true"

    # ── Crunchyroll ────────────────────────────────────────────────────────
    CR_EMAIL         = os.getenv("CR_EMAIL", "Namtran.mov@gmail.com")
    CR_PASSWORD      = os.getenv("CR_PASSWORD", "AUnime$Figs2015%")
    CR_PREMIUM_ACCOUNT = os.getenv("CR_PREMIUM_ACCOUNT", "False").lower() == "true"

    # ── Subscription ──────────────────────────────────────────────────────
    SUBSCRIPTION_PRICES  = {"weekly": 20, "monthly": 50, "yearly": 500, "lifetime": 1500}
    SUBSCRIPTION_DAYS    = {"weekly": 7,  "monthly": 30, "yearly": 365, "lifetime": 36500}
    SUBSCRIPTION_FEATURES = {
        "weekly":   ["720p/1080p", "50 downloads/day", "queue priority", "subtitles"],
        "monthly":  ["4K", "200 downloads/day", "batch download", "custom thumbnail"],
        "yearly":   ["4K/HDR", "unlimited", "all features", "watermark", "trim/compress"],
        "lifetime": ["all features", "vip support", "custom emoji", "gift premium", "early access"],
    }

    # ── Limits ────────────────────────────────────────────────────────────
    FREE_DAILY_LIMIT     = int(os.getenv("FREE_DAILY_LIMIT", "3"))
    PREMIUM_DAILY_LIMIT  = int(os.getenv("PREMIUM_DAILY_LIMIT", "999999"))
    MAX_CONCURRENT       = int(os.getenv("MAX_CONCURRENT", "5"))
    PREMIUM_CONCURRENT   = int(os.getenv("PREMIUM_CONCURRENT", "10"))
    MAX_QUEUE_PER_USER   = int(os.getenv("MAX_QUEUE_PER_USER", "10"))
    MAX_BATCH_SIZE       = int(os.getenv("MAX_BATCH_SIZE", "20"))
    MAX_FILE_SIZE_MB     = int(os.getenv("MAX_FILE_SIZE_MB", "2000"))
    DOWNLOAD_TIMEOUT     = int(os.getenv("DOWNLOAD_TIMEOUT", "3600"))
    FREE_DOWNLOAD_DELAY  = int(os.getenv("FREE_DOWNLOAD_DELAY", "30"))

    # ── Quality ───────────────────────────────────────────────────────────
    QUALITIES = {
        "144p":  {"height": 144,  "bitrate": "200k",   "crf": 32, "audio": "64k"},
        "240p":  {"height": 240,  "bitrate": "400k",   "crf": 30, "audio": "96k"},
        "360p":  {"height": 360,  "bitrate": "800k",   "crf": 28, "audio": "128k"},
        "480p":  {"height": 480,  "bitrate": "1200k",  "crf": 26, "audio": "128k"},
        "720p":  {"height": 720,  "bitrate": "2500k",  "crf": 23, "audio": "192k"},
        "1080p": {"height": 1080, "bitrate": "5000k",  "crf": 20, "audio": "256k"},
        "4K":    {"height": 2160, "bitrate": "16000k", "crf": 18, "audio": "320k"},
        "HDR":   {"height": 1080, "bitrate": "8000k",  "crf": 17, "audio": "320k", "hdr": True},
    }
    PREMIUM_QUALITIES  = ["1080p", "4K", "HDR"]
    DEFAULT_QUALITY    = "720p"

    # ── Encode ────────────────────────────────────────────────────────────
    ENCODE_PRESETS = {
        "ultrafast": {"preset": "ultrafast", "tune": "zerolatency"},
        "fast":      {"preset": "veryfast",  "tune": "film"},
        "balanced":  {"preset": "medium",    "tune": "film"},
        "high":      {"preset": "slow",      "tune": "film"},
        "master":    {"preset": "veryslow",  "tune": "film"},
        "anime":     {"preset": "slow",      "tune": "animation"},
        "hevc":      {"preset": "medium",    "tune": "film", "codec": "libx265"},
        "av1":       {"preset": "6",         "tune": "",     "codec": "libaom-av1"},
    }
    DEFAULT_ENCODE = "balanced"

    # ── Paths ─────────────────────────────────────────────────────────────
    BASE_DIR      = Path(__file__).parent.absolute()
    DOWNLOAD_PATH = BASE_DIR / "downloads"
    OUTPUT_PATH   = BASE_DIR / "output"
    DATA_PATH     = BASE_DIR / "data"
    LOG_PATH      = BASE_DIR / "logs"
    THUMB_PATH    = BASE_DIR / "thumbnails"
    ENCODE_PATH   = BASE_DIR / "encode"
    TEMP_PATH     = BASE_DIR / "temp"
    COOKIES_PATH  = BASE_DIR / "cookies"

    DATABASE_PATH = DATA_PATH / "crunchyroll_bot.db"
    COOKIES_FILE  = COOKIES_PATH / "cr_cookies.pkl"
    COOKIES_JSON  = COOKIES_PATH / "cr_cookies.json"

    # ── FFmpeg ────────────────────────────────────────────────────────────
    FFMPEG_PATH  = shutil.which("ffmpeg")  or "/usr/bin/ffmpeg"
    FFPROBE_PATH = shutil.which("ffprobe") or "/usr/bin/ffprobe"
    YTDLP_PATH   = shutil.which("yt-dlp")  or shutil.which("yt_dlp") or "yt-dlp"

    # ── Referral ──────────────────────────────────────────────────────────
    REFERRAL_REWARD   = int(os.getenv("REFERRAL_REWARD", "50"))
    REFERRAL_REQUIRED = int(os.getenv("REFERRAL_REQUIRED", "5"))

    # ── Channels ──────────────────────────────────────────────────────────
    LOG_CHANNEL    = int(os.getenv("LOG_CHANNEL", "0") or "0")
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "")
    NEWS_CHANNEL   = os.getenv("NEWS_CHANNEL", "")

    @classmethod
    def create_dirs(cls):
        for p in [cls.DOWNLOAD_PATH, cls.OUTPUT_PATH, cls.DATA_PATH,
                  cls.LOG_PATH, cls.THUMB_PATH, cls.ENCODE_PATH,
                  cls.TEMP_PATH, cls.COOKIES_PATH]:
            p.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        if cls.BOT_TOKEN in ("YOUR_BOT_TOKEN_HERE", ""):
            logger.error("❌ BOT_TOKEN not set! Set BOT_TOKEN environment variable.")
            return False
        return True

Config.create_dirs()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3: ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ ꜱʏꜱᴛᴇᴍ
# ══════════════════════════════════════════════════════════════════════════════

class PremiumEmoji:
    REGISTRY: Dict[str, Tuple[str, str]] = {
        "success":     ("5368324170671202286", "✅"),
        "error":       ("5210952531676504517", "❌"),
        "warning":     ("5373123633494116952", "⚠️"),
        "loading":     ("5307954949981078657", "⏳"),
        "info":        ("5395444784611480792", "ℹ️"),
        "anime":       ("5368324170671202286", "🎬"),
        "episode":     ("5307954949981078657", "📺"),
        "quality":     ("5373123633494116952", "🎨"),
        "encode":      ("5395444784611480792", "⚙️"),
        "subtitle":    ("5368324170671202286", "📝"),
        "audio":       ("5307954949981078657", "🎤"),
        "video":       ("5373123633494116952", "🎥"),
        "thumbnail":   ("5395444784611480792", "🖼️"),
        "rename":      ("5368324170671202286", "✏️"),
        "premium":     ("5368324170671202286", "💎"),
        "vip":         ("5373123633494116952", "👑"),
        "crown":       ("5307954949981078657", "👑"),
        "fire":        ("5395444784611480792", "🔥"),
        "star":        ("5368324170671202286", "⭐"),
        "rocket":      ("5307954949981078657", "🚀"),
        "download":    ("5373123633494116952", "📥"),
        "upload":      ("5395444784611480792", "📤"),
        "stats":       ("5368324170671202286", "📊"),
        "settings":    ("5307954949981078657", "⚙️"),
        "queue":       ("5373123633494116952", "📋"),
        "ban":         ("5395444784611480792", "🚫"),
        "unban":       ("5368324170671202286", "✅"),
        "gift":        ("5307954949981078657", "🎁"),
        "redeem":      ("5373123633494116952", "🎟️"),
        "news":        ("5395444784611480792", "📰"),
        "fast":        ("5368324170671202286", "⚡"),
        "slow":        ("5307954949981078657", "🐢"),
        "referral":    ("5373123633494116952", "👥"),
        "cookie":      ("5395444784611480792", "🍪"),
        "back":        ("5368324170671202286", "◀️"),
        "next":        ("5307954949981078657", "▶️"),
        "close":       ("5373123633494116952", "✖️"),
        "refresh":     ("5395444784611480792", "🔄"),
        "history":     ("5368324170671202286", "📜"),
        "broadcast":   ("5307954949981078657", "📢"),
        "schedule":    ("5373123633494116952", "🕐"),
        "heart":       ("5395444784611480792", "❤️"),
        "watch":       ("5368324170671202286", "👀"),
        "lead":        ("5307954949981078657", "🏆"),
        "code":        ("5373123633494116952", "💻"),
        "auth":        ("5395444784611480792", "🔐"),
        "log":         ("5368324170671202286", "📝"),
        "admin":       ("5307954949981078657", "👨‍💼"),
        "support":     ("5373123633494116952", "🆘"),
        "paid":        ("5395444784611480792", "💳"),
        "progress":    ("5368324170671202286", "📈"),
        "image":       ("5395444784611480792", "🖼️"),
        "palette":     ("5368324170671202286", "🎨"),
        "bell":        ("5307954949981078657", "🔔"),
        "lock":        ("5373123633494116952", "🔒"),
        "unlock":      ("5395444784611480792", "🔓"),
        "users":       ("5368324170671202286", "👥"),
        "tools":       ("5307954949981078657", "🔧"),
        "trash":       ("5373123633494116952", "🗑️"),
        "pin":         ("5395444784611480792", "📌"),
        "chart":       ("5368324170671202286", "📉"),
        "diamond":     ("5307954949981078657", "💠"),
        "shield":      ("5373123633494116952", "🛡️"),
        "key":         ("5395444784611480792", "🗝️"),
        "globe":       ("5368324170671202286", "🌐"),
        "mail":        ("5307954949981078657", "📧"),
        "phone":       ("5373123633494116952", "📱"),
    }

    USE_CUSTOM = os.getenv("USE_PREMIUM_EMOJI", "True").lower() == "true"

    @classmethod
    def get(cls, name: str, html: bool = True) -> str:
        entry = cls.REGISTRY.get(name, ("", "❓"))
        emoji_id, fallback = entry
        if cls.USE_CUSTOM and emoji_id:
            if html:
                return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
        return fallback

    @classmethod
    def build(cls, *names, html: bool = True) -> str:
        return "".join(cls.get(n, html) for n in names)

# ── Short aliases ─────────────────────────────────────────────────────────────
class Em:
    SUCCESS   = PremiumEmoji.get("success")
    ERROR     = PremiumEmoji.get("error")
    WARNING   = PremiumEmoji.get("warning")
    LOADING   = PremiumEmoji.get("loading")
    INFO      = PremiumEmoji.get("info")
    ANIME     = PremiumEmoji.get("anime")
    EPISODE   = PremiumEmoji.get("episode")
    QUALITY   = PremiumEmoji.get("quality")
    ENCODE    = PremiumEmoji.get("encode")
    SUBTITLE  = PremiumEmoji.get("subtitle")
    AUDIO     = PremiumEmoji.get("audio")
    VIDEO     = PremiumEmoji.get("video")
    THUMBNAIL = PremiumEmoji.get("thumbnail")
    RENAME    = PremiumEmoji.get("rename")
    PREMIUM   = PremiumEmoji.get("premium")
    VIP       = PremiumEmoji.get("vip")
    CROWN     = PremiumEmoji.get("crown")
    FIRE      = PremiumEmoji.get("fire")
    STAR      = PremiumEmoji.get("star")
    ROCKET    = PremiumEmoji.get("rocket")
    DOWNLOAD  = PremiumEmoji.get("download")
    UPLOAD    = PremiumEmoji.get("upload")
    STATS     = PremiumEmoji.get("stats")
    SETTINGS  = PremiumEmoji.get("settings")
    QUEUE     = PremiumEmoji.get("queue")
    BAN       = PremiumEmoji.get("ban")
    UNBAN     = PremiumEmoji.get("unban")   # FIX-03: was missing
    GIFT      = PremiumEmoji.get("gift")
    REDEEM    = PremiumEmoji.get("redeem")
    NEWS      = PremiumEmoji.get("news")
    FAST      = PremiumEmoji.get("fast")
    SLOW      = PremiumEmoji.get("slow")
    REFERRAL  = PremiumEmoji.get("referral")
    COOKIE    = PremiumEmoji.get("cookie")
    BACK      = PremiumEmoji.get("back")
    NEXT      = PremiumEmoji.get("next")
    CLOSE     = PremiumEmoji.get("close")
    REFRESH   = PremiumEmoji.get("refresh")
    HISTORY   = PremiumEmoji.get("history")
    BROADCAST = PremiumEmoji.get("broadcast")
    SCHEDULE  = PremiumEmoji.get("schedule")
    HEART     = PremiumEmoji.get("heart")
    WATCH     = PremiumEmoji.get("watch")
    LEAD      = PremiumEmoji.get("lead")
    CODE      = PremiumEmoji.get("code")
    AUTH      = PremiumEmoji.get("auth")
    LOG       = PremiumEmoji.get("log")
    ADMIN     = PremiumEmoji.get("admin")
    SUPPORT   = PremiumEmoji.get("support")
    PAID      = PremiumEmoji.get("paid")
    PROGRESS  = PremiumEmoji.get("progress")
    IMAGE     = PremiumEmoji.get("image")
    PALETTE   = PremiumEmoji.get("palette")
    BELL      = PremiumEmoji.get("bell")
    LOCK      = PremiumEmoji.get("lock")
    UNLOCK    = PremiumEmoji.get("unlock")
    USERS     = PremiumEmoji.get("users")
    TOOLS     = PremiumEmoji.get("tools")
    TRASH     = PremiumEmoji.get("trash")
    PIN       = PremiumEmoji.get("pin")
    CHART     = PremiumEmoji.get("chart")
    DIAMOND   = PremiumEmoji.get("diamond")
    SHIELD    = PremiumEmoji.get("shield")
    KEY       = PremiumEmoji.get("key")
    GLOBE     = PremiumEmoji.get("globe")
    MAIL      = PremiumEmoji.get("mail")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4: ᴅᴀᴛᴀʙᴀꜱᴇ
# ══════════════════════════════════════════════════════════════════════════════

class Database:
    """ꜱǫʟɪᴛᴇ ᴅᴀᴛᴀʙᴀꜱᴇ — ᴏᴡɴ ꜱᴛᴏʀᴇ ꜰᴏʀ ᴀʟʟ ʙᴏᴛ ᴅᴀᴛᴀ"""

    def __init__(self):
        self.path = Config.DATABASE_PATH
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._init_schema()

    def _connect(self):
        self.conn = sqlite3.connect(
            str(self.path), check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA cache_size=-8192")

    def _init_schema(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id         INTEGER PRIMARY KEY,
                username        TEXT,
                first_name      TEXT,
                last_name       TEXT,
                is_admin        INTEGER DEFAULT 0,
                is_banned       INTEGER DEFAULT 0,
                banned_reason   TEXT,
                banned_until    TEXT,
                warnings        INTEGER DEFAULT 0,
                premium_type    TEXT    DEFAULT 'free',
                premium_expiry  TEXT,
                stars_balance   INTEGER DEFAULT 0,
                daily_downloads INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                total_size      INTEGER DEFAULT 0,
                last_reset      TEXT    DEFAULT '',
                last_active     TEXT    DEFAULT CURRENT_TIMESTAMP,
                joined_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
                default_quality TEXT    DEFAULT '720p',
                encode_preset   TEXT    DEFAULT 'balanced',
                language        TEXT    DEFAULT 'en',
                notify_complete INTEGER DEFAULT 1,
                custom_thumb    TEXT,
                referral_code   TEXT    UNIQUE,
                referred_by     INTEGER,
                referral_count  INTEGER DEFAULT 0,
                referral_points INTEGER DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS queue (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                url             TEXT,
                quality         TEXT,
                encode_preset   TEXT    DEFAULT 'balanced',
                priority        INTEGER DEFAULT 0,
                status          TEXT    DEFAULT 'pending',
                progress        INTEGER DEFAULT 0,
                message_id      INTEGER,
                chat_id         INTEGER,
                file_path       TEXT,
                error_message   TEXT,
                is_fast         INTEGER DEFAULT 0,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP,
                started_at      TEXT,
                completed_at    TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS download_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                url             TEXT,
                quality         TEXT,
                file_name       TEXT,
                file_size       INTEGER DEFAULT 0,
                duration        INTEGER DEFAULT 0,
                status          TEXT    DEFAULT 'completed',
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS settings (
                key     TEXT PRIMARY KEY,
                value   TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS scheduled (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                url             TEXT,
                quality         TEXT,
                encode_preset   TEXT    DEFAULT 'balanced',
                run_at          TEXT,
                status          TEXT    DEFAULT 'pending',
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS custom_commands (
                command     TEXT PRIMARY KEY,
                response    TEXT,
                code        TEXT,
                cmd_type    TEXT DEFAULT 'text',
                created_by  INTEGER,
                usage_count INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS redeem_codes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT UNIQUE,
                plan_type   TEXT,
                days        INTEGER,
                max_uses    INTEGER DEFAULT 1,
                used_count  INTEGER DEFAULT 0,
                created_by  INTEGER,
                expires_at  TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS redeem_log (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                code    TEXT,
                user_id INTEGER,
                used_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS auth_groups (
                group_id    INTEGER PRIMARY KEY,
                group_name  TEXT,
                group_link  TEXT,
                added_by    INTEGER,
                is_required INTEGER DEFAULT 1,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS gifts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user   INTEGER,
                to_user     INTEGER,
                plan_type   TEXT,
                days        INTEGER,
                message     TEXT,
                gift_code   TEXT UNIQUE,
                claimed     INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS favorites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                anime_title TEXT,
                anime_id    TEXT,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, anime_id)
            )""",
            """CREATE TABLE IF NOT EXISTS watchlist (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                anime_title TEXT,
                anime_id    TEXT,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, anime_id)
            )""",
            """CREATE TABLE IF NOT EXISTS cookies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                service     TEXT DEFAULT 'crunchyroll',
                cookie_data BLOB,
                cookies_json TEXT,
                email       TEXT,
                is_premium  INTEGER DEFAULT 0,
                is_valid    INTEGER DEFAULT 1,
                expires_at  TEXT,
                added_by    INTEGER,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_cookies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                service     TEXT DEFAULT 'crunchyroll',
                cookie_data BLOB,
                cookies_json TEXT,
                is_valid    INTEGER DEFAULT 1,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, service)
            )""",
            """CREATE TABLE IF NOT EXISTS cr_news (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                description TEXT,
                url         TEXT UNIQUE,
                image_url   TEXT,
                published_at TEXT,
                notified    INTEGER DEFAULT 0,
                saved_at    TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS rate_limits (
                user_id      INTEGER PRIMARY KEY,
                requests     INTEGER DEFAULT 0,
                window_start TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS feedback (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                rating      INTEGER,
                message     TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS achievements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                achievement TEXT,
                awarded_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS premium_transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                plan_type   TEXT,
                days        INTEGER,
                payment_ref TEXT,
                added_by    INTEGER,
                added_at    TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
        ]
        for sql in tables:
            self.conn.execute(sql)
        self.conn.commit()
        self._migrate()

    def _migrate(self):
        """Add missing columns without breaking existing DBs."""
        safe_cols = [
            ("users", "trial_used", "INTEGER DEFAULT 0"),
            ("users", "stars_balance", "INTEGER DEFAULT 0"),
        ]
        for table, col, coldef in safe_cols:
            try:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coldef}")
                self.conn.commit()
            except Exception:
                pass

    # ──── ᴜꜱᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ──────────────────────────────────────────────────

    def register_user(self, uid: int, username: str = None,
                      first_name: str = None, last_name: str = None,
                      referred_by: int = None):
        self.conn.execute(
            "INSERT OR IGNORE INTO users(user_id,username,first_name,last_name,referred_by) "
            "VALUES(?,?,?,?,?)",
            (uid, username, first_name, last_name, referred_by))
        self.conn.execute(
            "UPDATE users SET username=?,first_name=?,last_name=?,last_active=CURRENT_TIMESTAMP "
            "WHERE user_id=?",
            (username, first_name, last_name, uid))
        if referred_by:
            self.conn.execute(
                "UPDATE users SET referral_count=referral_count+1,"
                "referral_points=referral_points+? WHERE user_id=?",
                (Config.REFERRAL_REWARD, referred_by))
        self.conn.commit()

    def get_user(self, uid: int) -> Optional[Dict]:
        c = self.conn.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return dict(r) if r else None

    # FIX-05: missing method that cmd_start relied on
    def get_user_by_ref_code(self, code: str) -> Optional[int]:
        """Return user_id for a given referral code, or None."""
        c = self.conn.execute(
            "SELECT user_id FROM users WHERE referral_code=?", (code.upper(),))
        r = c.fetchone()
        return r[0] if r else None

    def get_user_count(self) -> Dict:
        total   = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        premium = self.conn.execute(
            "SELECT COUNT(*) FROM users WHERE premium_type!='free' AND "
            "(premium_expiry IS NULL OR premium_expiry>CURRENT_TIMESTAMP)").fetchone()[0]
        banned  = self.conn.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
        free    = total - premium
        return {"total": total, "premium": premium, "free": free, "banned": banned}

    def get_all_users(self, premium_only: bool = False) -> List[int]:
        if premium_only:
            c = self.conn.execute(
                "SELECT user_id FROM users WHERE premium_type!='free' AND is_banned=0 "
                "AND (premium_expiry IS NULL OR premium_expiry>CURRENT_TIMESTAMP)")
        else:
            c = self.conn.execute("SELECT user_id FROM users WHERE is_banned=0")
        return [r[0] for r in c.fetchall()]

    def is_admin(self, uid: int) -> bool:
        return uid in Config.ADMIN_IDS or uid in Config.SUPER_ADMIN_IDS

    def is_premium(self, uid: int) -> bool:
        if uid in Config.ADMIN_IDS:
            return True
        c = self.conn.execute(
            "SELECT premium_type,premium_expiry FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if not r or r[0] == "free":
            return False
        if r[1] is None:
            return True
        try:
            return datetime.fromisoformat(r[1]) > datetime.now()
        except Exception:
            return False

    def is_banned(self, uid: int) -> bool:
        c = self.conn.execute(
            "SELECT is_banned,banned_until FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if not r or not r[0]:
            return False
        if r[1]:
            try:
                if datetime.fromisoformat(r[1]) < datetime.now():
                    self.conn.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,))
                    self.conn.commit()
                    return False
            except Exception:
                pass
        return True

    def ban_user(self, uid: int, by: int, reason: str = "", days: int = 0):
        until = (datetime.now() + timedelta(days=days)).isoformat() if days else None
        self.conn.execute(
            "UPDATE users SET is_banned=1,banned_reason=?,banned_until=? WHERE user_id=?",
            (reason, until, uid))
        self.conn.commit()

    def unban_user(self, uid: int):
        self.conn.execute(
            "UPDATE users SET is_banned=0,banned_reason=NULL,banned_until=NULL WHERE user_id=?",
            (uid,))
        self.conn.commit()

    def add_warning(self, uid: int) -> int:
        self.conn.execute(
            "UPDATE users SET warnings=warnings+1 WHERE user_id=?", (uid,))
        self.conn.commit()
        c = self.conn.execute("SELECT warnings FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return r[0] if r else 0

    def add_premium(self, uid: int, plan: str, days: int,
                    payment_ref: str = "", added_by: int = 0) -> bool:
        try:
            expiry = (datetime.now() + timedelta(days=days)).isoformat()
            self.conn.execute(
                "UPDATE users SET premium_type=?,premium_expiry=? WHERE user_id=?",
                (plan, expiry, uid))
            self.conn.execute(
                "INSERT INTO premium_transactions(user_id,plan_type,days,payment_ref,added_by) "
                "VALUES(?,?,?,?,?)",
                (uid, plan, days, payment_ref, added_by))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"add_premium: {e}")
            return False

    def revoke_premium(self, uid: int) -> bool:
        try:
            self.conn.execute(
                "UPDATE users SET premium_type='free',premium_expiry=NULL WHERE user_id=?",
                (uid,))
            self.conn.commit()
            return True
        except Exception:
            return False

    def set_user_setting(self, uid: int, key: str, value: str):
        allowed = {"default_quality", "encode_preset", "language",
                   "notify_complete", "custom_thumb"}
        if key not in allowed:
            return
        self.conn.execute(f"UPDATE users SET {key}=? WHERE user_id=?", (value, uid))
        self.conn.commit()

    def check_daily_limit(self, uid: int) -> Tuple[bool, int, int]:
        today = datetime.now().strftime("%Y-%m-%d")
        c = self.conn.execute(
            "SELECT daily_downloads,last_reset FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if not r:
            return True, 0, Config.FREE_DAILY_LIMIT
        count, last = r[0], r[1] or ""
        if last != today:
            self.conn.execute(
                "UPDATE users SET daily_downloads=0,last_reset=? WHERE user_id=?",
                (today, uid))
            self.conn.commit()
            count = 0
        limit = Config.PREMIUM_DAILY_LIMIT if self.is_premium(uid) else Config.FREE_DAILY_LIMIT
        return count < limit, count, limit

    def increment_downloads(self, uid: int, file_size: int = 0):
        today = datetime.now().strftime("%Y-%m-%d")
        self.conn.execute(
            "UPDATE users SET daily_downloads=daily_downloads+1,"
            "total_downloads=total_downloads+1,"
            f"total_size=total_size+{file_size},"
            "last_reset=? WHERE user_id=?",
            (today, uid))
        self.conn.commit()

    # ──── ǫᴜᴇᴜᴇ ─────────────────────────────────────────────────────────────

    def add_to_queue(self, uid: int, url: str, quality: str,
                     preset: str = "balanced", msg_id: int = 0,
                     chat_id: int = 0) -> int:
        is_fast = 1 if self.is_premium(uid) else 0
        priority = 10 if is_fast else 0
        c = self.conn.execute(
            "INSERT INTO queue(user_id,url,quality,encode_preset,priority,is_fast,"
            "message_id,chat_id) VALUES(?,?,?,?,?,?,?,?)",
            (uid, url, quality, preset, priority, is_fast, msg_id, chat_id))
        self.conn.commit()
        return c.lastrowid

    def get_next_queue_item(self, fast_lane: bool = False) -> Optional[Dict]:
        where = "is_fast=1" if fast_lane else "is_fast=0"
        c = self.conn.execute(
            f"SELECT * FROM queue WHERE status='pending' AND {where} "
            "ORDER BY priority DESC, created_at ASC LIMIT 1")
        r = c.fetchone()
        return dict(r) if r else None

    def get_queue_position(self, qid: int) -> int:
        c = self.conn.execute(
            "SELECT COUNT(*) FROM queue WHERE status='pending' AND "
            "created_at<=(SELECT created_at FROM queue WHERE id=?)", (qid,))
        r = c.fetchone()
        return r[0] if r else 1

    def start_processing(self, qid: int):
        self.conn.execute(
            "UPDATE queue SET status='processing',started_at=CURRENT_TIMESTAMP WHERE id=?",
            (qid,))
        self.conn.commit()

    def complete_queue_item(self, qid: int, file_path: str = ""):
        self.conn.execute(
            "UPDATE queue SET status='completed',progress=100,"
            "file_path=?,completed_at=CURRENT_TIMESTAMP WHERE id=?",
            (file_path, qid))
        self.conn.commit()

    def fail_queue_item(self, qid: int, error: str = ""):
        self.conn.execute(
            "UPDATE queue SET status='failed',error_message=?,"
            "completed_at=CURRENT_TIMESTAMP WHERE id=?",
            (error[:500], qid))
        self.conn.commit()

    def cancel_queue_item(self, qid: int, uid: int) -> bool:
        c = self.conn.execute(
            "UPDATE queue SET status='cancelled' WHERE id=? AND user_id=? "
            "AND status='pending'",
            (qid, uid))
        self.conn.commit()
        return c.rowcount > 0

    def update_queue_progress(self, qid: int, pct: int):
        self.conn.execute(
            "UPDATE queue SET progress=? WHERE id=?", (pct, qid))
        self.conn.commit()

    def get_user_queue(self, uid: int) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM queue WHERE user_id=? AND status IN "
            "('pending','processing') ORDER BY created_at ASC",
            (uid,))
        return [dict(r) for r in c.fetchall()]

    def get_all_queue(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM queue WHERE status IN ('pending','processing') "
            "ORDER BY priority DESC, created_at ASC")
        return [dict(r) for r in c.fetchall()]

    def clear_queue(self):
        self.conn.execute(
            "UPDATE queue SET status='cancelled' WHERE status='pending'")
        self.conn.commit()

    def get_user_history(self, uid: int, limit: int = 10) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM queue WHERE user_id=? AND status IN "
            "('completed','failed') ORDER BY completed_at DESC LIMIT ?",
            (uid, limit))
        return [dict(r) for r in c.fetchall()]

    # ──── ꜱᴇᴛᴛɪɴɢꜱ ──────────────────────────────────────────────────────────

    def get_setting(self, key: str, default: str = "") -> str:
        c = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        r = c.fetchone()
        return r[0] if r else default

    def set_setting(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
        self.conn.commit()

    # ──── ꜱᴄʜᴇᴅᴜʟᴇᴅ ────────────────────────────────────────────────────────

    def schedule_download(self, uid: int, url: str, quality: str,
                          preset: str, run_at: str) -> int:
        c = self.conn.execute(
            "INSERT INTO scheduled(user_id,url,quality,encode_preset,run_at) VALUES(?,?,?,?,?)",
            (uid, url, quality, preset, run_at))
        self.conn.commit()
        return c.lastrowid

    def get_pending_scheduled(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM scheduled WHERE status='pending' AND run_at<=CURRENT_TIMESTAMP")
        return [dict(r) for r in c.fetchall()]

    def mark_scheduled_done(self, sid: int):
        self.conn.execute(
            "UPDATE scheduled SET status='queued' WHERE id=?", (sid,))
        self.conn.commit()

    # ──── ᴄᴜꜱᴛᴏᴍ ᴄᴏᴍᴍᴀɴᴅꜱ ──────────────────────────────────────────────────

    def add_custom_cmd(self, cmd: str, response: str, code: str,
                       cmd_type: str, created_by: int) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO custom_commands(command,response,code,cmd_type,created_by) "
                "VALUES(?,?,?,?,?)",
                (cmd, response, code, cmd_type, created_by))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_custom_cmd(self, cmd: str, response: str,
                          code: str, cmd_type: str) -> bool:
        c = self.conn.execute(
            "UPDATE custom_commands SET response=?,code=?,cmd_type=? WHERE command=?",
            (response, code, cmd_type, cmd))
        self.conn.commit()
        return c.rowcount > 0

    def remove_custom_cmd(self, cmd: str) -> bool:
        c = self.conn.execute(
            "DELETE FROM custom_commands WHERE command=?", (cmd,))
        self.conn.commit()
        return c.rowcount > 0

    def get_custom_cmd(self, cmd: str) -> Optional[Dict]:
        c = self.conn.execute(
            "SELECT * FROM custom_commands WHERE command=?", (cmd,))
        r = c.fetchone()
        if r:
            self.conn.execute(
                "UPDATE custom_commands SET usage_count=usage_count+1 WHERE command=?",
                (cmd,))
            self.conn.commit()
            d = dict(r)
            d["type"] = d.pop("cmd_type", "text")
            return d
        return None

    def list_custom_cmds(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT command,cmd_type,usage_count,created_at FROM custom_commands "
            "ORDER BY usage_count DESC")
        return [dict(r) for r in c.fetchall()]

    # ──── ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ ──────────────────────────────────────────────────────

    def create_redeem_code(self, code: str, plan: str, days: int,
                           max_uses: int, created_by: int,
                           exp_days: int) -> bool:
        try:
            expires = (datetime.now() + timedelta(days=exp_days)).isoformat()
            self.conn.execute(
                "INSERT INTO redeem_codes(code,plan_type,days,max_uses,created_by,expires_at) "
                "VALUES(?,?,?,?,?,?)",
                (code, plan, days, max_uses, created_by, expires))
            self.conn.commit()
            return True
        except Exception:
            return False

    def use_redeem_code(self, code: str, uid: int) -> Tuple[bool, str, Optional[str], int]:
        c = self.conn.execute(
            "SELECT * FROM redeem_codes WHERE code=?", (code.upper(),))
        r = c.fetchone()
        if not r:
            return False, sc("invalid code"), None, 0
        r = dict(r)
        if r["expires_at"]:
            try:
                if datetime.fromisoformat(r["expires_at"]) < datetime.now():
                    return False, sc("code has expired"), None, 0
            except Exception:
                pass
        if r["used_count"] >= r["max_uses"]:
            return False, sc("code already used maximum times"), None, 0
        used = self.conn.execute(
            "SELECT 1 FROM redeem_log WHERE code=? AND user_id=?",
            (code.upper(), uid)).fetchone()
        if used:
            return False, sc("you already used this code"), None, 0
        self.conn.execute(
            "UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?",
            (code.upper(),))
        self.conn.execute(
            "INSERT INTO redeem_log(code,user_id) VALUES(?,?)",
            (code.upper(), uid))
        self.conn.commit()
        return True, "ok", r["plan_type"], r["days"]

    # ──── ᴀᴜᴛʜ ɢʀᴏᴜᴘꜱ ───────────────────────────────────────────────────────

    def add_auth_group(self, gid: int, name: str, link: str, added_by: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO auth_groups(group_id,group_name,group_link,added_by) "
            "VALUES(?,?,?,?)", (gid, name, link, added_by))
        self.conn.commit()

    def remove_auth_group(self, gid: int):
        self.conn.execute("DELETE FROM auth_groups WHERE group_id=?", (gid,))
        self.conn.commit()

    def get_auth_groups(self) -> List[Dict]:
        c = self.conn.execute("SELECT * FROM auth_groups WHERE is_required=1")
        return [dict(r) for r in c.fetchall()]

    # ──── ɢɪꜰᴛꜱ ──────────────────────────────────────────────────────────────

    def create_gift(self, from_user: int, to_user: int, plan: str,
                    days: int, message: str = "") -> str:
        code = secrets.token_hex(6).upper()
        self.conn.execute(
            "INSERT INTO gifts(from_user,to_user,plan_type,days,message,gift_code) "
            "VALUES(?,?,?,?,?,?)",
            (from_user, to_user, plan, days, message, code))
        self.conn.commit()
        return code

    def claim_gift(self, code: str, uid: int) -> Tuple[bool, str, Optional[str], int]:
        c = self.conn.execute(
            "SELECT * FROM gifts WHERE gift_code=?", (code.upper(),))
        r = c.fetchone()
        if not r:
            return False, sc("invalid gift code"), None, 0
        r = dict(r)
        if r["claimed"]:
            return False, sc("gift already claimed"), None, 0
        if r["to_user"] and r["to_user"] != uid:
            return False, sc("this gift is not for you"), None, 0
        self.conn.execute(
            "UPDATE gifts SET claimed=1 WHERE gift_code=?", (code.upper(),))
        self.conn.commit()
        return True, "ok", r["plan_type"], r["days"]

    # ──── ʀᴇꜰᴇʀʀᴀʟꜱ ──────────────────────────────────────────────────────────

    def get_referral_code(self, uid: int) -> str:
        c = self.conn.execute(
            "SELECT referral_code FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if r and r[0]:
            return r[0]
        code = secrets.token_hex(4).upper()
        self.conn.execute(
            "UPDATE users SET referral_code=? WHERE user_id=?", (code, uid))
        self.conn.commit()
        return code

    def get_referral_count(self, uid: int) -> int:
        c = self.conn.execute(
            "SELECT referral_count FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return r[0] if r else 0

    def get_referral_points(self, uid: int) -> int:
        c = self.conn.execute(
            "SELECT referral_points FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return r[0] if r else 0

    def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        c = self.conn.execute(
            "SELECT user_id,first_name,referral_count,referral_points FROM users "
            "WHERE is_banned=0 ORDER BY referral_count DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]

    # ──── ꜰᴀᴠᴏᴜʀɪᴛᴇꜱ / ᴡᴀᴛᴄʜʟɪꜱᴛ ──────────────────────────────────────────

    def add_favorite(self, uid: int, title: str, anime_id: str) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO favorites(user_id,anime_title,anime_id) VALUES(?,?,?)",
                (uid, title, anime_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_favorites(self, uid: int) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM favorites WHERE user_id=? ORDER BY added_at DESC",
            (uid,))
        return [dict(r) for r in c.fetchall()]

    def add_watchlist(self, uid: int, title: str, anime_id: str) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO watchlist(user_id,anime_title,anime_id) VALUES(?,?,?)",
                (uid, title, anime_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_watchlist(self, uid: int) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM watchlist WHERE user_id=? ORDER BY added_at DESC",
            (uid,))
        return [dict(r) for r in c.fetchall()]

    # ──── ᴄᴏᴏᴋɪᴇꜱ ────────────────────────────────────────────────────────────

    def save_cookies(self, cookie_data: bytes, cookies_json: str,
                     email: str = "", is_premium: bool = False,
                     added_by: int = 0, expires_days: int = 30) -> int:
        expires = (datetime.now() + timedelta(days=expires_days)).isoformat()
        self.conn.execute(
            "UPDATE cookies SET is_valid=0 WHERE service='crunchyroll'")
        c = self.conn.execute(
            "INSERT INTO cookies(service,cookie_data,cookies_json,email,is_premium,is_valid,"
            "expires_at,added_by) VALUES('crunchyroll',?,?,?,?,1,?,?)",
            (cookie_data, cookies_json, email, int(is_premium), expires, added_by))
        self.conn.commit()
        return c.lastrowid

    def get_active_cookies(self) -> Optional[Dict]:
        c = self.conn.execute(
            "SELECT * FROM cookies WHERE service='crunchyroll' AND is_valid=1 "
            "AND (expires_at IS NULL OR expires_at>CURRENT_TIMESTAMP) "
            "ORDER BY added_at DESC LIMIT 1")
        r = c.fetchone()
        return dict(r) if r else None

    def save_user_cookies(self, uid: int, cookie_data: bytes,
                          cookies_json: str) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO user_cookies(user_id,cookie_data,cookies_json) VALUES(?,?,?) "
                "ON CONFLICT(user_id,service) DO UPDATE SET "
                "cookie_data=excluded.cookie_data,cookies_json=excluded.cookies_json,"
                "added_at=CURRENT_TIMESTAMP",
                (uid, cookie_data, cookies_json))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_user_cookies(self, uid: int) -> Optional[Dict]:
        c = self.conn.execute(
            "SELECT * FROM user_cookies WHERE user_id=? AND is_valid=1", (uid,))
        r = c.fetchone()
        return dict(r) if r else None

    def invalidate_cookies(self):
        self.conn.execute(
            "UPDATE cookies SET is_valid=0 WHERE service='crunchyroll'")
        self.conn.commit()

    # ──── ɴᴇᴡꜱ ───────────────────────────────────────────────────────────────

    def save_news(self, title: str, description: str, url: str,
                  image_url: str, published_at: str) -> bool:
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO cr_news(title,description,url,image_url,published_at) "
                "VALUES(?,?,?,?,?)",
                (title, description, url, image_url, published_at))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_latest_news(self, limit: int = 5) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM cr_news ORDER BY published_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]

    def get_unnotified_news(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM cr_news WHERE notified=0 ORDER BY published_at DESC")
        return [dict(r) for r in c.fetchall()]

    def mark_news_notified(self, news_id: int):
        self.conn.execute(
            "UPDATE cr_news SET notified=1 WHERE id=?", (news_id,))
        self.conn.commit()

    # ──── ʀᴀᴛᴇ ʟɪᴍɪᴛ ─────────────────────────────────────────────────────────

    def check_rate_limit(self, uid: int) -> bool:
        if self.get_setting("rate_limit_enabled", "True") != "True":
            return True
        if self.is_admin(uid):
            return True
        max_req = int(self.get_setting("rate_limit_requests", "30"))
        window  = int(self.get_setting("rate_limit_window", "60"))
        c = self.conn.execute(
            "SELECT requests,window_start FROM rate_limits WHERE user_id=?", (uid,))
        r = c.fetchone()
        now = datetime.now()
        if not r:
            self.conn.execute(
                "INSERT INTO rate_limits(user_id,requests,window_start) VALUES(?,1,?)",
                (uid, now.isoformat()))
            self.conn.commit()
            return True
        requests, window_start = r[0], r[1]
        try:
            ws = datetime.fromisoformat(window_start)
        except Exception:
            ws = now - timedelta(seconds=window + 1)
        if (now - ws).total_seconds() > window:
            self.conn.execute(
                "UPDATE rate_limits SET requests=1,window_start=? WHERE user_id=?",
                (now.isoformat(), uid))
            self.conn.commit()
            return True
        if requests >= max_req:
            return False
        self.conn.execute(
            "UPDATE rate_limits SET requests=requests+1 WHERE user_id=?", (uid,))
        self.conn.commit()
        return True

    # ──── ꜰᴇᴇᴅʙᴀᴄᴋ ──────────────────────────────────────────────────────────

    def add_feedback(self, uid: int, rating: int, message: str):
        self.conn.execute(
            "INSERT INTO feedback(user_id,rating,message) VALUES(?,?,?)",
            (uid, rating, message))
        self.conn.commit()

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        c = self.conn.execute(
            "SELECT user_id,first_name,total_downloads,total_size FROM users "
            "WHERE is_banned=0 ORDER BY total_downloads DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5: ᴘʀᴏɢʀᴇꜱꜱ ʙᴀʀ + ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ
# ══════════════════════════════════════════════════════════════════════════════

class ProgressBar:
    @staticmethod
    def make(pct: int, length: int = 12) -> str:
        pct    = max(0, min(100, pct))
        filled = int(length * pct / 100)
        bar    = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {pct}%"


class VideoTools:
    @staticmethod
    def build_filename(series: str, season: int, ep: int,
                       title: str, quality: str, preset: str) -> str:
        safe       = re.sub(r'[^\w\s\-]', '', series)[:40].strip()
        safe_title = re.sub(r'[^\w\s\-]', '', title)[:30].strip()
        return f"{safe}.S{season:02d}E{ep:02d}.{safe_title}.{quality}.{preset}.mp4"

    @staticmethod
    async def generate_thumbnail(video_path: str) -> Optional[str]:
        if not Path(video_path).exists():
            return None
        timestamps = ["00:00:05", "00:00:10", "00:00:15", "00:00:03"]
        out = str(Config.THUMB_PATH / f"{Path(video_path).stem}_thumb.jpg")
        for t in timestamps:
            cmd = [Config.FFMPEG_PATH, "-y", "-i", video_path, "-ss", t,
                   "-vframes", "1",
                   "-vf", "scale=1280:720:force_original_aspect_ratio=decrease",
                   "-q:v", "2", out]
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stderr=asyncio.subprocess.DEVNULL)
                await asyncio.wait_for(proc.wait(), timeout=30)
                if Path(out).exists() and Path(out).stat().st_size > 1000:
                    return out
            except asyncio.TimeoutError:
                pass
        return None

    @staticmethod
    async def embed_thumbnail(video_path: str, thumb_path: str) -> Optional[str]:
        if not Path(video_path).exists() or not Path(thumb_path).exists():
            return None
        out = str(Config.TEMP_PATH / f"{Path(video_path).stem}_t.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", video_path,
            "-i", thumb_path, "-map", "0", "-map", "1",
            "-c", "copy", "-disposition:1", "attached_pic", out,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=120)
            if proc.returncode == 0 and Path(out).exists():
                return out
        except asyncio.TimeoutError:
            pass
        return None

    @staticmethod
    async def encode_video(input_path: str, quality: str, preset_name: str,
                           progress_cb=None) -> Optional[str]:
        q_cfg   = Config.QUALITIES.get(quality, Config.QUALITIES["720p"])
        pre_cfg = Config.ENCODE_PRESETS.get(preset_name, Config.ENCODE_PRESETS["balanced"])
        codec   = pre_cfg.get("codec", "libx264")
        out     = str(Config.ENCODE_PATH / f"{Path(input_path).stem}_{quality}_{preset_name}.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", input_path,
            "-c:v", codec, "-preset", pre_cfg["preset"],
            "-crf", str(q_cfg["crf"]),
            "-vf", f"scale=-2:{q_cfg['height']}",
            "-c:a", "aac", "-b:a", q_cfg["audio"],
            "-movflags", "+faststart", "-progress", "pipe:1", out,
        ]
        if pre_cfg.get("tune"):
            cmd.extend(["-tune", pre_cfg["tune"]])
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL)
            duration_secs = None
            async for line in proc.stdout:
                line = line.decode("utf-8", errors="ignore").strip()
                if line.startswith("out_time_ms="):
                    try:
                        out_ms = int(line.split("=")[1])
                        if duration_secs and duration_secs > 0 and progress_cb:
                            pct = min(99, int(out_ms / 1_000_000 / duration_secs * 100))
                            await progress_cb(pct)
                    except Exception:
                        pass
            await proc.wait()
            if proc.returncode == 0 and Path(out).exists():
                if progress_cb:
                    await progress_cb(100)
                return out
        except Exception as e:
            logger.error(f"encode_video: {e}")
        return None

    @staticmethod
    async def trim_video(input_path: str, start: str, end: str) -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_trim.mp4")
        cmd = [Config.FFMPEG_PATH, "-y", "-i", input_path,
               "-ss", start, "-to", end, "-c", "copy", out]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=300)
            return out if proc.returncode == 0 and Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def compress_video(input_path: str, target_mb: int) -> Optional[str]:
        size = Path(input_path).stat().st_size / (1024 * 1024)
        if size <= target_mb:
            return input_path
        info      = await VideoTools.get_media_info(input_path)
        dur       = float(info.get("raw_duration", 60))
        target_bps = int(target_mb * 8 * 1024 * 1024 / dur)
        audio_bps  = 128_000
        video_bps  = max(target_bps - audio_bps, 100_000)
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_compressed.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", input_path,
            "-c:v", "libx264", "-b:v", str(video_bps),
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", out,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=600)
            return out if proc.returncode == 0 and Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def extract_audio(input_path: str, fmt: str = "mp3") -> Optional[str]:
        out   = str(Config.TEMP_PATH / f"{Path(input_path).stem}_audio.{fmt}")
        codec = "libmp3lame" if fmt == "mp3" else "aac"
        cmd   = [Config.FFMPEG_PATH, "-y", "-i", input_path,
                 "-vn", "-c:a", codec, out]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=300)
            return out if proc.returncode == 0 and Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def screenshot_video(input_path: str,
                               timestamp: str = "00:00:05") -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_shot.jpg")
        cmd = [Config.FFMPEG_PATH, "-y", "-i", input_path,
               "-ss", timestamp, "-vframes", "1", out]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=60)
            return out if Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def make_gif(input_path: str, start: str = "00:00:00",
                       duration: int = 5, scale: int = 320) -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}.gif")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", input_path,
            "-ss", start, "-t", str(duration),
            "-vf", f"scale={scale}:-1:flags=lanczos,fps=12", out,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=120)
            return out if proc.returncode == 0 and Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def add_watermark(input_path: str, text: str,
                            position: str = "bottomright") -> Optional[str]:
        positions = {
            "topleft":     "10:10",
            "topright":    "W-tw-10:10",
            "bottomleft":  "10:H-th-10",
            "bottomright": "W-tw-10:H-th-10",
            "center":      "(W-tw)/2:(H-th)/2",
        }
        pos       = positions.get(position, positions["bottomright"])
        safe_text = re.sub(r"[:'\\]", "", text)
        out       = str(Config.TEMP_PATH / f"{Path(input_path).stem}_wm.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", input_path,
            "-vf",
            f"drawtext=text='{safe_text}':fontcolor=white:fontsize=24:"
            f"box=1:boxcolor=black@0.5:x={pos}",
            "-codec:a", "copy", out,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=600)
            return out if proc.returncode == 0 and Path(out).exists() else None
        except Exception:
            return None

    @staticmethod
    async def get_media_info(fp: str) -> Dict:
        cmd = [
            Config.FFPROBE_PATH, "-v", "error",
            "-print_format", "json",
            "-show_format", "-show_streams", fp,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL)
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            data   = json.loads(out.decode("utf-8", errors="ignore"))
            fmt    = data.get("format", {})
            streams = data.get("streams", [])
            video  = next((s for s in streams if s.get("codec_type") == "video"), {})
            audio  = next((s for s in streams if s.get("codec_type") == "audio"), {})
            dur    = float(fmt.get("duration", 0))
            return {
                "duration":     format_duration_human(int(dur)),
                "raw_duration": dur,
                "size":         format_file_size(int(fmt.get("size", 0))),
                "bitrate":      f"{int(fmt.get('bit_rate', 0)) // 1000} kbps",
                "video_codec":  video.get("codec_name", "?"),
                "resolution":   f"{video.get('width','?')}x{video.get('height','?')}",
                "fps":          video.get("r_frame_rate", "?"),
                "audio_codec":  audio.get("codec_name", "?"),
                "channels":     audio.get("channels", "?"),
                "sample_rate":  audio.get("sample_rate", "?"),
            }
        except Exception as e:
            logger.error(f"get_media_info: {e}")
            return {}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6: ᴄᴏᴏᴋɪᴇ ᴍᴀɴᴀɢᴇʀ
# ══════════════════════════════════════════════════════════════════════════════

class CookieManager:
    @staticmethod
    async def validate_cookies(raw: str) -> Tuple[bool, str]:
        raw = raw.strip()
        if raw.startswith("["):
            try:
                cookies = json.loads(raw)
                if isinstance(cookies, list) and cookies:
                    return True, json.dumps(cookies)
                return False, sc("empty cookie list")
            except json.JSONDecodeError as e:
                return False, f"JSON parse error: {e}"
        if "# Netscape HTTP Cookie File" in raw or "\t" in raw:
            lines = [l for l in raw.splitlines()
                     if l.strip() and not l.startswith("#")]
            cookies = []
            for line in lines:
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies.append({
                        "domain": parts[0], "path": parts[2],
                        "secure": parts[3].upper() == "TRUE",
                        "expires": int(parts[4]) if parts[4].isdigit() else 0,
                        "name":   parts[5], "value": parts[6],
                    })
            if cookies:
                return True, json.dumps(cookies)
            return False, sc("could not parse netscape cookies")
        return False, sc("unrecognised cookie format")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7: ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ
# ══════════════════════════════════════════════════════════════════════════════

class CrunchyrollClient:
    CR_DOMAINS = ("crunchyroll.com", "www.crunchyroll.com", "beta.crunchyroll.com")

    def is_valid_url(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            return any(d in parsed.netloc for d in self.CR_DOMAINS)
        except Exception:
            return False

    async def fetch_cr_news(self) -> List[Dict]:
        if not AIOHTTP_AVAILABLE:
            return []
        feeds = [
            "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss",
            "https://www.crunchyroll.com/feed",
        ]
        for feed in feeds:
            try:
                async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=15)) as session:
                    async with session.get(feed) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            items = re.findall(
                                r'<item>(.*?)</item>', text, re.DOTALL)
                            results = []
                            for item in items[:10]:
                                title = re.search(
                                    r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                                link  = re.search(r'<link>(.*?)</link>', item)
                                desc  = re.search(
                                    r'<description><!\[CDATA\[(.*?)\]\]></description>',
                                    item, re.DOTALL)
                                pub   = re.search(r'<pubDate>(.*?)</pubDate>', item)
                                img   = re.search(
                                    r'<media:content[^>]+url="([^"]+)"', item)
                                if title and link:
                                    results.append({
                                        "title":        title.group(1).strip(),
                                        "url":          link.group(1).strip(),
                                        "description":  (desc.group(1)[:300]
                                                         if desc else ""),
                                        "published_at": (pub.group(1)
                                                         if pub else ""),
                                        "image_url":    (img.group(1)
                                                         if img else ""),
                                    })
                            if results:
                                return results
            except Exception as e:
                logger.warning(f"fetch_cr_news from {feed}: {e}")
        return []

    async def get_video_info(self, url: str,
                             cookies_json: str = "") -> Optional[Dict]:
        cmd = [
            Config.YTDLP_PATH,
            "--dump-json",
            "--no-warnings",
        ]
        if cookies_json:
            try:
                cj_path = str(Config.TEMP_PATH / "yt_cookies.json")
                Path(cj_path).write_text(cookies_json, encoding="utf-8")
                cmd.extend(["--cookies", cj_path])
            except Exception:
                pass
        cmd.append(url)
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL)
            out, _ = await asyncio.wait_for(
                proc.communicate(), timeout=60)
            if proc.returncode == 0 and out:
                return json.loads(out.decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.warning(f"get_video_info: {e}")
        return None

    async def download(self, url: str, quality: str,
                       output_dir: str,
                       cookies_json: str = "",
                       progress_cb=None) -> Optional[str]:
        q_cfg  = Config.QUALITIES.get(quality, Config.QUALITIES["720p"])
        height = q_cfg["height"]
        fname  = str(Path(output_dir) / f"cr_{uuid.uuid4().hex[:8]}.%(ext)s")
        cmd    = [
            Config.YTDLP_PATH,
            "-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "--merge-output-format", "mp4",
            "--no-warnings",
            "-o", fname,
        ]
        if cookies_json:
            try:
                cj_path = str(Config.TEMP_PATH / "yt_cookies_dl.json")
                Path(cj_path).write_text(cookies_json, encoding="utf-8")
                cmd.extend(["--cookies", cj_path])
            except Exception:
                pass
        if progress_cb:
            cmd.extend(["--newline"])
        cmd.append(url)
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            async for line in proc.stdout:
                line = line.decode("utf-8", errors="ignore").strip()
                m = re.search(r'(\d+\.?\d*)%', line)
                if m and progress_cb:
                    try:
                        await progress_cb(min(98, int(float(m.group(1)))))
                    except Exception:
                        pass
            await asyncio.wait_for(proc.wait(), timeout=Config.DOWNLOAD_TIMEOUT)
            if proc.returncode == 0:
                # find the downloaded file
                for f in sorted(Path(output_dir).glob("cr_*.mp4"),
                                 key=lambda x: x.stat().st_mtime, reverse=True):
                    return str(f)
        except Exception as e:
            logger.error(f"download: {e}")
        return None


class DownloadManager:
    def __init__(self, db: "Database"):
        self.db = db
        self.cr = CrunchyrollClient()

    async def process(self, qid: int, uid: int, url: str,
                      quality: str, preset: str,
                      progress_cb=None) -> Tuple[bool, str]:
        try:
            cookies_row = self.db.get_active_cookies()
            cookies_json = ""
            if cookies_row:
                cookies_json = cookies_row.get("cookies_json", "")
            out_dir = str(Config.OUTPUT_PATH)

            async def dl_cb(pct):
                if progress_cb:
                    await progress_cb(pct, sc("downloading"))

            file_path = await self.cr.download(
                url, quality, out_dir, cookies_json, dl_cb)
            if not file_path or not Path(file_path).exists():
                self.db.fail_queue_item(qid, "download failed")
                return False, sc("download failed or file not found")

            if preset != "balanced":
                async def enc_cb(pct):
                    if progress_cb:
                        await progress_cb(pct, sc("encoding"))
                encoded = await VideoTools.encode_video(
                    file_path, quality, preset, enc_cb)
                if encoded and Path(encoded).exists():
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                    file_path = encoded

            self.db.complete_queue_item(qid, file_path)
            self.db.increment_downloads(uid, Path(file_path).stat().st_size)
            return True, file_path

        except Exception as e:
            logger.exception(f"DownloadManager.process: {e}")
            self.db.fail_queue_item(qid, str(e))
            return False, str(e)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8: ᴄᴏᴅᴇ ꜱᴀɴᴅʙᴏx
# ══════════════════════════════════════════════════════════════════════════════

class CodeSandbox:
    BANNED = ["import os", "import sys", "import subprocess",
              "open(", "exec(", "__import__", "eval("]

    @classmethod
    def run(cls, code: str, ctx_vars: Dict) -> Tuple[bool, str]:
        for b in cls.BANNED:
            if b in code:
                return False, f"❌ {sc('forbidden')} : {b}"
        try:
            output = io.StringIO()
            globs  = {"__builtins__": {"print": lambda *a: output.write(" ".join(map(str, a)) + "\n"),
                                       "len": len, "str": str, "int": int,
                                       "float": float, "list": list, "dict": dict}}
            globs.update(ctx_vars)
            exec(compile(code, "<custom_cmd>", "exec"), globs)
            return True, output.getvalue() or f"✅ {sc('code executed (no output)')}"
        except Exception as e:
            return False, f"❌ {sc('error')}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 9: ᴀᴜᴛʜ ᴄʜᴇᴄᴋᴇʀ
# ══════════════════════════════════════════════════════════════════════════════

class AuthChecker:
    @staticmethod
    async def check_user(bot, uid: int, db: Database) -> Tuple[bool, List[str]]:
        if db.get_setting("force_sub_enabled", "False") != "True":
            return True, []
        groups   = db.get_auth_groups()
        required = []
        for g in groups:
            try:
                member = await bot.get_chat_member(g["group_id"], uid)
                if member.status in ("left", "kicked", "banned"):
                    required.append(g.get("group_link", ""))
            except Exception as e:
                logger.warning(f"AuthChecker: {e}")
                required.append(g.get("group_link", ""))
        return len(required) == 0, required


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 10: ᴅᴇᴄᴏʀᴀᴛᴏʀꜱ
# ══════════════════════════════════════════════════════════════════════════════

def admin_only(func):
    @wraps(func)
    async def wrapper(self_or_update, update_or_ctx=None, ctx=None):
        if isinstance(self_or_update, Update):
            update = self_or_update
            ctx    = update_or_ctx
            self   = None
        else:
            self   = self_or_update
            update = update_or_ctx
        uid = update.effective_user.id if update.effective_user else 0
        if uid not in Config.ADMIN_IDS and uid not in Config.SUPER_ADMIN_IDS:
            msg = update.effective_message
            if msg:
                try:
                    await msg.reply_text(
                        f"{Em.BAN} {sc('admin only command')}.",
                        parse_mode=ParseMode.HTML)
                except Exception:
                    pass
            return
        if self:
            return await func(self, update, ctx)
        return await func(update, ctx)
    return wrapper


def mod_only(func):
    @wraps(func)
    async def wrapper(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else 0
        if uid not in Config.ADMIN_IDS and uid not in Config.MOD_IDS:
            msg = update.effective_message
            if msg:
                try:
                    await msg.reply_text(
                        f"{Em.BAN} {sc('moderator only command')}.",
                        parse_mode=ParseMode.HTML)
                except Exception:
                    pass
            return
        return await func(self, update, ctx)
    return wrapper


def premium_only(func):
    @wraps(func)
    async def wrapper(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else 0
        if not self.db.is_premium(uid):
            msg = update.effective_message
            if msg:
                try:
                    await msg.reply_text(
                        f"{Em.PREMIUM} {sc('this feature requires premium membership')}.\n"
                        f"{sc('use')} /premium {sc('to upgrade')}.",
                        parse_mode=ParseMode.HTML)
                except Exception:
                    pass
            return
        return await func(self, update, ctx)
    return wrapper


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 11: ɪɴʟɪɴᴇ ᴋᴇʏʙᴏᴀʀᴅ ꜰᴀᴄᴛᴏʀʏ  (60+ ᴄᴏʟᴏᴜʀ ʙᴜᴛᴛᴏɴꜱ)
# ══════════════════════════════════════════════════════════════════════════════

# Colour badge helpers — these prepend a coloured circle to every button label
# so the Telegram inline keyboard has a colour-coded "theme" per panel.
def _btn(label: str, cb: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=cb)

def _url_btn(label: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, url=url)


class KB:
    """ᴄᴇɴᴛʀᴀʟɪᴢᴇᴅ ɪɴʟɪɴᴇ ᴋᴇʏʙᴏᴀʀᴅ ꜰᴀᴄᴛᴏʀʏ — 60+ ᴄᴏʟᴏᴜʀ-ᴄᴏᴅᴇᴅ ʙᴜᴛᴛᴏɴꜱ"""

    # ─── main home ───────────────────────────────────────────────────────────
    @staticmethod
    def home() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"📥 {sc('download')}",    "show_download"),
             _btn(f"💎 {sc('premium')}",     "show_premium")],
            [_btn(f"📊 {sc('my stats')}",    "show_stats"),
             _btn(f"⚙️ {sc('settings')}",   "show_settings")],
            [_btn(f"📋 {sc('queue')}",       "show_queue"),
             _btn(f"📜 {sc('history')}",     "show_history")],
            [_btn(f"📰 {sc('cr news')}",     "show_news"),
             _btn(f"👥 {sc('referral')}",    "show_referral")],
            [_btn(f"❤️ {sc('favorites')}",  "show_favorites"),
             _btn(f"👀 {sc('watchlist')}",   "show_watchlist")],
            [_btn(f"🔍 {sc('search anime')}", "show_search"),
             _btn(f"🏆 {sc('leaderboard')}", "show_leaderboard")],
            [_btn(f"🎟️ {sc('redeem code')}", "show_redeem"),
             _btn(f"🎁 {sc('gift')}",        "show_gift")],
            [_url_btn(f"🆘 {sc('support')} {Config.SUPPORT_USERNAME}",
                      Config.SUPPORT_CHANNEL)],
        ])

    # ─── download menu ────────────────────────────────────────────────────────
    @staticmethod
    def download_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("🟢 " + sc("single episode"),  "dl_single"),
             _btn("🔵 " + sc("batch download"),  "dl_batch")],
            [_btn("🟡 " + sc("schedule later"),  "dl_schedule"),
             _btn("🟠 " + sc("my queue"),        "show_queue")],
            [_btn("◀️ " + sc("back"),             "show_home")],
        ])

    # ─── quality picker ───────────────────────────────────────────────────────
    @staticmethod
    def quality(is_premium: bool) -> InlineKeyboardMarkup:
        colours = ["🟢", "🟡", "🟠", "🔴", "🔵", "💜", "⚫", "🟤"]
        rows    = []
        quals   = list(Config.QUALITIES.keys())
        for i in range(0, len(quals), 3):
            row = []
            for j, q in enumerate(quals[i:i+3]):
                locked = q in Config.PREMIUM_QUALITIES and not is_premium
                c      = colours[(i + j) % len(colours)]
                label  = f"🔒 {q}" if locked else f"{c} {q}"
                row.append(_btn(label, f"set_quality_{q}"))
            rows.append(row)
        rows.append([_btn(f"◀️ {sc('back')}", "show_settings")])
        return InlineKeyboardMarkup(rows)

    # ─── encode preset picker ─────────────────────────────────────────────────
    @staticmethod
    def encode_preset() -> InlineKeyboardMarkup:
        icons    = ["🟢", "🔵", "🟡", "🟠", "🔴", "🟣", "⚫", "🔷"]
        presets  = list(Config.ENCODE_PRESETS.keys())
        rows     = []
        for i in range(0, len(presets), 3):
            row = [_btn(f"{icons[i+j % len(icons)]} {p}",
                        f"set_preset_{p}")
                   for j, p in enumerate(presets[i:i+3])]
            rows.append(row)
        rows.append([_btn(f"◀️ {sc('back')}", "show_settings")])
        return InlineKeyboardMarkup(rows)

    # ─── premium plans ────────────────────────────────────────────────────────
    @staticmethod
    def premium_plans() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"⭐ {sc('weekly')} — {Config.SUBSCRIPTION_PRICES['weekly']} {sc('stars')}",
                  "buy_weekly")],
            [_btn(f"💎 {sc('monthly')} — {Config.SUBSCRIPTION_PRICES['monthly']} {sc('stars')}",
                  "buy_monthly")],
            [_btn(f"👑 {sc('yearly')} — {Config.SUBSCRIPTION_PRICES['yearly']} {sc('stars')}",
                  "buy_yearly")],
            [_btn(f"🔥 {sc('lifetime')} — {Config.SUBSCRIPTION_PRICES['lifetime']} {sc('stars')}",
                  "buy_lifetime")],
            [_btn(f"🎟️ {sc('redeem code')}",              "show_redeem"),
             _btn(f"🎁 {sc('claim gift')}",                "show_claimgift")],
            [_url_btn(f"💬 {sc('buy via')} {Config.SUPPORT_USERNAME}",
                      Config.SUPPORT_CHANNEL)],
            [_btn(f"◀️ {sc('back')}", "show_home")],
        ])

    # ─── download options ─────────────────────────────────────────────────────
    @staticmethod
    def download_options(queue_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"📝 {sc('subtitles')}",  f"dl_sub_{queue_id}"),
             _btn(f"🎤 {sc('audio only')}", f"dl_audio_{queue_id}")],
            [_btn(f"🖼️ {sc('thumbnail')}",  f"dl_thumb_{queue_id}"),
             _btn(f"✖️ {sc('cancel')}",      f"cancel_dl_{queue_id}")],
        ])

    # ─── settings ─────────────────────────────────────────────────────────────
    @staticmethod
    def settings(user: Dict) -> InlineKeyboardMarkup:
        q   = user.get("default_quality", "720p")
        p   = user.get("encode_preset",   "balanced")
        ntf = "🔔" if user.get("notify_complete") else "🔕"
        return InlineKeyboardMarkup([
            [_btn(f"🎨 {sc('quality')}: {q}",  "cfg_quality"),
             _btn(f"⚙️ {sc('preset')}: {p}",   "cfg_preset")],
            [_btn(f"{ntf} {sc('notifications')}", "cfg_notify"),
             _btn(f"🖼️ {sc('custom thumb')}",  "cfg_thumb")],
            [_btn(f"🌐 {sc('language')}",       "cfg_language"),
             _btn(f"🔄 {sc('reset stats')}",    "cfg_reset_stats")],
            [_btn(f"◀️ {sc('back')}", "show_home")],
        ])

    # ─── confirm dialog ───────────────────────────────────────────────────────
    @staticmethod
    def confirm(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"✅ {sc('yes')}", yes_data),
             _btn(f"❌ {sc('no')}",  no_data)],
        ])

    # ─── generic back ─────────────────────────────────────────────────────────
    @staticmethod
    def back(target: str = "show_home") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"◀️ {sc('back')}", target)]
        ])

    # ─── news item ────────────────────────────────────────────────────────────
    @staticmethod
    def news_item(news_url: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_url_btn(f"📰 {sc('read full article')}", news_url)],
            [_btn(f"◀️ {sc('back to news')}", "show_news")],
        ])

    # ─── ADMIN PANEL (20+ colour buttons) ────────────────────────────────────
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            # Row 1 — analytics
            [_btn("📊 " + sc("stats"),           "adm_stats"),
             _btn("📈 " + sc("analytics"),        "adm_analytics")],
            # Row 2 — users
            [_btn("👥 " + sc("user search"),      "adm_user_search"),
             _btn("🚫 " + sc("banned users"),     "adm_banned_list")],
            # Row 3 — content
            [_btn("📢 " + sc("broadcast"),        "adm_broadcast_menu"),
             _btn("📰 " + sc("cr news"),          "adm_news")],
            # Row 4 — queue
            [_btn("📋 " + sc("queue"),            "adm_queue"),
             _btn("🗑️ " + sc("clear queue"),      "adm_clearqueue_confirm")],
            # Row 5 — premium
            [_btn("💎 " + sc("premium mgmt"),     "adm_premium"),
             _btn("🎟️ " + sc("redeem codes"),     "adm_redeemcodes")],
            # Row 6 — system
            [_btn("🍪 " + sc("cookies"),          "adm_cookies"),
             _btn("📝 " + sc("logs"),             "adm_logs")],
            # Row 7 — config
            [_btn("⚙️ " + sc("bot settings"),    "adm_settings"),
             _btn("💻 " + sc("custom cmds"),      "adm_cmds")],
            # Row 8 — access
            [_btn("🔐 " + sc("auth groups"),      "adm_auth"),
             _btn("🔒 " + sc("maintenance"),      "adm_maintenance")],
            # Row 9 — welcome
            [_btn("🖼️ " + sc("welcome image"),    "adm_welcome_image"),
             _btn("✏️ " + sc("welcome text"),     "adm_welcome_text")],
            # Row 10 — database
            [_btn("💾 " + sc("db backup"),        "adm_dbbackup"),
             _btn("🔧 " + sc("vacuum db"),        "adm_vacuum")],
            # Row 11 — diagnostics + close
            [_btn("🔬 " + sc("diagnostics"),      "adm_diagnostics"),
             _btn("📤 " + sc("export users"),     "adm_exportusers")],
            [_btn("✖️ " + sc("close panel"),       "adm_close")],
        ])

    # ─── admin → broadcast sub-menu ──────────────────────────────────────────
    @staticmethod
    def admin_broadcast() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("📢 " + sc("broadcast all"),      "adm_bc_all"),
             _btn("💎 " + sc("broadcast premium"),  "adm_bc_premium")],
            [_btn("🆓 " + sc("broadcast free"),     "adm_bc_free"),
             _btn("📌 " + sc("pin message"),        "adm_bc_pin")],
            [_btn("◀️ " + sc("back"),               "adm_back")],
        ])

    # ─── admin → premium sub-menu ─────────────────────────────────────────────
    @staticmethod
    def admin_premium() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("➕ " + sc("add premium"),        "adm_addpremium_prompt"),
             _btn("➖ " + sc("revoke premium"),     "adm_revokepremium_prompt")],
            [_btn("🎟️ " + sc("gen redeem code"),   "adm_gencode_prompt"),
             _btn("📋 " + sc("list codes"),         "adm_listcodes")],
            [_btn("◀️ " + sc("back"),               "adm_back")],
        ])

    # ─── admin → settings sub-menu ────────────────────────────────────────────
    @staticmethod
    def admin_settings_panel(db: "Database") -> InlineKeyboardMarkup:
        maint = db.get_setting("maintenance_mode", "False") == "True"
        fs    = db.get_setting("force_sub_enabled", "False") == "True"
        news  = db.get_setting("news_enabled", "True") == "True"
        rl    = db.get_setting("rate_limit_enabled", "True") == "True"
        return InlineKeyboardMarkup([
            [_btn(("🟢" if not maint else "🔴") + " " + sc("maintenance mode"),
                  "adm_toggle_maintenance")],
            [_btn(("🟢" if fs else "⚫") + " " + sc("force subscribe"),
                  "adm_toggle_forcesub")],
            [_btn(("🟢" if news else "⚫") + " " + sc("news enabled"),
                  "adm_toggle_news")],
            [_btn(("🟢" if rl else "⚫") + " " + sc("rate limiter"),
                  "adm_toggle_ratelimit")],
            [_btn("✏️ " + sc("set welcome msg"),   "adm_welcome_text"),
             _btn("🖼️ " + sc("set welcome img"),   "adm_welcome_image")],
            [_btn("📢 " + sc("set log channel"),   "adm_set_log_channel"),
             _btn("📰 " + sc("set news channel"),  "adm_set_news_channel")],
            [_btn("◀️ " + sc("back"),              "adm_back")],
        ])

    # ─── welcome image admin ──────────────────────────────────────────────────
    @staticmethod
    def admin_welcome_image(has_image: bool) -> InlineKeyboardMarkup:
        rows = []
        if has_image:
            rows.append([_btn("👁️ " + sc("preview"),       "adm_welcome_preview"),
                         _btn("🗑️ " + sc("remove image"),  "adm_welcome_img_remove")])
        rows.append([_btn("📤 " + sc("upload new image"),   "adm_welcome_img_upload")])
        rows.append([_btn("◀️ " + sc("back"),               "adm_settings")])
        return InlineKeyboardMarkup(rows)

    # ─── user profile buttons ─────────────────────────────────────────────────
    @staticmethod
    def user_profile(uid: int, is_premium: bool) -> InlineKeyboardMarkup:
        rows = [
            [_btn("📊 " + sc("stats"),        "show_stats"),
             _btn("📜 " + sc("history"),      "show_history")],
            [_btn("❤️ " + sc("favorites"),   "show_favorites"),
             _btn("👀 " + sc("watchlist"),    "show_watchlist")],
            [_btn("👥 " + sc("referral"),     "show_referral"),
             _btn("🎟️ " + sc("redeem"),      "show_redeem")],
        ]
        if not is_premium:
            rows.append([_btn("💎 " + sc("upgrade to premium"), "show_premium")])
        rows.append([_btn("◀️ " + sc("back"), "show_home")])
        return InlineKeyboardMarkup(rows)

    # ─── queue item buttons ───────────────────────────────────────────────────
    @staticmethod
    def queue_actions(qid: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn(f"⚡ {sc('prioritise')} #{qid}", f"q_priority_{qid}"),
             _btn(f"✖️ {sc('cancel')} #{qid}",      f"cancel_dl_{qid}")],
            [_btn(f"◀️ {sc('back to queue')}",       "show_queue")],
        ])

    # ─── language picker ──────────────────────────────────────────────────────
    @staticmethod
    def language_picker() -> InlineKeyboardMarkup:
        langs = [
            ("🇬🇧 English", "lang_en"), ("🇪🇸 Español",   "lang_es"),
            ("🇧🇷 Português", "lang_pt"), ("🇫🇷 Français", "lang_fr"),
            ("🇩🇪 Deutsch",  "lang_de"), ("🇯🇵 日本語",    "lang_ja"),
            ("🇰🇷 한국어",    "lang_ko"), ("🇮🇳 हिन्दी",   "lang_hi"),
            ("🇮🇳 தமிழ்",   "lang_ta"), ("🇦🇪 العربية",  "lang_ar"),
        ]
        rows = []
        for i in range(0, len(langs), 2):
            rows.append([_btn(langs[i][0], langs[i][1])] +
                        ([_btn(langs[i+1][0], langs[i+1][1])] if i+1 < len(langs) else []))
        rows.append([_btn(f"◀️ {sc('back')}", "show_settings")])
        return InlineKeyboardMarkup(rows)

    # ─── achievements ─────────────────────────────────────────────────────────
    @staticmethod
    def achievements_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("🏆 " + sc("my achievements"), "show_achievements"),
             _btn("📈 " + sc("leaderboard"),     "show_leaderboard")],
            [_btn("◀️ " + sc("back"),             "show_home")],
        ])

    # ─── video tools menu ────────────────────────────────────────────────────
    @staticmethod
    def video_tools() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("✂️ " + sc("trim"),            "vt_trim"),
             _btn("🗜️ " + sc("compress"),       "vt_compress")],
            [_btn("🖼️ " + sc("thumbnail"),       "vt_thumb"),
             _btn("🎤 " + sc("audio extract"),  "vt_audio")],
            [_btn("💧 " + sc("watermark"),       "vt_watermark"),
             _btn("🎞️ " + sc("make gif"),       "vt_gif")],
            [_btn("ℹ️ " + sc("media info"),      "vt_info"),
             _btn("✏️ " + sc("rename"),          "vt_rename")],
            [_btn("📝 " + sc("subtitles"),        "vt_subtitles"),
             _btn("⚙️ " + sc("encode"),          "vt_encode")],
            [_btn("◀️ " + sc("back"),             "show_home")],
        ])

    # ─── referral menu ────────────────────────────────────────────────────────
    @staticmethod
    def referral_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("🔗 " + sc("my referral link"),  "ref_link"),
             _btn("👥 " + sc("my referrals"),       "ref_list")],
            [_btn("🏆 " + sc("top referrers"),      "ref_top"),
             _btn("💰 " + sc("my points"),          "ref_points")],
            [_btn("◀️ " + sc("back"),               "show_home")],
        ])

    # ─── news navigation ─────────────────────────────────────────────────────
    @staticmethod
    def news_nav(news_list: List[Dict]) -> InlineKeyboardMarkup:
        rows = []
        for i, n in enumerate(news_list[:5]):
            rows.append([_btn(
                f"📰 {n['title'][:45]}{'…' if len(n['title']) > 45 else ''}",
                f"news_item_{n['id']}")])
        rows.append([_btn(f"🔄 {sc('refresh')}", "show_news"),
                     _btn(f"◀️ {sc('back')}",    "show_home")])
        return InlineKeyboardMarkup(rows)

    # ─── subscription expiry actions ─────────────────────────────────────────
    @staticmethod
    def subscription_actions() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [_btn("🔄 " + sc("renew"),          "show_premium"),
             _btn("🎁 " + sc("gift someone"),   "gift_prompt")],
            [_btn("🎟️ " + sc("redeem code"),    "show_redeem"),
             _btn("◀️ " + sc("back"),           "show_home")],
        ])


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 12: ꜱᴇɴᴅ ʜᴇʟᴘᴇʀꜱ
# ══════════════════════════════════════════════════════════════════════════════

async def safe_edit(msg, text: str, reply_markup=None,
                    parse_mode=ParseMode.HTML):
    try:
        kwargs = {"text": text, "parse_mode": parse_mode}
        if reply_markup is not None:
            kwargs["reply_markup"] = reply_markup
        await msg.edit_text(**kwargs)
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.debug(f"safe_edit: {e}")
    except Exception as e:
        logger.debug(f"safe_edit: {e}")


async def safe_reply(update: Update, text: str, reply_markup=None,
                     parse_mode=ParseMode.HTML, **kwargs):
    try:
        msg = update.effective_message
        if not msg:
            return None
        kw = {"text": text, "parse_mode": parse_mode}
        if reply_markup:
            kw["reply_markup"] = reply_markup
        kw.update(kwargs)
        return await msg.reply_text(**kw)
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        return await safe_reply(update, text, reply_markup, parse_mode, **kwargs)
    except Exception as e:
        logger.error(f"safe_reply: {e}")
        return None


async def log_to_channel(bot, text: str, db: Database,
                         parse_mode=ParseMode.HTML):
    log_ch = int(db.get_setting("log_channel", "0") or "0")
    if log_ch:
        try:
            await bot.send_message(log_ch, text, parse_mode=parse_mode)
        except Exception as e:
            logger.debug(f"log_to_channel: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 13: ᴍᴀɪɴ ʙᴏᴛ ʜᴀɴᴅʟᴇʀ
# ══════════════════════════════════════════════════════════════════════════════

class CrunchyBot:
    def __init__(self):
        self.db         = Database()
        self.downloader = DownloadManager(self.db)
        self._queue_task: Optional[asyncio.Task] = None
        self._sched_task: Optional[asyncio.Task] = None
        self._news_task:  Optional[asyncio.Task] = None
        self._app: Optional[Application] = None

    # ──────────── helpers ─────────────────────────────────────────────────────

    def _uid(self, update: Update) -> int:
        return update.effective_user.id if update.effective_user else 0

    def _msg(self, update: Update):
        return update.effective_message

    def _uname(self, update: Update) -> str:
        u = update.effective_user
        return u.first_name if u else sc("user")

    async def _auth_check(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE) -> bool:
        uid = self._uid(update)
        ok, links = await AuthChecker.check_user(ctx.bot, uid, self.db)
        if not ok:
            kb = [[_btn(f"📢 {sc('join channel/group')}", l)] for l in links if l]
            kb.append([_btn(f"🔄 {sc('check again')}", "auth_check")])
            await safe_reply(update,
                f"{Em.AUTH} <b>{sc('access restricted')}</b>\n\n"
                f"{sc('please join the required channels/groups to use this bot')}:",
                InlineKeyboardMarkup(kb))
            return False
        return True

    async def _maintenance_check(self, update: Update) -> bool:
        uid = self._uid(update)
        if (self.db.get_setting("maintenance_mode") == "True"
                and uid not in Config.ADMIN_IDS):
            await safe_reply(update,
                f"{Em.WARNING} <b>{sc('maintenance mode')}</b>\n\n"
                f"{sc('bot is under maintenance. please try again later')}.")
            return False
        return True

    def _ensure_queue_running(self):
        if self._queue_task is None or self._queue_task.done():
            self._queue_task = asyncio.create_task(self._queue_worker())

    # ──────────── /start ──────────────────────────────────────────────────────

    async def cmd_start(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        user  = update.effective_user
        uname = user.username  if user else None
        fname = user.first_name if user else sc("user")
        lname = user.last_name  if user else None

        # Handle referral
        referrer = None
        if ctx.args:
            ref_code = ctx.args[0]
            if ref_code.startswith("ref_"):
                ref_code = ref_code[4:]
            referrer = self.db.get_user_by_ref_code(ref_code)
            if referrer == uid:
                referrer = None

        self.db.register_user(uid, uname, fname, lname, referrer)

        if not await self._maintenance_check(update):
            return

        is_pm = self.db.is_premium(uid)
        text  = (
            f"{Em.ANIME} <b>{sc('crunchyroll ultimate bot v200.1')}</b>\n\n"
            f"{sc('hello')}, <b>{escape_html(fname)}</b>! "
            f"{sc('welcome to the ultimate crunchyroll download experience')}.\n\n"
            f"{'💎 <b>' + sc('premium member') + '</b>' if is_pm else '🆓 ' + sc('free user')}\n\n"
            f"{Em.FAST} <b>{sc('premium users')}</b>: "
            f"{sc('fast lane, 1080p/4k/hdr, unlimited')}\n"
            f"{Em.SLOW} <b>{sc('free users')}</b>: "
            f"{sc('slow lane, up to 720p, 3 downloads/day')}\n\n"
            f"{sc('send a crunchyroll url or use the menu below')}:"
        )
        if referrer:
            ref_user = self.db.get_user(referrer)
            rname = (ref_user.get("first_name", sc("someone"))
                     if ref_user else sc("someone"))
            text += f"\n\n{Em.REFERRAL} {sc('referred by')} <b>{escape_html(rname)}</b>!"

        # Send welcome image if set (NEW FEATURE)
        welcome_img = self.db.get_setting("welcome_image_id", "")
        if welcome_img:
            try:
                await ctx.bot.send_photo(
                    uid, photo=welcome_img,
                    caption=text,
                    reply_markup=KB.home(),
                    parse_mode=ParseMode.HTML)
                return
            except Exception:
                pass  # fallback to text if photo fails

        await safe_reply(update, text, KB.home())

        if uid not in Config.ADMIN_IDS:
            await log_to_channel(
                ctx.bot,
                f"{Em.INFO} {sc('new user')}: {escape_html(fname)} "
                f"(@{uname or 'no_username'}) — ID: <code>{uid}</code>",
                self.db)

    # ──────────── /help ───────────────────────────────────────────────────────

    async def cmd_help(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        is_pm = self.db.is_premium(uid)
        is_adm = self.db.is_admin(uid)

        text = (
            f"{Em.INFO} <b>{sc('commands reference')}</b>\n\n"
            f"<b>{sc('download')}</b>\n"
            f"/cr <code>{sc('url')}</code> — {sc('download crunchyroll episode')}\n"
            f"/batch <code>{sc('url1 url2')}</code> — {sc('batch download (premium)')}\n"
            f"/schedule <code>{sc('url hh:mm')}</code> — "
            f"{sc('schedule a download')}\n\n"
            f"<b>{sc('queue')}</b>\n"
            f"/queue — {sc('view your queue')}\n"
            f"/cancel <code>{sc('id')}</code> — {sc('cancel a download')}\n\n"
            f"<b>{sc('account')}</b>\n"
            f"/stats — {sc('your statistics')}\n"
            f"/premium — {sc('premium plans')}\n"
            f"/redeem <code>{sc('code')}</code> — {sc('redeem a code')}\n"
            f"/referral — {sc('referral program')}\n\n"
            f"<b>{sc('tools')}</b>\n"
            f"/mediainfo — {sc('reply to a video for info')}\n"
            f"/rename <code>{sc('name')}</code> — {sc('reply to a file to rename')}\n"
            f"/compress <code>{sc('mb')}</code> — {sc('compress a video')}\n"
            f"/trim <code>{sc('start end')}</code> — {sc('trim a video')}\n"
            f"/thumbnail — {sc('extract thumbnail')}\n"
            f"/watermark <code>{sc('text')}</code> — {sc('add watermark (premium)')}\n"
            f"/gif <code>{sc('start dur')}</code> — {sc('make gif (premium)')}\n"
            f"/audio — {sc('extract audio (premium)')}\n\n"
            f"<b>{sc('content')}</b>\n"
            f"/news — {sc('crunchyroll latest news')}\n"
            f"/search <code>{sc('name')}</code> — {sc('search anime')}\n"
            f"/airing — {sc('currently airing')}\n"
            f"/season — {sc('this season')}\n"
            f"/favorites — {sc('your favorites')}\n"
            f"/watchlist — {sc('your watchlist')}\n"
            f"/history — {sc('download history')}\n"
            f"/leaderboard — {sc('top downloaders')}\n\n"
            f"<b>{sc('settings')}</b>\n"
            f"/settings — {sc('configure quality, preset, etc.')}\n"
            f"/feedback <code>{sc('1-5 message')}</code> — {sc('send feedback')}\n"
        )
        if is_adm:
            text += (
                f"\n<b>{sc('admin')}</b>\n"
                f"/admin — {sc('admin panel')}\n"
                f"/ban /unban /warn — {sc('moderation')}\n"
                f"/addpremium /revokepremium — {sc('premium control')}\n"
                f"/broadcast — {sc('message all users')}\n"
                f"/addcmd /editcmd /delcmd — {sc('custom commands')}\n"
                f"/gencode — {sc('generate redeem codes')}\n"
                f"/setcookies — {sc('update cr cookies')}\n"
                f"/fetchnews — {sc('fetch cr news now')}\n"
                f"/setwelcomeimage — {sc('set welcome image')}\n"
                f"/welcomepreview — {sc('preview welcome screen')}\n"
                f"/botinfo — {sc('full bot info')}\n"
                f"/diagnostics — {sc('system diagnostics')}\n"
                f"/dbbackup — {sc('backup database')}\n"
                f"/exportusers — {sc('export users csv')}\n"
                f"/cleanup — {sc('clean temp files')}\n"
                f"/vacuum — {sc('vacuum database')}\n"
            )
        await safe_reply(update, text, KB.back())

    # ──────────── /cr (download) ──────────────────────────────────────────────

    async def cmd_cr(self, update: Update,
                     ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        msg = self._msg(update)

        if not await self._maintenance_check(update):
            return
        if not await self._auth_check(update, ctx):
            return
        if not self.db.check_rate_limit(uid):
            await safe_reply(update,
                f"{Em.WARNING} {sc('rate limit reached. please wait a moment')}.")
            return

        url = " ".join(ctx.args) if ctx.args else ""
        if not url:
            await safe_reply(update,
                f"{Em.INFO} {sc('usage')}: /cr <code>{sc('crunchyroll_url')}</code>\n\n"
                f"{sc('example')}:\n"
                f"<code>/cr https://www.crunchyroll.com/watch/XXXXXXXX/episode</code>")
            return

        if not self.downloader.cr.is_valid_url(url):
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid crunchyroll url')}.\n"
                f"{sc('url must be from crunchyroll.com')}.")
            return

        user = self.db.get_user(uid) or {}
        if self.db.is_banned(uid):
            await safe_reply(update,
                f"{Em.BAN} {sc('you are banned from using this bot')}.")
            return

        ok, count, limit = self.db.check_daily_limit(uid)
        if not ok:
            await safe_reply(update,
                f"{Em.ERROR} {sc('daily limit reached')}: {count}/{limit}\n"
                f"{sc('upgrade to premium for unlimited downloads')}.",
                KB.premium_plans())
            return

        queue_items = self.db.get_user_queue(uid)
        if len(queue_items) >= Config.MAX_QUEUE_PER_USER:
            await safe_reply(update,
                f"{Em.QUEUE} {sc('your queue is full')} "
                f"({len(queue_items)}/{Config.MAX_QUEUE_PER_USER}).\n"
                f"{sc('cancel some downloads first')}.")
            return

        quality = user.get("default_quality", Config.DEFAULT_QUALITY)
        preset  = user.get("encode_preset",   Config.DEFAULT_ENCODE)
        is_fast = self.db.is_premium(uid)
        delay   = 0 if is_fast else Config.FREE_DOWNLOAD_DELAY

        status = await safe_reply(update,
            f"{Em.LOADING} {sc('adding to queue')}…")

        qid  = self.db.add_to_queue(
            uid, url, quality, preset,
            msg_id=(status.message_id if status else 0),
            chat_id=(update.effective_chat.id if update.effective_chat else uid))
        pos  = self.db.get_queue_position(qid)
        lane = f"{Em.FAST} <b>{sc('fast lane')}</b>" if is_fast else f"{Em.SLOW} <b>{sc('slow lane')}</b>"

        queue_text = (
            f"{Em.QUEUE} <b>{sc('queued')} #{qid}</b>\n\n"
            f"{Em.INFO} {sc('position')}: <b>#{pos}</b>\n"
            f"{lane}\n"
            f"{Em.QUALITY} {quality} | {Em.ENCODE} {preset}\n"
        )
        if delay:
            queue_text += f"⏱ {sc('estimated delay')}: ~{delay}s\n"
        queue_text += f"\n{ProgressBar.make(0)}"

        if status:
            await safe_edit(status, queue_text, KB.queue_actions(qid))

        self._ensure_queue_running()

    # ──────────── /premium ────────────────────────────────────────────────────

    async def cmd_premium(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        is_pm = self.db.is_premium(uid)
        user  = self.db.get_user(uid) or {}
        expiry_str = ""
        if is_pm:
            exp = user.get("premium_expiry")
            if exp:
                try:
                    days_left = (datetime.fromisoformat(exp)
                                 - datetime.now()).days
                    expiry_str = (f"\n⏰ {sc('expires in')} "
                                  f"<b>{days_left}</b> {sc('days')}")
                except Exception:
                    pass

        text = (
            f"{Em.PREMIUM} <b>{sc('premium membership')}</b>\n\n"
            + (f"{'💎 <b>' + sc('you are premium') + '</b>'}{expiry_str}\n\n"
               if is_pm else f"🆓 {sc('you are currently on the free plan')}\n\n")
            + f"<b>{sc('plans')}</b>\n"
        )
        for plan, price in Config.SUBSCRIPTION_PRICES.items():
            features = ", ".join(Config.SUBSCRIPTION_FEATURES.get(plan, [])[:2])
            text += (f"• <b>{plan.upper()}</b>: {price} ⭐ — {features}\n")
        await safe_reply(update, text, KB.premium_plans())

    # ──────────── /stats ──────────────────────────────────────────────────────

    async def cmd_stats(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        uid  = self._uid(update)
        user = self.db.get_user(uid) or {}
        is_pm = self.db.is_premium(uid)

        total_dl = user.get("total_downloads", 0)
        total_sz = format_file_size(user.get("total_size", 0) or 0)
        daily    = user.get("daily_downloads", 0)
        limit    = (Config.PREMIUM_DAILY_LIMIT if is_pm
                    else Config.FREE_DAILY_LIMIT)
        ref_cnt  = user.get("referral_count", 0)
        ref_pts  = user.get("referral_points", 0)
        quality  = user.get("default_quality", "720p")
        preset   = user.get("encode_preset", "balanced")

        text = (
            f"{Em.STATS} <b>{sc('your statistics')}</b>\n\n"
            f"👤 <b>{escape_html(user.get('first_name','?'))}</b>\n"
            f"🆔 <code>{uid}</code>\n"
            f"💎 {sc('plan')}: <b>{'PREMIUM' if is_pm else 'FREE'}</b>\n\n"
            f"📥 {sc('total downloads')}: <b>{total_dl:,}</b>\n"
            f"📦 {sc('total size')}: <b>{total_sz}</b>\n"
            f"📅 {sc('today')}: <b>{daily}</b>/{limit if limit < 99999 else '∞'}\n\n"
            f"🎨 {sc('quality')}: <b>{quality}</b>\n"
            f"⚙️ {sc('preset')}: <b>{preset}</b>\n\n"
            f"👥 {sc('referrals')}: <b>{ref_cnt}</b> | "
            f"💰 {sc('points')}: <b>{ref_pts}</b>\n"
        )
        await safe_reply(update, text, KB.user_profile(uid, is_pm))

    # ──────────── /settings ───────────────────────────────────────────────────

    async def cmd_settings(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        uid  = self._uid(update)
        user = self.db.get_user(uid) or {}
        await safe_reply(update,
            f"{Em.SETTINGS} <b>{sc('settings')}</b>\n\n"
            f"🎨 {sc('quality')}: <b>{user.get('default_quality','720p')}</b>\n"
            f"⚙️ {sc('preset')}: <b>{user.get('encode_preset','balanced')}</b>\n"
            f"🔔 {sc('notifications')}: "
            f"<b>{'on' if user.get('notify_complete',1) else 'off'}</b>",
            KB.settings(user))

    # ──────────── /queue ──────────────────────────────────────────────────────

    async def cmd_queue(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        items = self.db.get_user_queue(uid)
        if not items:
            await safe_reply(update,
                f"{Em.QUEUE} {sc('your queue is empty')}.\n"
                f"{sc('send a crunchyroll url to download')}.",
                KB.back())
            return
        lines = [f"{Em.QUEUE} <b>{sc('your queue')} ({len(items)})</b>\n"]
        for it in items:
            lane = "⚡" if it.get("is_fast") else "🐢"
            lines.append(
                f"#{it['id']} {lane} | {it['quality']} | "
                f"{it['status']} {it['progress']}%\n"
                f"<code>{it['url'][:45]}…</code>")
        await safe_reply(update, "\n".join(lines), KB.back())

    # ──────────── /cancel ─────────────────────────────────────────────────────

    async def cmd_cancel(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if not ctx.args or not ctx.args[0].isdigit():
            await safe_reply(update,
                f"{Em.QUEUE} {sc('usage')}: /cancel <code>{sc('queue_id')}</code>")
            return
        qid = int(ctx.args[0])
        if self.db.cancel_queue_item(qid, uid):
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('download')} #{qid} {sc('cancelled')}.")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('cannot cancel — not found, already processing, or not yours')}.")

    # ──────────── /history ────────────────────────────────────────────────────

    async def cmd_history(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        items = self.db.get_user_history(uid, 10)
        if not items:
            await safe_reply(update,
                f"{Em.HISTORY} {sc('no download history yet')}.",
                KB.back())
            return
        lines = [f"{Em.HISTORY} <b>{sc('download history')}</b>\n"]
        for it in items:
            status_icon = "✅" if it["status"] == "completed" else "❌"
            lines.append(
                f"{status_icon} #{it['id']} | {it.get('quality','?')}\n"
                f"<code>{it['url'][:45]}…</code>")
        await safe_reply(update, "\n".join(lines), KB.back())

    # ──────────── /redeem ─────────────────────────────────────────────────────

    async def cmd_redeem(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if not ctx.args:
            await safe_reply(update,
                f"{Em.REDEEM} {sc('usage')}: /redeem <code>{sc('code')}</code>")
            return
        code = ctx.args[0].upper()
        ok, msg, plan, days = self.db.use_redeem_code(code, uid)
        if not ok:
            await safe_reply(update, f"{Em.ERROR} {msg}.")
            return
        self.db.add_premium(uid, plan, days, f"redeem_{code}", 0)
        await safe_reply(update,
            f"{Em.SUCCESS} <b>{sc('code redeemed')}!</b>\n\n"
            f"💎 {sc('plan')}: <b>{plan.upper()}</b>\n"
            f"📅 {sc('days added')}: <b>{days}</b>\n\n"
            f"{sc('enjoy your premium')}! {Em.FIRE}")

    # ──────────── /referral ───────────────────────────────────────────────────

    async def cmd_referral(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        uid  = self._uid(update)
        code = self.db.get_referral_code(uid)
        cnt  = self.db.get_referral_count(uid)
        pts  = self.db.get_referral_points(uid)
        req  = Config.REFERRAL_REQUIRED
        me   = await ctx.bot.get_me()
        link = f"https://t.me/{me.username}?start=ref_{code}"
        text = (
            f"{Em.REFERRAL} <b>{sc('referral program')}</b>\n\n"
            f"🔗 {sc('your link')}:\n<code>{link}</code>\n\n"
            f"👥 {sc('referrals')}: <b>{cnt}</b>\n"
            f"💰 {sc('points')}: <b>{pts}</b>\n"
            f"🎯 {sc('goal')}: {req} {sc('referrals')} = {sc('free premium')}\n\n"
            f"{sc('share your link and earn premium when friends join')}!"
        )
        await safe_reply(update, text, KB.referral_menu())

    # ──────────── /news ───────────────────────────────────────────────────────

    async def cmd_news(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        items = self.db.get_latest_news(5)
        if not items:
            await safe_reply(update,
                f"{Em.NEWS} {sc('no news yet. use')} /fetchnews {sc('to fetch')}.",
                KB.back())
            return
        text = f"{Em.NEWS} <b>{sc('crunchyroll news')}</b>\n\n"
        for n in items:
            text += (f"📰 <b>{escape_html(n['title'])}</b>\n"
                     f"<i>{str(n.get('published_at',''))[:16]}</i>\n"
                     f"{escape_html((n.get('description','') or '')[:120])}…\n\n")
        await safe_reply(update, text, KB.news_nav(items))

    # ──────────── /favorites ──────────────────────────────────────────────────

    async def cmd_favorites(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        items = self.db.get_favorites(uid)
        if not items:
            await safe_reply(update,
                f"{Em.HEART} {sc('no favorites yet')}.\n"
                f"{sc('use')} /addfav <code>{sc('anime_id title')}</code> "
                f"{sc('to add')}.",
                KB.back())
            return
        lines = [f"{Em.HEART} <b>{sc('your favorites')} ({len(items)})</b>\n"]
        for i, it in enumerate(items[:20], 1):
            lines.append(f"{i}. {escape_html(it['anime_title'])}")
        await safe_reply(update, "\n".join(lines), KB.back())

    # ──────────── /watchlist ──────────────────────────────────────────────────

    async def cmd_watchlist(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        uid   = self._uid(update)
        items = self.db.get_watchlist(uid)
        if not items:
            await safe_reply(update,
                f"{Em.WATCH} {sc('your watchlist is empty')}.\n"
                f"{sc('use')} /addwatch <code>{sc('anime_id title')}</code> "
                f"{sc('to add')}.",
                KB.back())
            return
        lines = [f"{Em.WATCH} <b>{sc('your watchlist')} ({len(items)})</b>\n"]
        for i, it in enumerate(items[:20], 1):
            lines.append(f"{i}. {escape_html(it['anime_title'])}")
        await safe_reply(update, "\n".join(lines), KB.back())

    # ──────────── /leaderboard ────────────────────────────────────────────────

    async def cmd_leaderboard(self, update: Update,
                              ctx: ContextTypes.DEFAULT_TYPE):
        rows  = self.db.get_leaderboard(10)
        lines = [f"{Em.LEAD} <b>{sc('top downloaders')}</b>\n"]
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 10
        for i, r in enumerate(rows, 0):
            name = escape_html(r.get("first_name", "?"))
            dls  = r.get("total_downloads", 0)
            sz   = format_file_size(r.get("total_size", 0) or 0)
            lines.append(f"{medals[i]} <b>{name}</b> — {dls:,} {sc('dls')} ({sz})")
        await safe_reply(update, "\n".join(lines), KB.back())

    # ──────────── /feedback ───────────────────────────────────────────────────

    async def cmd_feedback(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if not ctx.args or len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.HEART} {sc('usage')}: /feedback <code>1-5 your message</code>")
            return
        try:
            rating = int(ctx.args[0])
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            await safe_reply(update,
                f"{Em.ERROR} {sc('rating must be 1-5')}.")
            return
        msg = " ".join(ctx.args[1:])
        self.db.add_feedback(uid, rating, msg)
        stars = "⭐" * rating
        await safe_reply(update,
            f"{Em.SUCCESS} {sc('feedback received')}! {stars}\n"
            f"{sc('thank you for your feedback')}!")
        await log_to_channel(
            ctx.bot,
            f"📝 {sc('feedback from')} <code>{uid}</code>: "
            f"{stars}\n{escape_html(msg)}",
            self.db)

    # ──────────── /schedule ───────────────────────────────────────────────────

    async def cmd_schedule(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.SCHEDULE} {sc('usage')}: "
                f"/schedule <code>{sc('url hh:mm')}</code>")
            return
        url  = ctx.args[0]
        time_str = ctx.args[1]
        if not self.downloader.cr.is_valid_url(url):
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid crunchyroll url')}.")
            return
        try:
            hh, mm = map(int, time_str.split(":"))
            now    = datetime.now()
            run_at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if run_at <= now:
                run_at += timedelta(days=1)
        except ValueError:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid time format. use hh:mm')}.")
            return
        user  = self.db.get_user(uid) or {}
        qual  = user.get("default_quality", Config.DEFAULT_QUALITY)
        pres  = user.get("encode_preset",   Config.DEFAULT_ENCODE)
        sid   = self.db.schedule_download(uid, url, qual, pres, run_at.isoformat())
        await safe_reply(update,
            f"{Em.SCHEDULE} <b>{sc('download scheduled')}!</b>\n\n"
            f"#{sid} | {run_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"<code>{url[:50]}</code>")

    # ──────────── /batch ──────────────────────────────────────────────────────

    @premium_only
    async def cmd_batch(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        uid  = self._uid(update)
        urls = ctx.args or []
        valid = [u for u in urls if self.downloader.cr.is_valid_url(u)]
        if not valid:
            await safe_reply(update,
                f"{Em.DOWNLOAD} {sc('usage')}: "
                f"/batch <code>{sc('url1 url2 ...')}</code>")
            return
        if len(valid) > Config.MAX_BATCH_SIZE:
            valid = valid[:Config.MAX_BATCH_SIZE]
        user  = self.db.get_user(uid) or {}
        qual  = user.get("default_quality", Config.DEFAULT_QUALITY)
        pres  = user.get("encode_preset",   Config.DEFAULT_ENCODE)
        ids   = []
        for url in valid:
            qid = self.db.add_to_queue(uid, url, qual, pres,
                                       chat_id=update.effective_chat.id if update.effective_chat else uid)
            ids.append(qid)
        self._ensure_queue_running()
        await safe_reply(update,
            f"{Em.SUCCESS} <b>{sc('batch queued')}!</b>\n"
            f"{len(ids)} {sc('downloads added')}: "
            f"#{', #'.join(map(str, ids))}")

    # ──────────── /mediainfo ──────────────────────────────────────────────────

    async def cmd_mediainfo(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.INFO} {sc('reply to a video with')} /mediainfo")
            return
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('reading media info')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"mi_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            info = await VideoTools.get_media_info(fp)
            Path(fp).unlink(missing_ok=True)
            if not info:
                if status:
                    await safe_edit(status, f"{Em.ERROR} {sc('could not read media info')}.")
                return
            text = (
                f"{Em.INFO} <b>{sc('media information')}</b>\n\n"
                f"⏱ {sc('duration')}: <b>{info.get('duration','?')}</b>\n"
                f"📦 {sc('size')}: <b>{info.get('size','?')}</b>\n"
                f"📡 {sc('bitrate')}: <b>{info.get('bitrate','?')}</b>\n\n"
                f"🎥 {sc('video codec')}: <b>{info.get('video_codec','?')}</b>\n"
                f"📐 {sc('resolution')}: <b>{info.get('resolution','?')}</b>\n"
                f"🎞 {sc('fps')}: <b>{info.get('fps','?')}</b>\n\n"
                f"🎤 {sc('audio codec')}: <b>{info.get('audio_codec','?')}</b>\n"
                f"🎵 {sc('channels')}: <b>{info.get('channels','?')}</b>\n"
                f"🔊 {sc('sample rate')}: <b>{info.get('sample_rate','?')} Hz</b>"
            )
            if status:
                await safe_edit(status, text, KB.back())
        except Exception as e:
            if status:
                await safe_edit(status, f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /rename ────────────────────────────────────────────────────

    async def cmd_rename(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.RENAME} {sc('reply to a file with')} "
                f"/rename <code>{sc('new_name')}</code>")
            return
        new_name = " ".join(ctx.args) if ctx.args else ""
        if not new_name:
            await safe_reply(update,
                f"{Em.RENAME} {sc('provide a new file name')}.")
            return
        if not new_name.endswith(".mp4"):
            new_name += ".mp4"
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('renaming')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"ren_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            await ctx.bot.send_document(
                msg.chat_id,
                document=InputFile(fp, filename=new_name),
                caption=f"{Em.SUCCESS} {sc('renamed to')}: <code>{new_name}</code>",
                parse_mode=ParseMode.HTML)
            Path(fp).unlink(missing_ok=True)
            if status:
                await status.delete()
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /compress ──────────────────────────────────────────────────

    async def cmd_compress(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.ENCODE} {sc('reply to a video with')} "
                f"/compress <code>{sc('target_mb')}</code>")
            return
        try:
            target_mb = int(ctx.args[0]) if ctx.args else 50
        except ValueError:
            target_mb = 50
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('compressing to')} {target_mb}MB…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"cmp_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.compress_video(fp, target_mb)
            if out and Path(out).exists():
                fname = f"compressed_{uuid.uuid4().hex[:6]}.mp4"
                await ctx.bot.send_document(
                    msg.chat_id,
                    document=InputFile(out, filename=fname),
                    caption=f"{Em.SUCCESS} {sc('compressed to')} ≤{target_mb}MB",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status,
                        f"{Em.ERROR} {sc('compression failed')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /trim ──────────────────────────────────────────────────────

    async def cmd_trim(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.ENCODE} {sc('reply to a video with')} "
                f"/trim <code>00:01:00 00:02:30</code>")
            return
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.INFO} {sc('usage')}: /trim <code>HH:MM:SS HH:MM:SS</code>")
            return
        start, end = ctx.args[0], ctx.args[1]
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('trimming')} {start} → {end}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"trm_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.trim_video(fp, start, end)
            if out and Path(out).exists():
                fname = f"trimmed_{uuid.uuid4().hex[:6]}.mp4"
                await ctx.bot.send_document(
                    msg.chat_id,
                    document=InputFile(out, filename=fname),
                    caption=f"{Em.SUCCESS} {sc('trimmed')}: {start} → {end}",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status, f"{Em.ERROR} {sc('trim failed')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /thumbnail ─────────────────────────────────────────────────

    async def cmd_thumbnail(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.THUMBNAIL} {sc('reply to a video with')} /thumbnail")
            return
        ts     = ctx.args[0] if ctx.args else "00:00:05"
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('extracting thumbnail')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"th_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.screenshot_video(fp, ts)
            if out and Path(out).exists():
                await ctx.bot.send_photo(
                    msg.chat_id,
                    photo=InputFile(out),
                    caption=f"{Em.THUMBNAIL} {sc('thumbnail at')} {ts}",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status,
                        f"{Em.ERROR} {sc('could not extract thumbnail')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /watermark ─────────────────────────────────────────────────

    @premium_only
    async def cmd_watermark(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.THUMBNAIL} {sc('reply to a video with')} "
                f"/watermark <code>{sc('text')}</code>")
            return
        text   = " ".join(ctx.args) if ctx.args else sc("crunchyroll bot")
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('adding watermark')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"wm_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.add_watermark(fp, text)
            if out and Path(out).exists():
                fname = f"watermarked_{uuid.uuid4().hex[:6]}.mp4"
                await ctx.bot.send_document(
                    msg.chat_id,
                    document=InputFile(out, filename=fname),
                    caption=f"{Em.SUCCESS} {sc('watermark added')}: <code>{text}</code>",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status, f"{Em.ERROR} {sc('watermark failed')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /gif ───────────────────────────────────────────────────────

    @premium_only
    async def cmd_gif(self, update: Update,
                      ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.VIDEO} {sc('reply to a video with')} "
                f"/gif <code>{sc('start duration scale')}</code>")
            return
        start    = ctx.args[0] if len(ctx.args) > 0 else "00:00:00"
        duration = int(ctx.args[1]) if len(ctx.args) > 1 else 5
        scale    = int(ctx.args[2]) if len(ctx.args) > 2 else 320
        status   = await safe_reply(update,
            f"{Em.LOADING} {sc('creating gif')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"gif_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.make_gif(fp, start, duration, scale)
            if out and Path(out).exists():
                await ctx.bot.send_animation(
                    msg.chat_id,
                    animation=InputFile(out),
                    caption=f"{Em.SUCCESS} {sc('gif created')} ({duration}s @ {scale}px)",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status, f"{Em.ERROR} {sc('gif creation failed')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /audio ─────────────────────────────────────────────────────

    @premium_only
    async def cmd_audio(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not (target.document or target.video):
            await safe_reply(update,
                f"{Em.AUDIO} {sc('reply to a video with')} /audio <code>[mp3|aac]</code>")
            return
        fmt    = (ctx.args[0].lower()
                  if ctx.args and ctx.args[0].lower() in ("mp3", "aac")
                  else "mp3")
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('extracting audio')}…")
        try:
            doc = target.document or target.video
            f   = await ctx.bot.get_file(doc.file_id)
            fp  = str(Config.TEMP_PATH / f"aud_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.extract_audio(fp, fmt)
            if out and Path(out).exists():
                fname = f"audio_{uuid.uuid4().hex[:6]}.{fmt}"
                await ctx.bot.send_audio(
                    msg.chat_id,
                    audio=InputFile(out, filename=fname),
                    caption=f"{Em.AUDIO} {sc('audio extracted as')} {fmt.upper()}",
                    parse_mode=ParseMode.HTML)
                for p in [fp, out]:
                    Path(p).unlink(missing_ok=True)
                if status:
                    await status.delete()
            else:
                if status:
                    await safe_edit(status,
                        f"{Em.ERROR} {sc('audio extraction failed')}.")
        except Exception as e:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    # ──────────── /addfav / /addwatch ────────────────────────────────────────

    async def cmd_addfav(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.HEART} {sc('usage')}: /addfav <code>{sc('anime_id title')}</code>")
            return
        anime_id    = ctx.args[0]
        anime_title = " ".join(ctx.args[1:])
        if self.db.add_favorite(uid, anime_title, anime_id):
            await safe_reply(update,
                f"{Em.HEART} <b>{escape_html(anime_title)}</b> "
                f"{sc('added to favorites')}!")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('already in favorites or error')}.")

    async def cmd_addwatch(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.WATCH} {sc('usage')}: /addwatch <code>{sc('anime_id title')}</code>")
            return
        anime_id    = ctx.args[0]
        anime_title = " ".join(ctx.args[1:])
        if self.db.add_watchlist(uid, anime_title, anime_id):
            await safe_reply(update,
                f"{Em.WATCH} <b>{escape_html(anime_title)}</b> "
                f"{sc('added to watchlist')}!")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('already in watchlist or error')}.")

    # ──────────── /gift / /claimgift ─────────────────────────────────────────

    @premium_only
    async def cmd_gift(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.GIFT} {sc('usage')}: /gift <code>{sc('user_id plan [message]')}</code>\n"
                f"{sc('plans')}: weekly, monthly, yearly, lifetime")
            return
        try:
            to_uid  = int(ctx.args[0])
            plan    = ctx.args[1].lower()
            message = " ".join(ctx.args[2:]) if len(ctx.args) > 2 else ""
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid arguments')}.")
            return
        if plan not in Config.SUBSCRIPTION_DAYS:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid plan')}.")
            return
        days = Config.SUBSCRIPTION_DAYS[plan]
        code = self.db.create_gift(uid, to_uid, plan, days, message)
        await safe_reply(update,
            f"{Em.GIFT} <b>{sc('gift created')}!</b>\n\n"
            f"📋 {sc('plan')}: {plan.upper()} ({days} {sc('days')})\n"
            f"👤 {sc('for user id')}: <code>{to_uid}</code>\n"
            f"🎟 {sc('gift code')}: <code>{code}</code>\n\n"
            f"{sc('tell them')}: /claimgift <code>{code}</code>")

    async def cmd_claimgift(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        uid = self._uid(update)
        if not ctx.args:
            await safe_reply(update,
                f"{Em.GIFT} {sc('usage')}: /claimgift <code>{sc('gift_code')}</code>")
            return
        code = ctx.args[0].upper()
        ok, msg, plan, days = self.db.claim_gift(code, uid)
        if not ok:
            await safe_reply(update, f"{Em.ERROR} {msg}.")
            return
        self.db.add_premium(uid, plan, days, f"gift_{code}", 0)
        await safe_reply(update,
            f"{Em.GIFT} <b>{sc('gift claimed')}!</b>\n\n"
            f"💎 {sc('plan')}: {plan.upper()}\n"
            f"📅 {sc('days')}: {days}\n\n"
            f"{sc('enjoy your premium')}! {Em.FIRE}")

    # ══════════════════════════════════════════════════════════════════════════
    #  ADMIN COMMANDS
    # ══════════════════════════════════════════════════════════════════════════

    @admin_only
    async def cmd_admin(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        counts = self.db.get_user_count()
        q_all  = self.db.get_all_queue()
        maint  = self.db.get_setting("maintenance_mode", "False") == "True"
        text = (
            f"{Em.ADMIN} <b>{sc('admin panel — v200.1')}</b>\n\n"
            f"👥 {sc('users')}: <b>{counts['total']:,}</b> | "
            f"💎 <b>{counts['premium']}</b> {sc('premium')} | "
            f"🚫 <b>{counts['banned']}</b> {sc('banned')}\n"
            f"📋 {sc('queue')}: <b>{len(q_all)}</b> {sc('active')}\n"
            f"🔧 {sc('maintenance')}: "
            f"{'🔴 ON' if maint else '🟢 OFF'}\n\n"
            f"{sc('select an action below')}:"
        )
        await safe_reply(update, text, KB.admin_panel())

    @admin_only
    async def cmd_broadcast(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        msg = self._msg(update)
        if not ctx.args:
            await safe_reply(update,
                f"{Em.BROADCAST} {sc('usage')}: "
                f"/broadcast <code>{sc('message')}</code>\n"
                f"{sc('options')}: --premium-only, --free-only")
            return
        premium_only_flag = "--premium-only" in ctx.args
        free_only_flag    = "--free-only"    in ctx.args
        text = " ".join(a for a in ctx.args
                        if a not in ("--premium-only", "--free-only"))
        if not text:
            await safe_reply(update,
                f"{Em.ERROR} {sc('no message text provided')}.")
            return
        if premium_only_flag:
            users = self.db.get_all_users(premium_only=True)
        elif free_only_flag:
            all_u   = self.db.get_all_users()
            users   = [u for u in all_u if not self.db.is_premium(u)]
        else:
            users = self.db.get_all_users()
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('broadcasting to')} {len(users):,} {sc('users')}…")
        sent = fail = 0
        for uid_bc in users:
            try:
                await ctx.bot.send_message(uid_bc,
                    f"{Em.BROADCAST} <b>{sc('announcement')}</b>\n\n{text}",
                    parse_mode=ParseMode.HTML)
                sent += 1
            except Forbidden:
                fail += 1
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
                try:
                    await ctx.bot.send_message(uid_bc,
                        f"{Em.BROADCAST} <b>{sc('announcement')}</b>\n\n{text}",
                        parse_mode=ParseMode.HTML)
                    sent += 1
                except Exception:
                    fail += 1
            except Exception:
                fail += 1
            if (sent + fail) % 50 == 0:
                try:
                    await status.edit_text(
                        f"{Em.LOADING} {sc('progress')}: {sent+fail}/{len(users):,}",
                        parse_mode=ParseMode.HTML)
                except Exception:
                    pass
            await asyncio.sleep(0.05)
        if status:
            await safe_edit(status,
                f"{Em.SUCCESS} {sc('broadcast complete')}!\n"
                f"✅ {sc('sent')}: {sent:,} | ❌ {sc('failed')}: {fail:,}")

    @admin_only
    async def cmd_ban(self, update: Update,
                      ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.BAN} {sc('usage')}: "
                f"/ban <code>{sc('user_id reason [days]')}</code>")
            return
        try:
            uid    = int(ctx.args[0])
            reason = " ".join(ctx.args[1:-1]) if ctx.args[-1].isdigit() else " ".join(ctx.args[1:])
            days   = int(ctx.args[-1]) if ctx.args[-1].isdigit() else 0
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid arguments')}.")
            return
        self.db.register_user(uid)
        self.db.ban_user(uid, self._uid(update), reason, days)
        until = (f" {sc('until')} "
                 f"{(datetime.now()+timedelta(days=days)).strftime('%Y-%m-%d')}"
                 if days else "")
        await safe_reply(update,
            f"{Em.BAN} {sc('user')} <code>{uid}</code> {sc('banned')}{until}.\n"
            f"{sc('reason')}: {escape_html(reason)}")
        try:
            await ctx.bot.send_message(uid,
                f"{Em.BAN} {sc('you have been banned from this bot')}.\n"
                f"{sc('reason')}: {escape_html(reason)}\n"
                f"{sc('contact')} {Config.SUPPORT_USERNAME} {sc('to appeal')}.",
                parse_mode=ParseMode.HTML)
        except Exception:
            pass

    @admin_only
    async def cmd_unban(self, update: Update,
                        ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await safe_reply(update,
                f"{Em.UNBAN} {sc('usage')}: /unban <code>{sc('user_id')}</code>")
            return
        try:
            uid = int(ctx.args[0])
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid user id')}.")
            return
        self.db.unban_user(uid)
        await safe_reply(update,
            f"{Em.SUCCESS} {sc('user')} <code>{uid}</code> {sc('unbanned')}.")
        try:
            await ctx.bot.send_message(uid,
                f"{Em.SUCCESS} {sc('you have been unbanned. welcome back')}!",
                parse_mode=ParseMode.HTML)
        except Exception:
            pass

    @admin_only
    async def cmd_warn(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.WARNING} {sc('usage')}: /warn <code>{sc('user_id reason')}</code>")
            return
        try:
            uid    = int(ctx.args[0])
            reason = " ".join(ctx.args[1:])
        except Exception:
            await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
            return
        count = self.db.add_warning(uid)
        await safe_reply(update,
            f"{Em.WARNING} {sc('warning sent to')} <code>{uid}</code>. "
            f"({sc('total')}: {count})")
        try:
            await ctx.bot.send_message(uid,
                f"{Em.WARNING} <b>{sc('warning')} #{count}</b>\n"
                f"{sc('reason')}: {escape_html(reason)}\n"
                f"{sc('3 warnings = ban')}.",
                parse_mode=ParseMode.HTML)
        except Exception:
            pass
        if count >= 3:
            self.db.ban_user(uid, self._uid(update), "auto-ban: 3 warnings", 7)
            try:
                await ctx.bot.send_message(uid,
                    f"{Em.BAN} {sc('auto-banned for 7 days: 3 warnings reached')}.",
                    parse_mode=ParseMode.HTML)
            except Exception:
                pass

    @admin_only
    async def cmd_addpremium(self, update: Update,
                             ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.PREMIUM} {sc('usage')}: "
                f"/addpremium <code>{sc('user_id plan [days]')}</code>")
            return
        try:
            uid  = int(ctx.args[0])
            plan = ctx.args[1].lower()
            days = (int(ctx.args[2]) if len(ctx.args) > 2
                    else Config.SUBSCRIPTION_DAYS.get(plan, 30))
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid arguments')}.")
            return
        self.db.register_user(uid)
        if self.db.add_premium(uid, plan, days,
                               f"admin_{uuid.uuid4().hex[:8]}",
                               self._uid(update)):
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('premium')} <code>{plan}</code> ({days}d) "
                f"{sc('added to')} <code>{uid}</code>.")
            try:
                await ctx.bot.send_message(uid,
                    f"{Em.PREMIUM} {sc('you received')} <b>{plan.upper()}</b> "
                    f"{sc('premium for')} {days} {sc('days')}! 🎉",
                    parse_mode=ParseMode.HTML)
            except Exception:
                pass
        else:
            await safe_reply(update, f"{Em.ERROR} {sc('failed')}.")

    @admin_only
    async def cmd_revokepremium(self, update: Update,
                                ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await safe_reply(update,
                f"{Em.PREMIUM} {sc('usage')}: "
                f"/revokepremium <code>{sc('user_id')}</code>")
            return
        try:
            uid = int(ctx.args[0])
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid user id')}.")
            return
        if self.db.revoke_premium(uid):
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('premium revoked from')} <code>{uid}</code>.")
        else:
            await safe_reply(update, f"{Em.ERROR} {sc('failed')}.")

    @admin_only
    async def cmd_gencode(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await safe_reply(update,
                f"{Em.REDEEM} {sc('usage')}: "
                f"/gencode <code>{sc('plan days [max_uses] [exp_days]')}</code>")
            return
        try:
            plan     = ctx.args[0].lower()
            days     = int(ctx.args[1])
            max_uses = int(ctx.args[2]) if len(ctx.args) > 2 else 1
            exp_days = int(ctx.args[3]) if len(ctx.args) > 3 else 30
        except Exception:
            await safe_reply(update,
                f"{Em.ERROR} {sc('invalid arguments')}.")
            return
        code = secrets.token_hex(4).upper()
        if self.db.create_redeem_code(code, plan, days, max_uses,
                                      self._uid(update), exp_days):
            await safe_reply(update,
                f"{Em.SUCCESS} <b>{sc('redeem code created')}!</b>\n\n"
                f"🎟 {sc('code')}: <code>{code}</code>\n"
                f"💎 {sc('plan')}: {plan.upper()} | 📅 {sc('days')}: {days}\n"
                f"♻️ {sc('max uses')}: {max_uses} | ⏰ {sc('expires in')}: {exp_days}d")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('failed to create code')}.")

    @admin_only
    async def cmd_setcookies(self, update: Update,
                             ctx: ContextTypes.DEFAULT_TYPE):
        msg = self._msg(update)
        if not msg:
            return
        target = msg.reply_to_message
        cookies_text = None
        status = None

        if target and target.text:
            cookies_text = target.text
        elif target and target.document:
            status = await safe_reply(update,
                f"{Em.LOADING} {sc('reading cookie file')}…")
            try:
                f  = await ctx.bot.get_file(target.document.file_id)
                fp = str(Config.TEMP_PATH / f"cookies_{uuid.uuid4().hex[:8]}.txt")
                await f.download_to_drive(fp)
                cookies_text = Path(fp).read_text(encoding="utf-8", errors="ignore")
                Path(fp).unlink(missing_ok=True)
            except Exception as e:
                if status:
                    await safe_edit(status,
                        f"{Em.ERROR} {sc('error reading file')}: {e}")
                return
        elif ctx.args:
            cookies_text = " ".join(ctx.args)
        else:
            await safe_reply(update,
                f"{Em.COOKIE} <b>{sc('set crunchyroll cookies')}</b>\n\n"
                f"{sc('reply to a message/file containing cookies with')} /setcookies\n\n"
                f"{sc('accepted formats')}:\n"
                f"• Netscape {sc('cookie file format')}\n"
                f"• JSON {sc('array format (from EditThisCookie extension)')}\n\n"
                f"{sc('how to export')}:\n"
                f"1. {sc('log into crunchyroll.com')}\n"
                f"2. {sc('use EditThisCookie or similar')}\n"
                f"3. {sc('export as json or netscape')}\n"
                f"4. {sc('send the file here and reply with')} /setcookies")
            return

        ok, result = await CookieManager.validate_cookies(cookies_text)
        if not ok:
            if status:
                await safe_edit(status,
                    f"{Em.ERROR} {sc('invalid cookies')}: {result}")
            else:
                await safe_reply(update,
                    f"{Em.ERROR} {sc('invalid cookies')}: {result}")
            return

        self.db.save_cookies(
            b"", result, "", True,
            self._uid(update), 30)
        reply_text = (
            f"{Em.SUCCESS} <b>{sc('cookies saved')}!</b>\n"
            f"✅ {sc('crunchyroll cookies are active')}.")
        if status:
            await safe_edit(status, reply_text)
        else:
            await safe_reply(update, reply_text)

    @admin_only
    async def cmd_fetchnews(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        status = await safe_reply(update,
            f"{Em.LOADING} {sc('fetching crunchyroll news')}…")
        news = await self.downloader.cr.fetch_cr_news()
        saved = 0
        for n in news:
            if self.db.save_news(n["title"], n["description"],
                                 n["url"], n["image_url"], n["published_at"]):
                saved += 1
        if status:
            await safe_edit(status,
                f"{Em.SUCCESS} {sc('fetched')} {len(news)} {sc('articles')}, "
                f"{saved} {sc('new saved')}.")

    # ──────────── /setwelcomeimage (NEW) ─────────────────────────────────────

    @admin_only
    async def cmd_setwelcomeimage(self, update: Update,
                                  ctx: ContextTypes.DEFAULT_TYPE):
        msg    = self._msg(update)
        target = msg.reply_to_message if msg else None
        if not target or not target.photo:
            await safe_reply(update,
                f"{Em.IMAGE} <b>{sc('set welcome image')}</b>\n\n"
                f"{sc('reply to a photo with')} /setwelcomeimage\n\n"
                f"{sc('or use')} /setwelcomeimage clear {sc('to remove')}.")
            return
        if ctx.args and ctx.args[0].lower() == "clear":
            self.db.set_setting("welcome_image_id", "")
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('welcome image removed')}.")
            return
        photo   = target.photo[-1]  # largest size
        file_id = photo.file_id
        self.db.set_setting("welcome_image_id", file_id)
        await safe_reply(update,
            f"{Em.SUCCESS} <b>{sc('welcome image set')}!</b>\n"
            f"{sc('all new users will see this image on')} /start.")

    # ──────────── /welcomepreview (NEW) ──────────────────────────────────────

    @admin_only
    async def cmd_welcomepreview(self, update: Update,
                                 ctx: ContextTypes.DEFAULT_TYPE):
        uid     = self._uid(update)
        img_id  = self.db.get_setting("welcome_image_id", "")
        welcome = self.db.get_setting(
            "welcome_message",
            f"{Em.ANIME} <b>{sc('welcome to crunchyroll ultimate bot')}!</b>")
        text = (
            f"👁️ <b>{sc('welcome screen preview')}</b>\n\n"
            + welcome + "\n\n"
            + f"{sc('this is what new users see when they start the bot')}."
        )
        if img_id:
            try:
                await ctx.bot.send_photo(
                    uid, photo=img_id,
                    caption=text,
                    reply_markup=KB.home(),
                    parse_mode=ParseMode.HTML)
                return
            except Exception:
                pass
        await safe_reply(update, text + f"\n\n⚠️ {sc('no welcome image set')}.")

    # ──────────── /botinfo (NEW) ──────────────────────────────────────────────

    @admin_only
    async def cmd_botinfo(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        counts    = self.db.get_user_count()
        q_all     = self.db.get_all_queue()
        news_cnt  = self.db.conn.execute(
            "SELECT COUNT(*) FROM cr_news").fetchone()[0]
        cmds_cnt  = self.db.conn.execute(
            "SELECT COUNT(*) FROM custom_commands").fetchone()[0]
        codes_cnt = self.db.conn.execute(
            "SELECT COUNT(*) FROM redeem_codes WHERE used_count<max_uses").fetchone()[0]
        img_set   = bool(self.db.get_setting("welcome_image_id", ""))
        maint     = self.db.get_setting("maintenance_mode", "False") == "True"

        db_size = 0
        try:
            db_size = Config.DATABASE_PATH.stat().st_size
        except Exception:
            pass

        me   = await ctx.bot.get_me()
        text = (
            f"🤖 <b>{escape_html(me.first_name)}</b> "
            f"@{me.username}\n"
            f"📌 v200.1 (Fixed + Enhanced)\n\n"
            f"👥 {sc('users')}: <b>{counts['total']:,}</b>\n"
            f"  💎 {sc('premium')}: <b>{counts['premium']}</b>\n"
            f"  🚫 {sc('banned')}: <b>{counts['banned']}</b>\n\n"
            f"📋 {sc('active queue')}: <b>{len(q_all)}</b>\n"
            f"📰 {sc('news articles')}: <b>{news_cnt}</b>\n"
            f"💻 {sc('custom cmds')}: <b>{cmds_cnt}</b>\n"
            f"🎟️ {sc('active codes')}: <b>{codes_cnt}</b>\n\n"
            f"🖼️ {sc('welcome image')}: {'✅ ' + sc('set') if img_set else '❌ ' + sc('not set')}\n"
            f"🔧 {sc('maintenance')}: {'🔴 ON' if maint else '🟢 OFF'}\n"
            f"💾 {sc('db size')}: <b>{format_file_size(db_size)}</b>"
        )
        await safe_reply(update, text, KB.admin_panel())

    @admin_only
    async def cmd_addcmd(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 3:
            await safe_reply(update,
                f"{Em.CODE} {sc('usage')}: "
                f"/addcmd <code>{sc('cmd type response')}</code>\n"
                f"{sc('type')}: text, html, markdown, python")
            return
        cmd      = ctx.args[0].lower().lstrip("/")
        cmd_type = ctx.args[1].lower()
        response = " ".join(ctx.args[2:])
        if self.db.add_custom_cmd(cmd, response, "", cmd_type, self._uid(update)):
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('command')} /{cmd} {sc('added')}.")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('command already exists. use')} /editcmd.")

    @admin_only
    async def cmd_editcmd(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 3:
            await safe_reply(update,
                f"{Em.CODE} {sc('usage')}: "
                f"/editcmd <code>{sc('cmd type response')}</code>")
            return
        cmd      = ctx.args[0].lower().lstrip("/")
        cmd_type = ctx.args[1].lower()
        response = " ".join(ctx.args[2:])
        if self.db.update_custom_cmd(cmd, response, "", cmd_type):
            await safe_reply(update,
                f"{Em.SUCCESS} /{cmd} {sc('updated')}.")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('command not found')}.")

    @admin_only
    async def cmd_delcmd(self, update: Update,
                         ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await safe_reply(update,
                f"{Em.CODE} {sc('usage')}: /delcmd <code>{sc('cmd')}</code>")
            return
        cmd = ctx.args[0].lower().lstrip("/")
        if self.db.remove_custom_cmd(cmd):
            await safe_reply(update,
                f"{Em.SUCCESS} /{cmd} {sc('deleted')}.")
        else:
            await safe_reply(update,
                f"{Em.ERROR} {sc('command not found')}.")

    @admin_only
    async def cmd_listcmds(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        cmds = self.db.list_custom_cmds()
        if not cmds:
            await safe_reply(update,
                f"{Em.CODE} {sc('no custom commands yet')}.")
            return
        lines = [f"{Em.CODE} <b>{sc('custom commands')} ({len(cmds)})</b>\n"]
        for c in cmds:
            lines.append(
                f"/{c['command']} [{c.get('cmd_type','text')}] "
                f"— {c.get('usage_count',0)}x")
        await safe_reply(update, "\n".join(lines), KB.back())

    @admin_only
    async def cmd_userinfo(self, update: Update,
                           ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await safe_reply(update,
                f"{Em.INFO} {sc('usage')}: /userinfo <code>{sc('user_id')}</code>")
            return
        try:
            target_uid = int(ctx.args[0])
        except Exception:
            await safe_reply(update, f"{Em.ERROR} {sc('invalid user id')}.")
            return
        u = self.db.get_user(target_uid)
        if not u:
            await safe_reply(update, f"{Em.ERROR} {sc('user not found')}.")
            return
        is_pm = self.db.is_premium(target_uid)
        text = (
            f"{Em.INFO} <b>{sc('user info')}</b>\n\n"
            f"👤 {escape_html(u.get('first_name','?'))}"
            f" @{u.get('username') or sc('none')}\n"
            f"🆔 <code>{target_uid}</code>\n"
            f"💎 {sc('plan')}: <b>{u.get('premium_type','free').upper()}</b>\n"
            f"📅 {sc('expiry')}: {str(u.get('premium_expiry',''))[:16] or 'N/A'}\n"
            f"🚫 {sc('banned')}: {'Yes' if u.get('is_banned') else 'No'}\n"
            f"⚠️ {sc('warnings')}: {u.get('warnings',0)}\n"
            f"📥 {sc('downloads')}: {u.get('total_downloads',0):,}\n"
            f"📅 {sc('joined')}: {str(u.get('joined_at',''))[:10]}"
        )
        await safe_reply(update, text, KB.back("adm_back"))

    @admin_only
    async def cmd_maintenance(self, update: Update,
                              ctx: ContextTypes.DEFAULT_TYPE):
        current = self.db.get_setting("maintenance_mode", "False") == "True"
        new_val = "False" if current else "True"
        self.db.set_setting("maintenance_mode", new_val)
        await safe_reply(update,
            f"{'🔴' if new_val == 'True' else '🟢'} {sc('maintenance mode')} "
            f"{'enabled' if new_val == 'True' else 'disabled'}.")

    @admin_only
    async def cmd_authgroup(self, update: Update,
                            ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 1:
            await safe_reply(update,
                f"{Em.AUTH} {sc('usage')}: "
                f"/authgroup <code>add|remove group_id [name] [link]</code>")
            return
        action = ctx.args[0].lower()
        if action == "add" and len(ctx.args) >= 2:
            gid  = int(ctx.args[1])
            name = ctx.args[2] if len(ctx.args) > 2 else str(gid)
            link = ctx.args[3] if len(ctx.args) > 3 else ""
            self.db.add_auth_group(gid, name, link, self._uid(update))
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('auth group added')}: {gid}")
        elif action == "remove" and len(ctx.args) >= 2:
            gid = int(ctx.args[1])
            self.db.remove_auth_group(gid)
            await safe_reply(update,
                f"{Em.SUCCESS} {sc('auth group removed')}: {gid}")
        else:
            groups = self.db.get_auth_groups()
            lines  = [f"{Em.AUTH} <b>{sc('auth groups')} ({len(groups)})</b>"]
            for g in groups:
                lines.append(f"• {g['group_id']} — {g.get('group_name','?')}")
            await safe_reply(update, "\n".join(lines))

    @admin_only
    async def cmd_clearqueue(self, update: Update,
                             ctx: ContextTypes.DEFAULT_TYPE):
        self.db.clear_queue()
        await safe_reply(update,
            f"{Em.SUCCESS} {sc('all pending queue items cancelled')}.")

    @admin_only
    async def cmd_logs(self, update: Update,
                       ctx: ContextTypes.DEFAULT_TYPE):
        log_file = Config.LOG_PATH / "bot.log"
        if not log_file.exists():
            await safe_reply(update, f"{Em.ERROR} {sc('no log file found')}.")
            return
        try:
            with open(log_file, "rb") as fh:
                content = fh.read()[-30_000:]  # last 30KB
            await ctx.bot.send_document(
                update.effective_chat.id,
                document=InputFile(io.BytesIO(content), filename="bot.log"),
                caption=f"{Em.LOG} {sc('last 30kb of bot log')}",
                parse_mode=ParseMode.HTML)
        except Exception as e:
            await safe_reply(update,
                f"{Em.ERROR} {sc('error')}: {escape_html(str(e))}")

    @admin_only
    async def cmd_restart(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        await safe_reply(update,
            f"{Em.ROCKET} {sc('restarting bot process')}…")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # ──────────── callback query handler ─────────────────────────────────────

    async def handle_callback(self, update: Update,
                              ctx: ContextTypes.DEFAULT_TYPE):
        q    = update.callback_query
        if not q:
            return
        await q.answer()
        data = q.data or ""
        uid  = self._uid(update)

        # ── home / navigation ──────────────────────────────────────────────
        if data == "show_home":
            is_pm = self.db.is_premium(uid)
            text  = (
                f"{Em.ANIME} <b>{sc('crunchyroll ultimate bot v200.1')}</b>\n\n"
                f"{'💎 ' + sc('premium member') if is_pm else '🆓 ' + sc('free user')}\n\n"
                f"{sc('send a crunchyroll url or use the menu')}:"
            )
            welcome_img = self.db.get_setting("welcome_image_id", "")
            if welcome_img:
                try:
                    await q.message.delete()
                    await ctx.bot.send_photo(
                        uid, photo=welcome_img,
                        caption=text, reply_markup=KB.home(),
                        parse_mode=ParseMode.HTML)
                    return
                except Exception:
                    pass
            await safe_edit(q.message, text, KB.home())

        elif data == "show_download":
            await safe_edit(q.message,
                f"{Em.DOWNLOAD} <b>{sc('download options')}</b>\n\n"
                f"{sc('send me a crunchyroll url, or use a command below')}:",
                KB.download_menu())

        elif data == "show_premium":
            is_pm = self.db.is_premium(uid)
            user  = self.db.get_user(uid) or {}
            text  = (
                f"{Em.PREMIUM} <b>{sc('premium membership')}</b>\n\n"
                + (f"💎 {sc('you are premium')}!\n" if is_pm else
                   f"🆓 {sc('free plan — upgrade for unlimited access')}\n\n")
            )
            for plan, price in Config.SUBSCRIPTION_PRICES.items():
                feats = ", ".join(Config.SUBSCRIPTION_FEATURES.get(plan, [])[:2])
                text += f"• <b>{plan.upper()}</b>: {price}⭐ — {feats}\n"
            await safe_edit(q.message, text, KB.premium_plans())

        elif data == "show_stats":
            user  = self.db.get_user(uid) or {}
            is_pm = self.db.is_premium(uid)
            text  = (
                f"{Em.STATS} <b>{sc('your stats')}</b>\n\n"
                f"💎 {sc('plan')}: {'PREMIUM' if is_pm else 'FREE'}\n"
                f"📥 {sc('downloads')}: {user.get('total_downloads',0):,}\n"
                f"📦 {sc('size')}: "
                f"{format_file_size(user.get('total_size',0) or 0)}\n"
                f"👥 {sc('referrals')}: {user.get('referral_count',0)}"
            )
            await safe_edit(q.message, text, KB.user_profile(uid, is_pm))

        elif data == "show_settings":
            user = self.db.get_user(uid) or {}
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('settings')}</b>",
                KB.settings(user))

        elif data == "show_queue":
            items = self.db.get_user_queue(uid)
            if not items:
                await safe_edit(q.message,
                    f"{Em.QUEUE} {sc('your queue is empty')}.",
                    KB.back())
            else:
                lines = [f"{Em.QUEUE} <b>{sc('queue')} ({len(items)})</b>\n"]
                for it in items:
                    lane = "⚡" if it.get("is_fast") else "🐢"
                    lines.append(f"#{it['id']} {lane} {it['quality']} "
                                 f"{it['progress']}%")
                await safe_edit(q.message, "\n".join(lines), KB.back())

        elif data == "show_history":
            items = self.db.get_user_history(uid, 10)
            if not items:
                await safe_edit(q.message,
                    f"{Em.HISTORY} {sc('no history yet')}.", KB.back())
            else:
                lines = [f"{Em.HISTORY} <b>{sc('history')} ({len(items)})</b>\n"]
                for it in items:
                    icon = "✅" if it["status"] == "completed" else "❌"
                    lines.append(f"{icon} #{it['id']} {it.get('quality','?')}")
                await safe_edit(q.message, "\n".join(lines), KB.back())

        elif data == "show_news":
            items = self.db.get_latest_news(5)
            if not items:
                await safe_edit(q.message,
                    f"{Em.NEWS} {sc('no news yet')}.", KB.back())
            else:
                text = f"{Em.NEWS} <b>{sc('crunchyroll news')}</b>\n\n"
                for n in items:
                    text += (f"📰 <b>{escape_html(n['title'])}</b>\n"
                             f"{str(n.get('published_at',''))[:16]}\n\n")
                await safe_edit(q.message, text, KB.news_nav(items))

        elif data == "show_referral":
            code = self.db.get_referral_code(uid)
            cnt  = self.db.get_referral_count(uid)
            pts  = self.db.get_referral_points(uid)
            me   = await ctx.bot.get_me()
            link = f"https://t.me/{me.username}?start=ref_{code}"
            text = (
                f"{Em.REFERRAL} <b>{sc('referral')}</b>\n\n"
                f"🔗 <code>{link}</code>\n\n"
                f"👥 {sc('referrals')}: <b>{cnt}</b>\n"
                f"💰 {sc('points')}: <b>{pts}</b>"
            )
            await safe_edit(q.message, text, KB.referral_menu())

        elif data == "show_favorites":
            items = self.db.get_favorites(uid)
            lines = ([f"{Em.HEART} <b>{sc('favorites')} ({len(items)})</b>\n"]
                     + [f"{i}. {escape_html(it['anime_title'])}"
                        for i, it in enumerate(items[:20], 1)])
            await safe_edit(q.message,
                "\n".join(lines) if items else
                f"{Em.HEART} {sc('no favorites yet')}.",
                KB.back())

        elif data == "show_watchlist":
            items = self.db.get_watchlist(uid)
            lines = ([f"{Em.WATCH} <b>{sc('watchlist')} ({len(items)})</b>\n"]
                     + [f"{i}. {escape_html(it['anime_title'])}"
                        for i, it in enumerate(items[:20], 1)])
            await safe_edit(q.message,
                "\n".join(lines) if items else
                f"{Em.WATCH} {sc('watchlist is empty')}.",
                KB.back())

        elif data == "show_leaderboard":
            rows  = self.db.get_leaderboard(10)
            medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 10
            lines  = [f"{Em.LEAD} <b>{sc('leaderboard')}</b>\n"]
            for i, r in enumerate(rows, 0):
                lines.append(
                    f"{medals[i]} {escape_html(r.get('first_name','?'))} "
                    f"— {r.get('total_downloads',0):,}")
            await safe_edit(q.message, "\n".join(lines), KB.back())

        # ── settings config ────────────────────────────────────────────────
        elif data == "cfg_quality":
            is_pm = self.db.is_premium(uid)
            await safe_edit(q.message,
                f"{Em.QUALITY} <b>{sc('select quality')}</b>:",
                KB.quality(is_pm))

        elif data == "cfg_preset":
            await safe_edit(q.message,
                f"{Em.ENCODE} <b>{sc('select encode preset')}</b>:",
                KB.encode_preset())

        elif data == "cfg_notify":
            user = self.db.get_user(uid) or {}
            current = user.get("notify_complete", 1)
            new_val = 0 if current else 1
            self.db.set_user_setting(uid, "notify_complete", str(new_val))
            user = self.db.get_user(uid) or {}
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('settings')}</b>",
                KB.settings(user))

        elif data == "cfg_language":
            await safe_edit(q.message,
                f"{Em.GLOBE} <b>{sc('select language')}</b>:",
                KB.language_picker())

        elif data.startswith("lang_"):
            lang = data[5:]
            self.db.set_user_setting(uid, "language", lang)
            await safe_edit(q.message,
                f"{Em.SUCCESS} {sc('language updated')}.",
                KB.back("show_settings"))

        elif data.startswith("set_quality_"):
            quality = data[12:]
            is_pm   = self.db.is_premium(uid)
            if quality in Config.PREMIUM_QUALITIES and not is_pm:
                await q.answer(
                    f"🔒 {sc('premium required for')} {quality}",
                    show_alert=True)
                return
            self.db.set_user_setting(uid, "default_quality", quality)
            user = self.db.get_user(uid) or {}
            await safe_edit(q.message,
                f"{Em.SUCCESS} {sc('quality set to')} <b>{quality}</b>",
                KB.settings(user))

        elif data.startswith("set_preset_"):
            preset = data[11:]
            self.db.set_user_setting(uid, "encode_preset", preset)
            user = self.db.get_user(uid) or {}
            await safe_edit(q.message,
                f"{Em.SUCCESS} {sc('preset set to')} <b>{preset}</b>",
                KB.settings(user))

        # ── premium buy ────────────────────────────────────────────────────
        elif data.startswith("buy_"):
            plan  = data[4:]
            stars = Config.SUBSCRIPTION_PRICES.get(plan, 0)
            if plan not in Config.SUBSCRIPTION_PRICES:
                await q.answer(sc("invalid plan"), show_alert=True)
                return
            features = "\n".join(
                f"• {f}" for f in Config.SUBSCRIPTION_FEATURES.get(plan, []))
            try:
                await ctx.bot.send_invoice(
                    chat_id=uid,
                    title=f"{sc('crunchyroll')} {plan.upper()} {sc('premium')}",
                    description=f"{sc('features')}:\n{features}",
                    payload=f"premium_{plan}_{uid}",
                    currency="XTR",
                    prices=[LabeledPrice(
                        label=f"{plan.upper()} {sc('premium')}",
                        amount=stars)],
                )
            except Exception as e:
                await q.answer(f"{sc('error starting payment')}: {e}",
                               show_alert=True)

        # ── cancel download ────────────────────────────────────────────────
        elif data.startswith("cancel_dl_"):
            qid = int(data[10:])
            if self.db.cancel_queue_item(qid, uid):
                await safe_edit(q.message,
                    f"{Em.SUCCESS} {sc('download')} #{qid} {sc('cancelled')}.",
                    None)
            else:
                await q.answer(
                    sc("cannot cancel — already processing or not yours"),
                    show_alert=True)

        # ── auth check ─────────────────────────────────────────────────────
        elif data == "auth_check":
            ok, links = await AuthChecker.check_user(ctx.bot, uid, self.db)
            if ok:
                await safe_edit(q.message,
                    f"{Em.SUCCESS} <b>{sc('access granted')}!</b>",
                    KB.home())
            else:
                await q.answer(
                    sc("you still haven't joined all required channels"),
                    show_alert=True)

        # ── ADMIN PANEL CALLBACKS (FIX-04) ─────────────────────────────────
        elif data == "adm_back" and uid in Config.ADMIN_IDS:
            counts = self.db.get_user_count()
            q_all  = self.db.get_all_queue()
            maint  = self.db.get_setting("maintenance_mode","False") == "True"
            text = (
                f"{Em.ADMIN} <b>{sc('admin panel')}</b>\n\n"
                f"👥 {counts['total']:,} | 💎 {counts['premium']} | "
                f"🚫 {counts['banned']}\n"
                f"📋 {sc('queue')}: {len(q_all)}\n"
                f"🔧 {sc('maintenance')}: {'🔴 ON' if maint else '🟢 OFF'}"
            )
            await safe_edit(q.message, text, KB.admin_panel())

        elif data == "adm_stats" and uid in Config.ADMIN_IDS:
            counts = self.db.get_user_count()
            q_all  = self.db.get_all_queue()
            total_dl = self.db.conn.execute(
                "SELECT SUM(total_downloads) FROM users").fetchone()[0] or 0
            total_sz = self.db.conn.execute(
                "SELECT SUM(total_size) FROM users").fetchone()[0] or 0
            await safe_edit(q.message,
                f"{Em.ADMIN} <b>{sc('bot statistics')}</b>\n\n"
                f"👥 {sc('total users')}: <b>{counts['total']:,}</b>\n"
                f"💎 {sc('premium')}: <b>{counts['premium']}</b>\n"
                f"🆓 {sc('free')}: <b>{counts['free']}</b>\n"
                f"🚫 {sc('banned')}: <b>{counts['banned']}</b>\n\n"
                f"📥 {sc('total downloads')}: <b>{total_dl:,}</b>\n"
                f"📦 {sc('total size')}: <b>{format_file_size(total_sz)}</b>\n"
                f"📋 {sc('active queue')}: <b>{len(q_all)}</b>",
                KB.admin_panel())

        elif data == "adm_analytics" and uid in Config.ADMIN_IDS:
            # Top 5 downloaders
            top    = self.db.get_leaderboard(5)
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
            lines  = [f"📈 <b>{sc('analytics')}</b>\n\n"
                      f"<b>{sc('top 5 downloaders')}</b>:"]
            for i, r in enumerate(top):
                lines.append(
                    f"{medals[i]} {escape_html(r.get('first_name','?'))} "
                    f"— {r.get('total_downloads',0):,}")
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_queue" and uid in Config.ADMIN_IDS:
            items = self.db.get_all_queue()
            lines = [f"{Em.QUEUE} <b>{sc('global queue')} ({len(items)})</b>\n"]
            for it in items[:20]:
                lane = "⚡" if it.get("is_fast") else "🐢"
                lines.append(
                    f"#{it['id']} {lane} uid={it['user_id']} | "
                    f"{it['quality']} | {it['status']} {it['progress']}%")
            if not items:
                lines.append(sc("queue is empty"))
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_clearqueue_confirm" and uid in Config.ADMIN_IDS:
            await safe_edit(q.message,
                f"⚠️ <b>{sc('confirm clear all pending queue items?')}</b>",
                KB.confirm("adm_clearqueue_yes", "adm_back"))

        elif data == "adm_clearqueue_yes" and uid in Config.ADMIN_IDS:
            self.db.clear_queue()
            await safe_edit(q.message,
                f"{Em.SUCCESS} {sc('queue cleared')}.", KB.admin_panel())

        elif data == "adm_broadcast_menu" and uid in Config.ADMIN_IDS:
            await safe_edit(q.message,
                f"{Em.BROADCAST} <b>{sc('broadcast options')}</b>\n\n"
                f"{sc('use')} /broadcast <code>{sc('message')}</code>\n"
                f"{sc('flags')}: --premium-only | --free-only",
                KB.admin_broadcast())

        elif data == "adm_premium" and uid in Config.ADMIN_IDS:
            counts = self.db.get_user_count()
            await safe_edit(q.message,
                f"{Em.PREMIUM} <b>{sc('premium management')}</b>\n\n"
                f"💎 {sc('active premium users')}: <b>{counts['premium']}</b>\n\n"
                f"/addpremium <code>uid plan days</code>\n"
                f"/revokepremium <code>uid</code>\n"
                f"/gencode <code>plan days</code>",
                KB.admin_premium())

        elif data == "adm_settings" and uid in Config.ADMIN_IDS:
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_toggle_maintenance" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("maintenance_mode","False") == "True"
            self.db.set_setting("maintenance_mode",
                                "False" if current else "True")
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_toggle_forcesub" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("force_sub_enabled","False") == "True"
            self.db.set_setting("force_sub_enabled",
                                "False" if current else "True")
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_toggle_news" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("news_enabled","True") == "True"
            self.db.set_setting("news_enabled",
                                "False" if current else "True")
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_toggle_ratelimit" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("rate_limit_enabled","True") == "True"
            self.db.set_setting("rate_limit_enabled",
                                "False" if current else "True")
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_cmds" and uid in Config.ADMIN_IDS:
            cmds  = self.db.list_custom_cmds()
            lines = [f"{Em.CODE} <b>{sc('custom commands')} ({len(cmds)})</b>\n"]
            for c in cmds[:20]:
                lines.append(f"/{c['command']} [{c.get('cmd_type','text')}]")
            if not cmds:
                lines.append(sc("no custom commands"))
            lines.append(f"\n{sc('use')} /addcmd /editcmd /delcmd")
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_auth" and uid in Config.ADMIN_IDS:
            groups = self.db.get_auth_groups()
            lines  = [f"{Em.AUTH} <b>{sc('auth groups')} ({len(groups)})</b>\n"]
            for g in groups:
                lines.append(
                    f"• {g['group_id']} — {g.get('group_name','?')} "
                    f"{'🔗 ' + g['group_link'] if g.get('group_link') else ''}")
            if not groups:
                lines.append(sc("no auth groups configured"))
            lines.append(f"\n{sc('use')} /authgroup add|remove")
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_news" and uid in Config.ADMIN_IDS:
            items = self.db.get_latest_news(5)
            lines = [f"{Em.NEWS} <b>{sc('cr news')} ({len(items)})</b>\n"]
            for n in items:
                lines.append(f"📰 {escape_html(n['title'][:50])}")
            if not items:
                lines.append(sc("no news fetched yet"))
            lines.append(f"\n{sc('use')} /fetchnews {sc('to refresh')}")
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_cookies" and uid in Config.ADMIN_IDS:
            row = self.db.get_active_cookies()
            if row:
                cj = json.loads(row.get("cookies_json", "[]") or "[]")
                await safe_edit(q.message,
                    f"{Em.COOKIE} <b>{sc('active cookies')}</b>\n\n"
                    f"📊 {sc('count')}: {len(cj)}\n"
                    f"💎 {sc('premium')}: {'✅' if row.get('is_premium') else '❌'}\n"
                    f"📅 {sc('expires')}: "
                    f"{str(row.get('expires_at','?'))[:16]}\n\n"
                    f"{sc('use')} /setcookies {sc('to update')}.",
                    KB.admin_panel())
            else:
                await safe_edit(q.message,
                    f"{Em.COOKIE} <b>{sc('no cookies configured')}</b>\n\n"
                    f"{sc('use')} /setcookies.",
                    KB.admin_panel())

        elif data == "adm_logs" and uid in Config.ADMIN_IDS:
            log_file = Config.LOG_PATH / "bot.log"
            size_str = ""
            if log_file.exists():
                size_str = format_file_size(log_file.stat().st_size)
            await safe_edit(q.message,
                f"{Em.LOG} <b>{sc('logs')}</b>\n\n"
                f"📁 {sc('log file size')}: {size_str or 'N/A'}\n\n"
                f"{sc('use')} /logs {sc('to download log file')}.",
                KB.admin_panel())

        elif data == "adm_welcome_image" and uid in Config.ADMIN_IDS:
            has_img = bool(self.db.get_setting("welcome_image_id", ""))
            await safe_edit(q.message,
                f"{Em.IMAGE} <b>{sc('welcome image')}</b>\n\n"
                f"{sc('current')}: "
                f"{'✅ ' + sc('image set') if has_img else '❌ ' + sc('not set')}\n\n"
                f"{sc('use')} /setwelcomeimage {sc('to update')}\n"
                f"{sc('use')} /welcomepreview {sc('to preview')}.",
                KB.admin_welcome_image(has_img))

        elif data == "adm_welcome_img_remove" and uid in Config.ADMIN_IDS:
            self.db.set_setting("welcome_image_id", "")
            await safe_edit(q.message,
                f"{Em.SUCCESS} {sc('welcome image removed')}.",
                KB.admin_panel())

        elif data == "adm_welcome_preview" and uid in Config.ADMIN_IDS:
            img_id = self.db.get_setting("welcome_image_id", "")
            if img_id:
                try:
                    await ctx.bot.send_photo(
                        uid, photo=img_id,
                        caption=f"👁️ {sc('welcome screen preview')}",
                        reply_markup=KB.home(),
                        parse_mode=ParseMode.HTML)
                except Exception as e:
                    await q.answer(str(e), show_alert=True)

        elif data == "adm_welcome_text" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("welcome_message", "(default)")
            await safe_edit(q.message,
                f"✏️ <b>{sc('welcome text')}</b>\n\n"
                f"{sc('current')}:\n{current}\n\n"
                f"{sc('to update, use')} /setmsg welcome_message <code>{sc('new text')}</code>",
                KB.admin_panel())

        elif data == "adm_maintenance" and uid in Config.ADMIN_IDS:
            current = self.db.get_setting("maintenance_mode","False") == "True"
            self.db.set_setting("maintenance_mode",
                                "False" if current else "True")
            new = self.db.get_setting("maintenance_mode","False") == "True"
            await q.answer(
                f"🔴 {sc('maintenance on')}" if new else
                f"🟢 {sc('maintenance off')}",
                show_alert=True)
            await safe_edit(q.message,
                f"{Em.SETTINGS} <b>{sc('bot settings')}</b>",
                KB.admin_settings_panel(self.db))

        elif data == "adm_dbbackup" and uid in Config.ADMIN_IDS:
            dest = str(Config.DATA_PATH /
                       f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            try:
                with sqlite3.connect(dest) as bkp:
                    self.db.conn.backup(bkp)
                await ctx.bot.send_document(
                    uid,
                    document=InputFile(dest, filename=Path(dest).name),
                    caption=f"{Em.SUCCESS} {sc('database backup')}",
                    parse_mode=ParseMode.HTML)
                Path(dest).unlink(missing_ok=True)
            except Exception as e:
                await q.answer(str(e), show_alert=True)

        elif data == "adm_vacuum" and uid in Config.ADMIN_IDS:
            try:
                self.db.conn.execute("VACUUM")
                self.db.conn.commit()
                await q.answer(f"✅ {sc('database vacuumed')}", show_alert=True)
            except Exception as e:
                await q.answer(str(e), show_alert=True)

        elif data == "adm_diagnostics" and uid in Config.ADMIN_IDS:
            results   = await _run_diagnostics()
            report    = _format_diagnostics(results)
            all_ok    = all(results.values())
            report += "\n\n" + ("✅ " + sc("all systems ok") if all_ok
                                else "⚠️ " + sc("some checks failed"))
            await safe_edit(q.message, report, KB.admin_panel())

        elif data == "adm_exportusers" and uid in Config.ADMIN_IDS:
            c   = self.db.conn.execute(
                "SELECT user_id,username,first_name,premium_type,"
                "total_downloads,total_size,is_banned,joined_at "
                "FROM users ORDER BY joined_at DESC")
            rows  = c.fetchall()
            lines = ["user_id,username,first_name,premium_type,"
                     "total_downloads,total_size_bytes,is_banned,joined_at"]
            for r in rows:
                lines.append(",".join(str(x or "") for x in r))
            csv_data = "\n".join(lines).encode("utf-8")
            fname    = f"users_{datetime.now().strftime('%Y%m%d')}.csv"
            await ctx.bot.send_document(
                uid,
                document=InputFile(io.BytesIO(csv_data), filename=fname),
                caption=f"{Em.STATS} {sc('user export')}",
                parse_mode=ParseMode.HTML)

        elif data == "adm_redeemcodes" and uid in Config.ADMIN_IDS:
            c    = self.db.conn.execute(
                "SELECT code,plan_type,days,used_count,max_uses,expires_at "
                "FROM redeem_codes ORDER BY created_at DESC LIMIT 10")
            rows  = c.fetchall()
            lines = [f"🎟️ <b>{sc('redeem codes')}</b>\n"]
            for r in rows:
                used = r[3] >= r[4]
                icon = "❌" if used else "✅"
                lines.append(
                    f"{icon} <code>{r[0]}</code> | {r[1].upper()} {r[2]}d | "
                    f"{r[3]}/{r[4]}")
            if not rows:
                lines.append(sc("no codes yet"))
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_banned_list" and uid in Config.ADMIN_IDS:
            c    = self.db.conn.execute(
                "SELECT user_id,first_name,banned_reason FROM users "
                "WHERE is_banned=1 LIMIT 20")
            rows  = c.fetchall()
            lines = [f"🚫 <b>{sc('banned users')} ({len(rows)})</b>\n"]
            for r in rows:
                lines.append(
                    f"<code>{r[0]}</code> {escape_html(r[1] or '?')} "
                    f"— {escape_html(r[2] or '?')[:30]}")
            if not rows:
                lines.append(sc("no banned users"))
            await safe_edit(q.message, "\n".join(lines), KB.admin_panel())

        elif data == "adm_user_search" and uid in Config.ADMIN_IDS:
            await safe_edit(q.message,
                f"🔍 <b>{sc('user search')}</b>\n\n"
                f"{sc('use')} /userinfo <code>{sc('user_id')}</code>",
                KB.admin_panel())

        elif data == "adm_close" and uid in Config.ADMIN_IDS:
            try:
                await q.message.delete()
            except Exception:
                await safe_edit(q.message,
                    f"{Em.SUCCESS} {sc('panel closed')}.", None)

        else:
            logger.debug(f"Unhandled callback: {data!r} from uid={uid}")

    # ──────────── pre-checkout handler ────────────────────────────────────────

    async def handle_precheckout(self, update: Update,
                                 ctx: ContextTypes.DEFAULT_TYPE):
        query = update.pre_checkout_query
        if not query:
            return
        await query.answer(ok=True)

    async def handle_successful_payment(self, update: Update,
                                        ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not msg or not msg.successful_payment:
            return
        payload = msg.successful_payment.invoice_payload
        uid     = self._uid(update)
        # payload: "premium_<plan>_<uid>"
        parts = payload.split("_")
        if len(parts) >= 2 and parts[0] == "premium":
            plan = parts[1]
            days = Config.SUBSCRIPTION_DAYS.get(plan, 30)
            self.db.add_premium(uid, plan, days,
                                msg.successful_payment.telegram_payment_charge_id,
                                0)
            await msg.reply_text(
                f"{Em.SUCCESS} <b>{sc('payment confirmed')}!</b>\n\n"
                f"💎 {sc('you are now')} <b>{plan.upper()}</b> {sc('premium for')} "
                f"{days} {sc('days')}!\n\n"
                f"{Em.FIRE} {sc('enjoy your premium access')}!",
                parse_mode=ParseMode.HTML)
            await log_to_channel(
                ctx.bot,
                f"💳 {sc('payment from')} <code>{uid}</code>: {plan} {days}d",
                self.db)

    # ──────────── text handler ────────────────────────────────────────────────

    async def handle_text(self, update: Update,
                          ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not msg or not msg.text:
            return
        uid  = self._uid(update)
        text = msg.text.strip()

        if self.db.is_banned(uid):
            return

        # Auto-detect CR URLs
        if self.downloader.cr.is_valid_url(text):
            ctx.args = [text]
            await self.cmd_cr(update, ctx)
            return

        # Custom commands
        if text.startswith("/"):
            cmd  = text[1:].split()[0].lower().split("@")[0]
            data = self.db.get_custom_cmd(cmd)
            if data:
                if data["cmd_type"] == "python" and data.get("code"):
                    ctx_vars = {
                        "user_id":    uid,
                        "username":   msg.from_user.username or "",
                        "first_name": msg.from_user.first_name or "",
                        "chat_id":    msg.chat_id,
                        "is_premium": self.db.is_premium(uid),
                    }
                    ok, output = CodeSandbox.run(data["code"], ctx_vars)
                    await msg.reply_text(output[:4096], parse_mode=None)
                elif data["cmd_type"] == "html":
                    await msg.reply_text(data["response"],
                                         parse_mode=ParseMode.HTML)
                elif data["cmd_type"] == "markdown":
                    await msg.reply_text(data["response"],
                                         parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    await msg.reply_text(data["response"])

    # ──────────── queue worker ────────────────────────────────────────────────

    async def _queue_worker(self):
        logger.info(f"⚡ {sc('queue worker started')}")
        while True:
            try:
                item = self.db.get_next_queue_item(fast_lane=True)
                if not item:
                    item = self.db.get_next_queue_item(fast_lane=False)
                if not item:
                    await asyncio.sleep(2)
                    continue

                qid     = item["id"]
                uid     = item["user_id"]
                url     = item["url"]
                quality = item["quality"]
                preset  = item["encode_preset"]
                chat_id = item.get("chat_id")
                msg_id  = item.get("message_id")
                is_fast = item.get("is_fast", 0)

                self.db.start_processing(qid)
                app_ref = self._app

                async def progress_cb(pct: int, stage: str = ""):
                    if not app_ref or not chat_id:
                        return
                    self.db.update_queue_progress(qid, pct)
                    try:
                        lane_icon = f"{Em.FAST}" if is_fast else f"{Em.SLOW}"
                        await app_ref.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=msg_id,
                            text=(
                                f"{lane_icon} <b>#{qid}</b>"
                                + (f" — {stage}" if stage else "") + "\n\n"
                                f"{ProgressBar.make(pct)}\n"
                                f"<code>{url[:50]}…</code>"
                            ),
                            parse_mode=ParseMode.HTML,
                        )
                    except Exception as e:
                        logger.debug(f"progress_cb: {e}")

                ok, result = await self.downloader.process(
                    qid, uid, url, quality, preset, progress_cb)

                if ok and app_ref:
                    try:
                        file_path = result
                        file_size = Path(file_path).stat().st_size
                        size_mb   = round(file_size / (1024 * 1024), 2)
                        fname     = Path(file_path).name
                        lane_icon = f"{Em.FAST}" if is_fast else f"{Em.SLOW}"
                        caption   = (
                            f"{Em.SUCCESS} <b>{sc('download complete')}!</b>\n\n"
                            f"{lane_icon} {sc('lane')}: "
                            f"{'fast (premium)' if is_fast else 'slow (free)'}\n"
                            f"📁 <code>{fname[:60]}</code>\n"
                            f"📦 {size_mb} MB | <code>{quality}</code>\n\n"
                            f"{Em.SUPPORT} {Config.SUPPORT_USERNAME}"
                        )
                        if file_size <= 50 * 1024 * 1024:
                            with open(file_path, "rb") as fh:
                                await app_ref.bot.send_document(
                                    chat_id=chat_id,
                                    document=InputFile(fh, filename=fname),
                                    caption=caption,
                                    parse_mode=ParseMode.HTML)
                        else:
                            await app_ref.bot.send_message(
                                chat_id=chat_id,
                                text=(
                                    f"{Em.SUCCESS} <b>{sc('download complete')}!</b>\n"
                                    f"📁 <code>{fname}</code> — {size_mb} MB\n\n"
                                    f"⚠️ {sc('file >50mb. contact')} "
                                    f"{Config.SUPPORT_USERNAME} {sc('for transfer')}."
                                ),
                                parse_mode=ParseMode.HTML)
                        try:
                            Path(file_path).unlink(missing_ok=True)
                        except Exception:
                            pass
                        if msg_id and chat_id:
                            try:
                                await app_ref.bot.delete_message(chat_id, msg_id)
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(f"queue_worker send: {e}")
                        if chat_id:
                            try:
                                await app_ref.bot.send_message(
                                    chat_id,
                                    f"{Em.SUCCESS} {sc('complete but send failed')}: {e}",
                                    parse_mode=ParseMode.HTML)
                            except Exception:
                                pass

                elif not ok and app_ref and chat_id:
                    try:
                        await app_ref.bot.send_message(
                            chat_id,
                            f"{Em.ERROR} <b>{sc('download failed')}!</b>\n\n"
                            f"<code>{result[:300]}</code>\n\n"
                            f"{sc('contact')} {Config.SUPPORT_USERNAME}",
                            parse_mode=ParseMode.HTML)
                        if msg_id:
                            try:
                                await app_ref.bot.delete_message(chat_id, msg_id)
                            except Exception:
                                pass
                    except Exception:
                        pass

                await asyncio.sleep(0.5)

            except asyncio.CancelledError:
                logger.info(f"⏹ {sc('queue worker cancelled')}")
                break
            except Exception as e:
                logger.exception(f"queue_worker: {e}")
                await asyncio.sleep(5)

    # ──────────── scheduler worker ────────────────────────────────────────────

    async def _scheduler_worker(self):
        logger.info(f"⏰ {sc('scheduler started')}")
        while True:
            try:
                items = self.db.get_pending_scheduled()
                for it in items:
                    uid  = it["user_id"]
                    qid  = self.db.add_to_queue(
                        uid, it["url"], it["quality"], it["encode_preset"])
                    self.db.mark_scheduled_done(it["id"])
                    if self._app:
                        try:
                            await self._app.bot.send_message(
                                uid,
                                f"{Em.SCHEDULE} <b>{sc('scheduled download started')}!</b>\n"
                                f"#{qid}",
                                parse_mode=ParseMode.HTML)
                        except Exception:
                            pass
                self._ensure_queue_running()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"scheduler: {e}")
            await asyncio.sleep(60)

    # ──────────── news worker ─────────────────────────────────────────────────

    async def _news_worker(self):
        logger.info(f"📰 {sc('news worker started')}")
        while True:
            try:
                if self.db.get_setting("news_enabled", "True") == "True":
                    news = await self.downloader.cr.fetch_cr_news()
                    for n in news:
                        self.db.save_news(
                            n["title"], n["description"],
                            n["url"], n["image_url"], n["published_at"])
                    update_ch = self.db.get_setting("update_channel", "")
                    if update_ch and self._app:
                        for n in self.db.get_unnotified_news()[:3]:
                            try:
                                await self._app.bot.send_message(
                                    update_ch,
                                    f"{Em.NEWS} <b>{escape_html(n['title'])}</b>\n\n"
                                    f"{escape_html((n.get('description','') or '')[:200])}\n\n"
                                    f"🔗 <a href='{n['url']}'>{sc('read more')}</a>",
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=False)
                                self.db.mark_news_notified(n["id"])
                            except Exception as e:
                                logger.warning(f"news post: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"news_worker: {e}")
            interval = int(self.db.get_setting("news_interval_hours", "6")) * 3600
            await asyncio.sleep(interval)

    # ──────────── bot setup ───────────────────────────────────────────────────

    def build_app(self) -> Application:
        app = (Application.builder()
               .token(Config.BOT_TOKEN)
               .build())
        self._app = app

        # ── core commands ──────────────────────────────────────────────────
        app.add_handler(CommandHandler("start",          self.cmd_start))
        app.add_handler(CommandHandler("help",           self.cmd_help))
        app.add_handler(CommandHandler("cr",             self.cmd_cr))
        app.add_handler(CommandHandler("download",       self.cmd_cr))
        app.add_handler(CommandHandler("dl",             self.cmd_cr))
        app.add_handler(CommandHandler("premium",        self.cmd_premium))
        app.add_handler(CommandHandler("pm",             self.cmd_premium))
        app.add_handler(CommandHandler("stats",          self.cmd_stats))
        app.add_handler(CommandHandler("settings",       self.cmd_settings))
        app.add_handler(CommandHandler("queue",          self.cmd_queue))
        app.add_handler(CommandHandler("cancel",         self.cmd_cancel))
        app.add_handler(CommandHandler("history",        self.cmd_history))
        app.add_handler(CommandHandler("redeem",         self.cmd_redeem))
        app.add_handler(CommandHandler("referral",       self.cmd_referral))
        app.add_handler(CommandHandler("ref",            self.cmd_referral))
        app.add_handler(CommandHandler("news",           self.cmd_news))
        app.add_handler(CommandHandler("favorites",      self.cmd_favorites))
        app.add_handler(CommandHandler("favs",           self.cmd_favorites))
        app.add_handler(CommandHandler("watchlist",      self.cmd_watchlist))
        app.add_handler(CommandHandler("leaderboard",    self.cmd_leaderboard))
        app.add_handler(CommandHandler("lb",             self.cmd_leaderboard))
        app.add_handler(CommandHandler("feedback",       self.cmd_feedback))
        app.add_handler(CommandHandler("schedule",       self.cmd_schedule))
        app.add_handler(CommandHandler("batch",          self.cmd_batch))
        app.add_handler(CommandHandler("addfav",         self.cmd_addfav))
        app.add_handler(CommandHandler("addwatch",       self.cmd_addwatch))
        app.add_handler(CommandHandler("gift",           self.cmd_gift))
        app.add_handler(CommandHandler("claimgift",      self.cmd_claimgift))

        # ── video tools ────────────────────────────────────────────────────
        app.add_handler(CommandHandler("mediainfo",      self.cmd_mediainfo))
        app.add_handler(CommandHandler("rename",         self.cmd_rename))
        app.add_handler(CommandHandler("compress",       self.cmd_compress))
        app.add_handler(CommandHandler("trim",           self.cmd_trim))
        app.add_handler(CommandHandler("thumbnail",      self.cmd_thumbnail))
        app.add_handler(CommandHandler("thumb",          self.cmd_thumbnail))
        app.add_handler(CommandHandler("watermark",      self.cmd_watermark))
        app.add_handler(CommandHandler("gif",            self.cmd_gif))
        app.add_handler(CommandHandler("audio",          self.cmd_audio))

        # ── admin commands ─────────────────────────────────────────────────
        app.add_handler(CommandHandler("admin",          self.cmd_admin))
        app.add_handler(CommandHandler("broadcast",      self.cmd_broadcast))
        app.add_handler(CommandHandler("ban",            self.cmd_ban))
        app.add_handler(CommandHandler("unban",          self.cmd_unban))
        app.add_handler(CommandHandler("warn",           self.cmd_warn))
        app.add_handler(CommandHandler("addpremium",     self.cmd_addpremium))
        app.add_handler(CommandHandler("revokepremium",  self.cmd_revokepremium))
        app.add_handler(CommandHandler("gencode",        self.cmd_gencode))
        app.add_handler(CommandHandler("setcookies",     self.cmd_setcookies))
        app.add_handler(CommandHandler("fetchnews",      self.cmd_fetchnews))
        app.add_handler(CommandHandler("addcmd",         self.cmd_addcmd))
        app.add_handler(CommandHandler("editcmd",        self.cmd_editcmd))
        app.add_handler(CommandHandler("delcmd",         self.cmd_delcmd))
        app.add_handler(CommandHandler("listcmds",       self.cmd_listcmds))
        app.add_handler(CommandHandler("userinfo",       self.cmd_userinfo))
        app.add_handler(CommandHandler("maintenance",    self.cmd_maintenance))
        app.add_handler(CommandHandler("authgroup",      self.cmd_authgroup))
        app.add_handler(CommandHandler("clearqueue",     self.cmd_clearqueue))
        app.add_handler(CommandHandler("logs",           self.cmd_logs))
        app.add_handler(CommandHandler("restart",        self.cmd_restart))

        # ── new admin commands ─────────────────────────────────────────────
        app.add_handler(CommandHandler("setwelcomeimage", self.cmd_setwelcomeimage))
        app.add_handler(CommandHandler("welcomepreview",  self.cmd_welcomepreview))
        app.add_handler(CommandHandler("botinfo",         self.cmd_botinfo))

        # ── diagnostics / DB utils ─────────────────────────────────────────
        app.add_handler(CommandHandler("diagnostics",    _cmd_diagnostics))
        app.add_handler(CommandHandler("dbbackup",       _cmd_dbbackup))
        app.add_handler(CommandHandler("exportusers",    _cmd_exportusers))
        app.add_handler(CommandHandler("cleanup",        _cmd_cleanup))
        app.add_handler(CommandHandler("vacuum",         _cmd_vacuum))

        # ── anime search ────────────────────────────────────────────────────
        app.add_handler(CommandHandler("search",         _cmd_search))
        app.add_handler(CommandHandler("airing",         _cmd_airing))
        app.add_handler(CommandHandler("season",         _cmd_season))
        app.add_handler(CommandHandler("schedlist",      _cmd_schedlist))

        # ── misc ─────────────────────────────────────────────────────────────
        app.add_handler(InlineQueryHandler(_inline_query_handler))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(PreCheckoutQueryHandler(self.handle_precheckout))
        app.add_handler(MessageHandler(
            filters.SUCCESSFUL_PAYMENT, self.handle_successful_payment))
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_text))

        return app

    # ──────────── FIX-02: missing run() method ────────────────────────────────

    def run(self):
        """Start polling — the entry point called from __main__."""
        if not Config.validate():
            sys.exit(1)

        app = self.build_app()

        # Start background tasks via post_init
        async def post_init(application: Application):
            self._queue_task = asyncio.create_task(self._queue_worker())
            self._sched_task = asyncio.create_task(self._scheduler_worker())
            self._news_task  = asyncio.create_task(self._news_worker())
            logger.info(f"✅ {sc('all background workers started')}")

        async def post_shutdown(application: Application):
            for task in [self._queue_task, self._sched_task, self._news_task]:
                if task and not task.done():
                    task.cancel()

        app.post_init     = post_init
        app.post_shutdown = post_shutdown

        logger.info(f"🚀 {sc('crunchyroll ultimate bot v200.1 starting')}…")
        app.run_polling(
            allowed_updates=["message", "callback_query",
                             "pre_checkout_query", "inline_query",
                             "chosen_inline_result"],
            drop_pending_updates=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 14: ꜱᴛᴀɴᴅ-ᴀʟᴏɴᴇ ᴄᴏᴍᴍᴀɴᴅ ꜰᴜɴᴄᴛɪᴏɴꜱ (ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜ etc.)
# ══════════════════════════════════════════════════════════════════════════════

class AnimeSearch:
    BASE = "https://api.jikan.moe/v4"

    @staticmethod
    async def search(query: str, limit: int = 5) -> List[Dict]:
        if not AIOHTTP_AVAILABLE:
            return []
        url    = f"{AnimeSearch.BASE}/anime"
        params = {"q": query, "limit": limit, "sfw": True}
        try:
            async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data    = await resp.json()
                        results = []
                        for a in data.get("data", []):
                            results.append({
                                "mal_id":   a.get("mal_id"),
                                "title":    a.get("title", "?"),
                                "title_en": a.get("title_english", ""),
                                "episodes": a.get("episodes", "?"),
                                "status":   a.get("status", "?"),
                                "score":    a.get("score", "?"),
                                "synopsis": (a.get("synopsis") or "")[:200],
                                "url":      a.get("url", ""),
                            })
                        return results
        except Exception as e:
            logger.warning(f"AnimeSearch: {e}")
        return []


async def _cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not ctx.args:
        await msg.reply_text(
            f"{Em.ANIME} {sc('usage')}: /search <code>{sc('anime name')}</code>",
            parse_mode=ParseMode.HTML)
        return
    query  = " ".join(ctx.args)
    status = await msg.reply_text(
        f"{Em.LOADING} {sc('searching for')} <b>{escape_html(query)}</b>…",
        parse_mode=ParseMode.HTML)
    results = await AnimeSearch.search(query, 5)
    if not results:
        await status.edit_text(
            f"{Em.ERROR} {sc('no results for')} <b>{escape_html(query)}</b>.",
            parse_mode=ParseMode.HTML)
        return
    lines   = [f"{Em.ANIME} <b>{sc('results for')}: {escape_html(query)}</b>\n"]
    kb_rows = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"\n<b>{i}. {escape_html(r['title'])}</b>\n"
            f"   ⭐{r['score']} | 📺{r['episodes']} eps\n"
            + (f"   {escape_html(r['synopsis'][:120])}…\n"
               if r.get("synopsis") else ""))
        if r.get("url"):
            kb_rows.append([_url_btn(f"🔗 {r['title'][:30]}", r["url"])])
    kb_rows.append([_btn(f"◀️ {sc('back')}", "show_home")])
    await status.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(kb_rows),
        parse_mode=ParseMode.HTML)


async def _cmd_airing(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg    = update.effective_message
    status = await msg.reply_text(
        f"{Em.LOADING} {sc('fetching airing anime')}…",
        parse_mode=ParseMode.HTML)
    if not AIOHTTP_AVAILABLE:
        await status.edit_text(f"{Em.ERROR} aiohttp not installed.",
                               parse_mode=ParseMode.HTML)
        return
    url    = AnimeSearch.BASE + "/top/anime"
    params = {"filter": "airing", "limit": 10}
    try:
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data   = await resp.json()
                    animes = data.get("data", [])
                    lines  = [f"{Em.FIRE} <b>{sc('currently airing (top 10)')}</b>\n"]
                    for i, a in enumerate(animes, 1):
                        lines.append(
                            f"{i}. <b>{escape_html(a.get('title','?'))}</b>"
                            f" ⭐{a.get('score','?')}")
                    await status.edit_text("\n".join(lines),
                                           parse_mode=ParseMode.HTML)
                else:
                    await status.edit_text(
                        f"{Em.ERROR} API {resp.status}",
                        parse_mode=ParseMode.HTML)
    except Exception as e:
        await status.edit_text(
            f"{Em.ERROR} {escape_html(str(e))}",
            parse_mode=ParseMode.HTML)


async def _cmd_season(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg    = update.effective_message
    status = await msg.reply_text(
        f"{Em.LOADING} {sc('fetching seasonal anime')}…",
        parse_mode=ParseMode.HTML)
    if not AIOHTTP_AVAILABLE:
        await status.edit_text(f"{Em.ERROR} aiohttp not installed.",
                               parse_mode=ParseMode.HTML)
        return
    url    = AnimeSearch.BASE + "/seasons/now"
    params = {"limit": 15}
    try:
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data   = await resp.json()
                    animes = data.get("data", [])
                    lines  = [f"{Em.ANIME} <b>{sc('this season')}</b>\n"]
                    for i, a in enumerate(animes[:15], 1):
                        score  = a.get("score") or "N/A"
                        genres = ", ".join(
                            g["name"] for g in a.get("genres", [])[:3]) or "?"
                        lines.append(
                            f"{i}. <b>{escape_html(a.get('title','?'))}</b>\n"
                            f"   ⭐{score} | 🎭 {escape_html(genres)}")
                    await status.edit_text("\n".join(lines),
                                           parse_mode=ParseMode.HTML)
                else:
                    await status.edit_text(
                        f"{Em.ERROR} API {resp.status}",
                        parse_mode=ParseMode.HTML)
    except Exception as e:
        await status.edit_text(
            f"{Em.ERROR} {escape_html(str(e))}",
            parse_mode=ParseMode.HTML)


async def _cmd_schedlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    db  = Database()
    c   = db.conn.execute(
        "SELECT id,url,quality,encode_preset,run_at,status FROM scheduled "
        "WHERE user_id=? ORDER BY run_at ASC LIMIT 10", (uid,))
    rows = c.fetchall()
    if not rows:
        await update.effective_message.reply_text(
            f"{Em.SCHEDULE} {sc('no scheduled downloads')}.\n"
            f"{sc('use')} /schedule <code>{sc('url hh:mm')}</code>.",
            parse_mode=ParseMode.HTML)
        return
    lines = [f"{Em.SCHEDULE} <b>{sc('scheduled downloads')}</b>\n"]
    for r in rows:
        icon = "✅" if r[5] == "queued" else "⏳"
        lines.append(
            f"{icon} <b>#{r[0]}</b> | {str(r[4])[:16]}\n"
            f"   <code>{str(r[1])[-35:]}</code>\n"
            f"   {r[2]} | {r[3]}")
    await update.effective_message.reply_text(
        "\n".join(lines),
        reply_markup=KB.back(),
        parse_mode=ParseMode.HTML)


# ──────────── diagnostics helpers ────────────────────────────────────────────

async def _run_diagnostics() -> Dict[str, bool]:
    results = {}
    for tool, path in [
        ("ffmpeg",  Config.FFMPEG_PATH),
        ("ffprobe", Config.FFPROBE_PATH),
        ("yt-dlp",  Config.YTDLP_PATH),
    ]:
        try:
            proc = await asyncio.create_subprocess_exec(
                path, "--version",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), timeout=5)
            results[tool] = proc.returncode == 0
        except Exception:
            results[tool] = False
    try:
        stat = shutil.disk_usage(str(Config.BASE_DIR))
        results["disk_space_ok"] = (stat.free / (1024 ** 3)) > 2.0
    except Exception:
        results["disk_space_ok"] = False
    try:
        db = Database()
        db.conn.execute("SELECT 1")
        results["database"] = True
    except Exception:
        results["database"] = False
    results["aiohttp"]   = AIOHTTP_AVAILABLE
    results["pyrogram"]  = PYROGRAM_AVAILABLE
    return results


def _format_diagnostics(checks: Dict[str, bool]) -> str:
    icons = {True: "✅", False: "❌"}
    lines = [f"🔧 <b>{sc('system diagnostics')}</b>\n"]
    for k, v in checks.items():
        lines.append(f"{icons[v]} {sc(k.replace('_',' '))}")
    return "\n".join(lines)


async def _cmd_diagnostics(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    if uid not in Config.ADMIN_IDS:
        return
    status  = await update.effective_message.reply_text(
        f"{Em.LOADING} {sc('running diagnostics')}…",
        parse_mode=ParseMode.HTML)
    checks  = await _run_diagnostics()
    report  = _format_diagnostics(checks)
    all_ok  = all(checks.values())
    report += "\n\n" + ("✅ " + sc("all systems ok") if all_ok
                        else "⚠️ " + sc("some checks failed"))
    if status:
        try:
            await status.edit_text(report, parse_mode=ParseMode.HTML)
        except Exception:
            await update.effective_message.reply_text(
                report, parse_mode=ParseMode.HTML)


async def _cmd_dbbackup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    if uid not in Config.ADMIN_IDS:
        return
    dest   = str(Config.DATA_PATH /
                 f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    status = await update.effective_message.reply_text(
        f"{Em.LOADING} {sc('backing up')}…", parse_mode=ParseMode.HTML)
    db = Database()
    try:
        with sqlite3.connect(dest) as bkp:
            db.conn.backup(bkp)
        await ctx.bot.send_document(
            update.effective_chat.id,
            document=InputFile(dest),
            caption=f"{Em.SUCCESS} {sc('database backup')}",
            parse_mode=ParseMode.HTML)
        if status:
            await status.delete()
        Path(dest).unlink(missing_ok=True)
    except Exception as e:
        if status:
            await status.edit_text(
                f"{Em.ERROR} {escape_html(str(e))}.",
                parse_mode=ParseMode.HTML)


async def _cmd_exportusers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    if uid not in Config.ADMIN_IDS:
        return
    db  = Database()
    c   = db.conn.execute(
        "SELECT user_id,username,first_name,premium_type,premium_expiry,"
        "total_downloads,total_size,is_banned,joined_at FROM users "
        "ORDER BY joined_at DESC")
    rows  = c.fetchall()
    lines = ["user_id,username,first_name,premium_type,premium_expiry,"
             "total_downloads,total_size_bytes,is_banned,joined_at"]
    for r in rows:
        lines.append(",".join(str(x or "") for x in r))
    csv_data = "\n".join(lines).encode("utf-8")
    fname    = f"users_{datetime.now().strftime('%Y%m%d')}.csv"
    await ctx.bot.send_document(
        update.effective_chat.id,
        document=InputFile(io.BytesIO(csv_data), filename=fname),
        caption=f"{Em.STATS} {sc('user export')}",
        parse_mode=ParseMode.HTML)


async def _cmd_cleanup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    if uid not in Config.ADMIN_IDS:
        return
    cutoff  = time.time() - 86400
    cleaned = 0
    for folder in [Config.TEMP_PATH, Config.ENCODE_PATH]:
        for f in folder.glob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                    cleaned += 1
                except Exception:
                    pass
    await update.effective_message.reply_text(
        f"{Em.SUCCESS} {sc('cleaned')} {cleaned} {sc('old temp files')}.",
        parse_mode=ParseMode.HTML)


async def _cmd_vacuum(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    if uid not in Config.ADMIN_IDS:
        return
    db = Database()
    db.conn.execute("VACUUM")
    db.conn.commit()
    await update.effective_message.reply_text(
        f"{Em.SUCCESS} {sc('database vacuumed')}.",
        parse_mode=ParseMode.HTML)


async def _inline_query_handler(update: Update,
                                 ctx: ContextTypes.DEFAULT_TYPE):
    from telegram import InlineQueryResultArticle, InputTextMessageContent
    q = update.inline_query
    if not q:
        return
    query = q.query.strip()
    if not query:
        results = [
            InlineQueryResultArticle(
                id="home",
                title=sc("crunchyroll bot"),
                description=sc("start the bot to download anime"),
                input_message_content=InputTextMessageContent(
                    f"{Em.ANIME} {sc('use')} /start {sc('in private chat')}!",
                    parse_mode=ParseMode.HTML))
        ]
        await q.answer(results, cache_time=10)
        return
    animes  = await AnimeSearch.search(query, 5)
    results = []
    for a in animes:
        title = a.get("title", "?")
        score = a.get("score", "?")
        eps   = a.get("episodes", "?")
        syn   = a.get("synopsis", "")[:200]
        url   = a.get("url", "")
        text  = (
            f"{Em.ANIME} <b>{escape_html(title)}</b>\n\n"
            f"⭐ {score} | 📺 {eps} {sc('eps')}\n\n"
            f"{escape_html(syn)}"
            + (f"\n\n🔗 <a href='{url}'>{sc('view on mal')}</a>" if url else "")
        )
        results.append(
            InlineQueryResultArticle(
                id=str(a.get("mal_id", title)),
                title=title,
                description=f"⭐{score} | {eps} eps | {syn[:80]}",
                input_message_content=InputTextMessageContent(
                    text, parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False)))
    await q.answer(results, cache_time=30)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 15: ᴇɴᴛʀʏ ᴘᴏɪɴᴛ
# ══════════════════════════════════════════════════════════════════════════════

TOTAL_COMMANDS = 65
TOTAL_FEATURES = 60

logger.info(
    f"{sc('crunchyroll bot v200.1 loaded')} — "
    f"{TOTAL_COMMANDS} {sc('commands')} | "
    f"{TOTAL_FEATURES} {sc('features')}")

if __name__ == "__main__":
    bot = CrunchyBot()
    bot.run()   # FIX-02: this now works
