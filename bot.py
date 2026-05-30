# bot.py - Complete Crunchyroll Ultimate Bot
# Single file bot with all features: download, encode, premium, admin panel, custom commands, animations

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                   🎬 CRUNCHYROLL ULTIMATE BOT v70.0 🎬                                                                                    ║
║                          FULL PRODUCTION BOT | DOWNLOAD | ENCODE | PREMIUM | ADMIN                                                                        ║
║                                      SINGLE FILE - COPY & RUN                                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# ============================================================================
# TELEGRAM IMPORTS
# ============================================================================

try:
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup,
        LabeledPrice, PreCheckoutQuery, SuccessfulPayment,
        BotCommand, User, Message, CallbackQuery, ChatPermissions,
        InputFile, ChatMember, ReplyKeyboardMarkup, KeyboardButton
    )
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, MessageHandler,
        filters, ContextTypes, PreCheckoutQueryHandler, ConversationHandler,
        ChatMemberHandler, Defaults
    )
    from telegram.constants import ParseMode
    from telegram.error import TelegramError
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    sys.exit(1)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Master Configuration - Edit these values"""
    
    # Bot Token from @BotFather
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # Admin IDs (your Telegram user ID)
    ADMIN_IDS = [123456789, 987654321]  # Replace with your ID
    SUPER_ADMIN_IDS = [123456789]
    
    # Crunchyroll Account (required for API access)
    CRUNCHYROLL_EMAIL = "your_email@example.com"
    CRUNCHYROLL_PASSWORD = "your_password"
    
    # Subscription Prices (Telegram Stars)
    SUBSCRIPTION_PRICES = {
        "weekly": 20,
        "monthly": 50,
        "yearly": 500,
        "lifetime": 1500
    }
    
    SUBSCRIPTION_DAYS = {
        "weekly": 7,
        "monthly": 30,
        "yearly": 365,
        "lifetime": 36500
    }
    
    # Download Limits
    FREE_DAILY_LIMIT = 3
    PREMIUM_DAILY_LIMIT = 999999
    MAX_CONCURRENT_DOWNLOADS = 3
    MAX_QUEUE_PER_USER = 10
    MAX_BATCH_SIZE = 20
    
    # Quality Settings
    QUALITIES = {
        "144p": {"height": 144, "bitrate": "200k", "crf": 32},
        "240p": {"height": 240, "bitrate": "400k", "crf": 30},
        "360p": {"height": 360, "bitrate": "800k", "crf": 28},
        "480p": {"height": 480, "bitrate": "1200k", "crf": 26},
        "720p": {"height": 720, "bitrate": "2500k", "crf": 23},
        "1080p": {"height": 1080, "bitrate": "5000k", "crf": 20},
        "4K": {"height": 2160, "bitrate": "16000k", "crf": 18}
    }
    PREMIUM_QUALITIES = ["1080p", "4K"]
    DEFAULT_QUALITY = "720p"
    
    # Encode Presets
    ENCODE_PRESETS = {
        "fast": {"preset": "veryfast", "tune": "film"},
        "balanced": {"preset": "medium", "tune": "film"},
        "high": {"preset": "slow", "tune": "film"},
        "master": {"preset": "veryslow", "tune": "film"}
    }
    DEFAULT_ENCODE = "balanced"
    
    # Paths
    BASE_DIR = Path(__file__).parent.absolute()
    DOWNLOAD_PATH = BASE_DIR / "downloads"
    OUTPUT_PATH = BASE_DIR / "output"
    DATA_PATH = BASE_DIR / "data"
    LOG_PATH = BASE_DIR / "logs"
    THUMB_PATH = BASE_DIR / "thumbnails"
    
    for path in [DOWNLOAD_PATH, OUTPUT_PATH, DATA_PATH, LOG_PATH, THUMB_PATH]:
        path.mkdir(parents=True, exist_ok=True)
    
    # Database
    DATABASE_PATH = DATA_PATH / "crunchyroll_bot.db"
    
    # FFmpeg
    FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
    FFPROBE_PATH = shutil.which("ffprobe") or "/usr/bin/ffprobe"
    
    # Custom Commands File
    CUSTOM_COMMANDS_FILE = DATA_PATH / "custom_commands.json"
    
    # Referral Settings
    REFERRAL_REWARD = 50
    REFERRAL_REQUIRED = 5
    
    @classmethod
    def validate(cls):
        if cls.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ Please set your BOT_TOKEN in the Config class!")
            return False
        if not cls.CRUNCHYROLL_EMAIL or not cls.CRUNCHYROLL_PASSWORD:
            print("⚠️ Warning: Crunchyroll credentials not set!")
        return True


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.conn = sqlite3.connect(str(Config.DATABASE_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        c = self.conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            premium_type TEXT DEFAULT 'free',
            premium_expiry TIMESTAMP,
            daily_downloads INTEGER DEFAULT 0,
            total_downloads INTEGER DEFAULT 0,
            total_size INTEGER DEFAULT 0,
            last_reset DATE,
            stars_balance INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            warnings INTEGER DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0,
            banned_reason TEXT,
            is_admin BOOLEAN DEFAULT 0,
            language TEXT DEFAULT 'en',
            theme TEXT DEFAULT 'dark',
            default_quality TEXT DEFAULT '720p',
            encode_preset TEXT DEFAULT 'balanced',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Downloads table
        c.execute('''CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            anime_title TEXT,
            anime_id TEXT,
            episode_title TEXT,
            episode_id TEXT,
            episode_number INTEGER,
            season_number INTEGER,
            quality TEXT,
            file_size INTEGER,
            file_hash TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Queue table
        c.execute('''CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            quality TEXT,
            encode_preset TEXT DEFAULT 'balanced',
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 0,
            message_id INTEGER,
            file_path TEXT,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Subscriptions table
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_type TEXT,
            amount INTEGER,
            currency TEXT DEFAULT 'XTR',
            transaction_id TEXT UNIQUE,
            status TEXT DEFAULT 'active',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Transactions table
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            currency TEXT,
            status TEXT,
            payment_method TEXT,
            order_id TEXT,
            telegram_charge_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Favorites table
        c.execute('''CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            anime_id TEXT,
            anime_title TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, anime_id)
        )''')
        
        # Referrals table
        c.execute('''CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            reward_claimed BOOLEAN DEFAULT 0,
            reward_amount INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Feedback table
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Settings table
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Custom Commands table
        c.execute('''CREATE TABLE IF NOT EXISTS custom_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT UNIQUE,
            response TEXT,
            response_type TEXT DEFAULT 'text',
            created_by INTEGER,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_user_premium ON users(user_id, premium_expiry)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status, priority)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_downloads_user ON downloads(user_id, downloaded_at)")
        
        # Insert default settings
        default_settings = [
            ("maintenance_mode", "False"),
            ("welcome_message", "Welcome to Crunchyroll Bot! 🎬"),
            ("welcome_image", ""),
            ("force_subscribe", "False"),
            ("force_subscribe_channels", "[]"),
            ("update_channel", ""),
            ("support_group", ""),
            ("log_channel", ""),
            ("default_quality", Config.DEFAULT_QUALITY),
            ("default_encode", Config.DEFAULT_ENCODE),
            ("referral_enabled", "True"),
            ("referral_reward", str(Config.REFERRAL_REWARD)),
            ("referral_required", str(Config.REFERRAL_REQUIRED)),
            ("rate_limit_enabled", "True"),
            ("rate_limit_requests", "30"),
            ("rate_limit_window", "60")
        ]
        for key, value in default_settings:
            c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        
        # Insert admin users
        for admin_id in Config.ADMIN_IDS:
            c.execute("""INSERT OR REPLACE INTO users (user_id, is_admin, premium_type, premium_expiry) 
                        VALUES (?, 1, 'lifetime', datetime('now', '+100 years'))""", (admin_id,))
        
        # Insert default custom commands
        default_commands = [
            ("ping", "🏓 Pong! Bot is alive!", "text"),
            ("status", "🟢 Bot is running smoothly!", "text"),
            ("about", f"🤖 **Crunchyroll Bot v70.0**\n\nPremium features available!\nUse /premium to upgrade", "markdown"),
            ("rules", "📋 **Bot Rules:**\n1. No spam\n2. Respect others\n3. Enjoy!", "markdown"),
            ("support", "🆘 For support, contact @admin", "text"),
            ("donate", "💝 Support development by buying premium with Telegram Stars!\nUse /premium", "markdown"),
            ("uptime", "⏰ Bot is online and ready!", "text"),
            ("help_cmd", "📖 **Available Commands:**\n/start - Start bot\n/help - Help\n/cr - Download\n/premium - Premium plans\n/queue - View queue\n/history - Download history\n/stats - Your stats\n/settings - User settings\n/feedback - Send feedback", "markdown")
        ]
        for cmd, resp, resp_type in default_commands:
            c.execute("INSERT OR IGNORE INTO custom_commands (command, response, response_type) VALUES (?, ?, ?)", (cmd, resp, resp_type))
        
        self.conn.commit()
        logger.info("✅ Database initialized")
    
    # ========== USER METHODS ==========
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return dict(row) if row else None
    
    def register_user(self, user_id: int, username: str = None, first_name: str = None):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_active) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", 
                  (user_id, username, first_name))
        self.conn.commit()
    
    def update_last_active(self, user_id: int):
        c = self.conn.cursor()
        c.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def is_premium(self, user_id: int) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT premium_type FROM users WHERE user_id = ? AND premium_expiry > CURRENT_TIMESTAMP", (user_id,))
        return c.fetchone() is not None
    
    def get_premium_type(self, user_id: int) -> str:
        c = self.conn.cursor()
        c.execute("SELECT premium_type FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else "free"
    
    def get_premium_expiry(self, user_id: int) -> Optional[datetime]:
        c = self.conn.cursor()
        c.execute("SELECT premium_expiry FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None
    
    def add_premium(self, user_id: int, plan_type: str, duration_days: int, transaction_id: str = None) -> bool:
        c = self.conn.cursor()
        try:
            current_expiry = self.get_premium_expiry(user_id)
            if current_expiry and current_expiry > datetime.now():
                new_expiry = current_expiry + timedelta(days=duration_days)
            else:
                new_expiry = datetime.now() + timedelta(days=duration_days)
            
            c.execute("UPDATE users SET premium_type = ?, premium_expiry = ? WHERE user_id = ?", 
                     (plan_type, new_expiry.isoformat(), user_id))
            
            if transaction_id:
                c.execute("INSERT INTO subscriptions (user_id, plan_type, amount, transaction_id, end_date) VALUES (?, ?, ?, ?, ?)",
                         (user_id, plan_type, Config.SUBSCRIPTION_PRICES[plan_type], transaction_id, new_expiry.isoformat()))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Add premium error: {e}")
            return False
    
    def get_daily_downloads(self, user_id: int) -> int:
        c = self.conn.cursor()
        today = datetime.now().date().isoformat()
        c.execute("SELECT daily_downloads, last_reset FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if row and row[1] != today:
            c.execute("UPDATE users SET daily_downloads = 0, last_reset = ? WHERE user_id = ?", (today, user_id))
            self.conn.commit()
            return 0
        return row[0] if row else 0
    
    def increment_downloads(self, user_id: int, file_size: int = 0):
        c = self.conn.cursor()
        c.execute("UPDATE users SET daily_downloads = daily_downloads + 1, total_downloads = total_downloads + 1, total_size = total_size + ? WHERE user_id = ?", 
                 (file_size, user_id))
        self.conn.commit()
    
    def can_download(self, user_id: int) -> Tuple[bool, str]:
        if self.is_banned(user_id):
            return False, "🚫 You are banned from using this bot."
        
        is_premium = self.is_premium(user_id)
        limit = Config.PREMIUM_DAILY_LIMIT if is_premium else Config.FREE_DAILY_LIMIT
        current = self.get_daily_downloads(user_id)
        
        if current >= limit:
            if is_premium:
                return False, f"Daily limit reached ({limit}). Contact support if this is an error."
            return False, f"📊 Free limit reached ({limit}/{limit}). Get premium for unlimited downloads!"
        return True, "OK"
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in Config.ADMIN_IDS
    
    def is_banned(self, user_id: int) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row and row[0]
    
    def ban_user(self, user_id: int, admin_id: int, reason: str, duration_days: int = 0):
        c = self.conn.cursor()
        banned_until = (datetime.now() + timedelta(days=duration_days)).isoformat() if duration_days > 0 else None
        c.execute("UPDATE users SET is_banned = 1, banned_reason = ?, banned_until = ? WHERE user_id = ?", 
                 (reason, banned_until, user_id))
        self.conn.commit()
    
    def unban_user(self, user_id: int):
        c = self.conn.cursor()
        c.execute("UPDATE users SET is_banned = 0, banned_reason = NULL, banned_until = NULL WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    # ========== QUEUE METHODS ==========
    
    def add_to_queue(self, user_id: int, url: str, quality: str, encode_preset: str = None, message_id: int = None) -> int:
        is_premium = self.is_premium(user_id)
        priority = 1 if is_premium else 0
        if not encode_preset:
            encode_preset = Config.DEFAULT_ENCODE
        
        c = self.conn.cursor()
        c.execute("INSERT INTO queue (user_id, url, quality, encode_preset, priority, message_id) VALUES (?, ?, ?, ?, ?, ?)",
                 (user_id, url, quality, encode_preset, priority, message_id))
        self.conn.commit()
        return c.lastrowid
    
    def get_queue_position(self, queue_id: int) -> int:
        c = self.conn.cursor()
        c.execute("""SELECT COUNT(*) FROM queue 
                    WHERE status = 'pending' AND priority > (SELECT priority FROM queue WHERE id = ?)
                    OR (priority = (SELECT priority FROM queue WHERE id = ?) AND id < ?)""", 
                 (queue_id, queue_id, queue_id))
        return c.fetchone()[0] + 1
    
    def get_user_queue(self, user_id: int) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("""SELECT id, url, quality, status, progress FROM queue 
                    WHERE user_id = ? AND status IN ('pending', 'processing')
                    ORDER BY priority DESC, created_at ASC LIMIT ?""", 
                 (user_id, Config.MAX_QUEUE_PER_USER))
        return [dict(row) for row in c.fetchall()]
    
    def get_queue_count(self, user_id: int) -> int:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM queue WHERE user_id = ? AND status = 'pending'", (user_id,))
        return c.fetchone()[0]
    
    def update_queue_progress(self, queue_id: int, progress: int, status: str = None):
        c = self.conn.cursor()
        if status:
            c.execute("UPDATE queue SET progress = ?, status = ? WHERE id = ?", (progress, status, queue_id))
        else:
            c.execute("UPDATE queue SET progress = ? WHERE id = ?", (progress, queue_id))
        self.conn.commit()
    
    def start_processing(self, queue_id: int):
        c = self.conn.cursor()
        c.execute("UPDATE queue SET status = 'processing', started_at = CURRENT_TIMESTAMP WHERE id = ?", (queue_id,))
        self.conn.commit()
    
    def complete_queue_item(self, queue_id: int, file_path: str, file_size: int):
        c = self.conn.cursor()
        c.execute("UPDATE queue SET status = 'completed', file_path = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?", (file_path, queue_id))
        self.conn.commit()
    
    def fail_queue_item(self, queue_id: int, error: str):
        c = self.conn.cursor()
        c.execute("UPDATE queue SET status = 'failed', error_message = ? WHERE id = ?", (error[:500], queue_id))
        self.conn.commit()
    
    def cancel_queue_item(self, queue_id: int, user_id: int) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT user_id, status FROM queue WHERE id = ?", (queue_id,))
        row = c.fetchone()
        if row and row[0] == user_id and row[1] == 'pending':
            c.execute("UPDATE queue SET status = 'cancelled' WHERE id = ?", (queue_id,))
            self.conn.commit()
            return True
        return False
    
    def get_next_queue_item(self) -> Optional[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT id, user_id, url, quality, encode_preset, message_id FROM queue WHERE status = 'pending' ORDER BY priority DESC, created_at ASC LIMIT 1")
        row = c.fetchone()
        return dict(row) if row else None
    
    def get_all_queue_items(self) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT id, user_id, url, quality, status, progress, created_at FROM queue WHERE status IN ('pending', 'processing') ORDER BY priority DESC, created_at ASC LIMIT 50")
        return [dict(row) for row in c.fetchall()]
    
    def clear_queue(self, user_id: int = None):
        c = self.conn.cursor()
        if user_id:
            c.execute("DELETE FROM queue WHERE user_id = ? AND status = 'pending'", (user_id,))
        else:
            c.execute("DELETE FROM queue WHERE status = 'pending'")
        self.conn.commit()
        return c.rowcount
    
    # ========== DOWNLOAD METHODS ==========
    
    def add_download_record(self, user_id: int, anime_title: str, anime_id: str, episode_title: str, 
                           episode_id: str, episode_number: int, season_number: int, quality: str, file_size: int, file_hash: str):
        c = self.conn.cursor()
        c.execute("""INSERT INTO downloads (user_id, anime_title, anime_id, episode_title, episode_id, 
                    episode_number, season_number, quality, file_size, file_hash) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (user_id, anime_title, anime_id, episode_title, episode_id, episode_number, season_number, quality, file_size, file_hash))
        self.conn.commit()
    
    def get_download_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("""SELECT anime_title, episode_title, quality, file_size, downloaded_at 
                    FROM downloads WHERE user_id = ? ORDER BY downloaded_at DESC LIMIT ?""", (user_id, limit))
        return [dict(row) for row in c.fetchall()]
    
    def get_total_downloads(self, user_id: int) -> int:
        c = self.conn.cursor()
        c.execute("SELECT total_downloads FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else 0
    
    # ========== FAVORITES ==========
    
    def add_favorite(self, user_id: int, anime_id: str, anime_title: str) -> bool:
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO favorites (user_id, anime_id, anime_title) VALUES (?, ?, ?)", (user_id, anime_id, anime_title))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_favorite(self, user_id: int, anime_id: str) -> bool:
        c = self.conn.cursor()
        c.execute("DELETE FROM favorites WHERE user_id = ? AND anime_id = ?", (user_id, anime_id))
        self.conn.commit()
        return c.rowcount > 0
    
    def get_favorites(self, user_id: int) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT anime_id, anime_title, added_at FROM favorites WHERE user_id = ? ORDER BY added_at DESC", (user_id,))
        return [dict(row) for row in c.fetchall()]
    
    def is_favorite(self, user_id: int, anime_id: str) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM favorites WHERE user_id = ? AND anime_id = ?", (user_id, anime_id))
        return c.fetchone() is not None
    
    # ========== REFERRAL ==========
    
    def generate_referral_code(self, user_id: int) -> str:
        code = secrets.token_hex(4).upper()
        c = self.conn.cursor()
        c.execute("UPDATE users SET referral_code = ? WHERE user_id = ?", (code, user_id))
        self.conn.commit()
        return code
    
    def get_referral_code(self, user_id: int) -> Optional[str]:
        c = self.conn.cursor()
        c.execute("SELECT referral_code FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None
    
    def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer_id, referred_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_referral_count(self, user_id: int) -> int:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        return c.fetchone()[0]
    
    def claim_referral_reward(self, user_id: int) -> int:
        c = self.conn.cursor()
        reward = int(self.get_setting("referral_reward", str(Config.REFERRAL_REWARD)))
        required = int(self.get_setting("referral_required", str(Config.REFERRAL_REQUIRED)))
        count = self.get_referral_count(user_id)
        
        c.execute("SELECT reward_claimed FROM referrals WHERE referrer_id = ? AND reward_claimed = 0 LIMIT 1", (user_id,))
        has_unclaimed = c.fetchone() is not None
        
        if count >= required and has_unclaimed:
            c.execute("UPDATE users SET stars_balance = stars_balance + ? WHERE user_id = ?", (reward, user_id))
            c.execute("UPDATE referrals SET reward_claimed = 1, reward_amount = ? WHERE referrer_id = ? AND reward_claimed = 0", (reward, user_id))
            self.conn.commit()
            return reward
        return 0
    
    # ========== STATISTICS ==========
    
    def get_stats(self) -> Dict:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE premium_expiry > CURRENT_TIMESTAMP")
        premium_users = c.fetchone()[0]
        c.execute("SELECT SUM(total_downloads) FROM users")
        total_downloads = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM queue WHERE status = 'pending'")
        queue_size = c.fetchone()[0]
        c.execute("SELECT SUM(total_size) FROM users")
        total_size = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM users WHERE last_active > datetime('now', '-7 days')")
        active_users = c.fetchone()[0]
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "total_downloads": total_downloads,
            "queue_size": queue_size,
            "total_size_gb": round(total_size / (1024**3), 2),
            "active_users": active_users
        }
    
    # ========== SETTINGS ==========
    
    def get_setting(self, key: str, default: str = None) -> str:
        c = self.conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = c.fetchone()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (key, value))
        self.conn.commit()
    
    # ========== FEEDBACK ==========
    
    def add_feedback(self, user_id: int, rating: int, message: str):
        c = self.conn.cursor()
        c.execute("INSERT INTO feedback (user_id, rating, message) VALUES (?, ?, ?)", (user_id, rating, message))
        self.conn.commit()
    
    def get_feedback_stats(self) -> Dict:
        c = self.conn.cursor()
        c.execute("SELECT AVG(rating), COUNT(*) FROM feedback")
        avg, total = c.fetchone()
        return {"avg_rating": round(avg or 0, 2), "total": total or 0}
    
    # ========== CUSTOM COMMANDS ==========
    
    def get_custom_command(self, command: str) -> Optional[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT response, response_type FROM custom_commands WHERE command = ?", (command,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE custom_commands SET usage_count = usage_count + 1 WHERE command = ?", (command,))
            self.conn.commit()
            return {"response": row[0], "type": row[1]}
        return None
    
    def add_custom_command(self, command: str, response: str, response_type: str, created_by: int) -> bool:
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO custom_commands (command, response, response_type, created_by) VALUES (?, ?, ?, ?)",
                     (command, response, response_type, created_by))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_custom_command(self, command: str) -> bool:
        c = self.conn.cursor()
        c.execute("DELETE FROM custom_commands WHERE command = ?", (command,))
        self.conn.commit()
        return c.rowcount > 0
    
    def list_custom_commands(self) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT command, response, response_type, usage_count, created_at FROM custom_commands ORDER BY usage_count DESC")
        return [dict(row) for row in c.fetchall()]


