"""
send_email.py
-------------
Sends today's MacroSushi edition via Resend.
Called by server.py on publish, or run manually:

    python3 send_email.py published_2026-04-13.json
"""

import json
import os
import sys
import requests
from datetime import date
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).parent
DOTENV_PATH = Path.home() / "Desktop" / ".env"

FROM = "yum@macrosushi.com"
RESEND_API = "https://api.resend.com/emails"


def load_env():
    if not DOTENV_PATH.exists():
        raise FileNotFoundError(f".env not found at {DOTENV_PATH}")
    for line in DOTENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def load_published(path):
    data = json.loads(Path(path).read_text())
    if len(data["pieces"]) != 3:
        raise ValueError(f"expected 3 pieces, got {len(data['pieces'])}")
    return data


def load_subscribers():
    worker_url = os.environ.get("WORKER_URL", "https://macrosushi.com")
    secret = os.environ.get("WORKER_SECRET")
    if not secret:
        raise ValueError("WORKER_SECRET not found in .env")

    r = requests.get(
        f"{worker_url}/subscribers",
        headers={"Authorization": f"Bearer {secret}"},
        timeout=15
    )
    if r.status_code != 200:
        print(f"  failed to fetch subscribers: {r.status_code} - {r.text}")
        return []

    data = r.json()
    return data.get("subscribers", [])


def build_html(data, unsub_url):
    pieces = data["pieces"]

    def piece_html(text):
        return f"""
      <div style="padding:1.75rem 0;border-top:0.5px solid #eee;text-align:center;">
        <div style="width:9px;height:9px;border-radius:50%;background:#c9684a;opacity:0.6;margin:0 auto 0.6rem;"></div>
        <div style="font-size:15px;color:#1a1a1a;line-height:1.75;font-weight:300;">{text}</div>
      </div>"""

    pieces_html = "".join(piece_html(p["text"]) for p in pieces)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#fff;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <div style="max-width:440px;margin:0 auto;padding:3rem 1.5rem;text-align:center;">

    <div style="font-size:22px;font-weight:300;color:#bbb;letter-spacing:0.02em;margin-bottom:4px;">
      macro<span style="color:#c9684a;">sushi</span>
    </div>
    <div style="font-size:12px;color:#bbb;margin-bottom:3rem;font-weight:300;">
      3 fresh pieces, every weekday.
    </div>

    <div style="margin-bottom:3.5rem;">
      {pieces_html}
      <div style="border-bottom:0.5px solid #eee;"></div>
    </div>

    <div style="font-size:11px;color:#bbb;margin-bottom:2.5rem;">that's it. off you go.</div>

    <div style="font-size:11px;color:#ccc;">
      powered by <a href="https://macrosnaps.app" style="color:#c9684a;text-decoration:none;">macrosnaps</a>
      &nbsp;&middot;&nbsp;
      <a href="https://macrosushi.com" style="color:#c9684a;text-decoration:none;">macrosushi.com</a>
      &nbsp;&middot;&nbsp;
      <a href="{unsub_url}" style="color:#ccc;text-decoration:none;">unsubscribe</a>
    </div>

  </div>
</body>
</html>"""


def send_to(api_key, to_email, subject, html):
    try:
        r = requests.post(
            RESEND_API,
            json={"from": FROM, "to": [to_email], "subject": subject, "html": html},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.status_code
        else:
            return False, f"{r.status_code} - {r.text}"
    except Exception as e:
        return False, str(e)


def main(published_path=None):
    load_env()

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY not found in .env")

    worker_url = os.environ.get("WORKER_URL", "https://macrosushi.com")

    # find published file
    if published_path:
        path = Path(published_path)
    else:
        today = date.today().isoformat()
        path = REPO / f"published_{today}.json"

    if not path.exists():
        raise FileNotFoundError(f"published file not found: {path}")

    data = load_published(path)
    subscribers = load_subscribers()

    if not subscribers:
        print("  no subscribers found")
        return

    subject = data["subject"].capitalize()

    print(f"  sending to {len(subscribers)} subscriber(s)...")
    ok = 0
    failed = 0
    for sub in subscribers:
        email = sub["email"]
        token = sub["token"]
        unsub_url = f"{worker_url}/unsubscribe?email={quote(email)}&token={token}"
        html = build_html(data, unsub_url)

        success, info = send_to(api_key, email, subject, html)
        if success:
            print(f"    sent: {email}")
            ok += 1
        else:
            print(f"    failed: {email} - {info}")
            failed += 1

    print(f"  done - {ok} sent, {failed} failed")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
