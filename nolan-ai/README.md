# Nolan AI

A two-agent AI content system built on [Relevance AI](https://relevanceai.com) that runs the weekly content pipeline for [@physicsexperimental](https://instagram.com/physicsexperimental) — a physics education Instagram channel — from topic discovery to a camera-ready script.

## Why "Nolan"

The channel's whole content philosophy is borrowed from Christopher Nolan's style of filmmaking: build suspense, withhold the payoff, deliver a reveal that feels *earned* rather than just informative. Every script the system produces is built around that same hook → build → twist structure.

## What it does

Each week, two agents hand off to each other:

1. **Search Engine Agent** — scans for physics topics, filters them against the channel's content criteria (audience fit, shareability, feasibility with available equipment), and hands Rishi a shortlist to pick from.
2. **Script Generation Agent** — takes a picked topic and turns it into a complete, ready-to-record package: paired audio + video script, camera settings, lighting direction, hook variations, captions, hashtags, and text overlays.

Both agents run in Relevance AI, share a Google Sheets backend as their source of truth, and are designed for a very specific real-world constraint: 30 minutes of recording time, two phones/cameras, one ring light, and 2 reels a week.

## Repo structure

```
nolan-ai/
├── agents/           # Copy-paste-ready system prompts + knowledge bases for Relevance AI
│   ├── search-agent-prompt.md
│   └── script-agent-prompt.md
├── docs/
│   ├── design-doc.md          # Full original design doc — architecture, analytics, rationale
│   ├── relevance-ai-guide.md  # How-to guide for building agents on Relevance AI
│   └── agentic-tools-guide.md # Credits, BYOK & token economics across no-code agent platforms
├── examples/         # Sample outputs from the Script Generation Agent
├── voice-reference/  # Voice/tone analysis used to keep scripts in Rishi's voice
└── tools/            # Small standalone HTML forms (setup + feedback capture)
```

## Getting started

1. Read `docs/design-doc.md` for the full context — channel analytics, the Google Sheets architecture, and why the system is built the way it is.
2. Read `docs/relevance-ai-guide.md` if you're new to Relevance AI.
3. Copy the contents of `agents/search-agent-prompt.md` and `agents/script-agent-prompt.md` into two separate agents in Relevance AI (Part 1 goes in the system prompt field, Part 2 gets uploaded as a knowledge base document).
4. Wire up a Google Sheets backend per the schema in `docs/design-doc.md` (Part 4).

## Status

Actively in use for @physicsexperimental's weekly content pipeline. Built and maintained by [Sharayu](https://github.com/) as a hands-on exploration of multi-agent system design — RAG, prompt chaining, tool use, and human-in-the-loop workflows — outside of a traditional engineering role.
