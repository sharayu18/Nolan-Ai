# Nolan AI

A three-agent AI content system for [@physicsexperimental](https://instagram.com/physicsexperimental) — a physics education Instagram channel — covering topic discovery, script generation, and post-performance analytics.

**This repo is mid-rebuild.** The original system ran on [Relevance AI](https://relevanceai.com) with a Google Sheets backend (`agents/`, `docs/design-doc.md`) — that version is preserved here for reference. It's being rebuilt as a real FastAPI + Postgres/Supabase backend (`backend/`) with a React chat frontend and Google login (`frontend/`); see `docs/HANDOFF.md` for the rebuild's full spec and status.

## Why "Nolan"

The channel's whole content philosophy is borrowed from Christopher Nolan's style of filmmaking: build suspense, withhold the payoff, deliver a reveal that feels *earned* rather than just informative. Every script the system produces is built around that same hook → build → twist structure.

## What it does

Three agents hand off to each other:

1. **Search Engine Agent** — scans for physics topics, filters them against the channel's content criteria (audience fit, shareability, feasibility with available equipment), and hands Rishi a shortlist to pick from.
2. **Script Generation Agent** — takes a picked topic and turns it into a complete, ready-to-record package: paired audio + video script, camera settings, lighting direction, hook variations, captions, hashtags, and text overlays.
3. **Analytics & Feedback Agent** — pulls per-reel Instagram performance data, flags trends (skip rate creep, underperforming categories), and logs Rishi's script feedback — informs the other two agents, doesn't act on their behalf.

Designed for a very specific real-world constraint: 30 minutes of recording time, two phones/cameras, one ring light, and 2 reels a week.

## Repo structure

```
nolan-ai/
├── backend/            # FastAPI + Postgres/Supabase rebuild — see backend/README.md
├── frontend/           # React chat UI + Google login (Supabase Auth) — see frontend/README.md
├── agents/            # Original Relevance AI system prompts + knowledge bases (reference)
│   ├── search-agent-prompt.md
│   └── script-agent-prompt.md
├── docs/
│   ├── HANDOFF.md             # Rebuild spec — architecture, all 3 agents, data model, status
│   ├── design-doc.md          # Original design doc — Relevance AI era, channel analytics, rationale
│   ├── relevance-ai-guide.md  # How-to guide for building agents on Relevance AI
│   └── agentic-tools-guide.md # Credits, BYOK & token economics across no-code agent platforms
├── examples/          # Sample outputs from the Script Generation Agent
├── voice-reference/   # Voice/tone analysis used to keep scripts in Rishi's voice
└── tools/             # Small standalone HTML forms (setup + feedback capture)
```

## Getting started

**Rebuild (current):** read `docs/HANDOFF.md` for the full spec, then `backend/README.md` and `frontend/README.md` to run both locally.

**Original Relevance AI version (reference only):**
1. Read `docs/design-doc.md` for the full context — channel analytics, the Google Sheets architecture, and why the system was built the way it was.
2. Read `docs/relevance-ai-guide.md` if you're new to Relevance AI.
3. Copy the contents of `agents/search-agent-prompt.md` and `agents/script-agent-prompt.md` into two separate agents in Relevance AI (Part 1 goes in the system prompt field, Part 2 gets uploaded as a knowledge base document).
4. Wire up a Google Sheets backend per the schema in `docs/design-doc.md` (Part 4).

## Status

Rebuild in progress — see `docs/HANDOFF.md`. Built and maintained by [Sharayu](https://github.com/) as a hands-on exploration of multi-agent system design — RAG, prompt chaining, tool use, and human-in-the-loop workflows — outside of a traditional engineering role.
