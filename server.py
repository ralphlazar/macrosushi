"""
server.py
---------
Tiny local server for the MacroSushi editor tool.
Serves editor.html and writes published JSON straight to the repo.

Usage:
    python3 server.py

Then open: http://localhost:5123
"""

import json
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

REPO = Path(__file__).parent
PORT = 5123
TEMPLATE = REPO / "template.html"
INDEX = REPO / "index.html"


def rebuild_index(data):
    """Replace placeholders in template.html and write index.html."""
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"template.html not found at {TEMPLATE}")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{SUBJECT}}", data.get("subject", ""))
    for i, piece in enumerate(data["pieces"], 1):
        html = html.replace(f"{{{{PIECE_{i}}}}}", piece["text"])

    INDEX.write_text(html, encoding="utf-8")
    print(f"  rebuilt: {INDEX}")


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # clean up terminal output
        print(f"  {args[0]} {args[1]}")

    def do_GET(self):
        if self.path in ("/", "/editor.html"):
            self._serve_file(REPO / "editor.html", "text/html")
        else:
            self._send(404, "text/plain", b"not found")

    def do_POST(self):
        if self.path == "/publish":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send(400, "application/json", b'{"error":"invalid json"}')
                return

            today = date.today().isoformat()
            data["date"] = today
            filename = f"published_{today}.json"
            out_path = REPO / filename

            out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            print(f"\n  saved: {out_path}")

            try:
                rebuild_index(data)
            except Exception as e:
                print(f"  warning: could not rebuild index.html - {e}")

            try:
                import send_email
                send_email.main(str(out_path))
            except Exception as e:
                print(f"  warning: email send failed - {e}")

            resp = json.dumps({"ok": True, "file": filename}).encode()
            self._send(200, "application/json", resp)
        else:
            self._send(404, "application/json", b'{"error":"not found"}')

    def _serve_file(self, path, content_type):
        if not path.exists():
            self._send(404, "text/plain", b"file not found")
            return
        self._send(200, content_type, path.read_bytes())

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"macrosushi editor running at http://localhost:{PORT}")
    print(f"repo: {REPO}")
    print("ctrl-c to stop\n")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
