#!/usr/bin/env python3
"""Serve World Cup Today locally and open it in your browser."""

import argparse
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "public"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch World Cup Today in your browser")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser tab automatically")
    args = parser.parse_args()

    url = f"http://127.0.0.1:{args.port}/"

    with socketserver.TCPServer(("", args.port), Handler) as httpd:
        print(f"Serving World Cup Today at {url}")
        print("Press Ctrl+C to stop")

        if not args.no_open:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
