#!/usr/bin/env python3
"""
jfredbot - Minimal Telegram bot that launches the Mini App and receives web_app_data.

This is intentionally dependency-light (only requests) and uses long polling so you
can get it running in < 30 seconds for testing.

For production use a proper framework (aiogram, python-telegram-bot, or webhook + FastAPI)
and validate initData on any authenticated endpoints.

Usage:
    export BOT_TOKEN="123456:ABCDEF..."
    export JFREDBOT_URL="https://yourname.github.io/jfredbot/"
    python bot.py

Then in Telegram:
    /start  -> big "Open jfredbot" button that launches your Mini App
    Any actions inside the Mini App that call sendData() will arrive here as web_app_data
"""

import os
import sys
import time
import json
import signal
from typing import Any, Dict, Optional

try:
    import requests
except ImportError:
    print("Missing 'requests'. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # dotenv is optional

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
MINIAPP_URL = os.environ.get("JFREDBOT_URL", "https://yourname.github.io/jfredbot/").strip()

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is required.")
    print("  export BOT_TOKEN=123456:ABC-...")
    print("You can also paste it now for a quick test (not saved):")
    try:
        BOT_TOKEN = input("BOT_TOKEN> ").strip()
    except EOFError:
        BOT_TOKEN = ""
    if not BOT_TOKEN:
        sys.exit(1)

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

session = requests.Session()
running = True


def api_call(method: str, **params: Any) -> Dict[str, Any]:
    """Simple Telegram Bot API call."""
    url = f"{API}/{method}"
    try:
        resp = session.post(url, json=params, timeout=30)
        data = resp.json()
        if not data.get("ok"):
            print(f"[TG API error] {method}: {data}")
        return data
    except Exception as e:
        print(f"[Network error] {method}: {e}")
        return {"ok": False, "error": str(e)}


def get_me() -> Optional[Dict[str, Any]]:
    data = api_call("getMe")
    if data.get("ok"):
        return data["result"]
    return None


def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> None:
    params: Dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        params["reply_markup"] = reply_markup
    api_call("sendMessage", **params)


def answer_web_app_query(query_id: str, result: Dict) -> None:
    """For inline web apps (different launch path)."""
    api_call("answerWebAppQuery", web_app_query_id=query_id, result=result)


def build_webapp_button(url: str, text: str = "🏆 Today's World Cup") -> Dict:
    """Inline keyboard button that opens the Mini App."""
    return {
        "inline_keyboard": [
            [
                {
                    "text": text,
                    "web_app": {"url": url}
                }
            ]
        ]
    }


def build_reply_keyboard_with_webapp(url: str) -> Dict:
    """Persistent reply keyboard (less common for web apps but works)."""
    return {
        "keyboard": [
            [{"text": "🚀 Open jfredbot", "web_app": {"url": url}}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


def handle_update(update: Dict[str, Any]) -> None:
    """Process one update from getUpdates."""
    global MINIAPP_URL

    if "message" not in update:
        return

    msg = update["message"]
    chat_id = msg["chat"]["id"]
    from_user = msg.get("from", {})
    text = (msg.get("text") or "").strip()

    # === web_app_data coming from the Mini App ===
    if "web_app_data" in msg:
        wa = msg["web_app_data"]
        raw = wa.get("data", "")
        button_text = wa.get("button_text", "")

        print(f"[web_app_data] from {from_user.get('username') or from_user.get('id')} "
              f"(via '{button_text}'): {raw}")

        # Try to pretty-print if JSON
        pretty = raw
        try:
            obj = json.loads(raw)
            pretty = json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            pass

        reply = (
            "✅ <b>Data received from jfredbot Mini App</b>\n\n"
            f"<b>Button:</b> {button_text or '(sendData)'}\n"
            f"<pre>{pretty}</pre>\n\n"
            "You can now reply, store this in a DB, trigger actions, etc."
        )
        send_message(chat_id, reply)

        # Optional: also send a follow-up action button so they can go right back in
        send_message(
            chat_id,
            "Tap below to jump back into the app:",
            reply_markup=build_webapp_button(MINIAPP_URL)
        )
        return

    # === Regular commands ===
    if text.startswith("/start"):
        me = get_me()
        bot_name = me["first_name"] if me else "jfredbot"

        welcome = (
            f"👋 Hello {from_user.get('first_name', 'there')}!\n\n"
            f"Welcome to <b>{bot_name}</b>.\n"
            "See today's <b>FIFA World Cup 2026</b> matches — kickoff times, "
            "live scores, and venues.\n\n"
            "Tap the button below to open the schedule:"
        )
        send_message(
            chat_id,
            welcome,
            reply_markup=build_webapp_button(MINIAPP_URL)
        )
        # You can also set a menu button for this chat:
        # api_call("setChatMenuButton", chat_id=chat_id, menu_button={"type": "web_app", "text": "jfredbot", "web_app": {"url": MINIAPP_URL}})
        return

    if text.startswith("/help"):
        send_message(
            chat_id,
            "Commands:\n"
            "/start — open today's World Cup matches\n"
            "/open — get the launch button again\n"
            "/url — show current Mini App URL (for debugging)\n"
            "\nThe Mini App shows today's FIFA World Cup fixtures with live score updates."
        )
        return

    if text.startswith("/open"):
        send_message(
            chat_id,
            "Open World Cup schedule:",
            reply_markup=build_webapp_button(MINIAPP_URL)
        )
        return

    if text.startswith("/url"):
        send_message(chat_id, f"Current Mini App URL:\n<code>{MINIAPP_URL}</code>")
        return

    if text.startswith("/seturl "):
        new_url = text.split(" ", 1)[1].strip()
        if new_url.startswith("http"):
            MINIAPP_URL = new_url
            send_message(chat_id, f"Updated in-memory Mini App URL to:\n<code>{MINIAPP_URL}</code>\n"
                                  "Restart the bot to persist.")
        else:
            send_message(chat_id, "Please provide a full https:// URL.")
        return

    # Fallback: give them the button again + a little nudge
    if text:
        send_message(
            chat_id,
            "I only understand /start, /open, /help right now.\n"
            "Open the Mini App to interact:",
            reply_markup=build_webapp_button(MINIAPP_URL)
        )


def poll_loop() -> None:
    """Long-poll getUpdates in a simple loop."""
    global running
    offset = 0
    print("jfredbot polling... (Ctrl+C to stop)")
    print(f"Using Mini App URL: {MINIAPP_URL}")
    print("Send /start to your bot in Telegram to test.")

    while running:
        try:
            resp = session.get(
                f"{API}/getUpdates",
                params={"offset": offset, "timeout": 50, "allowed_updates": json.dumps(["message"])},
                timeout=60,
            )
            data = resp.json()

            if not data.get("ok"):
                print("[getUpdates error]", data)
                time.sleep(2)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    handle_update(update)
                except Exception as e:
                    print(f"[handle_update error] {e}")
                    # Don't crash the loop

        except KeyboardInterrupt:
            running = False
            break
        except Exception as e:
            print(f"[poll error] {e}")
            time.sleep(3)

    print("Stopped.")


def shutdown(signum, frame):
    global running
    print("\nShutting down gracefully...")
    running = False


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    me = get_me()
    if me:
        print(f"Logged in as @{me.get('username')} (id={me.get('id')})")
    else:
        print("WARNING: Could not validate token. Check BOT_TOKEN.")

    # One-time helpful tip
    if "yourname" in MINIAPP_URL or "example" in MINIAPP_URL:
        print("\n⚠️  JFREDBOT_URL looks like a placeholder.")
        print("   Set a real HTTPS URL so the web_app buttons actually work:")
        print("   export JFREDBOT_URL=https://yourname.github.io/jfredbot/\n")

    poll_loop()


if __name__ == "__main__":
    main()
