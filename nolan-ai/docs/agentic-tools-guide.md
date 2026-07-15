# AI Agent Platforms — Complete Guide 2026
## Credits, BYOK, Token Optimization & Platform Comparison

---

## PART 1 — UNDERSTANDING THE CREDIT SYSTEM

### What are Credits?

Credits are the internal currency most no-code agent 
platforms use to measure and charge for usage. Instead 
of billing you directly per LLM token or API call, 
platforms convert all costs into "credits" — a simplified 
unit that bundles compute, tool usage, and AI thinking 
into one number.

**Why platforms use credits:**
- Simpler billing — users don't need to understand 
  tokens, API rates, or compute costs
- Revenue protection — platforms markup credits over 
  actual costs
- Usage control — easier to set plan limits with 
  one unit vs multiple cost types

**The problem with credits:**
- Opaque — you often don't know the real cost behind 
  each credit
- Unpredictable — complex workflows burn credits 
  faster than simple ones
- Hidden markups — the platform pays $0.003 per 1K 
  tokens but charges you 10 credits for the same call

---

### Two Types of Costs in Every Agentic Tool

**Type 1 — Actions / Tool Credits**
Every time the agent DOES something — reads a file, 
searches the web, writes to a database, sends an email, 
calls an API. This is about what the agent executes, 
not what it thinks.

Examples:
- Read Google Sheet row = 1 Action
- Web search = 1 Action
- Send Slack message = 1 Action
- Write to database = 1 Action

**Type 2 — Vendor Credits / LLM Tokens**
Every time the LLM THINKS — reads your system prompt, 
processes context, generates a response. This is the 
actual AI cost, billed by token.

Examples:
- System prompt loaded (500 tokens) = Vendor Credits
- Web search results processed (3,000 tokens) = 
  Vendor Credits
- Script generated (1,500 tokens output) = 
  Vendor Credits

**The key insight:**
Actions = what it does
Vendor Credits = what it thinks

Both cost money. Optimising one without the other 
gives incomplete savings.

---

### How Credits Get Consumed — A Real Example

Search Engine Agent Monday run:

| Step | Type | Cost |
|---|---|---|
| Read Master Topics sheet | Action | 1 Action |
| Web search x 25 queries | Actions | 25 Actions |
| LLM reads prompt + results | Vendor Credits | ~15,000 tokens input |
| LLM generates 15 topics | Vendor Credits | ~1,500 tokens output |
| Write to Master Topics | Action | 1 Action |
| Write to Error Management | Action | 1 Action |
| **Total** | | **28 Actions + ~16,500 tokens** |

At Relevance AI Pro rates:
- 28 Actions = 28 of your 2,500/month budget
- 16,500 tokens on Sonnet 4.6 = ~$0.07
- 4 Monday runs/month = 112 Actions + $0.28

---

## PART 2 — WHAT IS BYOK AND WHY IT MATTERS

### BYOK = Bring Your Own Key

BYOK means connecting your own API key from an LLM 
provider (Anthropic, OpenAI, Google) directly to the 
agent platform, instead of using the platform's 
bundled LLM access.

**Without BYOK:**
Platform buys tokens from Anthropic → marks up the 
cost → charges you as Vendor Credits at a higher rate.

**With BYOK:**
You connect your Anthropic API key → platform calls 
the API directly on your behalf → Anthropic bills 
you directly at their published rates → platform 
only charges you for Actions (tool calls).

**Real-world impact:**

| Scenario | Monthly LLM cost |
|---|---|
| Without BYOK (Relevance AI Vendor Credits) | ~$20 included in plan |
| With BYOK (direct Anthropic billing) | ~$0.50-1.00 at actual usage |
| **Saving** | **~$19/month on LLM alone** |

The platform subscription stays the same. You just 
stop paying the platform's markup on LLM tokens.

---

### How BYOK Saves You Actions (Not Just Tokens)

This is the part most people miss.

On Gumloop specifically — without BYOK, an Advanced 
AI node costs 20 credits per call. With BYOK, the 
same node costs 1 credit. That's a 95% reduction in 
credit consumption per AI step.

Why? Because without BYOK, the platform includes 
their LLM cost inside the credit charge. With BYOK, 
the LLM cost goes to your provider directly, so the 
platform only charges the minimal execution cost.

