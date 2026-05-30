#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║     CONFIG.PY - CRUNCHYROLL ULTIMATE BOT v4.0 - COMPLETE CONFIGURATION            ║
║     40+ Features | Custom Emojis | Font System | Authorities Group | Encoding     ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

class Env:
    """Environment variables with defaults"""
    
    # Bot Token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Admin & Authorities Group
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
    AUTHORITIES_GROUP_ID = int(os.getenv("AUTHORITIES_GROUP_ID", "-1001234567890"))
    MODERATOR_IDS = [int(x.strip()) for x in os.getenv("MODERATOR_IDS", "").split(",") if x]
    SUPPORT_IDS = [int(x.strip()) for x in os.getenv("SUPPORT_IDS", "").split(",") if x]
    
    # Crunchyroll Account
    CRUNCHYROLL_EMAIL = os.getenv("CRUNCHYROLL_EMAIL", "your_email@example.com")
    CRUNCHYROLL_PASSWORD = os.getenv("CRUNCHYROLL_PASSWORD", "your_password")
    CRUNCHYROLL_PREMIUM = os.getenv("CRUNCHYROLL_PREMIUM", "False").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///crunchyroll_bot.db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "True").lower() == "true"
    
    # Payment Providers
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    TELEGRAM_PAYMENTS_TOKEN = os.getenv("TELEGRAM_PAYMENTS_TOKEN", "")
    
    # Storage Paths
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "/app/downloads")
    ENCODE_PATH = os.getenv("ENCODE_PATH", "/app/encode")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/app/output")
    THUMBNAIL_PATH = os.getenv("THUMBNAIL_PATH", "/app/thumbnails")
    LOG_PATH = os.getenv("LOG_PATH", "/app/logs")
    
    # FFmpeg Paths
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")
    FFPROBE_PATH = os.getenv("FFPROBE_PATH", "/usr/bin/ffprobe")
    MP4DECRYPT_PATH = os.getenv("MP4DECRYPT_PATH", "/usr/bin/mp4decrypt")
    
    @classmethod
    def create_directories(cls):
        for path in [cls.DOWNLOAD_PATH, cls.ENCODE_PATH, cls.OUTPUT_PATH, 
                     cls.THUMBNAIL_PATH, cls.LOG_PATH]:
            Path(path).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        return user_id in cls.ADMIN_IDS
    
    @classmethod
    def is_moderator(cls, user_id: int) -> bool:
        return user_id in cls.MODERATOR_IDS or user_id in cls.ADMIN_IDS
    
    @classmethod
    def is_support(cls, user_id: int) -> bool:
        return user_id in cls.SUPPORT_IDS or cls.is_moderator(user_id)


# ============================================================================
# CUSTOM EMOJI SYSTEM (30+ Premium Emojis)
# ============================================================================

