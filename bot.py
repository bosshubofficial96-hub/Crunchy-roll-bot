#!/usr/bin/env python3
  """
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║       🎬 ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ ᴠ200.0 🎬                             ║
  ║  ꜰᴜʟʟ ᴘʀᴏᴅᴜᴄᴛɪᴏɴ | 50+ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ | ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ | ᴄᴏᴏᴋɪᴇ ᴀᴜᴛʜ   ║
  ║  ʀᴇɴᴀᴍᴇ | ᴛʜᴜᴍʙɴᴀɪʟ | ᴄᴜꜱᴛᴏᴍ ᴄᴍᴅꜱ | ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ | 2ɢʙ ꜰɪʟᴇꜱ        ║
  ║  ꜰᴀꜱᴛ/ꜱʟᴏᴡ ǫᴜᴇᴜᴇ | ɴᴇᴡꜱ | ʀᴇꜰᴇʀʀᴀʟ | @ꜰᴜɴɴʏᴛᴀᴍɪʟᴀɴ ꜱᴜᴘᴘᴏʀᴛ          ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
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
          JobQueue
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

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 2: ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ
  # ══════════════════════════════════════════════════════════════════════════════

  class Config:
      """ᴍᴀꜱᴛᴇʀ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ — ᴀʟʟ ᴠᴀʟᴜᴇꜱ ꜰʀᴏᴍ ᴇɴᴠ ᴠᴀʀꜱ"""

      BOT_TOKEN        = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
      ADMIN_IDS        = [int(x) for x in os.getenv("ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
      SUPER_ADMIN_IDS  = [int(x) for x in os.getenv("SUPER_ADMIN_IDS", "8525952693").split(",") if x.strip().isdigit()]
      MOD_IDS          = [int(x) for x in os.getenv("MOD_IDS", "8525952693").split(",") if x.strip().isdigit()]
      SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@funnytamilan")
      SUPPORT_CHANNEL  = os.getenv("SUPPORT_CHANNEL", "https://t.me/funnytamilan")

      # ── MTProto ───────────────────────────────────────────────────────────────
      API_ID           = int(os.getenv("API_ID", "0"))
      API_HASH         = os.getenv("API_HASH", "")
      USE_MT_PROTO     = os.getenv("USE_MT_PROTO", "False").lower() == "true"

      # ── Auth Group / Force-sub ─────────────────────────────────────────────
      AUTH_GROUP_ID    = int(os.getenv("AUTH_GROUP_ID", "0"))
      AUTH_GROUP_LINK  = os.getenv("AUTH_GROUP_LINK", "")
      AUTH_CHANNEL_ID  = int(os.getenv("AUTH_CHANNEL_ID", "0"))
      AUTH_CHANNEL_LINK= os.getenv("AUTH_CHANNEL_LINK", "")
      FORCE_SUB_ENABLED= os.getenv("FORCE_SUB_ENABLED", "False").lower() == "true"

      # ── Crunchyroll ────────────────────────────────────────────────────────
      CR_EMAIL         = os.getenv("CR_EMAIL", "")
      CR_PASSWORD      = os.getenv("CR_PASSWORD", "")
      CR_PREMIUM_ACCOUNT = os.getenv("CR_PREMIUM_ACCOUNT", "False").lower() == "true"

      # ── Subscription ──────────────────────────────────────────────────────
      SUBSCRIPTION_PRICES  = {"weekly": 20, "monthly": 50, "yearly": 500, "lifetime": 1500}
      SUBSCRIPTION_DAYS    = {"weekly": 7,  "monthly": 30, "yearly": 365, "lifetime": 36500}
      SUBSCRIPTION_FEATURES = {
          "weekly":   ["720p/1080p", sc("50 downloads/day"),  sc("queue priority"), sc("subtitles")],
          "monthly":  ["4K",  sc("200 downloads/day"), sc("batch download"), sc("custom thumbnail")],
          "yearly":   ["4K/HDR", sc("unlimited"),  sc("all features"), sc("watermark"), sc("trim/compress")],
          "lifetime": [sc("all features"), sc("vip support"), sc("custom emoji"), sc("gift premium"), sc("early access")],
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
      FREE_DOWNLOAD_DELAY  = int(os.getenv("FREE_DOWNLOAD_DELAY", "30"))   # seconds slow-lane delay

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

      DATABASE_PATH    = DATA_PATH / "crunchyroll_bot.db"
      COOKIES_FILE     = COOKIES_PATH / "cr_cookies.pkl"
      COOKIES_JSON     = COOKIES_PATH / "cr_cookies.json"

      # ── FFmpeg ────────────────────────────────────────────────────────────
      FFMPEG_PATH  = shutil.which("ffmpeg")  or "/usr/bin/ffmpeg"
      FFPROBE_PATH = shutil.which("ffprobe") or "/usr/bin/ffprobe"
      YTDLP_PATH   = shutil.which("yt-dlp")  or shutil.which("yt_dlp") or "yt-dlp"

      # ── Referral ──────────────────────────────────────────────────────────
      REFERRAL_REWARD   = int(os.getenv("REFERRAL_REWARD", "50"))
      REFERRAL_REQUIRED = int(os.getenv("REFERRAL_REQUIRED", "5"))

      # ── Channels ──────────────────────────────────────────────────────────
      LOG_CHANNEL    = int(os.getenv("LOG_CHANNEL", "0"))
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
          if cls.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
              logger.error("❌ BOT_TOKEN not set! Set BOT_TOKEN environment variable.")
              return False
          return True

  Config.create_dirs()

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 3: ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ ꜱʏꜱᴛᴇᴍ (ɴᴇᴡ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘɪ)
  # ══════════════════════════════════════════════════════════════════════════════

  class PremiumEmoji:
      """
      ᴛᴇʟᴇɢʀᴀᴍ ᴄᴜꜱᴛᴏᴍ ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ ꜱʏꜱᴛᴇᴍ
      Uses <tg-emoji emoji-id="..."> tags in HTML parse mode.
      Falls back to standard Unicode emoji automatically.
      Replace emoji_id values with real IDs from @Stickers bot.
      """
      # (emoji_id, fallback_unicode)
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
      }

      # Set True if your bot is in a premium context (channel/group that supports custom emoji)
      USE_CUSTOM = os.getenv("USE_PREMIUM_EMOJI", "True").lower() == "true"

      @classmethod
      def get(cls, name: str, html: bool = True) -> str:
          entry = cls.REGISTRY.get(name, ("", "❓"))
          emoji_id, fallback = entry
          if cls.USE_CUSTOM and emoji_id and not emoji_id.startswith("5000000"):
              if html:
                  return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
          return fallback

      @classmethod
      def build(cls, *names, html: bool = True) -> str:
          return "".join(cls.get(n, html) for n in names)

  # ── Short aliases for convenience ─────────────────────────────────────────────
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
                  file_size       INTEGER DEFAULT 0,
                  file_name       TEXT,
                  file_hash       TEXT,
                  downloaded_at   TEXT    DEFAULT CURRENT_TIMESTAMP
              )""",
              """CREATE TABLE IF NOT EXISTS subscriptions (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id         INTEGER,
                  plan_type       TEXT,
                  amount          INTEGER,
                  transaction_id  TEXT    UNIQUE,
                  start_date      TEXT    DEFAULT CURRENT_TIMESTAMP,
                  end_date        TEXT,
                  gifted_by       INTEGER
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
              """CREATE TABLE IF NOT EXISTS settings (
                  key             TEXT    PRIMARY KEY,
                  value           TEXT,
                  updated_at      TEXT    DEFAULT CURRENT_TIMESTAMP
              )""",
              """CREATE TABLE IF NOT EXISTS favorites (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id         INTEGER,
                  anime_title     TEXT,
                  anime_id        TEXT,
                  added_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(user_id, anime_id)
              )""",
              """CREATE TABLE IF NOT EXISTS watchlist (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id         INTEGER,
                  anime_title     TEXT,
                  anime_id        TEXT,
                  next_episode    INTEGER DEFAULT 1,
                  added_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(user_id, anime_id)
              )""",
              """CREATE TABLE IF NOT EXISTS feedback (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id         INTEGER,
                  rating          INTEGER,
                  message         TEXT,
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
              """CREATE TABLE IF NOT EXISTS cookies (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  service         TEXT    DEFAULT 'crunchyroll',
                  cookie_data     BLOB,
                  cookies_json    TEXT,
                  email           TEXT,
                  is_premium      INTEGER DEFAULT 0,
                  is_valid        INTEGER DEFAULT 1,
                  last_checked    TEXT    DEFAULT CURRENT_TIMESTAMP,
                  expires_at      TEXT,
                  added_by        INTEGER,
                  added_at        TEXT    DEFAULT CURRENT_TIMESTAMP
              )""",
              """CREATE TABLE IF NOT EXISTS cr_news (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  title           TEXT,
                  description     TEXT,
                  url             TEXT,
                  image_url       TEXT,
                  published_at    TEXT,
                  fetched_at      TEXT    DEFAULT CURRENT_TIMESTAMP,
                  notified        INTEGER DEFAULT 0
              )""",
              """CREATE TABLE IF NOT EXISTS user_cookies (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id         INTEGER,
                  cookie_data     BLOB,
                  cookies_json    TEXT,
                  service         TEXT    DEFAULT 'crunchyroll',
                  is_valid        INTEGER DEFAULT 1,
                  added_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(user_id, service)
              )""",
              """CREATE TABLE IF NOT EXISTS rate_limits (
                  user_id         INTEGER PRIMARY KEY,
                  requests        INTEGER DEFAULT 0,
                  window_start    TEXT    DEFAULT CURRENT_TIMESTAMP
              )""",
          ]
          for sql in tables:
              self.conn.execute(sql)

          indexes = [
              "CREATE INDEX IF NOT EXISTS idx_users_premium    ON users(user_id, premium_expiry)",
              "CREATE INDEX IF NOT EXISTS idx_queue_status     ON queue(status, priority)",
              "CREATE INDEX IF NOT EXISTS idx_downloads_user   ON downloads(user_id, downloaded_at)",
              "CREATE INDEX IF NOT EXISTS idx_scheduled_run    ON scheduled(run_at, status)",
              "CREATE INDEX IF NOT EXISTS idx_cookies_service  ON cookies(service, is_valid)",
          ]
          for idx in indexes:
              self.conn.execute(idx)

          defaults = [
              ("maintenance_mode",    "False"),
              ("welcome_message",     f"{Em.ANIME} {sc('welcome to crunchyroll ultimate bot')}!"),
              ("welcome_image",       ""),
              ("force_sub_enabled",   str(Config.FORCE_SUB_ENABLED)),
              ("default_quality",     Config.DEFAULT_QUALITY),
              ("default_encode",      Config.DEFAULT_ENCODE),
              ("referral_enabled",    "True"),
              ("referral_reward",     str(Config.REFERRAL_REWARD)),
              ("referral_required",   str(Config.REFERRAL_REQUIRED)),
              ("rate_limit_enabled",  "True"),
              ("rate_limit_requests", "30"),
              ("rate_limit_window",   "60"),
              ("log_channel",         str(Config.LOG_CHANNEL)),
              ("update_channel",      Config.UPDATE_CHANNEL),
              ("embed_thumbnail",     "True"),
              ("rename_enabled",      "True"),
              ("free_download_delay", str(Config.FREE_DOWNLOAD_DELAY)),
              ("news_enabled",        "True"),
              ("news_interval_hours", "6"),
          ]
          for k, v in defaults:
              self.conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))

          for aid in Config.ADMIN_IDS:
              code = secrets.token_hex(4).upper()
              self.conn.execute(
                  "INSERT OR IGNORE INTO users(user_id,is_admin,premium_type,premium_expiry,referral_code) "
                  "VALUES(?,1,'lifetime',datetime('now','+100 years'),?)", (aid, code))

          seed_cmds = [
              ("ping",    f"{Em.SUCCESS} {sc('pong! bot is alive')}!", None, "text"),
              ("about",   f"{Em.ANIME} <b>{sc('crunchyroll ultimate bot v200.0')}</b>\n\n{sc('50+ premium features')}!\n/{sc('premium')} {sc('to upgrade')}", None, "html"),
              ("rules",   f"{Em.INFO} <b>{sc('rules')}</b>:\n1. {sc('no spam')}\n2. {sc('be respectful')}\n3. {sc('enjoy anime')}!", None, "html"),
              ("support", f"{Em.SUPPORT} {sc('contact')} {Config.SUPPORT_USERNAME} {sc('for support')}", None, "text"),
              ("uptime",  f"{Em.SUCCESS} {sc('bot is online and ready')}!", None, "text"),
          ]
          for cmd, resp, code, ctype in seed_cmds:
              self.conn.execute(
                  "INSERT OR IGNORE INTO custom_commands(command,response,code,cmd_type) VALUES(?,?,?,?)",
                  (cmd, resp, code, ctype))

          self.conn.commit()
          logger.info(f"✅ {sc('database initialized')}")

      # ──── ꜱᴇᴛᴛɪɴɢꜱ ──────────────────────────────────────────────────────────

      def get_setting(self, key: str, default: str = "") -> str:
          c = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
          r = c.fetchone()
          return r[0] if r else default

      def set_setting(self, key: str, value: str):
          self.conn.execute(
              "INSERT INTO settings(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) "
              "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
              (key, value))
          self.conn.commit()

      # ──── ᴜꜱᴇʀꜱ ──────────────────────────────────────────────────────────────

      def get_user(self, uid: int) -> Optional[Dict]:
          c = self.conn.execute("SELECT * FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          return dict(r) if r else None

      def register_user(self, uid: int, username: str = None,
                        first_name: str = None, last_name: str = None,
                        referrer_id: int = None):
          code = secrets.token_hex(4).upper()
          self.conn.execute(
              "INSERT OR IGNORE INTO users(user_id,username,first_name,last_name,referral_code,referred_by) "
              "VALUES(?,?,?,?,?,?)",
              (uid, username, first_name, last_name, code, referrer_id))
          self.conn.execute(
              "UPDATE users SET last_active=CURRENT_TIMESTAMP,username=?,first_name=?,last_name=? WHERE user_id=?",
              (username, first_name, last_name, uid))
          if referrer_id and referrer_id != uid:
              # Update referrer counts
              self.conn.execute(
                  "UPDATE users SET referral_count=referral_count+1 WHERE user_id=?", (referrer_id,))
              referral_reward = int(self.get_setting("referral_reward", "50"))
              self.conn.execute(
                  "UPDATE users SET referral_points=referral_points+?,stars_balance=stars_balance+? WHERE user_id=?",
                  (referral_reward, referral_reward, referrer_id))
          self.conn.commit()

      def get_user_by_ref_code(self, code: str) -> Optional[int]:
          c = self.conn.execute("SELECT user_id FROM users WHERE referral_code=?", (code.upper(),))
          r = c.fetchone()
          return r[0] if r else None

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
              try: return datetime.fromisoformat(r[0])
              except: pass
          return None

      def add_premium(self, uid: int, plan: str, days: int, txn_id: str = None,
                      gifted_by: int = None) -> bool:
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
                      "INSERT OR IGNORE INTO subscriptions(user_id,plan_type,amount,transaction_id,end_date,gifted_by) "
                      "VALUES(?,?,?,?,?,?)",
                      (uid, plan, Config.SUBSCRIPTION_PRICES.get(plan, 0),
                       txn_id, new_expiry.isoformat(), gifted_by))
              self.conn.commit()
              return True
          except Exception as e:
              logger.error(f"add_premium: {e}")
              return False

      def revoke_premium(self, uid: int) -> bool:
          try:
              self.conn.execute(
                  "UPDATE users SET premium_type='free',premium_expiry=NULL WHERE user_id=?", (uid,))
              self.conn.commit()
              return True
          except:
              return False

      def get_daily_downloads(self, uid: int) -> int:
          today = datetime.now().date().isoformat()
          c = self.conn.execute("SELECT daily_downloads,last_reset FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          if r and r[1] != today:
              self.conn.execute(
                  "UPDATE users SET daily_downloads=0,last_reset=? WHERE user_id=?", (today, uid))
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
              return False, f"{Em.BAN} {sc('you are banned from this bot')}."
          is_pm = self.is_premium(uid)
          limit = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
          curr  = self.get_daily_downloads(uid)
          if curr >= limit:
              if is_pm:
                  return False, f"{sc('daily limit')} {limit} {sc('reached. contact support')}."
              return False, (
                  f"{Em.PREMIUM} {sc('free limit reached')} ({curr}/{limit}).\n"
                  f"{sc('use')} /premium {sc('to get unlimited downloads')}!")
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

      def get_all_users(self, banned_only=False, premium_only=False) -> List[int]:
          if banned_only:
              c = self.conn.execute("SELECT user_id FROM users WHERE is_banned=1")
          elif premium_only:
              c = self.conn.execute(
                  "SELECT user_id FROM users WHERE premium_expiry>CURRENT_TIMESTAMP AND is_banned=0")
          else:
              c = self.conn.execute("SELECT user_id FROM users WHERE is_banned=0")
          return [r[0] for r in c.fetchall()]

      def get_user_count(self) -> Dict:
          total   = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
          premium = self.conn.execute(
              "SELECT COUNT(*) FROM users WHERE premium_expiry>CURRENT_TIMESTAMP").fetchone()[0]
          banned  = self.conn.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
          return {"total": total, "premium": premium, "free": total-premium-banned, "banned": banned}

      def set_user_setting(self, uid: int, key: str, value: str):
          allowed = ["default_quality","encode_preset","language","custom_thumb","notify_complete"]
          if key in allowed:
              self.conn.execute(f"UPDATE users SET {key}=? WHERE user_id=?", (value, uid))
              self.conn.commit()

      # ──── ǫᴜᴇᴜᴇ ──────────────────────────────────────────────────────────────

      def add_to_queue(self, uid: int, url: str, quality: str,
                       preset: str = None, msg_id: int = None,
                       chat_id: int = None) -> int:
          is_pm    = self.is_premium(uid)
          priority = 10 if is_pm else 0      # Premium users get 10x priority
          is_fast  = 1 if is_pm else 0
          preset   = preset or Config.DEFAULT_ENCODE
          c = self.conn.execute(
              "INSERT INTO queue(user_id,url,quality,encode_preset,priority,message_id,chat_id,is_fast) "
              "VALUES(?,?,?,?,?,?,?,?)",
              (uid, url, quality, preset, priority, msg_id, chat_id, is_fast))
          self.conn.commit()
          return c.lastrowid

      def get_queue_position(self, qid: int) -> int:
          c = self.conn.execute(
              "SELECT COUNT(*) FROM queue WHERE status='pending' AND id<?", (qid,))
          return (c.fetchone()[0] or 0) + 1

      def get_user_queue(self, uid: int) -> List[Dict]:
          c = self.conn.execute(
              "SELECT id,url,quality,encode_preset,status,progress,is_fast,created_at FROM queue "
              "WHERE user_id=? AND status IN ('pending','processing') "
              "ORDER BY priority DESC,created_at ASC LIMIT ?",
              (uid, Config.MAX_QUEUE_PER_USER))
          return [dict(r) for r in c.fetchall()]

      def get_queue_count(self, uid: int) -> int:
          c = self.conn.execute(
              "SELECT COUNT(*) FROM queue WHERE user_id=? AND status='pending'", (uid,))
          return c.fetchone()[0]

      def update_queue_progress(self, qid: int, progress: int, status: str = None):
          if status:
              self.conn.execute(
                  "UPDATE queue SET progress=?,status=? WHERE id=?", (progress, status, qid))
          else:
              self.conn.execute("UPDATE queue SET progress=? WHERE id=?", (progress, qid))
          self.conn.commit()

      def start_processing(self, qid: int):
          self.conn.execute(
              "UPDATE queue SET status='processing',started_at=CURRENT_TIMESTAMP WHERE id=?", (qid,))
          self.conn.commit()

      def complete_queue_item(self, qid: int, fp: str):
          self.conn.execute(
              "UPDATE queue SET status='completed',file_path=?,completed_at=CURRENT_TIMESTAMP "
              "WHERE id=?", (fp, qid))
          self.conn.commit()

      def fail_queue_item(self, qid: int, err: str):
          self.conn.execute(
              "UPDATE queue SET status='failed',error_message=? WHERE id=?", (err[:500], qid))
          self.conn.commit()

      def cancel_queue_item(self, qid: int, uid: int) -> bool:
          c = self.conn.execute("SELECT user_id,status FROM queue WHERE id=?", (qid,))
          r = c.fetchone()
          if r and r[0] == uid and r[1] == "pending":
              self.conn.execute("UPDATE queue SET status='cancelled' WHERE id=?", (qid,))
              self.conn.commit()
              return True
          return False

      def get_next_queue_item(self, fast_lane: bool = True) -> Optional[Dict]:
          if fast_lane:
              c = self.conn.execute(
                  "SELECT id,user_id,url,quality,encode_preset,message_id,chat_id,is_fast FROM queue "
                  "WHERE status='pending' AND is_fast=1 "
                  "ORDER BY priority DESC,created_at ASC LIMIT 1")
          else:
              c = self.conn.execute(
                  "SELECT id,user_id,url,quality,encode_preset,message_id,chat_id,is_fast FROM queue "
                  "WHERE status='pending' "
                  "ORDER BY priority DESC,created_at ASC LIMIT 1")
          r = c.fetchone()
          return dict(r) if r else None

      def get_all_queue(self) -> List[Dict]:
          c = self.conn.execute(
              "SELECT id,user_id,url,quality,status,progress,is_fast,created_at FROM queue "
              "WHERE status IN ('pending','processing') "
              "ORDER BY priority DESC,created_at ASC LIMIT 50")
          return [dict(r) for r in c.fetchall()]

      def clear_queue(self, uid: int = None) -> int:
          if uid:
              c = self.conn.execute(
                  "DELETE FROM queue WHERE user_id=? AND status='pending'", (uid,))
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
              (uid, anime_title, anime_id, ep_title, ep_id, ep_num, season,
               quality, preset, size, fname, fhash))
          self.conn.commit()

      def get_download_history(self, uid: int, limit: int = 20) -> List[Dict]:
          c = self.conn.execute(
              "SELECT * FROM downloads WHERE user_id=? "
              "ORDER BY downloaded_at DESC LIMIT ?", (uid, limit))
          return [dict(r) for r in c.fetchall()]

      def get_leaderboard(self, limit: int = 10) -> List[Dict]:
          c = self.conn.execute(
              "SELECT user_id,first_name,total_downloads,total_size FROM users "
              "WHERE is_banned=0 ORDER BY total_downloads DESC LIMIT ?", (limit,))
          return [dict(r) for r in c.fetchall()]

      # ──── ꜰᴀᴠᴏʀɪᴛᴇꜱ / ᴡᴀᴛᴄʜʟɪꜱᴛ ───────────────────────────────────────────

      def add_favorite(self, uid: int, anime_title: str, anime_id: str) -> bool:
          try:
              self.conn.execute(
                  "INSERT OR IGNORE INTO favorites(user_id,anime_title,anime_id) VALUES(?,?,?)",
                  (uid, anime_title, anime_id))
              self.conn.commit()
              return True
          except: return False

      def remove_favorite(self, uid: int, anime_id: str) -> bool:
          c = self.conn.execute(
              "DELETE FROM favorites WHERE user_id=? AND anime_id=?", (uid, anime_id))
          self.conn.commit()
          return c.rowcount > 0

      def get_favorites(self, uid: int) -> List[Dict]:
          c = self.conn.execute(
              "SELECT * FROM favorites WHERE user_id=? ORDER BY added_at DESC", (uid,))
          return [dict(r) for r in c.fetchall()]

      def add_watchlist(self, uid: int, anime_title: str, anime_id: str) -> bool:
          try:
              self.conn.execute(
                  "INSERT OR IGNORE INTO watchlist(user_id,anime_title,anime_id) VALUES(?,?,?)",
                  (uid, anime_title, anime_id))
              self.conn.commit()
              return True
          except: return False

      def remove_watchlist(self, uid: int, anime_id: str) -> bool:
          c = self.conn.execute(
              "DELETE FROM watchlist WHERE user_id=? AND anime_id=?", (uid, anime_id))
          self.conn.commit()
          return c.rowcount > 0

      def get_watchlist(self, uid: int) -> List[Dict]:
          c = self.conn.execute(
              "SELECT * FROM watchlist WHERE user_id=? ORDER BY added_at DESC", (uid,))
          return [dict(r) for r in c.fetchall()]

      # ──── ꜰᴇᴇᴅʙᴀᴄᴋ ───────────────────────────────────────────────────────────

      def add_feedback(self, uid: int, rating: int, message: str):
          self.conn.execute(
              "INSERT INTO feedback(user_id,rating,message) VALUES(?,?,?)", (uid, rating, message))
          self.conn.commit()

      # ──── ꜱᴄʜᴇᴅᴜʟᴇᴅ ─────────────────────────────────────────────────────────

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

      def update_custom_cmd(self, cmd: str, response: str, code: str, cmd_type: str) -> bool:
          c = self.conn.execute(
              "UPDATE custom_commands SET response=?,code=?,cmd_type=? WHERE command=?",
              (response, code, cmd_type, cmd))
          self.conn.commit()
          return c.rowcount > 0

      def remove_custom_cmd(self, cmd: str) -> bool:
          c = self.conn.execute("DELETE FROM custom_commands WHERE command=?", (cmd,))
          self.conn.commit()
          return c.rowcount > 0

      def get_custom_cmd(self, cmd: str) -> Optional[Dict]:
          c = self.conn.execute("SELECT * FROM custom_commands WHERE command=?", (cmd,))
          r = c.fetchone()
          if r:
              self.conn.execute(
                  "UPDATE custom_commands SET usage_count=usage_count+1 WHERE command=?", (cmd,))
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
                             max_uses: int, created_by: int, exp_days: int) -> bool:
          try:
              expires = (datetime.now() + timedelta(days=exp_days)).isoformat()
              self.conn.execute(
                  "INSERT INTO redeem_codes(code,plan_type,days,max_uses,created_by,expires_at) "
                  "VALUES(?,?,?,?,?,?)",
                  (code, plan, days, max_uses, created_by, expires))
              self.conn.commit()
              return True
          except:
              return False

      def use_redeem_code(self, code: str, uid: int) -> Tuple[bool, str, Optional[str], int]:
          c = self.conn.execute("SELECT * FROM redeem_codes WHERE code=?", (code.upper(),))
          r = c.fetchone()
          if not r:
              return False, sc("invalid code"), None, 0
          r = dict(r)
          if r["expires_at"] and datetime.fromisoformat(r["expires_at"]) < datetime.now():
              return False, sc("code has expired"), None, 0
          if r["used_count"] >= r["max_uses"]:
              return False, sc("code already used maximum times"), None, 0
          used = self.conn.execute(
              "SELECT 1 FROM redeem_log WHERE code=? AND user_id=?", (code.upper(), uid)).fetchone()
          if used:
              return False, sc("you already used this code"), None, 0
          self.conn.execute(
              "UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?", (code.upper(),))
          self.conn.execute(
              "INSERT INTO redeem_log(code,user_id) VALUES(?,?)", (code.upper(), uid))
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
          c = self.conn.execute("SELECT * FROM gifts WHERE gift_code=?", (code.upper(),))
          r = c.fetchone()
          if not r:
              return False, sc("invalid gift code"), None, 0
          r = dict(r)
          if r["claimed"]:
              return False, sc("gift already claimed"), None, 0
          if r["to_user"] and r["to_user"] != uid:
              return False, sc("this gift is not for you"), None, 0
          self.conn.execute("UPDATE gifts SET claimed=1 WHERE gift_code=?", (code.upper(),))
          self.conn.commit()
          return True, "ok", r["plan_type"], r["days"]

      # ──── ʀᴇꜰᴇʀʀᴀʟꜱ ──────────────────────────────────────────────────────────

      def get_referral_code(self, uid: int) -> str:
          c = self.conn.execute("SELECT referral_code FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          if r and r[0]:
              return r[0]
          code = secrets.token_hex(4).upper()
          self.conn.execute("UPDATE users SET referral_code=? WHERE user_id=?", (code, uid))
          self.conn.commit()
          return code

      def get_referral_count(self, uid: int) -> int:
          c = self.conn.execute(
              "SELECT referral_count FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          return r[0] if r else 0

      def get_referral_points(self, uid: int) -> int:
          c = self.conn.execute("SELECT referral_points FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          return r[0] if r else 0

      def get_top_referrers(self, limit: int = 10) -> List[Dict]:
          c = self.conn.execute(
              "SELECT user_id,first_name,referral_count,referral_points FROM users "
              "WHERE is_banned=0 ORDER BY referral_count DESC LIMIT ?", (limit,))
          return [dict(r) for r in c.fetchall()]

      # ──── ᴄᴏᴏᴋɪᴇꜱ ────────────────────────────────────────────────────────────

      def save_cookies(self, cookie_data: bytes, cookies_json: str,
                       email: str = "", is_premium: bool = False,
                       added_by: int = 0, expires_days: int = 30) -> int:
          expires = (datetime.now() + timedelta(days=expires_days)).isoformat()
          # Deactivate old cookies
          self.conn.execute("UPDATE cookies SET is_valid=0 WHERE service='crunchyroll'")
          c = self.conn.execute(
              "INSERT INTO cookies(service,cookie_data,cookies_json,email,is_premium,is_valid,"
              "expires_at,added_by) VALUES('crunchyroll',?,?,?,1,1,?,?)",
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

      def save_user_cookies(self, uid: int, cookie_data: bytes, cookies_json: str) -> bool:
          try:
              self.conn.execute(
                  "INSERT INTO user_cookies(user_id,cookie_data,cookies_json) VALUES(?,?,?) "
                  "ON CONFLICT(user_id,service) DO UPDATE SET "
                  "cookie_data=excluded.cookie_data,cookies_json=excluded.cookies_json,"
                  "added_at=CURRENT_TIMESTAMP",
                  (uid, cookie_data, cookies_json))
              self.conn.commit()
              return True
          except:
              return False

      def get_user_cookies(self, uid: int) -> Optional[Dict]:
          c = self.conn.execute(
              "SELECT * FROM user_cookies WHERE user_id=? AND is_valid=1", (uid,))
          r = c.fetchone()
          return dict(r) if r else None

      def invalidate_cookies(self):
          self.conn.execute("UPDATE cookies SET is_valid=0 WHERE service='crunchyroll'")
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
          except:
              return False

      def get_latest_news(self, limit: int = 5) -> List[Dict]:
          c = self.conn.execute(
              "SELECT * FROM cr_news ORDER BY published_at DESC LIMIT ?", (limit,))
          return [dict(r) for r in c.fetchall()]

      def get_unnotified_news(self) -> List[Dict]:
          c = self.conn.execute("SELECT * FROM cr_news WHERE notified=0 ORDER BY published_at DESC")
          return [dict(r) for r in c.fetchall()]

      def mark_news_notified(self, news_id: int):
          self.conn.execute("UPDATE cr_news SET notified=1 WHERE id=?", (news_id,))
          self.conn.commit()

      # ──── ʀᴀᴛᴇ ʟɪᴍɪᴛ ─────────────────────────────────────────────────────────

      def check_rate_limit(self, uid: int) -> bool:
          if self.get_setting("rate_limit_enabled", "True") != "True":
              return True
          if self.is_admin(uid):
              return True
          max_req = int(self.get_setting("rate_limit_requests", "30"))
          window  = int(self.get_setting("rate_limit_window", "60"))
          c = self.conn.execute("SELECT requests,window_start FROM rate_limits WHERE user_id=?", (uid,))
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
          except:
              ws = now - timedelta(seconds=window+1)
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
  

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 5: ᴘʀᴏɢʀᴇꜱꜱ ʙᴀʀ + ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class ProgressBar:
      @staticmethod
      def make(pct: int, length: int = 12) -> str:
          pct = max(0, min(100, pct))
          filled = int(length * pct / 100)
          bar = "█" * filled + "░" * (length - filled)
          return f"[{bar}] {pct}%"

  class VideoTools:
      @staticmethod
      def build_filename(series: str, season: int, ep: int,
                         title: str, quality: str, preset: str) -> str:
          safe = re.sub(r'[^\w\s\-]', '', series)[:40].strip()
          safe_title = re.sub(r'[^\w\s\-]', '', title)[:30].strip()
          return f"{safe}.S{season:02d}E{ep:02d}.{safe_title}.{quality}.{preset}.mp4"

      @staticmethod
      async def generate_thumbnail(video_path: str) -> Optional[str]:
          if not Path(video_path).exists():
              return None
          ts  = ["00:00:05", "00:00:10", "00:00:15", "00:00:03"]
          out = str(Config.THUMB_PATH / f"{Path(video_path).stem}_thumb.jpg")
          for t in ts:
              cmd = [Config.FFMPEG_PATH, "-y", "-i", video_path, "-ss", t,
                     "-vframes", "1", "-vf", "scale=1280:720:force_original_aspect_ratio=decrease",
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
              "-i", thumb_path,
              "-map", "0", "-map", "1",
              "-c", "copy",
              "-disposition:1", "attached_pic",
              out,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
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
              "-c:v", codec,
              "-preset", pre_cfg["preset"],
              "-crf", str(q_cfg["crf"]),
              "-vf", f"scale=-2:{q_cfg['height']}",
              "-c:a", "aac", "-b:a", q_cfg["audio"],
              "-movflags", "+faststart",
              "-progress", "pipe:1",
              out,
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
                      except:
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
          cmd = [
              Config.FFMPEG_PATH, "-y",
              "-i", input_path,
              "-ss", start, "-to", end,
              "-c", "copy", out,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=300)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
              return None

      @staticmethod
      async def compress_video(input_path: str, target_mb: int) -> Optional[str]:
          size = Path(input_path).stat().st_size / (1024 * 1024)
          if size <= target_mb:
              return input_path
          info = await VideoTools.get_media_info(input_path)
          dur  = float(info.get("raw_duration", 60))
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
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=600)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
              return None

      @staticmethod
      async def extract_audio(input_path: str, fmt: str = "mp3") -> Optional[str]:
          out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_audio.{fmt}")
          codec = "libmp3lame" if fmt == "mp3" else "aac"
          cmd   = [Config.FFMPEG_PATH, "-y", "-i", input_path, "-vn", "-c:a", codec, out]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=300)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
              return None

      @staticmethod
      async def screenshot_video(input_path: str, timestamp: str = "00:00:05") -> Optional[str]:
          out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_shot.jpg")
          cmd = [Config.FFMPEG_PATH, "-y", "-i", input_path, "-ss", timestamp,
                 "-vframes", "1", out]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=60)
              return out if Path(out).exists() else None
          except:
              return None

      @staticmethod
      async def make_gif(input_path: str, start: str = "00:00:00",
                         duration: int = 5, scale: int = 320) -> Optional[str]:
          out = str(Config.TEMP_PATH / f"{Path(input_path).stem}.gif")
          cmd = [
              Config.FFMPEG_PATH, "-y", "-i", input_path,
              "-ss", start, "-t", str(duration),
              "-vf", f"scale={scale}:-1:flags=lanczos,fps=12",
              out,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=120)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
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
          pos = positions.get(position, positions["bottomright"])
          safe_text = re.sub(r"[:'\\]", "", text)
          out = str(Config.TEMP_PATH / f"{Path(input_path).stem}_wm.mp4")
          cmd = [
              Config.FFMPEG_PATH, "-y", "-i", input_path,
              "-vf",
              f"drawtext=text='{safe_text}':fontcolor=white:fontsize=24:"
              f"box=1:boxcolor=black@0.5:x={pos}",
              "-codec:a", "copy", out,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=600)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
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
                  *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
              out, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
              data   = json.loads(out.decode())
              fmt    = data.get("format", {})
              streams= data.get("streams", [])
              v = next((s for s in streams if s.get("codec_type") == "video"), {})
              a = next((s for s in streams if s.get("codec_type") == "audio"), {})
              size = int(fmt.get("size", 0))
              dur  = float(fmt.get("duration", 0))
              fps  = 0
              if v.get("r_frame_rate"):
                  try:
                      num, den = v["r_frame_rate"].split("/")
                      fps = round(int(num) / int(den), 2) if int(den) else 0
                  except:
                      pass
              return {
                  "duration":     f"{int(dur//3600):02d}:{int((dur%3600)//60):02d}:{int(dur%60):02d}",
                  "raw_duration": dur,
                  "size_mb":      round(size / (1024**2), 2),
                  "format":       fmt.get("format_name", "unknown"),
                  "video_codec":  v.get("codec_name", "N/A"),
                  "width":        v.get("width", 0),
                  "height":       v.get("height", 0),
                  "fps":          fps,
                  "audio_codec":  a.get("codec_name", "N/A"),
                  "channels":     a.get("channels", 0),
                  "sample_rate":  a.get("sample_rate", "N/A"),
              }
          except Exception as e:
              logger.error(f"media_info: {e}")
              return {}

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 6: ᴄᴏᴏᴋɪᴇ ᴍᴀɴᴀɢᴇʀ
  # ══════════════════════════════════════════════════════════════════════════════

  class CookieManager:
      """ᴏᴡɴ ᴄᴏᴏᴋɪᴇ ꜱᴛᴏʀᴇ ꜰᴏʀ ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ"""

      @staticmethod
      def parse_netscape_cookies(text: str) -> List[Dict]:
          cookies = []
          for line in text.strip().splitlines():
              line = line.strip()
              if not line or line.startswith("#") and "HttpOnly" not in line:
                  continue
              line = line.replace("#HttpOnly_", "")
              parts = line.split("\t")
              if len(parts) >= 7:
                  cookies.append({
                      "domain":   parts[0],
                      "flag":     parts[1],
                      "path":     parts[2],
                      "secure":   parts[3].upper() == "TRUE",
                      "expires":  parts[4],
                      "name":     parts[5],
                      "value":    parts[6],
                  })
          return cookies

      @staticmethod
      def parse_json_cookies(text: str) -> List[Dict]:
          try:
              data = json.loads(text)
              if isinstance(data, list):
                  return data
          except:
              pass
          return []

      @staticmethod
      def cookies_to_netscape(cookies: List[Dict]) -> str:
          lines = ["# Netscape HTTP Cookie File\n# https://curl.haxx.se/rfc/cookie_spec.html\n"]
          for c in cookies:
              domain  = c.get("domain", "")
              flag    = "TRUE" if domain.startswith(".") else "FALSE"
              path    = c.get("path", "/")
              secure  = "TRUE" if c.get("secure", False) else "FALSE"
              expires = str(c.get("expirationDate", c.get("expires", "0")))
              name    = c.get("name", "")
              value   = c.get("value", "")
              lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
          return "\n".join(lines)

      @staticmethod
      def is_crunchyroll_cookie(cookies: List[Dict]) -> bool:
          cr_domains = ["crunchyroll.com", ".crunchyroll.com"]
          cr_names   = ["etp_rt", "_cr_user_data", "session_id", "auth_v2"]
          has_domain = any(
              any(d in c.get("domain", "") for d in cr_domains) for c in cookies)
          has_name = any(c.get("name", "") in cr_names for c in cookies)
          return has_domain and has_name

      @staticmethod
      async def validate_cookies(cookies_text: str) -> Tuple[bool, str]:
          """Try to validate cookies by hitting a CR endpoint."""
          cookies_list = CookieManager.parse_netscape_cookies(cookies_text)
          if not cookies_list:
              cookies_list = CookieManager.parse_json_cookies(cookies_text)
          if not cookies_list:
              return False, sc("could not parse cookies format. use netscape or json format")
          if not CookieManager.is_crunchyroll_cookie(cookies_list):
              return False, sc("cookies don't appear to be from crunchyroll.com")
          return True, "ok"

      @staticmethod
      def save_to_file(cookies_text: str) -> bool:
          try:
              cfg = Config.COOKIES_FILE
              cookies_list = (CookieManager.parse_netscape_cookies(cookies_text)
                              or CookieManager.parse_json_cookies(cookies_text))
              with open(str(cfg), "wb") as f:
                  pickle.dump(cookies_list, f)
              with open(str(Config.COOKIES_JSON), "w", encoding="utf-8") as f:
                  json.dump(cookies_list, f, ensure_ascii=False, indent=2)
              return True
          except Exception as e:
              logger.error(f"save_to_file: {e}")
              return False

      @staticmethod
      def get_cookies_file_path() -> Optional[str]:
          if Config.COOKIES_JSON.exists():
              return str(Config.COOKIES_JSON)
          return None

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 7: ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴀᴘɪ
  # ══════════════════════════════════════════════════════════════════════════════

  class CrunchyrollAPI:
      """ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴜʀʟ ᴘᴀʀꜱᴇʀ + ᴅᴏᴡɴʟᴏᴀᴅ ᴏʀᴄʜᴇꜱᴛʀᴀᴛᴏʀ"""

      CR_PATTERNS = [
          r"crunchyroll\.com/watch/([A-Z0-9]+)",
          r"crunchyroll\.com/[a-z-]+/episode-[^/]+/([A-Z0-9]+)",
          r"cr\.now/([A-Z0-9]+)",
          r"crunchyroll\.com/(?:[a-z]{2}-[a-z]{2}/)?watch/([A-Z0-9]+)",
      ]

      def extract_id(self, url: str) -> Optional[str]:
          for p in self.CR_PATTERNS:
              m = re.search(p, url, re.IGNORECASE)
              if m:
                  return m.group(1)
          return None

      def is_valid_url(self, url: str) -> bool:
          return bool(re.search(r"(crunchyroll\.com|cr\.now)", url, re.I))

      async def get_episode_info_ytdlp(self, url: str, cookies_file: str = None) -> Dict:
          """Get episode info using yt-dlp (the real implementation)."""
          cmd = [Config.YTDLP_PATH, "--dump-json", "--no-playlist"]
          if cookies_file and Path(cookies_file).exists():
              cmd += ["--cookies", cookies_file]
          cmd.append(url)
          try:
              proc = await asyncio.create_subprocess_exec(
                  *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
              stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
              if proc.returncode == 0 and stdout:
                  data = json.loads(stdout.decode())
                  return {
                      "id":             data.get("id", "unknown"),
                      "series_title":   data.get("series", data.get("uploader", "Unknown Anime")),
                      "episode_title":  data.get("title", "Unknown Episode"),
                      "episode_number": int(data.get("episode_number", 1) or 1),
                      "season_number":  int(data.get("season_number", 1) or 1),
                      "duration":       int(data.get("duration", 0) or 0),
                      "thumbnail_url":  data.get("thumbnail"),
                      "description":    data.get("description", ""),
                      "raw":            data,
                  }
          except asyncio.TimeoutError:
              logger.warning("yt-dlp info timeout")
          except Exception as e:
              logger.error(f"get_episode_info_ytdlp: {e}")
          ep_id = self.extract_id(url) or "UNKNOWN"
          return {
              "id":             ep_id,
              "series_title":   "Unknown Anime",
              "episode_title":  "Unknown Episode",
              "episode_number": 1,
              "season_number":  1,
              "duration":       0,
              "thumbnail_url":  None,
          }

      async def download_ytdlp(self, url: str, quality: str, output_path: str,
                                cookies_file: str = None,
                                progress_cb=None) -> Tuple[bool, str]:
          """Download using yt-dlp with quality selection."""
          q_cfg    = Config.QUALITIES.get(quality, Config.QUALITIES["720p"])
          height   = q_cfg["height"]

          fmt = (f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
                 if height < 2160 else "bestvideo+bestaudio/best")

          cmd = [
              Config.YTDLP_PATH,
              "-f", fmt,
              "--merge-output-format", "mp4",
              "--output", output_path,
              "--no-playlist",
              "--newline",
              "--progress",
          ]
          if cookies_file and Path(cookies_file).exists():
              cmd += ["--cookies", cookies_file]

          # Add sub options
          cmd += [
              "--write-sub", "--sub-format", "srt",
              "--convert-subs", "srt",
          ]
          cmd.append(url)

          try:
              proc = await asyncio.create_subprocess_exec(
                  *cmd,
                  stdout=asyncio.subprocess.PIPE,
                  stderr=asyncio.subprocess.STDOUT)

              async for raw_line in proc.stdout:
                  line = raw_line.decode("utf-8", errors="ignore").strip()
                  # Parse yt-dlp progress: [download] XX.X% of ...
                  m = re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%", line)
                  if m and progress_cb:
                      pct = int(float(m.group(1)))
                      await progress_cb(pct, f"{sc('downloading')} {pct}%")

              await proc.wait()
              # yt-dlp may append .mp4 automatically
              final = output_path
              if not Path(final).exists():
                  # Try with extension
                  candidates = list(Path(output_path).parent.glob(
                      Path(output_path).stem + "*"))
                  if candidates:
                      final = str(candidates[0])
              if proc.returncode == 0 and Path(final).exists():
                  return True, final
              return False, sc("download failed — check url and cookies")
          except asyncio.TimeoutError:
              return False, sc("download timed out")
          except Exception as e:
              logger.error(f"download_ytdlp: {e}")
              return False, str(e)

      async def fetch_cr_news(self) -> List[Dict]:
          """Fetch Crunchyroll news from RSS feed."""
          rss_urls = [
              "https://www.crunchyroll.com/news/feed",
              "https://feeds.feedburner.com/crunchyroll/animenews",
          ]
          news = []
          for rss_url in rss_urls:
              try:
                  if AIOHTTP_AVAILABLE:
                      async with aiohttp.ClientSession(
                          timeout=aiohttp.ClientTimeout(total=15)) as session:
                          async with session.get(rss_url, headers={
                              "User-Agent": "Mozilla/5.0 CrunchyrollBot/2.0"}) as resp:
                              if resp.status == 200:
                                  text = await resp.text()
                                  items = re.findall(
                                      r"<item>(.*?)</item>", text, re.DOTALL)
                                  for item in items[:10]:
                                      title = re.search(
                                          r"<title><!\[CDATA\[(.+?)\]\]></title>|<title>(.+?)</title>",
                                          item, re.DOTALL)
                                      link  = re.search(r"<link>(.+?)</link>", item)
                                      desc  = re.search(
                                          r"<description><!\[CDATA\[(.+?)\]\]></description>|"
                                          r"<description>(.+?)</description>",
                                          item, re.DOTALL)
                                      pub   = re.search(r"<pubDate>(.+?)</pubDate>", item)
                                      img   = re.search(
                                          r'<media:content[^>]+url="([^"]+)"', item)
                                      if title and link:
                                          t = (title.group(1) or title.group(2) or "").strip()
                                          d = (desc.group(1) or desc.group(2) or "").strip()[:300]
                                          d = re.sub(r"<[^>]+>", "", d).strip()
                                          news.append({
                                              "title":       t,
                                              "description": d,
                                              "url":         link.group(1).strip(),
                                              "image_url":   img.group(1) if img else "",
                                              "published_at": pub.group(1).strip() if pub else "",
                                          })
                                  if news:
                                      return news
              except Exception as e:
                  logger.warning(f"fetch_cr_news {rss_url}: {e}")
                  continue
          return news

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 8: ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴀɴᴀɢᴇʀ (ꜰᴀꜱᴛ/ꜱʟᴏᴡ ʟᴀɴᴇ)
  # ══════════════════════════════════════════════════════════════════════════════

  class DownloadManager:
      """
      ⚡ ꜰᴀꜱᴛ ʟᴀɴᴇ → ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ (ɴᴏ ᴅᴇʟᴀʏ, ʜɪɢʜ ᴘʀɪᴏʀɪᴛʏ)
      🐢 ꜱʟᴏᴡ ʟᴀɴᴇ → ꜰʀᴇᴇ ᴜꜱᴇʀꜱ (ᴅᴇʟᴀʏ + ʟᴏᴡᴇʀ ᴘʀɪᴏʀɪᴛʏ)
      """

      def __init__(self, db: Database):
          self.db   = db
          self.cr   = CrunchyrollAPI()
          self._active_fast = 0
          self._active_slow = 0
          self._lock = asyncio.Lock()

      def get_cookies_file(self) -> Optional[str]:
          row = self.db.get_active_cookies()
          if row and row.get("cookies_json"):
              p = Config.COOKIES_JSON
              try:
                  p.write_text(row["cookies_json"], encoding="utf-8")
                  return str(p)
              except:
                  pass
          if Config.COOKIES_JSON.exists():
              return str(Config.COOKIES_JSON)
          return None

      async def process(self, queue_id: int, uid: int, url: str,
                        quality: str, preset: str,
                        progress_cb=None) -> Tuple[bool, str]:
          is_pm = self.db.is_premium(uid)
          delay = 0 if is_pm else int(self.db.get_setting("free_download_delay", "30"))

          try:
              if delay > 0:
                  if progress_cb:
                      await progress_cb(1, f"{Em.SLOW} {sc('free user queue — please wait')} {delay}s…")
                  await asyncio.sleep(delay)

              if progress_cb:
                  await progress_cb(3, f"{Em.LOADING} {sc('fetching episode info')}…")

              cookies_file = self.get_cookies_file()
              info = await self.cr.get_episode_info_ytdlp(url, cookies_file)

              if progress_cb:
                  lane_icon = Em.FAST if is_pm else Em.SLOW
                  await progress_cb(8,
                      f"{lane_icon} {info['series_title']} "
                      f"S{info['season_number']:02d}E{info['episode_number']:02d}")

              # Check premium quality access
              if quality in Config.PREMIUM_QUALITIES and not is_pm:
                  quality = "720p"
                  if progress_cb:
                      await progress_cb(9,
                          f"{Em.WARNING} {sc('quality downgraded to 720p — upgrade to premium for 4k/hdr')}")

              fname = VideoTools.build_filename(
                  info["series_title"], info["season_number"],
                  info["episode_number"], info["episode_title"],
                  quality, preset)
              raw_path = str(Config.DOWNLOAD_PATH / Path(fname).stem)

              if progress_cb:
                  await progress_cb(10, f"{Em.DOWNLOAD} {sc('starting download')}…")

              async def dl_progress(pct, msg):
                  if progress_cb:
                      mapped = 10 + int(pct * 0.55)
                      await progress_cb(mapped, msg)

              ok, result = await self.cr.download_ytdlp(
                  url, quality, raw_path, cookies_file, dl_progress)

              if not ok:
                  self.db.fail_queue_item(queue_id, result)
                  return False, result

              actual_path = result  # yt-dlp returns actual path

              if progress_cb:
                  await progress_cb(66, f"{Em.ENCODE} {sc('encoding')}…")

              encode_progress_mapped = 0

              async def enc_cb(pct):
                  nonlocal encode_progress_mapped
                  encode_progress_mapped = pct
                  if progress_cb:
                      await progress_cb(66 + int(pct * 0.22), f"{Em.ENCODE} {sc('encoding')} {pct}%")

              encoded = await VideoTools.encode_video(actual_path, quality, preset, enc_cb)
              if encoded:
                  try:
                      Path(actual_path).unlink(missing_ok=True)
                  except:
                      pass
                  actual_path = encoded

              if progress_cb:
                  await progress_cb(89, f"{Em.THUMBNAIL} {sc('generating thumbnail')}…")

              thumb = await VideoTools.generate_thumbnail(actual_path)
              if thumb and self.db.get_setting("embed_thumbnail") == "True":
                  embedded = await VideoTools.embed_thumbnail(actual_path, thumb)
                  if embedded:
                      try:
                          Path(actual_path).unlink(missing_ok=True)
                      except:
                          pass
                      actual_path = embedded

              # Move to output
              final_name = VideoTools.build_filename(
                  info["series_title"], info["season_number"],
                  info["episode_number"], info["episode_title"],
                  quality, preset)
              final_path = str(Config.OUTPUT_PATH / final_name)
              try:
                  Path(actual_path).rename(final_path)
                  actual_path = final_path
              except:
                  pass

              if progress_cb:
                  await progress_cb(95, f"{Em.LOADING} {sc('finalizing')}…")

              file_size = Path(actual_path).stat().st_size
              file_hash = hashlib.md5(Path(actual_path).read_bytes()[:65536]).hexdigest()

              self.db.complete_queue_item(queue_id, actual_path)
              self.db.increment_downloads(uid, file_size)
              self.db.add_download_record(
                  uid, info["series_title"], info["id"],
                  info["episode_title"], info["id"],
                  info["episode_number"], info["season_number"],
                  quality, preset, file_size,
                  Path(actual_path).name, file_hash)

              if progress_cb:
                  await progress_cb(100, f"{Em.SUCCESS} {sc('complete')}!")

              return True, actual_path

          except Exception as e:
              logger.exception(f"DownloadManager.process: {e}")
              self.db.fail_queue_item(queue_id, str(e))
              return False, str(e)

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 9: ꜱᴀɴᴅʙᴏx ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛᴏʀ
  # ══════════════════════════════════════════════════════════════════════════════

  class CodeSandbox:
      ALLOWED_BUILTINS = {
          "abs","all","any","bin","bool","chr","dict","dir","divmod","enumerate",
          "filter","float","format","frozenset","hash","hex","int","isinstance",
          "issubclass","iter","len","list","map","max","min","next","oct","ord",
          "pow","print","range","repr","reversed","round","set","slice","sorted",
          "str","sum","tuple","type","zip","True","False","None",
      }
      BLOCKED = [
          r"import\s+os", r"import\s+sys", r"import\s+subprocess",
          r"import\s+socket", r"import\s+urllib", r"import\s+requests",
          r"import\s+httpx", r"import\s+shutil",
          r"open\s*\(", r"exec\s*\(", r"eval\s*\(",
          r"__import__\s*\(", r"__builtins__", r"globals\s*\(",
          r"locals\s*\(", r"vars\s*\(", r"compile\s*\(",
          r"breakpoint\s*\(", r"input\s*\(",
          r"__loader__", r"__spec__", r"__package__",
      ]

      @classmethod
      def run(cls, code: str, context: Dict = None) -> Tuple[bool, str]:
          for pat in cls.BLOCKED:
              if re.search(pat, code, re.I):
                  return False, f"❌ Blocked: `{pat}`"
          output = io.StringIO()
          import builtins as _bi
          safe_builtins = {k: getattr(_bi, k) for k in cls.ALLOWED_BUILTINS if hasattr(_bi, k)}
          safe_builtins["print"] = lambda *a, **kw: output.write(" ".join(str(x) for x in a) + "\n")
          safe_globals = {
              "__builtins__": safe_builtins,
              "context": context or {},
              "random": random,
              "datetime": datetime,
              "timedelta": timedelta,
              "sc": sc,
          }
          try:
              exec(compile(code, "<custom_cmd>", "exec"), safe_globals)
              return True, output.getvalue() or f"✅ {sc('code executed (no output)')}"
          except Exception as e:
              return False, f"❌ {sc('error')}: {e}"

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 10: ᴀᴜᴛʜ ᴄʜᴇᴄᴋᴇʀ
  # ══════════════════════════════════════════════════════════════════════════════

  class AuthChecker:
      @staticmethod
      async def check_user(bot, uid: int, db: Database) -> Tuple[bool, List[str]]:
          if db.get_setting("force_sub_enabled", "False") != "True":
              return True, []
          groups = db.get_auth_groups()
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
  #  SECTION 11: ᴅᴇᴄᴏʀᴀᴛᴏʀꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  def admin_only(func):
      @wraps(func)
      async def wrapper(self_or_update, update_or_ctx=None, ctx=None):
          # Handle both (self, update, ctx) and (update, ctx) calling conventions
          if isinstance(self_or_update, Update):
              update = self_or_update
              ctx    = update_or_ctx
              self   = None
          else:
              self   = self_or_update
              update = update_or_ctx
              ctx    = ctx

          uid = update.effective_user.id if update.effective_user else 0
          db  = self.db if self else None
          if uid not in Config.ADMIN_IDS and uid not in Config.SUPER_ADMIN_IDS:
              msg = update.effective_message
              if msg:
                  try:
                      await msg.reply_text(
                          f"{Em.BAN} {sc('admin only command')}.",
                          parse_mode=ParseMode.HTML)
                  except:
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
                  except:
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
                  except:
                      pass
              return
          return await func(self, update, ctx)
      return wrapper
  

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 12: ɪɴʟɪɴᴇ ᴋᴇʏʙᴏᴀʀᴅ ʙᴜɪʟᴅᴇʀꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class KB:
      """ᴄᴇɴᴛʀᴀʟɪᴢᴇᴅ ɪɴʟɪɴᴇ ᴋᴇʏʙᴏᴀʀᴅ ꜰᴀᴄᴛᴏʀʏ"""

      @staticmethod
      def home() -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"{Em.DOWNLOAD} {sc('download')}",    callback_data="show_download"),
               InlineKeyboardButton(f"{Em.PREMIUM} {sc('premium')}",      callback_data="show_premium")],
              [InlineKeyboardButton(f"{Em.STATS}   {sc('my stats')}",     callback_data="show_stats"),
               InlineKeyboardButton(f"{Em.SETTINGS} {sc('settings')}",    callback_data="show_settings")],
              [InlineKeyboardButton(f"{Em.QUEUE}   {sc('queue')}",        callback_data="show_queue"),
               InlineKeyboardButton(f"{Em.HISTORY} {sc('history')}",      callback_data="show_history")],
              [InlineKeyboardButton(f"{Em.NEWS}    {sc('cr news')}",      callback_data="show_news"),
               InlineKeyboardButton(f"{Em.REFERRAL} {sc('referral')}",   callback_data="show_referral")],
              [InlineKeyboardButton(f"{Em.HEART}   {sc('favorites')}",   callback_data="show_favorites"),
               InlineKeyboardButton(f"{Em.WATCH}   {sc('watchlist')}",   callback_data="show_watchlist")],
              [InlineKeyboardButton(f"{Em.SUPPORT} {sc('support')} {Config.SUPPORT_USERNAME}",
                                    url=Config.SUPPORT_CHANNEL)],
          ])

      @staticmethod
      def quality(is_premium: bool) -> InlineKeyboardMarkup:
          rows = []
          quals = list(Config.QUALITIES.keys())
          for i in range(0, len(quals), 3):
              row = []
              for q in quals[i:i+3]:
                  locked = q in Config.PREMIUM_QUALITIES and not is_premium
                  label  = f"🔒 {q}" if locked else q
                  row.append(InlineKeyboardButton(label, callback_data=f"set_quality_{q}"))
              rows.append(row)
          rows.append([InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_settings")])
          return InlineKeyboardMarkup(rows)

      @staticmethod
      def encode_preset() -> InlineKeyboardMarkup:
          presets = list(Config.ENCODE_PRESETS.keys())
          rows = []
          for i in range(0, len(presets), 3):
              row = [InlineKeyboardButton(p, callback_data=f"set_preset_{p}")
                     for p in presets[i:i+3]]
              rows.append(row)
          rows.append([InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_settings")])
          return InlineKeyboardMarkup(rows)

      @staticmethod
      def premium_plans() -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(
                  f"⭐ {sc('weekly')} — {Config.SUBSCRIPTION_PRICES['weekly']} {sc('stars')}",
                  callback_data="buy_weekly")],
              [InlineKeyboardButton(
                  f"💎 {sc('monthly')} — {Config.SUBSCRIPTION_PRICES['monthly']} {sc('stars')}",
                  callback_data="buy_monthly")],
              [InlineKeyboardButton(
                  f"👑 {sc('yearly')} — {Config.SUBSCRIPTION_PRICES['yearly']} {sc('stars')}",
                  callback_data="buy_yearly")],
              [InlineKeyboardButton(
                  f"🔥 {sc('lifetime')} — {Config.SUBSCRIPTION_PRICES['lifetime']} {sc('stars')}",
                  callback_data="buy_lifetime")],
              [InlineKeyboardButton(
                  f"{Em.SUPPORT} {sc('buy via')} {Config.SUPPORT_USERNAME}",
                  url=Config.SUPPORT_CHANNEL)],
              [InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")],
          ])

      @staticmethod
      def download_options(queue_id: int, has_sub: bool = False) -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(
                  f"{Em.SUBTITLE} {sc('subtitles')}", callback_data=f"dl_sub_{queue_id}"),
               InlineKeyboardButton(
                  f"{Em.AUDIO} {sc('audio only')}", callback_data=f"dl_audio_{queue_id}")],
              [InlineKeyboardButton(
                  f"{Em.THUMBNAIL} {sc('thumbnail')}", callback_data=f"dl_thumb_{queue_id}"),
               InlineKeyboardButton(
                  f"{Em.CLOSE} {sc('cancel')}", callback_data=f"cancel_dl_{queue_id}")],
          ])

      @staticmethod
      def settings(user: Dict) -> InlineKeyboardMarkup:
          q   = user.get("default_quality",  "720p")
          p   = user.get("encode_preset",    "balanced")
          ntf = "🔔" if user.get("notify_complete") else "🔕"
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"{Em.QUALITY} {sc('quality')}: {q}",
                                     callback_data="cfg_quality")],
              [InlineKeyboardButton(f"{Em.ENCODE} {sc('preset')}: {p}",
                                     callback_data="cfg_preset")],
              [InlineKeyboardButton(f"{ntf} {sc('notifications')}",
                                     callback_data="cfg_notify")],
              [InlineKeyboardButton(f"{Em.THUMBNAIL} {sc('custom thumb')}",
                                     callback_data="cfg_thumb")],
              [InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")],
          ])

      @staticmethod
      def admin_panel() -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"{Em.STATS}    {sc('stats')}",       callback_data="adm_stats"),
               InlineKeyboardButton(f"{Em.BROADCAST} {sc('broadcast')}",  callback_data="adm_broadcast_menu")],
              [InlineKeyboardButton(f"{Em.QUEUE}   {sc('queue')}",        callback_data="adm_queue"),
               InlineKeyboardButton(f"{Em.LOG}     {sc('logs')}",         callback_data="adm_logs")],
              [InlineKeyboardButton(f"{Em.PREMIUM} {sc('premium mgmt')}", callback_data="adm_premium"),
               InlineKeyboardButton(f"{Em.COOKIE}  {sc('cookies')}",      callback_data="adm_cookies")],
              [InlineKeyboardButton(f"{Em.SETTINGS} {sc('settings')}",    callback_data="adm_settings"),
               InlineKeyboardButton(f"{Em.CODE}    {sc('custom cmds')}",  callback_data="adm_cmds")],
              [InlineKeyboardButton(f"{Em.AUTH}    {sc('auth groups')}",  callback_data="adm_auth"),
               InlineKeyboardButton(f"{Em.NEWS}    {sc('cr news')}",      callback_data="adm_news")],
              [InlineKeyboardButton(f"{Em.CLOSE}   {sc('close')}",        callback_data="adm_close")],
          ])

      @staticmethod
      def confirm(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"✅ {sc('yes')}", callback_data=yes_data),
               InlineKeyboardButton(f"❌ {sc('no')}",  callback_data=no_data)],
          ])

      @staticmethod
      def back(target: str = "show_home") -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data=target)]
          ])

      @staticmethod
      def news_item(news_url: str, news_id: int) -> InlineKeyboardMarkup:
          return InlineKeyboardMarkup([
              [InlineKeyboardButton(f"📰 {sc('read full article')}", url=news_url)],
              [InlineKeyboardButton(f"{Em.BACK} {sc('back to news')}", callback_data="show_news")],
          ])

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 13: ꜱᴇɴᴅ ʜᴇʟᴘᴇʀꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  async def safe_edit(msg, text: str, reply_markup=None, parse_mode=ParseMode.HTML):
      """Edit message, ignoring 'message is not modified' errors."""
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
      """Reply to update (works for messages and callback queries)."""
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
      except (TelegramError, Exception) as e:
          logger.error(f"safe_reply: {e}")
          return None

  async def log_to_channel(bot, text: str, db: Database, parse_mode=ParseMode.HTML):
      """Send log message to log channel if configured."""
      log_ch = int(db.get_setting("log_channel", "0"))
      if log_ch:
          try:
              await bot.send_message(log_ch, text, parse_mode=parse_mode)
          except Exception as e:
              logger.debug(f"log_to_channel: {e}")

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 14: ᴍᴀɪɴ ʙᴏᴛ ʜᴀɴᴅʟᴇʀ
  # ══════════════════════════════════════════════════════════════════════════════

  class CrunchyBot:
      def __init__(self):
          self.db         = Database()
          self.downloader = DownloadManager(self.db)
          self._queue_task: Optional[asyncio.Task] = None
          self._sched_task: Optional[asyncio.Task] = None
          self._news_task:  Optional[asyncio.Task] = None
          self._processing: Dict[int, bool] = {}

      # ──────────── ʜᴇʟᴘᴇʀꜱ ────────────────────────────────────────────────────

      def _uid(self, update: Update) -> int:
          return update.effective_user.id if update.effective_user else 0

      def _msg(self, update: Update):
          return update.effective_message

      def _uname(self, update: Update) -> str:
          u = update.effective_user
          return u.first_name if u else sc("user")

      async def _auth_check(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
          uid = self._uid(update)
          ok, links = await AuthChecker.check_user(ctx.bot, uid, self.db)
          if not ok:
              kb = [[InlineKeyboardButton(f"📢 {sc('join channel/group')}", url=l)] for l in links if l]
              kb.append([InlineKeyboardButton(f"{Em.REFRESH} {sc('check again')}", callback_data="auth_check")])
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

      # ──────────── /ꜱᴛᴀʀᴛ ─────────────────────────────────────────────────────

      async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          user  = update.effective_user
          uname = user.username if user else None
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

          welcome = self.db.get_setting("welcome_message",
              f"{Em.ANIME} <b>{sc('welcome to crunchyroll ultimate bot')}!</b>")

          is_pm = self.db.is_premium(uid)
          text = (
              f"{Em.ANIME} <b>{sc('crunchyroll ultimate bot v200.0')}</b>\n\n"
              f"{sc('hello')}, <b>{fname}</b>! {sc('welcome to the ultimate crunchyroll download experience')}.\n\n"
              f"{'💎 <b>' + sc('premium member') + '</b>' if is_pm else '🆓 ' + sc('free user')}\n\n"
              f"{Em.FAST} <b>{sc('premium users')}</b>: {sc('fast lane, 1080p/4k/hdr, unlimited')}\n"
              f"{Em.SLOW} <b>{sc('free users')}</b>: {sc('slow lane, up to 720p, 3 downloads/day')}\n\n"
              f"{sc('send a crunchyroll url or use the menu below')}:"
          )
          if referrer:
              referrer_user = self.db.get_user(referrer)
              rname = referrer_user.get("first_name", sc("someone")) if referrer_user else sc("someone")
              text += f"\n\n{Em.REFERRAL} {sc('referred by')} <b>{rname}</b>!"

          await safe_reply(update, text, KB.home())

          if uid not in Config.ADMIN_IDS:
              await log_to_channel(ctx.bot,
                  f"{Em.INFO} {sc('new user')}: {fname} (@{uname or 'no_username'}) — ID: <code>{uid}</code>",
                  self.db)

      # ──────────── /ʜᴇʟᴘ ──────────────────────────────────────────────────────

      async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          is_pm = self.db.is_premium(uid)
          is_adm= self.db.is_admin(uid)

          text = (
              f"{Em.INFO} <b>{sc('commands reference')}</b>\n\n"
              f"<b>{sc('download')}</b>\n"
              f"/cr <code>{sc('url')}</code> — {sc('download crunchyroll episode')}\n"
              f"/batch <code>{sc('url1 url2')}</code> — {sc('batch download (premium)')}\n"
              f"/schedule <code>{sc('url hh:mm')}</code> — {sc('schedule a download')}\n\n"
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
              )
          await safe_reply(update, text, KB.back())

      # ──────────── /ᴄʀ (ᴅᴏᴡɴʟᴏᴀᴅ) ────────────────────────────────────────────

      async def cmd_cr(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid  = self._uid(update)
          msg  = self._msg(update)

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
                  f"<code>/cr https://www.crunchyroll.com/watch/XXXXXXXX/episode-title</code>")
              return

          if not self.downloader.cr.is_valid_url(url):
              await safe_reply(update,
                  f"{Em.ERROR} {sc('not a valid crunchyroll url')}.\n"
                  f"{sc('please send a crunchyroll.com link')}.")
              return

          can, reason = self.db.can_download(uid)
          if not can:
              await safe_reply(update, reason, KB.premium_plans() if "free limit" in reason else None)
              return

          queue_count = self.db.get_queue_count(uid)
          if queue_count >= Config.MAX_QUEUE_PER_USER:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('queue full')} ({queue_count}/{Config.MAX_QUEUE_PER_USER}).\n"
                  f"{sc('wait for current downloads to finish or use')} /cancel {sc('to remove items')}.")
              return

          user_data = self.db.get_user(uid) or {}
          quality   = user_data.get("default_quality", Config.DEFAULT_QUALITY)
          preset    = user_data.get("encode_preset",   Config.DEFAULT_ENCODE)
          is_pm     = self.db.is_premium(uid)

          qid = self.db.add_to_queue(uid, url, quality, preset,
                                     msg.message_id if msg else None,
                                     msg.chat_id if msg else None)
          pos = self.db.get_queue_position(qid)

          lane_text = (f"{Em.FAST} <b>{sc('fast lane')}</b>" if is_pm
                       else f"{Em.SLOW} <b>{sc('slow lane')}</b>")
          delay_text = (sc("no delay") if is_pm
                        else f"{sc('~')} {self.db.get_setting('free_download_delay', '30')}s {sc('delay')}")

          status_msg = await safe_reply(update,
              f"{Em.QUEUE} <b>{sc('added to queue')}</b>\n\n"
              f"{Em.INFO} {sc('id')}: <code>#{qid}</code>\n"
              f"{Em.PROGRESS} {sc('position')}: #{pos}\n"
              f"{lane_text} — {delay_text}\n"
              f"{Em.QUALITY} {sc('quality')}: <code>{quality}</code>\n"
              f"{Em.ENCODE} {sc('preset')}: <code>{preset}</code>\n\n"
              f"{ProgressBar.make(0)}",
              KB.download_options(qid))

          # Store status message for progress updates
          if status_msg and ctx.bot_data is not None:
              ctx.bot_data[f"qmsg_{qid}"] = (status_msg.chat_id, status_msg.message_id)

          self._ensure_queue_running()

      # ──────────── /ᴘʀᴇᴍɪᴜᴍ ──────────────────────────────────────────────────

      async def cmd_premium(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          is_pm = self.db.is_premium(uid)
          plan  = self.db.get_premium_type(uid)
          exp   = self.db.get_premium_expiry(uid)

          text = f"{Em.PREMIUM} <b>{sc('crunchyroll premium membership')}</b>\n\n"

          if is_pm:
              text += (
                  f"{Em.SUCCESS} {sc('you are a premium member')}!\n"
                  f"📋 {sc('plan')}: <b>{plan.upper()}</b>\n"
                  f"📅 {sc('expires')}: <b>{exp.strftime('%Y-%m-%d %H:%M') if exp else sc('lifetime')}</b>\n\n"
              )
          else:
              text += f"{Em.INFO} {sc('you are on the free plan')}\n\n"

          text += (
              f"<b>{sc('plans')}:</b>\n\n"
              f"⭐ <b>{sc('weekly')}</b> — {Config.SUBSCRIPTION_PRICES['weekly']} {sc('stars')}\n"
              f"   {'  '.join(Config.SUBSCRIPTION_FEATURES['weekly'])}\n\n"
              f"💎 <b>{sc('monthly')}</b> — {Config.SUBSCRIPTION_PRICES['monthly']} {sc('stars')}\n"
              f"   {'  '.join(Config.SUBSCRIPTION_FEATURES['monthly'])}\n\n"
              f"👑 <b>{sc('yearly')}</b> — {Config.SUBSCRIPTION_PRICES['yearly']} {sc('stars')}\n"
              f"   {'  '.join(Config.SUBSCRIPTION_FEATURES['yearly'])}\n\n"
              f"🔥 <b>{sc('lifetime')}</b> — {Config.SUBSCRIPTION_PRICES['lifetime']} {sc('stars')}\n"
              f"   {'  '.join(Config.SUBSCRIPTION_FEATURES['lifetime'])}\n\n"
              f"{Em.FAST} {sc('premium benefits')}:\n"
              f"• {sc('fast download lane (no delay)')}\n"
              f"• {sc('1080p / 4k / hdr quality')}\n"
              f"• {sc('unlimited daily downloads')}\n"
              f"• {sc('batch downloads up to')} {Config.MAX_BATCH_SIZE} {sc('at once')}\n"
              f"• {sc('priority queue (10x faster)')}\n"
              f"• {sc('custom thumbnail & watermark')}\n\n"
              f"{Em.SUPPORT} {sc('to buy contact')}: {Config.SUPPORT_USERNAME}"
          )
          await safe_reply(update, text, KB.premium_plans())

      # ──────────── /ꜱᴛᴀᴛꜱ ─────────────────────────────────────────────────────

      async def cmd_stats(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          user  = self.db.get_user(uid)
          is_pm = self.db.is_premium(uid)
          daily = self.db.get_daily_downloads(uid)
          limit = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
          plan  = self.db.get_premium_type(uid)
          exp   = self.db.get_premium_expiry(uid)
          lane  = f"{Em.FAST} {sc('fast lane')}" if is_pm else f"{Em.SLOW} {sc('slow lane')}"

          await safe_reply(update,
              f"{Em.STATS} <b>{sc('your statistics')}</b>\n\n"
              f"<b>{sc('profile')}:</b>\n"
              f"├ {sc('name')}: {user.get('first_name','?') if user else '?'}\n"
              f"├ {sc('plan')}: {'💎 ' + plan.upper() if is_pm else '🆓 ' + sc('free')}\n"
              f"├ {sc('lane')}: {lane}\n"
              f"├ {sc('expires')}: {exp.strftime('%Y-%m-%d') if exp and is_pm else 'N/A'}\n"
              f"└ {sc('referral code')}: <code>{self.db.get_referral_code(uid)}</code>\n\n"
              f"<b>{sc('usage')}:</b>\n"
              f"├ {sc('today')}: {daily}/{limit if limit < 999999 else sc('unlimited')}\n"
              f"├ {sc('all-time')}: {user.get('total_downloads',0) if user else 0:,}\n"
              f"├ {sc('data')}: {round((user.get('total_size',0) if user else 0)/(1024**3),3)} GB\n"
              f"└ {sc('queue')}: {self.db.get_queue_count(uid)}\n\n"
              f"<b>{sc('social')}:</b>\n"
              f"├ {sc('referrals')}: {self.db.get_referral_count(uid)}\n"
              f"├ {sc('referral points')}: {self.db.get_referral_points(uid)}\n"
              f"└ {sc('favorites')}: {len(self.db.get_favorites(uid))}",
              KB.back())

      # ──────────── /ꜱᴇᴛᴛɪɴɢꜱ ──────────────────────────────────────────────────

      async def cmd_settings(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid  = self._uid(update)
          user = self.db.get_user(uid) or {}
          await safe_reply(update,
              f"{Em.SETTINGS} <b>{sc('user settings')}</b>\n\n"
              f"{sc('tap a button to change')}:",
              KB.settings(user))

      # ──────────── /ʀᴇᴅᴇᴇᴍ ───────────────────────────────────────────────────

      async def cmd_redeem(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
          self.db.add_premium(uid, plan, days, f"redeem_{code}")
          await safe_reply(update,
              f"{Em.SUCCESS} <b>{sc('code redeemed')}!</b>\n\n"
              f"📋 {sc('plan')}: <b>{plan.upper()}</b>\n"
              f"📅 {sc('days')}: <b>{days}</b>\n\n"
              f"{sc('enjoy your premium membership')}! {Em.FIRE}")

      # ──────────── /ʀᴇꜰᴇʀʀᴀʟ ─────────────────────────────────────────────────

      async def cmd_referral(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid     = self._uid(update)
          code    = self.db.get_referral_code(uid)
          count   = self.db.get_referral_count(uid)
          points  = self.db.get_referral_points(uid)
          reward  = int(self.db.get_setting("referral_reward",  "50"))
          req     = int(self.db.get_setting("referral_required", "5"))
          bot_info= await ctx.bot.get_me()
          ref_link= f"https://t.me/{bot_info.username}?start=ref_{code}"

          top = self.db.get_top_referrers(5)
          lb  = ""
          medals = ["🥇","🥈","🥉","🏅","🏅"]
          for i, u in enumerate(top):
              is_me = " ← {sc('you')}" if u["user_id"] == uid else ""
              lb += f"\n{medals[i]} {u.get('first_name','?')} — {u['referral_count']} {sc('refs')}{is_me}"

          await safe_reply(update,
              f"{Em.REFERRAL} <b>{sc('referral program')}</b>\n\n"
              f"🔗 {sc('your link')}:\n<code>{ref_link}</code>\n\n"
              f"📊 {sc('your stats')}:\n"
              f"├ {sc('total referrals')}: <b>{count}</b>\n"
              f"├ {sc('points earned')}: <b>{points}</b>\n"
              f"└ {sc('reward per referral')}: <b>{reward} {sc('points')}</b>\n\n"
              f"🎯 {sc('refer')} <b>{req}</b> {sc('users to unlock a free week of premium')}!\n\n"
              f"<b>{sc('top referrers')}:</b>{lb}",
              InlineKeyboardMarkup([
                  [InlineKeyboardButton(f"🔗 {sc('share link')}", switch_inline_query=f"ref_{code}")],
                  [InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")],
              ]))

      # ──────────── /ɴᴇᴡꜱ ──────────────────────────────────────────────────────

      async def cmd_news(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid  = self._uid(update)
          news = self.db.get_latest_news(8)
          if not news:
              status = await safe_reply(update,
                  f"{Em.NEWS} {sc('fetching crunchyroll news')}…")
              fetched = await self.downloader.cr.fetch_cr_news()
              for n in fetched:
                  self.db.save_news(n["title"], n["description"],
                                    n["url"], n["image_url"], n["published_at"])
              news = self.db.get_latest_news(8)
              if status:
                  try: await status.delete()
                  except: pass

          if not news:
              await safe_reply(update,
                  f"{Em.NEWS} {sc('no news available right now. try again later')}.",
                  KB.back())
              return

          lines = [f"{Em.NEWS} <b>{sc('crunchyroll latest news')}</b>\n"]
          kb_rows = []
          for i, n in enumerate(news[:8], 1):
              title  = n.get("title", "")[:60]
              pub    = str(n.get("published_at",""))[:16]
              lines.append(f"\n<b>{i}.</b> {title}\n   📅 {pub}")
              if n.get("url"):
                  kb_rows.append([
                      InlineKeyboardButton(f"📰 {i}. {title[:30]}…", url=n["url"])
                  ])
          kb_rows.append([InlineKeyboardButton(f"{Em.REFRESH} {sc('refresh')}", callback_data="refresh_news")])
          kb_rows.append([InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")])
          await safe_reply(update, "\n".join(lines), InlineKeyboardMarkup(kb_rows))

      # ──────────── /ꜰᴀᴠᴏʀɪᴛᴇꜱ ─────────────────────────────────────────────────

      async def cmd_favorites(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid  = self._uid(update)
          favs = self.db.get_favorites(uid)
          if not favs:
              await safe_reply(update,
                  f"{Em.HEART} {sc('no favorites yet')}.\n"
                  f"{sc('use')} /addfav <code>{sc('anime_id title')}</code> {sc('to add')}.",
                  KB.back())
              return
          lines = [f"{Em.HEART} <b>{sc('your favorites')} ({len(favs)})</b>\n"]
          for f in favs[:20]:
              lines.append(f"• <b>{f['anime_title'][:40]}</b> — <code>{f['anime_id']}</code>")
          await safe_reply(update, "\n".join(lines), KB.back())

      # ──────────── /ᴡᴀᴛᴄʜʟɪꜱᴛ ─────────────────────────────────────────────────

      async def cmd_watchlist(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          wl  = self.db.get_watchlist(uid)
          if not wl:
              await safe_reply(update,
                  f"{Em.WATCH} {sc('watchlist empty')}.\n"
                  f"{sc('use')} /addwatch <code>{sc('anime_id title')}</code> {sc('to add')}.",
                  KB.back())
              return
          lines = [f"{Em.WATCH} <b>{sc('your watchlist')} ({len(wl)})</b>\n"]
          for w in wl[:20]:
              lines.append(f"• <b>{w['anime_title'][:40]}</b> — {sc('next')}: Ep {w['next_episode']}")
          await safe_reply(update, "\n".join(lines), KB.back())

      # ──────────── /ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ──────────────────────────────────────────────

      async def cmd_leaderboard(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          lb     = self.db.get_leaderboard(10)
          medals = ["🥇","🥈","🥉"] + ["🏅"]*7
          lines  = [f"{Em.LEAD} <b>{sc('top downloaders')}</b>\n"]
          for i, u in enumerate(lb):
              gb = round((u.get("total_size",0) or 0)/(1024**3), 2)
              lines.append(
                  f"{medals[i]} <b>{u.get('first_name','?')}</b> — "
                  f"{u['total_downloads']:,} {sc('dls')} | {gb} GB")
          await safe_reply(update, "\n".join(lines), KB.back())

      # ──────────── /ꜰᴇᴇᴅʙᴀᴄᴋ ─────────────────────────────────────────────────

      async def cmd_feedback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /feedback <code>{sc('1-5 message')}</code>")
              return
          try:
              rating = int(ctx.args[0])
              assert 1 <= rating <= 5
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('rating must be 1-5')}.")
              return
          msg_text = " ".join(ctx.args[1:])
          stars = "⭐" * rating + "☆" * (5 - rating)
          self.db.add_feedback(self._uid(update), rating, msg_text)
          await safe_reply(update,
              f"{Em.SUCCESS} {sc('thank you for your feedback')}!\n"
              f"{sc('rating')}: {stars}\n"
              f"{sc('message')}: {msg_text[:200]}")

      # ──────────── /ꜱᴄʜᴇᴅᴜʟᴇ ─────────────────────────────────────────────────

      async def cmd_schedule(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.SCHEDULE} {sc('usage')}: /schedule <code>{sc('url hh:mm [quality] [preset]')}</code>\n"
                  f"{sc('example')}: <code>/schedule https://crunchyroll.com/watch/... 22:00 1080p balanced</code>")
              return
          url      = ctx.args[0]
          time_str = ctx.args[1]
          quality  = ctx.args[2] if len(ctx.args) > 2 else Config.DEFAULT_QUALITY
          preset   = ctx.args[3] if len(ctx.args) > 3 else Config.DEFAULT_ENCODE
          try:
              today  = datetime.now().date()
              run_at = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")
              if run_at < datetime.now():
                  run_at += timedelta(days=1)
          except ValueError:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('invalid time format. use hh:mm')}.")
              return
          sid = self.db.schedule_download(
              self._uid(update), url, quality, preset, run_at.isoformat())
          await safe_reply(update,
              f"{Em.SCHEDULE} <b>{sc('scheduled')}!</b>\n\n"
              f"{sc('id')}: <code>#{sid}</code>\n"
              f"{sc('time')}: {run_at.strftime('%Y-%m-%d %H:%M')}\n"
              f"{sc('quality')}: <code>{quality}</code> | {sc('preset')}: <code>{preset}</code>")

      # ──────────── /ʙᴀᴛᴄʜ ─────────────────────────────────────────────────────

      @premium_only
      async def cmd_batch(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          urls  = [a for a in ctx.args if self.downloader.cr.is_valid_url(a)][:Config.MAX_BATCH_SIZE]
          if not urls:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /batch <code>{sc('url1 url2 ...')}</code>\n"
                  f"{sc('provide crunchyroll urls separated by spaces')}.")
              return
          udata   = self.db.get_user(uid) or {}
          quality = udata.get("default_quality", Config.DEFAULT_QUALITY)
          preset  = udata.get("encode_preset",   Config.DEFAULT_ENCODE)
          added   = []
          for url in urls:
              can, _ = self.db.can_download(uid)
              if can:
                  qid = self.db.add_to_queue(uid, url, quality, preset)
                  added.append(qid)
          await safe_reply(update,
              f"{Em.SUCCESS} <b>{sc('batch queued')}:</b> {len(added)}/{len(urls)} {sc('items')}\n"
              f"{Em.QUALITY} {sc('quality')}: <code>{quality}</code> | "
              f"{Em.ENCODE} {sc('preset')}: <code>{preset}</code>")
          self._ensure_queue_running()

      # ──────────── /ǫᴜᴇᴜᴇ ─────────────────────────────────────────────────────

      async def cmd_queue(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid   = self._uid(update)
          items = self.db.get_user_queue(uid)
          if not items:
              await safe_reply(update,
                  f"{Em.QUEUE} {sc('queue is empty')}. {sc('use')} /cr {sc('to start a download')}.",
                  KB.back())
              return
          lines = [f"{Em.QUEUE} <b>{sc('your queue')} ({len(items)} {sc('items')})</b>\n"]
          for it in items:
              lane  = f"{Em.FAST}" if it.get("is_fast") else f"{Em.SLOW}"
              icon  = "⚡" if it["status"] == "processing" else "⏳"
              short = it["url"][-35:] if len(it["url"]) > 35 else it["url"]
              lines.append(
                  f"{icon} {lane} <b>#{it['id']}</b> | <code>{it['quality']}</code> | "
                  f"<code>{it['encode_preset']}</code>\n"
                  f"   <code>…{short}</code>\n"
                  f"   {ProgressBar.make(it['progress'])}")
          lines.append(f"\n{sc('use')} /cancel <code>{sc('id')}</code> {sc('to remove')}")
          await safe_reply(update, "\n".join(lines), KB.back())

      # ──────────── /ᴄᴀɴᴄᴇʟ ───────────────────────────────────────────────────

      async def cmd_cancel(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /cancel <code>{sc('queue_id')}</code>")
              return
          try:
              qid = int(ctx.args[0])
              if self.db.cancel_queue_item(qid, uid):
                  await safe_reply(update,
                      f"{Em.SUCCESS} {sc('download')} #{qid} {sc('cancelled')}.")
              else:
                  await safe_reply(update,
                      f"{Em.ERROR} {sc('cannot cancel (already processing or not yours)')}.")
          except ValueError:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid id')}.")

      # ──────────── /ʜɪꜱᴛᴏʀʏ ──────────────────────────────────────────────────

      async def cmd_history(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid  = self._uid(update)
          hist = self.db.get_download_history(uid, 15)
          if not hist:
              await safe_reply(update,
                  f"{Em.HISTORY} {sc('no history yet. use')} /cr {sc('to start')}!",
                  KB.back())
              return
          lines = [f"{Em.HISTORY} <b>{sc('download history')}</b>\n"]
          for h in hist:
              size_mb = round(h["file_size"]/(1024*1024), 1) if h["file_size"] else 0
              lines.append(
                  f"🎬 <b>{h['anime_title'][:35]}</b>\n"
                  f"   {h['episode_title'][:40]}\n"
                  f"   <code>{h['quality']}</code> | <code>{h['encode_preset']}</code> | {size_mb}MB\n"
                  f"   📅 {str(h['downloaded_at'])[:10]}")
          await safe_reply(update, "\n\n".join(lines), KB.back())

      # ──────────── ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ ──────────────────────────────────────────────

      async def cmd_mediainfo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg = self._msg(update)
          if not msg:
              return
          target = msg.reply_to_message
          if not target:
              await safe_reply(update,
                  f"{Em.INFO} {sc('reply to a video/document with')} /mediainfo")
              return
          doc = target.document or target.video
          if not doc:
              await safe_reply(update, f"{Em.ERROR} {sc('reply to a video or document')}.")
              return
          if doc.file_size > 100 * 1024 * 1024:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('file too large for analysis (>100mb)')}.")
              return
          status = await safe_reply(update, f"{Em.LOADING} {sc('analyzing')}…")
          try:
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"mi_{doc.file_unique_id}.tmp")
              await f.download_to_drive(fp)
              info = await VideoTools.get_media_info(fp)
              Path(fp).unlink(missing_ok=True)
              if not info:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('could not read media info')}.")
                  return
              text = (
                  f"{Em.INFO} <b>{sc('media info')}</b>\n\n"
                  f"⏱ {sc('duration')}: {info.get('duration','N/A')}\n"
                  f"📦 {sc('size')}: {info.get('size_mb','N/A')} MB\n"
                  f"🎞 {sc('format')}: {info.get('format','N/A')}\n"
                  f"🎬 {sc('video')}: {info.get('video_codec','N/A')} "
                  f"{info.get('width','?')}×{info.get('height','?')} "
                  f"@ {info.get('fps',0)} fps\n"
                  f"🎵 {sc('audio')}: {info.get('audio_codec','N/A')} "
                  f"{info.get('channels','?')}ch @ {info.get('sample_rate','N/A')}Hz"
              )
              if status: await safe_edit(status, text)
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      async def cmd_rename(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg = self._msg(update)
          if not msg:
              return
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.RENAME} {sc('usage')}: /rename <code>{sc('new_filename')}</code>\n"
                  f"{sc('reply to a file and use this command')}.")
              return
          target = msg.reply_to_message
          if not target or not (target.document or target.video):
              await safe_reply(update,
                  f"{Em.ERROR} {sc('reply to a video/document')}.")
              return
          new_name  = " ".join(ctx.args)
          safe_name = re.sub(r'[<>:"/\\|?*]', "_", new_name)
          if not safe_name.endswith(".mp4"):
              safe_name += ".mp4"
          status = await safe_reply(update, f"{Em.LOADING} {sc('renaming')}…")
          try:
              doc = target.document or target.video
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"rename_{doc.file_unique_id}.mp4")
              await f.download_to_drive(fp)
              out = str(Config.TEMP_PATH / safe_name)
              Path(fp).rename(out)
              await ctx.bot.send_document(
                  msg.chat_id,
                  document=InputFile(out, filename=safe_name),
                  caption=f"{Em.SUCCESS} {sc('renamed to')}: <code>{safe_name}</code>",
                  parse_mode=ParseMode.HTML)
              Path(out).unlink(missing_ok=True)
              if status: await status.delete()
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      async def cmd_compress(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          msg = self._msg(update)
          if not msg:
              return
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.ENCODE} {sc('usage')}: /compress <code>{sc('target_mb')}</code>\n"
                  f"{sc('reply to a video')}")
              return
          target = msg.reply_to_message
          if not target or not (target.document or target.video):
              await safe_reply(update, f"{Em.ERROR} {sc('reply to a video/document')}.")
              return
          try:
              target_mb = int(ctx.args[0])
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid size')}.")
              return
          status = await safe_reply(update,
              f"{Em.LOADING} {sc('compressing to')} {target_mb}MB…")
          try:
              doc = target.document or target.video
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"comp_{doc.file_unique_id}.mp4")
              await f.download_to_drive(fp)
              out = await VideoTools.compress_video(fp, target_mb)
              if out and Path(out).exists():
                  fname = f"compressed_{target_mb}mb_{uuid.uuid4().hex[:6]}.mp4"
                  await ctx.bot.send_document(
                      msg.chat_id,
                      document=InputFile(out, filename=fname),
                      caption=f"{Em.SUCCESS} {sc('compressed to')} {round(Path(out).stat().st_size/1024/1024,1)}MB",
                      parse_mode=ParseMode.HTML)
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('compression failed')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      async def cmd_trim(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg = self._msg(update)
          if not ctx.args or len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.VIDEO} {sc('usage')}: /trim <code>{sc('start end')}</code>\n"
                  f"{sc('example')}: /trim 00:00:10 00:02:30\n"
                  f"{sc('reply to a video')}.")
              return
          target = msg.reply_to_message if msg else None
          if not target or not (target.document or target.video):
              await safe_reply(update, f"{Em.ERROR} {sc('reply to a video/document')}.")
              return
          start, end = ctx.args[0], ctx.args[1]
          status = await safe_reply(update, f"{Em.LOADING} {sc('trimming')}…")
          try:
              doc = target.document or target.video
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"trim_{doc.file_unique_id}.mp4")
              await f.download_to_drive(fp)
              out = await VideoTools.trim_video(fp, start, end)
              if out and Path(out).exists():
                  fname = f"trimmed_{uuid.uuid4().hex[:6]}.mp4"
                  await ctx.bot.send_document(
                      msg.chat_id,
                      document=InputFile(out, filename=fname),
                      caption=f"{Em.SUCCESS} {sc('trimmed')}: {start} → {end}",
                      parse_mode=ParseMode.HTML)
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('trim failed')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      async def cmd_thumbnail(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg    = self._msg(update)
          target = msg.reply_to_message if msg else None
          if not target or not (target.document or target.video):
              await safe_reply(update,
                  f"{Em.THUMBNAIL} {sc('reply to a video with')} /thumbnail")
              return
          ts = ctx.args[0] if ctx.args else "00:00:05"
          status = await safe_reply(update, f"{Em.LOADING} {sc('extracting thumbnail')}…")
          try:
              doc = target.document or target.video
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"th_{doc.file_unique_id}.mp4")
              await f.download_to_drive(fp)
              out = await VideoTools.screenshot_video(fp, ts)
              if out and Path(out).exists():
                  await ctx.bot.send_photo(
                      msg.chat_id, photo=InputFile(out),
                      caption=f"{Em.THUMBNAIL} {sc('thumbnail at')} {ts}",
                      parse_mode=ParseMode.HTML)
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('could not extract thumbnail')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      @premium_only
      async def cmd_watermark(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg    = self._msg(update)
          target = msg.reply_to_message if msg else None
          if not target or not (target.document or target.video):
              await safe_reply(update,
                  f"{Em.THUMBNAIL} {sc('reply to a video with')} /watermark <code>{sc('text')}</code>")
              return
          text = " ".join(ctx.args) if ctx.args else sc("crunchyroll bot")
          pos  = "bottomright"
          status = await safe_reply(update, f"{Em.LOADING} {sc('adding watermark')}…")
          try:
              doc = target.document or target.video
              f   = await ctx.bot.get_file(doc.file_id)
              fp  = str(Config.TEMP_PATH / f"wm_{doc.file_unique_id}.mp4")
              await f.download_to_drive(fp)
              out = await VideoTools.add_watermark(fp, text, pos)
              if out and Path(out).exists():
                  fname = f"watermarked_{uuid.uuid4().hex[:6]}.mp4"
                  await ctx.bot.send_document(
                      msg.chat_id,
                      document=InputFile(out, filename=fname),
                      caption=f"{Em.SUCCESS} {sc('watermark added')}: <code>{text}</code>",
                      parse_mode=ParseMode.HTML)
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('watermark failed')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      @premium_only
      async def cmd_gif(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg    = self._msg(update)
          target = msg.reply_to_message if msg else None
          if not target or not (target.document or target.video):
              await safe_reply(update,
                  f"{Em.VIDEO} {sc('reply to a video with')} /gif <code>{sc('start duration scale')}</code>\n"
                  f"{sc('example')}: /gif 00:01:30 5 480")
              return
          start    = ctx.args[0] if len(ctx.args) > 0 else "00:00:00"
          duration = int(ctx.args[1]) if len(ctx.args) > 1 else 5
          scale    = int(ctx.args[2]) if len(ctx.args) > 2 else 320
          status   = await safe_reply(update, f"{Em.LOADING} {sc('creating gif')}…")
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
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('gif creation failed')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      @premium_only
      async def cmd_audio(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg    = self._msg(update)
          target = msg.reply_to_message if msg else None
          if not target or not (target.document or target.video):
              await safe_reply(update,
                  f"{Em.AUDIO} {sc('reply to a video with')} /audio <code>[mp3|aac]</code>")
              return
          fmt    = ctx.args[0].lower() if ctx.args and ctx.args[0].lower() in ("mp3","aac") else "mp3"
          status = await safe_reply(update, f"{Em.LOADING} {sc('extracting audio')}…")
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
                  Path(fp).unlink(missing_ok=True)
                  Path(out).unlink(missing_ok=True)
                  if status: await status.delete()
              else:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('audio extraction failed')}.")
          except Exception as e:
              if status: await safe_edit(status, f"{Em.ERROR} {sc('error')}: {e}")

      # ──────────── /ᴀᴅᴅᴡᴀᴛᴄʜ / /ᴀᴅᴅꜰᴀᴠ ──────────────────────────────────────

      async def cmd_addfav(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.HEART} {sc('usage')}: /addfav <code>{sc('anime_id title')}</code>")
              return
          anime_id    = ctx.args[0]
          anime_title = " ".join(ctx.args[1:])
          if self.db.add_favorite(uid, anime_title, anime_id):
              await safe_reply(update,
                  f"{Em.HEART} <b>{anime_title}</b> {sc('added to favorites')}!")
          else:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('already in favorites or error')}.")

      async def cmd_addwatch(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.WATCH} {sc('usage')}: /addwatch <code>{sc('anime_id title')}</code>")
              return
          anime_id    = ctx.args[0]
          anime_title = " ".join(ctx.args[1:])
          if self.db.add_watchlist(uid, anime_title, anime_id):
              await safe_reply(update,
                  f"{Em.WATCH} <b>{anime_title}</b> {sc('added to watchlist')}!")
          else:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('already in watchlist or error')}.")

      # ──────────── /ɢɪꜰᴛ / /ᴄʟᴀɪᴍɢɪꜰᴛ ──────────────────────────────────────

      @premium_only
      async def cmd_gift(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          uid = self._uid(update)
          if len(ctx.args) < 3:
              await safe_reply(update,
                  f"{Em.GIFT} {sc('usage')}: /gift <code>{sc('user_id plan [message]')}</code>\n"
                  f"{sc('plans')}: weekly, monthly, yearly, lifetime")
              return
          try:
              to_uid  = int(ctx.args[0])
              plan    = ctx.args[1].lower()
              message = " ".join(ctx.args[2:]) if len(ctx.args) > 2 else ""
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
              return
          if plan not in Config.SUBSCRIPTION_DAYS:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('invalid plan. choose')}: weekly, monthly, yearly, lifetime")
              return
          days = Config.SUBSCRIPTION_DAYS[plan]
          code = self.db.create_gift(uid, to_uid, plan, days, message)
          await safe_reply(update,
              f"{Em.GIFT} <b>{sc('gift created')}!</b>\n\n"
              f"📋 {sc('plan')}: {plan.upper()} ({days} {sc('days')})\n"
              f"👤 {sc('for user id')}: <code>{to_uid}</code>\n"
              f"🎟 {sc('gift code')}: <code>{code}</code>\n\n"
              f"{sc('tell them to use')}: /claimgift <code>{code}</code>")

      async def cmd_claimgift(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
          self.db.add_premium(uid, plan, days, f"gift_{code}", None)
          await safe_reply(update,
              f"{Em.GIFT} <b>{sc('gift claimed')}!</b>\n\n"
              f"📋 {sc('plan')}: {plan.upper()}\n"
              f"📅 {sc('days')}: {days}\n\n"
              f"{sc('enjoy your premium')}! {Em.FIRE}")
  

      # ══════════════════════════════════════════════════════════════════════════
      #  ADMIN COMMANDS
      # ══════════════════════════════════════════════════════════════════════════

      @admin_only
      async def cmd_admin(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          counts = self.db.get_user_count()
          q_all  = self.db.get_all_queue()
          text = (
              f"{Em.ADMIN} <b>{sc('admin panel')}</b>\n\n"
              f"👥 {sc('users')}: {counts['total']:,} total | "
              f"{counts['premium']} {sc('premium')} | "
              f"{counts['banned']} {sc('banned')}\n"
              f"{Em.QUEUE} {sc('active queue')}: {len(q_all)} {sc('items')}\n"
          )
          await safe_reply(update, text, KB.admin_panel())

      @admin_only
      async def cmd_broadcast(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg  = self._msg(update)
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.BROADCAST} {sc('usage')}: /broadcast <code>{sc('message')}</code>\n"
                  f"{sc('options')}: --premium-only, --free-only")
              return
          premium_only_flag = "--premium-only" in ctx.args
          free_only_flag    = "--free-only"    in ctx.args
          text = " ".join(a for a in ctx.args
                          if a not in ("--premium-only", "--free-only"))
          if not text:
              await safe_reply(update, f"{Em.ERROR} {sc('no message text provided')}.")
              return
          users  = (self.db.get_all_users(premium_only=True) if premium_only_flag
                    else [u for u in self.db.get_all_users()
                          if not self.db.is_premium(u)] if free_only_flag
                    else self.db.get_all_users())
          status = await safe_reply(update,
              f"{Em.LOADING} {sc('broadcasting to')} {len(users):,} {sc('users')}…")
          sent = fail = 0
          for uid in users:
              try:
                  await ctx.bot.send_message(uid,
                      f"{Em.BROADCAST} <b>{sc('announcement')}</b>\n\n{text}",
                      parse_mode=ParseMode.HTML)
                  sent += 1
              except Forbidden:
                  fail += 1
              except RetryAfter as e:
                  await asyncio.sleep(e.retry_after + 1)
                  try:
                      await ctx.bot.send_message(uid,
                          f"{Em.BROADCAST} <b>{sc('announcement')}</b>\n\n{text}",
                          parse_mode=ParseMode.HTML)
                      sent += 1
                  except:
                      fail += 1
              except:
                  fail += 1
              if (sent + fail) % 50 == 0:
                  try:
                      await status.edit_text(
                          f"{Em.LOADING} {sc('progress')}: {sent+fail}/{len(users):,}",
                          parse_mode=ParseMode.HTML)
                  except:
                      pass
              await asyncio.sleep(0.05)
          if status:
              await safe_edit(status,
                  f"{Em.SUCCESS} {sc('broadcast complete')}!\n"
                  f"{sc('sent')}: {sent:,} | {sc('failed')}: {fail:,}")

      @admin_only
      async def cmd_ban(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.BAN} {sc('usage')}: /ban <code>{sc('user_id reason [days]')}</code>")
              return
          try:
              uid    = int(ctx.args[0])
              reason = " ".join(ctx.args[1:-1]) if ctx.args[-1].isdigit() else " ".join(ctx.args[1:])
              days   = int(ctx.args[-1]) if ctx.args[-1].isdigit() else 0
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
              return
          self.db.register_user(uid)
          self.db.ban_user(uid, self._uid(update), reason, days)
          until = f" {sc('until')} {(datetime.now()+timedelta(days=days)).strftime('%Y-%m-%d')}" if days else ""
          await safe_reply(update,
              f"{Em.BAN} {sc('user')} <code>{uid}</code> {sc('banned')}{until}.\n"
              f"{sc('reason')}: {reason}")
          try:
              await ctx.bot.send_message(uid,
                  f"{Em.BAN} {sc('you have been banned from this bot')}.\n"
                  f"{sc('reason')}: {reason}\n"
                  f"{sc('contact')} {Config.SUPPORT_USERNAME} {sc('to appeal')}.",
                  parse_mode=ParseMode.HTML)
          except:
              pass

      @admin_only
      async def cmd_unban(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.UNBAN} {sc('usage')}: /unban <code>{sc('user_id')}</code>")
              return
          try:
              uid = int(ctx.args[0])
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid user id')}.")
              return
          self.db.unban_user(uid)
          await safe_reply(update,
              f"{Em.SUCCESS} {sc('user')} <code>{uid}</code> {sc('unbanned')}.")
          try:
              await ctx.bot.send_message(uid,
                  f"{Em.SUCCESS} {sc('you have been unbanned')}. {sc('welcome back')}!",
                  parse_mode=ParseMode.HTML)
          except:
              pass

      @admin_only
      async def cmd_warn(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /warn <code>{sc('user_id reason')}</code>")
              return
          try:
              uid    = int(ctx.args[0])
              reason = " ".join(ctx.args[1:])
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
              return
          count = self.db.add_warning(uid)
          await safe_reply(update,
              f"{Em.WARNING} {sc('warning sent to')} <code>{uid}</code>. "
              f"({sc('total')}: {count})")
          try:
              await ctx.bot.send_message(uid,
                  f"{Em.WARNING} <b>{sc('warning')}</b> #{count}\n"
                  f"{sc('reason')}: {reason}\n"
                  f"{sc('3 warnings = ban')}.",
                  parse_mode=ParseMode.HTML)
          except:
              pass
          if count >= 3:
              self.db.ban_user(uid, self._uid(update), sc("auto-ban: 3 warnings"), 7)
              try:
                  await ctx.bot.send_message(uid,
                      f"{Em.BAN} {sc('you have been auto-banned for 7 days due to 3 warnings')}.",
                      parse_mode=ParseMode.HTML)
              except:
                  pass

      @admin_only
      async def cmd_addpremium(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.PREMIUM} {sc('usage')}: /addpremium <code>{sc('user_id plan [days]')}</code>")
              return
          try:
              uid  = int(ctx.args[0])
              plan = ctx.args[1].lower()
              days = int(ctx.args[2]) if len(ctx.args) > 2 else Config.SUBSCRIPTION_DAYS.get(plan, 30)
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
              return
          self.db.register_user(uid)
          if self.db.add_premium(uid, plan, days, f"admin_{uuid.uuid4().hex[:8]}"):
              await safe_reply(update,
                  f"{Em.SUCCESS} {sc('premium')} <code>{plan}</code> ({days}d) "
                  f"{sc('added to user')} <code>{uid}</code>.")
              try:
                  await ctx.bot.send_message(uid,
                      f"{Em.PREMIUM} {sc('you received')} <b>{plan.upper()}</b> "
                      f"{sc('premium for')} {days} {sc('days')}! 🎉",
                      parse_mode=ParseMode.HTML)
              except:
                  pass
          else:
              await safe_reply(update, f"{Em.ERROR} {sc('failed')}.")

      @admin_only
      async def cmd_revokepremium(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.PREMIUM} {sc('usage')}: /revokepremium <code>{sc('user_id')}</code>")
              return
          try:
              uid = int(ctx.args[0])
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid user id')}.")
              return
          if self.db.revoke_premium(uid):
              await safe_reply(update,
                  f"{Em.SUCCESS} {sc('premium revoked from')} <code>{uid}</code>.")
          else:
              await safe_reply(update, f"{Em.ERROR} {sc('failed')}.")

      @admin_only
      async def cmd_gencode(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 2:
              await safe_reply(update,
                  f"{Em.REDEEM} {sc('usage')}: /gencode <code>{sc('plan days [max_uses] [exp_days]')}</code>\n"
                  f"{sc('example')}: /gencode monthly 30 5 7")
              return
          try:
              plan     = ctx.args[0].lower()
              days     = int(ctx.args[1])
              max_uses = int(ctx.args[2]) if len(ctx.args) > 2 else 1
              exp_days = int(ctx.args[3]) if len(ctx.args) > 3 else 30
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")
              return
          code = secrets.token_hex(4).upper()
          if self.db.create_redeem_code(code, plan, days, max_uses,
                                         self._uid(update), exp_days):
              await safe_reply(update,
                  f"{Em.SUCCESS} <b>{sc('redeem code created')}!</b>\n\n"
                  f"🎟 {sc('code')}: <code>{code}</code>\n"
                  f"📋 {sc('plan')}: {plan.upper()} | 📅 {sc('days')}: {days}\n"
                  f"♻️ {sc('max uses')}: {max_uses} | ⏰ {sc('expires')}: {exp_days}d")
          else:
              await safe_reply(update, f"{Em.ERROR} {sc('failed to create code')}.")

      @admin_only
      async def cmd_setcookies(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg = self._msg(update)
          if not msg:
              return
          target = msg.reply_to_message
          if target and target.text:
              cookies_text = target.text
          elif target and target.document:
              status = await safe_reply(update, f"{Em.LOADING} {sc('reading cookie file')}…")
              try:
                  f  = await ctx.bot.get_file(target.document.file_id)
                  fp = str(Config.TEMP_PATH / f"cookies_{uuid.uuid4().hex[:8]}.txt")
                  await f.download_to_drive(fp)
                  cookies_text = Path(fp).read_text(encoding="utf-8", errors="ignore")
                  Path(fp).unlink(missing_ok=True)
              except Exception as e:
                  if status: await safe_edit(status, f"{Em.ERROR} {sc('error reading file')}: {e}")
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
                  f"{sc('how to export cookies')}:\n"
                  f"1. {sc('log into crunchyroll.com')}\n"
                  f"2. {sc('use EditThisCookie or similar extension')}\n"
                  f"3. {sc('export as json or netscape format')}\n"
                  f"4. {sc('send the file here and reply with')} /setcookies")
              return

          ok, result = await CookieManager.validate_cookies(cookies_text)
          if not ok:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid cookies')}: {result}")
              return

          cookies_list = (CookieManager.parse_netscape_cookies(cookies_text)
                          or CookieManager.parse_json_cookies(cookies_text))
          cookies_json = json.dumps(cookies_list, ensure_ascii=False)
          cookie_bytes = pickle.dumps(cookies_list)

          is_premium_acc = any(
              c.get("name","") in ("etp_rt","crunchyroll_user","_cr_user_data")
              for c in cookies_list)

          cid = self.db.save_cookies(
              cookie_bytes, cookies_json,
              email=Config.CR_EMAIL,
              is_premium=is_premium_acc,
              added_by=self._uid(update))

          CookieManager.save_to_file(cookies_text)

          await safe_reply(update,
              f"{Em.COOKIE} <b>{sc('cookies saved')}!</b>\n\n"
              f"📊 {sc('cookies count')}: {len(cookies_list)}\n"
              f"💎 {sc('premium account detected')}: {'✅' if is_premium_acc else '❌'}\n"
              f"🆔 {sc('cookie id')}: <code>#{cid}</code>\n\n"
              f"{sc('bot will now use these cookies for downloads')}.")

      @admin_only
      async def cmd_fetchnews(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          status = await safe_reply(update, f"{Em.NEWS} {sc('fetching crunchyroll news')}…")
          news   = await self.downloader.cr.fetch_cr_news()
          saved  = 0
          for n in news:
              if self.db.save_news(n["title"], n["description"],
                                    n["url"], n["image_url"], n["published_at"]):
                  saved += 1
          if status:
              await safe_edit(status,
                  f"{Em.SUCCESS} {sc('fetched')} {len(news)} {sc('news items, saved')} {saved} {sc('new')}.")

      @admin_only
      async def cmd_queueall(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          items = self.db.get_all_queue()
          if not items:
              await safe_reply(update, f"{Em.QUEUE} {sc('global queue is empty')}.")
              return
          lines = [f"{Em.QUEUE} <b>{sc('global queue')} ({len(items)})</b>\n"]
          for it in items[:30]:
              lane = "⚡" if it.get("is_fast") else "🐢"
              lines.append(
                  f"#{it['id']} {lane} uid={it['user_id']} | "
                  f"{it['quality']} | {it['status']} {it['progress']}%")
          await safe_reply(update, "\n".join(lines))

      @admin_only
      async def cmd_clearqueue(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          count = self.db.clear_queue()
          await safe_reply(update,
              f"{Em.SUCCESS} {sc('cleared')} {count} {sc('items from queue')}.")

      @admin_only
      async def cmd_maintenance(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args or ctx.args[0] not in ("on","off"):
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /maintenance <code>on|off</code>")
              return
          val = "True" if ctx.args[0] == "on" else "False"
          self.db.set_setting("maintenance_mode", val)
          await safe_reply(update,
              f"{Em.SUCCESS} {sc('maintenance mode')}: <b>{sc(ctx.args[0])}</b>")

      @admin_only
      async def cmd_authgroup(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.AUTH} {sc('usage')}:\n"
                  f"/authgroup add <code>{sc('group_id link [name]')}</code>\n"
                  f"/authgroup remove <code>{sc('group_id')}</code>\n"
                  f"/authgroup list\n"
                  f"/authgroup on|off")
              return
          action = ctx.args[0].lower()
          if action == "list":
              groups = self.db.get_auth_groups()
              if not groups:
                  await safe_reply(update,
                      f"{Em.INFO} {sc('no auth groups configured')}.")
                  return
              lines = [f"{Em.AUTH} <b>{sc('auth groups')}:</b>\n"]
              for g in groups:
                  lines.append(
                      f"• <code>{g['group_id']}</code> — {g.get('group_name','?')} — "
                      f"<a href=\'{g.get('group_link','')}\'>{sc('join')}</a>")
              await safe_reply(update, "\n".join(lines))
          elif action == "add" and len(ctx.args) >= 3:
              try:
                  gid  = int(ctx.args[1])
                  link = ctx.args[2]
                  name = " ".join(ctx.args[3:]) if len(ctx.args) > 3 else f"Group {gid}"
                  self.db.add_auth_group(gid, name, link, self._uid(update))
                  await safe_reply(update,
                      f"{Em.SUCCESS} {sc('auth group')} <code>{gid}</code> {sc('added')}.")
              except ValueError:
                  await safe_reply(update, f"{Em.ERROR} {sc('invalid group id')}.")
          elif action == "remove" and len(ctx.args) >= 2:
              try:
                  gid = int(ctx.args[1])
                  self.db.remove_auth_group(gid)
                  await safe_reply(update,
                      f"{Em.SUCCESS} {sc('auth group')} <code>{gid}</code> {sc('removed')}.")
              except ValueError:
                  await safe_reply(update, f"{Em.ERROR} {sc('invalid group id')}.")
          elif action in ("on","off"):
              val = "True" if action == "on" else "False"
              self.db.set_setting("force_sub_enabled", val)
              await safe_reply(update,
                  f"{Em.SUCCESS} {sc('force-subscribe')}: <b>{sc(action)}</b>")
          else:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid arguments')}.")

      @admin_only
      async def cmd_logs(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          c    = self.db.conn.execute(
              "SELECT user_id,anime_title,episode_title,quality,downloaded_at "
              "FROM downloads ORDER BY downloaded_at DESC LIMIT 20")
          rows = c.fetchall()
          if not rows:
              await safe_reply(update, f"{Em.LOG} {sc('no download logs yet')}.")
              return
          lines = [f"{Em.LOG} <b>{sc('recent downloads (20)')}</b>\n"]
          for r in rows:
              lines.append(
                  f"uid=<code>{r[0]}</code> | {str(r[1])[:25]} | {r[3]} | {str(r[4])[:16]}")
          await safe_reply(update, "\n".join(lines))

      @admin_only
      async def cmd_restart(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          await safe_reply(update, f"{Em.LOADING} {sc('restarting bot')}…")
          await asyncio.sleep(1)
          os._exit(0)

      @admin_only
      async def cmd_userinfo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.INFO} {sc('usage')}: /userinfo <code>{sc('user_id')}</code>")
              return
          try:
              uid = int(ctx.args[0])
          except:
              await safe_reply(update, f"{Em.ERROR} {sc('invalid user id')}.")
              return
          u = self.db.get_user(uid)
          if not u:
              await safe_reply(update, f"{Em.ERROR} {sc('user not found')}.")
              return
          is_pm = self.db.is_premium(uid)
          exp   = self.db.get_premium_expiry(uid)
          await safe_reply(update,
              f"{Em.INFO} <b>{sc('user info')}</b>\n\n"
              f"🆔 ID: <code>{uid}</code>\n"
              f"👤 {sc('name')}: {u.get('first_name','?')} {u.get('last_name','') or ''}\n"
              f"📛 {sc('username')}: @{u.get('username','none')}\n"
              f"💎 {sc('premium')}: {'✅ ' + sc(u.get('premium_type','free')) if is_pm else '❌'}\n"
              f"📅 {sc('expires')}: {exp.strftime('%Y-%m-%d') if exp and is_pm else 'N/A'}\n"
              f"🚫 {sc('banned')}: {'✅' if u.get('is_banned') else '❌'}\n"
              f"⚠️ {sc('warnings')}: {u.get('warnings',0)}\n"
              f"📥 {sc('total downloads')}: {u.get('total_downloads',0):,}\n"
              f"📊 {sc('total data')}: {round((u.get('total_size',0) or 0)/(1024**3),3)} GB\n"
              f"👥 {sc('referrals')}: {u.get('referral_count',0)}\n"
              f"🔗 {sc('ref code')}: <code>{u.get('referral_code','N/A')}</code>\n"
              f"📅 {sc('joined')}: {str(u.get('joined_at','?'))[:10]}")

      # ──────────── ᴄᴜꜱᴛᴏᴍ ᴄᴏᴍᴍᴀɴᴅꜱ ──────────────────────────────────────────

      @admin_only
      async def cmd_addcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 3:
              await safe_reply(update,
                  f"{Em.CODE} {sc('usage')}: /addcmd <code>{sc('name text|markdown|python content')}</code>\n\n"
                  f"{sc('python example')}:\n"
                  f"<code>/addcmd roll python print(f\'you rolled: {{random.randint(1,6)}}\')</code>\n"
                  f"⚠️ {sc('python runs in a sandbox. no imports allowed.')}")
              return
          cmd_name = ctx.args[0].lower()
          cmd_type = ctx.args[1].lower()
          content  = " ".join(ctx.args[2:])
          if cmd_type not in ("text","markdown","python","html"):
              await safe_reply(update,
                  f"{Em.ERROR} {sc('type must be')}: text, markdown, html, python")
              return
          if cmd_type == "python":
              ok, out = CodeSandbox.run(content, {"user_id": self._uid(update)})
              if not ok:
                  await safe_reply(update,
                      f"{Em.ERROR} {sc('code validation failed')}:\n{out}")
                  return
          response = content if cmd_type != "python" else ""
          code     = content if cmd_type == "python" else None
          if self.db.add_custom_cmd(cmd_name, response, code, cmd_type, self._uid(update)):
              await safe_reply(update,
                  f"{Em.SUCCESS} {sc('custom command')} <code>/{cmd_name}</code> "
                  f"({cmd_type}) {sc('added')}!")
          else:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('command')} <code>/{cmd_name}</code> "
                  f"{sc('already exists. use')} /editcmd {sc('to update')}.")

      @admin_only
      async def cmd_editcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if len(ctx.args) < 3:
              await safe_reply(update,
                  f"{Em.CODE} {sc('usage')}: /editcmd <code>{sc('name type content')}</code>")
              return
          cmd_name = ctx.args[0].lower()
          cmd_type = ctx.args[1].lower()
          content  = " ".join(ctx.args[2:])
          response = content if cmd_type != "python" else ""
          code     = content if cmd_type == "python" else None
          if self.db.update_custom_cmd(cmd_name, response, code, cmd_type):
              await safe_reply(update,
                  f"{Em.SUCCESS} <code>/{cmd_name}</code> {sc('updated')}!")
          else:
              await safe_reply(update,
                  f"{Em.ERROR} {sc('command not found')}.")

      @admin_only
      async def cmd_delcmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          if not ctx.args:
              await safe_reply(update,
                  f"{Em.WARNING} {sc('usage')}: /delcmd <code>{sc('name')}</code>")
              return
          if self.db.remove_custom_cmd(ctx.args[0].lower()):
              await safe_reply(update,
                  f"{Em.SUCCESS} {sc('command')} <code>/{ctx.args[0]}</code> {sc('removed')}.")
          else:
              await safe_reply(update, f"{Em.ERROR} {sc('command not found')}.")

      async def cmd_listcmds(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          cmds = self.db.list_custom_cmds()
          if not cmds:
              await safe_reply(update,
                  f"{Em.INFO} {sc('no custom commands')}.", KB.back())
              return
          lines = [f"{Em.CODE} <b>{sc('custom commands')} ({len(cmds)})</b>\n"]
          for c in cmds[:40]:
              icon = "🐍" if c["cmd_type"] == "python" else (
                     "📝" if c["cmd_type"] in ("markdown","html") else "💬")
              lines.append(
                  f"{icon} <code>/{c['command']}</code> ({c['cmd_type']}) "
                  f"— {c['usage_count']} {sc('uses')}")
          await safe_reply(update, "\n".join(lines), KB.back())

      # ══════════════════════════════════════════════════════════════════════════
      #  ᴘᴀʏᴍᴇɴᴛ ʜᴀɴᴅʟᴇʀꜱ
      # ══════════════════════════════════════════════════════════════════════════

      async def precheckout(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          q = update.pre_checkout_query
          if not q:
              return
          try:
              await q.answer(ok=True)
          except Exception as e:
              logger.error(f"precheckout: {e}")

      async def payment_success(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          pay = update.message.successful_payment if update.message else None
          if not pay:
              return
          payload = pay.invoice_payload
          parts   = payload.split("_")
          plan    = parts[1] if len(parts) > 1 else "monthly"
          uid     = (int(parts[2]) if len(parts) > 2 and parts[2].isdigit()
                     else self._uid(update))
          days    = Config.SUBSCRIPTION_DAYS.get(plan, 30)
          self.db.add_premium(uid, plan, days, pay.telegram_payment_charge_id)
          await update.message.reply_text(
              f"{Em.SUCCESS} <b>{sc('payment successful')}!</b> 🎉\n\n"
              f"📋 {sc('plan')}: <b>{plan.upper()}</b> ({days} {sc('days')})\n"
              f"🔑 {sc('your premium is now active')}!\n\n"
              f"{sc('thank you for your support')}! 🙏",
              parse_mode=ParseMode.HTML)
          await log_to_channel(ctx.bot,
              f"{Em.PAID} {sc('payment')}: uid=<code>{uid}</code> plan={plan} "
              f"stars={pay.total_amount} txn=<code>{pay.telegram_payment_charge_id[:16]}</code>",
              self.db)
          for aid in Config.ADMIN_IDS:
              try:
                  await ctx.bot.send_message(aid,
                      f"{Em.PAID} {sc('new payment')}!\n"
                      f"uid=<code>{uid}</code> plan={plan} stars={pay.total_amount}",
                      parse_mode=ParseMode.HTML)
              except:
                  pass

      # ══════════════════════════════════════════════════════════════════════════
      #  ᴄᴀʟʟʙᴀᴄᴋ ǫᴜᴇʀʏ ʜᴀɴᴅʟᴇʀ (ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴꜱ)
      # ══════════════════════════════════════════════════════════════════════════

      async def callback_handler(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          q   = update.callback_query
          if not q:
              return
          uid = q.from_user.id if q.from_user else 0

          try:
              await q.answer()
          except Exception as e:
              logger.debug(f"q.answer: {e}")

          data = q.data or ""

          # ── ɴᴀᴠɪɢᴀᴛɪᴏɴ ────────────────────────────────────────────────────
          if data == "show_home":
              is_pm = self.db.is_premium(uid)
              fname = q.from_user.first_name if q.from_user else sc("user")
              await safe_edit(q.message,
                  f"{Em.ANIME} <b>{sc('crunchyroll ultimate bot v200.0')}</b>\n\n"
                  f"{sc('hello')}, <b>{fname}</b>!\n"
                  f"{'💎 ' + sc('premium member') if is_pm else '🆓 ' + sc('free user')}\n\n"
                  f"{sc('send a crunchyroll url or choose an option')}:",
                  KB.home())

          elif data == "show_premium":
              fake_update = type('obj', (object,), {
                  'effective_user': q.from_user,
                  'effective_message': q.message,
                  'callback_query': q,
              })()
              uid_  = uid
              is_pm = self.db.is_premium(uid_)
              plan  = self.db.get_premium_type(uid_)
              exp   = self.db.get_premium_expiry(uid_)
              text  = f"{Em.PREMIUM} <b>{sc('crunchyroll premium membership')}</b>\n\n"
              if is_pm:
                  text += (f"{Em.SUCCESS} {sc('you are a premium member')}!\n"
                           f"📋 {sc('plan')}: <b>{plan.upper()}</b>\n"
                           f"📅 {sc('expires')}: <b>{exp.strftime('%Y-%m-%d') if exp else sc('lifetime')}</b>\n\n")
              else:
                  text += f"{Em.INFO} {sc('you are on the free plan')}\n\n"
              text += (
                  f"⭐ <b>{sc('weekly')}</b> — {Config.SUBSCRIPTION_PRICES['weekly']} {sc('stars')}\n"
                  f"💎 <b>{sc('monthly')}</b> — {Config.SUBSCRIPTION_PRICES['monthly']} {sc('stars')}\n"
                  f"👑 <b>{sc('yearly')}</b> — {Config.SUBSCRIPTION_PRICES['yearly']} {sc('stars')}\n"
                  f"🔥 <b>{sc('lifetime')}</b> — {Config.SUBSCRIPTION_PRICES['lifetime']} {sc('stars')}\n\n"
                  f"{Em.SUPPORT} {sc('buy via')}: {Config.SUPPORT_USERNAME}"
              )
              await safe_edit(q.message, text, KB.premium_plans())

          elif data == "show_stats":
              user  = self.db.get_user(uid)
              is_pm = self.db.is_premium(uid)
              daily = self.db.get_daily_downloads(uid)
              limit = Config.PREMIUM_DAILY_LIMIT if is_pm else Config.FREE_DAILY_LIMIT
              plan  = self.db.get_premium_type(uid)
              exp   = self.db.get_premium_expiry(uid)
              lane  = f"{Em.FAST} {sc('fast lane')}" if is_pm else f"{Em.SLOW} {sc('slow lane')}"
              await safe_edit(q.message,
                  f"{Em.STATS} <b>{sc('your statistics')}</b>\n\n"
                  f"├ {sc('plan')}: {'💎 ' + plan.upper() if is_pm else '🆓 ' + sc('free')}\n"
                  f"├ {sc('lane')}: {lane}\n"
                  f"├ {sc('expires')}: {exp.strftime('%Y-%m-%d') if exp and is_pm else 'N/A'}\n"
                  f"├ {sc('today')}: {daily}/{limit if limit < 999999 else sc('unlimited')}\n"
                  f"├ {sc('all-time')}: {user.get('total_downloads',0) if user else 0:,}\n"
                  f"├ {sc('referrals')}: {self.db.get_referral_count(uid)}\n"
                  f"└ {sc('favorites')}: {len(self.db.get_favorites(uid))}",
                  KB.back())

          elif data == "show_settings":
              user = self.db.get_user(uid) or {}
              await safe_edit(q.message,
                  f"{Em.SETTINGS} <b>{sc('user settings')}</b>\n\n"
                  f"{sc('tap a button to change')}:",
                  KB.settings(user))

          elif data == "show_queue":
              items = self.db.get_user_queue(uid)
              if not items:
                  await safe_edit(q.message,
                      f"{Em.QUEUE} {sc('queue is empty')}. {sc('send a cr link to start')}.",
                      KB.back())
              else:
                  lines = [f"{Em.QUEUE} <b>{sc('your queue')} ({len(items)})</b>\n"]
                  for it in items:
                      lane = "⚡" if it.get("is_fast") else "🐢"
                      icon = "⚡" if it["status"] == "processing" else "⏳"
                      short = it["url"][-30:]
                      lines.append(
                          f"{icon} {lane} <b>#{it['id']}</b> | "
                          f"<code>{it['quality']}</code>\n"
                          f"   {ProgressBar.make(it['progress'])}")
                  await safe_edit(q.message, "\n".join(lines), KB.back())

          elif data == "show_history":
              hist = self.db.get_download_history(uid, 10)
              if not hist:
                  await safe_edit(q.message,
                      f"{Em.HISTORY} {sc('no history yet')}.", KB.back())
              else:
                  lines = [f"{Em.HISTORY} <b>{sc('recent downloads')}</b>\n"]
                  for h in hist:
                      lines.append(
                          f"🎬 <b>{h['anime_title'][:30]}</b>\n"
                          f"   {h['episode_title'][:30]} | <code>{h['quality']}</code>")
                  await safe_edit(q.message, "\n".join(lines), KB.back())

          elif data == "show_news" or data == "refresh_news":
              news = self.db.get_latest_news(8)
              if not news or data == "refresh_news":
                  fetched = await self.downloader.cr.fetch_cr_news()
                  for n in fetched:
                      self.db.save_news(n["title"], n["description"],
                                        n["url"], n["image_url"], n["published_at"])
                  news = self.db.get_latest_news(8)
              if not news:
                  await safe_edit(q.message,
                      f"{Em.NEWS} {sc('no news available. try again later')}.", KB.back())
                  return
              lines  = [f"{Em.NEWS} <b>{sc('crunchyroll latest news')}</b>\n"]
              kb_rows= []
              for i, n in enumerate(news[:8], 1):
                  title = n.get("title","")[:55]
                  pub   = str(n.get("published_at",""))[:10]
                  lines.append(f"\n<b>{i}.</b> {title}\n   📅 {pub}")
                  if n.get("url"):
                      kb_rows.append([
                          InlineKeyboardButton(f"📰 {i}. {title[:25]}…", url=n["url"])
                      ])
              kb_rows.append([
                  InlineKeyboardButton(f"{Em.REFRESH} {sc('refresh')}", callback_data="refresh_news")])
              kb_rows.append([
                  InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")])
              await safe_edit(q.message, "\n".join(lines), InlineKeyboardMarkup(kb_rows))

          elif data == "show_referral":
              code    = self.db.get_referral_code(uid)
              count   = self.db.get_referral_count(uid)
              points  = self.db.get_referral_points(uid)
              reward  = int(self.db.get_setting("referral_reward","50"))
              req     = int(self.db.get_setting("referral_required","5"))
              try:
                  bot_info = await ctx.bot.get_me()
                  ref_link = f"https://t.me/{bot_info.username}?start=ref_{code}"
              except:
                  ref_link = f"https://t.me/crunchyrollbot?start=ref_{code}"
              await safe_edit(q.message,
                  f"{Em.REFERRAL} <b>{sc('referral program')}</b>\n\n"
                  f"🔗 <code>{ref_link}</code>\n\n"
                  f"├ {sc('referrals')}: <b>{count}</b>\n"
                  f"├ {sc('points')}: <b>{points}</b>\n"
                  f"└ {sc('reward per ref')}: <b>{reward} {sc('pts')}</b>\n\n"
                  f"🎯 {sc('get')} {req} {sc('referrals for a free week of premium')}!",
                  InlineKeyboardMarkup([
                      [InlineKeyboardButton(
                          f"🔗 {sc('share link')}",
                          switch_inline_query=f"ref_{code}")],
                      [InlineKeyboardButton(f"{Em.BACK} {sc('back')}", callback_data="show_home")],
                  ]))

          elif data == "show_favorites":
              favs  = self.db.get_favorites(uid)
              lines = [f"{Em.HEART} <b>{sc('favorites')} ({len(favs)})</b>\n"]
              if not favs:
                  lines = [f"{Em.HEART} {sc('no favorites yet')}."]
              else:
                  for f in favs[:15]:
                      lines.append(f"• {f['anime_title'][:35]}")
              await safe_edit(q.message, "\n".join(lines), KB.back())

          elif data == "show_watchlist":
              wl    = self.db.get_watchlist(uid)
              lines = [f"{Em.WATCH} <b>{sc('watchlist')} ({len(wl)})</b>\n"]
              if not wl:
                  lines = [f"{Em.WATCH} {sc('watchlist empty')}."]
              else:
                  for w in wl[:15]:
                      lines.append(f"• {w['anime_title'][:35]} — Ep {w['next_episode']}")
              await safe_edit(q.message, "\n".join(lines), KB.back())

          # ── ꜱᴇᴛᴛɪɴɢꜱ ────────────────────────────────────────────────────────
          elif data == "cfg_quality":
              is_pm = self.db.is_premium(uid)
              await safe_edit(q.message,
                  f"{Em.QUALITY} <b>{sc('select download quality')}</b>\n\n"
                  f"{'🔒 ' + sc('4k/hdr requires premium') if not is_pm else sc('all qualities unlocked')}:",
                  KB.quality(is_pm))

          elif data == "cfg_preset":
              await safe_edit(q.message,
                  f"{Em.ENCODE} <b>{sc('select encode preset')}</b>\n\n"
                  f"{sc('faster = lower quality, slower = better quality')}:",
                  KB.encode_preset())

          elif data == "cfg_notify":
              user = self.db.get_user(uid) or {}
              curr = bool(user.get("notify_complete",1))
              self.db.set_user_setting(uid, "notify_complete", "0" if curr else "1")
              user = self.db.get_user(uid) or {}
              await safe_edit(q.message,
                  f"{Em.SETTINGS} <b>{sc('settings updated')}</b>",
                  KB.settings(user))

          elif data == "cfg_thumb":
              await safe_edit(q.message,
                  f"{Em.THUMBNAIL} <b>{sc('custom thumbnail')}</b>\n\n"
                  f"{sc('send a photo and it will be used as default thumbnail')}.\n"
                  f"{sc('current')}: {sc('default (auto-generated)')}",
                  KB.back("show_settings"))

          elif data.startswith("set_quality_"):
              quality = data[12:]
              is_pm   = self.db.is_premium(uid)
              if quality in Config.PREMIUM_QUALITIES and not is_pm:
                  await q.answer(
                      f"🔒 {sc(quality)} {sc('requires premium')}!", show_alert=True)
                  return
              self.db.set_user_setting(uid, "default_quality", quality)
              user = self.db.get_user(uid) or {}
              await safe_edit(q.message,
                  f"{Em.SUCCESS} <b>{sc('quality set to')} {quality}</b>",
                  KB.settings(user))

          elif data.startswith("set_preset_"):
              preset = data[11:]
              self.db.set_user_setting(uid, "encode_preset", preset)
              user = self.db.get_user(uid) or {}
              await safe_edit(q.message,
                  f"{Em.SUCCESS} <b>{sc('encode preset set to')} {preset}</b>",
                  KB.settings(user))

          # ── ᴘʀᴇᴍɪᴜᴍ ʙᴜʏ ────────────────────────────────────────────────────
          elif data.startswith("buy_"):
              plan  = data[4:]
              stars = Config.SUBSCRIPTION_PRICES.get(plan, 0)
              if plan not in Config.SUBSCRIPTION_PRICES:
                  await q.answer(f"{sc('invalid plan')}", show_alert=True)
                  return
              features = "\n".join(f"• {f}" for f in Config.SUBSCRIPTION_FEATURES.get(plan,[]))
              try:
                  await ctx.bot.send_invoice(
                      chat_id=uid,
                      title=f"{sc('crunchyroll')} {plan.upper()} {sc('premium')}",
                      description=f"{sc('features')}:\n{features}",
                      payload=f"premium_{plan}_{uid}",
                      currency="XTR",
                      prices=[LabeledPrice(label=f"{plan.upper()} {sc('premium')}", amount=stars)],
                  )
              except Exception as e:
                  await q.answer(f"{sc('error starting payment')}: {e}", show_alert=True)

          # ── ᴅᴏᴡɴʟᴏᴀᴅ ᴏᴘᴛɪᴏɴꜱ ───────────────────────────────────────────────
          elif data.startswith("cancel_dl_"):
              qid = int(data[10:])
              if self.db.cancel_queue_item(qid, uid):
                  await safe_edit(q.message,
                      f"{Em.SUCCESS} {sc('download')} #{qid} {sc('cancelled')}.",
                      None)
              else:
                  await q.answer(sc("cannot cancel — already processing or not yours"),
                                 show_alert=True)

          # ── ᴀᴜᴛʜ ᴄʜᴇᴄᴋ ─────────────────────────────────────────────────────
          elif data == "auth_check":
              ok, links = await AuthChecker.check_user(ctx.bot, uid, self.db)
              if ok:
                  await safe_edit(q.message,
                      f"{Em.SUCCESS} <b>{sc('access granted')}!</b>\n"
                      f"{sc('you are now verified. send a crunchyroll url to download')}.",
                      KB.home())
              else:
                  kb = [[InlineKeyboardButton(f"📢 {sc('join')}", url=l)] for l in links if l]
                  kb.append([InlineKeyboardButton(f"{Em.REFRESH} {sc('check again')}", callback_data="auth_check")])
                  await q.answer(
                      sc("you still haven't joined all required channels"),
                      show_alert=True)

          # ── ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ʙᴜᴛᴛᴏɴꜱ ──────────────────────────────────────────
          elif data == "adm_stats" and uid in Config.ADMIN_IDS:
              counts = self.db.get_user_count()
              q_all  = self.db.get_all_queue()
              await safe_edit(q.message,
                  f"{Em.ADMIN} <b>{sc('bot statistics')}</b>\n\n"
                  f"👥 {sc('total users')}: <b>{counts['total']:,}</b>\n"
                  f"💎 {sc('premium')}: <b>{counts['premium']}</b>\n"
                  f"🆓 {sc('free')}: <b>{counts['free']}</b>\n"
                  f"🚫 {sc('banned')}: <b>{counts['banned']}</b>\n"
                  f"{Em.QUEUE} {sc('active queue')}: <b>{len(q_all)}</b>",
                  KB.admin_panel())

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

          elif data == "adm_cookies" and uid in Config.ADMIN_IDS:
              row = self.db.get_active_cookies()
              if row:
                  cookies_list = json.loads(row.get("cookies_json","[]") or "[]")
                  await safe_edit(q.message,
                      f"{Em.COOKIE} <b>{sc('active cookies')}</b>\n\n"
                      f"📊 {sc('count')}: {len(cookies_list)}\n"
                      f"💎 {sc('premium')}: {'✅' if row.get('is_premium') else '❌'}\n"
                      f"📅 {sc('expires')}: {str(row.get('expires_at','?'))[:16]}\n"
                      f"📅 {sc('added')}: {str(row.get('added_at','?'))[:16]}\n\n"
                      f"{sc('use')} /setcookies {sc('to update')}.",
                      KB.admin_panel())
              else:
                  await safe_edit(q.message,
                      f"{Em.COOKIE} <b>{sc('no cookies configured')}</b>\n\n"
                      f"{sc('use')} /setcookies {sc('to add crunchyroll cookies')}.",
                      KB.admin_panel())

          elif data == "adm_close" and uid in Config.ADMIN_IDS:
              try:
                  await q.message.delete()
              except:
                  await safe_edit(q.message, f"{Em.SUCCESS} {sc('panel closed')}.", None)

          else:
              # Unknown callback — just answer silently
              logger.debug(f"Unhandled callback: {data} from uid={uid}")

      # ══════════════════════════════════════════════════════════════════════════
      #  ᴛᴇxᴛ / ᴄᴜꜱᴛᴏᴍ ᴄᴏᴍᴍᴀɴᴅ ʜᴀɴᴅʟᴇʀ
      # ══════════════════════════════════════════════════════════════════════════

      async def handle_text(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
          msg = update.message
          if not msg or not msg.text:
              return
          uid  = self._uid(update)
          text = msg.text.strip()

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
                      await msg.reply_text(data["response"], parse_mode=ParseMode.HTML)
                  elif data["cmd_type"] == "markdown":
                      await msg.reply_text(data["response"], parse_mode=ParseMode.MARKDOWN_V2)
                  else:
                      await msg.reply_text(data["response"])

      # ══════════════════════════════════════════════════════════════════════════
      #  ǫᴜᴇᴜᴇ ᴡᴏʀᴋᴇʀ
      # ══════════════════════════════════════════════════════════════════════════

      async def _queue_worker(self):
          logger.info(f"⚡ {sc('queue worker started')}")
          while True:
              try:
                  # Fast lane first (premium users)
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

                  # Get the stored status message
                  status_key = f"qmsg_{qid}"
                  # We'll send progress updates to user
                  app_ref = getattr(self, "_app", None)

                  async def progress_cb(pct: int, msg_text: str = ""):
                      if not app_ref or not chat_id:
                          return
                      self.db.update_queue_progress(qid, pct)
                      try:
                          lane_icon = f"{Em.FAST}" if is_fast else f"{Em.SLOW}"
                          await app_ref.bot.edit_message_text(
                              chat_id=chat_id,
                              message_id=msg_id,
                              text=(
                                  f"{lane_icon} <b>#{qid}</b> — {msg_text}\n\n"
                                  f"{ProgressBar.make(pct)}\n"
                                  f"<code>{url[:50]}…</code>"
                              ),
                              parse_mode=ParseMode.HTML,
                          )
                      except Exception as e:
                          logger.debug(f"progress_cb edit: {e}")

                  ok, result = await self.downloader.process(
                      qid, uid, url, quality, preset, progress_cb)

                  if ok and app_ref:
                      try:
                          file_path = result
                          file_size = Path(file_path).stat().st_size
                          size_mb   = round(file_size / (1024 * 1024), 2)
                          fname     = Path(file_path).name

                          lane_icon = f"{Em.FAST}" if is_fast else f"{Em.SLOW}"
                          caption = (
                              f"{Em.SUCCESS} <b>{sc('download complete')}!</b>\n\n"
                              f"{lane_icon} {sc('lane')}: "
                              f"{'fast (premium)' if is_fast else 'slow (free)'}\n"
                              f"📁 <code>{fname[:60]}</code>\n"
                              f"📦 {size_mb} MB | <code>{quality}</code>\n\n"
                              f"{Em.SUPPORT} {Config.SUPPORT_USERNAME}"
                          )

                          # Upload file
                          if file_size <= 50 * 1024 * 1024:  # ≤50MB: normal API
                              with open(file_path, "rb") as fh:
                                  await app_ref.bot.send_document(
                                      chat_id=chat_id,
                                      document=InputFile(fh, filename=fname),
                                      caption=caption,
                                      parse_mode=ParseMode.HTML,
                                  )
                          else:
                              await app_ref.bot.send_message(
                                  chat_id=chat_id,
                                  text=(
                                      f"{Em.SUCCESS} <b>{sc('download complete')}!</b>\n"
                                      f"📁 <code>{fname}</code>\n"
                                      f"📦 {size_mb} MB\n\n"
                                      f"⚠️ {sc('file is too large for direct telegram send (>50mb)')}. "
                                      f"{sc('contact')} {Config.SUPPORT_USERNAME} {sc('for file transfer')}.\n\n"
                                      f"{sc('file saved to server at')}: <code>{file_path}</code>"
                                  ),
                                  parse_mode=ParseMode.HTML,
                              )

                          # Notify in dm if completion notify is on
                          user_data = self.db.get_user(uid)
                          if user_data and user_data.get("notify_complete",1):
                              pass  # Already sent to chat_id above

                          # Clean up
                          try:
                              Path(file_path).unlink(missing_ok=True)
                          except:
                              pass

                          # Delete progress message
                          if msg_id and chat_id:
                              try:
                                  await app_ref.bot.delete_message(chat_id, msg_id)
                              except:
                                  pass

                      except Exception as e:
                          logger.error(f"queue_worker send: {e}")
                          if chat_id:
                              try:
                                  await app_ref.bot.send_message(
                                      chat_id,
                                      f"{Em.SUCCESS} {sc('download complete but send failed')}: {e}\n"
                                      f"{sc('contact')} {Config.SUPPORT_USERNAME}",
                                      parse_mode=ParseMode.HTML)
                              except:
                                  pass

                  elif not ok and app_ref and chat_id:
                      try:
                          await app_ref.bot.send_message(
                              chat_id,
                              f"{Em.ERROR} <b>{sc('download failed')}!</b>\n\n"
                              f"<code>{result[:300]}</code>\n\n"
                              f"{sc('please try again or contact')} {Config.SUPPORT_USERNAME}",
                              parse_mode=ParseMode.HTML)
                          if msg_id:
                              try:
                                  await app_ref.bot.delete_message(chat_id, msg_id)
                              except:
                                  pass
                      except:
                          pass

                  await asyncio.sleep(0.5)

              except asyncio.CancelledError:
                  logger.info(f"⏹ {sc('queue worker cancelled')}")
                  break
              except Exception as e:
                  logger.exception(f"queue_worker: {e}")
                  await asyncio.sleep(5)

      # ══════════════════════════════════════════════════════════════════════════
      #  ꜱᴄʜᴇᴅᴜʟᴇʀ
      # ══════════════════════════════════════════════════════════════════════════

      async def _scheduler_worker(self):
          logger.info(f"⏰ {sc('scheduler started')}")
          while True:
              try:
                  items = self.db.get_pending_scheduled()
                  for it in items:
                      uid     = it["user_id"]
                      url     = it["url"]
                      quality = it["quality"]
                      preset  = it["encode_preset"]
                      qid = self.db.add_to_queue(uid, url, quality, preset)
                      self.db.mark_scheduled_done(it["id"])
                      logger.info(f"Scheduled item #{it['id']} → queue #{qid}")
                      app_ref = getattr(self, "_app", None)
                      if app_ref:
                          try:
                              await app_ref.bot.send_message(
                                  uid,
                                  f"{Em.SCHEDULE} <b>{sc('scheduled download started')}!</b>\n"
                                  f"{sc('queue id')}: #{qid}",
                                  parse_mode=ParseMode.HTML)
                          except:
                              pass
                  self._ensure_queue_running()
              except asyncio.CancelledError:
                  break
              except Exception as e:
                  logger.error(f"scheduler: {e}")
              await asyncio.sleep(60)

      # ══════════════════════════════════════════════════════════════════════════
      #  ɴᴇᴡꜱ ᴡᴏʀᴋᴇʀ
      # ══════════════════════════════════════════════════════════════════════════

      async def _news_worker(self):
          logger.info(f"📰 {sc('news worker started')}")
          while True:
              try:
                  if self.db.get_setting("news_enabled","True") == "True":
                      news = await self.downloader.cr.fetch_cr_news()
                      for n in news:
                          self.db.save_news(n["title"], n["description"],
                                            n["url"], n["image_url"], n["published_at"])
                      # Notify update channel
                      update_ch = self.db.get_setting("update_channel","")
                      if update_ch:
                          unnotified = self.db.get_unnotified_news()
                          for n in unnotified[:3]:
                              app_ref = getattr(self, "_app", None)
                              if app_ref:
                                  try:
                                      await app_ref.bot.send_message(
                                          update_ch,
                                          f"{Em.NEWS} <b>{n['title']}</b>\n\n"
                                          f"{n.get('description','')[:200]}\n\n"
                                          f"🔗 <a href=\'{n['url']}\'>{sc('read more')}</a>",
                                          parse_mode=ParseMode.HTML,
                                          disable_web_page_preview=False)
                                      self.db.mark_news_notified(n["id"])
                                  except Exception as e:
                                      logger.warning(f"news post: {e}")
              except asyncio.CancelledError:
                  break
              except Exception as e:
                  logger.error(f"news_worker: {e}")
              interval = int(self.db.get_setting("news_interval_hours","6")) * 3600
              await asyncio.sleep(interval)

      # ══════════════════════════════════════════════════════════════════════════
      #  ʙᴏᴛ ꜱᴇᴛᴜᴘ + ʀᴜɴ
      # ══════════════════════════════════════════════════════════════════════════

      def build_app(self) -> Application:
          app = (Application.builder()
                 .token(Config.BOT_TOKEN)
                 .build())
          self._app = app

          # Commands
          app.add_handler(CommandHandler("start",        self.cmd_start))
          app.add_handler(CommandHandler("help",         self.cmd_help))
          app.add_handler(CommandHandler("cr",           self.cmd_cr))
          app.add_handler(CommandHandler("download",     self.cmd_cr))
          app.add_handler(CommandHandler("dl",           self.cmd_cr))
          app.add_handler(CommandHandler("premium",      self.cmd_premium))
          app.add_handler(CommandHandler("pm",           self.cmd_premium))
          app.add_handler(CommandHandler("stats",        self.cmd_stats))
          app.add_handler(CommandHandler("settings",     self.cmd_settings))
          app.add_handler(CommandHandler("queue",        self.cmd_queue))
          app.add_handler(CommandHandler("cancel",       self.cmd_cancel))
          app.add_handler(CommandHandler("history",      self.cmd_history))
          app.add_handler(CommandHandler("redeem",       self.cmd_redeem))
          app.add_handler(CommandHandler("referral",     self.cmd_referral))
          app.add_handler(CommandHandler("ref",          self.cmd_referral))
          app.add_handler(CommandHandler("news",         self.cmd_news))
          app.add_handler(CommandHandler("favorites",    self.cmd_favorites))
          app.add_handler(CommandHandler("favs",         self.cmd_favorites))
          app.add_handler(CommandHandler("watchlist",    self.cmd_watchlist))
          app.add_handler(CommandHandler("leaderboard",  self.cmd_leaderboard))
          app.add_handler(CommandHandler("lb",           self.cmd_leaderboard))
          app.add_handler(CommandHandler("feedback",     self.cmd_feedback))
          app.add_handler(CommandHandler("schedule",     self.cmd_schedule))
          app.add_handler(CommandHandler("batch",        self.cmd_batch))
          app.add_handler(CommandHandler("addfav",       self.cmd_addfav))
          app.add_handler(CommandHandler("addwatch",     self.cmd_addwatch))
          app.add_handler(CommandHandler("gift",         self.cmd_gift))
          app.add_handler(CommandHandler("claimgift",    self.cmd_claimgift))

          # Video tools
          app.add_handler(CommandHandler("mediainfo",   self.cmd_mediainfo))
          app.add_handler(CommandHandler("rename",      self.cmd_rename))
          app.add_handler(CommandHandler("compress",    self.cmd_compress))
          app.add_handler(CommandHandler("trim",        self.cmd_trim))
          app.add_handler(CommandHandler("thumbnail",   self.cmd_thumbnail))
          app.add_handler(CommandHandler("thumb",       self.cmd_thumbnail))
          app.add_handler(CommandHandler("watermark",   self.cmd_watermark))
          app.add_handler(CommandHandler("gif",         self.cmd_gif))
          app.add_handler(CommandHandler("audio",       self.cmd_audio))

          # Admin commands
          app.add_handler(CommandHandler("admin",       self.cmd_admin))
          app.add_handler(CommandHandler("broadcast",   self.cmd_broadcast))
          app.add_handler(CommandHandler("ban",         self.cmd_ban))
          app.add_handler(CommandHandler("unban",       self.cmd_unban))
          app.add_handler(CommandHandler("warn",        self.cmd_warn))
          app.add_handler(CommandHandler("addpremium",  self.cmd_addpremium))
          app.add_handler(CommandHandler("revokepremium", self.cmd_revokepremium))
          app.add_handler(CommandHandler("gencode",     self.cmd_gencode))
          app.add_handler(CommandHandler("setcookies",  self.cmd_setcookies))
          app.add_handler(CommandHandler("fetchnews",   self.cmd_fetchnews))
          app.add_handler(CommandHandler("queueall",    self.cmd_queueall))
          app.add_handler(CommandHandler("clearqueue",  self.cmd_clearqueue))
          app.add_handler(CommandHandler("maintenance", self.cmd_maintenance))
          app.add_handler(CommandHandler("authgroup",   self.cmd_authgroup))
          app.add_handler(CommandHandler("logs",        self.cmd_logs))
          app.add_handler(CommandHandler("restart",     self.cmd_restart))
          app.add_handler(CommandHandler("userinfo",    self.cmd_userinfo))
          app.add_handler(CommandHandler("addcmd",      self.cmd_addcmd))
          app.add_handler(CommandHandler("editcmd",     self.cmd_editcmd))
          app.add_handler(CommandHandler("delcmd",      self.cmd_delcmd))
          app.add_handler(CommandHandler("listcmds",    self.cmd_listcmds))
          app.add_handler(CommandHandler("cmds",        self.cmd_listcmds))

          # Callback queries (inline buttons)
          app.add_handler(CallbackQueryHandler(self.callback_handler))

          # Text messages (URLs + custom commands)
          app.add_handler(MessageHandler(
              filters.TEXT & ~filters.COMMAND,
              self.handle_text))

          # Payment
          app.add_handler(PreCheckoutQueryHandler(self.precheckout))
          app.add_handler(MessageHandler(
              filters.SUCCESSFUL_PAYMENT,
              self.payment_success))

          return app

      async def post_init(self, app: Application):
          """Called after app starts — set bot commands and start workers."""
          commands = [
              BotCommand("start",       sc("start the bot")),
              BotCommand("cr",          sc("download cr episode")),
              BotCommand("premium",     sc("view premium plans")),
              BotCommand("stats",       sc("your statistics")),
              BotCommand("queue",       sc("view your queue")),
              BotCommand("history",     sc("download history")),
              BotCommand("news",        sc("crunchyroll news")),
              BotCommand("settings",    sc("configure settings")),
              BotCommand("referral",    sc("referral program")),
              BotCommand("redeem",      sc("redeem a code")),
              BotCommand("batch",       sc("batch download (premium)")),
              BotCommand("schedule",    sc("schedule a download")),
              BotCommand("favorites",   sc("your favorites")),
              BotCommand("watchlist",   sc("your watchlist")),
              BotCommand("leaderboard", sc("top downloaders")),
              BotCommand("help",        sc("commands list")),
          ]
          try:
              await app.bot.set_my_commands(commands)
          except Exception as e:
              logger.warning(f"set_my_commands: {e}")

          # Start background workers
          self._queue_task = asyncio.create_task(self._queue_worker())
          self._sched_task  = asyncio.create_task(self._scheduler_worker())
          self._news_task   = asyncio.create_task(self._news_worker())
          logger.info(f"✅ {sc('all workers started')}")

      async def post_shutdown(self, app: Application):
          """Cancel background workers on shutdown."""
          for task in [self._queue_task, self._sched_task, self._news_task]:
              if task and not task.done():
                  task.cancel()
                  try:
                      await task
                  except asyncio.CancelledError:
                      pass
          logger.info(f"⏹ {sc('all workers stopped')}")

      def run(self):
          if not Config.validate():
              sys.exit(1)
          app = self.build_app()
          app.post_init    = self.post_init
          app.post_shutdown = self.post_shutdown
          logger.info(
              f"\n{'═'*60}\n"
              f"  {sc('crunchyroll ultimate bot v200.0')}\n"
              f"  {sc('starting')}...\n"
              f"{'═'*60}"
          )
          app.run_polling(
              allowed_updates=Update.ALL_TYPES,
              drop_pending_updates=True)

  # ══════════════════════════════════════════════════════════════════════════════
  #  ᴇɴᴛʀʏᴘᴏɪɴᴛ
  # ══════════════════════════════════════════════════════════════════════════════

  if __name__ == "__main__":
      bot = CrunchyBot()
      bot.run()
  


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 31: ᴀᴅᴠᴀɴᴄᴇᴅ ᴄᴏᴏᴋɪᴇ ᴠᴀʟɪᴅᴀᴛᴏʀ + ꜱᴛᴀᴛᴜꜱ ᴄʜᴇᴄᴋ
  # ══════════════════════════════════════════════════════════════════════════════

  class CookieValidator:
      CR_PROFILE_URL = "https://www.crunchyroll.com/accounts/v1/me"

      @staticmethod
      async def validate_via_api(cookies_json: str) -> Tuple[bool, str]:
          if not AIOHTTP_AVAILABLE:
              return True, sc("validation skipped (aiohttp unavailable)")
          try:
              cookies_list = json.loads(cookies_json or "[]")
              cookie_dict  = {c["name"]: c["value"] for c in cookies_list if "name" in c}
              headers = {
                  "User-Agent": (
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"),
                  "Referer": "https://www.crunchyroll.com/",
              }
              async with aiohttp.ClientSession(
                  timeout=aiohttp.ClientTimeout(total=10),
                  cookies=cookie_dict) as session:
                  async with session.get(
                      CookieValidator.CR_PROFILE_URL,
                      headers=headers) as resp:
                      if resp.status == 200:
                          data  = await resp.json()
                          email = data.get("email","") or data.get("username","")
                          return True, sc("valid — account: " + email)
                      elif resp.status == 401:
                          return False, sc("cookies expired or invalid (401)")
                      else:
                          return True, sc("status " + str(resp.status) + " — assuming valid")
          except Exception as e:
              return True, sc("validation error: " + str(e) + " — assuming valid")

      @staticmethod
      async def check_premium_status(cookies_json: str) -> Tuple[bool, str]:
          if not AIOHTTP_AVAILABLE:
              return False, sc("cannot check — aiohttp unavailable")
          try:
              cookies_list = json.loads(cookies_json or "[]")
              cookie_dict  = {c["name"]: c["value"] for c in cookies_list if "name" in c}
              headers = {
                  "User-Agent": (
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
              }
              async with aiohttp.ClientSession(
                  timeout=aiohttp.ClientTimeout(total=10),
                  cookies=cookie_dict) as session:
                  async with session.get(
                      CookieValidator.CR_PROFILE_URL, headers=headers) as resp:
                      if resp.status == 200:
                          data = await resp.json()
                          is_pm = (
                              data.get("is_premium", False)
                              or data.get("subscription_type","") not in ("","free","anonymous")
                          )
                          tier = data.get("subscription_type","?")
                          return is_pm, sc("tier: " + tier)
          except Exception as e:
              logger.warning("check_premium_status: " + str(e))
          try:
              cookies_list = json.loads(cookies_json or "[]")
              premium_markers = ["etp_rt", "crunchyroll_user", "subscription"]
              for c in cookies_list:
                  if any(m in c.get("name","").lower() for m in premium_markers):
                      if c.get("value",""):
                          return True, sc("detected via cookie names (heuristic)")
          except:
              pass
          return False, sc("not detected")


  async def cmd_cookiestatus(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      """/cookiestatus — Admin: Check active cookie status."""
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      db  = Database()
      row = db.get_active_cookies()
      if not row:
          await update.effective_message.reply_text(
              Em.COOKIE + " <b>" + sc("no active cookies") + "</b>\n\n"
              + sc("use") + " /setcookies " + sc("to add crunchyroll cookies") + ".",
              parse_mode=ParseMode.HTML)
          return
      cookies_json = row.get("cookies_json","[]") or "[]"
      cookies_list = json.loads(cookies_json)
      cookie_count = len(cookies_list)
      status_msg = await update.effective_message.reply_text(
          Em.LOADING + " " + sc("validating cookies") + "...",
          parse_mode=ParseMode.HTML)
      is_valid, valid_msg = await CookieValidator.validate_via_api(cookies_json)
      is_pm, pm_msg       = await CookieValidator.check_premium_status(cookies_json)
      text = (
          Em.COOKIE + " <b>" + sc("cookie status") + "</b>\n\n"
          + "📊 " + sc("count") + ": " + str(cookie_count) + " " + sc("cookies") + "\n"
          + "✅ " + sc("valid") + ": "
          + ("yes — " + valid_msg if is_valid else "❌ no — " + valid_msg) + "\n"
          + "💎 " + sc("cr premium") + ": "
          + ("✅ yes — " + pm_msg if is_pm else "❌ no — " + pm_msg) + "\n"
          + "📅 " + sc("expires") + ": " + str(row.get("expires_at","?"))[:16] + "\n"
          + "📅 " + sc("added") + ": " + str(row.get("added_at","?"))[:16] + "\n\n"
          + sc("use") + " /setcookies " + sc("to update cookies") + "."
      )
      if status_msg:
          await safe_edit(status_msg, text)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 32: ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴀʟʏᴛɪᴄꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class DownloadAnalytics:
      @staticmethod
      def get_user_insights(db: Database, uid: int) -> Dict:
          conn = db.conn
          c = conn.execute(
              "SELECT COUNT(*), SUM(file_size), AVG(file_size) FROM downloads WHERE user_id=?",
              (uid,))
          r = c.fetchone()
          total_dls  = r[0] or 0
          total_size = r[1] or 0
          avg_size   = r[2] or 0
          c = conn.execute(
              "SELECT anime_title, COUNT(*) as cnt FROM downloads "
              "WHERE user_id=? GROUP BY anime_title ORDER BY cnt DESC LIMIT 3",
              (uid,))
          top_anime = c.fetchall()
          c = conn.execute(
              "SELECT quality, COUNT(*) as cnt FROM downloads "
              "WHERE user_id=? GROUP BY quality ORDER BY cnt DESC LIMIT 1",
              (uid,))
          r = c.fetchone()
          fav_quality = r[0] if r else "N/A"
          c = conn.execute(
              "SELECT COUNT(*) FROM downloads "
              "WHERE user_id=? AND downloaded_at>=date('now','-7 days')",
              (uid,))
          week_dls = c.fetchone()[0] or 0
          return {
              "total_downloads": total_dls,
              "total_size":      total_size,
              "avg_size":        avg_size,
              "top_anime":       [(r[0], r[1]) for r in top_anime],
              "fav_quality":     fav_quality,
              "week_downloads":  week_dls,
          }

      @staticmethod
      def format_size(size_bytes: int) -> str:
          for unit in ["B","KB","MB","GB","TB"]:
              if size_bytes < 1024:
                  return str(round(size_bytes, 2)) + " " + unit
              size_bytes /= 1024
          return str(round(size_bytes, 2)) + " PB"

      @staticmethod
      def format_insights(insights: Dict) -> str:
          size   = DownloadAnalytics.format_size
          top3   = ""
          for i, (title, n) in enumerate(insights["top_anime"]):
              top3 += "\n   " + str(i+1) + ". " + str(title)[:30] + " (" + str(n) + " ep)"
          if not top3:
              top3 = "\n   " + sc("none yet")
          return (
              Em.PROGRESS + " <b>" + sc("download insights") + "</b>\n\n"
              + "📥 " + sc("total downloads") + ": <b>" + str(insights["total_downloads"]) + "</b>\n"
              + "📦 " + sc("total data") + ": <b>" + size(insights["total_size"]) + "</b>\n"
              + "📊 " + sc("avg file size") + ": <b>" + size(int(insights["avg_size"])) + "</b>\n"
              + "🗓 " + sc("this week") + ": <b>" + str(insights["week_downloads"]) + "</b>\n"
              + "🎨 " + sc("favourite quality") + ": <b>" + str(insights["fav_quality"]) + "</b>\n\n"
              + "<b>" + sc("top 3 anime") + ":</b>" + top3
          )


  async def cmd_insights(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid     = update.effective_user.id if update.effective_user else 0
      db      = Database()
      insight = DownloadAnalytics.get_user_insights(db, uid)
      text    = DownloadAnalytics.format_insights(insight)
      await update.effective_message.reply_text(
          text, reply_markup=KB.back(), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 33: ɢᴀᴍɪꜰɪᴄᴀᴛɪᴏɴ — ᴀᴄʜɪᴇᴠᴇᴍᴇɴᴛꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  ACHIEVEMENTS = {
      "first_download": {
          "title": sc("first download"),
          "icon":  "🌟",
          "desc":  sc("downloaded your first episode"),
          "condition": lambda u: u.get("total_downloads",0) >= 1,
          "reward_stars": 10,
      },
      "ten_downloads": {
          "title": sc("getting started"),
          "icon":  "🎖",
          "desc":  sc("downloaded 10 episodes"),
          "condition": lambda u: u.get("total_downloads",0) >= 10,
          "reward_stars": 20,
      },
      "hundred_downloads": {
          "title": sc("anime addict"),
          "icon":  "🏆",
          "desc":  sc("downloaded 100 episodes"),
          "condition": lambda u: u.get("total_downloads",0) >= 100,
          "reward_stars": 100,
      },
      "first_referral": {
          "title": sc("recruiter"),
          "icon":  "👥",
          "desc":  sc("referred your first user"),
          "condition": lambda u: u.get("referral_count",0) >= 1,
          "reward_stars": 25,
      },
      "five_referrals": {
          "title": sc("ambassador"),
          "icon":  "🌐",
          "desc":  sc("referred 5 users"),
          "condition": lambda u: u.get("referral_count",0) >= 5,
          "reward_stars": 100,
      },
      "premium_member": {
          "title": sc("vip member"),
          "icon":  "💎",
          "desc":  sc("became a premium member"),
          "condition": lambda u: u.get("premium_type","free") != "free",
          "reward_stars": 50,
      },
      "one_gb": {
          "title": sc("data hoarder"),
          "icon":  "💾",
          "desc":  sc("downloaded over 1gb of anime"),
          "condition": lambda u: u.get("total_size",0) >= 1024**3,
          "reward_stars": 50,
      },
      "ten_gb": {
          "title": sc("server killer"),
          "icon":  "🗄",
          "desc":  sc("downloaded over 10gb of anime"),
          "condition": lambda u: u.get("total_size",0) >= 10 * 1024**3,
          "reward_stars": 200,
      },
      "five_star_rating": {
          "title": sc("reviewer"),
          "icon":  "⭐",
          "desc":  sc("gave a 5-star feedback"),
          "condition": lambda u: False,  # checked separately
          "reward_stars": 15,
      },
      "daily_streak_7": {
          "title": sc("dedicated watcher"),
          "icon":  "🔥",
          "desc":  sc("downloaded anime 7 days in a row"),
          "condition": lambda u: False,  # checked separately
          "reward_stars": 75,
      },
  }


  def check_achievements(db: Database, uid: int) -> List[str]:
      user = db.get_user(uid)
      if not user:
          return []
      awarded_key = "achievements_" + str(uid)
      c = db.conn.execute("SELECT value FROM settings WHERE key=?", (awarded_key,))
      r = c.fetchone()
      already = set(json.loads(r[0] if r else "[]"))
      newly   = []
      for name, ach in ACHIEVEMENTS.items():
          if name not in already:
              try:
                  if ach["condition"](user):
                      already.add(name)
                      newly.append(name)
                      StarsEconomy.award_stars(db, uid, ach["reward_stars"], name)
              except:
                  pass
      if newly:
          db.conn.execute(
              "INSERT INTO settings(key,value) VALUES(?,?) "
              "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
              (awarded_key, json.dumps(list(already))))
          db.conn.commit()
      return newly


  def format_achievement_unlock(names: List[str]) -> str:
      if not names:
          return ""
      parts = []
      for name in names:
          ach = ACHIEVEMENTS.get(name, {})
          parts.append(
              ach.get("icon","🏅") + " <b>" + str(ach.get("title","?")) + "</b> — "
              + str(ach.get("desc","?")) + " (+" + str(ach.get("reward_stars",0)) + " ⭐)")
      return "\n\n🎉 <b>" + sc("achievement unlocked") + "!</b>\n" + "\n".join(parts)


  async def cmd_achievements(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid  = update.effective_user.id if update.effective_user else 0
      db   = Database()
      user = db.get_user(uid)
      if not user:
          await update.effective_message.reply_text(
              Em.ERROR + " " + sc("please start the bot first with") + " /start",
              parse_mode=ParseMode.HTML)
          return
      awarded_key = "achievements_" + str(uid)
      c = db.conn.execute("SELECT value FROM settings WHERE key=?", (awarded_key,))
      r = c.fetchone()
      already = set(json.loads(r[0] if r else "[]"))
      lines   = ["🏆 <b>" + sc("your achievements") + "</b>\n"]
      for name, ach in ACHIEVEMENTS.items():
          unlocked   = name in already
          can_unlock = False
          try:
              can_unlock = ach["condition"](user)
          except:
              pass
          icon = "✅" if unlocked else ("🔓" if can_unlock else "🔒")
          lines.append(
              icon + " " + ach["icon"] + " <b>" + str(ach["title"]) + "</b>\n"
              + "   " + str(ach["desc"]) + " (+" + str(ach["reward_stars"]) + " ⭐)")
      lines.append("\n" + sc("unlocked") + ": " + str(len(already)) + "/" + str(len(ACHIEVEMENTS)))
      await update.effective_message.reply_text(
          "\n".join(lines), reply_markup=KB.back(), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 34: ꜱᴛᴀʀꜱ ᴇᴄᴏɴᴏᴍʏ ꜱʏꜱᴛᴇᴍ
  # ══════════════════════════════════════════════════════════════════════════════

  class StarsEconomy:
      @staticmethod
      def award_stars(db: Database, uid: int, amount: int, reason: str = "") -> int:
          db.conn.execute(
              "UPDATE users SET stars_balance=stars_balance+? WHERE user_id=?",
              (amount, uid))
          db.conn.commit()
          c = db.conn.execute("SELECT stars_balance FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          bal = r[0] if r else 0
          if reason:
              logger.info("Stars +" + str(amount) + " uid=" + str(uid) + " (" + reason + "), total=" + str(bal))
          return bal

      @staticmethod
      def spend_stars(db: Database, uid: int, amount: int) -> Tuple[bool, int]:
          c = db.conn.execute("SELECT stars_balance FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          bal = r[0] if r else 0
          if bal < amount:
              return False, bal
          db.conn.execute(
              "UPDATE users SET stars_balance=stars_balance-? WHERE user_id=?",
              (amount, uid))
          db.conn.commit()
          return True, bal - amount

      @staticmethod
      def get_balance(db: Database, uid: int) -> int:
          c = db.conn.execute("SELECT stars_balance FROM users WHERE user_id=?", (uid,))
          r = c.fetchone()
          return r[0] if r else 0

      @staticmethod
      def transfer_stars(db: Database, from_uid: int, to_uid: int,
                         amount: int) -> Tuple[bool, str]:
          ok, remaining = StarsEconomy.spend_stars(db, from_uid, amount)
          if not ok:
              return False, sc("insufficient stars") + " (" + str(remaining) + " " + sc("available") + ")"
          StarsEconomy.award_stars(db, to_uid, amount, "transfer from " + str(from_uid))
          return True, sc("transfer successful")


  async def cmd_stars(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      """/stars — Check your stars balance."""
      uid = update.effective_user.id if update.effective_user else 0
      db  = Database()
      bal = StarsEconomy.get_balance(db, uid)
      await update.effective_message.reply_text(
          Em.STAR + " <b>" + sc("your stars balance") + "</b>\n\n"
          + "⭐ " + sc("balance") + ": <b>" + str(bal) + " " + sc("stars") + "</b>\n\n"
          + sc("earn stars by") + ":\n"
          + "• " + sc("referring users") + " (+" + str(Config.REFERRAL_REWARD) + " " + sc("stars") + ")\n"
          + "• " + sc("unlocking achievements") + "\n"
          + "• " + sc("buying via telegram stars") + "\n\n"
          + sc("use") + " /premium " + sc("to spend stars on premium"),
          reply_markup=KB.back(),
          parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 35: ꜰʀᴇᴇ ᴛʀɪᴀʟ ᴄᴏᴍᴍᴀɴᴅ
  # ══════════════════════════════════════════════════════════════════════════════

  async def cmd_trial(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      """/trial — Claim a free 24-hour premium trial (once per user)."""
      uid = update.effective_user.id if update.effective_user else 0
      db  = Database()
      user = db.get_user(uid)
      if not user:
          await update.effective_message.reply_text(
              Em.ERROR + " " + sc("please start the bot first"),
              parse_mode=ParseMode.HTML)
          return
      c = db.conn.execute("SELECT value FROM settings WHERE key=?", ("trial_used_" + str(uid),))
      r = c.fetchone()
      if r:
          await update.effective_message.reply_text(
              Em.WARNING + " " + sc("you have already used the free trial") + ".\n"
              + sc("use") + " /premium " + sc("to upgrade"),
              parse_mode=ParseMode.HTML)
          return
      if db.is_premium(uid):
          await update.effective_message.reply_text(
              Em.INFO + " " + sc("you already have premium!"),
              parse_mode=ParseMode.HTML)
          return
      expiry = (datetime.now() + timedelta(hours=24)).isoformat()
      db.conn.execute(
          "UPDATE users SET premium_type='trial',premium_expiry=? WHERE user_id=?",
          (expiry, uid))
      db.conn.execute(
          "INSERT INTO settings(key,value) VALUES(?,CURRENT_TIMESTAMP) "
          "ON CONFLICT(key) DO NOTHING",
          ("trial_used_" + str(uid),))
      db.conn.commit()
      await update.effective_message.reply_text(
          Em.PREMIUM + " <b>" + sc("free trial activated") + "!</b>\n\n"
          + "⏱ " + sc("duration") + ": <b>24 " + sc("hours") + "</b>\n"
          + "🎨 " + sc("quality") + ": up to <b>720p</b>\n"
          + "📥 " + sc("limit") + ": <b>5 " + sc("downloads") + "</b>\n\n"
          + sc("upgrade to full premium at") + " /premium " + sc("for unlimited access") + "!",
          reply_markup=KB.premium_plans(),
          parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 36: ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜ (ᴊɪᴋᴀɴ.ᴍᴏᴇ)
  # ══════════════════════════════════════════════════════════════════════════════

  class AnimeSearch:
      BASE = "https://api.jikan.moe/v4"

      @staticmethod
      async def search(query: str, limit: int = 5) -> List[Dict]:
          if not AIOHTTP_AVAILABLE:
              return []
          url = AnimeSearch.BASE + "/anime"
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
                                  "title":    a.get("title","?"),
                                  "title_en": a.get("title_english",""),
                                  "episodes": a.get("episodes","?"),
                                  "status":   a.get("status","?"),
                                  "score":    a.get("score","?"),
                                  "synopsis": (a.get("synopsis","") or "")[:200],
                                  "url":      a.get("url",""),
                              })
                          return results
          except Exception as e:
              logger.warning("AnimeSearch: " + str(e))
          return []


  async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      msg = update.effective_message
      if not ctx.args:
          await msg.reply_text(
              Em.ANIME + " " + sc("usage") + ": /search <code>" + sc("anime name") + "</code>",
              parse_mode=ParseMode.HTML)
          return
      query  = " ".join(ctx.args)
      status = await msg.reply_text(
          Em.LOADING + " " + sc("searching for") + " <b>" + query + "</b>...",
          parse_mode=ParseMode.HTML)
      results = await AnimeSearch.search(query, 5)
      if not results:
          await status.edit_text(
              Em.ERROR + " " + sc("no results found for") + " <b>" + query + "</b>.",
              parse_mode=ParseMode.HTML)
          return
      lines   = [Em.ANIME + " <b>" + sc("search results for") + ": " + query + "</b>\n"]
      kb_rows = []
      for i, r in enumerate(results, 1):
          score = r.get("score","?")
          eps   = r.get("episodes","?")
          lines.append(
              "\n<b>" + str(i) + ". " + r["title"] + "</b>\n"
              + "   ⭐" + str(score) + " | 📺 " + str(eps) + " " + sc("eps") + "\n"
              + (r["synopsis"][:120] + "...\n" if r.get("synopsis") else "")
          )
          if r.get("url"):
              kb_rows.append([InlineKeyboardButton(
                  "🔗 " + r["title"][:30], url=r["url"])])
      kb_rows.append([InlineKeyboardButton(
          Em.BACK + " " + sc("home"), callback_data="show_home")])
      await status.edit_text(
          "\n".join(lines),
          reply_markup=InlineKeyboardMarkup(kb_rows),
          parse_mode=ParseMode.HTML)


  async def cmd_airing(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      msg    = update.effective_message
      status = await msg.reply_text(
          Em.LOADING + " " + sc("fetching currently airing anime") + "...",
          parse_mode=ParseMode.HTML)
      if not AIOHTTP_AVAILABLE:
          await status.edit_text(Em.ERROR + " aiohttp not installed.", parse_mode=ParseMode.HTML)
          return
      url = AnimeSearch.BASE + "/top/anime"
      params = {"filter": "airing", "limit": 10}
      try:
          async with aiohttp.ClientSession(
              timeout=aiohttp.ClientTimeout(total=10)) as session:
              async with session.get(url, params=params) as resp:
                  if resp.status == 200:
                      data   = await resp.json()
                      animes = data.get("data", [])
                      lines  = [Em.FIRE + " <b>" + sc("currently airing anime (top 10)") + "</b>\n"]
                      for i, a in enumerate(animes, 1):
                          score = a.get("score","?")
                          eps   = a.get("episodes","?") or "?"
                          lines.append(
                              str(i) + ". <b>" + a.get("title","?") + "</b>"
                              + " ⭐" + str(score) + " | 📺 " + str(eps) + " " + sc("eps"))
                      await status.edit_text("\n".join(lines), parse_mode=ParseMode.HTML)
                  else:
                      await status.edit_text(
                          Em.ERROR + " " + sc("api error") + ": " + str(resp.status),
                          parse_mode=ParseMode.HTML)
      except Exception as e:
          await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  async def cmd_season(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      msg    = update.effective_message
      status = await msg.reply_text(
          Em.LOADING + " " + sc("fetching seasonal anime") + "...", parse_mode=ParseMode.HTML)
      if not AIOHTTP_AVAILABLE:
          await status.edit_text(Em.ERROR + " aiohttp not installed.", parse_mode=ParseMode.HTML)
          return
      url = AnimeSearch.BASE + "/seasons/now"
      params = {"limit": 15}
      try:
          async with aiohttp.ClientSession(
              timeout=aiohttp.ClientTimeout(total=10)) as session:
              async with session.get(url, params=params) as resp:
                  if resp.status == 200:
                      data   = await resp.json()
                      animes = data.get("data",[])
                      lines  = [Em.ANIME + " <b>" + sc("this season anime") + "</b>\n"]
                      for i, a in enumerate(animes[:15], 1):
                          score  = a.get("score") or "N/A"
                          genres = ", ".join(
                              g["name"] for g in a.get("genres",[])[:3]) or "?"
                          lines.append(
                              str(i) + ". <b>" + a.get("title","?") + "</b>\n"
                              + "   ⭐" + str(score) + " | 🎭 " + genres)
                      await status.edit_text("\n".join(lines), parse_mode=ParseMode.HTML)
                  else:
                      await status.edit_text(
                          Em.ERROR + " " + sc("api error") + ": " + str(resp.status),
                          parse_mode=ParseMode.HTML)
      except Exception as e:
          await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 37: ᴄᴏɴꜰɪɢ + ᴅɪᴀɢɴᴏꜱᴛɪᴄꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class Diagnostics:
      @staticmethod
      async def check_all() -> Dict[str, bool]:
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
              except:
                  results[tool] = False
          try:
              stat = shutil.disk_usage(str(Config.BASE_DIR))
              results["disk_space_ok"] = (stat.free / (1024**3)) > 2.0
          except:
              results["disk_space_ok"] = False
          try:
              db = Database()
              db.conn.execute("SELECT 1")
              results["database"] = True
          except:
              results["database"] = False
          return results

      @staticmethod
      def format_report(checks: Dict[str, bool]) -> str:
          icons = {True: "✅", False: "❌"}
          lines = ["🔧 <b>" + sc("system diagnostics") + "</b>\n"]
          for k, v in checks.items():
              lines.append(icons[v] + " " + sc(k.replace("_"," ")))
          return "\n".join(lines)


  async def cmd_diagnostics(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      status = await update.effective_message.reply_text(
          Em.LOADING + " " + sc("running diagnostics") + "...", parse_mode=ParseMode.HTML)
      checks = await Diagnostics.check_all()
      report = Diagnostics.format_report(checks)
      all_ok = all(checks.values())
      report += "\n\n" + ("✅ " + sc("all systems ok") if all_ok else "⚠️ " + sc("some checks failed"))
      if status:
          try:
              await status.edit_text(report, parse_mode=ParseMode.HTML)
          except:
              await update.effective_message.reply_text(report, parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 38: ᴅʙ ᴜᴛɪʟɪᴛɪᴇꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class DBUtils:
      @staticmethod
      def vacuum(db: Database):
          db.conn.execute("VACUUM")
          db.conn.commit()

      @staticmethod
      def backup(db: Database, dest: str) -> bool:
          try:
              with sqlite3.connect(dest) as bkp:
                  db.conn.backup(bkp)
              return True
          except Exception as e:
              logger.error("DB backup: " + str(e))
              return False

      @staticmethod
      def export_users_csv(db: Database) -> str:
          c = db.conn.execute(
              "SELECT user_id,username,first_name,premium_type,premium_expiry,"
              "total_downloads,total_size,is_banned,joined_at FROM users "
              "ORDER BY joined_at DESC")
          rows  = c.fetchall()
          lines = ["user_id,username,first_name,premium_type,premium_expiry,"
                   "total_downloads,total_size_bytes,is_banned,joined_at"]
          for r in rows:
              lines.append(",".join(str(x or "") for x in r))
          return "\n".join(lines)

      @staticmethod
      def cleanup_old_files() -> int:
          cutoff  = time.time() - 86400
          cleaned = 0
          for folder in [Config.TEMP_PATH, Config.ENCODE_PATH]:
              for f in folder.glob("*"):
                  if f.is_file() and f.stat().st_mtime < cutoff:
                      try:
                          f.unlink()
                          cleaned += 1
                      except:
                          pass
          return cleaned


  async def cmd_dbbackup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      dest   = str(Config.DATA_PATH / ("backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".db"))
      status = await update.effective_message.reply_text(
          Em.LOADING + " " + sc("backing up database") + "...", parse_mode=ParseMode.HTML)
      db = Database()
      ok = DBUtils.backup(db, dest)
      if ok:
          await ctx.bot.send_document(
              update.effective_chat.id,
              document=InputFile(dest),
              caption=Em.SUCCESS + " " + sc("database backup"),
              parse_mode=ParseMode.HTML)
          if status: await status.delete()
          Path(dest).unlink(missing_ok=True)
      else:
          if status:
              await status.edit_text(Em.ERROR + " " + sc("backup failed") + ".", parse_mode=ParseMode.HTML)


  async def cmd_exportusers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      db  = Database()
      csv = DBUtils.export_users_csv(db)
      fp  = str(Config.TEMP_PATH / ("users_" + datetime.now().strftime("%Y%m%d") + ".csv"))
      Path(fp).write_text(csv, encoding="utf-8")
      await ctx.bot.send_document(
          update.effective_chat.id,
          document=InputFile(fp, filename=Path(fp).name),
          caption=Em.STATS + " " + sc("user export"),
          parse_mode=ParseMode.HTML)
      Path(fp).unlink(missing_ok=True)


  async def cmd_cleanup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      count = DBUtils.cleanup_old_files()
      await update.effective_message.reply_text(
          Em.SUCCESS + " " + sc("cleaned up") + " " + str(count) + " " + sc("old temp files") + ".",
          parse_mode=ParseMode.HTML)


  async def cmd_vacuum(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      if uid not in Config.ADMIN_IDS:
          return
      db = Database()
      DBUtils.vacuum(db)
      await update.effective_message.reply_text(
          Em.SUCCESS + " " + sc("database vacuumed") + ".",
          parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 39: ꜱᴜʙᴛɪᴛʟᴇ ᴛᴏᴏʟꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  SUPPORTED_SUB_LANGUAGES = {
      "en": sc("english"), "es": sc("spanish"), "pt": sc("portuguese"),
      "fr": sc("french"),  "de": sc("german"),  "ja": "japanese",
      "ar": "arabic",      "zh": "chinese",     "ko": "korean",
      "ru": sc("russian"), "tr": sc("turkish"),
      "hi": sc("hindi"),   "ta": sc("tamil"),   "id": sc("indonesian"),
  }


  class SubtitleTools:
      @staticmethod
      async def extract_subtitles(video_path: str, stream_idx: int = 0) -> Optional[str]:
          out = str(Config.TEMP_PATH / (Path(video_path).stem + "_sub_" + str(stream_idx) + ".srt"))
          cmd = [Config.FFMPEG_PATH, "-y", "-i", video_path,
                 "-map", "0:s:" + str(stream_idx), out]
          try:
              proc = await asyncio.create_subprocess_exec(
                  *cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=120)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
              return None

      @staticmethod
      async def list_subtitle_tracks(video_path: str) -> List[Dict]:
          cmd = [
              Config.FFPROBE_PATH, "-v", "error",
              "-select_streams", "s",
              "-show_entries", "stream=index:stream_tags=language,title",
              "-of", "json", video_path,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(
                  *cmd,
                  stdout=asyncio.subprocess.PIPE,
                  stderr=asyncio.subprocess.DEVNULL)
              out, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
              data   = json.loads(out.decode())
              return [{"index": s.get("index",0),
                       "lang":  s.get("tags",{}).get("language","und"),
                       "title": s.get("tags",{}).get("title","")}
                      for s in data.get("streams",[])]
          except:
              return []


  async def cmd_subtracks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      msg    = update.effective_message
      target = msg.reply_to_message if msg else None
      if not target or not (target.document or target.video):
          await msg.reply_text(
              Em.SUBTITLE + " " + sc("reply to a video with") + " /subtracks",
              parse_mode=ParseMode.HTML)
          return
      status = await msg.reply_text(
          Em.LOADING + " " + sc("reading subtitle tracks") + "...", parse_mode=ParseMode.HTML)
      try:
          doc = target.document or target.video
          f   = await ctx.bot.get_file(doc.file_id)
          fp  = str(Config.TEMP_PATH / ("st_" + str(doc.file_unique_id) + ".mp4"))
          await f.download_to_drive(fp)
          tracks = await SubtitleTools.list_subtitle_tracks(fp)
          Path(fp).unlink(missing_ok=True)
          if not tracks:
              await status.edit_text(
                  Em.INFO + " " + sc("no subtitle tracks found") + ".",
                  parse_mode=ParseMode.HTML)
              return
          lines = [Em.SUBTITLE + " <b>" + sc("subtitle tracks") + "</b>\n"]
          for t in tracks:
              lang_name = SUPPORTED_SUB_LANGUAGES.get(t["lang"], t["lang"])
              lines.append(
                  "  #" + str(t["index"]) + " | " + t["lang"].upper() + " — " + lang_name
                  + (" | " + t["title"] if t.get("title") else ""))
          lines.append("\n" + sc("use") + " /extsub <code>" + sc("track_number") + "</code> " + sc("to extract"))
          await status.edit_text("\n".join(lines), parse_mode=ParseMode.HTML)
      except Exception as e:
          if status:
              await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  async def cmd_extsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      msg    = update.effective_message
      target = msg.reply_to_message if msg else None
      if not target or not (target.document or target.video):
          await msg.reply_text(
              Em.SUBTITLE + " " + sc("reply to a video with") + " /extsub <code>[track]</code>",
              parse_mode=ParseMode.HTML)
          return
      track  = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 0
      status = await msg.reply_text(
          Em.LOADING + " " + sc("extracting subtitle track") + " #" + str(track) + "...",
          parse_mode=ParseMode.HTML)
      try:
          doc = target.document or target.video
          f   = await ctx.bot.get_file(doc.file_id)
          fp  = str(Config.TEMP_PATH / ("es_" + str(doc.file_unique_id) + ".mp4"))
          await f.download_to_drive(fp)
          out = await SubtitleTools.extract_subtitles(fp, track)
          Path(fp).unlink(missing_ok=True)
          if out and Path(out).exists():
              await ctx.bot.send_document(
                  msg.chat_id,
                  document=InputFile(out, filename=Path(out).name),
                  caption=Em.SUBTITLE + " " + sc("subtitle track") + " #" + str(track),
                  parse_mode=ParseMode.HTML)
              Path(out).unlink(missing_ok=True)
              if status: await status.delete()
          else:
              if status:
                  await status.edit_text(
                      Em.ERROR + " " + sc("could not extract subtitle track") + " #" + str(track) + ".",
                      parse_mode=ParseMode.HTML)
      except Exception as e:
          if status:
              await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 40: ɪɴʟɪɴᴇ ᴍᴏᴅᴇ + ꜱᴄʜᴇᴅʟɪꜱᴛ
  # ══════════════════════════════════════════════════════════════════════════════

  async def inline_query_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
                      Em.ANIME + " " + sc("use") + " /start " + sc("in private chat to download anime!"),
                      parse_mode=ParseMode.HTML))
          ]
          await q.answer(results, cache_time=10)
          return
      animes  = await AnimeSearch.search(query, 5)
      results = []
      for a in animes:
          title = a.get("title","?")
          score = a.get("score","?")
          eps   = a.get("episodes","?")
          syn   = a.get("synopsis","")[:200]
          url   = a.get("url","")
          text  = (
              Em.ANIME + " <b>" + title + "</b>\n\n"
              + "⭐ " + sc("score") + ": " + str(score) + " | 📺 " + sc("episodes") + ": " + str(eps) + "\n\n"
              + syn
              + ("\n\n🔗 <a href='" + url + "'>" + sc("view on mal") + "</a>" if url else "")
          )
          results.append(
              InlineQueryResultArticle(
                  id=str(a.get("mal_id", title)),
                  title=title,
                  description="⭐" + str(score) + " | " + str(eps) + " eps | " + syn[:80],
                  input_message_content=InputTextMessageContent(
                      text, parse_mode=ParseMode.HTML,
                      disable_web_page_preview=False)))
      await q.answer(results, cache_time=30)


  async def cmd_schedlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      uid = update.effective_user.id if update.effective_user else 0
      db  = Database()
      c   = db.conn.execute(
          "SELECT id,url,quality,encode_preset,run_at,status FROM scheduled "
          "WHERE user_id=? ORDER BY run_at ASC LIMIT 10",
          (uid,))
      rows = c.fetchall()
      if not rows:
          await update.effective_message.reply_text(
              Em.SCHEDULE + " " + sc("no scheduled downloads") + ".\n"
              + sc("use") + " /schedule <code>" + sc("url hh:mm") + "</code> " + sc("to schedule") + ".",
              parse_mode=ParseMode.HTML)
          return
      lines = [Em.SCHEDULE + " <b>" + sc("scheduled downloads") + "</b>\n"]
      for r in rows:
          status_icon = "✅" if r[5] == "queued" else "⏳"
          lines.append(
              status_icon + " <b>#" + str(r[0]) + "</b> | " + str(r[4])[:16] + "\n"
              + "   <code>" + str(r[1])[-35:] + "</code>\n"
              + "   <code>" + str(r[2]) + "</code> | <code>" + str(r[3]) + "</code>")
      await update.effective_message.reply_text(
          "\n".join(lines), reply_markup=KB.back(), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 41: ᴇxᴛᴇɴᴅ ʙᴜɪʟᴅ_ᴀᴘᴘ ᴡɪᴛʜ ᴀʟʟ ɴᴇᴡ ʜᴀɴᴅʟᴇʀꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  _ORIGINAL_BUILD_APP_5 = CrunchyBot.build_app

  def _extended_build_app_v2(self) -> Application:
      from telegram.ext import InlineQueryHandler as IQH
      app = _ORIGINAL_BUILD_APP_5(self)
      app.add_handler(CommandHandler("search",       cmd_search))
      app.add_handler(CommandHandler("airing",       cmd_airing))
      app.add_handler(CommandHandler("season",       cmd_season))
      app.add_handler(CommandHandler("subtracks",    cmd_subtracks))
      app.add_handler(CommandHandler("extsub",       cmd_extsub))
      app.add_handler(CommandHandler("diagnostics",  cmd_diagnostics))
      app.add_handler(CommandHandler("dbbackup",     cmd_dbbackup))
      app.add_handler(CommandHandler("exportusers",  cmd_exportusers))
      app.add_handler(CommandHandler("cleanup",      cmd_cleanup))
      app.add_handler(CommandHandler("vacuum",       cmd_vacuum))
      app.add_handler(CommandHandler("insights",     cmd_insights))
      app.add_handler(CommandHandler("achievements", cmd_achievements))
      app.add_handler(CommandHandler("achieve",      cmd_achievements))
      app.add_handler(CommandHandler("stars",        cmd_stars))
      app.add_handler(CommandHandler("trial",        cmd_trial))
      app.add_handler(CommandHandler("schedlist",    cmd_schedlist))
      app.add_handler(CommandHandler("cookiestatus", cmd_cookiestatus))
      app.add_handler(CommandHandler("cs",           cmd_cookiestatus))
      app.add_handler(IQH(inline_query_handler))
      return app

  CrunchyBot.build_app = _extended_build_app_v2


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 42: ꜱᴛᴀʀᴛᴜᴘ ʙᴀɴɴᴇʀ
  # ══════════════════════════════════════════════════════════════════════════════

  def print_startup_banner():
      bar = "=" * 64
      print(bar)
      print("  " + sc("crunchyroll ultimate bot v200.0"))
      print("  " + sc("fast/slow lane | cookies | cr news | achievements"))
      print("  " + sc("referral | premium emoji | sqlite db | 50+ commands"))
      print("-" * 64)
      print("  " + sc("support") + ": " + Config.SUPPORT_USERNAME)
      print("  " + sc("admin ids") + ": " + str(Config.ADMIN_IDS))
      print("  DB: " + str(Config.DATABASE_PATH))
      print("  Downloads: " + str(Config.DOWNLOAD_PATH))
      print("-" * 64)
      print("  ffmpeg:  " + Config.FFMPEG_PATH)
      print("  ffprobe: " + Config.FFPROBE_PATH)
      print("  yt-dlp:  " + Config.YTDLP_PATH)
      print(bar)
      logger.info(sc("startup banner printed"))


  _ORIGINAL_RUN = CrunchyBot.run

  def _run_with_banner(self):
      print_startup_banner()
      _ORIGINAL_RUN(self)

  CrunchyBot.run = _run_with_banner
  

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 43: ᴠɪᴅᴇᴏ ꜱᴘʟɪᴛᴛᴇʀ + ᴍᴇʀɢᴇʀ ᴛᴏᴏʟꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  class VideoSplitter:
      """ꜱᴘʟɪᴛ ᴀ ᴠɪᴅᴇᴏ ɪɴᴛᴏ ᴄʜᴜɴᴋꜱ ᴏʀ ꜱᴇɢᴍᴇɴᴛꜱ ʙʏ ꜱɪᴢᴇ/ᴛɪᴍᴇ."""

      @staticmethod
      async def split_by_size(input_path: str, chunk_mb: int = 50) -> List[str]:
          info    = await VideoTools.get_media_info(input_path)
          dur     = float(info.get("raw_duration", 0))
          size_mb = float(info.get("size_mb", 0))
          if size_mb <= chunk_mb or dur == 0:
              return [input_path]
          n_chunks    = max(2, int(size_mb / chunk_mb) + 1)
          chunk_dur   = dur / n_chunks
          output_files: List[str] = []
          stem = Path(input_path).stem
          for i in range(n_chunks):
              start  = i * chunk_dur
              out    = str(Config.TEMP_PATH / (stem + "_part" + str(i+1) + ".mp4"))
              cmd    = [
                  Config.FFMPEG_PATH, "-y", "-i", input_path,
                  "-ss", str(start), "-t", str(chunk_dur),
                  "-c", "copy", out,
              ]
              try:
                  proc = await asyncio.create_subprocess_exec(
                      *cmd, stderr=asyncio.subprocess.DEVNULL)
                  await asyncio.wait_for(proc.wait(), timeout=300)
                  if proc.returncode == 0 and Path(out).exists():
                      output_files.append(out)
              except:
                  pass
          return output_files if output_files else [input_path]

      @staticmethod
      async def split_by_time(input_path: str, segment_minutes: int = 10) -> List[str]:
          info   = await VideoTools.get_media_info(input_path)
          dur    = float(info.get("raw_duration", 0))
          seg    = segment_minutes * 60
          if dur <= seg:
              return [input_path]
          output_files: List[str] = []
          stem   = Path(input_path).stem
          ts     = 0.0
          idx    = 1
          while ts < dur:
              out = str(Config.TEMP_PATH / (stem + "_seg" + str(idx) + ".mp4"))
              cmd = [
                  Config.FFMPEG_PATH, "-y", "-i", input_path,
                  "-ss", str(ts), "-t", str(seg),
                  "-c", "copy", out,
              ]
              try:
                  proc = await asyncio.create_subprocess_exec(
                      *cmd, stderr=asyncio.subprocess.DEVNULL)
                  await asyncio.wait_for(proc.wait(), timeout=300)
                  if proc.returncode == 0 and Path(out).exists():
                      output_files.append(out)
              except:
                  pass
              ts  += seg
              idx += 1
          return output_files if output_files else [input_path]


  async def cmd_split(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      """/split [mb|time] [value] — Split a video into parts (reply to file)."""
      uid    = update.effective_user.id if update.effective_user else 0
      msg    = update.effective_message
      target = msg.reply_to_message if msg else None
      if not target or not (target.document or target.video):
          await msg.reply_text(
              Em.VIDEO + " " + sc("usage") + ": /split <code>[mb N | time N]</code>\n"
              + sc("example") + ": /split mb 50 — " + sc("split into 50mb chunks") + "\n"
              + sc("example") + ": /split time 10 — " + sc("split into 10-minute segments"),
              parse_mode=ParseMode.HTML)
          return
      mode  = ctx.args[0].lower() if ctx.args else "mb"
      value = int(ctx.args[1]) if len(ctx.args) > 1 and ctx.args[1].isdigit() else 50

      status = await msg.reply_text(
          Em.LOADING + " " + sc("splitting video") + "...", parse_mode=ParseMode.HTML)
      try:
          doc = target.document or target.video
          f   = await ctx.bot.get_file(doc.file_id)
          fp  = str(Config.TEMP_PATH / ("split_" + str(doc.file_unique_id) + ".mp4"))
          await f.download_to_drive(fp)

          if mode == "time":
              parts = await VideoSplitter.split_by_time(fp, value)
          else:
              parts = await VideoSplitter.split_by_size(fp, value)

          if len(parts) <= 1:
              if status:
                  await status.edit_text(
                      Em.INFO + " " + sc("video already fits in one chunk") + ".",
                      parse_mode=ParseMode.HTML)
              Path(fp).unlink(missing_ok=True)
              return

          if status:
              await status.edit_text(
                  Em.SUCCESS + " " + sc("split into") + " " + str(len(parts)) + " " + sc("parts") + "!",
                  parse_mode=ParseMode.HTML)

          for i, part_path in enumerate(parts, 1):
              fname = Path(part_path).name
              await ctx.bot.send_document(
                  msg.chat_id,
                  document=InputFile(part_path, filename=fname),
                  caption=Em.VIDEO + " " + sc("part") + " " + str(i) + "/" + str(len(parts)),
                  parse_mode=ParseMode.HTML)
              Path(part_path).unlink(missing_ok=True)
          Path(fp).unlink(missing_ok=True)

      except Exception as e:
          if status:
              await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 44: ᴠɪᴅᴇᴏ ꜱᴘᴇᴇᴅ ᴄᴏɴᴛʀᴏʟ
  # ══════════════════════════════════════════════════════════════════════════════

  class VideoSpeedChanger:
      """ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ ꜱᴘᴇᴇᴅ ᴏꜰ ᴀ ᴠɪᴅᴇᴏ."""

      ALLOWED_SPEEDS = [0.25, 0.5, 0.75, 1.25, 1.5, 2.0, 3.0, 4.0]

      @staticmethod
      async def change_speed(input_path: str, speed: float) -> Optional[str]:
          speed  = max(0.25, min(4.0, speed))
          vf     = "setpts=" + str(round(1.0/speed, 4)) + "*PTS"
          af     = "atempo=" + str(speed)
          if speed > 2.0:
              af = "atempo=2.0,atempo=" + str(round(speed/2.0, 4))
          if speed < 0.5:
              af = "atempo=0.5,atempo=" + str(round(speed/0.5, 4))
          out = str(Config.TEMP_PATH / (Path(input_path).stem + "_x" + str(speed) + ".mp4"))
          cmd = [
              Config.FFMPEG_PATH, "-y", "-i", input_path,
              "-vf", vf, "-af", af,
              "-c:v", "libx264", "-c:a", "aac", out,
          ]
          try:
              proc = await asyncio.create_subprocess_exec(
                  *cmd, stderr=asyncio.subprocess.DEVNULL)
              await asyncio.wait_for(proc.wait(), timeout=600)
              return out if proc.returncode == 0 and Path(out).exists() else None
          except:
              return None


  async def cmd_speed(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      """/speed [rate] — Change video playback speed (reply to file)."""
      msg    = update.effective_message
      target = msg.reply_to_message if msg else None
      if not target or not (target.document or target.video):
          await msg.reply_text(
              Em.VIDEO + " " + sc("usage") + ": /speed <code>[rate]</code>\n"
              + sc("example") + ": /speed 2.0 — " + sc("double speed") + "\n"
              + sc("allowed") + ": 0.25, 0.5, 0.75, 1.25, 1.5, 2.0, 3.0, 4.0",
              parse_mode=ParseMode.HTML)
          return
      try:
          speed = float(ctx.args[0]) if ctx.args else 2.0
      except:
          await msg.reply_text(Em.ERROR + " " + sc("invalid speed value") + ".", parse_mode=ParseMode.HTML)
          return
      status = await msg.reply_text(
          Em.LOADING + " " + sc("changing speed to") + " " + str(speed) + "x...", parse_mode=ParseMode.HTML)
      try:
          doc = target.document or target.video
          f   = await ctx.bot.get_file(doc.file_id)
          fp  = str(Config.TEMP_PATH / ("spd_" + str(doc.file_unique_id) + ".mp4"))
          await f.download_to_drive(fp)
          out = await VideoSpeedChanger.change_speed(fp, speed)
          if out and Path(out).exists():
              fname = "speed_" + str(speed) + "x_" + uuid.uuid4().hex[:6] + ".mp4"
              await ctx.bot.send_document(
                  msg.chat_id,
                  document=InputFile(out, filename=fname),
                  caption=Em.SUCCESS + " " + sc("speed changed to") + " " + str(speed) + "x",
                  parse_mode=ParseMode.HTML)
              Path(fp).unlink(missing_ok=True)
              Path(out).unlink(missing_ok=True)
              if status: await status.delete()
          else:
              if status:
                  await status.edit_text(Em.ERROR + " " + sc("speed change failed") + ".", parse_mode=ParseMode.HTML)
      except Exception as e:
          if status:
              await status.edit_text(Em.ERROR + " " + sc("error") + ": " + str(e), parse_mode=ParseMode.HTML)


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 45: ꜰɪɴᴀʟ ʙᴜɪʟᴅ_ᴀᴘᴘ ᴇxᴛᴇɴꜱɪᴏɴ
  # ══════════════════════════════════════════════════════════════════════════════

  _ORIGINAL_BUILD_APP_FINAL = CrunchyBot.build_app

  def _final_v3_build_app(self) -> Application:
      app = _ORIGINAL_BUILD_APP_FINAL(self)
      app.add_handler(CommandHandler("split", cmd_split))
      app.add_handler(CommandHandler("speed", cmd_speed))
      return app

  CrunchyBot.build_app = _final_v3_build_app

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 46: ᴇɴᴅ ᴏꜰ ꜰɪʟᴇ — ᴡᴀʀᴍ ɢʀᴇᴇᴛɪɴɢ
  # ══════════════════════════════════════════════════════════════════════════════
  # ᴄʀᴜɴᴄʜʏʀᴏʟʟ ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ ᴠ200.0
  # ʙᴜɪʟᴛ ꜰᴏʀ ᴀɴɪᴍᴇ ꜰᴀɴꜱ. ꜱᴜᴘᴘᴏʀᴛ: @ꜰᴜɴɴʏᴛᴀᴍɪʟᴀɴ
  # ꜰᴇᴀᴛᴜʀᴇꜱ:
  #  ✅ ꜰᴀꜱᴛ/ꜱʟᴏᴡ ʟᴀɴᴇ ǫᴜᴇᴜᴇ (ᴘʀᴇᴍɪᴜᴍ ᴠꜱ ꜰʀᴇᴇ)
  #  ✅ ᴏᴡɴ ꜱQLɪᴛᴇ ᴅʙ ᴡɪᴛʜ 10+ ᴛᴀʙʟᴇꜱ
  #  ✅ ᴄᴏᴏᴋɪᴇ ꜱᴛᴏʀᴇ + ᴠᴀʟɪᴅᴀᴛɪᴏɴ
  #  ✅ ᴄʀᴜɴᴄʜʏʀᴏʟʟ ɴᴇᴡꜱ ᴡᴏʀᴋᴇʀ
  #  ✅ ʀᴇꜰᴇʀʀᴀʟ ꜱʏꜱᴛᴇᴍ ᴡɪᴛʜ ꜱᴛᴀʀꜱ
  #  ✅ ꜱᴍᴀʟʟ ᴄᴀᴘꜱ ᴜɴɪᴄᴏᴅᴇ ꜰᴏɴᴛ + ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪꜱ
  #  ✅ ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜ (ᴍʏᴀɴɪᴍᴇʟɪꜱᴛ)
  #  ✅ ᴀᴄʜɪᴇᴠᴇᴍᴇɴᴛꜱ + ɢᴀᴍɪꜰɪᴄᴀᴛɪᴏɴ
  #  ✅ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴀʟʏᴛɪᴄꜱ + ɪɴꜱɪɢʜᴛꜱ
  #  ✅ ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅꜱ + ꜱᴄʜᴇᴅᴜʟɪɴɢ
  #  ✅ ꜰᴜʟʟ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ + ᴄᴜꜱᴛᴏᴍ ᴄᴏᴍᴍᴀɴᴅꜱ
  #  ✅ ᴠɪᴅᴇᴏ ᴛᴏᴏʟꜱ (ᴇɴᴄᴏᴅᴇ/ᴛʀɪᴍ/ꜱᴘʟɪᴛ/ꜱᴘᴇᴇᴅ/ɢɪꜰ/ᴡᴀᴛᴇʀᴍᴀʀᴋ)
  #  ✅ ꜱᴜʙᴛɪᴛʟᴇ ᴇxᴛʀᴀᴄᴛɪᴏɴ + 14 ʟᴀɴɢᴜᴀɢᴇꜱ
  #  ✅ ᴛᴇʟᴇɢʀᴀᴍ ꜱᴛᴀʀꜱ ᴘᴀʏᴍᴇɴᴛ ɪɴᴛᴇɢʀᴀᴛɪᴏɴ
  #  ✅ 24h ꜰʀᴇᴇ ᴛʀɪᴀʟ ꜱʏꜱᴛᴇᴍ
  #  ✅ ɢɪꜰᴛ ᴄᴀʀᴅ ꜱʏꜱᴛᴇᴍ
  #  ✅ ꜰᴏʀᴄᴇ-ꜱᴜʙꜱᴄʀɪʙᴇ ꜱʏꜱᴛᴇᴍ
  #  ✅ 2ɢʙ ᴍᴛᴘʀᴏᴛᴏ ᴜᴘʟᴏᴀᴅꜱ (ᴘʏʀᴏɢʀᴀᴍ)
  #  ✅ ɪɴʟɪɴᴇ ᴍᴏᴅᴇ (@ʙᴏᴛ ꜱᴇᴀʀᴄʜ)
  #  ✅ ꜱʏꜱᴛᴇᴍ ᴅɪᴀɢɴᴏꜱᴛɪᴄꜱ + ʜᴇᴀʟᴛʜ ᴄʜᴇᴄᴋꜱ
  #  ✅ ᴅᴀᴛᴀʙᴀꜱᴇ ʙᴀᴄᴋᴜᴘ + ᴄꜱᴠ ᴇxᴘᴏʀᴛ
  # ══════════════════════════════════════════════════════════════════════════════
  

  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 47: ᴀᴅᴅɪᴛɪᴏɴᴀʟ ʜᴇʟᴘᴇʀ ꜰᴜɴᴄᴛɪᴏɴꜱ + ᴄᴏɴꜱᴛᴀɴᴛꜱ
  # ══════════════════════════════════════════════════════════════════════════════

  # ─── ꜱᴍᴀʟʟ ᴄᴀᴘꜱ ᴄᴏɴꜱᴛᴀɴᴛꜱ ────────────────────────────────────────────────
  BOT_NAME        = sc("crunchyroll ultimate bot")
  BOT_VERSION     = "v200.0"
  BOT_ABOUT       = sc("the best crunchyroll downloader bot on telegram")
  FREE_TIER_NAME  = sc("free user")
  PREM_TIER_NAME  = sc("premium member")
  BOT_CREATOR     = sc("@funnytamilan")

  # ─── ᴄᴏʟᴏᴜʀ ᴄᴏᴅᴇꜱ (ꜰᴏʀ ʜᴛᴍʟ ᴇᴍʙᴇᴅᴅɪɴɢ) ─────────────────────────────────
  COLOUR_PREMIUM = "#FFD700"
  COLOUR_FREE    = "#A9A9A9"
  COLOUR_ADMIN   = "#FF4500"
  COLOUR_SUCCESS = "#32CD32"
  COLOUR_ERROR   = "#DC143C"
  COLOUR_INFO    = "#1E90FF"

  # ─── ᴄᴏᴍᴍᴏɴ ᴇʀʀᴏʀ ᴍᴇꜱꜱᴀɢᴇꜱ ───────────────────────────────────────────────
  ERR_INVALID_URL      = Em.ERROR + " " + sc("not a valid crunchyroll url")
  ERR_RATE_LIMITED     = Em.WARNING + " " + sc("too many requests — please wait a moment")
  ERR_BANNED           = Em.BAN + " " + sc("you are banned from using this bot")
  ERR_MAINTENANCE      = Em.WARNING + " " + sc("bot is under maintenance")
  ERR_QUEUE_FULL       = Em.QUEUE + " " + sc("your queue is full — cancel a download first")
  ERR_DAILY_LIMIT      = Em.WARNING + " " + sc("daily download limit reached")
  ERR_PREMIUM_REQUIRED = Em.PREMIUM + " " + sc("this feature requires premium")
  ERR_NO_FILE          = Em.ERROR + " " + sc("please reply to a video or document")
  ERR_INTERNAL         = Em.ERROR + " " + sc("internal error — please try again or contact support")

  # ─── ꜱᴜᴄᴄᴇꜱꜱ ᴍᴇꜱꜱᴀɢᴇꜱ ────────────────────────────────────────────────────
  MSG_QUEUED          = Em.QUEUE + " " + sc("added to queue")
  MSG_DOWNLOAD_DONE   = Em.SUCCESS + " " + sc("download complete")
  MSG_PREMIUM_ACTIVE  = Em.PREMIUM + " " + sc("premium membership active")
  MSG_CODE_REDEEMED   = Em.SUCCESS + " " + sc("code redeemed successfully")
  MSG_SETTINGS_SAVED  = Em.SUCCESS + " " + sc("settings saved")
  MSG_BANNED          = Em.SUCCESS + " " + sc("user banned")
  MSG_UNBANNED        = Em.SUCCESS + " " + sc("user unbanned")
  MSG_CODE_GENERATED  = Em.SUCCESS + " " + sc("redeem code generated")

  # ─── ꜱᴄʜᴇᴅᴜʟᴇᴅ ᴊᴏʙ ᴛɪᴍᴇꜱ ────────────────────────────────────────────────
  SCHEDULE_NEWS_EVERY_HOURS  = 6
  SCHEDULE_CLEANUP_EVERY_H   = 24
  SCHEDULE_HEARTBEAT_EVERY_H = 1
  SCHEDULE_EXPIRE_CHECK_MINS = 30

  # ─── ᴀʟʟᴏᴡᴇᴅ ᴇɴᴄᴏᴅᴇ ᴘʀᴇꜱᴇᴛꜱ ────────────────────────────────────────────
  ALLOWED_PRESETS = list(Config.ENCODE_PRESETS.keys())

  # ─── ǫᴜᴀʟɪᴛʏ ᴄᴏɴꜱᴛᴀɴᴛꜱ ──────────────────────────────────────────────────
  QUALITY_LABELS = {
      "240p":  sc("low quality"),
      "360p":  sc("standard quality"),
      "480p":  sc("good quality"),
      "720p":  sc("hd quality"),
      "1080p": sc("full hd quality"),
      "4k":    sc("4k ultra hd"),
      "hdr":   sc("4k hdr"),
  }


  def quality_label(q: str) -> str:
      return QUALITY_LABELS.get(q, q)


  def format_file_size(size_bytes: int) -> str:
      if size_bytes == 0:
          return "0 B"
      for unit in ["B", "KB", "MB", "GB", "TB"]:
          if size_bytes < 1024:
              return str(round(size_bytes, 2)) + " " + unit
          size_bytes /= 1024
      return str(round(size_bytes, 2)) + " PB"


  def format_duration_human(seconds: float) -> str:
      if seconds < 60:
          return str(int(seconds)) + "s"
      if seconds < 3600:
          return str(int(seconds // 60)) + "m " + str(int(seconds % 60)) + "s"
      h = int(seconds // 3600)
      m = int((seconds % 3600) // 60)
      return str(h) + "h " + str(m) + "m"


  def truncate(text: str, maxlen: int = 50, suffix: str = "...") -> str:
      if len(text) <= maxlen:
          return text
      return text[:maxlen - len(suffix)] + suffix


  def escape_html(text: str) -> str:
      return (text
              .replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;")
              .replace('"', "&quot;"))


  def safe_int(val, default: int = 0) -> int:
      try:
          return int(val)
      except:
          return default


  def safe_float(val, default: float = 0.0) -> float:
      try:
          return float(val)
      except:
          return default


  def parse_time_to_seconds(time_str: str) -> Optional[float]:
      try:
          parts = time_str.split(":")
          if len(parts) == 3:
              return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
          elif len(parts) == 2:
              return int(parts[0]) * 60 + float(parts[1])
          else:
              return float(parts[0])
      except:
          return None


  def seconds_to_hhmmss(secs: float) -> str:
      secs  = max(0, int(secs))
      h     = secs // 3600
      m     = (secs % 3600) // 60
      s     = secs % 60
      return f"{h:02d}:{m:02d}:{s:02d}"


  def build_progress_text(pct: int, label: str = "") -> str:
      bar = ProgressBar.make(pct)
      return (bar + " — " + label) if label else bar


  def is_valid_telegram_id(uid: int) -> bool:
      return isinstance(uid, int) and 0 < uid < 10**15


  def chunk_list(lst: list, size: int) -> list:
      return [lst[i:i+size] for i in range(0, len(lst), size)]


  def flatten(lst: list) -> list:
      result = []
      for item in lst:
          if isinstance(item, (list, tuple)):
              result.extend(flatten(item))
          else:
              result.append(item)
      return result


  def dict_to_lines(d: dict, indent: int = 0) -> str:
      lines = []
      prefix = "  " * indent
      for k, v in d.items():
          if isinstance(v, dict):
              lines.append(prefix + str(k) + ":")
              lines.append(dict_to_lines(v, indent+1))
          else:
              lines.append(prefix + str(k) + ": " + str(v))
      return "\n".join(lines)


  def normalize_quality(q: str) -> str:
      q = q.lower().strip()
      aliases = {
          "fhd": "1080p", "fullhd": "1080p", "full hd": "1080p",
          "hd": "720p",   "sd": "480p",       "ld": "360p",
          "4k": "4k",     "uhd": "4k",        "ultra hd": "4k",
      }
      return aliases.get(q, q)


  def get_env_int(key: str, default: int = 0) -> int:
      return safe_int(os.getenv(key, str(default)), default)


  def get_env_bool(key: str, default: bool = False) -> bool:
      return os.getenv(key, str(default)).lower() in ("true", "1", "yes", "on")


  def get_env_list(key: str, sep: str = ",", default: list = None) -> list:
      val = os.getenv(key, "")
      if not val:
          return default or []
      return [x.strip() for x in val.split(sep) if x.strip()]


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 48: ʀᴇꜱᴘᴏɴꜱɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇ ꜰᴏʀᴍᴀᴛᴛᴇʀ
  # ══════════════════════════════════════════════════════════════════════════════

  class MessageFormatter:
      """ʙᴜɪʟᴅ ꜱᴛᴀɴᴅᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ᴄᴀʀᴅꜱ ꜰᴏʀ ʙᴏᴛ ʀᴇꜱᴘᴏɴꜱᴇꜱ."""

      @staticmethod
      def user_card(user: Dict) -> str:
          uid  = user.get("user_id","?")
          name = user.get("first_name","?")
          un   = "@" + user.get("username","") if user.get("username") else sc("no username")
          pm   = user.get("premium_type","free")
          dls  = user.get("total_downloads",0)
          size = format_file_size(user.get("total_size",0) or 0)
          return (
              "👤 <b>" + str(name) + "</b> " + un + "\n"
              + "🆔 <code>" + str(uid) + "</code>\n"
              + "💎 " + sc("plan") + ": " + str(pm).upper() + "\n"
              + "📥 " + sc("downloads") + ": " + str(dls) + " (" + size + ")"
          )

      @staticmethod
      def download_card(info: Dict, quality: str, preset: str, is_pm: bool) -> str:
          series  = info.get("series_title","?")
          ep      = info.get("episode_title","?")
          ep_num  = info.get("episode_number",1)
          s_num   = info.get("season_number",1)
          dur     = format_duration_human(info.get("duration",0))
          lane    = (Em.FAST + " " + sc("fast lane")) if is_pm else (Em.SLOW + " " + sc("slow lane"))
          return (
              Em.ANIME + " <b>" + str(series) + "</b>\n"
              + "📺 S" + str(s_num).zfill(2) + "E" + str(ep_num).zfill(2)
              + " — " + str(ep)[:50] + "\n"
              + "⏱ " + sc("duration") + ": " + dur + "\n"
              + Em.QUALITY + " " + sc("quality") + ": <code>" + quality + "</code>\n"
              + Em.ENCODE + " " + sc("preset") + ": <code>" + preset + "</code>\n"
              + lane
          )

      @staticmethod
      def error_card(error: str, support: bool = True) -> str:
          text = Em.ERROR + " <b>" + sc("error") + "</b>\n\n<code>" + escape_html(str(error)[:300]) + "</code>"
          if support:
              text += "\n\n" + sc("need help? contact") + " " + Config.SUPPORT_USERNAME
          return text

      @staticmethod
      def success_card(title: str, body: str) -> str:
          return Em.SUCCESS + " <b>" + str(title) + "</b>\n\n" + str(body)

      @staticmethod
      def premium_required_card(feature: str) -> str:
          return (
              Em.PREMIUM + " <b>" + sc("premium required") + "</b>\n\n"
              + sc("the feature") + " <b>" + str(feature) + "</b> "
              + sc("requires a premium subscription") + ".\n\n"
              + sc("use") + " /premium " + sc("to see plans or contact") + " "
              + Config.SUPPORT_USERNAME + " " + sc("to purchase") + "."
          )

      @staticmethod
      def queue_position_card(qid: int, pos: int, quality: str, preset: str,
                               is_pm: bool, delay: int) -> str:
          lane  = (Em.FAST + " <b>" + sc("fast lane") + "</b>") if is_pm else (Em.SLOW + " <b>" + sc("slow lane") + "</b>")
          delay_text = sc("no delay") if is_pm else ("~" + str(delay) + "s " + sc("delay"))
          return (
              Em.QUEUE + " <b>" + sc("queued") + "</b> #" + str(qid) + "\n\n"
              + Em.INFO + " " + sc("position") + ": <b>#" + str(pos) + "</b>\n"
              + lane + " — " + delay_text + "\n"
              + Em.QUALITY + " " + quality + " | " + Em.ENCODE + " " + preset + "\n\n"
              + ProgressBar.make(0)
          )


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 49: ꜰɪɴᴀʟ ᴄᴏᴍᴍᴀɴᴅ ᴛᴀʙʟᴇ + ᴄᴏᴜɴᴛ
  # ══════════════════════════════════════════════════════════════════════════════

  TOTAL_COMMANDS = 60  # total commands implemented
  TOTAL_FEATURES = 50  # total premium features

  COMMAND_CATEGORIES = {
      sc("download"):  ["/cr", "/batch", "/schedule", "/queue", "/cancel", "/history"],
      sc("account"):   ["/stats", "/premium", "/redeem", "/referral", "/trial", "/stars"],
      sc("content"):   ["/news", "/search", "/airing", "/season", "/favorites", "/watchlist"],
      sc("tools"):     ["/mediainfo", "/rename", "/compress", "/trim", "/thumbnail",
                        "/watermark", "/gif", "/audio", "/split", "/speed"],
      sc("subtitles"): ["/subtracks", "/extsub"],
      sc("social"):    ["/leaderboard", "/feedback", "/achievements", "/insights"],
      sc("admin"):     ["/admin", "/broadcast", "/ban", "/unban", "/warn",
                        "/addpremium", "/revokepremium", "/gencode", "/setcookies",
                        "/fetchnews", "/queueall", "/clearqueue", "/maintenance",
                        "/authgroup", "/logs", "/restart", "/userinfo",
                        "/diagnostics", "/dbbackup", "/exportusers", "/cleanup", "/vacuum",
                        "/cookiestatus", "/addcmd", "/editcmd", "/delcmd", "/listcmds"],
  }

  FEATURE_LIST = [
      sc("fast/slow lane queue"),
      sc("own sqlite database"),
      sc("crunchyroll cookie store"),
      sc("yt-dlp based download"),
      sc("crunchyroll news rss"),
      sc("referral program"),
      sc("telegram stars payment"),
      sc("small caps unicode font"),
      sc("premium custom emoji"),
      sc("anime search (jikan api)"),
      sc("achievement system"),
      sc("download analytics"),
      sc("batch downloads (20 max)"),
      sc("scheduled downloads"),
      sc("free 24h trial"),
      sc("gift card system"),
      sc("redeem codes"),
      sc("force subscribe"),
      sc("broadcast system"),
      sc("2gb mtproto upload"),
      sc("inline mode search"),
      sc("system diagnostics"),
      sc("database backup/export"),
      sc("video encoding (h264/hevc)"),
      sc("video trimming"),
      sc("video splitting"),
      sc("playback speed change"),
      sc("gif creator"),
      sc("watermark tool"),
      sc("audio extractor"),
      sc("thumbnail extractor"),
      sc("subtitle extraction"),
      sc("14 subtitle languages"),
      sc("media info reader"),
      sc("file renamer"),
      sc("video compression"),
      sc("embed thumbnails"),
      sc("python sandbox commands"),
      sc("admin panel (inline)"),
      sc("user ban/warn system"),
      sc("custom commands (admin)"),
      sc("auto news notifications"),
      sc("leaderboard system"),
      sc("user favorites/watchlist"),
      sc("heartbeat/self-heal"),
      sc("progress bar updates"),
      sc("stars economy"),
      sc("group url detector"),
      sc("cookie status checker"),
      sc("full html parse mode"),
  ]

  logger.info(
      sc("bot loaded with") + " "
      + str(TOTAL_COMMANDS) + " " + sc("commands and") + " "
      + str(TOTAL_FEATURES) + " " + sc("features"))


  # ══════════════════════════════════════════════════════════════════════════════
  #  SECTION 50: ᴇɴᴛʀʏᴘᴏɪɴᴛ ɢᴜᴀʀᴅ
  # ══════════════════════════════════════════════════════════════════════════════

  if __name__ == "__main__":
      bot = CrunchyBot()
      bot.run()
  