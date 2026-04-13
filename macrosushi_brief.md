# macrosushi - product & build brief

*3 fresh pieces, every weekday.*

last updated: april 2026

---

## the idea

MacroSushi is a daily one-page website and email/sms/whatsapp product that distills the global economy into exactly three pieces every weekday. nothing more.

the insight: the internet has a hosepipe problem. everyone is drowning in macro data, newsletters, dashboards and noise. MacroSushi is the antidote. three sentences. served fresh. done.

MacroSushi is editorially driven. every weekday, the editor runs a single script that searches the web for the most significant global economic developments of the last 24 hours, generates six candidate pieces via claude, and presents them in a lightweight editing tool. the editor picks three, tweaks the wording, and publishes. the whole process takes around fifteen minutes.

MacroSnaps - a rigorous daily data engine covering 12 major economies - sits in the background as a credibility layer, linked from the footer. it is not part of the content pipeline. the kitchen is serious. the menu is simple.

---

## the product

### what it is

a single webpage - macrosushi.com - that shows three pieces about the global economy today. updated every weekday. no navigation. no archive. no dashboard. just today.

the same three pieces are delivered by email, sms, and whatsapp to subscribers every weekday morning.

### what it is not

- a news site
- a financial data dashboard
- a newsletter with five stories and three ads
- a product that requires you to understand economics
- automated - a human editor picks and edits every piece before it goes out

### cadence

monday to friday only. the script is run manually by the editor - there is no cron job, no scheduled automation. the editor decides when it goes out.

### the writing rules

- two sentences per piece. maximum.
- dinner party casual. smart but not showing off.
- no jargon that requires a textbook. tariffs fine. yield curve not fine.
- no em dashes.
- everything lowercase.
- the test: could a smart 28-year-old who reads the news but has never worked in finance read it and think "oh, i actually get that"? if yes: in. if no: rewrite.

---

## the page

the full homepage, in order from top to bottom:

**logo** - macrosushi (macro in light grey, sushi in salmon)

**tagline** - 3 fresh pieces, every weekday.

**three pieces** - centre-aligned. salmon pip above each piece. text centred beneath. separated by a hairline rule.

**subscribe** - yum, yes please / by email / by whatsapp or text

**sign-off** - that's it. off you go.

**footer** - powered by macrosnaps (opens in new tab)

design notes: white background. light grey and salmon only. everything lowercase. no borders, no boxes, no icons. the salmon pip above each piece is the only decoration. the page breathes. no share buttons.

---

## the editor tool

a private lightweight webpage - served locally by server.py at http://localhost:5123 - that sits between the script and publication. no login system needed.

the tool shows all six drafted pieces as cards. the editor selects three, edits the text inline, and hits publish. on publish the tool:

- writes published_YYYY-MM-DD.json to the repo root
- rebuilds index.html with the final three pieces
- triggers the resend email send
- queues the twilio sms send (not yet built)
- queues the whatsapp send (not yet built)

the six candidate pieces are written to drafts_YYYY-MM-DD.json by update_sushi.py. the editor tool reads from this file via a file input button in the browser.

---

## the engine

### update_sushi.py

a single python script, run manually by the editor each weekday. two-step process:

step 1 - calls claude with web search enabled and today's date injected into the prompt. gathers raw research notes on the most significant global economic developments of the last 24 hours.

step 2 - passes the research notes to claude without web search and asks for six candidate pieces as clean JSON. writes the output to drafts_YYYY-MM-DD.json.

the script does not publish. it only generates and saves drafts. publication is always a deliberate human action via the editor tool.

### the prompt

step 1 research prompt includes today's date and asks for at least 6 distinct stories covering different regions and themes from the last 24 hours only.

step 2 format prompt passes the research and instructs claude to write 6 pieces following all writing rules, plus a subject line. returns JSON only, no preamble.

### subject line rules

names the dominant story of the day. one short phrase. lowercase. single full stop at the end. no clickbait. if no single story dominates, name the most surprising one.

example: "india's moment." not: "why india is booming right now"

---

## the repo

location: ~/RALPH/AI/macrosushi/

github: https://github.com/ralphlazar/macrosushi

files:

- update_sushi.py - daily draft generator
- server.py - local editor server (http://localhost:5123)
- editor.html - the editing ui, served by server.py
- template.html - macrosushi page with content placeholders
- index.html - rebuilt on every publish, deployed to macrosushi.com
- send_email.py - sends the edition via resend
- subscribers.json - flat list of email subscribers (not in git)
- macrosushi_brief.md - this file

.gitignore excludes: .env, drafts_*.json, published_*.json, subscribers.json, __pycache__

---

## distribution

### website

macrosushi.com - deployed via cloudflare pages, connected to the github repo. every push to main redeploys the site. currently live at https://macrosushi.pages.dev. custom domain not yet activated - waiting until distribution is fully in place.

### email

sent via resend (resend.com). domain macrosushi.com verified. sending from yum@macrosushi.com. html email matches the macrosushi.com aesthetic. unsubscribe link in footer. subscriber list managed as subscribers.json in the repo (excluded from git).

pricing: free up to 3,000 emails/month. $20/month up to 50,000.

status: working. wired into the publish action in server.py.

### sms

to be built. sent via twilio. the three pieces delivered as a single message. cost: approximately 4-5p per message per subscriber in the uk, ~1p in the us. twilio campaign registration required for us sending.

### whatsapp

phase 1 (soft launch): whatsapp channel. no api, no meta approval. manual broadcast.
phase 2 (scaled): whatsapp business api via twilio or meta cloud api. requires meta business verification and pre-approved message templates.

status: not yet built.

---

## delivery stack summary

- email: resend - working
- sms: twilio - not yet built
- whatsapp (early): whatsapp channel (manual) - not yet set up
- whatsapp (scaled): whatsapp business api via twilio - not yet built
- website: cloudflare pages + github - working, custom domain pending

---

## environment

.env location: ~/Desktop/.env

keys required:
- ANTHROPIC_API_KEY
- RESEND_API_KEY

keys to add when ready:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_FROM_NUMBER

---

## next steps

### 1. twilio sms

- create twilio account at https://twilio.com
- buy a uk number (or us number if sending to us subscribers)
- register the messaging campaign (required for us sending - takes a few days)
- add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER to ~/Desktop/.env
- build send_sms.py - reads published_YYYY-MM-DD.json, sends one message containing all three pieces to each number in subscribers.json
- wire into server.py publish action, same pattern as send_email.py
- add sms subscriber list to subscribers.json alongside email list

### 2. signup flows

- wire up the "by email" link on macrosushi.com to a simple form or mailto
- wire up the "by whatsapp or text" link
- decide: hosted form (typeform, tally) or build a lightweight /subscribe endpoint in server.py
- handle new subscribers writing to subscribers.json automatically
- handle unsubscribe - currently a mailto link, needs a real handler

### 3. whatsapp channel (soft launch)

- create a whatsapp channel at https://business.whatsapp.com
- add the channel link to the "by whatsapp or text" signup on the site
- manual broadcast for now while meta business api approval runs in parallel

### 4. custom domain

- go live once sms and signup flows are in place
- in cloudflare pages, add macrosushi.com as a custom domain
- add www.macrosushi.com redirect if desired
- test all three distribution channels before announcing

### 5. meta business api (whatsapp scaled)

- begin meta business verification at https://business.facebook.com
- takes 1-2 weeks
- once approved, build whatsapp send into server.py via twilio or meta cloud api directly

### 6. git push workflow

after each session, push completed work to github:

```bash
cd ~/RALPH/AI/macrosushi && git add -A && git commit -m "your message here" && git push
```

cloudflare pages redeploys automatically on every push to main.

---

## tone of voice

the voice is a well-travelled friend who happens to know a lot about how the world works, but never makes you feel stupid for not knowing. slightly wry. never alarming. never cheerleading.

- slightly opinionated, never political
- warm, not corporate
- confident, not arrogant
- plain english. always.

---

## macrosnaps

MacroSnaps is a daily data engine that has been running for over a year. it fetches market data across 12 economies (USA, GBR, DEU, FRA, ITA, CAN, JPN, CHN, IND, BRA, ZAF, RUS), updates commodity data and stories, generates headlines and metric stories per economy, and builds and publishes macrosnaps.app.

MacroSnaps is not part of the MacroSushi content pipeline. it is an ambient credibility layer - linked from the MacroSushi footer, visible to curious readers, but not feeding the daily pieces.

---

## session working rules

- files always download to ~/Downloads/ - always provide bash copy commands using $(ls -t ~/Downloads/filename*.ext | head -1) to grab the most recently downloaded version, with quotes around the subshell to handle mac's space-in-filename convention
- always show a plan before building. never start without it.
- always ask for confirmation after showing the plan. wait for go-ahead.
- all text must not look ai-written. no em-dashes - use regular hyphens. no apostrophes in JSON summary fields.
- add to brief when asked. never present as download unless asked.
- always give the brief as a .md file for download.
- when asked for bash code, respond with just the code block. no preamble.
- do not push to git during development. push only when session work is complete and confirmed.
- when you need to see a file from the local repo, give bash code to copy it to downloads, and wait for the user to upload it.
- always give urls as clickable hyperlinks.
- when asked to add a rule, add it to the brief. do not present the revised brief unless asked.
- never ask two questions at the same time.
- i never manually edit files. claude does it. if a file needs a patch, do it, or ask the user to upload the file.
