# Nolan AI — Frontend

React (Vite + TS) chat interface for Nolan AI, talking to the FastAPI
backend in `../backend`. Google login via Supabase Auth.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # fill in Supabase project details once it exists
npm run dev
```

Without `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` set, the app skips
the login gate and runs straight into the chat/topics UI (useful for
local development against the backend before the Supabase project is
provisioned) — every backend call will then fail with the same "auth not
configured" message the backend returns until `SUPABASE_JWT_SECRET` is
also set there. See Setup Dependencies in `../docs/HANDOFF.md`.

## Structure

```
src/
├── App.tsx                # top-level shell: login gate, tabs (Chat / Topics)
├── components/
│   ├── Login.tsx            # Google sign-in button
│   ├── ChatWindow.tsx       # free-text chat, posts to backend /chat
│   └── TopicPicker.tsx      # pending-topic cards — pick / reject / generate script
└── lib/
    ├── supabaseClient.ts    # Supabase JS client
    ├── useAuth.ts           # session state + signIn/signOut
    └── api.ts                # typed fetch wrapper, attaches the Supabase access token
```

## Why a Topics panel and not just chat

Topic and Script IDs are UUIDs — fine for the backend, unusable for
someone to type in a chat box. The chat window stays close to the
original design's phrase-triggered feel ("share this week's topics",
"how is my channel doing"), while picking/rejecting a topic or
generating its script happens by clicking a card in the Topics tab,
which passes the real ID under the hood.