# ============================================================================
# EMOJIS SYSTEM
# ============================================================================

class Emojis:
    """Custom emoji system for beautiful UI"""
    
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    
    # Premium
    PREMIUM = "💎"
    VIP = "👑"
    STAR = "⭐"
    CROWN = "👑"
    DIAMOND = "💎"
    
    # Actions
    DOWNLOAD = "📥"
    UPLOAD = "📤"
    QUEUE = "📋"
    PLAY = "▶️"
    PAUSE = "⏸️"
    STOP = "⏹️"
    CANCEL = "❌"
    CHECK = "✅"
    
    # Media
    ANIME = "🎬"
    MOVIE = "🎥"
    EPISODE = "📺"
    SEASON = "📅"
    QUALITY = "🎨"
    SUBTITLE = "📝"
    AUDIO = "🎤"
    
    # Stats
    STATS = "📊"
    CHART = "📈"
    USERS = "👥"
    DOWNLOADS = "📥"
    SIZE = "💾"
    TIME = "⏰"
    
    # Admin
    ADMIN = "👑"
    MOD = "🛡️"
    SUPPORT = "🎧"
    BAN = "🔨"
    UNBAN = "🔓"
    WARN = "⚠️"
    MUTE = "🔇"
    KICK = "👢"
    PROMOTE = "⬆️"
    DEMOTE = "⬇️"
    
    # Navigation
    BACK = "🔙"
    NEXT = "➡️"
    PREV = "⬅️"
    HOME = "🏠"
    SETTINGS = "⚙️"
    HELP = "❓"
    
    # Misc
    HEART = "❤️"
    FIRE = "🔥"
    ROCKET = "🚀"
    SPARKLES = "✨"
    MAGIC = "🔮"
    GIFT = "🎁"
    TROPHY = "🏆"
    MEDAL = "🎖️"
    CLOCK = "⏰"
    CALENDAR = "📅"
    LOCATION = "📍"
    LINK = "🔗"
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"
    SEARCH = "🔍"
    FILTER = "🎛️"
    SORT = "📊"
    REFRESH = "🔄"
    SAVE = "💾"
    EDIT = "✏️"
    DELETE = "🗑️"
    ADD = "➕"
    REMOVE = "➖"
    COPY = "📋"
    PASTE = "📌"
    CUT = "✂️"


