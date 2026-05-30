#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🧪 CRUNCHYROLL ULTIMATE BOT v100.0 — TEST SUITE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
Run: python test_bot.py
All tests run without a BOT_TOKEN (offline unit tests).
"""

import asyncio
import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# ── Patch token validation so we can import bot.py without a real token ──────
os.environ.setdefault("BOT_TOKEN", "1234567890:AAABBBCCC_TEST_TOKEN_PLACEHOLDER")
os.environ.setdefault("ADMIN_IDS", "99999999")

# ── Redirect data paths to a temp directory ──────────────────────────────────
_TMP = Path(tempfile.mkdtemp(prefix="cr_bot_test_"))

# Import after env setup
import importlib
import bot as _bot_module

# Override all paths to tmp dir
_bot_module.Config.BASE_DIR      = _TMP
_bot_module.Config.DOWNLOAD_PATH = _TMP / "downloads"
_bot_module.Config.OUTPUT_PATH   = _TMP / "output"
_bot_module.Config.DATA_PATH     = _TMP / "data"
_bot_module.Config.LOG_PATH      = _TMP / "logs"
_bot_module.Config.THUMB_PATH    = _TMP / "thumbnails"
_bot_module.Config.ENCODE_PATH   = _TMP / "encode"
_bot_module.Config.TEMP_PATH     = _TMP / "temp"
_bot_module.Config.DATABASE_PATH = _TMP / "data" / "test_bot.db"
_bot_module.Config.create_dirs()

from bot import (
    Config, Database, PremiumEmoji, Em, ProgressBar,
    VideoTools, CrunchyrollAPI, CodeSandbox, AuthChecker,
)

PASS  = "✅"
FAIL  = "❌"
SEP   = "─" * 60


# ══════════════════════════════════════════════════════════════════════════════
class TestConfig(unittest.TestCase):

    def test_bot_token_loaded(self):
        self.assertIsNotNone(Config.BOT_TOKEN)
        self.assertNotEqual(Config.BOT_TOKEN, "")

    def test_qualities_defined(self):
        self.assertIn("720p",  Config.QUALITIES)
        self.assertIn("1080p", Config.QUALITIES)
        self.assertIn("4K",    Config.QUALITIES)
        self.assertIn("HDR",   Config.QUALITIES)

    def test_encode_presets_defined(self):
        for p in ("ultrafast", "fast", "balanced", "high", "master", "anime", "hevc", "av1"):
            self.assertIn(p, Config.ENCODE_PRESETS)

    def test_subscription_prices(self):
        for plan in ("weekly", "monthly", "yearly", "lifetime"):
            self.assertIn(plan, Config.SUBSCRIPTION_PRICES)
            self.assertIn(plan, Config.SUBSCRIPTION_DAYS)
            self.assertIn(plan, Config.SUBSCRIPTION_FEATURES)
            self.assertGreater(Config.SUBSCRIPTION_PRICES[plan], 0)

    def test_dirs_created(self):
        Config.create_dirs()
        for d in [Config.DOWNLOAD_PATH, Config.OUTPUT_PATH, Config.DATA_PATH,
                  Config.LOG_PATH, Config.THUMB_PATH, Config.ENCODE_PATH, Config.TEMP_PATH]:
            self.assertTrue(d.exists(), f"Directory missing: {d}")


# ══════════════════════════════════════════════════════════════════════════════
class TestPremiumEmoji(unittest.TestCase):

    def test_get_known_emoji(self):
        result = PremiumEmoji.get("success")
        self.assertTrue(len(result) > 0)

    def test_get_unknown_emoji_fallback(self):
        result = PremiumEmoji.get("nonexistent_key_xyz")
        self.assertEqual(result, "✨")

    def test_shortcuts(self):
        self.assertIsNotNone(PremiumEmoji.ok())
        self.assertIsNotNone(PremiumEmoji.err())
        self.assertIsNotNone(PremiumEmoji.warn())
        self.assertIsNotNone(PremiumEmoji.pm())
        self.assertIsNotNone(PremiumEmoji.adm())

    def test_em_constants(self):
        self.assertEqual(Em.SUCCESS, "✅")
        self.assertEqual(Em.ERROR,   "❌")
        self.assertEqual(Em.PREMIUM, "💎")


# ══════════════════════════════════════════════════════════════════════════════
class TestProgressBar(unittest.TestCase):

    def test_zero_percent(self):
        bar = ProgressBar.make(0)
        self.assertIn("0%", bar)
        self.assertIn("⏳", bar)

    def test_fifty_percent(self):
        bar = ProgressBar.make(50)
        self.assertIn("50%", bar)

    def test_hundred_percent(self):
        bar = ProgressBar.make(100)
        self.assertIn("100%", bar)
        self.assertIn("✅", bar)

    def test_bar_has_brackets(self):
        for pct in (0, 25, 50, 75, 100):
            bar = ProgressBar.make(pct)
            self.assertIn("[", bar)
            self.assertIn("]", bar)


# ══════════════════════════════════════════════════════════════════════════════
class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database()

    def tearDown(self):
        self.db.conn.close()

    # ── User management ──────────────────────────────────────────────────────

    def test_register_and_get_user(self):
        self.db.register_user(10001, "testuser", "Test")
        user = self.db.get_user(10001)
        self.assertIsNotNone(user)
        self.assertEqual(user["user_id"], 10001)
        self.assertEqual(user["username"], "testuser")

    def test_user_not_premium_by_default(self):
        self.db.register_user(10002, "user2", "User2")
        self.assertFalse(self.db.is_premium(10002))
        self.assertEqual(self.db.get_premium_type(10002), "free")

    def test_add_premium(self):
        self.db.register_user(10003, "pmuser", "PMUser")
        result = self.db.add_premium(10003, "monthly", 30, "txn_test_001")
        self.assertTrue(result)
        self.assertTrue(self.db.is_premium(10003))
        self.assertEqual(self.db.get_premium_type(10003), "monthly")

    def test_premium_expiry_extends(self):
        self.db.register_user(10004, "extuser", "ExtUser")
        self.db.add_premium(10004, "weekly", 7, "txn_ext_001")
        expiry1 = self.db.get_premium_expiry(10004)
        self.db.add_premium(10004, "weekly", 7, "txn_ext_002")
        expiry2 = self.db.get_premium_expiry(10004)
        self.assertGreater(expiry2, expiry1)

    def test_ban_and_unban(self):
        self.db.register_user(10005, "banme", "BanUser")
        self.db.ban_user(10005, 99999999, "test ban")
        self.assertTrue(self.db.is_banned(10005))
        can, msg = self.db.can_download(10005)
        self.assertFalse(can)
        self.db.unban_user(10005)
        self.assertFalse(self.db.is_banned(10005))

    def test_warnings(self):
        self.db.register_user(10006, "warnme", "WarnUser")
        for i in range(1, 4):
            count = self.db.add_warning(10006)
            self.assertEqual(count, i)

    def test_daily_downloads_reset(self):
        self.db.register_user(10007, "dluser", "DLUser")
        count = self.db.get_daily_downloads(10007)
        self.assertEqual(count, 0)
        self.db.increment_downloads(10007, 1024)
        self.db.increment_downloads(10007, 1024)
        # Simulate new day
        self.db.conn.execute(
            "UPDATE users SET last_reset='2000-01-01' WHERE user_id=?", (10007,))
        self.db.conn.commit()
        count = self.db.get_daily_downloads(10007)
        self.assertEqual(count, 0)

    def test_can_download_free_limit(self):
        self.db.register_user(10008, "limituser", "LimitUser")
        can, _ = self.db.can_download(10008)
        self.assertTrue(can)
        # Simulate limit reached
        self.db.conn.execute(
            "UPDATE users SET daily_downloads=? WHERE user_id=?",
            (Config.FREE_DAILY_LIMIT, 10008))
        self.db.conn.commit()
        can, msg = self.db.can_download(10008)
        self.assertFalse(can)
        self.assertIn("premium", msg.lower())

    # ── Queue ──────────────────────────────────────────────────────────────

    def test_add_and_get_queue(self):
        self.db.register_user(10010)
        qid = self.db.add_to_queue(10010, "https://crunchyroll.com/watch/ABC123", "720p", "balanced")
        self.assertGreater(qid, 0)
        items = self.db.get_user_queue(10010)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quality"], "720p")

    def test_queue_position(self):
        self.db.register_user(10011)
        qid1 = self.db.add_to_queue(10011, "https://crunchyroll.com/watch/A1", "720p")
        qid2 = self.db.add_to_queue(10011, "https://crunchyroll.com/watch/A2", "720p")
        pos1 = self.db.get_queue_position(qid1)
        self.assertGreaterEqual(pos1, 1)

    def test_cancel_queue_item(self):
        self.db.register_user(10012)
        qid = self.db.add_to_queue(10012, "https://crunchyroll.com/watch/CC1", "480p")
        result = self.db.cancel_queue_item(qid, 10012)
        self.assertTrue(result)
        # Cancelling again should fail
        result2 = self.db.cancel_queue_item(qid, 10012)
        self.assertFalse(result2)

    def test_complete_and_fail_queue(self):
        self.db.register_user(10013)
        qid = self.db.add_to_queue(10013, "https://crunchyroll.com/watch/CC2", "1080p")
        self.db.start_processing(qid)
        self.db.complete_queue_item(qid, "/output/test.mp4")
        c = self.db.conn.execute("SELECT status FROM queue WHERE id=?", (qid,))
        self.assertEqual(c.fetchone()[0], "completed")

        qid2 = self.db.add_to_queue(10013, "https://crunchyroll.com/watch/CC3", "1080p")
        self.db.fail_queue_item(qid2, "Test error")
        c2 = self.db.conn.execute("SELECT status,error_message FROM queue WHERE id=?", (qid2,))
        row = c2.fetchone()
        self.assertEqual(row[0], "failed")
        self.assertEqual(row[1], "Test error")

    # ── Download history ──────────────────────────────────────────────────

    def test_download_record(self):
        self.db.register_user(10020)
        self.db.add_download_record(
            10020, "Test Anime", "ANM001", "Episode 1", "EP001",
            1, 1, "720p", "balanced", 52428800, "test_anime_S01E01.mp4",
            "abc123hash")
        hist = self.db.get_download_history(10020)
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["anime_title"], "Test Anime")
        self.assertEqual(hist[0]["quality"], "720p")

    # ── Favorites & Watchlist ─────────────────────────────────────────────

    def test_favorites(self):
        self.db.register_user(10030)
        added = self.db.add_favorite(10030, "ANM999", "My Anime")
        self.assertTrue(added)
        dup = self.db.add_favorite(10030, "ANM999", "My Anime")
        self.assertFalse(dup)
        favs = self.db.get_favorites(10030)
        self.assertEqual(len(favs), 1)

    def test_watchlist(self):
        self.db.register_user(10031)
        added = self.db.add_to_watchlist(10031, "WL001", "Watch Anime")
        self.assertTrue(added)
        wl = self.db.get_watchlist(10031)
        self.assertEqual(len(wl), 1)
        self.assertEqual(wl[0]["next_episode"], 1)

    # ── Referral ──────────────────────────────────────────────────────────

    def test_referral_code(self):
        self.db.register_user(10040)
        code = self.db.get_or_create_referral_code(10040)
        self.assertEqual(len(code), 8)  # hex(4) = 8 chars
        # Same user gets same code
        code2 = self.db.get_or_create_referral_code(10040)
        self.assertEqual(code, code2)

    def test_referral_lookup(self):
        self.db.register_user(10041)
        code = self.db.get_or_create_referral_code(10041)
        uid  = self.db.get_user_by_referral(code)
        self.assertEqual(uid, 10041)

    def test_add_referral(self):
        self.db.register_user(10042)
        self.db.register_user(10043)
        added = self.db.add_referral(10042, 10043)
        self.assertTrue(added)
        count = self.db.get_referral_count(10042)
        self.assertEqual(count, 1)

    # ── Redeem codes ──────────────────────────────────────────────────────

    def test_create_and_redeem_code(self):
        self.db.register_user(10050)
        ok = self.db.create_redeem_code("TESTCODE1", "weekly", 7, 1, 99999999, 30)
        self.assertTrue(ok)
        success, msg = self.db.redeem_code("TESTCODE1", 10050)
        self.assertTrue(success)
        self.assertIn("weekly", msg.lower())
        self.assertTrue(self.db.is_premium(10050))

    def test_redeem_already_used(self):
        self.db.register_user(10051)
        self.db.register_user(10052)
        self.db.create_redeem_code("ONCE_CODE", "weekly", 7, 1, 99999999, 30)
        ok1, _ = self.db.redeem_code("ONCE_CODE", 10051)
        ok2, _ = self.db.redeem_code("ONCE_CODE", 10052)
        self.assertTrue(ok1)
        self.assertFalse(ok2)

    def test_redeem_same_user_twice(self):
        self.db.register_user(10053)
        self.db.create_redeem_code("MULTI2", "weekly", 7, 5, 99999999, 30)
        ok1, _ = self.db.redeem_code("MULTI2", 10053)
        ok2, _ = self.db.redeem_code("MULTI2", 10053)
        self.assertTrue(ok1)
        self.assertFalse(ok2)

    def test_redeem_invalid_code(self):
        self.db.register_user(10054)
        ok, msg = self.db.redeem_code("NOTACODE", 10054)
        self.assertFalse(ok)
        self.assertIn("Invalid", msg)

    # ── Settings ──────────────────────────────────────────────────────────

    def test_settings_get_set(self):
        self.db.set_setting("test_key", "hello_world")
        val = self.db.get_setting("test_key")
        self.assertEqual(val, "hello_world")

    def test_settings_default(self):
        val = self.db.get_setting("nonexistent_key_xyz", "default_val")
        self.assertEqual(val, "default_val")

    def test_maintenance_mode_toggle(self):
        self.db.set_setting("maintenance_mode", "True")
        self.assertEqual(self.db.get_setting("maintenance_mode"), "True")
        self.db.set_setting("maintenance_mode", "False")
        self.assertEqual(self.db.get_setting("maintenance_mode"), "False")

    # ── Statistics ─────────────────────────────────────────────────────────

    def test_get_stats(self):
        stats = self.db.get_stats()
        self.assertIn("total_users",    stats)
        self.assertIn("premium_users",  stats)
        self.assertIn("total_downloads",stats)
        self.assertIn("queue_size",     stats)
        self.assertIn("total_size_gb",  stats)
        self.assertIn("active_7d",      stats)

    def test_leaderboard(self):
        lb = self.db.get_leaderboard(5)
        self.assertIsInstance(lb, list)
        self.assertLessEqual(len(lb), 5)

    # ── Custom commands ────────────────────────────────────────────────────

    def test_add_text_command(self):
        ok = self.db.add_custom_cmd("testcmd1", "Hello!", None, "text", 99999999)
        self.assertTrue(ok)
        data = self.db.get_custom_cmd("testcmd1")
        self.assertIsNotNone(data)
        self.assertEqual(data["response"], "Hello!")
        self.assertEqual(data["type"], "text")

    def test_add_duplicate_command(self):
        self.db.add_custom_cmd("dupcmd", "First", None, "text", 99999999)
        ok = self.db.add_custom_cmd("dupcmd", "Second", None, "text", 99999999)
        self.assertFalse(ok)

    def test_remove_command(self):
        self.db.add_custom_cmd("rmcmd", "Remove me", None, "text", 99999999)
        removed = self.db.remove_custom_cmd("rmcmd")
        self.assertTrue(removed)
        data = self.db.get_custom_cmd("rmcmd")
        self.assertIsNone(data)

    def test_list_commands(self):
        cmds = self.db.list_custom_cmds()
        self.assertIsInstance(cmds, list)

    # ── Auth groups ─────────────────────────────────────────────────────────

    def test_add_remove_auth_group(self):
        self.db.add_auth_group(-100123456, "Test Group", "https://t.me/testgroup", 99999999)
        groups = self.db.get_auth_groups()
        gids = [g["group_id"] for g in groups]
        self.assertIn(-100123456, gids)
        self.db.remove_auth_group(-100123456)
        groups2 = self.db.get_auth_groups()
        gids2 = [g["group_id"] for g in groups2]
        self.assertNotIn(-100123456, gids2)

    # ── Gifts ────────────────────────────────────────────────────────────────

    def test_create_gift(self):
        self.db.register_user(10060)
        self.db.register_user(10061)
        code = self.db.create_gift(10060, 10061, "monthly", 30, "Happy gifting!")
        self.assertEqual(len(code), 12)  # hex(6) = 12 chars

    # ── Scheduled downloads ───────────────────────────────────────────────

    def test_schedule_download(self):
        self.db.register_user(10070)
        run_at = (datetime.now() + timedelta(hours=1)).isoformat()
        sid = self.db.schedule_download(
            10070, "https://crunchyroll.com/watch/XYZ", "1080p", "balanced", run_at)
        self.assertGreater(sid, 0)

    def test_due_schedules_empty_future(self):
        self.db.register_user(10071)
        run_at = (datetime.now() + timedelta(days=1)).isoformat()
        self.db.schedule_download(
            10071, "https://crunchyroll.com/watch/FUT", "720p", "fast", run_at)
        due = self.db.get_due_schedules()
        # Future schedule should not be due
        ids = [s["user_id"] for s in due]
        # 10071's schedule is in the future, should not appear
        self.assertNotIn(10071, ids)


# ══════════════════════════════════════════════════════════════════════════════
class TestCrunchyrollAPI(unittest.TestCase):

    def setUp(self):
        self.api = CrunchyrollAPI()

    def test_extract_id_watch_url(self):
        url = "https://www.crunchyroll.com/watch/GRDV0019R/mushoku-tensei-jobless-reincarnation"
        eid = self.api.extract_id(url)
        self.assertEqual(eid, "GRDV0019R")

    def test_extract_id_uppercase(self):
        url = "https://crunchyroll.com/watch/ABC123XYZ"
        eid = self.api.extract_id(url)
        self.assertEqual(eid, "ABC123XYZ")

    def test_extract_id_invalid(self):
        eid = self.api.extract_id("https://netflix.com/watch/123")
        self.assertIsNone(eid)

    def test_valid_url(self):
        self.assertTrue(self.api.is_valid_url("https://crunchyroll.com/watch/ABC"))
        self.assertTrue(self.api.is_valid_url("https://www.crunchyroll.com/series/XYZ"))
        self.assertFalse(self.api.is_valid_url("https://netflix.com/watch/123"))
        self.assertFalse(self.api.is_valid_url("https://youtube.com/watch?v=abc"))

    def test_get_episode_info(self):
        async def run():
            info = await self.api.get_episode_info("TEST001")
            self.assertIn("series_title",   info)
            self.assertIn("episode_title",  info)
            self.assertIn("episode_number", info)
            self.assertIn("season_number",  info)
        asyncio.run(run())

    def test_get_stream_url(self):
        async def run():
            url = await self.api.get_stream_url("TEST001", "720p")
            self.assertIsNotNone(url)
            self.assertIn("TEST001", url)
        asyncio.run(run())


# ══════════════════════════════════════════════════════════════════════════════
class TestVideoTools(unittest.TestCase):

    def test_build_filename_basic(self):
        name = VideoTools.build_filename(
            "Attack on Titan", 3, 5, "The Attack", "1080p", "balanced")
        self.assertIn("S03E05",    name)
        self.assertIn("1080p",     name)
        self.assertIn("balanced",  name)
        self.assertTrue(name.endswith(".mp4"))

    def test_build_filename_special_chars(self):
        name = VideoTools.build_filename(
            "Re:Zero — Starting Life!", 1, 1, "Episode: 1", "720p", "fast")
        # Should not contain dangerous chars
        self.assertNotIn(":", name)
        self.assertNotIn("—", name)
        self.assertTrue(name.endswith(".mp4"))

    def test_build_filename_long_title(self):
        long_title = "A" * 100
        name = VideoTools.build_filename(long_title, 1, 1, "EP", "720p", "balanced")
        # Should be truncated
        self.assertLess(len(name), 250)

    def test_get_duration_missing_file(self):
        async def run():
            dur = await VideoTools._get_duration("/nonexistent/file.mp4")
            self.assertEqual(dur, 0)
        asyncio.run(run())


# ══════════════════════════════════════════════════════════════════════════════
class TestCodeSandbox(unittest.TestCase):

    def test_simple_print(self):
        ok, out = CodeSandbox.run("print('hello world')")
        self.assertTrue(ok)
        self.assertIn("hello world", out)

    def test_math_operations(self):
        ok, out = CodeSandbox.run("print(2 + 2 * 10)")
        self.assertTrue(ok)
        self.assertIn("22", out)

    def test_context_variable(self):
        ok, out = CodeSandbox.run("print(context['user_id'])", {"user_id": 42})
        self.assertTrue(ok)
        self.assertIn("42", out)

    def test_list_comprehension(self):
        ok, out = CodeSandbox.run("print([x**2 for x in range(5)])")
        self.assertTrue(ok)
        self.assertIn("0", out)
        self.assertIn("16", out)

    def test_string_operations(self):
        ok, out = CodeSandbox.run("s = 'hello'; print(s.upper())")
        self.assertTrue(ok)
        self.assertIn("HELLO", out)

    def test_random_available(self):
        ok, out = CodeSandbox.run("import random; print(type(random.randint(1,6)))")
        # 'import random' pattern may be blocked depending on implementation
        # Try the pre-injected random variable
        ok2, out2 = CodeSandbox.run("r = random.randint(1,100); print(1 <= r <= 100)")
        self.assertTrue(ok2)
        self.assertIn("True", out2)

    def test_block_os_import(self):
        ok, out = CodeSandbox.run("import os; print(os.getcwd())")
        self.assertFalse(ok)
        self.assertIn("Blocked", out)

    def test_block_subprocess(self):
        ok, out = CodeSandbox.run("import subprocess; subprocess.run(['ls'])")
        self.assertFalse(ok)

    def test_block_open(self):
        ok, out = CodeSandbox.run("f = open('/etc/passwd'); print(f.read())")
        self.assertFalse(ok)

    def test_block_eval(self):
        ok, out = CodeSandbox.run("eval('2+2')")
        self.assertFalse(ok)

    def test_block_builtins_escape(self):
        ok, out = CodeSandbox.run("__import__('os').system('ls')")
        self.assertFalse(ok)

    def test_empty_code_no_output(self):
        ok, out = CodeSandbox.run("x = 1 + 1")
        self.assertTrue(ok)
        self.assertIn("no output", out.lower())

    def test_multiline_code(self):
        code = """
