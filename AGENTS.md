# jfredbot

A vanilla Telegram Mini App (`index.html` + `assets/`) that shows today's FIFA World Cup matches from ESPN's public API, plus a companion long-polling Telegram bot (`bot.py`).

## Cursor Cloud specific instructions

### Services

- Mini App (frontend): static files in `index.html` + `assets/`. No build step and zero runtime dependencies (only the remote `telegram-web-app.js` script). Serve it with a static server and open it in a browser: `python3 -m http.server 8000` from the repo root, then visit `http://localhost:8000/index.html`. It works standalone outside Telegram (shows "Guest"/degraded mode) and fetches live match data from `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard`, so it needs outbound internet to render matches.
- Companion bot (`bot.py`): a `requests`-based long-polling Telegram bot. Run with `python bot.py`. It requires a real `BOT_TOKEN` (from @BotFather) to connect to Telegram; without it the script prompts interactively on stdin and then exits. Optionally set `JFREDBOT_URL` to the public HTTPS URL of the hosted Mini App. The bot cannot be exercised end-to-end without a valid `BOT_TOKEN` secret.

### Non-obvious notes

- There are no automated tests and no linter configured in this repo. "Lint/test" here means a compile check: `python3 -m py_compile bot.py generate_gif.py`.
- `generate_gif.py` is an optional one-time asset generator and needs `Pillow` (and optionally `numpy`), which are intentionally NOT in `requirements.txt`. The app uses the committed inline SVG/GIF hero, so you normally don't need to run it. Install `Pillow`/`numpy` on demand only if you specifically want to regenerate `assets/hero-640x360.gif`.
- The Mini App's `sendData()` flows (score changes, quick commands, free-form messages) only actually deliver to the bot when the app is launched from inside Telegram via a `web_app` button; in a plain browser those calls are no-ops/logged only.
