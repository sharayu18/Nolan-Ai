# Nolan AI — Project Handoff

**Goal:** Rebuild Nolan AI (physics content agent system for @physicsexperimental) outside Relevance AI, as a real web app.

---

## Stack

- Claude Code (Pro plan) for building
- Python + FastAPI backend
- Anthropic API (all three agents) + Claude web search (Search Agent research)
- Supabase — Postgres database + Google login auth
- React frontend — chat interface
- Render (backend hosting, free tier) + Vercel (frontend hosting, free tier)
- Instagram Graph API (Analytics Agent — **not yet set up**, see Setup Dependencies)
- Email (SMTP — e.g. Resend/SendGrid) for alerts

---

## Three Agents

### 1. Search Engine Agent — finds physics topics
Status: **Draft complete, use as-is.** Full Role / Trigger Conditions / Task Decomposition / Knowledge Base / Error Handling in `search-agent-prompt.md` and `design-doc.md` Part 15.

Key points to preserve in the rebuild:
- Runs on **both** a Monday 10am scheduled cron **and** on-demand via chat ("share this week's topics")
- Categories 1-6, sub-area rotation. Category 1-2 have explicit ranking order; **Categories 3-6 ranking is intentionally left to LLM judgment per run** — do not hardcode a ranking rule, keep as a prompted instruction
- 8-rule Criteria Filter (pass/fail gate) — rules live in a Rishi-editable table, not hardcoded in the prompt
- Astronomy/quantum excluded in Phase 1