total = 0
for i in range(10):
    total += i
print(f'Sum: {total}')
"""
        ok, out = CodeSandbox.run(code)
        self.assertTrue(ok)
        self.assertIn("Sum: 45", out)

    def test_exception_handling(self):
        ok, out = CodeSandbox.run("x = 1 / 0")
        self.assertFalse(ok)
        self.assertIn("Error", out)

    def test_datetime_available(self):
        ok, out = CodeSandbox.run("print(datetime.now().year)")
        self.assertTrue(ok)
        self.assertIn(str(datetime.now().year), out)


# ══════════════════════════════════════════════════════════════════════════════
class TestIntegration(unittest.TestCase):
    """End-to-end integration tests (no bot token required)."""

    def test_full_user_lifecycle(self):
        """Register → premium → download → history → ban → unban."""
        db = Database()
        uid = 88888

        # Register
        db.register_user(uid, "fulltest", "Full")
        user = db.get_user(uid)
        self.assertIsNotNone(user)
        self.assertFalse(db.is_premium(uid))

        # Add premium
        db.add_premium(uid, "monthly", 30, "lifecycle_txn_1")
        self.assertTrue(db.is_premium(uid))

        # Simulate download
        can, _ = db.can_download(uid)
        self.assertTrue(can)
        db.increment_downloads(uid, 52428800)
        db.add_download_record(uid, "Anime", "A1", "Ep1", "E1", 1, 1,
                               "1080p", "high", 52428800, "a.mp4", "hash1")
        hist = db.get_download_history(uid)
        self.assertEqual(len(hist), 1)

        # Ban
        db.ban_user(uid, 99999999, "test lifecycle ban")
        can2, _ = db.can_download(uid)
        self.assertFalse(can2)

        # Unban
        db.unban_user(uid)
        can3, _ = db.can_download(uid)
        self.assertTrue(can3)
        db.conn.close()

    def test_referral_and_redeem_chain(self):
        """Full referral + redeem code chain."""
        db = Database()

        # Create referrer
        db.register_user(77001, "referrer", "Ref")
        code = db.get_or_create_referral_code(77001)

        # New user joins via referral
        db.register_user(77002, "newbie", "New")
        db.add_referral(77001, 77002)
        self.assertEqual(db.get_referral_count(77001), 1)

        # Admin creates redeem code
        db.create_redeem_code("CHAIN01", "yearly", 365, 2, 99999999, 60)

        # Two users redeem
        db.register_user(77003)
        db.register_user(77004)
        ok1, msg1 = db.redeem_code("CHAIN01", 77003)
        ok2, msg2 = db.redeem_code("CHAIN01", 77004)
        ok3, msg3 = db.redeem_code("CHAIN01", 77003)  # duplicate

        self.assertTrue(ok1)
        self.assertTrue(ok2)
        self.assertFalse(ok3)
        self.assertTrue(db.is_premium(77003))
        self.assertTrue(db.is_premium(77004))
        db.conn.close()


# ══════════════════════════════════════════════════════════════════════════════
class TestFilenameRename(unittest.TestCase):

    def test_rename_via_file(self):
        src = _TMP / "temp" / "original_file.mp4"
        src.write_bytes(b"fake video data")
        new_name = "NewName_S01E01_720p.mp4"
        dst = src.parent / new_name
        src.rename(dst)
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(dst.name, new_name)

    def test_build_all_quality_names(self):
        for quality in Config.QUALITIES:
            for preset in Config.ENCODE_PRESETS:
                name = VideoTools.build_filename(
                    "MyAnime", 1, 1, "Ep One", quality, preset)
                self.assertIn(quality, name)
                self.assertIn(preset, name)
                self.assertTrue(name.endswith(".mp4"))


# ══════════════════════════════════════════════════════════════════════════════
def run_tests():
    print(f"\n{SEP}")
    print("🧪  CRUNCHYROLL ULTIMATE BOT v100.0 — TEST SUITE")
    print(SEP)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    test_classes = [
        TestConfig,
        TestPremiumEmoji,
        TestProgressBar,
        TestDatabase,
        TestCrunchyrollAPI,
        TestVideoTools,
        TestCodeSandbox,
        TestIntegration,
        TestFilenameRename,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print(f"\n{SEP}")
    total   = result.testsRun
    passed  = total - len(result.failures) - len(result.errors)
    failed  = len(result.failures)
    errors  = len(result.errors)
    skipped = len(result.skipped)

    print(f"📊  Results: {total} tests")
    print(f"   {PASS}  Passed:  {passed}")
    if failed:  print(f"   {FAIL}  Failed:  {failed}")
    if errors:  print(f"   ❗  Errors:  {errors}")
    if skipped: print(f"   ⏭️  Skipped: {skipped}")
    print(SEP)

    if result.wasSuccessful():
        print("✅  ALL TESTS PASSED!")
    else:
        print("❌  SOME TESTS FAILED — see details above.")
        sys.exit(1)

    # Cleanup temp dir
    try:
        shutil.rmtree(_TMP)
    except:
        pass

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