class CustomEmojis:
    """30+ Premium Custom Emojis for Telegram"""
    
    # Replace these IDs with actual emoji IDs from @Stickers bot
    # Format: "emoji_name": "telegram_emoji_id"
    EMOJIS = {
        # Anime Category
        "anime": "5000000000000000001",
        "otaku": "5000000000000000002",
        "manga": "5000000000000000003",
        "studio": "5000000000000000004",
        "season": "5000000000000000005",
        "episode": "5000000000000000006",
        "character": "5000000000000000007",
        "voice": "5000000000000000008",
        "subbed": "5000000000000000009",
        "dubbed": "5000000000000000010",
        
        # Premium Category
        "premium": "5000000000000000011",
        "vip": "5000000000000000012",
        "crown": "5000000000000000013",
        "diamond": "5000000000000000014",
        "star": "5000000000000000015",
        "unlimited": "5000000000000000016",
        "4k": "5000000000000000017",
        "hdr": "5000000000000000018",
        "dolby": "5000000000000000019",
        
        # Actions Category
        "download": "5000000000000000020",
        "upload": "5000000000000000021",
        "play": "5000000000000000022",
        "pause": "5000000000000000023",
        "stop": "5000000000000000024",
        "queue": "5000000000000000025",
        "success": "5000000000000000026",
        "error": "5000000000000000027",
        "warning": "5000000000000000028",
        "info": "5000000000000000029",
        "loading": "5000000000000000030",
        
        # Social Category
        "like": "5000000000000000031",
        "heart": "5000000000000000032",
        "share": "5000000000000000033",
        "comment": "5000000000000000034",
        "follow": "5000000000000000035",
        "notification": "5000000000000000036",
        
        # Tools Category
        "settings": "5000000000000000037",
        "admin": "5000000000000000038",
        "mod": "5000000000000000039",
        "support": "5000000000000000040",
        "report": "5000000000000000041",
        "ban": "5000000000000000042",
        "warn": "5000000000000000043",
        
        # Misc Category
        "rocket": "5000000000000000044",
        "sparkles": "5000000000000000045",
        "fire": "5000000000000000046",
        "magic": "5000000000000000047",
        "gift": "5000000000000000048",
        "trophy": "5000000000000000049",
        "medal": "5000000000000000050"
    }
    
    # Categories for organization
    CATEGORIES = {
        "🎬 Anime": ["anime", "otaku", "manga", "studio", "season", "episode", "character", "voice", "subbed", "dubbed"],
        "💎 Premium": ["premium", "vip", "crown", "diamond", "star", "unlimited", "4k", "hdr", "dolby"],
        "⚡ Actions": ["download", "upload", "play", "pause", "stop", "queue", "success", "error", "warning", "info", "loading"],
        "❤️ Social": ["like", "heart", "share", "comment", "follow", "notification"],
        "🛠️ Tools": ["settings", "admin", "mod", "support", "report", "ban", "warn"],
        "✨ Misc": ["rocket", "sparkles", "fire", "magic", "gift", "trophy", "medal"]
    }
    
    @classmethod
    def get(cls, name: str, fallback: str = "✨") -> str:
        """Get custom emoji by name"""
        emoji_id = cls.EMOJIS.get(name)
        if emoji_id:
            return f"![{fallback}](tg://emoji?id={emoji_id})"
        return fallback
    
    @classmethod
    def success(cls) -> str:
        return cls.get("success", "✅")
    
    @classmethod
    def error(cls) -> str:
        return cls.get("error", "❌")
    
    @classmethod
    def warning(cls) -> str:
        return cls.get("warning", "⚠️")
    
    @classmethod
    def info(cls) -> str:
        return cls.get("info", "ℹ️")
    
    @classmethod
    def loading(cls) -> str:
        return cls.get("loading", "⏳")
    
    @classmethod
    def premium(cls) -> str:
        return cls.get("premium", "💎")
    
    @classmethod
    def download(cls) -> str:
        return cls.get("download", "📥")
    
    @classmethod
    def admin(cls) -> str:
        return cls.get("admin", "👑")
    
    @classmethod
    def mod(cls) -> str:
        return cls.get("mod", "🛡️")


# ============================================================================
# FANCY FONT SYSTEM (Multiple Text Styles)
# ============================================================================

