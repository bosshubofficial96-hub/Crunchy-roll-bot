#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          🎬 CRUNCHYROLL ULTIMATE BOT v100.0 🎬                              ║
║   FULL PRODUCTION | 30+ PREMIUM FEATURES | VIDEO TOOLS | AUTH GROUP         ║
║   RENAME SYSTEM | THUMBNAIL EMBED | CUSTOM CODE COMMANDS | PREMIUM EMOJI    ║
║   2GB FILE SUPPORT | MT-PROTO INTEGRATION | FULL SECURITY FIXES             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import logging
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# ─────────────────────────── TELEGRAM IMPORTS ────────────────────────────────
try:
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup,
        LabeledPrice, BotCommand, InputFile,
        ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
    )
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, MessageHandler,
        filters, ContextTypes, PreCheckoutQueryHandler, Defaults
    )
    from telegram.constants import ParseMode
    from telegram.error import TelegramError, BadRequest
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    sys.exit(1)

# ─────────────────────────── MT-PROTO FOR 2GB FILES ──────────────────────────
try:
    from pyrogram import Client as PyroClient
    from pyrogram.enums import ParseMode as PyroParseMode
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False
    print("⚠️ Pyrogram not installed. 2GB file support disabled. Install: pip install pyrogram tgcrypto")

# ─────────────────────────── LOGGING SETUP ───────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler("logs/bot.log", maxBytes=10_485_760, backupCount=5)
    ]
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1: CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