**Gumloop example:**
- Without BYOK: 100 AI calls = 2,000 credits
- With BYOK: 100 AI calls = 100 credits
- Monthly saving: 1,900 credits (nearly 2x plan 
  allowance on Solo tier)

**Relevance AI example:**
- Without BYOK: Vendor Credits consumed on every LLM 
  call, $2 one-time on free plan
- With BYOK: Vendor Credits = $0. Only Actions consumed.
- Result: Your 2,500 monthly Actions go entirely 
  to tool execution, not LLM thinking.

---

### How to Set Up BYOK — Step by Step

**Step 1 — Get your API key**

For Anthropic (Claude):
1. Go to console.anthropic.com
2. Sign up / log in
3. Click "API Keys" in left sidebar
4. Click "+ Create Key"
5. Name it (e.g. "Relevance AI agent")
6. Copy the key — you see it only once
7. Add billing at console.anthropic.com/settings/billing
   (Pay-as-you-go, no minimum spend)

For OpenAI:
1. Go to platform.openai.com
2. Settings → API Keys → Create new key

For Google (Gemini):
1. Go to aistudio.google.com
2. Get API Key → Create API key

**Step 2 — Add key to your platform**

Relevance AI:
- Settings (bottom left) → Integrations
- Select Anthropic → paste key → Save
- In agent settings → select Claude model with 
  your key → Save

Gumloop:
- Settings → API Keys
- Add Anthropic / OpenAI key
- In workflow node → select "Use my API key"

Flowise:
- Credentials → Add Credential → ChatAnthropic
- Paste API key → Save
- In flow nodes → select saved credential

Lindy:
- Settings → Integrations → LLM Providers
- Paste key → Save (Pro/Business plan required)

---

### When BYOK Is Not Available

Not all platforms offer BYOK on all plans:

| Platform | BYOK available | Minimum plan |
|---|---|---|
| Relevance AI | Yes | Pro ($19/mo) |
| Gumloop | Yes | Solo ($37/mo) |
| Flowise | Always (self-hosted) / Cloud: yes | Starter ($35/mo) |
| Lindy | Limited | Business ($299/mo) |
| Coze | No (uses own model budget) | N/A |
| Stack AI | Yes | Starter ($49/mo) |

If BYOK isn't available — you're locked into the 
platform's LLM pricing, which is always more 
expensive than going direct.

---

## PART 3 — SAVING TOKENS AND ACTIONS

### Token Optimisation Strategies

**Strategy 1 — Prompt caching**
Anthropic supports prompt caching — static content 
(system prompt, knowledge base) cached after first 
call. Subsequent calls use cached tokens at 90% 
discount.

Impact: System prompt of 2,837 tokens loaded 4 times/
month = 11,348 tokens. With caching: only first load 
at full price, remaining 3 at 10% = saves ~$0.03/month 
(negligible at low volume, significant at scale).

Works automatically with BYOK if the platform 
supports Anthropic's caching API.

**Strategy 2 — Smaller models for simple tasks**
Not every step needs Claude Sonnet. Use model routing:
- Sheet reads, status updates, routing decisions → 
  Claude Haiku 4.5 ($1/$5 per M tokens)
- Complex reasoning, script generation → 
  Claude Sonnet 4.6 ($3/$15 per M tokens)

Impact at scale: 70% of agent steps are simple tool 
calls or routing decisions. Running those on Haiku 
instead of Sonnet = 3x cheaper per token.

**Strategy 3 — Reduce context window per call**
Every call loads: system prompt + conversation 
history + tool results. History grows with every turn.

Optimise by:
- Summarising conversation history after 5 turns 
  instead of passing full history
- Loading knowledge base on demand (RAG) not all 
  at once
- Trimming tool results to only relevant fields 
  before passing to LLM

Impact: Reducing average input from 15,000 to 8,000 
tokens per call = 47% token saving.

**Strategy 4 — Batch tool calls**
Instead of 25 separate web search calls (25 Actions), 
batch similar queries into one search session where 
possible. Some platforms allow multi-query tool calls 
that count as 1 Action.

Impact: Monday search run from 25 Actions to 5-10 
Actions = 50-80% Action saving.

**Strategy 5 — Structured outputs**
Ask the LLM to respond in JSON with only the fields 
you need. Prevents verbose outputs that consume 
extra output tokens.

Instead of: "Here are 15 topics I found for you..."
Use: {"topics": [{"id": "001", "title": "...", ...}]}

