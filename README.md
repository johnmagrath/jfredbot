# jfredbot

A polished, production-minded **Telegram Mini App** (TMA) with a companion Telegram bot.

It demonstrates best-practice integration so it "just works" inside Telegram:
- Uses `Telegram.WebApp` APIs extensively (MainButton, CloudStorage, HapticFeedback, sendData, theme vars, expand/ready, etc.)
- Persists user data via Telegram Cloud Storage when available
- Sends rich payloads back to the bot using `sendData()` (only works when launched via a web_app button)
- Feels fast and native on iOS, Android, and Desktop
- Zero external dependencies besides the official Telegram WebApp script

## Features

- Personalized greeting from Telegram user object
- **J-Score** counter persisted with `CloudStorage` (graceful fallback to localStorage)
- Quick commands that send structured data + receive instant simulated (or real) replies
- Free-form messaging with MainButton as primary CTA
- Local activity log + nice haptic feedback on every interaction
- "Share" button that tries `switchInlineQuery` (great for virality)
- Dev info panel (useful during development)
- Respects Telegram theme (light/dark + dynamic colors)
- Early `ready()` + `expand()` for instant perceived load

## How to make it work in Telegram (setup)

### 1. Host the Mini App (static files)

The `index.html` + `assets/` folder must be served over **HTTPS**.

Easy free options:
- GitHub Pages (repo → Settings → Pages → deploy from `/jfredbot` or root)
- Cloudflare Pages
- Vercel / Netlify (drag folder or git connect)
- Render static site

**Important**: The final public URL must end with the `index.html` (or be directory index). Example: `https://yourname.github.io/jfredbot/`

### 2. Create / configure your bot

1. Talk to [@BotFather](https://t.me/BotFather)
2. `/newbot` → give it a name and username (e.g. `jfredbot` or `your_jfred_bot`)
3. Copy the **HTTP API token**

(Recommended) Set a Menu Button so users can always open the app:
- In BotFather: `/setmenubutton` → choose your bot → "Configure Menu Button" → choose "Web App" → paste your HTTPS URL to the mini app.

You can also attach web_app buttons to specific messages (see bot.py below).

### 3. Run the companion bot (recommended)

The bot gives users the actual launch button and receives data you send from the Mini App.

```bash
cd jfredbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` or export:

```bash
export BOT_TOKEN="123456:ABC-DEF..."
export JFREDBOT_URL="https://yourname.github.io/jfredbot/"   # must be the exact public URL
```

Then:

```bash
python bot.py
```

- Send `/start` to your bot in Telegram.
- It will reply with a big "🚀 Open jfredbot" button that launches the Mini App.
- Interact inside the app — when you use sendData flows (MainButton send, quick commands, +1 score), the bot receives a `web_app_data` update and can reply in the chat.

### 4. Test locally (outside Telegram)

Just open `index.html` in any browser. It degrades gracefully:
- Shows "Guest" user
- Uses localStorage for score
- Logs what would be sent via `sendData`
- MainButton is still wired (but real `sendData` requires the Telegram context)

For better local testing you can use the Telegram desktop/web "Web App" inspector or @webappbot test tools.

## What data gets sent to the bot?

Every meaningful action calls `sendData(JSON.stringify(payload))`:

- `{ "type": "score_change", "delta": 1, "total": 42, "ts": ... }`
- `{ "type": "quick_cmd", "cmd": "joke", "ts": ... }`
- `{ "type": "message", "text": "your freeform text", "ts": ... }`

In the bot these arrive as a normal message containing `web_app_data.data` (the JSON string) + `web_app_data.button_text`.

See `bot.py` for a minimal handler that prints + replies to the user.

## Security notes (for real usage)

- Never trust `initDataUnsafe` on the client for auth decisions.
- If you add a real backend, always validate `initData` (the raw string) server-side using HMAC-SHA256 with your bot token (see official docs: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).
- For production, add a tiny server (FastAPI, Flask, etc.) that:
  - Serves the static files (or proxy)
  - Runs the bot webhook (instead of polling)
  - Validates incoming data and stores real user state

## Optimizing further

- Swap the hero visual for a lighter SVG-only or CSS version (the GIF is ~430 KB and optional)
- Add real backend persistence + user accounts
- Implement proper loading skeletons if you add async data
- Use `CloudStorage` for more keys (limited to a few KB per key, ~5-10 keys typical)
- Add `Telegram.WebApp.openLink`, biometric auth, or `requestWriteAccess` where it makes sense
- For very heavy apps, consider React + Vite + service worker, but this vanilla version loads in <1s

## Files

- `index.html` — the complete optimized Mini App
- `bot.py` — minimal long-polling bot that launches the app and handles `web_app_data`
- `requirements.txt` — Python deps for the bot
- `assets/` — optional hero images + generator
- `generate_gif.py` — (one-time) heavy pixel GIF creator (the SVG in the app is preferred for speed)

## Development tips

- `window.JFRED` is exposed in the console for quick debugging (`JFRED.sendToBot(...)`, `JFRED.getScore()`)
- All haptic + MainButton usage is behind safe `if (tg && tg.XXX)` guards
- Keep the first paint extremely light — `ready()` is called synchronously at the top of the script

Enjoy building with jfredbot!

PRs and improvements welcome.
