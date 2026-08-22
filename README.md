# World Cup Today

A lightweight web app for **today's FIFA World Cup 2026 matches** — live scores, kickoff times, and venues. Runs entirely in the browser with no backend required.

## Features

- Today's World Cup fixtures with team flags and venues
- Live, scheduled, and final match status badges
- Auto-refresh every 60 seconds
- Light and dark mode (follows your system preference)
- Share via the Web Share API or clipboard fallback
- Mobile-friendly, single-page layout

## Quick start

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

The app is a static site — just host `index.html` (and optionally `assets/`) on any static host:

- GitHub Pages
- Cloudflare Pages
- Vercel / Netlify
- Any web server (`nginx`, `apache`, etc.)

Match data is fetched client-side from ESPN's public scoreboard API.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Complete web app (HTML, CSS, JS) |
| `serve.py` | Local dev server with auto-open browser |
| `assets/` | Optional hero images |
| `generate_gif.py` | One-time asset generator (optional) |

## Development

For quick iteration without the launcher script:

```bash
python3 -m http.server 8080
```

Then visit http://localhost:8080/ in your browser.

> **Note:** Opening `index.html` directly as a `file://` URL may fail because browsers block cross-origin requests to the ESPN API. Always serve over HTTP.