class FancyFonts:
    """Advanced font styling system with 20+ text styles"""
    
    # Unicode mapping for different font styles
    STYLES = {
        "normal": lambda x: x,
        "bold": lambda x: ''.join(chr(0x1D400 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                   else chr(0x1D41A + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                   else c for c in x),
        "italic": lambda x: ''.join(chr(0x1D434 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                     else chr(0x1D44E + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                     else c for c in x),
        "bold_italic": lambda x: ''.join(chr(0x1D468 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                         else chr(0x1D482 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                         else c for c in x),
        "script": lambda x: ''.join(chr(0x1D49C + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                    else chr(0x1D4B6 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                    else c for c in x),
        "bold_script": lambda x: ''.join(chr(0x1D4D0 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                         else chr(0x1D4EA + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                         else c for c in x),
        "fraktur": lambda x: ''.join(chr(0x1D504 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                     else chr(0x1D51E + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                     else c for c in x),
        "bold_fraktur": lambda x: ''.join(chr(0x1D56C + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                          else chr(0x1D586 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                          else c for c in x),
        "monospace": lambda x: ''.join(chr(0x1D670 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                       else chr(0x1D68A + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                       else c for c in x),
        "double_struck": lambda x: ''.join(chr(0x1D538 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                           else chr(0x1D552 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                           else c for c in x),
        "sans_serif": lambda x: ''.join(chr(0x1D5A0 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                        else chr(0x1D5BA + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                        else c for c in x),
        "sans_bold": lambda x: ''.join(chr(0x1D5D4 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                       else chr(0x1D5EE + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                       else c for c in x),
        "sans_italic": lambda x: ''.join(chr(0x1D608 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                         else chr(0x1D622 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                         else c for c in x),
        "sans_bold_italic": lambda x: ''.join(chr(0x1D63C + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                              else chr(0x1D656 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                              else c for c in x),
        "circled": lambda x: ''.join(chr(0x24B6 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                     else chr(0x24D0 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                     else c for c in x),
        "parenthesis": lambda x: ''.join(chr(0x1F110 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                         else c for c in x),
        "squared": lambda x: ''.join(chr(0x1F130 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                     else c for c in x),
        "fullwidth": lambda x: ''.join(chr(0xFF21 + ord(c) - 0x41) if 'A' <= c <= 'Z' 
                                       else chr(0xFF41 + ord(c) - 0x61) if 'a' <= c <= 'z' 
                                       else c for c in x),
        "smallcaps": lambda x: x.upper(),
        "upside_down": lambda x: ''.join({'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ',
                                          'f': 'ɟ', 'g': 'ɓ', 'h': 'ɥ', 'i': 'ı', 'j': 'ɾ',
                                          'k': 'ʞ', 'l': 'ʃ', 'm': 'ɯ', 'n': 'u', 'o': 'o',
                                          'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ',
                                          'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ',
                                          'z': 'z'}.get(c.lower(), c) for c in x[::-1])
    }
    
    @classmethod
    def convert(cls, text: str, style: str = "normal") -> str:
        """Convert text to selected font style"""
        if style not in cls.STYLES:
            style = "normal"
        return cls.STYLES[style](text)
    
    @classmethod
    def anime_style(cls, text: str) -> str:
        """Anime-style text (italic + sparkles)"""
        return f"✨ {cls.convert(text, 'italic')} ✨"
    
    @classmethod
    def premium_style(cls, text: str) -> str:
        """Premium-style text (bold + double struck)"""
        return f"💎 {cls.convert(text, 'bold')} 💎"
    
    @classmethod
    def warning_style(cls, text: str) -> str:
        """Warning-style text"""
        return f"⚠️ {cls.convert(text, 'bold')} ⚠️"
    
    @classmethod
    def success_style(cls, text: str) -> str:
        """Success-style text"""
        return f"✅ {cls.convert(text, 'bold')} ✅"


# ============================================================================
# AUTHORITIES GROUP SYSTEM
# ============================================================================

class AuthoritiesGroup:
    """Group management and moderation system"""
    
    # Permission Levels
    LEVEL_USER = 0
    LEVEL_SUPPORT = 1
    LEVEL_MODERATOR = 2
    LEVEL_ADMIN = 3
    LEVEL_SUPER_ADMIN = 4
    
    PERMISSION_NAMES = {
        LEVEL_USER: "👤 User",
        LEVEL_SUPPORT: "🛟 Support",
        LEVEL_MODERATOR: "🛡️ Moderator",
        LEVEL_ADMIN: "👑 Admin",
        LEVEL_SUPER_ADMIN: "⭐ Super Admin"
    }
    
    # Actions
    ACTIONS = {
        "ban": "🔨 Ban User",
        "unban": "🔓 Unban User",
        "warn": "⚠️ Warn User",
        "mute": "🔇 Mute User",
        "unmute": "🔊 Unmute User",
        "kick": "👢 Kick User",
        "promote": "⬆️ Promote",
        "demote": "⬇️ Demote",
        "clear": "🗑️ Clear Messages",
        "pin": "📌 Pin Message",
        "unpin": "📍 Unpin Message",
        "slowmode": "🐌 Slow Mode",
        "lock": "🔒 Lock Chat",
        "unlock": "🔓 Unlock Chat"
    }
    
    @classmethod
    def get_permission_level(cls, user_id: int) -> int:
        """Get user's permission level"""
        if user_id in Env.ADMIN_IDS:
            return cls.LEVEL_ADMIN
        if user_id in Env.MODERATOR_IDS:
            return cls.LEVEL_MODERATOR
        if user_id in Env.SUPPORT_IDS:
            return cls.LEVEL_SUPPORT
        return cls.LEVEL_USER
    
    @classmethod
    def can_ban(cls, user_id: int) -> bool:
        """Check if user can ban others"""
        return cls.get_permission_level(user_id) >= cls.LEVEL_MODERATOR
    
    @classmethod
    def can_warn(cls, user_id: int) -> bool:
        """Check if user can warn others"""
        return cls.get_permission_level(user_id) >= cls.LEVEL_SUPPORT
    
    @classmethod
    def can_promote(cls, user_id: int) -> bool:
        """Check if user can promote others"""
        return cls.get_permission_level(user_id) >= cls.LEVEL_ADMIN
    
    @classmethod
    def format_action_log(cls, action: str, target: int, moderator: int, reason: str = "") -> str:
        """Format action log message"""
        return f"""
{CustomEmojis.admin()} **Action Log** {CustomEmojis.admin()}

**Action:** {cls.ACTIONS.get(action, action)}
**Target:** `{target}`
**Moderator:** `{moderator}`
**Reason:** {reason}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# ============================================================================
# BOT CONFIGURATION
# ============================================================================

class BotConfig:
    """Main bot configuration"""
    
    NAME = "Crunchyroll Ultimate Bot"
    VERSION = "4.0.0"
    DESCRIPTION = "Advanced Crunchyroll downloader with 40+ premium features"
    
    # Feature Toggles
    FEATURES = {
        "download": True,
        "payments": True,
        "encoding": True,
        "subtitles": True,
        "batch": True,
        "schedule": True,
        "analytics": True,
        "referral": True,
        "giveaway": True,
        "news": True,
        "anime_db": True,
        "recommendations": True,
        "watchlist": True,
        "notifications": True,
        "backup": True
    }
    
    # Limits
    FREE_DAILY_LIMIT = 3
    PREMIUM_DAILY_LIMIT = 999999
    MAX_CONCURRENT_DOWNLOADS = 3
    MAX_QUEUE_PER_USER = 10
    MAX_BATCH_SIZE = 20
    MAX_FILE_SIZE_MB = 2000
    DOWNLOAD_TIMEOUT = 3600
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 30
    RATE_LIMIT_WINDOW = 60
    
    # Cache
    CACHE_ENABLED = True
    CACHE_TTL = 3600
    CACHE_MAX_SIZE_MB = 500


# ============================================================================
# QUALITY PRESETS FOR ENCODING
# ============================================================================

class QualityPresets:
    """Video quality presets for encoding"""
    
    PRESETS = {
        "144p": {"crf": 32, "bitrate": "200k", "height": 144, "audio": "64k"},
        "240p": {"crf": 30, "bitrate": "400k", "height": 240, "audio": "96k"},
        "360p": {"crf": 28, "bitrate": "800k", "height": 360, "audio": "128k"},
        "480p": {"crf": 26, "bitrate": "1200k", "height": 480, "audio": "128k"},
        "720p": {"crf": 23, "bitrate": "2500k", "height": 720, "audio": "192k"},
        "1080p": {"crf": 20, "bitrate": "5000k", "height": 1080, "audio": "256k"},
        "4K": {"crf": 18, "bitrate": "16000k", "height": 2160, "audio": "320k"},
        "HDRip": {"crf": 17, "bitrate": "25000k", "height": 1080, "audio": "320k", "hdr": True}
    }
    
    PREMIUM_QUALITIES = ["1080p", "4K", "HDRip"]
    DEFAULT_QUALITY = "720p"
    
    @classmethod
    def get(cls, quality: str) -> Dict:
        return cls.PRESETS.get(quality, cls.PRESETS[cls.DEFAULT_QUALITY])
    
    @classmethod
    def is_premium(cls, quality: str) -> bool:
        return quality in cls.PREMIUM_QUALITIES


# ============================================================================
# SUBSCRIPTION PLANS
# ============================================================================

class SubscriptionPlans:
    """Premium subscription plans"""
    
    PLANS = {
        "weekly": {
            "name": "Weekly Premium",
            "stars": 20,
            "days": 7,
            "features": ["720p Downloads", "5 downloads/day", "Basic Support"]
        },
        "monthly": {
            "name": "Monthly Premium",
            "stars": 50,
            "days": 30,
            "features": ["1080p Downloads", "25 downloads/day", "Priority Queue", "Subtitles"]
        },
        "yearly": {
            "name": "Yearly Premium",
            "stars": 500,
            "days": 365,
            "features": ["4K Downloads", "Unlimited Downloads", "Batch Download", "VIP Support"]
        },
        "lifetime": {
            "name": "Lifetime Premium",
            "stars": 1500,
            "days": 36500,
            "features": ["All Features", "Lifetime Access", "Custom Emojis", "Early Access"]
        }
    }
    
    @classmethod
    def get_plan(cls, plan_name: str) -> Dict:
        return cls.PLANS.get(plan_name, cls.PLANS["monthly"])
    
    @classmethod
    def format_plans(cls) -> str:
        text = f"{CustomEmojis.premium()} **Premium Plans** {CustomEmojis.premium()}\n\n"
        for name, plan in cls.PLANS.items():
            text += f"**{plan['name']}** - {plan['stars']} Stars\n"
            text += f"📅 {plan['days']} days\n"
            text += f"✨ {', '.join(plan['features'][:2])}\n\n"
        return text


# ============================================================================
# MESSAGE TEMPLATES
# ============================================================================

class MessageTemplates:
    """All bot message templates"""
    
    WELCOME = f"""
{CustomEmojis.anime()} **Welcome to Crunchyroll Ultimate Bot!** {CustomEmojis.anime()}

{FancyFonts.anime_style("Your ultimate anime downloading solution")}

**Features:**
{CustomEmojis.download()} Download any Crunchyroll episode
{CustomEmojis.premium()} Premium quality (up to 4K)
{CustomEmojis.star()} Telegram Stars payments
{CustomEmojis.rocket()} Fast encoding system

**Commands:**
/cr <url> - Download episode
/premium - View plans
/status - Your status
/queue - View queue
/help - Help

{FancyFonts.premium_style("Get premium for unlimited downloads!")}
"""
    
    PREMIUM_INFO = f"""
{CustomEmojis.premium()} **Premium Subscription** {CustomEmojis.premium()}

{SubscriptionPlans.format_plans()}

{CustomEmojis.warning()} **Free users:** {BotConfig.FREE_DAILY_LIMIT} downloads/day
{CustomEmojis.success()} **Premium users:** Unlimited downloads

Use /subscribe <plan> to purchase
Example: `/subscribe monthly`
"""
    
    DOWNLOAD_PROGRESS = f"""
{CustomEmojis.loading()} **Downloading Episode** {CustomEmojis.loading()}

**Anime:** {{anime}}
**Episode:** {{episode}}
**Quality:** {{quality}}

{{progress_bar}}

⏱️ Estimated time: {{eta}}s
"""
    
    DOWNLOAD_COMPLETE = f"""
{CustomEmojis.success()} **Download Complete!** {CustomEmojis.success()}

**Anime:** {{anime}}
**Episode:** {{episode}}
**Quality:** {{quality}}
**Size:** {{size}} MB

{CustomEmojis.download()} [Download File]({{file_link}})
"""
    
    QUEUE_STATUS = f"""
{CustomEmojis.queue()} **Download Queue** {CustomEmojis.queue()}

**Position:** {{position}}/{{total}}
**Status:** {{status}}
**Progress:** {{progress}}%

{{progress_bar}}
"""
    
    ADMIN_PANEL = f"""
{CustomEmojis.admin()} **Admin Panel** {CustomEmojis.admin()}

**Statistics:**
📊 Total Users: {{total_users}}
💎 Premium Users: {{premium_users}}
📥 Total Downloads: {{total_downloads}}
⏳ Queue Size: {{queue_size}}

**System Status:**
🟢 Bot: Running
🟢 Database: Connected
🟢 Redis: {{redis_status}}
"""
    
    AUTHORITIES_PANEL = f"""
{CustomEmojis.mod()} **Authorities Group Panel** {CustomEmojis.mod()}

**Your Level:** {{level}}
**Permissions:** {{permissions}}

**Actions:**
🔨 /ban <user> <reason>
⚠️ /warn <user> <reason>
🔇 /mute <user> <duration>
⬆️ /promote <user> <level>
🗑️ /clear <count>
🔒 /lock - Lock chat
🔓 /unlock - Unlock chat
"""


# ============================================================================
# PROGRESS BAR SYSTEM
# ============================================================================

class ProgressBar:
    """Advanced progress bar system"""
    
    STYLES = {
        "anime": ["░", "▒", "▓", "█"],
        "magic": ["✨", "⭐", "🌟", "💫"],
        "download": ["📥", "💾", "📀", "✅"],
        "encode": ["🎬", "🎥", "📹", "✨"],
        "premium": ["💎", "👑", "⭐", "✨"]
    }
    
    @classmethod
    def create(cls, percentage: int, width: int = 20, style: str = "anime") -> str:
        """Create progress bar"""
        if style not in cls.STYLES:
            style = "anime"
        
        chars = cls.STYLES[style]
        filled = int(width * percentage / 100)
        empty = width - filled
        
        if filled == 0:
            bar = chars[0] * width
        elif filled == width:
            bar = chars[-1] * width
        else:
            bar = chars[-2] * filled + chars[0] * empty
        
        # Add emoji based on progress
        if percentage < 25:
            icon = CustomEmojis.loading()
        elif percentage < 50:
            icon = "⚡"
        elif percentage < 75:
            icon = "🔥"
        elif percentage < 100:
            icon = "⭐"
        else:
            icon = CustomEmojis.success()
        
        return f"{icon} `[{bar}]` {percentage}%"
    
    @classmethod
    def animate(cls, current: int, total: int, task: str) -> str:
        """Animated progress"""
        percentage = int((current / total) * 100)
        frames = ["◐", "◓", "◑", "◒"]
        frame = frames[current % len(frames)]
        return f"{frame} {task}: {cls.create(percentage, style='magic')}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, Env.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{Env.LOG_PATH}/bot.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# Create directories on import
Env.create_directories()
logger = setup_logging()

# Export all configurations
__all__ = [
    'Env', 'CustomEmojis', 'FancyFonts', 'AuthoritiesGroup',
    'BotConfig', 'QualityPresets', 'SubscriptionPlans',
    'MessageTemplates', 'ProgressBar', 'logger'
]