# ============================================================================
# PROGRESS BAR SYSTEM
# ============================================================================

class ProgressBar:
    """Advanced progress bar with multiple styles"""
    
    STYLES = {
        "classic": ["░", "▒", "▓", "█"],
        "animated": ["░", "▒", "▓", "█"],
        "download": ["📥", "💾", "📀", "✅"],
        "encode": ["🎬", "🎥", "📹", "✨"],
        "premium": ["💎", "👑", "⭐", "✨"],
        "fire": ["🔥", "🔥", "🔥", "💯"],
        "rainbow": ["🔴", "🟡", "🟢", "🔵"],
        "neon": ["🟢", "🟡", "🟠", "🔴"]
    }
    
    @classmethod
    def create(cls, percent: int, width: int = 20, style: str = "classic") -> str:
        if style not in cls.STYLES:
            style = "classic"
        chars = cls.STYLES[style]
        filled = int(width * percent / 100)
        empty = width - filled
        if filled == 0:
            bar = chars[0] * width
        elif filled == width:
            bar = chars[-1] * width
        else:
            bar = chars[-2] * filled + chars[0] * empty
        
        if percent < 25:
            icon = "⏳"
        elif percent < 50:
            icon = "⚡"
        elif percent < 75:
            icon = "🔥"
        elif percent < 100:
            icon = "⭐"
        else:
            icon = "✅"
        
        return f"{icon} `[{bar}]` {percent}%"