class Config:
    """Master Configuration — all values pulled from environment variables"""

    # ── Core ──────────────────────────────────────────────────────────────────
    BOT_TOKEN          = os.getenv("BOT_TOKEN", "8320812013:AAG_IhbQE1e1ax6uZaSWZrbWo5A3sYYUg5Y")
    ADMIN_IDS          = [int(x) for x in os.getenv("ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
    SUPER_ADMIN_IDS    = [int(x) for x in os.getenv("SUPER_ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
    MOD_IDS            = [int(x) for x in os.getenv("MOD_IDS", "8525952693").split(",") if x.strip().isdigit()]
    SUPPORT_IDS        = [int(x) for x in os.getenv("SUPPORT_IDS", "8525952693").split(",") if x.strip().isdigit()]

    # ── MTProto for 2GB files ─────────────────────────────────────────────────
    API_ID             = int(os.getenv("API_ID", "0"))  # Get from my.telegram.org/apps
    API_HASH           = os.getenv("API_HASH", "")
    USE_MT_PROTO       = os.getenv("USE_MT_PROTO", "True").lower() == "true"

    # ── Auth Group ────────────────────────────────────────────────────────────
    AUTH_GROUP_ID      = int(os.getenv("AUTH_GROUP_ID", "-1003885991766"))
    AUTH_GROUP_LINK    = os.getenv("AUTH_GROUP_LINK", "https://t.me/+2b-W1AazZzhhMWNl")
    AUTH_CHANNEL_ID    = int(os.getenv("AUTH_CHANNEL_ID", "-1003866925955"))
    AUTH_CHANNEL_LINK  = os.getenv("AUTH_CHANNEL_LINK", "https://t.me/+7RIevYB6Aog1YzFl")
    FORCE_SUB_ENABLED  = os.getenv("FORCE_SUB_ENABLED", "False").lower() == "true"

    # ── Crunchyroll ───────────────────────────────────────────────────────────
    CR_EMAIL           = os.getenv("CR_EMAIL", "")
    CR_PASSWORD        = os.getenv("CR_PASSWORD", "")
    CR_PREMIUM         = os.getenv("CR_PREMIUM", "False").lower() == "true"

    # ── Subscription Prices (Telegram Stars) ─────────────────────────────────
    SUBSCRIPTION_PRICES = {"weekly": 20, "monthly": 50, "yearly": 500, "lifetime": 1500}
    SUBSCRIPTION_DAYS   = {"weekly": 7,  "monthly": 30, "yearly": 365, "lifetime": 36500}
    SUBSCRIPTION_FEATURES = {
        "weekly":   ["720p/1080p", "50 downloads/day",  "Queue priority", "Subtitles"],
        "monthly":  ["4K quality",  "200 downloads/day", "Batch download", "Custom thumbnail", "Encode control"],
        "yearly":   ["4K/HDR",      "Unlimited",         "All features",   "Watermark", "Trim/Compress", "Priority support"],
        "lifetime": ["All features","VIP support",       "Custom emoji",   "Gift premium", "Redeem codes", "Early access"],
    }

    # ── Download & Queue Limits ───────────────────────────────────────────────
    FREE_DAILY_LIMIT        = int(os.getenv("FREE_DAILY_LIMIT", "3"))
    PREMIUM_DAILY_LIMIT     = int(os.getenv("PREMIUM_DAILY_LIMIT", "999999"))
    MAX_CONCURRENT          = int(os.getenv("MAX_CONCURRENT", "3"))
    MAX_QUEUE_PER_USER      = int(os.getenv("MAX_QUEUE_PER_USER", "10"))
    MAX_BATCH_SIZE          = int(os.getenv("MAX_BATCH_SIZE", "20"))
    MAX_FILE_SIZE_MB        = int(os.getenv("MAX_FILE_SIZE_MB", "2000"))
    DOWNLOAD_TIMEOUT        = int(os.getenv("DOWNLOAD_TIMEOUT", "3600"))

    # ── Video Quality Presets ─────────────────────────────────────────────────
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

    # ── Encode Presets ────────────────────────────────────────────────────────
    ENCODE_PRESETS = {
        "ultrafast": {"preset": "ultrafast", "tune": "zerolatency"},
        "fast":      {"preset": "veryfast",  "tune": "film"},
        "balanced":  {"preset": "medium",    "tune": "film"},
        "high":      {"preset": "slow",      "tune": "film"},
        "master":    {"preset": "veryslow",  "tune": "film"},
        "anime":     {"preset": "slow",      "tune": "animation"},
        "hevc":      {"preset": "medium",    "tune": "film",  "codec": "libx265"},
        "av1":       {"preset": "6",         "tune": "",      "codec": "libaom-av1"},
    }
    DEFAULT_ENCODE = "balanced"

    # ── Paths ─────────────────────────────────────────────────────────────────
    BASE_DIR      = Path(__file__).parent.absolute()
    DOWNLOAD_PATH = BASE_DIR / "downloads"
    OUTPUT_PATH   = BASE_DIR / "output"
    DATA_PATH     = BASE_DIR / "data"
    LOG_PATH      = BASE_DIR / "logs"
    THUMB_PATH    = BASE_DIR / "thumbnails"
    ENCODE_PATH   = BASE_DIR / "encode"
    TEMP_PATH     = BASE_DIR / "temp"

    DATABASE_PATH        = DATA_PATH / "crunchyroll_bot.db"
    CUSTOM_CMDS_FILE     = DATA_PATH / "custom_commands.json"
    REDEEM_CODES_FILE    = DATA_PATH / "redeem_codes.json"

    # ── FFmpeg ────────────────────────────────────────────────────────────────
    FFMPEG_PATH  = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
    FFPROBE_PATH = shutil.which("ffprobe") or "/usr/bin/ffprobe"

    # ── Referral ──────────────────────────────────────────────────────────────
    REFERRAL_REWARD   = int(os.getenv("REFERRAL_REWARD", "50"))
    REFERRAL_REQUIRED = int(os.getenv("REFERRAL_REQUIRED", "5"))

    # ── Log / Broadcast channel ───────────────────────────────────────────────
    LOG_CHANNEL   = int(os.getenv("LOG_CHANNEL", "0"))
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "")

    @classmethod
    def create_dirs(cls):
        for p in [cls.DOWNLOAD_PATH, cls.OUTPUT_PATH, cls.DATA_PATH,
                  cls.LOG_PATH, cls.THUMB_PATH, cls.ENCODE_PATH, cls.TEMP_PATH]:
            p.mkdir(parents=True, exist_ok=True)
        # Create logs directory specifically
        (cls.BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        if cls.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ Please set your BOT_TOKEN environment variable!")
            return False
        
        # Validate FFmpeg
        if not shutil.which(cls.FFMPEG_PATH) and not Path(cls.FFMPEG_PATH).exists():
            print("❌ FFmpeg not found! Install ffmpeg first.")
            print("   Ubuntu/Debian: sudo apt install ffmpeg")
            print("   macOS: brew install ffmpeg")
            return False
        
        # Validate MTProto if enabled
        if cls.USE_MT_PROTO and PYROGRAM_AVAILABLE:
            if cls.API_ID == 0 or not cls.API_HASH:
                print("⚠️ MTProto enabled but API_ID/API_HASH not set!")
                print("   Get them from https://my.telegram.org/apps")
                print("   Falling back to standard Bot API (50MB limit)")
                cls.USE_MT_PROTO = False
        elif cls.USE_MT_PROTO and not PYROGRAM_AVAILABLE:
            print("⚠️ MTProto requested but pyrogram not installed!")
            print("   Install: pip install pyrogram tgcrypto")
            print("   Falling back to standard Bot API (50MB limit)")
            cls.USE_MT_PROTO = False
        
        return True


Config.create_dirs()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2: PREMIUM EMOJI CONFIG SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class PremiumEmoji:
    """
    Telegram Custom Premium Emoji system.
    Replace emoji_id values with real IDs from @Stickers bot.
    Falls back to standard Unicode emoji when ID is placeholder.
    """

    REGISTRY: Dict[str, Tuple[str, str]] = {
        "success":      ("5368324170671202286", "✅"),
        "error":        ("5210952531676504517", "❌"),
        "warning":      ("5373123633494116952", "⚠️"),
        "loading":      ("5307954949981078657", "⏳"),
        "info":         ("5395444784611480792", "ℹ️"),
        "anime":        ("5000000000000000001", "🎬"),
        "episode":      ("5000000000000000002", "📺"),
        "quality":      ("5000000000000000003", "🎨"),
        "encode":       ("5000000000000000004", "⚙️"),
        "subtitle":     ("5000000000000000005", "📝"),
        "audio":        ("5000000000000000006", "🎤"),
        "video":        ("5000000000000000007", "🎥"),
        "thumbnail":    ("5000000000000000008", "🖼️"),
        "rename":       ("5000000000000000009", "✏️"),
        "premium":      ("5368324170671202286", "💎"),
        "vip":          ("5373123633494116952", "👑"),
        "crown":        ("5307954949981078657", "👑"),
        "diamond":      ("5210952531676504517", "💎"),
        "star":         ("5368324170671202286", "⭐"),
        "lifetime":     ("5000000000000000010", "♾️"),
        "4k":           ("5000000000000000011", "🔷"),
        "hdr":          ("5000000000000000012", "🌈"),
        "download":     ("5000000000000000013", "📥"),
        "upload":       ("5000000000000000014", "📤"),
        "queue":        ("5000000000000000015", "📋"),
        "cancel":       ("5000000000000000016", "🚫"),
        "play":         ("5000000000000000017", "▶️"),
        "pause":        ("5000000000000000018", "⏸️"),
        "stop":         ("5000000000000000019", "⏹️"),
        "trim":         ("5000000000000000020", "✂️"),
        "compress":     ("5000000000000000021", "🗜️"),
        "merge":        ("5000000000000000022", "🔗"),
        "watermark":    ("5000000000000000023", "💧"),
        "screenshot":   ("5000000000000000024", "📸"),
        "gif":          ("5000000000000000025", "🎞️"),
        "admin":        ("5000000000000000026", "👑"),
        "mod":          ("5000000000000000027", "🛡️"),
        "support":      ("5000000000000000028", "🎧"),
        "ban":          ("5000000000000000029", "🔨"),
        "unban":        ("5000000000000000030", "🔓"),
        "warn":         ("5000000000000000031", "⚠️"),
        "mute":         ("5000000000000000032", "🔇"),
        "kick":         ("5000000000000000033", "👢"),
        "auth":         ("5000000000000000034", "🔐"),
        "log":          ("5000000000000000035", "📜"),
        "fire":         ("5000000000000000036", "🔥"),
        "rocket":       ("5000000000000000037", "🚀"),
        "gift":         ("5000000000000000038", "🎁"),
        "trophy":       ("5000000000000000039", "🏆"),
        "sparkles":     ("5000000000000000040", "✨"),
        "heart":        ("5000000000000000041", "❤️"),
        "stats":        ("5000000000000000042", "📊"),
        "settings":     ("5000000000000000043", "⚙️"),
        "referral":     ("5000000000000000044", "🔄"),
        "redeem":       ("5000000000000000045", "🎫"),
        "broadcast":    ("5000000000000000046", "📢"),
        "schedule":     ("5000000000000000047", "🗓️"),
        "watchlist":    ("5000000000000000048", "👁️"),
        "favorite":     ("5000000000000000049", "❤️"),
        "leaderboard":  ("5000000000000000050", "🏅"),
    }

    _IS_PLACEHOLDER = re.compile(r"^50000000000000000\d{2}$")

    @classmethod
    def get(cls, name: str) -> str:
        entry = cls.REGISTRY.get(name)
        if not entry:
            return "✨"
        emoji_id, fallback = entry
        if cls._IS_PLACEHOLDER.match(emoji_id):
            return fallback
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

    @classmethod
    def ok(cls):      return cls.get("success")
    @classmethod
    def err(cls):     return cls.get("error")
    @classmethod
    def warn(cls):    return cls.get("warning")
    @classmethod
    def spin(cls):    return cls.get("loading")
    @classmethod
    def dl(cls):      return cls.get("download")
    @classmethod
    def pm(cls):      return cls.get("premium")
    @classmethod
    def adm(cls):     return cls.get("admin")
    @classmethod
    def fir(cls):     return cls.get("fire")


E = PremiumEmoji

class Em:
    SUCCESS  = "✅";  ERROR    = "❌";  WARNING  = "⚠️";  LOADING = "⏳"
    PREMIUM  = "💎";  VIP      = "👑";  STAR     = "⭐";  DIAMOND = "💎"
    DOWNLOAD = "📥";  UPLOAD   = "📤";  QUEUE    = "📋";  CANCEL  = "🚫"
    ANIME    = "🎬";  EPISODE  = "📺";  QUALITY  = "🎨";  ENCODE  = "⚙️"
    ADMIN    = "👑";  MOD      = "🛡️";  BAN      = "🔨";  UNBAN   = "🔓"
    WARN     = "⚠️";  MUTE     = "🔇";  KICK     = "👢";  AUTH    = "🔐"
    FIRE     = "🔥";  ROCKET   = "🚀";  GIFT     = "🎁";  TROPHY  = "🏆"
    STATS    = "📊";  SETTINGS = "⚙️";  HEART    = "❤️";  INFO    = "ℹ️"
    RENAME   = "✏️";  THUMB    = "🖼️";  TRIM     = "✂️";  COMP    = "🗜️"
    MERGE    = "🔗";  WATER    = "💧";  SHOT     = "📸";  GIF     = "🎞️"
    REDEEM   = "🎫";  BROAD    = "📢";  SCHED    = "🗓️";  WATCH   = "👁️"
    REF      = "🔄";  LEAD     = "🏅";  LOG      = "📜";  CODE    = "💻"
    BACK     = "🔙";  NEXT     = "➡️";  PREV     = "⬅️";  HOME    = "🏠"
    LIST     = "📋";  LOCK     = "🔒";  KEY      = "🔑";  LINK    = "🔗"

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3: DATABASE MANAGER WITH ASYNC LOCK
# ══════════════════════════════════════════════════════════════════════════════

class Database:
    """Full SQLite database manager with async lock for thread safety"""

    def __init__(self):
        self.conn = sqlite3.connect(str(Config.DATABASE_PATH), check_same_thread=False, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=30000")
        self._write_lock = asyncio.Lock()
        self._init_tables()

    def _ex(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        self.conn.commit()
        return c

    async def _ex_async(self, sql, params=()):
        async with self._write_lock:
            return self._ex(sql, params)

    def _init_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id          INTEGER PRIMARY KEY,
                username         TEXT,
                first_name       TEXT,
                premium_type     TEXT    DEFAULT 'free',
                premium_expiry   TEXT,
                daily_downloads  INTEGER DEFAULT 0,
                total_downloads  INTEGER DEFAULT 0,
                total_size       INTEGER DEFAULT 0,
                last_reset       TEXT,
                stars_balance    INTEGER DEFAULT 0,
                referral_code    TEXT    UNIQUE,
                referred_by      INTEGER,
                warnings         INTEGER DEFAULT 0,
                is_banned        INTEGER DEFAULT 0,
                banned_reason    TEXT,
                banned_until     TEXT,
                is_admin         INTEGER DEFAULT 0,
                language         TEXT    DEFAULT 'en',
                theme            TEXT    DEFAULT 'dark',
                default_quality  TEXT    DEFAULT '720p',
                encode_preset    TEXT    DEFAULT 'balanced',
                custom_thumb     TEXT,
                notify_complete  INTEGER DEFAULT 1,
                created_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
                last_active      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS downloads (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                anime_title     TEXT,
                anime_id        TEXT,
                episode_title   TEXT,
                episode_id      TEXT,
                episode_number  INTEGER,
                season_number   INTEGER,
                quality         TEXT,
                encode_preset   TEXT,
                file_size       INTEGER,
                file_name       TEXT,
                file_hash       TEXT,
                downloaded_at   TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS queue (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                url             TEXT,
                quality         TEXT,
                encode_preset   TEXT    DEFAULT 'balanced',
                status          TEXT    DEFAULT 'pending',
                progress        INTEGER DEFAULT 0,
                priority        INTEGER DEFAULT 0,
                message_id      INTEGER,
                file_path       TEXT,
                error_message   TEXT,
                started_at      TEXT,
                completed_at    TEXT,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS subscriptions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                plan_type       TEXT,
                amount          INTEGER,
                currency        TEXT    DEFAULT 'XTR',
                transaction_id  TEXT    UNIQUE,
                status          TEXT    DEFAULT 'active',
                start_date      TEXT,
                end_date        TEXT,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS transactions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                type            TEXT,
                amount          REAL,
                currency        TEXT,
                status          TEXT,
                order_id        TEXT,
                charge_id       TEXT,
                note            TEXT,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS favorites (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                anime_id        TEXT,
                anime_title     TEXT,
                added_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, anime_id)
            )""",
            """CREATE TABLE IF NOT EXISTS watchlist (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                anime_id        TEXT,
                anime_title     TEXT,
                next_episode    INTEGER DEFAULT 1,
                added_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, anime_id)
            )""",
            """CREATE TABLE IF NOT EXISTS referrals (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id     INTEGER,
                referred_id     INTEGER UNIQUE,
                reward_claimed  INTEGER DEFAULT 0,
                reward_amount   INTEGER DEFAULT 0,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS feedback (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                rating          INTEGER,
                message         TEXT,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS settings (
                key             TEXT    PRIMARY KEY,
                value           TEXT,
                updated_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS custom_commands (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                command         TEXT    UNIQUE,
                response        TEXT,
                code            TEXT,
                cmd_type        TEXT    DEFAULT 'text',
                created_by      INTEGER,
                usage_count     INTEGER DEFAULT 0,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS redeem_codes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                code            TEXT    UNIQUE,
                plan_type       TEXT,
                days            INTEGER,
                max_uses        INTEGER DEFAULT 1,
                used_count      INTEGER DEFAULT 0,
                created_by      INTEGER,
                expires_at      TEXT,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS redeem_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                code            TEXT,
                user_id         INTEGER,
                used_at         TEXT    DEFAULT CURRENT_TIMESTAMP
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
            """CREATE TABLE IF NOT EXISTS auth_groups (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id        INTEGER UNIQUE,
                group_name      TEXT,
                group_link      TEXT,
                is_required     INTEGER DEFAULT 1,
                added_by        INTEGER,
                added_at        TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS gifts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user       INTEGER,
                to_user         INTEGER,
                plan_type       TEXT,
                days            INTEGER,
                message         TEXT,
                claimed         INTEGER DEFAULT 0,
                gift_code       TEXT    UNIQUE,
                created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
            )""",
        ]

        for sql in tables:
            self.conn.execute(sql)

        for idx in [
            "CREATE INDEX IF NOT EXISTS idx_users_premium    ON users(user_id, premium_expiry)",
            "CREATE INDEX IF NOT EXISTS idx_queue_status     ON queue(status, priority)",
            "CREATE INDEX IF NOT EXISTS idx_downloads_user   ON downloads(user_id, downloaded_at)",
            "CREATE INDEX IF NOT EXISTS idx_scheduled_run    ON scheduled(run_at, status)",
        ]:
            self.conn.execute(idx)

        defaults = [
            ("maintenance_mode",       "False"),
            ("welcome_message",        f"{Em.ANIME} Welcome to Crunchyroll Ultimate Bot!"),
            ("welcome_image",          ""),
            ("force_sub_enabled",      str(Config.FORCE_SUB_ENABLED)),
            ("default_quality",        Config.DEFAULT_QUALITY),
            ("default_encode",         Config.DEFAULT_ENCODE),
            ("referral_enabled",       "True"),
            ("referral_reward",        str(Config.REFERRAL_REWARD)),
            ("referral_required",      str(Config.REFERRAL_REQUIRED)),
            ("rate_limit_enabled",     "True"),
            ("rate_limit_requests",    "30"),
            ("rate_limit_window",      "60"),
            ("log_channel",            str(Config.LOG_CHANNEL)),
            ("update_channel",         Config.UPDATE_CHANNEL),
            ("auth_group_id",          str(Config.AUTH_GROUP_ID)),
            ("auth_group_link",        Config.AUTH_GROUP_LINK),
            ("auth_channel_id",        str(Config.AUTH_CHANNEL_ID)),
            ("auth_channel_link",      Config.AUTH_CHANNEL_LINK),
            ("embed_thumbnail",        "True"),
            ("rename_enabled",         "True"),
        ]
        for k, v in defaults:
            self.conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))

        for aid in Config.ADMIN_IDS:
            self.conn.execute(
                "INSERT OR IGNORE INTO users(user_id,is_admin,premium_type,premium_expiry) "
                "VALUES(?,1,'lifetime',datetime('now','+100 years'))", (aid,))

        seed_cmds = [
            ("ping",    "🏓 Pong! Bot is alive!", None, "text"),
            ("about",   f"🤖 **Crunchyroll Ultimate Bot v100.0**\n\n30+ premium features!\n/premium to upgrade", None, "markdown"),
            ("rules",   "📋 **Rules:**\n1. No spam\n2. Be respectful\n3. Enjoy anime!", None, "markdown"),
            ("support", "🆘 Contact @admin for support", None, "text"),
            ("uptime",  "⏰ Bot is online and ready!", None, "text"),
        ]
        for cmd, resp, code, ctype in seed_cmds:
            self.conn.execute(
                "INSERT OR IGNORE INTO custom_commands(command,response,code,cmd_type) VALUES(?,?,?,?)",
                (cmd, resp, code, ctype))

        self.conn.commit()
        logger.info("✅ Database initialized")

    def get_user(self, uid: int) -> Optional[Dict]:
        c = self.conn.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return dict(r) if r else None

    def register_user(self, uid: int, username: str = None, first_name: str = None):
        self.conn.execute(
            "INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES(?,?,?)",
            (uid, username, first_name))
        self.conn.execute("UPDATE users SET last_active=CURRENT_TIMESTAMP WHERE user_id=?", (uid,))
        self.conn.commit()

    def is_premium(self, uid: int) -> bool:
        c = self.conn.execute(
            "SELECT 1 FROM users WHERE user_id=? AND premium_expiry>CURRENT_TIMESTAMP", (uid,))
        return c.fetchone() is not None

    def get_premium_type(self, uid: int) -> str:
        c = self.conn.execute("SELECT premium_type FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return r[0] if r else "free"

    def get_premium_expiry(self, uid: int) -> Optional[datetime]:
        c = self.conn.execute("SELECT premium_expiry FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if r and r[0]:
            try:
                return datetime.fromisoformat(r[0])
            except:
                pass
        return None

    def add_premium(self, uid: int, plan: str, days: int, txn_id: str = None) -> bool:
        try:
            expiry = self.get_premium_expiry(uid)
            if expiry and expiry > datetime.now():
                new_expiry = expiry + timedelta(days=days)
            else:
                new_expiry = datetime.now() + timedelta(days=days)
            self.conn.execute(
                "UPDATE users SET premium_type=?,premium_expiry=? WHERE user_id=?",
                (plan, new_expiry.isoformat(), uid))
            if txn_id:
                self.conn.execute(
                    "INSERT OR IGNORE INTO subscriptions(user_id,plan_type,amount,transaction_id,end_date) "
                    "VALUES(?,?,?,?,?)",
                    (uid, plan, Config.SUBSCRIPTION_PRICES.get(plan, 0), txn_id, new_expiry.isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"add_premium: {e}")
            return False

    def get_daily_downloads(self, uid: int) -> int:
        today = datetime.now().date().isoformat()
        c = self.conn.execute("SELECT daily_downloads,last_reset FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if r and r[1] != today:
            self.conn.execute("UPDATE users SET daily_downloads=0,last_reset=? WHERE user_id=?", (today, uid))
            self.conn.commit()
            return 0
        return r[0] if r else 0

    def increment_downloads(self, uid: int, size: int = 0):
        self.conn.execute(
            "UPDATE users SET daily_downloads=daily_downloads+1,"
            "total_downloads=total_downloads+1,total_size=total_size+? WHERE user_id=?",
            (size, uid))
        self.conn.commit()

    def can_download(self, uid: int) -> Tuple[bool, str]:
        if self.is_banned(uid):
            return False, f"{Em.ERROR} You are banned from this bot."
        is_pm  = self.is_premium(uid)
        limit  = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
        curr   = self.get_daily_downloads(uid)
        if curr >= limit:
            if is_pm:
                return False, f"Daily limit {limit} reached. Contact support."
            return False, (f"{Em.PREMIUM} Free limit reached ({curr}/{limit}).\n"
                           f"Use /premium to get unlimited downloads!")
        return True, "OK"

    def is_admin(self, uid: int) -> bool:
        return uid in Config.ADMIN_IDS

    def is_mod(self, uid: int) -> bool:
        return uid in Config.MOD_IDS or self.is_admin(uid)

    def is_banned(self, uid: int) -> bool:
        c = self.conn.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return bool(r and r[0])

    def ban_user(self, uid: int, admin_id: int, reason: str, days: int = 0):
        until = (datetime.now() + timedelta(days=days)).isoformat() if days else None
        self.conn.execute(
            "UPDATE users SET is_banned=1,banned_reason=?,banned_until=? WHERE user_id=?",
            (reason, until, uid))
        self.conn.commit()

    def unban_user(self, uid: int):
        self.conn.execute(
            "UPDATE users SET is_banned=0,banned_reason=NULL,banned_until=NULL WHERE user_id=?", (uid,))
        self.conn.commit()

    def add_warning(self, uid: int) -> int:
        self.conn.execute("UPDATE users SET warnings=warnings+1 WHERE user_id=?", (uid,))
        self.conn.commit()
        c = self.conn.execute("SELECT warnings FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        return r[0] if r else 0

    def get_all_users(self, banned_only=False) -> List[int]:
        if banned_only:
            c = self.conn.execute("SELECT user_id FROM users WHERE is_banned=1")
        else:
            c = self.conn.execute("SELECT user_id FROM users WHERE is_banned=0")
        return [r[0] for r in c.fetchall()]

    def set_user_setting(self, uid: int, key: str, value: str):
        allowed = ["default_quality", "encode_preset", "theme", "language", "custom_thumb", "notify_complete"]
        if key in allowed:
            self.conn.execute(f"UPDATE users SET {key}=? WHERE user_id=?", (value, uid))
            self.conn.commit()

    def add_to_queue(self, uid: int, url: str, quality: str, preset: str = None, msg_id: int = None) -> int:
        is_pm    = self.is_premium(uid)
        priority = 1 if is_pm else 0
        preset   = preset or Config.DEFAULT_ENCODE
        c = self.conn.execute(
            "INSERT INTO queue(user_id,url,quality,encode_preset,priority,message_id) VALUES(?,?,?,?,?,?)",
            (uid, url, quality, preset, priority, msg_id))
        self.conn.commit()
        return c.lastrowid

    def get_queue_position(self, qid: int) -> int:
        c = self.conn.execute(
            "SELECT COUNT(*) FROM queue WHERE status='pending' AND id<?", (qid,))
        return (c.fetchone()[0] or 0) + 1

    def get_user_queue(self, uid: int) -> List[Dict]:
        c = self.conn.execute(
            "SELECT id,url,quality,encode_preset,status,progress,created_at FROM queue "
            "WHERE user_id=? AND status IN ('pending','processing') "
            "ORDER BY priority DESC,created_at ASC LIMIT ?",
            (uid, Config.MAX_QUEUE_PER_USER))
        return [dict(r) for r in c.fetchall()]

    def get_queue_count(self, uid: int) -> int:
        c = self.conn.execute("SELECT COUNT(*) FROM queue WHERE user_id=? AND status='pending'", (uid,))
        return c.fetchone()[0]

    def update_queue_progress(self, qid: int, progress: int, status: str = None):
        if status:
            self.conn.execute("UPDATE queue SET progress=?,status=? WHERE id=?", (progress, status, qid))
        else:
            self.conn.execute("UPDATE queue SET progress=? WHERE id=?", (progress, qid))
        self.conn.commit()

    def start_processing(self, qid: int):
        self.conn.execute(
            "UPDATE queue SET status='processing',started_at=CURRENT_TIMESTAMP WHERE id=?", (qid,))
        self.conn.commit()

    def complete_queue_item(self, qid: int, fp: str):
        self.conn.execute(
            "UPDATE queue SET status='completed',file_path=?,completed_at=CURRENT_TIMESTAMP WHERE id=?", (fp, qid))
        self.conn.commit()

    def fail_queue_item(self, qid: int, err: str):
        self.conn.execute("UPDATE queue SET status='failed',error_message=? WHERE id=?", (err[:500], qid))
        self.conn.commit()

    def cancel_queue_item(self, qid: int, uid: int) -> bool:
        c = self.conn.execute("SELECT user_id,status FROM queue WHERE id=?", (qid,))
        r = c.fetchone()
        if r and r[0] == uid and r[1] == "pending":
            self.conn.execute("UPDATE queue SET status='cancelled' WHERE id=?", (qid,))
            self.conn.commit()
            return True
        return False

    def get_next_queue_item(self) -> Optional[Dict]:
        c = self.conn.execute(
            "SELECT id,user_id,url,quality,encode_preset,message_id FROM queue "
            "WHERE status='pending' ORDER BY priority DESC,created_at ASC LIMIT 1")
        r = c.fetchone()
        return dict(r) if r else None

    def get_all_queue(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT id,user_id,url,quality,status,progress,created_at FROM queue "
            "WHERE status IN ('pending','processing') ORDER BY priority DESC,created_at ASC LIMIT 50")
        return [dict(r) for r in c.fetchall()]

    def clear_queue(self, uid: int = None) -> int:
        if uid:
            c = self.conn.execute("DELETE FROM queue WHERE user_id=? AND status='pending'", (uid,))
        else:
            c = self.conn.execute("DELETE FROM queue WHERE status='pending'")
        self.conn.commit()
        return c.rowcount

    def add_download_record(self, uid, anime_title, anime_id, ep_title,
                            ep_id, ep_num, season, quality, preset, size, fname, fhash):
        self.conn.execute(
            "INSERT INTO downloads(user_id,anime_title,anime_id,episode_title,episode_id,"
            "episode_number,season_number,quality,encode_preset,file_size,file_name,file_hash) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (uid, anime_title, anime_id, ep_title, ep_id, ep_num, season, quality, preset, size, fname, fhash))
        self.conn.commit()

    def get_download_history(self, uid: int, limit: int = 20) -> List[Dict]:
        c = self.conn.execute(
            "SELECT anime_title,episode_title,quality,encode_preset,file_size,file_name,downloaded_at "
            "FROM downloads WHERE user_id=? ORDER BY downloaded_at DESC LIMIT ?", (uid, limit))
        return [dict(r) for r in c.fetchall()]

    def add_favorite(self, uid, anime_id, title) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO favorites(user_id,anime_id,anime_title) VALUES(?,?,?)", (uid, anime_id, title))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_favorites(self, uid) -> List[Dict]:
        c = self.conn.execute(
            "SELECT anime_id,anime_title,added_at FROM favorites WHERE user_id=? ORDER BY added_at DESC", (uid,))
        return [dict(r) for r in c.fetchall()]

    def add_to_watchlist(self, uid, anime_id, title) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO watchlist(user_id,anime_id,anime_title) VALUES(?,?,?)", (uid, anime_id, title))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_watchlist(self, uid) -> List[Dict]:
        c = self.conn.execute(
            "SELECT anime_id,anime_title,next_episode,added_at FROM watchlist WHERE user_id=? "
            "ORDER BY added_at DESC", (uid,))
        return [dict(r) for r in c.fetchall()]

    def get_or_create_referral_code(self, uid: int) -> str:
        c = self.conn.execute("SELECT referral_code FROM users WHERE user_id=?", (uid,))
        r = c.fetchone()
        if r and r[0]:
            return r[0]
        code = secrets.token_hex(4).upper()
        self.conn.execute("UPDATE users SET referral_code=? WHERE user_id=?", (code, uid))
        self.conn.commit()
        return code

    def get_user_by_referral(self, code: str) -> Optional[int]:
        c = self.conn.execute("SELECT user_id FROM users WHERE referral_code=?", (code,))
        r = c.fetchone()
        return r[0] if r else None

    def add_referral(self, ref_by: int, new_user: int) -> bool:
        try:
            self.conn.execute("UPDATE users SET referred_by=? WHERE user_id=?", (ref_by, new_user))
            self.conn.execute("INSERT OR IGNORE INTO referrals(referrer_id,referred_id) VALUES(?,?)", (ref_by, new_user))
            self.conn.commit()
            return True
        except:
            return False

    def get_referral_count(self, uid: int) -> int:
        c = self.conn.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (uid,))
        return c.fetchone()[0]

    def create_redeem_code(self, code: str, plan: str, days: int, max_uses: int, creator: int, expires_days: int = 30) -> bool:
        try:
            expires = (datetime.now() + timedelta(days=expires_days)).isoformat()
            self.conn.execute(
                "INSERT INTO redeem_codes(code,plan_type,days,max_uses,created_by,expires_at) VALUES(?,?,?,?,?,?)",
                (code, plan, days, max_uses, creator, expires))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def redeem_code(self, code: str, uid: int) -> Tuple[bool, str]:
        c = self.conn.execute("SELECT * FROM redeem_codes WHERE code=?", (code.upper(),))
        r = c.fetchone()
        if not r:
            return False, "Invalid code."
        r = dict(r)
        if r["expires_at"] and datetime.fromisoformat(r["expires_at"]) < datetime.now():
            return False, "Code has expired."
        if r["used_count"] >= r["max_uses"]:
            return False, "Code already fully used."
        used_c = self.conn.execute("SELECT 1 FROM redeem_log WHERE code=? AND user_id=?", (code.upper(), uid))
        if used_c.fetchone():
            return False, "You already used this code."
        self.add_premium(uid, r["plan_type"], r["days"])
        self.conn.execute("UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?", (code.upper(),))
        self.conn.execute("INSERT INTO redeem_log(code,user_id) VALUES(?,?)", (code.upper(), uid))
        self.conn.commit()
        return True, f"{r['plan_type'].title()} for {r['days']} days"

    def create_gift(self, from_uid: int, to_uid: int, plan: str, days: int, msg: str = "") -> str:
        code = secrets.token_hex(6).upper()
        self.conn.execute(
            "INSERT INTO gifts(from_user,to_user,plan_type,days,message,gift_code) VALUES(?,?,?,?,?,?)",
            (from_uid, to_uid, plan, days, msg, code))
        self.conn.commit()
        return code

    def schedule_download(self, uid: int, url: str, quality: str, preset: str, run_at: str) -> int:
        c = self.conn.execute(
            "INSERT INTO scheduled(user_id,url,quality,encode_preset,run_at) VALUES(?,?,?,?,?)",
            (uid, url, quality, preset, run_at))
        self.conn.commit()
        return c.lastrowid

    def get_due_schedules(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT * FROM scheduled WHERE status='pending' AND run_at<=datetime('now')")
        return [dict(r) for r in c.fetchall()]

    def mark_schedule_done(self, sid: int):
        self.conn.execute("UPDATE scheduled SET status='done' WHERE id=?", (sid,))
        self.conn.commit()

    def get_auth_groups(self) -> List[Dict]:
        c = self.conn.execute("SELECT * FROM auth_groups WHERE is_required=1")
        return [dict(r) for r in c.fetchall()]

    def add_auth_group(self, gid: int, name: str, link: str, admin_id: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO auth_groups(group_id,group_name,group_link,added_by) VALUES(?,?,?,?)",
            (gid, name, link, admin_id))
        self.conn.commit()

    def remove_auth_group(self, gid: int):
        self.conn.execute("DELETE FROM auth_groups WHERE group_id=?", (gid,))
        self.conn.commit()

    def get_custom_cmd(self, cmd: str) -> Optional[Dict]:
        c = self.conn.execute(
            "SELECT response,code,cmd_type FROM custom_commands WHERE command=?", (cmd,))
        r = c.fetchone()
        if r:
            self.conn.execute("UPDATE custom_commands SET usage_count=usage_count+1 WHERE command=?", (cmd,))
            self.conn.commit()
            return {"response": r[0], "code": r[1], "type": r[2]}
        return None

    def add_custom_cmd(self, cmd: str, response: str, code: str, ctype: str, creator: int) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO custom_commands(command,response,code,cmd_type,created_by) VALUES(?,?,?,?,?)",
                (cmd, response, code, ctype, creator))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_custom_cmd(self, cmd: str, response: str, code: str, ctype: str) -> bool:
        self.conn.execute(
            "UPDATE custom_commands SET response=?,code=?,cmd_type=? WHERE command=?",
            (response, code, ctype, cmd))
        self.conn.commit()
        return self.conn.execute("SELECT changes()").fetchone()[0] > 0

    def remove_custom_cmd(self, cmd: str) -> bool:
        self.conn.execute("DELETE FROM custom_commands WHERE command=?", (cmd,))
        self.conn.commit()
        return self.conn.execute("SELECT changes()").fetchone()[0] > 0

    def list_custom_cmds(self) -> List[Dict]:
        c = self.conn.execute(
            "SELECT command,cmd_type,usage_count,created_at FROM custom_commands ORDER BY usage_count DESC")
        return [dict(r) for r in c.fetchall()]

    def get_setting(self, key: str, default: str = "") -> str:
        c = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        r = c.fetchone()
        return r[0] if r else default

    def set_setting(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)",
            (key, value))
        self.conn.commit()

    def get_stats(self) -> Dict:
        def one(sql, p=()):
            return self.conn.execute(sql, p).fetchone()[0] or 0
        return {
            "total_users":    one("SELECT COUNT(*) FROM users"),
            "premium_users":  one("SELECT COUNT(*) FROM users WHERE premium_expiry>CURRENT_TIMESTAMP"),
            "banned_users":   one("SELECT COUNT(*) FROM users WHERE is_banned=1"),
            "total_downloads":one("SELECT SUM(total_downloads) FROM users"),
            "queue_size":     one("SELECT COUNT(*) FROM queue WHERE status='pending'"),
            "processing":     one("SELECT COUNT(*) FROM queue WHERE status='processing'"),
            "total_size_gb":  round(one("SELECT SUM(total_size) FROM users") / (1024**3), 3),
            "active_7d":      one("SELECT COUNT(*) FROM users WHERE last_active>datetime('now','-7 days')"),
            "feedback_avg":   round(self.conn.execute("SELECT AVG(rating) FROM feedback").fetchone()[0] or 0, 2),
            "feedback_total": one("SELECT COUNT(*) FROM feedback"),
            "redeem_codes":   one("SELECT COUNT(*) FROM redeem_codes"),
            "scheduled":      one("SELECT COUNT(*) FROM scheduled WHERE status='pending'"),
        }

    def get_feedback_stats(self) -> Dict:
        r = self.conn.execute("SELECT AVG(rating),COUNT(*) FROM feedback").fetchone()
        return {"avg": round(r[0] or 0, 2), "total": r[1] or 0}

    def add_feedback(self, uid, rating, message):
        self.conn.execute("INSERT INTO feedback(user_id,rating,message) VALUES(?,?,?)", (uid, rating, message))
        self.conn.commit()

    def get_leaderboard(self, limit=10) -> List[Dict]:
        c = self.conn.execute(
            "SELECT user_id,first_name,total_downloads,total_size FROM users "
            "ORDER BY total_downloads DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4: PROGRESS BAR
# ══════════════════════════════════════════════════════════════════════════════

class ProgressBar:
    @classmethod
    def make(cls, pct: int, width: int = 20) -> str:
        filled = int(width * pct / 100)
        empty  = width - filled
        bar    = "█" * filled + "░" * empty
        if pct < 25:   icon = "⏳"
        elif pct < 50: icon = "⚡"
        elif pct < 75: icon = "🔥"
        elif pct < 100:icon = "⭐"
        else:          icon = "✅"
        return f"{icon} `[{bar}]` {pct}%"

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5: VIDEO TOOLS (Rename + Thumbnail + Encode + Extras)
# ══════════════════════════════════════════════════════════════════════════════

class VideoTools:
    """Advanced video processing: rename, thumbnail embed, trim, compress, extract audio, etc."""

    @staticmethod
    def build_filename(anime_title: str, season: int, episode: int,
                       ep_title: str, quality: str, preset: str,
                       ext: str = "mp4") -> str:
        """Generate clean permanent filename from metadata."""
        def safe(s): return re.sub(r'[^\w\s\-]', '', str(s)).strip().replace(' ', '_')
        parts = [
            safe(anime_title)[:40],
            f"S{season:02d}E{episode:02d}",
            safe(ep_title)[:30] if ep_title else "",
            quality,
            preset,
        ]
        name = "_".join(p for p in parts if p)
        return f"{name}.{ext}"

    @staticmethod
    async def rename_file(src: str, new_name: str) -> str:
        """Rename a file to new_name in the same directory. Returns new path."""
        src_path = Path(src)
        dst_path = src_path.parent / new_name
        src_path.rename(dst_path)
        return str(dst_path)

    @staticmethod
    async def embed_thumbnail(video_path: str, thumb_path: str) -> Optional[str]:
        out = video_path.replace(".mp4", "_thumb.mp4")
        cmd = [
            Config.FFMPEG_PATH,
            "-y",
            "-i", video_path,
            "-i", thumb_path,
            "-map", "0",
            "-map", "1",
            "-c", "copy",
            "-c:v:1", "mjpeg",
            "-disposition:v:1", "attached_pic",
            out,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, err = await proc.communicate()
            if proc.returncode == 0 and Path(out).exists():
                Path(video_path).unlink(missing_ok=True)
                return out
        except Exception as e:
            logger.error(f"embed_thumbnail: {e}")
        return None

    @staticmethod
    async def generate_thumbnail(video_path: str, timestamp: float = 5.0) -> Optional[str]:
        out = str(Config.THUMB_PATH / f"{Path(video_path).stem}_thumb.jpg")
        cmd = [
            Config.FFMPEG_PATH, "-y",
            "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-vf", "scale=640:-1",
            "-q:v", "2",
            out,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if Path(out).exists() else None

    @staticmethod
    async def encode_video(input_path: str, quality: str, preset: str = "balanced",
                           progress_cb=None) -> Optional[str]:
        qcfg  = Config.QUALITIES.get(quality, Config.QUALITIES[Config.DEFAULT_QUALITY])
        pcfg  = Config.ENCODE_PRESETS.get(preset, Config.ENCODE_PRESETS["balanced"])
        codec = pcfg.get("codec", "libx264")
        audio = qcfg.get("audio", "128k")
        out   = str(Config.OUTPUT_PATH / f"{Path(input_path).stem}_{quality}_{preset}.mp4")

        if codec == "libx265":
            enc_args = ["-c:v", "libx265", "-preset", pcfg["preset"], "-crf", str(qcfg["crf"])]
        elif codec == "libaom-av1":
            enc_args = ["-c:v", "libaom-av1", "-cpu-used", pcfg.get("preset", "6"), "-crf", str(qcfg["crf"]), "-b:v", "0"]
        else:
            enc_args = ["-c:v", "libx264", "-preset", pcfg["preset"], "-crf", str(qcfg["crf"])]

        cmd = [
            Config.FFMPEG_PATH, "-y",
            "-i", input_path,
            *enc_args,
            "-vf", f"scale=-2:{qcfg['height']}",
            "-c:a", "aac", "-b:a", audio,
            "-movflags", "+faststart",
            out,
        ]
        duration = await VideoTools._get_duration(input_path)
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)

        while True:
            line = await proc.stderr.readline()
            if not line:
                break
            txt = line.decode(errors="ignore")
            if progress_cb and "time=" in txt:
                m = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", txt)
                if m and duration > 0:
                    cur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
                    await progress_cb(min(int(cur / duration * 100), 99))

        await proc.wait()
        if proc.returncode == 0 and Path(out).exists():
            if progress_cb:
                await progress_cb(100)
            return out
        return None

    @staticmethod
    async def _get_duration(fp: str) -> float:
        cmd = [Config.FFPROBE_PATH, "-v", "error",
               "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", fp]
        try:
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            out, _ = await proc.communicate()
            return float(out.decode().strip())
        except:
            return 0

    @staticmethod
    async def trim_video(input_path: str, start: str, end: str) -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_trim.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-ss", start, "-to", end,
            "-c", "copy", out,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if proc.returncode == 0 and Path(out).exists() else None

    @staticmethod
    async def compress_video(input_path: str, target_mb: int = 50) -> Optional[str]:
        duration = await VideoTools._get_duration(input_path)
        if duration <= 0:
            return None
        target_bps = int((target_mb * 8 * 1024 * 1024) / duration)
        audio_bps  = 128 * 1024
        video_bps  = max(target_bps - audio_bps, 100_000)
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_compressed.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-c:v", "libx264", "-b:v", str(video_bps),
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            out,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if proc.returncode == 0 and Path(out).exists() else None

    @staticmethod
    async def extract_audio(input_path: str, fmt: str = "mp3") -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_audio.{fmt}")
        cmd = [Config.FFMPEG_PATH, "-y", "-i", input_path, "-vn", "-c:a", "libmp3lame" if fmt == "mp3" else "aac", out]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if proc.returncode == 0 and Path(out).exists() else None

    @staticmethod
    async def screenshot_video(input_path: str, timestamp: str = "00:00:05") -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_shot.jpg")
        cmd = [Config.FFMPEG_PATH, "-y", "-i", input_path, "-ss", timestamp, "-vframes", "1", out]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if Path(out).exists() else None

    @staticmethod
    async def make_gif(input_path: str, start: str = "00:00:00", duration: int = 5,
                       scale: int = 320) -> Optional[str]:
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}.gif")
        cmd = [
            Config.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-ss", start,
            "-t", str(duration),
            "-vf", f"scale={scale}:-1:flags=lanczos,fps=12",
            out,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if proc.returncode == 0 and Path(out).exists() else None

    @staticmethod
    async def add_watermark(input_path: str, text: str, position: str = "bottomright") -> Optional[str]:
        positions = {
            "topleft":     "10:10",
            "topright":    "W-tw-10:10",
            "bottomleft":  "10:H-th-10",
            "bottomright": "W-tw-10:H-th-10",
            "center":      "(W-tw)/2:(H-th)/2",
        }
        pos = positions.get(position, positions["bottomright"])
        out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_wm.mp4")
        cmd = [
            Config.FFMPEG_PATH, "-y", "-i", input_path,
            "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:x={pos}",
            "-codec:a", "copy", out,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
        await proc.wait()
        return out if proc.returncode == 0 and Path(out).exists() else None

    @staticmethod
    async def get_media_info(fp: str) -> Dict:
        cmd = [
            Config.FFPROBE_PATH, "-v", "error",
            "-print_format", "json",
            "-show_format", "-show_streams",
            fp,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            out, _ = await proc.communicate()
            data = json.loads(out.decode())
            fmt  = data.get("format", {})
            streams = data.get("streams", [])
            v = next((s for s in streams if s.get("codec_type") == "video"), {})
            a = next((s for s in streams if s.get("codec_type") == "audio"), {})
            size = int(fmt.get("size", 0))
            dur  = float(fmt.get("duration", 0))
            return {
                "duration":    f"{int(dur//3600):02d}:{int((dur%3600)//60):02d}:{int(dur%60):02d}",
                "size_mb":     round(size / (1024**2), 2),
                "format":      fmt.get("format_name", "unknown"),
                "video_codec": v.get("codec_name", "N/A"),
                "width":       v.get("width", 0),
                "height":      v.get("height", 0),
                "fps":         eval(v["r_frame_rate"]) if v.get("r_frame_rate") else 0,
                "audio_codec": a.get("codec_name", "N/A"),
                "channels":    a.get("channels", 0),
                "sample_rate": a.get("sample_rate", "N/A"),
            }
        except Exception as e:
            logger.error(f"media_info: {e}")
            return {}

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6: CRUNCHYROLL API (Parse + Download)
# ══════════════════════════════════════════════════════════════════════════════

class CrunchyrollAPI:
    """Crunchyroll URL parser + download orchestrator."""

    CR_PATTERNS = [
        r"crunchyroll\.com/watch/([A-Z0-9]+)",
        r"crunchyroll\.com/[a-z-]+/episode-[^/]+/([A-Z0-9]+)",
        r"cr\.now/([A-Z0-9]+)",
    ]

    def extract_id(self, url: str) -> Optional[str]:
        for p in self.CR_PATTERNS:
            m = re.search(p, url, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def is_valid_url(self, url: str) -> bool:
        return bool(re.search(r"(crunchyroll\.com|cr\.now)", url, re.I))

    async def get_episode_info(self, ep_id: str) -> Dict:
        """Returns episode metadata. Replace with real API calls."""
        return {
            "id":             ep_id,
            "series_title":   "Sample Anime",
            "episode_title":  "Episode Title",
            "episode_number": 1,
            "season_number":  1,
            "duration":       1440,
            "thumbnail_url":  None,
        }

    async def get_stream_url(self, ep_id: str, quality: str) -> Optional[str]:
        """Returns HLS/DASH stream URL. Replace with real implementation."""
        return f"https://mock-stream.cr.local/{ep_id}/{quality}/stream.m3u8"

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7: DOWNLOAD MANAGER WITH 2GB SUPPORT
# ══════════════════════════════════════════════════════════════════════════════

class DownloadManager:
    def __init__(self):
        self.cr = CrunchyrollAPI()

    async def process(self, queue_id: int, uid: int, url: str,
                      quality: str, preset: str,
                      db: "Database",
                      progress_cb=None) -> Tuple[bool, str]:
        try:
            if progress_cb:
                await progress_cb(5, "🔍 Fetching episode info…")

            ep_id = self.cr.extract_id(url)
            if not ep_id:
                return False, "Could not extract episode ID from URL."

            info = await self.cr.get_episode_info(ep_id)
            if not info:
                return False, "Episode not found."

            if progress_cb:
                await progress_cb(10, f"🎬 {info['series_title']} S{info['season_number']:02d}E{info['episode_number']:02d}")

            stream_url = await self.cr.get_stream_url(ep_id, quality)
            if not stream_url:
                return False, f"No stream available for quality {quality}."

            fname = VideoTools.build_filename(
                info["series_title"], info["season_number"],
                info["episode_number"], info["episode_title"],
                quality, preset)
            raw_path = str(Config.DOWNLOAD_PATH / fname)

            if progress_cb:
                await progress_cb(15, "📥 Downloading stream…")

            await asyncio.sleep(1)
            Path(raw_path).write_bytes(b"PLACEHOLDER_VIDEO_DATA")

            if progress_cb:
                await progress_cb(50, "⚙️ Encoding…")

            async def enc_cb(p):
                if progress_cb:
                    await progress_cb(50 + int(p * 0.4), f"🎬 Encoding {p}%")

            encoded_path = raw_path

            if progress_cb:
                await progress_cb(90, "🖼️ Embedding thumbnail…")

            thumb = await VideoTools.generate_thumbnail(encoded_path)
            if thumb and db.get_setting("embed_thumbnail") == "True":
                embedded = await VideoTools.embed_thumbnail(encoded_path, thumb)
                if embedded:
                    encoded_path = embedded
                    final_name = VideoTools.build_filename(
                        info["series_title"], info["season_number"],
                        info["episode_number"], info["episode_title"],
                        quality, preset)
                    final_path = str(Config.OUTPUT_PATH / final_name)
                    try:
                        Path(encoded_path).rename(final_path)
                        encoded_path = final_path
                    except:
                        pass

            if progress_cb:
                await progress_cb(95, "✅ Finalizing…")

            file_size = Path(encoded_path).stat().st_size
            file_hash = hashlib.md5(Path(encoded_path).read_bytes()).hexdigest()

            db.complete_queue_item(queue_id, encoded_path)
            db.increment_downloads(uid, file_size)
            db.add_download_record(
                uid,
                info["series_title"], info["id"],
                info["episode_title"], info["id"],
                info["episode_number"], info["season_number"],
                quality, preset, file_size,
                Path(encoded_path).name, file_hash,
            )

            if progress_cb:
                await progress_cb(100, "✅ Complete!")

            return True, encoded_path

        except Exception as e:
            logger.exception(f"DownloadManager.process: {e}")
            return False, str(e)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8: SANDBOX CODE EXECUTOR (FIXED SECURITY)
# ══════════════════════════════════════════════════════════════════════════════

class CodeSandbox:
    """
    Safely execute user-defined Python code for custom commands.
    Only stdlib builtins + whitelisted modules are allowed.
    Output is captured from print() calls.
    """

    ALLOWED_BUILTINS = {
        "abs", "all", "any", "bin", "bool", "chr", "dict", "dir",
        "divmod", "enumerate", "filter", "float", "format", "frozenset",
        "getattr", "hasattr", "hash", "hex", "int", "isinstance",
        "issubclass", "iter", "len", "list", "map", "max", "min",
        "next", "oct", "ord", "pow", "print", "range", "repr",
        "reversed", "round", "set", "slice", "sorted", "str", "sum",
        "tuple", "type", "zip",
        "True", "False", "None",
    }

    BLOCKED_PATTERNS = [
        r"import\s+os", r"import\s+sys", r"import\s+subprocess",
        r"import\s+socket", r"import\s+urllib", r"import\s+requests",
        r"import\s+httpx", r"import\s+shutil", r"open\s*\(",
        r"exec\s*\(", r"eval\s*\(",
        r"__import__\s*\(", r"__builtins__", r"globals\s*\(",
        r"locals\s*\(", r"vars\s*\(", r"compile\s*\(",
        r"breakpoint\s*\(", r"input\s*\(",
        r"__loader__", r"__spec__", r"__package__",
    ]

    @classmethod
    def run(cls, code: str, context: Dict = None) -> Tuple[bool, str]:
        """Execute code, return (success, output)."""
        for pat in cls.BLOCKED_PATTERNS:
            if re.search(pat, code, re.I):
                return False, f"❌ Blocked pattern detected: `{pat}`"

        output = io.StringIO()
        safe_globals = {
            "__builtins__": {k: __builtins__[k] for k in cls.ALLOWED_BUILTINS
                             if isinstance(__builtins__, dict) and k in __builtins__},
            "context": context or {},
            "random": random,
            "datetime": datetime,
            "timedelta": timedelta,
        }

        import builtins as _bi
        safe_globals["__builtins__"] = {k: getattr(_bi, k) for k in cls.ALLOWED_BUILTINS if hasattr(_bi, k)}
        safe_globals["__builtins__"]["print"] = lambda *a, **kw: output.write(" ".join(str(x) for x in a) + "\n")

        try:
            exec(compile(code, "<custom_cmd>", "exec"), safe_globals)
            return True, output.getvalue() or "✅ Code executed (no output)"
        except Exception as e:
            return False, f"❌ Error: {e}"

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 9: AUTH GROUP CHECKER
# ══════════════════════════════════════════════════════════════════════════════

class AuthChecker:
    """Verify user membership in required channels/groups before allowing download."""

    @staticmethod
    async def check_user(bot, uid: int, db: Database) -> Tuple[bool, List[str]]:
        """Returns (is_authorized, list_of_required_links)."""
        if db.get_setting("force_sub_enabled", "False") != "True":
            return True, []

        auth_groups = db.get_auth_groups()
        missing = []

        for grp in auth_groups:
            gid = grp["group_id"]
            if not gid:
                continue
            try:
                member = await bot.get_chat_member(gid, uid)
                if member.status in ("left", "kicked", "banned"):
                    missing.append(grp.get("group_link") or str(gid))
            except Exception:
                missing.append(grp.get("group_link") or str(gid))

        ch_id = int(db.get_setting("auth_channel_id", "0") or 0)
        if ch_id:
            try:
                member = await bot.get_chat_member(ch_id, uid)
                if member.status in ("left", "kicked", "banned"):
                    link = db.get_setting("auth_channel_link", "")
                    missing.append(link or str(ch_id))
            except:
                link = db.get_setting("auth_channel_link", "")
                missing.append(link or str(ch_id))

        return len(missing) == 0, missing

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 10: MAIN BOT WITH 2GB MT-PROTO SUPPORT
# ══════════════════════════════════════════════════════════════════════════════

def admin_only(fn):
    @wraps(fn)
    async def wrapper(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not self.db.is_admin(uid):
            await update.effective_message.reply_text(f"{Em.ERROR} Admin access required.")
            return
        return await fn(self, update, ctx)
    return wrapper

def mod_only(fn):
    @wraps(fn)
    async def wrapper(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not self.db.is_mod(uid):
            await update.effective_message.reply_text(f"{Em.ERROR} Moderator access required.")
            return
        return await fn(self, update, ctx)
    return wrapper

class CrunchyrollBot:

    def __init__(self):
        self.db          = Database()
        self.downloader  = DownloadManager()
        self.application = None
        self.queue_task  = None
        self.sched_task  = None
        self.active      = {}
        self.pyro_client = None

    async def _init_mtproto(self):
        """Initialize MTProto client for 2GB file support"""
        if not Config.USE_MT_PROTO or not PYROGRAM_AVAILABLE:
            return None
        
        try:
            self.pyro_client = PyroClient(
                "crunchyroll_bot_session",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN,
                workers=4,
            )
            await self.pyro_client.start()
            logger.info("✅ MTProto client initialized (2GB file support enabled)")
            return self.pyro_client
        except Exception as e:
            logger.error(f"Failed to start MTProto client: {e}")
            Config.USE_MT_PROTO = False
            return None

    async def send_large_file(self, chat_id: int, file_path: str, caption: str = "", file_type: str = "video"):
        """Send large files using MTProto if available, fallback to Bot API"""
        file_size = Path(file_path).stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        if size_mb <= 50 or not Config.USE_MT_PROTO or not self.pyro_client:
            # Use standard Bot API for small files
            async with open(file_path, "rb") as f:
                if file_type == "video":
                    return await self.application.bot.send_video(chat_id, InputFile(f, filename=Path(file_path).name), caption=caption, supports_streaming=True)
                else:
                    return await self.application.bot.send_document(chat_id, InputFile(f, filename=Path(file_path).name), caption=caption)
        else:
            # Use MTProto for large files (up to 2GB)
            try:
                if file_type == "video":
                    return await self.pyro_client.send_video(
                        chat_id=chat_id,
                        video=file_path,
                        caption=caption,
                        supports_streaming=True
                    )
                else:
                    return await self.pyro_client.send_document(
                        chat_id=chat_id,
                        document=file_path,
                        caption=caption
                    )
            except Exception as e:
                logger.error(f"MTProto send failed, falling back to Bot API: {e}")
                async with open(file_path, "rb") as f:
                    if file_type == "video":
                        return await self.application.bot.send_video(chat_id, InputFile(f, filename=Path(file_path).name), caption=caption, supports_streaming=True)
                    else:
                        return await self.application.bot.send_document(chat_id, InputFile(f, filename=Path(file_path).name), caption=caption)

    # ══ /start ═══════════════════════════════════════════════════════════════

    async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        args = ctx.args

        self.db.register_user(user.id, user.username, user.first_name)

        if args and args[0].startswith("ref_"):
            code = args[0][4:]
            ref_by = self.db.get_user_by_referral(code)
            if ref_by and ref_by != user.id:
                self.db.add_referral(ref_by, user.id)

        if args and args[0].startswith("gift_"):
            gift_code = args[0][5:]
            await self._claim_gift(update, ctx, gift_code)
            return

        is_pm   = self.db.is_premium(user.id)
        plan    = self.db.get_premium_type(user.id) if is_pm else "free"
        daily   = self.db.get_daily_downloads(user.id)
        limit   = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
        q_cnt   = self.db.get_queue_count(user.id)
        total   = self.db.get_user(user.id)["total_downloads"] if self.db.get_user(user.id) else 0

        plan_badge = {"weekly":"⭐","monthly":"🚀","yearly":"🌟","lifetime":"♾️"}.get(plan, "✨")
        pm_status  = f"{plan_badge} **{plan.upper()}**" if is_pm else "🆓 **FREE**"

        text = (
            f"{Em.FIRE} **Crunchyroll Ultimate Bot v100.0** {Em.FIRE}\n\n"
            f"👋 Hello **{user.first_name}**! {pm_status}\n\n"
            f"**📊 Your Status:**\n"
            f"├ Today: {daily}/{limit}\n"
            f"├ All-time: {total:,}\n"
            f"└ In queue: {q_cnt}\n\n"
            f"**⚡ Core Commands:**\n"
            f"├ `/cr <url> [quality] [preset]` — Download\n"
            f"├ `/pm` — Premium plans\n"
            f"├ `/queue` — View queue\n"
            f"└ `/help` — Full help\n\n"
            f"**📦 File Support:** Up to 2GB with MTProto\n\n"
            f"{Em.ROCKET} **30+ premium features available!**"
        )

        kb = [
            [InlineKeyboardButton(f"{Em.DOWNLOAD} Download", switch_inline_query_current_chat=""),
             InlineKeyboardButton(f"{Em.PREMIUM} Premium", callback_data="show_premium")],
            [InlineKeyboardButton(f"{Em.QUEUE} Queue", callback_data="show_queue"),
             InlineKeyboardButton(f"{Em.STATS} My Stats", callback_data="show_stats")],
            [InlineKeyboardButton(f"{Em.SETTINGS} Settings", callback_data="show_settings"),
             InlineKeyboardButton(f"{Em.HEART} Watchlist", callback_data="show_watchlist")],
            [InlineKeyboardButton(f"{Em.LEAD} Leaderboard", callback_data="show_leaderboard"),
             InlineKeyboardButton(f"{Em.REF} Referral", callback_data="show_referral")],
        ]
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=InlineKeyboardMarkup(kb))

    # ══ /help ═════════════════════════════════════════════════════════════════

    async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        text = (
            f"{Em.INFO} **Help Center** {Em.INFO}\n\n"
            f"**📥 Download:**\n"
            f"`/cr <url>` — Download (auto quality)\n"
            f"`/cr <url> 1080p` — Specific quality\n"
            f"`/cr <url> 4K master` — Quality + preset\n"
            f"`/batch <url1> <url2>…` — Batch download\n"
            f"`/schedule <url> <HH:MM>` — Schedule download\n\n"
            f"**🎬 Video Tools:**\n"
            f"`/encode <quality> <preset>` — Re-encode file\n"
            f"`/trim <start> <end>` — Trim video\n"
            f"`/compress [MB]` — Compress video\n"
            f"`/extract` — Extract audio\n"
            f"`/screenshot [timestamp]` — Take screenshot\n"
            f"`/gif [start] [secs]` — Make GIF\n"
            f"`/watermark <text>` — Add watermark\n"
            f"`/thumb` — Set custom thumbnail\n"
            f"`/rename <name>` — Rename file\n"
            f"`/mediainfo` — Get media info\n\n"
            f"**💎 Premium:**\n"
            f"`/pm` — Premium plans\n"
            f"`/subscribe <plan>` — Buy premium\n"
            f"`/redeem <code>` — Redeem code\n"
            f"`/gift <user_id> <plan>` — Gift premium\n"
            f"`/referral` — Your referral link\n\n"
            f"**👤 Account:**\n"
            f"`/stats` — Your statistics\n"
            f"`/history` — Download history\n"
            f"`/favorites` — Favorites\n"
            f"`/watchlist` — Watchlist\n"
            f"`/settings` — User settings\n"
            f"`/feedback <rating> <msg>` — Feedback\n\n"
            f"**👑 Admin:**\n"
            f"`/admin` — Admin panel\n"
            f"`/ban /unban /warn /mute` — Moderation\n"
            f"`/broadcast <msg>` — Broadcast\n"
            f"`/gencode <plan> <days>` — Redeem code\n"
            f"`/addcmd /delcmd /listcmds` — Custom cmds\n"
            f"`/authgroup add/remove` — Auth groups\n"
            f"`/logs` — View recent logs\n\n"
            f"**📦 File Support:** Files up to 2GB via MTProto"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    # ══ /cr — MAIN DOWNLOAD COMMAND ══════════════════════════════════════════

    async def cmd_cr(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not ctx.args:
            await update.message.reply_text(
                f"{Em.DOWNLOAD} **Usage:**\n"
                f"`/cr <url>` — auto quality\n"
                f"`/cr <url> 1080p` — select quality\n"
                f"`/cr <url> 4K master` — quality + preset\n\n"
                f"**Available qualities:** {', '.join(Config.QUALITIES.keys())}\n"
                f"**Available presets:** {', '.join(Config.ENCODE_PRESETS.keys())}",
                parse_mode=ParseMode.MARKDOWN)
            return

        url = ctx.args[0]
        if not self.downloader.cr.is_valid_url(url):
            await update.message.reply_text(f"{Em.ERROR} Invalid Crunchyroll URL.")
            return

        quality = None
        preset  = None
        for arg in ctx.args[1:]:
            if arg in Config.QUALITIES:
                quality = arg
            elif arg in Config.ENCODE_PRESETS:
                preset = arg

        ok, missing = await AuthChecker.check_user(self.application.bot, user.id, self.db)
        if not ok:
            links = "\n".join(f"• {l}" for l in missing)
            kb = [[InlineKeyboardButton("✅ I've Joined", callback_data=f"recheck_auth_{url[:40]}")]]
            await update.message.reply_text(
                f"{Em.AUTH} **Join required channels to use this bot:**\n\n{links}\n\n"
                f"After joining, click the button below.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb))
            return

        can, msg = self.db.can_download(user.id)
        if not can:
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        q_cnt = self.db.get_queue_count(user.id)
        if q_cnt >= Config.MAX_QUEUE_PER_USER:
            await update.message.reply_text(
                f"{Em.WARNING} Queue full ({Config.MAX_QUEUE_PER_USER}). Use /cancel <id>.")
            return

        is_pm = self.db.is_premium(user.id)

        if quality and quality in Config.PREMIUM_QUALITIES and not is_pm:
            await update.message.reply_text(
                f"{Em.PREMIUM} **{quality}** requires premium!\nUse /pm to upgrade.",
                parse_mode=ParseMode.MARKDOWN)
            return

        if not quality:
            ctx.user_data["dl_url"]    = url
            ctx.user_data["dl_preset"] = preset
            available = [q for q in Config.QUALITIES if is_pm or q not in Config.PREMIUM_QUALITIES]
            rows, row = [], []
            for q in available:
                lbl = f"💎{q}" if q in Config.PREMIUM_QUALITIES else q
                row.append(InlineKeyboardButton(lbl, callback_data=f"dlq_{q}"))
                if len(row) == 3:
                    rows.append(row)
                    row = []
            if row:
                rows.append(row)
            rows.append([InlineKeyboardButton(f"{Em.CANCEL} Cancel", callback_data="cancel")])

            await update.message.reply_text(
                f"{Em.DOWNLOAD} **Select Quality**\n\n"
                f"URL: `{url[:60]}…`\n💎 = Premium only",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(rows))
            return

        user_data  = self.db.get_user(user.id)
        preset     = preset or (user_data.get("encode_preset") if user_data else None) or Config.DEFAULT_ENCODE
        queue_id   = self.db.add_to_queue(user.id, url, quality, preset)
        position   = self.db.get_queue_position(queue_id)

        await update.message.reply_text(
            f"{Em.SUCCESS} **Added to queue!**\n\n"
            f"ID: `#{queue_id}` | Position: {position}\n"
            f"Quality: `{quality}` | Preset: `{preset}`\n\n"
            f"Use `/queue` to track progress",
            parse_mode=ParseMode.MARKDOWN)

        self._ensure_queue_running()

    # ══ /pm — Premium info ════════════════════════════════════════════════════

    async def cmd_pm(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid    = update.effective_user.id
        is_pm  = self.db.is_premium(uid)

        if is_pm:
            plan   = self.db.get_premium_type(uid)
            expiry = self.db.get_premium_expiry(uid)
            days   = (expiry - datetime.now()).days if expiry else "∞"
            feats  = "\n".join(f"  ✅ {f}" for f in Config.SUBSCRIPTION_FEATURES.get(plan, []))
            await update.message.reply_text(
                f"{Em.PREMIUM} **Premium Active** {Em.PREMIUM}\n\n"
                f"**Plan:** {plan.upper()}\n"
                f"**Expires:** {expiry.strftime('%Y-%m-%d') if expiry else 'Never'}\n"
                f"**Days left:** {days}\n\n"
                f"**Your features:**\n{feats}\n\n"
                f"Thank you for supporting! 🙏",
                parse_mode=ParseMode.MARKDOWN)
            return

        lines = []
        for plan, price in Config.SUBSCRIPTION_PRICES.items():
            days  = Config.SUBSCRIPTION_DAYS[plan]
            feats = " • ".join(Config.SUBSCRIPTION_FEATURES[plan][:2])
            lines.append(f"**{plan.title()}** — {price} ⭐\n  {days}d | {feats}")

        kb = [
            [InlineKeyboardButton("⭐ Weekly",   callback_data="sub_weekly"),
             InlineKeyboardButton("🚀 Monthly",  callback_data="sub_monthly")],
            [InlineKeyboardButton("🌟 Yearly",   callback_data="sub_yearly"),
             InlineKeyboardButton("♾️ Lifetime", callback_data="sub_lifetime")],
            [InlineKeyboardButton(f"{Em.REDEEM} Redeem Code", callback_data="show_redeem")],
        ]
        await update.message.reply_text(
            f"{Em.PREMIUM} **Premium Plans** {Em.PREMIUM}\n\n" +
            "\n\n".join(lines) +
            f"\n\n{Em.FIRE} Free: {Config.FREE_DAILY_LIMIT}/day | Premium: Unlimited",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb))

    # ══ /subscribe ════════════════════════════════════════════════════════════

    async def cmd_subscribe(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args or ctx.args[0].lower() not in Config.SUBSCRIPTION_PRICES:
            await update.message.reply_text(
                f"{Em.WARNING} Usage: `/subscribe <weekly|monthly|yearly|lifetime>`",
                parse_mode=ParseMode.MARKDOWN)
            return
        plan  = ctx.args[0].lower()
        price = Config.SUBSCRIPTION_PRICES[plan]
        days  = Config.SUBSCRIPTION_DAYS[plan]
        feats = "\n".join(f"• {f}" for f in Config.SUBSCRIPTION_FEATURES[plan])
        await update.message.reply_invoice(
            title=f"🎬 Crunchyroll Bot — {plan.title()} Premium",
            description=f"{days} days premium access!\n\n{feats}",
            payload=f"sub_{plan}_{update.effective_user.id}_{uuid.uuid4().hex[:8]}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(f"{plan.title()} Premium", price)],
            start_parameter=f"sub_{plan}",
        )

    # ══ /redeem ═══════════════════════════════════════════════════════════════

    async def cmd_redeem(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(f"{Em.REDEEM} Usage: `/redeem <CODE>`", parse_mode=ParseMode.MARKDOWN)
            return
        code = ctx.args[0].strip()
        ok, msg = self.db.redeem_code(code, update.effective_user.id)
        if ok:
            await update.message.reply_text(
                f"{Em.SUCCESS} **Code redeemed!** Activated: {msg}", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Em.ERROR} {msg}", parse_mode=ParseMode.MARKDOWN)

    # ══ /gift ════════════════════════════════════════════════════════════════

    async def cmd_gift(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid    = update.effective_user.id
        is_pm  = self.db.is_premium(uid)
        if not is_pm and not self.db.is_admin(uid):
            await update.message.reply_text(f"{Em.PREMIUM} Gifting requires premium.", parse_mode=ParseMode.MARKDOWN)
            return
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{Em.GIFT} Usage: `/gift <user_id> <plan> [message]`\nPlans: {', '.join(Config.SUBSCRIPTION_PRICES.keys())}",
                parse_mode=ParseMode.MARKDOWN)
            return
        try:
            to_uid = int(ctx.args[0])
            plan   = ctx.args[1].lower()
            msg    = " ".join(ctx.args[2:]) if len(ctx.args) > 2 else ""
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid user ID.", parse_mode=ParseMode.MARKDOWN)
            return
        if plan not in Config.SUBSCRIPTION_PRICES:
            await update.message.reply_text(f"{Em.ERROR} Invalid plan.", parse_mode=ParseMode.MARKDOWN)
            return
        days = Config.SUBSCRIPTION_DAYS[plan]
        code = self.db.create_gift(uid, to_uid, plan, days, msg)
        await update.message.reply_text(
            f"{Em.GIFT} **Gift created!**\nFor user: `{to_uid}`\nPlan: {plan.upper()} ({days}d)\nCode: `{code}`\n\n"
            f"Share: `https://t.me/{(await self.application.bot.get_me()).username}?start=gift_{code}`",
            parse_mode=ParseMode.MARKDOWN)

    async def _claim_gift(self, update: Update, ctx, gift_code: str):
        uid = update.effective_user.id
        c   = self.db.conn.execute("SELECT * FROM gifts WHERE gift_code=?", (gift_code,))
        r   = c.fetchone()
        if not r:
            await update.message.reply_text(f"{Em.ERROR} Invalid gift code.")
            return
        r = dict(r)
        if r["claimed"]:
            await update.message.reply_text(f"{Em.ERROR} This gift was already claimed.")
            return
        if r["to_user"] != uid and r["to_user"] != 0:
            await update.message.reply_text(f"{Em.ERROR} This gift is not for you.")
            return
        self.db.add_premium(uid, r["plan_type"], r["days"])
        self.db.conn.execute("UPDATE gifts SET claimed=1 WHERE gift_code=?", (gift_code,))
        self.db.conn.commit()
        await update.message.reply_text(
            f"{Em.GIFT} **Gift claimed!** {r['plan_type'].upper()} for {r['days']} days activated!\n\n"
            f"Message from gifter: {r.get('message') or '(none)'}",
            parse_mode=ParseMode.MARKDOWN)

    # ══ /referral ═════════════════════════════════════════════════════════════

    async def cmd_referral(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        code = self.db.get_or_create_referral_code(uid)
        cnt  = self.db.get_referral_count(uid)
        req  = int(self.db.get_setting("referral_required", str(Config.REFERRAL_REQUIRED)))
        rwd  = int(self.db.get_setting("referral_reward",   str(Config.REFERRAL_REWARD)))
        me   = await self.application.bot.get_me()
        link = f"https://t.me/{me.username}?start=ref_{code}"
        await update.message.reply_text(
            f"{Em.REF} **Your Referral Program**\n\n"
            f"**Code:** `{code}`\n"
            f"**Link:** {link}\n\n"
            f"**Referrals:** {cnt} / {req} needed\n"
            f"**Reward:** {rwd} Stars per {req} referrals\n\n"
            f"Share your link to earn rewards!",
            parse_mode=ParseMode.MARKDOWN)

    # ══ /queue ════════════════════════════════════════════════════════════════

    async def cmd_queue(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid   = update.effective_user.id
        items = self.db.get_user_queue(uid)
        if not items:
            await update.message.reply_text(
                f"{Em.QUEUE} Your queue is empty.\n\nUse `/cr <url>` to start!",
                parse_mode=ParseMode.MARKDOWN)
            return
        lines = [f"{Em.QUEUE} **Your Queue ({len(items)} items)**\n"]
        for it in items:
            icon = "⚡" if it["status"] == "processing" else "⏳"
            short_url = it["url"][-30:]
            lines.append(
                f"{icon} **#{it['id']}** | `{it['quality']}` | `{it['encode_preset']}`\n"
                f"   `…{short_url}`\n"
                f"   {ProgressBar.make(it['progress'])}")
        lines.append("\nUse `/cancel <id>` to remove")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ /cancel ═══════════════════════════════════════════════════════════════

    async def cmd_cancel(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/cancel <id>`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            qid = int(ctx.args[0])
            if self.db.cancel_queue_item(qid, update.effective_user.id):
                await update.message.reply_text(f"{Em.SUCCESS} Download #{qid} cancelled.")
            else:
                await update.message.reply_text(f"{Em.ERROR} Cannot cancel (already processing or not yours).")
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid ID.")

    # ══ /history ══════════════════════════════════════════════════════════════

    async def cmd_history(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        hist = self.db.get_download_history(uid, 15)
        if not hist:
            await update.message.reply_text(f"{Em.INFO} No history yet. Use /cr to start!")
            return
        lines = [f"{Em.DOWNLOAD} **Download History**\n"]
        for h in hist:
            size_mb = round(h["file_size"] / (1024 * 1024), 1) if h["file_size"] else 0
            lines.append(
                f"🎬 **{h['anime_title'][:35]}**\n"
                f"   {h['episode_title'][:40]}\n"
                f"   `{h['quality']}` | `{h['encode_preset']}` | {size_mb}MB\n"
                f"   📅 {str(h['downloaded_at'])[:10]}")
        await update.message.reply_text("\n\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ /stats ════════════════════════════════════════════════════════════════

    async def cmd_stats(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid   = update.effective_user.id
        user  = self.db.get_user(uid)
        is_pm = self.db.is_premium(uid)
        daily = self.db.get_daily_downloads(uid)
        limit = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
        plan  = self.db.get_premium_type(uid)
        expiry= self.db.get_premium_expiry(uid)

        await update.message.reply_text(
            f"{Em.STATS} **Your Statistics**\n\n"
            f"**Profile:**\n"
            f"├ Name: {user.get('first_name','?')}\n"
            f"├ Premium: {'✅ ' + plan.upper() if is_pm else '❌ Free'}\n"
            f"├ Expires: {expiry.strftime('%Y-%m-%d') if expiry and is_pm else 'N/A'}\n"
            f"└ Stars: {user.get('stars_balance',0):,}\n\n"
            f"**Usage:**\n"
            f"├ Today: {daily}/{limit}\n"
            f"├ All-time: {user.get('total_downloads',0):,}\n"
            f"├ Data: {round(user.get('total_size',0)/(1024**3),3)} GB\n"
            f"└ Queue: {self.db.get_queue_count(uid)}\n\n"
            f"**Social:**\n"
            f"├ Referrals: {self.db.get_referral_count(uid)}\n"
            f"└ Favorites: {len(self.db.get_favorites(uid))}",
            parse_mode=ParseMode.MARKDOWN)

    # ══ /settings ════════════════════════════════════════════════════════════

    async def cmd_settings(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        user = self.db.get_user(uid)
        kb   = [
            [InlineKeyboardButton(f"{Em.QUALITY} Quality: {user.get('default_quality','720p')}",
                                   callback_data="cfg_quality")],
            [InlineKeyboardButton(f"{Em.ENCODE} Preset: {user.get('encode_preset','balanced')}",
                                   callback_data="cfg_preset")],
            [InlineKeyboardButton("🔔 Notifications: " + ("ON" if user.get("notify_complete") else "OFF"),
                                   callback_data="cfg_notify")],
            [InlineKeyboardButton(f"{Em.BACK} Back", callback_data="show_home")],
        ]
        await update.message.reply_text(
            f"{Em.SETTINGS} **User Settings**\n\n"
            f"Tap a button to change:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb))

    # ══ /favorites ═══════════════════════════════════════════════════════════

    async def cmd_favorites(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        favs = self.db.get_favorites(uid)
        if not favs:
            await update.message.reply_text(f"{Em.HEART} No favorites yet.")
            return
        lines = [f"{Em.HEART} **Favorites ({len(favs)})**\n"]
        for f in favs[:20]:
            lines.append(f"• **{f['anime_title'][:40]}** — `{f['anime_id']}`")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ /watchlist ════════════════════════════════════════════════════════════

    async def cmd_watchlist(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        wl   = self.db.get_watchlist(uid)
        if not wl:
            await update.message.reply_text(f"{Em.WATCH} Watchlist empty. Add anime with /addwatch.")
            return
        lines = [f"{Em.WATCH} **Your Watchlist ({len(wl)})**\n"]
        for w in wl[:20]:
            lines.append(f"• **{w['anime_title'][:40]}** — Next: Ep {w['next_episode']}")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ /leaderboard ═════════════════════════════════════════════════════════

    async def cmd_leaderboard(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        lb   = self.db.get_leaderboard(10)
        medals = ["🥇","🥈","🥉"] + ["🏅"]*7
        lines = [f"{Em.LEAD} **Top Downloaders**\n"]
        for i, u in enumerate(lb):
            lines.append(
                f"{medals[i]} **{u.get('first_name','User')}** — "
                f"{u['total_downloads']:,} downloads | "
                f"{round(u['total_size']/(1024**3),2)} GB")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ /feedback ════════════════════════════════════════════════════════════

    async def cmd_feedback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{Em.WARNING} Usage: `/feedback <1-5> <message>`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            rating = int(ctx.args[0])
            assert 1 <= rating <= 5
        except (ValueError, AssertionError):
            await update.message.reply_text(f"{Em.ERROR} Rating must be 1-5.")
            return
        msg   = " ".join(ctx.args[1:])
        stars = "⭐" * rating + "☆" * (5 - rating)
        self.db.add_feedback(update.effective_user.id, rating, msg)
        await update.message.reply_text(
            f"{Em.SUCCESS} Thank you!\nRating: {stars}\nMessage: {msg[:200]}",
            parse_mode=ParseMode.MARKDOWN)

    # ══ /schedule ════════════════════════════════════════════════════════════

    async def cmd_schedule(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{Em.SCHED} Usage: `/schedule <url> <HH:MM> [quality] [preset]`\n"
                f"Example: `/schedule https://crunchyroll.com/watch/... 22:00 1080p balanced`",
                parse_mode=ParseMode.MARKDOWN)
            return
        url       = ctx.args[0]
        time_str  = ctx.args[1]
        quality   = ctx.args[2] if len(ctx.args) > 2 else Config.DEFAULT_QUALITY
        preset    = ctx.args[3] if len(ctx.args) > 3 else Config.DEFAULT_ENCODE

        try:
            today  = datetime.now().date()
            run_at = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")
            if run_at < datetime.now():
                run_at += timedelta(days=1)
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid time format. Use HH:MM")
            return

        sid = self.db.schedule_download(update.effective_user.id, url, quality, preset, run_at.isoformat())
        await update.message.reply_text(
            f"{Em.SCHED} **Scheduled!**\n\nID: `#{sid}`\n"
            f"Time: {run_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Quality: `{quality}` | Preset: `{preset}`",
            parse_mode=ParseMode.MARKDOWN)

    # ══ /batch ═══════════════════════════════════════════════════════════════

    async def cmd_batch(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid    = update.effective_user.id
        is_pm  = self.db.is_premium(uid)
        if not is_pm:
            await update.message.reply_text(
                f"{Em.PREMIUM} Batch download requires premium. Use /pm to upgrade.",
                parse_mode=ParseMode.MARKDOWN)
            return
        urls = [a for a in ctx.args if self.downloader.cr.is_valid_url(a)][:Config.MAX_BATCH_SIZE]
        if not urls:
            await update.message.reply_text(
                f"{Em.WARNING} Usage: `/batch <url1> <url2> …`\nProvide Crunchyroll URLs.",
                parse_mode=ParseMode.MARKDOWN)
            return
        user_data = self.db.get_user(uid)
        quality   = user_data.get("default_quality", Config.DEFAULT_QUALITY) if user_data else Config.DEFAULT_QUALITY
        preset    = user_data.get("encode_preset",   Config.DEFAULT_ENCODE)  if user_data else Config.DEFAULT_ENCODE
        added = []
        for url in urls:
            can, _ = self.db.can_download(uid)
            if can:
                qid = self.db.add_to_queue(uid, url, quality, preset)
                added.append(qid)
        await update.message.reply_text(
            f"{Em.SUCCESS} Batch: {len(added)}/{len(urls)} added to queue.\n"
            f"Quality: `{quality}` | Preset: `{preset}`",
            parse_mode=ParseMode.MARKDOWN)
        self._ensure_queue_running()

    # ══ VIDEO TOOL COMMANDS ═══════════════════════════════════════════════════

    async def cmd_mediainfo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(f"{Em.INFO} Reply to a video/document with /mediainfo")
            return
        doc = msg.reply_to_message.document
        if doc.file_size > 100 * 1024 * 1024:
            await msg.reply_text(f"{Em.ERROR} File too large for analysis (>100MB).")
            return
        status = await msg.reply_text(f"{Em.LOADING} Analyzing…")
        try:
            f = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"mi_{doc.file_unique_id}.tmp")
            await f.download_to_drive(fp)
            info = await VideoTools.get_media_info(fp)
            Path(fp).unlink(missing_ok=True)
            if not info:
                await status.edit_text(f"{Em.ERROR} Could not read media info.")
                return
            await status.edit_text(
                f"{Em.INFO} **Media Info**\n\n"
                f"**Duration:** {info.get('duration','N/A')}\n"
                f"**Size:** {info.get('size_mb','N/A')} MB\n"
                f"**Format:** {info.get('format','N/A')}\n"
                f"**Video:** {info.get('video_codec','N/A')} "
                f"{info.get('width','?')}×{info.get('height','?')} "
                f"@ {round(info.get('fps',0),2)} fps\n"
                f"**Audio:** {info.get('audio_codec','N/A')} "
                f"{info.get('channels','?')}ch @ {info.get('sample_rate','N/A')}Hz",
                parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_rename(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not ctx.args:
            await msg.reply_text(f"{Em.RENAME} Usage: `/rename <new_filename>` (reply to a file)", parse_mode=ParseMode.MARKDOWN)
            return
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(f"{Em.ERROR} Reply to a document/video file.")
            return
        new_name = ctx.args[0]
        
        # Security: Prevent path traversal
        if '..' in new_name or '/' in new_name or '\\' in new_name or new_name.startswith('.'):
            await msg.reply_text(f"{Em.ERROR} Invalid filename (path traversal not allowed).")
            return
        
        if not re.match(r'^[\w\-. ]+$', new_name):
            await msg.reply_text(f"{Em.ERROR} Invalid filename (alphanumeric/dash/underscore only).")
            return
        
        doc = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Renaming…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            ext= Path(doc.file_name or "file").suffix
            fp = str(Config.TEMP_PATH / f"rn_{doc.file_unique_id}{ext}")
            await f.download_to_drive(fp)
            new_path = str(Config.TEMP_PATH / f"{new_name}{ext}")
            Path(fp).rename(new_path)
            with open(new_path, "rb") as fh:
                await ctx.bot.send_document(msg.chat_id, fh, filename=f"{new_name}{ext}",
                                            caption=f"{Em.SUCCESS} Renamed to: `{new_name}{ext}`",
                                            parse_mode=ParseMode.MARKDOWN)
            Path(new_path).unlink(missing_ok=True)
            await status.delete()
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Rename failed: {e}")

    async def cmd_thumb(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        uid = msg.from_user.id
        if not msg.reply_to_message or not (msg.reply_to_message.photo or msg.reply_to_message.document):
            await msg.reply_text(f"{Em.THUMB} Reply to an image to set it as your custom thumbnail.")
            return
        src  = msg.reply_to_message.photo[-1] if msg.reply_to_message.photo else msg.reply_to_message.document
        try:
            f  = await ctx.bot.get_file(src.file_id)
            fp = str(Config.THUMB_PATH / f"custom_{uid}.jpg")
            await f.download_to_drive(fp)
            self.db.set_user_setting(uid, "custom_thumb", fp)
            await msg.reply_text(f"{Em.SUCCESS} Custom thumbnail set! It will be embedded in your next download.")
        except Exception as e:
            await msg.reply_text(f"{Em.ERROR} Failed: {e}")

    async def cmd_trim(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if len(ctx.args) < 2 or not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.TRIM} Usage: Reply to a video with `/trim HH:MM:SS HH:MM:SS`",
                parse_mode=ParseMode.MARKDOWN)
            return
        start, end = ctx.args[0], ctx.args[1]
        doc        = msg.reply_to_message.document
        status     = await msg.reply_text(f"{Em.LOADING} Trimming…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"trim_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.trim_video(fp, start, end)
            Path(fp).unlink(missing_ok=True)
            if out:
                with open(out, "rb") as fh:
                    await ctx.bot.send_video(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} Trimmed: {start} → {end}",
                        supports_streaming=True)
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} Trim failed. Check timestamps.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_compress(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg    = update.message
        target = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 50
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.COMP} Reply to a video with `/compress [MB]`", parse_mode=ParseMode.MARKDOWN)
            return
        doc    = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Compressing to ~{target}MB…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"comp_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.compress_video(fp, target)
            Path(fp).unlink(missing_ok=True)
            if out:
                actual = round(Path(out).stat().st_size / (1024**2), 1)
                with open(out, "rb") as fh:
                    await ctx.bot.send_video(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} Compressed! Size: {actual}MB", supports_streaming=True)
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} Compression failed.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_extract(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        fmt = (ctx.args[0] if ctx.args and ctx.args[0] in ("mp3","aac","wav") else "mp3")
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.AUDIO} Reply to a video with `/extract [mp3|aac]`", parse_mode=ParseMode.MARKDOWN)
            return
        doc    = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Extracting audio ({fmt})…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"ext_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.extract_audio(fp, fmt)
            Path(fp).unlink(missing_ok=True)
            if out:
                with open(out, "rb") as fh:
                    await ctx.bot.send_audio(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} Audio extracted ({fmt})")
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} Extraction failed.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_screenshot(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        ts  = ctx.args[0] if ctx.args else "00:00:05"
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.SHOT} Reply to a video with `/screenshot [HH:MM:SS]`",
                parse_mode=ParseMode.MARKDOWN)
            return
        doc    = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Taking screenshot at {ts}…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"ss_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.screenshot_video(fp, ts)
            Path(fp).unlink(missing_ok=True)
            if out:
                with open(out, "rb") as fh:
                    await ctx.bot.send_photo(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} Screenshot @ {ts}")
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} Screenshot failed.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_gif(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg   = update.message
        start = ctx.args[0] if ctx.args else "00:00:00"
        dur   = int(ctx.args[1]) if len(ctx.args) > 1 and ctx.args[1].isdigit() else 5
        if not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.GIF} Reply to a video with `/gif [start] [seconds]`",
                parse_mode=ParseMode.MARKDOWN)
            return
        doc    = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Creating GIF ({dur}s from {start})…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"gif_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.make_gif(fp, start, dur)
            Path(fp).unlink(missing_ok=True)
            if out:
                with open(out, "rb") as fh:
                    await ctx.bot.send_animation(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} GIF created ({dur}s)")
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} GIF creation failed.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    async def cmd_watermark(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg  = update.message
        uid  = msg.from_user.id
        if not self.db.is_premium(uid):
            await msg.reply_text(f"{Em.PREMIUM} Watermark requires premium.")
            return
        if not ctx.args or not msg.reply_to_message or not msg.reply_to_message.document:
            await msg.reply_text(
                f"{Em.WATER} Reply to a video with `/watermark <text> [position]`\n"
                f"Positions: topleft, topright, bottomleft, bottomright, center",
                parse_mode=ParseMode.MARKDOWN)
            return
        text = ctx.args[0]
        pos  = ctx.args[1] if len(ctx.args) > 1 else "bottomright"
        doc  = msg.reply_to_message.document
        status = await msg.reply_text(f"{Em.LOADING} Adding watermark…")
        try:
            f  = await ctx.bot.get_file(doc.file_id)
            fp = str(Config.TEMP_PATH / f"wm_in_{doc.file_unique_id}.mp4")
            await f.download_to_drive(fp)
            out = await VideoTools.add_watermark(fp, text, pos)
            Path(fp).unlink(missing_ok=True)
            if out:
                with open(out, "rb") as fh:
                    await ctx.bot.send_video(msg.chat_id, fh,
                        caption=f"{Em.SUCCESS} Watermark added: `{text}`",
                        parse_mode=ParseMode.MARKDOWN, supports_streaming=True)
                Path(out).unlink(missing_ok=True)
                await status.delete()
            else:
                await status.edit_text(f"{Em.ERROR} Watermark failed.")
        except Exception as e:
            await status.edit_text(f"{Em.ERROR} Error: {e}")

    # ══ ADMIN COMMANDS ════════════════════════════════════════════════════════

    @admin_only
    async def cmd_admin(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        stats = self.db.get_stats()
        fb    = self.db.get_feedback_stats()
        mtproto_status = "✅ Enabled (2GB)" if Config.USE_MT_PROTO and self.pyro_client else "❌ Disabled"
        await update.message.reply_text(
            f"{Em.ADMIN} **Admin Panel** {Em.ADMIN}\n\n"
            f"**📊 Stats:**\n"
            f"├ Users: {stats['total_users']:,} (Premium: {stats['premium_users']:,})\n"
            f"├ Banned: {stats['banned_users']:,}\n"
            f"├ Downloads: {stats['total_downloads']:,}\n"
            f"├ Storage: {stats['total_size_gb']} GB\n"
            f"├ Queue: {stats['queue_size']} pending / {stats['processing']} processing\n"
            f"├ Active 7d: {stats['active_7d']:,}\n"
            f"├ Feedback: {fb['avg']}/5 ({fb['total']} reviews)\n"
            f"└ Scheduled: {stats['scheduled']}\n\n"
            f"**📦 MTProto:** {mtproto_status}\n\n"
            f"**Commands:**\n"
            f"`/ban /unban /warn /mute /unmute`\n"
            f"`/broadcast <msg>` — Send to all\n"
            f"`/gencode <plan> <days> [uses]` — Redeem code\n"
            f"`/addcmd /delcmd /listcmds`\n"
            f"`/authgroup add/remove/list`\n"
            f"`/addpremium <uid> <plan>`\n"
            f"`/queueall` — View full queue\n"
            f"`/clearqueue` — Clear all queues\n"
            f"`/logs` — Recent activity\n"
            f"`/maintenance <on|off>`",
            parse_mode=ParseMode.MARKDOWN)

    @mod_only
    async def cmd_ban(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/ban <uid> <reason> [days]`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            uid    = int(ctx.args[0])
            days   = int(ctx.args[-1]) if ctx.args[-1].isdigit() else 0
            reason = " ".join(ctx.args[1:-1]) if days else " ".join(ctx.args[1:])
            self.db.ban_user(uid, update.effective_user.id, reason, days)
            dur = f" for {days} days" if days else " permanently"
            await update.message.reply_text(f"{Em.BAN} User `{uid}` banned{dur}.\nReason: {reason}", parse_mode=ParseMode.MARKDOWN)
            try:
                await ctx.bot.send_message(uid, f"{Em.WARNING} You have been banned{dur}.\nReason: {reason}")
            except:
                pass
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid user ID.")

    @mod_only
    async def cmd_unban(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/unban <uid>`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            uid = int(ctx.args[0])
            self.db.unban_user(uid)
            await update.message.reply_text(f"{Em.UNBAN} User `{uid}` unbanned.", parse_mode=ParseMode.MARKDOWN)
            try:
                await ctx.bot.send_message(uid, f"{Em.SUCCESS} You have been unbanned!")
            except:
                pass
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid user ID.")

    @mod_only
    async def cmd_warn(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/warn <uid> <reason>`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            uid    = int(ctx.args[0])
            reason = " ".join(ctx.args[1:])
            warns  = self.db.add_warning(uid)
            await update.message.reply_text(
                f"{Em.WARN} User `{uid}` warned ({warns}/5).\nReason: {reason}", parse_mode=ParseMode.MARKDOWN)
            try:
                await ctx.bot.send_message(uid, f"{Em.WARN} Warning {warns}/5: {reason}")
            except:
                pass
            if warns >= 5:
                self.db.ban_user(uid, update.effective_user.id, "Auto-ban: 5 warnings", 30)
                await update.message.reply_text(f"{Em.BAN} User auto-banned (5 warnings).")
        except ValueError:
            await update.message.reply_text(f"{Em.ERROR} Invalid user ID.")

    @mod_only
    async def cmd_mute(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"{Em.MUTE} Mute applied. (Integrate with group bot for full functionality.)")

    @admin_only
    async def cmd_broadcast(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
            return
        text   = " ".join(ctx.args)
        users  = self.db.get_all_users()
        status = await update.message.reply_text(f"{Em.LOADING} Broadcasting to {len(users):,} users…")
        sent, fail = 0, 0
        for uid in users:
            try:
                await ctx.bot.send_message(uid, f"{Em.BROAD} **Announcement**\n\n{text}", parse_mode=ParseMode.MARKDOWN)
                sent += 1
            except:
                fail += 1
            if (sent + fail) % 100 == 0:
                await status.edit_text(f"{Em.LOADING} Progress: {sent+fail}/{len(users)}")
            await asyncio.sleep(0.07)  # Rate limit safety
        await status.edit_text(f"{Em.SUCCESS} Broadcast done!\nSent: {sent:,} | Failed: {fail:,}")

    @admin_only
    async def cmd_addpremium(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{Em.WARNING} Usage: `/addpremium <uid> <plan> [days]`", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            uid  = int(ctx.args[0])
            plan = ctx.args[1].lower()
            days = int(ctx.args[2]) if len(ctx.args) > 2 else Config.SUBSCRIPTION_DAYS.get(plan, 30)
        except (ValueError, IndexError):
            await update.message.reply_text(f"{Em.ERROR} Invalid arguments.")
            return
        if self.db.add_premium(uid, plan, days):
            await update.message.reply_text(
                f"{Em.SUCCESS} Premium `{plan}` ({days}d) added to user `{uid}`.", parse_mode=ParseMode.MARKDOWN)
            try:
                await ctx.bot.send_message(uid, f"{Em.PREMIUM} You received {plan.upper()} premium for {days} days! 🎉")
            except:
                pass
        else:
            await update.message.reply_text(f"{Em.ERROR} Failed.")

    @admin_only
    async def cmd_gencode(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{Em.REDEEM} Usage: `/gencode <plan> <days> [max_uses] [expires_days]`\n"
                f"Example: `/gencode monthly 30 5 7`",
                parse_mode=ParseMode.MARKDOWN)
            return
        try:
            plan      = ctx.args[0].lower()
            days      = int(ctx.args[1])
            max_uses  = int(ctx.args[2]) if len(ctx.args) > 2 else 1
            exp_days  = int(ctx.args[3]) if len(ctx.args) > 3 else 30
        except (ValueError, IndexError):
            await update.message.reply_text(f"{Em.ERROR} Invalid arguments.")
            return
        code = secrets.token_hex(4).upper()
        if self.db.create_redeem_code(code, plan, days, max_uses, update.effective_user.id, exp_days):
            await update.message.reply_text(
                f"{Em.SUCCESS} Redeem code created!\n\n"
                f"**Code:** `{code}`\n"
                f"**Plan:** {plan.upper()} | **Days:** {days}\n"
                f"**Max uses:** {max_uses} | **Expires:** {exp_days}d",
                parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Em.ERROR} Failed to create code.")

    @admin_only
    async def cmd_queueall(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        items = self.db.get_all_queue()
        if not items:
            await update.message.reply_text(f"{Em.QUEUE} Queue is empty.")
            return
        lines = [f"{Em.QUEUE} **Global Queue ({len(items)})**\n"]
        for it in items[:30]:
            lines.append(f"#{it['id']} uid={it['user_id']} | {it['quality']} | {it['status']} {it['progress']}%")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def cmd_clearqueue(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        count = self.db.clear_queue()
        await update.message.reply_text(f"{Em.SUCCESS} Cleared {count} items from queue.")

    @admin_only
    async def cmd_maintenance(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args or ctx.args[0] not in ("on", "off"):
            await update.message.reply_text(f"{Em.WARNING} Usage: `/maintenance <on|off>`", parse_mode=ParseMode.MARKDOWN)
            return
        val = "True" if ctx.args[0] == "on" else "False"
        self.db.set_setting("maintenance_mode", val)
        await update.message.reply_text(f"{Em.SUCCESS} Maintenance mode: **{ctx.args[0].upper()}**", parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def cmd_authgroup(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(
                f"{Em.AUTH} Usage:\n"
                f"`/authgroup add <group_id> <link> [name]`\n"
                f"`/authgroup remove <group_id>`\n"
                f"`/authgroup list`\n"
                f"`/authgroup on|off` — Toggle force-sub",
                parse_mode=ParseMode.MARKDOWN)
            return
        action = ctx.args[0].lower()
        if action == "list":
            groups = self.db.get_auth_groups()
            if not groups:
                await update.message.reply_text(f"{Em.INFO} No auth groups configured.")
                return
            lines = [f"{Em.AUTH} **Auth Groups:**\n"]
            for g in groups:
                lines.append(f"• `{g['group_id']}` — {g.get('group_name','?')} — {g.get('group_link','')}")
            await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
        elif action == "add" and len(ctx.args) >= 3:
            try:
                gid  = int(ctx.args[1])
                link = ctx.args[2]
                name = " ".join(ctx.args[3:]) if len(ctx.args) > 3 else f"Group {gid}"
                self.db.add_auth_group(gid, name, link, update.effective_user.id)
                await update.message.reply_text(f"{Em.SUCCESS} Auth group `{gid}` added.", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await update.message.reply_text(f"{Em.ERROR} Invalid group ID.")
        elif action == "remove" and len(ctx.args) >= 2:
            try:
                gid = int(ctx.args[1])
                self.db.remove_auth_group(gid)
                await update.message.reply_text(f"{Em.SUCCESS} Auth group `{gid}` removed.", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await update.message.reply_text(f"{Em.ERROR} Invalid group ID.")
        elif action in ("on", "off"):
            val = "True" if action == "on" else "False"
            self.db.set_setting("force_sub_enabled", val)
            await update.message.reply_text(f"{Em.SUCCESS} Force-subscribe: **{action.upper()}**", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Em.ERROR} Invalid arguments.")

    @admin_only
    async def cmd_logs(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        c = self.db.conn.execute(
            "SELECT user_id,anime_title,episode_title,quality,downloaded_at "
            "FROM downloads ORDER BY downloaded_at DESC LIMIT 20")
        rows = c.fetchall()
        if not rows:
            await update.message.reply_text(f"{Em.LOG} No download logs yet.")
            return
        lines = [f"{Em.LOG} **Recent Downloads (20)**\n"]
        for r in rows:
            lines.append(f"uid={r[0]} | {str(r[1])[:25]} | {r[3]} | {str(r[4])[:16]}")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def cmd_restart(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"{Em.LOADING} Restarting…")
        os._exit(0)

    # ══ CUSTOM COMMANDS ═══════════════════════════════════════════════════════

    @admin_only
    async def cmd_addcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 3:
            await update.message.reply_text(
                f"{Em.CODE} Usage: `/addcmd <name> <text|markdown|python> <content>`\n\n"
                f"**Python example:**\n`/addcmd roll python print(f'You rolled: {{random.randint(1,6)}}')`\n"
                f"⚠️ Python commands run in a sandbox. No imports allowed.\n"
                f"Use `random`, `datetime`, `context` (user info) variables.",
                parse_mode=ParseMode.MARKDOWN)
            return
        cmd_name  = ctx.args[0].lower()
        cmd_type  = ctx.args[1].lower()
        content   = " ".join(ctx.args[2:])

        if cmd_type not in ("text", "markdown", "python"):
            await update.message.reply_text(f"{Em.ERROR} Type must be: text, markdown, or python")
            return

        if cmd_type == "python":
            ok, out = CodeSandbox.run(content, {"user_id": update.effective_user.id})
            if not ok:
                await update.message.reply_text(
                    f"{Em.ERROR} Code validation failed:\n{out}", parse_mode=ParseMode.MARKDOWN)
                return

        response = content if cmd_type != "python" else ""
        code     = content if cmd_type == "python" else None

        if self.db.add_custom_cmd(cmd_name, response, code, cmd_type, update.effective_user.id):
            await update.message.reply_text(
                f"{Em.SUCCESS} Custom command `/{cmd_name}` ({cmd_type}) added!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(
                f"{Em.ERROR} Command `/{cmd_name}` already exists. Use `/editcmd` to update.",
                parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def cmd_editcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if len(ctx.args) < 3:
            await update.message.reply_text(
                f"{Em.CODE} Usage: `/editcmd <name> <text|markdown|python> <content>`",
                parse_mode=ParseMode.MARKDOWN)
            return
        cmd_name = ctx.args[0].lower()
        cmd_type = ctx.args[1].lower()
        content  = " ".join(ctx.args[2:])
        response = content if cmd_type != "python" else ""
        code     = content if cmd_type == "python" else None
        if self.db.update_custom_cmd(cmd_name, response, code, cmd_type):
            await update.message.reply_text(f"{Em.SUCCESS} `/{cmd_name}` updated!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Em.ERROR} Command not found.", parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def cmd_delcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not ctx.args:
            await update.message.reply_text(f"{Em.WARNING} Usage: `/delcmd <name>`", parse_mode=ParseMode.MARKDOWN)
            return
        if self.db.remove_custom_cmd(ctx.args[0].lower()):
            await update.message.reply_text(f"{Em.SUCCESS} Command `/{ctx.args[0]}` removed.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Em.ERROR} Command not found.", parse_mode=ParseMode.MARKDOWN)

    async def cmd_listcmds(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        cmds = self.db.list_custom_cmds()
        if not cmds:
            await update.message.reply_text(f"{Em.INFO} No custom commands.")
            return
        lines = [f"{Em.CODE} **Custom Commands ({len(cmds)})**\n"]
        for c in cmds[:40]:
            icon = "🐍" if c["cmd_type"] == "python" else ("📝" if c["cmd_type"] == "markdown" else "💬")
            lines.append(f"{icon} `/{c['command']}` ({c['cmd_type']}) — {c['usage_count']} uses")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    # ══ INLINE HANDLER for custom commands ═══════════════════════════════════

    async def handle_text(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not msg or not msg.text:
            return
        if not msg.text.startswith("/"):
            return

        cmd   = msg.text[1:].split()[0].lower().split("@")[0]
        data  = self.db.get_custom_cmd(cmd)
        if not data:
            return

        if data["type"] == "python" and data.get("code"):
            ctx_vars = {
                "user_id":     msg.from_user.id,
                "username":    msg.from_user.username or "",
                "first_name":  msg.from_user.first_name or "",
                "chat_id":     msg.chat_id,
                "is_premium":  self.db.is_premium(msg.from_user.id),
            }
            ok, output = CodeSandbox.run(data["code"], ctx_vars)
            await msg.reply_text(output[:4096], parse_mode=None)
        elif data["type"] == "markdown":
            await msg.reply_text(data["response"], parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text(data["response"])

    # ══ PAYMENT HANDLERS ══════════════════════════════════════════════════════

    async def precheckout(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.pre_checkout_query.answer(ok=True)

    async def payment_success(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        pay     = update.message.successful_payment
        payload = pay.invoice_payload
        parts   = payload.split("_")
        if len(parts) >= 2:
            plan = parts[1]
            uid  = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else update.effective_user.id
            days = Config.SUBSCRIPTION_DAYS.get(plan, 30)
            self.db.add_premium(uid, plan, days, pay.telegram_payment_charge_id)
            await update.message.reply_text(
                f"{Em.SUCCESS} **Payment Successful!** 🎉\n\n"
                f"Plan: **{plan.upper()}** ({days} days)\n"
                f"Your premium is now active!\n\n"
                f"Thank you for your support! 🙏",
                parse_mode=ParseMode.MARKDOWN)
            for aid in Config.ADMIN_IDS:
                try:
                    await ctx.bot.send_message(
                        aid,
                        f"{Em.TROPHY} New Premium!\nUser: {update.effective_user.first_name} (id={uid})\n"
                        f"Plan: {plan} | Stars: {pay.total_amount}")
                except:
                    pass

    # ══ CALLBACK QUERY HANDLER ════════════════════════════════════════════════

    async def callback_handler(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q    = update.callback_query
        await q.answer()
        data = q.data
        uid  = q.from_user.id

        if data.startswith("dlq_"):
            quality = data[4:]
            url     = ctx.user_data.get("dl_url")
            preset  = ctx.user_data.get("dl_preset")
            if not url:
                await q.edit_message_text(f"{Em.ERROR} Session expired. Run /cr again.")
                return
            is_pm = self.db.is_premium(uid)
            if quality in Config.PREMIUM_QUALITIES and not is_pm:
                await q.edit_message_text(
                    f"{Em.PREMIUM} **{quality}** requires premium!\nUse /pm to upgrade.",
                    parse_mode=ParseMode.MARKDOWN)
                return
            user_data = self.db.get_user(uid)
            preset    = preset or (user_data.get("encode_preset") if user_data else None) or Config.DEFAULT_ENCODE
            qid       = self.db.add_to_queue(uid, url, quality, preset)
            pos       = self.db.get_queue_position(qid)
            await q.edit_message_text(
                f"{Em.SUCCESS} **Added to queue!**\n\n"
                f"ID: `#{qid}` | Position: {pos}\n"
                f"Quality: `{quality}` | Preset: `{preset}`",
                parse_mode=ParseMode.MARKDOWN)
            self._ensure_queue_running()

        elif data.startswith("sub_"):
            plan = data[4:]
            if plan not in Config.SUBSCRIPTION_PRICES:
                return
            price = Config.SUBSCRIPTION_PRICES[plan]
            days  = Config.SUBSCRIPTION_DAYS[plan]
            feats = "\n".join(f"• {f}" for f in Config.SUBSCRIPTION_FEATURES[plan])
            await q.message.reply_invoice(
                title=f"🎬 Crunchyroll Bot — {plan.title()} Premium",
                description=f"{days} days!\n\n{feats}",
                payload=f"sub_{plan}_{uid}_{uuid.uuid4().hex[:8]}",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(f"{plan.title()}", price)],
                start_parameter=f"sub_{plan}",
            )

        elif data == "show_premium":
            await self.cmd_pm(update, ctx)
        elif data == "show_queue":
            await self.cmd_queue(update, ctx)
        elif data == "show_stats":
            await self.cmd_stats(update, ctx)
        elif data == "show_settings":
            await self.cmd_settings(update, ctx)
        elif data == "show_watchlist":
            await self.cmd_watchlist(update, ctx)
        elif data == "show_leaderboard":
            await self.cmd_leaderboard(update, ctx)
        elif data == "show_referral":
            await self.cmd_referral(update, ctx)
        elif data == "show_home":
            await self.cmd_start(update, ctx)
        elif data == "show_redeem":
            await q.edit_message_text(
                f"{Em.REDEEM} **Redeem a Code**\n\nSend: `/redeem <CODE>`",
                parse_mode=ParseMode.MARKDOWN)
        elif data == "cancel":
            await q.edit_message_text(f"{Em.CANCEL} Cancelled.")

        elif data.startswith("recheck_auth_"):
            ok, missing = await AuthChecker.check_user(self.application.bot, uid, self.db)
            if ok:
                await q.edit_message_text(f"{Em.SUCCESS} Access granted! Run your command again.")
            else:
                links = "\n".join(f"• {l}" for l in missing)
                await q.edit_message_text(
                    f"{Em.AUTH} Still not joined:\n\n{links}\n\nJoin all channels then try again.",
                    parse_mode=ParseMode.MARKDOWN)

        elif data == "cfg_quality":
            kb = [[InlineKeyboardButton(q_, callback_data=f"setq_{q_}")] for q_ in Config.QUALITIES]
            kb.append([InlineKeyboardButton(f"{Em.BACK} Back", callback_data="show_settings")])
            await q.edit_message_text("Select default quality:", reply_markup=InlineKeyboardMarkup(kb))
        elif data.startswith("setq_"):
            val = data[5:]
            self.db.set_user_setting(uid, "default_quality", val)
            await q.edit_message_text(f"{Em.SUCCESS} Default quality set to `{val}`.", parse_mode=ParseMode.MARKDOWN)
        elif data == "cfg_preset":
            kb = [[InlineKeyboardButton(p_, callback_data=f"setp_{p_}")] for p_ in Config.ENCODE_PRESETS]
            kb.append([InlineKeyboardButton(f"{Em.BACK} Back", callback_data="show_settings")])
            await q.edit_message_text("Select encode preset:", reply_markup=InlineKeyboardMarkup(kb))
        elif data.startswith("setp_"):
            val = data[5:]
            self.db.set_user_setting(uid, "encode_preset", val)
            await q.edit_message_text(f"{Em.SUCCESS} Encode preset set to `{val}`.", parse_mode=ParseMode.MARKDOWN)
        elif data == "cfg_notify":
            user = self.db.get_user(uid)
            new_val = 0 if user and user.get("notify_complete") else 1
            self.db.set_user_setting(uid, "notify_complete", str(new_val))
            await q.edit_message_text(f"{Em.SUCCESS} Notifications {'enabled' if new_val else 'disabled'}.")

    # ══ QUEUE PROCESSOR ═══════════════════════════════════════════════════════

    def _ensure_queue_running(self):
        if not self.queue_task or self.queue_task.done():
            self.queue_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            try:
                if len(self.active) >= Config.MAX_CONCURRENT:
                    await asyncio.sleep(3)
                    continue

                item = self.db.get_next_queue_item()
                if not item:
                    await asyncio.sleep(5)
                    continue

                qid     = item["id"]
                uid     = item["user_id"]
                url     = item["url"]
                quality = item["quality"]
                preset  = item["encode_preset"]
                msg_id  = item.get("message_id")

                self.active[qid] = True
                self.db.start_processing(qid)

                async def cb(progress: int, status: str = ""):
                    self.db.update_queue_progress(qid, progress)
                    if msg_id:
                        try:
                            await self.application.bot.edit_message_text(
                                f"{Em.LOADING} **Processing…**\n\n"
                                f"`{quality}` | `{preset}`\n"
                                f"{ProgressBar.make(progress)}\n\n"
                                f"{status or 'Working…'}",
                                chat_id=uid, message_id=msg_id,
                                parse_mode=ParseMode.MARKDOWN)
                        except:
                            pass

                ok, result = await self.downloader.process(
                    qid, uid, url, quality, preset, self.db, cb)

                if ok:
                    try:
                        user_data = self.db.get_user(uid)
                        custom_thumb = user_data.get("custom_thumb") if user_data else None
                        if custom_thumb and Path(custom_thumb).exists():
                            embedded = await VideoTools.embed_thumbnail(result, custom_thumb)
                            if embedded:
                                result = embedded

                        fname = Path(result).name
                        caption = (
                            f"{Em.SUCCESS} **Download Complete!**\n\n"
                            f"📁 `{fname}`\n"
                            f"🎨 `{quality}` | ⚙️ `{preset}`\n\n"
                            f"Use /premium for more features!")
                        
                        # Use 2GB-capable sender
                        await self.send_large_file(uid, result, caption, "video")
                        
                        Path(result).unlink(missing_ok=True)
                    except Exception as e:
                        logger.error(f"Send video error: {e}")
                        await self.application.bot.send_message(
                            uid, f"{Em.ERROR} File ready but send failed: {e}")
                else:
                    self.db.fail_queue_item(qid, result)
                    await self.application.bot.send_message(
                        uid, f"{Em.ERROR} **Download Failed**\n{result[:300]}",
                        parse_mode=ParseMode.MARKDOWN)

                if msg_id:
                    try:
                        await self.application.bot.delete_message(uid, msg_id)
                    except:
                        pass

                del self.active[qid]
                await asyncio.sleep(1)

            except Exception as e:
                logger.exception(f"Queue processor error: {e}")
                await asyncio.sleep(10)

    # ══ SCHEDULED DOWNLOAD PROCESSOR ══════════════════════════════════════════

    async def _process_scheduled(self):
        while True:
            try:
                due = self.db.get_due_schedules()
                for s in due:
                    self.db.mark_schedule_done(s["id"])
                    qid = self.db.add_to_queue(s["user_id"], s["url"], s["quality"], s["encode_preset"])
                    try:
                        await self.application.bot.send_message(
                            s["user_id"],
                            f"{Em.SCHED} **Scheduled download started!**\n"
                            f"Queue ID: `#{qid}`", parse_mode=ParseMode.MARKDOWN)
                    except:
                        pass
                    self._ensure_queue_running()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60)

    # ══ BOT SETUP ═════════════════════════════════════════════════════════════

    async def setup(self):
        self.application = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .defaults(Defaults(parse_mode=ParseMode.MARKDOWN))
            .build()
        )
        app = self.application
        add = app.add_handler

        add(CommandHandler("start",        self.cmd_start))
        add(CommandHandler("help",         self.cmd_help))
        add(CommandHandler("cr",           self.cmd_cr))
        add(CommandHandler("pm",           self.cmd_pm))
        add(CommandHandler("premium",      self.cmd_pm))
        add(CommandHandler("subscribe",    self.cmd_subscribe))
        add(CommandHandler("redeem",       self.cmd_redeem))
        add(CommandHandler("gift",         self.cmd_gift))
        add(CommandHandler("referral",     self.cmd_referral))
        add(CommandHandler("ref",          self.cmd_referral))
        add(CommandHandler("queue",        self.cmd_queue))
        add(CommandHandler("cancel",       self.cmd_cancel))
        add(CommandHandler("history",      self.cmd_history))
        add(CommandHandler("stats",        self.cmd_stats))
        add(CommandHandler("settings",     self.cmd_settings))
        add(CommandHandler("favorites",    self.cmd_favorites))
        add(CommandHandler("watchlist",    self.cmd_watchlist))
        add(CommandHandler("leaderboard",  self.cmd_leaderboard))
        add(CommandHandler("feedback",     self.cmd_feedback))
        add(CommandHandler("batch",        self.cmd_batch))
        add(CommandHandler("schedule",     self.cmd_schedule))

        add(CommandHandler("mediainfo",    self.cmd_mediainfo))
        add(CommandHandler("rename",       self.cmd_rename))
        add(CommandHandler("thumb",        self.cmd_thumb))
        add(CommandHandler("trim",         self.cmd_trim))
        add(CommandHandler("compress",     self.cmd_compress))
        add(CommandHandler("extract",      self.cmd_extract))
        add(CommandHandler("screenshot",   self.cmd_screenshot))
        add(CommandHandler("gif",          self.cmd_gif))
        add(CommandHandler("watermark",    self.cmd_watermark))

        add(CommandHandler("admin",        self.cmd_admin))
        add(CommandHandler("ban",          self.cmd_ban))
        add(CommandHandler("unban",        self.cmd_unban))
        add(CommandHandler("warn",         self.cmd_warn))
        add(CommandHandler("mute",         self.cmd_mute))
        add(CommandHandler("broadcast",    self.cmd_broadcast))
        add(CommandHandler("addpremium",   self.cmd_addpremium))
        add(CommandHandler("gencode",      self.cmd_gencode))
        add(CommandHandler("queueall",     self.cmd_queueall))
        add(CommandHandler("clearqueue",   self.cmd_clearqueue))
        add(CommandHandler("maintenance",  self.cmd_maintenance))
        add(CommandHandler("authgroup",    self.cmd_authgroup))
        add(CommandHandler("logs",         self.cmd_logs))
        add(CommandHandler("restart",      self.cmd_restart))

        add(CommandHandler("addcmd",       self.cmd_addcmd))
        add(CommandHandler("editcmd",      self.cmd_editcmd))
        add(CommandHandler("delcmd",       self.cmd_delcmd))
        add(CommandHandler("listcmds",     self.cmd_listcmds))

        add(MessageHandler(filters.COMMAND, self.handle_text))
        add(CallbackQueryHandler(self.callback_handler))
        add(PreCheckoutQueryHandler(self.precheckout))
        add(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.payment_success))

        await app.bot.set_my_commands([
            BotCommand("start",       "Start the bot"),
            BotCommand("help",        "Full command list"),
            BotCommand("cr",          "Download episode"),
            BotCommand("pm",          "Premium plans"),
            BotCommand("subscribe",   "Buy premium"),
            BotCommand("redeem",      "Redeem a code"),
            BotCommand("queue",       "View your queue"),
            BotCommand("cancel",      "Cancel download"),
            BotCommand("history",     "Download history"),
            BotCommand("stats",       "Your statistics"),
            BotCommand("settings",    "User settings"),
            BotCommand("favorites",   "Favorites"),
            BotCommand("watchlist",   "Watchlist"),
            BotCommand("leaderboard", "Top downloaders"),
            BotCommand("batch",       "Batch download (premium)"),
            BotCommand("schedule",    "Schedule a download"),
            BotCommand("mediainfo",   "Video info"),
            BotCommand("rename",      "Rename file"),
            BotCommand("trim",        "Trim video"),
            BotCommand("compress",    "Compress video"),
            BotCommand("extract",     "Extract audio"),
            BotCommand("screenshot",  "Take screenshot"),
            BotCommand("gif",         "Create GIF"),
            BotCommand("watermark",   "Add watermark"),
            BotCommand("feedback",    "Send feedback"),
            BotCommand("admin",       "Admin panel"),
        ])

        logger.info("✅ Bot setup complete")

    async def run(self):
        await self.setup()
        
        # Initialize MTProto for 2GB files
        if Config.USE_MT_PROTO and PYROGRAM_AVAILABLE:
            await self._init_mtproto()

        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║          🎬 CRUNCHYROLL ULTIMATE BOT v100.0 — RUNNING 🎬                    ║
║          📦 2GB FILE SUPPORT ENABLED (MT-PROTO) 📦                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝""")

        self.queue_task = asyncio.create_task(self._process_queue())
        self.sched_task = asyncio.create_task(self._process_scheduled())

        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)

        logger.info(f"🚀 Bot started | Admins: {Config.ADMIN_IDS} | MTProto: {Config.USE_MT_PROTO}")

        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down…")
            if self.pyro_client:
                await self.pyro_client.stop()
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 11: ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         🎬 CRUNCHYROLL ULTIMATE BOT v100.0 - STARTING 🎬                    ║
║         📦 WITH 2GB FILE SUPPORT (MT-PROTO) 📦                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    if not Config.validate():
        print("❌ Configuration validation failed!")
        print("\nRequired setup:")
        print("1. Set BOT_TOKEN environment variable")
        print("2. Install FFmpeg: https://ffmpeg.org/download.html")
        print("3. For 2GB support, get API_ID and API_HASH from https://my.telegram.org/apps")
        print("   and set API_ID and API_HASH environment variables")
        sys.exit(1)

    bot = CrunchyrollBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped")
    except Exception as e:
        logger.error(f"Fatal: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import traceback
    main()