Impact: Reduces output tokens by 30-50% on structured 
tasks.

---

### Action Optimisation Strategies

**Strategy 1 — Read once, cache in context**
If the agent needs to read the same sheet multiple 
times in one session, read it once at the start and 
pass the data through as a variable instead of making 
multiple tool calls.

Impact: Reduces sheet reads from 5 per session to 1 
= saves 4 Actions per run.

**Strategy 2 — Conditional tool calls**
Don't call a tool unless the data is needed. Add a 
check step: "does this topic already exist in Master 
Topics?" — if the answer is clearly no based on 
context, skip the sheet read.

**Strategy 3 — Write all at once**
Instead of writing to sheets row by row (15 writes 
for 15 topics = 15 Actions), batch all rows into 
one write operation = 1 Action.

Impact: Monday search run from 15 write Actions to 
1 batch write = 14 Actions saved per run.

**Strategy 4 — Error handling efficiency**
Only write to Error Management when an actual error 
occurs. Don't log "success" events — that wastes 
Actions on non-errors.

---

## PART 4 — MULTI-AGENT SETUP

### What is a Multi-Agent System?

Instead of one large agent trying to do everything, 
you split the work across multiple specialised agents. 
Each agent does one job well and passes results to 
the next.

**Why multi-agent:**
- Each agent has a smaller, focused system prompt = 
  fewer tokens per call
- Agents can run in parallel = faster overall
- Easier to debug — you know which agent failed
- Easier to update — change one agent without 
  breaking others
- Each agent can use the best model for its task

**Rishi's two-agent architecture:**
```
Search Engine Agent
(runs Monday 10am, discovers topics)
        ↓
    Master Topics sheet
        ↓
Script Generation Agent
(runs on-demand, takes Topic ID → produces script)
```

These two agents are independent but share the same 
Google Sheet as a communication layer. No direct 
agent-to-agent connection needed in Phase 1.

---

### How to Connect Agents in Relevance AI

**Method 1 — Shared data layer (what Rishi uses)**
Both agents read/write the same Google Sheet. 
Agent 1 writes, Agent 2 reads. No direct connection. 
Simple, reliable, easy to debug.

Best for: Sequential workflows where timing doesn't 
matter (one runs Monday, one runs on-demand)

**Method 2 — Workforce Canvas (Relevance AI Pro)**
Visual canvas where you connect agents with arrows. 
Agent 1's output becomes Agent 2's input directly, 
passed in memory not through a sheet.

Steps:
1. Go to "Workforce" in Relevance AI left sidebar
2. Click "+ New Workforce"
3. Drag Agent 1 onto canvas
4. Drag Agent 2 onto canvas
5. Draw an arrow from Agent 1 output → Agent 2 input
6. Define what data gets passed (e.g. Topic ID + 
   description)
7. Set trigger (Agent 1 completion triggers Agent 2)
8. Save and publish

Best for: Real-time pipelines where Agent 2 should 
start immediately after Agent 1 finishes.

**Method 3 — Webhook / API handoff**
Agent 1 sends a webhook to trigger Agent 2 when done. 
More technical but most flexible — works across 
different platforms.

Best for: Cross-platform multi-agent systems (e.g. 
Relevance AI agent triggers an n8n workflow)

---

### Multi-Agent Cost Impact

Running two agents separately vs one combined agent:

| Metric | Single agent | Two agents |
|---|---|---|
| System prompt size | Large (covers both tasks) | Small per agent |
| Tokens per call | High | Lower per agent |
| Debugging complexity | Hard | Easy — isolated |
| Cost | Higher per call | Lower per call |
| Total monthly cost | Similar | Slightly lower |

The real saving isn't cost — it's reliability and 
maintainability. Two focused agents fail less and 
are easier to fix when they do fail.

---

## PART 5 — PLATFORM COMPARISON 2026

### Relevance AI

**What it is:** No-code agent builder with workforce 
management, knowledge base, and scheduling. Built for 
business automation teams.

**Credit system:**
- Actions: tool calls (reads, writes, searches)
- Vendor Credits: LLM tokens (passed through at cost)
- BYOK: Yes (Pro plan+) — eliminates Vendor Credits

**Pricing:**
- Free: 200 Actions/month, $2 Vendor Credits (once)
- Pro: $19/month, 2,500 Actions, $20 Vendor Credits
- Team: $49/month, 7,000 Actions, $70 Vendor Credits

