# Nolan AI — Backend

FastAPI backend implementing the three agents described in `HANDOFF.md`
(Search Engine, Script Generation, Analytics & Feedback), rebuilt outside
Relevance AI against a real Postgres/Supabase database.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and DATABASE_URL at minimum
```

Provision the database (Supabase or local Postgres 14+):

```bash
psql "$DATABASE_URL" -f db/schema.sql
```

Run the API:

```bash
uvicorn app.main:app --reload
```

`GET /health` should return `{"status": "ok", ...}`. The scheduler
(Monday 10am search run, weekly digest, hourly analytics fetch sweep)
starts automatically with the app — see `app/scheduler.py`.

## Structure

```
backend/
├── db/schema.sql            # Postgres DDL — source of truth for the 6-table schema
├── app/
│   ├── main.py               # FastAPI app, router wiring, scheduler lifespan
│   ├── config.py              # env-var settings
│   ├── scheduler.py           # cron triggers (APScheduler)
│   ├── db/
│   │   ├── database.py        # engine/session
│   │   └── models.py          # SQLAlchemy models mirroring schema.sql
│   ├── agents/
│   │   ├── search_agent.py    # Tasks 1-8 (search-agent-prompt.md)
│   │   ├── script_agent.py    # Tasks 0-21 (script-agent-prompt.md)
│   │   ├── analytics_agent.py # Tasks 1-10 (HANDOFF.md spec)
│   │   └── prompts/           # system prompts + knowledge bases per agent
│   ├── services/
│   │   ├── anthropic_client.py  # shared Claude wrapper (+ web search tool)
│   │   ├── instagram_client.py  # Graph API — see "What's stubbed" below
│   │   ├── email_client.py      # SMTP alerts
│   │   └── error_logger.py      # writes to Error Management table
│   └── api/routes/
│       ├── chat.py             # free-text dispatch (mirrors each agent's Trigger Conditions)
│       ├── topics.py           # Master Topics CRUD (pick/reject/add-Rishi's-idea)
│       ├── scripts.py          # generate + mark-posted
│       ├── analytics.py        # digest / ad-hoc report / manual fetch trigger
│       ├── feedback.py         # script-validation.html posts here
│       └── errors.py           # Error Management read endpoint
```

## What's real vs. stubbed

- **Search & Script agents**: fully wired to Claude (with web search for
  the Search Agent's topic discovery and no-web-search for scripting),
  reading/writing real Postgres tables. Nothing mocked.
- **Analytics Agent**: the DB writes, baseline math, anomaly flagging,
  digest, and feedback ingestion are all real and testable today against
  seed data. The Instagram Graph API calls in
  `services/instagram_client.py` are real HTTP calls, not mocks — they
  will work as soon as `INSTAGRAM_ACCESS_TOKEN` /
  `INSTAGRAM_BUSINESS_ACCOUNT_ID` are set (see Setup Dependencies in
  `HANDOFF.md`). Until then, calling them raises `InstagramAuthError`,
  which the agent turns into the documented critical alert: *"Instagram
  connection needs re-authorization — analytics paused until
  reconnected."*
- **Email alerts**: real SMTP send via `smtplib`; raises
  `EmailNotConfiguredError` (logged, not fatal) until `SMTP_HOST` /
  `ALERT_RECIPIENT_EMAIL` are set.
- **Auth**: `/chat`, `/topics`, `/scripts`, `/analytics`, `/errors` all
  require a valid Supabase-issued JWT (`app/services/auth.py`) — verified
  against the project's public JWKS (newer Supabase projects sign tokens
  asymmetrically with ES256, not a shared HS256 secret), fetched from
  `SUPABASE_URL/auth/v1/.well-known/jwks.json`. `/feedback` and `/health`
  stay open (script-validation.html submits without logging in). Until
  `SUPABASE_URL` is set, protected routes return 503 rather than
  silently allowing access. See `../frontend/` for the Google-login client.

## Known gaps / next steps

- No Supabase project exists yet — auth code is real but untestable
  end-to-end until one is created and `SUPABASE_URL` /
  `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` are set (Setup
  Dependencies in `HANDOFF.md`).
- Chat intent matching is deliberately simple keyword matching (same
  literal trigger-phrase style as the original docs), not general NLU —
  the frontend passes structured `topic_id`/`script_id` alongside the
  message once the user has picked something from a list, since raw
  UUIDs aren't chat-friendly (see `frontend/src/components/TopicPicker.tsx`).
- `Script.instagram_media_id` (set via `POST /scripts/{id}/posted`) is
  what lets the Analytics Agent find which Graph API object to pull for
  a given script — populate it when a reel actually goes up.
- The 48h fetch delay and the "digest precedes Monday search run"
  sequencing are both flagged in `HANDOFF.md` as assumptions to
  sanity-check once live data exists — nothing here should be treated as
  final tuning.