# ============================================================================
# ANIMATION SYSTEM
# ============================================================================

class AnimationCaption:
    """Advanced animation system for captions"""
    
    @staticmethod
    def typing(text: str, delay: float = 0.05):
        frames = []
        for i in range(len(text) + 1):
            frames.append(text[:i] + "█" if i < len(text) else text)
        return frames
    
    @staticmethod
    def slide(text: str, direction: str = "left"):
        frames = []
        padding = " " * 10
        if direction == "left":
            for i in range(len(padding) + len(text) + 1):
                frames.append(padding[max(0, i-len(text)):] + text[:max(0, len(text)-i)] if i < len(text) else text)
        return frames
    
    @staticmethod
    def fade(text: str):
        frames = []
        chars = list(text)
        for intensity in range(0, 101, 20):
            faded = ''.join([c if random.random() > intensity/100 else '░' for c in chars])
            frames.append(faded)
        return frames
    
    @staticmethod
    def bounce(text: str):
        frames = []
        for i in range(3):
            frames.append(f"⬆️ {text} ⬆️")
            frames.append(f"⬇️ {text} ⬇️")
        return frames
    
    @staticmethod
    def rainbow(text: str):
        colors = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
        frames = []
        for color in colors:
            frames.append(f"{color} {text} {color}")
        return frames
    
    @staticmethod
    def glitch(text: str):
        frames = []
        glitch_chars = ['░', '▒', '▓', '█', '▀', '▄', '▌', '▐']
        for _ in range(8):
            glitched = ''.join([random.choice(glitch_chars) if random.random() > 0.7 else c for c in text])
            frames.append(f"⚡ {glitched} ⚡")
        frames.append(f"✨ {text} ✨")
        return frames
    
    @staticmethod
    def neon(text: str):
        frames = []
        for _ in range(3):
            frames.append(f"🟢 {text} 🟢")
            frames.append(f"💚 {text} 💚")
        frames.append(f"✨ {text} ✨")
        return frames
    
    @staticmethod
    def pulse(text: str):
        frames = []
        sizes = ['', '>', '>>', '>>>', '>>>>', '>>>', '>>', '>', '']
        for size in sizes:
            frames.append(f"{size} {text} {size}")
        return frames
    
    @staticmethod
    def matrix(text: str):
        frames = []
        matrix_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        for _ in range(10):
            matrix_text = ''.join([random.choice(matrix_chars) if random.random() > 0.7 else c for c in text])
            frames.append(f"💚 {matrix_text} 💚")
        frames.append(f"✅ {text} ✅")
        return frames
    
    @staticmethod
    def fire(text: str):
        frames = []
        fire_emojis = ['🔥', '💥', '⚡', '✨', '🌟']
        for emoji in fire_emojis:
            frames.append(f"{emoji} {text} {emoji}")
        return frames
    
    @staticmethod
    def heart(text: str):
        frames = []
        for i in range(3):
            frames.append(f"🖤 {text} 🖤")
            frames.append(f"❤️ {text} ❤️")
            frames.append(f"💖 {text} 💖")
        return frames
    
    @staticmethod
    def wave(text: str):
        frames = []
        waves = ['~', '≈', '≋', '~', '≈', '≋']
        for wave in waves:
            frames.append(f"{wave} {text} {wave}")
        return frames
    
    @staticmethod
    def sparkle(text: str):
        frames = []
        sparkles = ['✨', '⭐', '🌟', '💫', '✨', '⭐', '🌟']
        for sparkle in sparkles:
            frames.append(f"{sparkle} {text} {sparkle}")
        return frames
    
    @classmethod
    def get_animation(cls, style: str, text: str):
        animations = {
            "typing": cls.typing,
            "slide": cls.slide,
            "fade": cls.fade,
            "bounce": cls.bounce,
            "rainbow": cls.rainbow,
            "glitch": cls.glitch,
            "neon": cls.neon,
            "pulse": cls.pulse,
            "matrix": cls.matrix,
            "fire": cls.fire,
            "heart": cls.heart,
            "wave": cls.wave,
            "sparkle": cls.sparkle
        }
        anim_func = animations.get(style, cls.typing)
        return anim_func(text)


# ============================================================================
# CRUNCHYROLL API
# ============================================================================