**Key limitations:**
- Knowledge base ingestion: Pro plan only
- Scheduled triggers: Pro plan only
- BYOK: Pro plan only
- Free plan: demo use only for complex agents

**Best for:** Business workflows, scheduled automation, 
multi-step agents with tool connections. Strong Google 
Sheets integration.

**BYOK saving:** Eliminates Vendor Credits entirely. 
Monthly LLM cost drops from $20 included → $0.50-1 
direct to Anthropic.

---

### Gumloop

**What it is:** Visual drag-and-drop workflow builder 
for AI automation. Node-based canvas similar to n8n 
but with AI-first design.

**Credit system:**
- Credits per node execution
- Without BYOK: AI node = 20 credits
- With BYOK: AI node = 1 credit (95% saving)
- Tool calls: 1-5 credits depending on complexity

**Pricing:**
- Free: 60,000 credits/year (~2,000/month), 1 seat
- Solo: $37/month, 10,000 credits, BYOK available
- Team: $244/month, 60,000 credits, 10 seats

**Key strength:** BYOK gives the biggest credit 
reduction of any platform — 20x cheaper per AI call.

**Key limitations:**
- Single seat on Solo plan
- Free plan: low concurrency, testing only
- Complex workflows can exhaust credits quickly 
  without BYOK

**Best for:** AI-heavy workflows where you want 
predictable costs. Visual builders who understand 
node-based design.

**BYOK saving:** 20 credits → 1 credit per AI node. 
At 100 AI calls/month: 2,000 credits → 100 credits. 
Massive saving at scale.

---

### Flowise

**What it is:** Open-source visual LLM app builder. 
Can be self-hosted (free) or used as cloud service. 
Developer-oriented, strong RAG support.

**Credit system:**
- Cloud: billed by "predictions" (one API call = 
  one prediction)
- Self-hosted: free — you only pay your LLM provider
- BYOK: always (cloud and self-hosted, you provide 
  your own LLM keys)

**Pricing:**
- Self-hosted: Free forever (you pay hosting ~$7-10/mo 
  + your LLM API costs)
- Starter: $35/month, 5,000 predictions
- Pro: $65/month, 10,000 predictions, 5 users
- Enterprise: custom

**Key strength:** Self-hosting means near-zero platform 
cost. You only pay Anthropic/OpenAI directly.

**Key limitations:**
- Self-hosting requires some technical setup 
  (Docker, server)
- Cloud plans don't publish overage pricing
- Less polished UI than Relevance AI or Gumloop
- Better for developers than pure no-code users

**Best for:** Technically comfortable users or 
developers who want maximum control and minimum cost. 
Excellent for RAG pipelines and knowledge-base agents.