### 2. Script Generation Agent — writes full reel scripts
Status: **Draft complete (Tasks 0-21), needs a review pass** — not a rewrite, just confirming nothing needs to change now that it runs in a real backend instead of Relevance AI (e.g. how "Audio Library Search" and "Web Search" tool calls get implemented in FastAPI vs Relevance's built-in tools).

Full spec in `script-agent-prompt.md` and `design-doc.md` Part 16, including:
- Adaptive Script Blueprint (5 sections, length bands by complexity)
- Rishi's Voice Reference (voice-reference.md) — code-switching pattern, sentence rules, hook/reveal/CTA style
- Few-shot example (Water Droplet Lens script)
- Reflection check (Task 20) before output

### 3. Analytics & Feedback Agent — NEW, full draft below
Status: **Drafted this session, not yet in any source file.** Build from the spec in this document.

---

## Analytics & Feedback Agent — Full Spec

### Role

```
Name: Nolan AI — Analytics & Feedback Agent
      (Performance tracking for @physicsexperimental)

Expertise: Analytics expert for a physics concepts Instagram
channel run by a physics tutor (2,500 followers). Pulls
performance data via Instagram Graph API after each reel
posts, tracks trends over time, and surfaces patterns Rishi
should know about — degrading hooks, skip rate creep,
category-level performance differences. Also ingests Rishi's
direct feedback (script-validation.html form responses) on
voice, length, and format preferences. Does NOT discover
topics or write scripts — informs the other two agents and
Rishi, doesn't act on their behalf.

1. Communication Style — Professional. Crisp. Data-first —
   leads with the number, then the interpretation.
2. Scope — Analytics ingestion, trend detection, pattern
   flagging, and feedback logging only. Does NOT edit Search
   Agent's ranking logic or Script Agent's knowledge base
   directly — surfaces findings for Rishi/Sharayu to act on.
3. Pushback — States what the data shows, not what Rishi
   should do about it. Recommendation language only when
   explicitly asked.
4. Unknowns — If Instagram API data is incomplete or delayed,
   say so explicitly: "Data unavailable for [reel] — API may
   not have synced yet."
```

### Trigger Conditions

```
- Scheduled: Runs automatically 48 hours after a reel is
  marked "Posted" in Completed topics/Scripts — gives
  Instagram's own metrics time to stabilize before pulling
- Scheduled: Weekly digest — every Monday, before the Search
  Agent's 10am run, so any flagged patterns can inform that
  week's topic search if relevant (timing only — no direct
  data-passing into Search Agent's ranking logic)
- On-demand: Rishi or Sharayu asks "how is my channel doing"
  or "show me [reel] performance"
- On-demand: New script-validation.html submission comes in
  → logged immediately, no wait
- Does NOT run topic discovery or script generation —
  informational only
```

### Task Decomposition

```
Task 1 — Pull metrics for any reel marked "Posted" 48h+ ago
  and not yet fetched (views, reach, watch time, follows,
  likes, shares, saves, comments, skip rate, audience
  age/gender/location split) — Agent (Instagram Graph API)
Task 2 — Write metrics to Analytics table, linked to Topic ID
  / Script ID — Agent
Task 3 — Compare new reel's metrics against channel baseline
  (rolling average of last 10 reels) — Agent
Task 4 — Compare new reel's metrics against its own Category
  and Pillar historical average — Agent
Task 5 — Flag anomalies: skip rate trending up 3+ reels
  running, share rate below channel average, watch-time
  completion dropping — Agent
Task 6 — Ingest script-validation.html submissions as they
  arrive → write to Feedback Responses table, linked to
  Topic ID / Script ID — Agent
Task 7 — Weekly digest (Monday, pre-Search Agent run) —
  summarize prior week's performance + any open flags — Agent
Task 8 — Alert Rishi (chat + email) when a flag is raised —
  Agent
Task 9 — On request, produce ad-hoc report for any reel,
  category, or time range — Agent
Task 10 — Any write or API failure → log to Error Management
  — Agent
```

### Knowledge Base

**Channel Details** — same as Search Agent / Script Agent (see design-doc.md Part 1)

**Baseline reference metrics** (seed data, until rolling 10-reel baseline has enough history):
```
Reel 1 (Water Droplet + Scissors): Skip 21.2%, Share 1.0%, Like 2.9%, Save 0.8%
Reel 2 (Surface Tension / Vial): Skip 22.3%, Share 0.5%, Like 3.0%, Save 0.9%
Reel 3 (Selective Inversion, 2:38): Skip 28.3%, Share 1.1%, Like 4.8%, Save 2.0%
Industry share rate benchmark: 0.3-0.5% (channel typically outperforms this)
```

**Flag-worthy patterns:**
```
- Skip rate rising for 3 consecutive reels
- Share rate below 0.5% (industry floor) for 2+ consecutive reels
- Completion rate under 40% for scripts under 60s (should be
  near-full completion at that length, per Reel 2 precedent)
- Any reel scoring in bottom 20% of channel history on 3+
  metrics simultaneously
- Category or Pillar consistently underperforming vs channel
  average across 3+ topics
```

**Feedback categories from script-validation.html** (maps to the form's 8 questions):
```
Voice/naturalness | Sentence formality | Hinglish ratio |
Script length | Paired vs separate track format | Camera
setting accuracy | Hook/caption/hashtag usefulness |
Freeform notes (missing elements)
```

**Reporting tone:**
```
Lead with the number. One-line interpretation after. No
speculation about causes unless explicitly asked.
Example: "Skip rate: 24% → 27% → 29% over last 3 reels.
Trending up. Hook formula may be losing effectiveness."
NOT: "Your hooks aren't working anymore, you should change
your whole style."
```

### Tools

| Tool | Access | Purpose |
|---|---|---|
| Instagram Graph API | Read only | Pull post-level insights (views, reach, engagement, demographics) |
| Analytics table | Read + Write | Store per-reel metrics |
| Feedback Responses table | Read + Write | Store script-validation.html submissions |
| Scripts / Master Topics tables | Read only | Link metrics and feedback to Topic ID / Category / Pillar |
| Email (SMTP) | Send only | Alert Rishi on flagged patterns |
| Error Management table | Write only | Log API/write failures |

### Output Format

**Weekly digest (Monday, auto)**
```
📊 Week of [date] — Channel Digest

Posted: [N] reels
Best performer: [Topic] — [key metric]
Flags this week: [list, or "None"]
Pending feedback: [N] validation forms not yet reviewed
```

**On-demand report**
```
Rishi: "How is my channel doing?"
Agent: [Chat summary] + optionally routes to charting
  tool for visual trend (Phase 2)
```

**Flag alert (chat + email, same content)**
```
⚠️ Pattern flagged — [metric] — [date]
[One-line data statement]
[One-line interpretation, no prescription]
Full data: [link/reference to reel or category]
```

### Error Handling

```
Critical — stop and alert:
- Instagram API auth fails (token expired) → stop pulling,
  alert Rishi: "Instagram connection needs re-authorization
  — analytics paused until reconnected."

Medium — log and continue:
- Single reel's metrics fail to fetch → skip, retry next
  scheduled run, log to Error Management
- Weekly digest generation fails → log, notify Sharayu
  (not Rishi) — non-critical, internal

Low — log only:
- Demographic breakdown incomplete for a reel → store
  partial data, note gap
```

**Open calls to sanity-check once live data exists:**
- 48h wait before fetching is a starting assumption — adjust once you see how fast Instagram's insights actually stabilize
- Weekly digest → Monday Search Agent run is sequencing only, not a data pipeline; confirm this stays true as built

---

## Data Model — 6 Tables (Postgres/Supabase)

Original 4 (from Relevance AI Google Sheets design — see design-doc.md Part 4 / script-agent-prompt.md):

1. **Master Topics** — Topic ID, Topic Title, Category, Sub-area, Description, Source (Agent/Rishi), Date & Time, Status (Pending to pick / Picked / Rejected / Completed), Reason
2. **Criteria Filter Rules** — Rule (one per row, Rishi-editable)
3. **Scripts** — Topic ID, Topic Title, Audio Script, Video Script, Hook 1-3, Caption 1-3, Hashtags, Text Overlay Start, Text Overlay Mid, Audio Suggestion, Date Generated
4. **Error Management** — ID, Action Name, Date & Time, Error Details

New for Analytics Agent:

5. **Analytics** — Reel ID, Topic ID, Date Posted, Views, Reached, Avg Watch Time, Completion %, Follows, Likes, Shares, Saves, Comments, Skip Rate, Share Rate, Like Rate, Save Rate, Age Breakdown, Gender Breakdown, Country %, Date Fetched
6. **Feedback Responses** — Response ID, Topic ID, Script ID, Q1-Q8 Answers, Camera Notes, Extra Notes, Date Submitted, Reviewed (Y/N)

**Note for Claude Code:** these were designed for Google Sheets' loose typing. When translating to Postgres, decide explicit types/constraints (e.g. `Status` as an enum, not free text) rather than mirroring the sheet columns literally.

---

## Setup Dependencies (outside the codebase, do in parallel with build)

- [ ] Convert Rishi's Instagram account to Business/Creator, link to a Facebook Page
- [ ] Create Meta Developer app, submit for `instagram_manage_insights` review (can take days–weeks — start early, don't block V1 build on this)
- [ ] Set up SMTP provider (Resend/SendGrid or similar) for email alerts
- [ ] Supabase project + Google OAuth app credentials

---

## V1 Scope

- Full rebuild — all three agents, chat UI, error handling, database, Google login (multi-user-ready structure, single user for now)
- Both chat-triggered and Monday 10am scheduled Search Agent run
- Email alerts only for Analytics Agent (WhatsApp deferred to V2)
- Categories 3-6 ranking stays as LLM judgment, not hardcoded

## Explicitly Deferred (V2+)

- WhatsApp alerts
- Auto-updating Script Agent's knowledge base from feedback (for now: Analytics Agent surfaces findings, human decides whether to update the Script Agent's voice reference)
- Charting/dashboard visuals
- Rejected topic revival, nice-to-have criteria scoring (per design-doc.md Part 9)

---

## Working Style

One focused push at a time, not a fixed schedule. Sharayu reviews product/UI decisions and is learning Python along the way, but isn't writing code directly.