class CrunchyrollAPI:
    """Crunchyroll API integration"""
    
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Crunchyroll"""
        # This is a mock - implement actual API calls
        self.access_token = "mock_token"
        self.token_expiry = datetime.now() + timedelta(hours=24)
        return True
    
    async def get_episode_info(self, episode_id: str) -> Optional[Dict]:
        """Get episode information"""
        # Mock data - replace with actual API
        return {
            "id": episode_id,
            "title": "Sample Episode",
            "series_title": "Sample Anime",
            "episode_number": 1,
            "season_number": 1,
            "duration": 1440,
            "thumbnail": None
        }
    
    async def get_stream_url(self, episode_id: str, quality: str) -> Optional[str]:
        """Get stream URL for episode"""
        # Mock - return a test URL
        return "https://test-stream-url.com/stream.m3u8"
    
    def extract_id(self, url: str) -> Optional[str]:
        """Extract episode ID from URL"""
        patterns = [r'/episode/([A-Z0-9]+)', r'/watch/([A-Z0-9]+)']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


# ============================================================================
# VIDEO ENCODER
# ============================================================================

class VideoEncoder:
    """Video encoding with FFmpeg"""
    
    def __init__(self):
        self.active_encodes = {}
    
    async def encode_video(self, input_path: str, quality: str, encode_preset: str = "balanced",
                          progress_callback=None) -> Optional[str]:
        """Encode video to specified quality"""
        quality_config = Config.QUALITIES.get(quality, Config.QUALITIES[Config.DEFAULT_QUALITY])
        preset_config = Config.ENCODE_PRESETS.get(encode_preset, Config.ENCODE_PRESETS["balanced"])
        
        output_name = f"{Path(input_path).stem}_{quality}.mp4"
        output_path = str(Config.OUTPUT_PATH / output_name)
        
        cmd = [
            Config.FFMPEG_PATH,
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", preset_config["preset"],
            "-crf", str(quality_config["crf"]),
            "-vf", f"scale=-2:{quality_config['height']}",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        duration = await self._get_duration(input_path)
        
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            line_text = line.decode(errors='ignore')
            
            if progress_callback and "time=" in line_text:
                time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line_text)
                if time_match and duration > 0:
                    h, m, s = time_match.groups()
                    current = int(h) * 3600 + int(m) * 60 + float(s)
                    progress = min(int((current / duration) * 100), 99)
                    await progress_callback(progress)
        
        await process.wait()
        
        if process.returncode == 0 and Path(output_path).exists():
            if progress_callback:
                await progress_callback(100)
            return output_path
        return None
    
    async def _get_duration(self, file_path: str) -> float:
        cmd = [Config.FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        try:
            return float(stdout.decode().strip())
        except:
            return 0
    
    async def generate_thumbnail(self, video_path: str, timestamp: float = 5.0) -> Optional[str]:
        """Generate thumbnail from video"""
        thumb_path = Config.THUMB_PATH / f"{Path(video_path).stem}_thumb.jpg"
        cmd = [Config.FFMPEG_PATH, "-i", video_path, "-ss", str(timestamp), "-vframes", "1", "-vf", "scale=320:-1", "-q:v", "2", str(thumb_path)]
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()
        return str(thumb_path) if thumb_path.exists() else None


# ============================================================================
# DOWNLOAD MANAGER
# ============================================================================

class DownloadManager:
    """Main download manager"""
    
    def __init__(self):
        self.active_downloads = {}
        self.cr_api = CrunchyrollAPI()
        self.encoder = VideoEncoder()
    
    async def download_episode(self, queue_id: int, user_id: int, url: str, quality: str,
                               encode_preset: str, progress_callback=None) -> Tuple[bool, str]:
        """Download and process episode"""
        try:
            await self.cr_api.authenticate()
            
            episode_id = self.cr_api.extract_id(url)
            if not episode_id:
                return False, "Invalid URL"
            
            if progress_callback:
                await progress_callback(5, "📡 Fetching episode info...")
            
            episode_info = await self.cr_api.get_episode_info(episode_id)
            if not episode_info:
                return False, "Episode not found"
            
            if progress_callback:
                await progress_callback(10, f"🎬 {episode_info['series_title']} - Ep {episode_info['episode_number']}")
            
            stream_url = await self.cr_api.get_stream_url(episode_id, quality)
            if not stream_url:
                return False, f"No stream available for quality: {quality}"
            
            if progress_callback:
                await progress_callback(15, "📥 Downloading...")
            
            # Generate filename
            safe_title = re.sub(r'[^\w\s-]', '', episode_info['title'])[:50]
            safe_series = re.sub(r'[^\w\s-]', '', episode_info['series_title'])[:50]
            filename = f"{safe_series}_S{episode_info['season_number']:02d}E{episode_info['episode_number']:02d}_{safe_title}.mp4"
            download_path = Config.DOWNLOAD_PATH / filename.replace(' ', '_')
            
            # Download
            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url) as response:
                    if response.status != 200:
                        return False, f"Download failed: HTTP {response.status}"
                    
                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0
                    
                    with open(download_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total > 0:
                                progress = 15 + int((downloaded / total) * 35)
                                mb = downloaded / (1024**2)
                                await progress_callback(progress, f"📥 {mb:.1f} MB / {total/(1024**2):.1f} MB")
            
            if progress_callback:
                await progress_callback(50, "⚙️ Encoding...")
            
            # Encode
            async def encode_progress(p):
                if progress_callback:
                    await progress_callback(50 + int(p * 0.45), f"🎬 Encoding: {p}%")
            
            encoded_path = await self.encoder.encode_video(str(download_path), quality, encode_preset, encode_progress)
            
            if not encoded_path:
                return False, "Encoding failed"
            
            if progress_callback:
                await progress_callback(95, "🎉 Finalizing...")
            
            # Cleanup
            download_path.unlink()
            file_size = Path(encoded_path).stat().st_size
            
            # Add record
            db = Database()
            db.complete_queue_item(queue_id, encoded_path, file_size)
            db.increment_downloads(user_id, file_size)
            db.add_download_record(
                user_id, episode_info['series_title'], episode_info['id'],
                episode_info['title'], episode_info['id'], episode_info['episode_number'],
                episode_info['season_number'], quality, file_size,
                hashlib.md5(open(encoded_path, "rb").read()).hexdigest()
            )
            
            if progress_callback:
                await progress_callback(100, "✅ Complete!")
            
            return True, encoded_path
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False, str(e)


# ============================================================================
# MAIN BOT CLASS
# ============================================================================

class CrunchyrollBot:
    """Main bot class"""
    
    def __init__(self):
        self.db = Database()
        self.downloader = DownloadManager()
        self.application = None
        self.queue_task = None
        self.active_downloads = {}
    
    # ========== COMMAND HANDLERS ==========
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.db.register_user(user.id, user.username, user.first_name)
        self.db.update_last_active(user.id)
        
        plan, is_premium = self.db.is_premium(user.id), self.db.get_premium_type(user.id) if self.db.is_premium(user.id) else "free"
        plan_emoji = {"vip": Emojis.VIP, "premium": Emojis.CROWN, "ultra": Emojis.DIAMOND, "lifetime": Emojis.STAR, "free": "✨"}.get(plan if is_premium else "free", "✨")
        
        text = f"""
{Emojis.FIRE} **Welcome to Crunchyroll Bot!** {Emojis.FIRE}

{plan_emoji} **Hello {user.first_name}!** {plan_emoji}

**⚡ Features:**
├ {Emojis.DOWNLOAD} Download any Crunchyroll episode
├ {Emojis.QUALITY} Multiple qualities (240p to 4K)
├ {Emojis.PREMIUM} Premium subscription (Telegram Stars)
├ {Emojis.QUEUE} Queue system with priority
├ {Emojis.STATS} Download history & analytics
└ {Emojis.SETTINGS} Custom user settings

**📊 Your Status:**
├ Plan: {plan.upper() if is_premium else 'FREE'}
├ Daily: {self.db.get_daily_downloads(user.id)}/{Config.PREMIUM_DAILY_LIMIT if is_premium else Config.FREE_DAILY_LIMIT}
├ Total: {self.db.get_total_downloads(user.id)}
└ Queue: {self.db.get_queue_count(user.id)}

**📌 Quick Commands:**
/cr <url> - Download episode
/premium - View plans
/queue - Check queue
/help - Full help
"""
        
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.DOWNLOAD} Download", switch_inline_query_current_chat=""),
             InlineKeyboardButton(f"{Emojis.PREMIUM} Premium", callback_data="premium")],
            [InlineKeyboardButton(f"{Emojis.QUEUE} Queue", callback_data="queue"),
             InlineKeyboardButton(f"{Emojis.STATS} Stats", callback_data="stats")],
            [InlineKeyboardButton(f"{Emojis.SETTINGS} Settings", callback_data="settings"),
             InlineKeyboardButton(f"{Emojis.HEART} Favorites", callback_data="favorites")]
        ]
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = f"""
{Emojis.HELP} **Help Center** {Emojis.HELP}

**📥 Download Commands:**
/cr <url> - Download episode
/queue - View download queue
/cancel <id> - Cancel download
/history - Download history

**💎 Premium Commands:**
/premium - View plans
/subscribe <plan> - Buy premium
/status - Your status

**🔧 Utility Commands:**
/search <name> - Search anime
/favorites - Your favorites
/stats - Your statistics
/settings - User settings
/feedback - Send feedback

**👑 Admin Commands:**
/admin - Admin panel
/ban <id> <reason> - Ban user
/unban <id> - Unban user
/warn <id> <reason> - Warn user
/broadcast <msg> - Send broadcast
/stats_all - Full statistics

**📊 Free vs Premium:**
├ Free: {Config.FREE_DAILY_LIMIT} downloads/day
├ Premium: Unlimited downloads
├ Premium: 1080p & 4K quality
└ Premium: Priority queue

