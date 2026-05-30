# Crunchyroll Ultimate Bot v100.0

## Setup
1. Set BOT_TOKEN in Replit Secrets (Settings → Secrets)
2. Set ADMIN_IDS=your_telegram_user_id
3. Click "Run" — bot starts automatically

## Features (30+)
- /cr <url> [quality] [preset]  — Download with smart rename + thumbnail embed
- /pm                           — Premium plans (weekly/monthly/yearly/lifetime)
- /batch <urls…>               — Batch download (premium)
- /schedule <url> <HH:MM>       — Schedule a download
- /queue /cancel                — Queue management
- /mediainfo /rename /thumb     — Video tools
- /trim /compress /extract      — Video editing
- /screenshot /gif /watermark   — Media generation
- /redeem /gift /referral       — Economy system
- /watchlist /favorites         — Anime tracking
- /leaderboard /stats           — Statistics
- /addcmd (text/markdown/python) — Custom commands w/ sandboxed Python
- /authgroup                    — Force-subscribe system
- /admin /ban /unban /warn      — Admin/moderation
- /broadcast /gencode           — Admin tools
- /maintenance /logs /restart   — System commands

## Run Tests
python test_bot.py

## Requirements
python-telegram-bot>=20.0
ffmpeg (for video tools)