**BYOK saving:** N/A — Flowise always uses your own 
keys. Total monthly cost = hosting ($7) + LLM 
direct (e.g. $1-2 for Rishi's use case) = ~$8-9/month.

---

### Lindy

**What it is:** AI assistant platform focused on 
personal productivity and business automation via 
iMessage/SMS. Strong email, calendar, and CRM 
automation.

**Credit system:**
- Credits per task action
- Simple tasks: 1-3 credits
- Complex tasks: 5-10+ credits
- Voice calls: high credit burn
- Advanced models (GPT-4, Claude Opus): 10x credit 
  multiplier vs basic models

**Pricing:**
- Free: 400 credits/month (testing only)
- Plus: $49.99/month, 5,000 credits
- Business: $299/month, higher limits

**Key limitation:** No proper BYOK on consumer plans. 
Credit system is opaque — costs hard to predict at 
scale. Most user complaints are about unexpected 
credit depletion.

**Best for:** Personal productivity automation — 
email management, meeting notes, scheduling. Not 
ideal for custom technical agents or scheduled 
batch processing.

**BYOK saving:** Not available on consumer plans. 
You're locked into Lindy's credit pricing.

---

### Coze (ByteDance)

**What it is:** Free no-code chatbot and agent 
builder by ByteDance (TikTok's parent). Extremely 
generous free tier — access to GPT-4o, Claude, 
Gemini for free. 400+ plugins.

**Credit system:**
- Free daily token budget included
- Pro: $9.99/month for higher limits
- No separate action/vendor credit split — simpler 
  billing

**Pricing:**
- Free: Generous daily limits on top models
- Pro: $9.99/month, higher daily limits

**Key strength:** Cheapest entry point of any 
platform. Free tier includes GPT-4o access. Good 
for chatbots, content generation, simple agents.

**Key limitations:**
- No BYOK — you use Coze's model budget
- Limited scheduling/triggers
- Data stored on ByteDance servers (privacy concern 
  for some users)
- Less suited for complex multi-step business agents
- Focused on chatbot/bot use cases, not full agent 
  workflows

**Best for:** Cost-sensitive users building simple 
chatbots, content generators, or exploratory 
prototypes. Great for learning and testing.

**BYOK saving:** Not available. But platform cost is 
so low it barely matters for light use.

---

### Stack AI

**What it is:** Enterprise no-code AI workflow 
builder. Strong data pipeline support, SOC 2 
compliant, HIPAA ready.

**Credit system:**
- Credits per workflow run
- BYOK available on paid plans
- More transparent pricing than most platforms

**Pricing:**
- Free: limited runs/month
- Starter: $49/month
- Pro: $149/month
- Enterprise: custom

**Key strength:** Best compliance story (HIPAA, SOC 2) 
for regulated industries. Strong data transformation 
and multi-step pipeline support.

**Key limitations:**
- More expensive entry point than competitors
- Overkill for individual creators
- Less intuitive for non-technical users

**Best for:** Healthcare, finance, legal teams needing 
compliant AI automation. Not for individual creators 
or small teams.

---

## PART 6 — BEST PLATFORM PICK BY USE CASE

### "I just want to build and test — lowest cost"
**Winner: Coze**
Free tier includes top models. Zero setup cost. 
Good enough for prototyping any agent idea.

### "I'm a solo creator/builder, want real automation"
**Winner: Gumloop Solo ($37/mo) with BYOK**
BYOK gives 95% credit saving on AI calls. 
Visual builder is intuitive. Scheduled triggers 
included. Total real cost: $37 + ~$1 LLM = $38/mo.

### "I want no-code, professional, Google Sheets 
integration, scheduled triggers"
**Winner: Relevance AI Pro ($19/mo) with BYOK**
Best balance of ease, features, and cost at this 
tier. BYOK eliminates LLM costs. Google Sheets 
integration is best-in-class. 
Total real cost: $19 + ~$1 LLM = $20/mo.

### "I'm technical and want maximum cost control"
**Winner: Flowise self-hosted**
Platform cost: $0. LLM cost: $1-2/month direct. 
Total: ~$8-10/month including server hosting. 
Requires Docker setup — not for beginners.

### "I need compliance (HIPAA/SOC 2)"
**Winner: Stack AI**
Only platform in this list with full compliance 
story. Higher cost justified for regulated industries.

---

## PART 7 — SUMMARY TABLE

| Platform | Free tier | Cheapest paid | BYOK | Scheduled | Best for |
|---|---|---|---|---|---|
| Relevance AI | 200 Actions | $19/mo | Pro+ | Pro+ | Business agents, Sheets |
| Gumloop | 2,000 credits/mo | $37/mo | Solo+ | Yes | AI-heavy workflows |
| Flowise | Self-host free | $35/mo cloud | Always | Yes (cloud) | Developers, RAG |
| Lindy | 400 credits | $49.99/mo | No | Yes | Personal productivity |
| Coze | Very generous | $9.99/mo | No | Limited | Chatbots, prototypes |
| Stack AI | Limited | $49/mo | Yes | Yes | Enterprise/compliance |

---

## PART 8 — FOR RISHI'S AGENTS SPECIFICALLY

**Recommended setup:**
Platform: Relevance AI Pro ($19/mo)
BYOK: Anthropic API key (console.anthropic.com)
LLM: Claude Sonnet 4.6 for script generation, 
     Claude Haiku 4.5 for simple tool steps

**Monthly cost breakdown:**
- Relevance AI Pro: $19.00
- Claude API (BYOK): ~$0.50-1.00
- Google Sheets API: Free
- **Total: ~$20/month**

**Why not Gumloop:**
Gumloop is better value at scale but Relevance AI's 
Google Sheets integration and knowledge base are 
more suited to this specific use case.

**Why not Flowise:**
Self-hosting adds friction. At $20/month total, 
Relevance AI Pro is easier and nearly as cheap.

**Why not Coze:**
No scheduled triggers, limited agent workflow 
complexity, data on ByteDance servers.

