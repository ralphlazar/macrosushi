"""
update_sushi.py
---------------
Run this manually each weekday to generate six candidate pieces for MacroSushi.
Writes drafts.json to the repo root. Does not publish anything.

Usage:
    python update_sushi.py

Requires:
    pip install anthropic python-dotenv
"""

import json
import os
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# --- config -----------------------------------------------------------

DOTENV_PATH = Path.home() / "Desktop" / ".env"
DRAFTS_PATH = Path.home() / "RALPH" / "AI" / "macrosushi" / "drafts.json"

MODEL = "claude-sonnet-4-6"

PROMPT = """You are the editor of MacroSushi, a daily briefing that distills the global
economy into three pieces for smart, curious people who don't work in finance.

Search the web for the most significant global economic developments from the
last 24 hours. Then write 6 candidate pieces for today's edition.

RULES:
- two sentences per piece. no more.
- everything lowercase.
- no em dashes.
- no jargon that requires a textbook. tariffs fine. yield curve not fine.
- dinner party casual - smart but not showing off.
- the test: could a smart 28-year-old who reads the news but has never worked
  in finance read it and think 'oh, i actually get that'? if yes: in.
  if no: rewrite.

COVERAGE: write 6 pieces that are as varied as possible in region and theme.
don't give me 6 takes on the same story. but follow the news - if it's a
big US day, that's fine.

SUBJECT: write a subject line for today's edition. one short phrase,
lowercase, naming the dominant story of the day. no clickbait.
no punctuation except a single full stop at the end. if no single story
dominates, name the most surprising one.

EXAMPLES OF THE RIGHT VOICE:
"america's new tariffs are hitting hard and fast. factories across asia are
already producing less, for the second month running."

"prices in europe and the uk are still rising, even as the economy slows.
wages went up, businesses passed the cost on, and nobody quite knows how
to stop it."

"india is quietly having a great year. people are spending, companies are
piling in, and it's becoming the world's favourite alternative to china."

OUTPUT: return valid JSON only. no preamble. no commentary. no markdown.

{
  "subject": "india's moment.",
  "pieces": [
    { "text": "..." },
    { "text": "..." },
    { "text": "..." },
    { "text": "..." },
    { "text": "..." },
    { "text": "..." }
  ]
}"""

# --- main -------------------------------------------------------------

def main():
    # load .env from Desktop
    if not DOTENV_PATH.exists():
        raise FileNotFoundError(f".env not found at {DOTENV_PATH}")
    load_dotenv(DOTENV_PATH)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env")

    client = anthropic.Anthropic(api_key=api_key)

    today = date.today().isoformat()  # e.g. 2026-04-13
    drafts_path = DRAFTS_PATH.parent / f"drafts_{today}.json"

    # step 1: gather today's news with web search
    print("step 1/2 - searching the web...")

    research_prompt = f"""Today is {today}. Search the web for the most significant global
economic developments from the last 24 hours - stories published today or late yesterday only.
Find at least 6 distinct stories covering different regions and themes.
Summarise what you find - raw notes are fine, this is for internal use only."""

    r1 = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 8
        }],
        messages=[{"role": "user", "content": research_prompt}]
    )

    # pull all text from the research response
    research_text = "\n\n".join(
        block.text for block in r1.content
        if block.type == "text" and block.text.strip()
    )

    if not research_text:
        raise ValueError("no text returned from web search step")

    print(f"  got {len(research_text)} chars of research")

    # step 2: write the pieces and return JSON
    print("step 2/2 - writing pieces...")

    format_prompt = f"""You are the editor of MacroSushi. Here are today's economic news notes:

{research_text}

Using these notes, write 6 candidate pieces following these rules exactly:
- two sentences per piece. no more.
- everything lowercase.
- no em dashes.
- no jargon that requires a textbook. tariffs fine. yield curve not fine.
- dinner party casual - smart but not showing off.
- the test: could a smart 28-year-old who reads the news but has never worked
  in finance read it and think 'oh, i actually get that'? if yes: in. if no: rewrite.
- cover 6 different regions or themes. varied as possible.

Also write a subject line: one short phrase, lowercase, naming the dominant story.
no clickbait. no punctuation except a single full stop at the end.

Return ONLY this JSON. No preamble. No commentary. No markdown fences.

{{"subject":"india's moment.","pieces":[{{"text":"..."}},{{"text":"..."}},{{"text":"..."}},{{"text":"..."}},{{"text":"..."}},{{"text":"..."}}]}}"""

    r2 = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": format_prompt}]
    )

    raw_json = None
    for block in reversed(r2.content):
        if block.type == "text" and block.text.strip():
            raw_json = block.text.strip()
            break

    if not raw_json:
        raise ValueError("no text returned from formatting step")

    # strip markdown fences if present
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
        raw_json = raw_json.strip()

    # strip markdown fences if claude added them
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
        raw_json = raw_json.strip()

    data = json.loads(raw_json)

    # validate structure
    if "subject" not in data or "pieces" not in data:
        raise ValueError("unexpected JSON structure from claude")
    if len(data["pieces"]) != 6:
        raise ValueError(f"expected 6 pieces, got {len(data['pieces'])}")

    data["date"] = today

    # write dated drafts file
    drafts_path.parent.mkdir(parents=True, exist_ok=True)
    with open(drafts_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\ndrafts written to {drafts_path}")
    print(f"date:    {today}")
    print(f"subject: {data['subject']}")
    print(f"pieces:  {len(data['pieces'])}")
    print("\npieces preview:")
    for i, piece in enumerate(data["pieces"], 1):
        preview = piece["text"][:80] + "..." if len(piece["text"]) > 80 else piece["text"]
        print(f"  {i}. {preview}")


if __name__ == "__main__":
    main()