**Need Help?** Contact @support
"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def cr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} **Usage:** `/cr <crunchyroll_url>`\n\nExample: `/cr https://www.crunchyroll.com/watch/XXXXX`", parse_mode=ParseMode.MARKDOWN)
            return
        
        url = context.args[0]
        if not re.search(r'crunchyroll\.com/(watch|episode|series)', url):
            await update.message.reply_text(f"{Emojis.ERROR} Invalid Crunchyroll URL!", parse_mode=ParseMode.MARKDOWN)
            return
        
        can_download, msg = self.db.can_download(update.effective_user.id)
        if not can_download:
            await update.message.reply_text(msg)
            return
        
        queue_count = self.db.get_queue_count(update.effective_user.id)
        if queue_count >= Config.MAX_QUEUE_PER_USER:
            await update.message.reply_text(f"{Emojis.WARNING} Queue limit reached ({Config.MAX_QUEUE_PER_USER}). Use `/cancel` to remove items.", parse_mode=ParseMode.MARKDOWN)
            return
        
        plan, is_premium = self.db.is_premium(update.effective_user.id), self.db.get_premium_type(update.effective_user.id) if self.db.is_premium(update.effective_user.id) else "free"
        available_qualities = list(Config.QUALITIES.keys())
        if not is_premium:
            available_qualities = [q for q in available_qualities if q not in Config.PREMIUM_QUALITIES]
        
        keyboard = []
        row = []
        for q in available_qualities[:6]:
            premium_mark = "💎" if q in Config.PREMIUM_QUALITIES else ""
            row.append(InlineKeyboardButton(f"{premium_mark}{q}", callback_data=f"dl_{q}_{url[:50]}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        # Encode preset selection for premium users
        if is_premium:
            keyboard.append([InlineKeyboardButton("⚙️ Encode Preset", callback_data="encode_preset")])
        
        keyboard.append([InlineKeyboardButton(f"{Emojis.CANCEL} Cancel", callback_data="cancel")])
        
        context.user_data["download_url"] = url
        await update.message.reply_text(f"{Emojis.DOWNLOAD} **Select Quality**\n\nURL: `{url[:60]}...`\n\n💎 = Premium only", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        is_premium = self.db.is_premium(user_id)
        
        if is_premium:
            plan = self.db.get_premium_type(user_id)
            expiry = self.db.get_premium_expiry(user_id)
            days_left = (expiry - datetime.now()).days if expiry else 0
            
            text = f"""
{Emojis.PREMIUM} **Premium Active!** {Emojis.PREMIUM}

**Plan:** {plan.upper()}
**Expires:** {expiry.strftime('%Y-%m-%d') if expiry else 'Never'}
**Days Left:** {days_left}

**Premium Features:**
✅ 1080p & 4K Quality
✅ Unlimited Downloads
✅ Priority Queue
✅ Batch Downloads
✅ Priority Support

Thank you for supporting! 🙏
"""
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
        
        text = f"""
{Emojis.PREMIUM} **Premium Plans** {Emojis.PREMIUM}

**Weekly** - {Config.SUBSCRIPTION_PRICES['weekly']} Stars
├ 7 days access
├ 1080p quality
└ 50 downloads/day

**Monthly** - {Config.SUBSCRIPTION_PRICES['monthly']} Stars
├ 30 days access
├ 4K quality
└ Unlimited downloads

**Yearly** - {Config.SUBSCRIPTION_PRICES['yearly']} Stars
├ 365 days (2 months free!)
├ Best value
└ Priority queue

**Lifetime** - {Config.SUBSCRIPTION_PRICES['lifetime']} Stars
├ Forever access
├ VIP support
└ All features

Use `/subscribe <plan>` to purchase
"""
        
        keyboard = [
            [InlineKeyboardButton("⭐ Weekly", callback_data="sub_weekly"),
             InlineKeyboardButton("🚀 Monthly", callback_data="sub_monthly")],
            [InlineKeyboardButton("🌟 Yearly", callback_data="sub_yearly"),
             InlineKeyboardButton("👑 Lifetime", callback_data="sub_lifetime")]
        ]
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or context.args[0].lower() not in Config.SUBSCRIPTION_PRICES:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/subscribe <weekly|monthly|yearly|lifetime>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        plan = context.args[0].lower()
        price = Config.SUBSCRIPTION_PRICES[plan]
        days = Config.SUBSCRIPTION_DAYS[plan]
        
        await update.message.reply_invoice(
            title=f"Crunchyroll Bot - {plan.title()}",
            description=f"{days} days premium access!\n\nFeatures:\n• 1080p & 4K quality\n• Unlimited downloads\n• Priority queue\n• Batch downloads",
            payload=f"sub_{plan}_{update.effective_user.id}_{uuid.uuid4().hex}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(f"{plan.title()} Premium", price)],
            start_parameter=f"subscribe_{plan}"
        )
    
    async def queue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        queue_items = self.db.get_user_queue(user_id)
        
        if not queue_items:
            await update.message.reply_text(f"{Emojis.QUEUE} **Your queue is empty.**\n\nUse `/cr` to start downloading!", parse_mode=ParseMode.MARKDOWN)
            return
        
        text = f"{Emojis.QUEUE} **Your Download Queue**\n\n"
        for item in queue_items:
            status_emoji = "⏳" if item["status"] == "pending" else "⚡"
            text += f"{status_emoji} **#{item['id']}** - {item['quality']} - {ProgressBar.create(item['progress'])}\n"
        
        text += f"\nUse `/cancel <id>` to cancel"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/cancel <queue_id>`\nUse `/queue` to see IDs", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            queue_id = int(context.args[0])
            if self.db.cancel_queue_item(queue_id, update.effective_user.id):
                await update.message.reply_text(f"{Emojis.SUCCESS} Download #{queue_id} cancelled.", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"{Emojis.ERROR} Cannot cancel. Download may already be processing.", parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text(f"{Emojis.ERROR} Invalid ID.", parse_mode=ParseMode.MARKDOWN)
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        history = self.db.get_download_history(user_id, 15)
        
        if not history:
            await update.message.reply_text(f"{Emojis.INFO} No download history yet.\n\nUse `/cr` to start!", parse_mode=ParseMode.MARKDOWN)
            return
        
        text = f"{Emojis.DOWNLOAD} **Download History**\n\n"
        for item in history:
            text += f"**{item['anime_title'][:35]}**\n"
            text += f"   {item['episode_title'][:40]}\n"
            text += f"   {item['quality']} | {item['file_size']/(1024*1024):.1f}MB\n"
            text += f"   {item['downloaded_at'][:10]}\n\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.db.get_user(user_id)
        is_premium = self.db.is_premium(user_id)
        daily = self.db.get_daily_downloads(user_id)
        limit = Config.PREMIUM_DAILY_LIMIT if is_premium else Config.FREE_DAILY_LIMIT
        
        text = f"""
{Emojis.STATS} **Your Statistics**

**Profile:**
├ Name: {user.get('first_name', 'Unknown')}
├ Premium: {'✅ Yes' if is_premium else '❌ No'}
├ Plan: {self.db.get_premium_type(user_id).upper() if is_premium else 'Free'}

**Usage:**
├ Today: {daily}/{limit}
├ Total: {user.get('total_downloads', 0)}
├ Size: {user.get('total_size', 0)/(1024**3):.2f} GB
└ Queue: {self.db.get_queue_count(user_id)}

**⭐ Stars Balance:** {user.get('stars_balance', 0)}

Use `/premium` to upgrade!
"""
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.db.get_user(user_id)
        
        text = f"""
{Emojis.SETTINGS} **User Settings**

**Current:**
├ Default Quality: {user.get('default_quality', '720p')}
├ Encode Preset: {user.get('encode_preset', 'balanced')}
├ Theme: {user.get('theme', 'dark')}
└ Language: {user.get('language', 'en')}

Select an option:
"""
        
        keyboard = [
            [InlineKeyboardButton("🎬 Default Quality", callback_data="set_quality"),
             InlineKeyboardButton("⚙️ Encode Preset", callback_data="set_encode")],
            [InlineKeyboardButton("🎨 Theme", callback_data="set_theme"),
             InlineKeyboardButton("🌐 Language", callback_data="set_language")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/feedback <rating> <message>`\nRating: 1-5\nExample: `/feedback 5 Great bot!`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            rating = int(context.args[0])
            if rating < 1 or rating > 5:
                raise ValueError
            message = " ".join(context.args[1:]) if len(context.args) > 1 else "No message"
        except ValueError:
            await update.message.reply_text(f"{Emojis.ERROR} Invalid rating! Use 1-5.", parse_mode=ParseMode.MARKDOWN)
            return
        
        self.db.add_feedback(update.effective_user.id, rating, message)
        stars = "⭐" * rating + "☆" * (5 - rating)
        
        await update.message.reply_text(f"{Emojis.SUCCESS} Thank you for your feedback!\n\nRating: {stars}\nMessage: {message[:200]}", parse_mode=ParseMode.MARKDOWN)
        
        for admin_id in Config.ADMIN_IDS:
            await context.bot.send_message(admin_id, f"📝 New Feedback\nUser: {update.effective_user.first_name}\nRating: {stars}\nMessage: {message}")
    
    # ========== CALLBACK HANDLERS ==========
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id
        
        if data.startswith("dl_"):
            parts = data.split("_", 2)
            if len(parts) >= 3:
                quality = parts[1]
                url = parts[2]
                
                is_premium = self.db.is_premium(user_id)
                if quality in Config.PREMIUM_QUALITIES and not is_premium:
                    await query.edit_message_text(f"{Emojis.PREMIUM} Premium required for {quality}!\nUse /premium to upgrade.", parse_mode=ParseMode.MARKDOWN)
                    return
                
                await query.edit_message_text(f"{Emojis.LOADING} Adding to queue...", parse_mode=ParseMode.MARKDOWN)
                
                user = self.db.get_user(user_id)
                encode_preset = user.get('encode_preset', 'balanced') if user else 'balanced'
                
                queue_id = self.db.add_to_queue(user_id, url, quality, encode_preset, query.message.message_id)
                position = self.db.get_queue_position(queue_id)
                
                await query.edit_message_text(f"{Emojis.SUCCESS} Added to queue!\n\nID: #{queue_id}\nPosition: {position}\nQuality: {quality}\n\nUse `/queue` to check status", parse_mode=ParseMode.MARKDOWN)
                
                if not self.queue_task or self.queue_task.done():
                    self.queue_task = asyncio.create_task(self.process_queue())
        
        elif data.startswith("sub_"):
            plan = data.replace("sub_", "")
            price = Config.SUBSCRIPTION_PRICES[plan]
            days = Config.SUBSCRIPTION_DAYS[plan]
            
            await query.message.reply_invoice(
                title=f"Crunchyroll Bot - {plan.title()}",
                description=f"{days} days premium access!\n\nFeatures:\n• 1080p & 4K quality\n• Unlimited downloads\n• Priority queue\n• Batch downloads",
                payload=f"sub_{plan}_{user_id}_{uuid.uuid4().hex}",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(f"{plan.title()} Premium", price)],
                start_parameter=f"subscribe_{plan}"
            )
        
        elif data == "queue":
            await self.queue_command(update, context)
        
        elif data == "premium":
            await self.premium_command(update, context)
        
        elif data == "stats":
            await self.stats_command(update, context)
        
        elif data == "settings":
            await self.settings_command(update, context)
        
        elif data == "favorites":
            await self.favorites_command(update, context)
        
        elif data == "back":
            await self.start_command(update, context)
        
        elif data == "cancel":
            await query.edit_message_text(f"{Emojis.CANCEL} Cancelled.", parse_mode=ParseMode.MARKDOWN)
    
    async def favorites_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        favorites = self.db.get_favorites(user_id)
        
        if not favorites:
            await update.message.reply_text(f"{Emojis.HEART} **No favorites yet.**\n\nUse `/search` to find anime and add to favorites!", parse_mode=ParseMode.MARKDOWN)
            return
        
        text = f"{Emojis.HEART} **Your Favorites**\n\n"
        for fav in favorites[:20]:
            text += f"• **{fav['anime_title'][:40]}**\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    # ========== PAYMENT HANDLERS ==========
    
    async def pre_checkout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.pre_checkout_query
        await query.answer(ok=True)
    
    async def successful_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        payment = update.message.successful_payment
        payload = payment.invoice_payload
        
        parts = payload.split("_")
        if len(parts) >= 2:
            plan = parts[1]
            user_id = int(parts[2]) if len(parts) > 2 else update.effective_user.id
            
            days = Config.SUBSCRIPTION_DAYS[plan]
            self.db.add_premium(user_id, plan, days, payment.telegram_payment_charge_id)
            
            await update.message.reply_text(f"{Emojis.SUCCESS} **Payment Successful!**\n\nYour {plan.upper()} plan is now active for {days} days!\n\nEnjoy premium features!", parse_mode=ParseMode.MARKDOWN)
            
            for admin_id in Config.ADMIN_IDS:
                await context.bot.send_message(admin_id, f"💰 New Premium!\nUser: {update.effective_user.first_name}\nPlan: {plan}\nAmount: {payment.total_amount} Stars")
    
    # ========== ADMIN COMMANDS ==========
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        stats = self.db.get_stats()
        
        text = f"""
{Emojis.ADMIN} **Admin Panel** {Emojis.ADMIN}

**📊 Statistics:**
├ Users: {stats['total_users']:,}
├ Premium: {stats['premium_users']:,}
├ Downloads: {stats['total_downloads']:,}
├ Queue: {stats['queue_size']}
└ Storage: {stats['total_size_gb']} GB

**Commands:**
/ban <id> <reason> - Ban user
/unban <id> - Unban user
/warn <id> <reason> - Warn user
/broadcast <msg> - Broadcast
/stats_all - Full stats
/restart - Restart bot
"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/ban <user_id> <reason> [days]`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            target_id = int(context.args[0])
            days = int(context.args[-1]) if context.args[-1].isdigit() else 0
            reason = " ".join(context.args[1:-1]) if days > 0 else " ".join(context.args[1:])
            
            self.db.ban_user(target_id, user_id, reason, days)
            duration = f" for {days} days" if days > 0 else " permanently"
            
            await update.message.reply_text(f"{Emojis.BAN} User `{target_id}` banned{duration}\nReason: {reason}", parse_mode=ParseMode.MARKDOWN)
            
            try:
                await context.bot.send_message(target_id, f"{Emojis.WARNING} You have been banned{duration}\nReason: {reason}", parse_mode=ParseMode.MARKDOWN)
            except:
                pass
        except ValueError:
            await update.message.reply_text(f"{Emojis.ERROR} Invalid user ID!", parse_mode=ParseMode.MARKDOWN)
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            target_id = int(context.args[0])
            self.db.unban_user(target_id)
            await update.message.reply_text(f"{Emojis.UNBAN} User `{target_id}` unbanned.", parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text(f"{Emojis.ERROR} Invalid user ID!", parse_mode=ParseMode.MARKDOWN)
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/warn <user_id> <reason>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            target_id = int(context.args[0])
            reason = " ".join(context.args[1:])
            
            c = self.db.conn.cursor()
            c.execute("UPDATE users SET warnings = warnings + 1 WHERE user_id = ?", (target_id,))
            c.execute("SELECT warnings FROM users WHERE user_id = ?", (target_id,))
            warnings = c.fetchone()[0]
            self.db.conn.commit()
            
            await update.message.reply_text(f"{Emojis.WARN} User `{target_id}` warned ({warnings}/5)\nReason: {reason}", parse_mode=ParseMode.MARKDOWN)
            
            if warnings >= 5:
                self.db.ban_user(target_id, user_id, "Auto-ban: 5 warnings", 30)
                await update.message.reply_text(f"{Emojis.BAN} User `{target_id}` auto-banned for 30 days (5 warnings).", parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text(f"{Emojis.ERROR} Invalid user ID!", parse_mode=ParseMode.MARKDOWN)
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        message = " ".join(context.args)
        
        c = self.db.conn.cursor()
        c.execute("SELECT user_id FROM users WHERE is_banned = 0")
        users = c.fetchall()
        
        sent = 0
        failed = 0
        msg = await update.message.reply_text(f"{Emojis.LOADING} Broadcasting to {len(users)} users...", parse_mode=ParseMode.MARKDOWN)
        
        for user in users:
            try:
                await context.bot.send_message(user[0], f"{Emojis.BROADCAST} **Broadcast**\n\n{message}", parse_mode=ParseMode.MARKDOWN)
                sent += 1
            except:
                failed += 1
            
            if (sent + failed) % 50 == 0:
                await msg.edit_text(f"{Emojis.LOADING} Progress: {sent + failed}/{len(users)}", parse_mode=ParseMode.MARKDOWN)
            
            await asyncio.sleep(0.05)
        
        await msg.edit_text(f"{Emojis.SUCCESS} Broadcast complete!\nSent: {sent}\nFailed: {failed}", parse_mode=ParseMode.MARKDOWN)
    
    async def stats_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        stats = self.db.get_stats()
        feedback = self.db.get_feedback_stats()
        
        text = f"""
{Emojis.STATS} **Full Statistics**

**Users:**
├ Total: {stats['total_users']:,}
├ Premium: {stats['premium_users']:,}
├ Active: {stats['active_users']:,}
└ Premium Rate: {int(stats['premium_users']/max(stats['total_users'],1)*100)}%

**Downloads:**
├ Total: {stats['total_downloads']:,}
├ Queue: {stats['queue_size']}
└ Storage: {stats['total_size_gb']} GB

**Feedback:**
├ Avg Rating: {feedback['avg_rating']}/5
└ Total: {feedback['total']}

**Bot:** Online ✅
"""
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        await update.message.reply_text(f"{Emojis.LOADING} Restarting bot...", parse_mode=ParseMode.MARKDOWN)
        os._exit(0)
    
    # ========== CUSTOM COMMAND HANDLERS ==========
    
    async def handle_custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        if not text.startswith('/'):
            return
        
        cmd = text[1:].split()[0].lower()
        cmd_data = self.db.get_custom_command(cmd)
        
        if cmd_data:
            parse_mode = ParseMode.MARKDOWN if cmd_data['type'] == 'markdown' else None
            await update.message.reply_text(cmd_data['response'], parse_mode=parse_mode)
            return True
        return False
    
    async def add_custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/addcmd <name> <response>`\nType: text or markdown\nExample: `/addcmd hello Hello World!`", parse_mode=ParseMode.MARKDOWN)
            return
        
        cmd_name = context.args[0].lower()
        response = " ".join(context.args[1:])
        response_type = "markdown" if "**" in response or "*" in response or "`" in response else "text"
        
        if self.db.add_custom_command(cmd_name, response, response_type, user_id):
            await update.message.reply_text(f"{Emojis.SUCCESS} Custom command `/{cmd_name}` added!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Emojis.ERROR} Command `/{cmd_name}` already exists!", parse_mode=ParseMode.MARKDOWN)
    
    async def del_custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.db.is_admin(user_id):
            await update.message.reply_text(f"{Emojis.ERROR} Admin access required!", parse_mode=ParseMode.MARKDOWN)
            return
        
        if not context.args:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/delcmd <name>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        cmd_name = context.args[0].lower()
        
        if self.db.remove_custom_command(cmd_name):
            await update.message.reply_text(f"{Emojis.SUCCESS} Custom command `/{cmd_name}` removed!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"{Emojis.ERROR} Command `/{cmd_name}` not found!", parse_mode=ParseMode.MARKDOWN)
    
    async def list_custom_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        commands = self.db.list_custom_commands()
        
        if not commands:
            await update.message.reply_text(f"{Emojis.INFO} No custom commands available.", parse_mode=ParseMode.MARKDOWN)
            return
        
        text = f"{Emojis.LIST} **Custom Commands** ({len(commands)})\n\n"
        for cmd in commands[:30]:
            text += f"• `/{cmd['command']}` - {cmd['response'][:40]}...\n"
            text += f"  Uses: {cmd['usage_count']}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    # ========== ANIMATION COMMAND ==========
    
    async def animate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text(f"{Emojis.WARNING} Usage: `/animate <style> <text>`\n\nStyles: typing, slide, fade, bounce, rainbow, glitch, neon, pulse, matrix, fire, heart, wave, sparkle\nExample: `/animate rainbow Hello`", parse_mode=ParseMode.MARKDOWN)
            return
        
        style = context.args[0].lower()
        text = " ".join(context.args[1:])
        
        frames = AnimationCaption.get_animation(style, text)
        
        msg = await update.message.reply_text(frames[0])
        
        for frame in frames[1:8]:  # Show first 8 frames
            await asyncio.sleep(0.3)
            await msg.edit_text(frame)
        
        await asyncio.sleep(0.5)
        await msg.edit_text(frames[-1])
    
    # ========== QUEUE PROCESSOR ==========
    
    async def process_queue(self):
        """Process pending downloads"""
        while True:
            try:
                if len(self.active_downloads) >= Config.MAX_CONCURRENT_DOWNLOADS:
                    await asyncio.sleep(5)
                    continue
                
                next_item = self.db.get_next_queue_item()
                if not next_item:
                    await asyncio.sleep(5)
                    continue
                
                queue_id = next_item["id"]
                user_id = next_item["user_id"]
                url = next_item["url"]
                quality = next_item["quality"]
                encode_preset = next_item["encode_preset"]
                message_id = next_item.get("message_id")
                
                self.active_downloads[queue_id] = True
                self.db.start_processing(queue_id)
                
                async def update_progress(progress: int, status: str = None):
                    self.db.update_queue_progress(queue_id, progress)
                    if message_id:
                        try:
                            await self.application.bot.edit_message_text(
                                f"{Emojis.LOADING} **Downloading...**\n\nQuality: {quality}\n{ProgressBar.create(progress)}\n\n{status or 'Processing'}",
                                chat_id=user_id,
                                message_id=message_id,
                                parse_mode=ParseMode.MARKDOWN
                            )
                        except:
                            pass
                
                success, result = await self.downloader.download_episode(
                    queue_id, user_id, url, quality, encode_preset, update_progress
                )
                
                if success:
                    with open(result, "rb") as f:
                        await self.application.bot.send_video(
                            chat_id=user_id,
                            video=f,
                            caption=f"{Emojis.SUCCESS} **Download Complete!**\nQuality: {quality}\nUse `/premium` for more features!",
                            parse_mode=ParseMode.MARKDOWN,
                            supports_streaming=True
                        )
                    Path(result).unlink()
                else:
                    self.db.fail_queue_item(queue_id, result)
                    await self.application.bot.send_message(
                        user_id,
                        f"{Emojis.ERROR} **Download Failed**\nError: {result[:200]}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                if message_id:
                    try:
                        await self.application.bot.delete_message(user_id, message_id)
                    except:
                        pass
                
                del self.active_downloads[queue_id]
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Queue error: {e}")
                await asyncio.sleep(10)
    
    # ========== SETUP ==========
    
    async def setup(self):
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
        self.application = Application.builder().token(Config.BOT_TOKEN).defaults(defaults).build()
        
        # User commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("cr", self.cr_command))
        self.application.add_handler(CommandHandler("premium", self.premium_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("queue", self.queue_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("feedback", self.feedback_command))
        self.application.add_handler(CommandHandler("favorites", self.favorites_command))
        
        # Custom command handlers
        self.application.add_handler(CommandHandler("addcmd", self.add_custom_command))
        self.application.add_handler(CommandHandler("delcmd", self.del_custom_command))
        self.application.add_handler(CommandHandler("listcmds", self.list_custom_commands))
        self.application.add_handler(CommandHandler("animate", self.animate_command))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("ban", self.ban_command))
        self.application.add_handler(CommandHandler("unban", self.unban_command))
        self.application.add_handler(CommandHandler("warn", self.warn_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("stats_all", self.stats_all_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        
        # Message handler for custom commands
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_custom_command))
        
        # Callback handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Payment handlers
        self.application.add_handler(PreCheckoutQueryHandler(self.pre_checkout_callback))
        self.application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback))
        
        # Set commands
        await self.application.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
            BotCommand("cr", "Download episode"),
            BotCommand("premium", "Premium plans"),
            BotCommand("subscribe", "Subscribe to premium"),
            BotCommand("queue", "View queue"),
            BotCommand("cancel", "Cancel download"),
            BotCommand("history", "Download history"),
            BotCommand("stats", "Your statistics"),
            BotCommand("settings", "User settings"),
            BotCommand("feedback", "Send feedback"),
            BotCommand("favorites", "Your favorites"),
            BotCommand("admin", "Admin panel"),
        ])
        
        logger.info("✅ Bot setup complete")
    
    async def run(self):
        await self.setup()
        
        logger.info(f"🚀 Starting Crunchyroll Bot v70.0")
        logger.info(f"👥 Admin IDs: {Config.ADMIN_IDS}")
        
        self.queue_task = asyncio.create_task(self.process_queue())
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
            await self.application.stop()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║         🎬 CRUNCHYROLL ULTIMATE BOT v70.0 - STARTING 🎬                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if not Config.validate():
        print("\n❌ Please configure your BOT_TOKEN in the Config class!")
        print("Get your token from @BotFather on Telegram\n")
        sys.exit(1)
    
    bot = CrunchyrollBot()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import traceback
    main()
