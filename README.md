# Premier League Scores

A lightweight web app for **today's Premier League matches** — live scores, kickoff times, venues, and club crests. Runs entirely in the browser with no backend required.

## Features

- Today's Premier League fixtures with club logos
- Live, scheduled, and final match status badges
- Auto-refresh every 60 seconds
- Light and dark mode (follows your system preference)
- Share via the Web Share API or clipboard fallback
- Mobile-friendly, single-page layout

## Quick start (Cloudflare Workers dev)

This project is set up for **Cloudflare Workers static assets**. Install dependencies and run the local dev server:

```bash
npm install
npm run dev
```

Wrangler serves the app at http://localhost:8787/ by default. Match data is fetched client-side from ESPN's public API (CORS-enabled), so no Worker proxy is needed.

Deploy to Cloudflare:

```bash
npm run deploy
```

## Alternative: Python local server

Requires Python 3.6+ (stdlib only — no dependencies).

```bash
python3 serve.py
```

This starts a local server at http://127.0.0.1:8080/ and opens it in your default browser.

Options:

```bash
python3 serve.py --port 3000      # use a different port
python3 serve.py --no-open        # start server without opening a browser
```

## Deploy anywhere

The app is a static site — just host the `public/` folder on any static host:

- Cloudflare Workers (included — see above)
- GitHub Pages
- Cloudflare Pages
- Vercel / Netlify

Match data is fetched client-side from ESPN's English Premier League scoreboard API (`eng.1`).

## Files

| File | Purpose |
|------|---------|
| `public/index.html` | Complete web app (HTML, CSS, JS) |
| `wrangler.jsonc` | Cloudflare Workers static assets config |
| `serve.py` | Alternative local dev server (Python) |
| `public/assets/` | Optional hero images |
| `generate_gif.py` | One-time asset generator (optional) |

## Development

For quick iteration without Wrangler:

```bash
python3 -m http.server 8080 --directory public
```

Then visit http://localhost:8080/ in your browser.

> **Note:** Opening `index.html` directly as a `file://` URL may fail because browsers block cross-origin requests to the ESPN API. Always serve over HTTP.
