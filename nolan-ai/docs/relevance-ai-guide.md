# How to Create Agents Using Relevance AI
## A Practical Guide for No-Code Agent Building

---

## What is Relevance AI?

Relevance AI is a no-code/low-code platform for building 
AI agents that autonomously complete tasks. Unlike Make or 
Zapier which add AI to fixed workflows, Relevance AI builds 
intelligent agents that can reason, use tools, and execute 
multi-step tasks autonomously — without writing code.

Think of it as CrewAI or LangGraph but without Python.

---

## Core Building Blocks

Every agent in Relevance AI is made of 4 components:

**1. Prompt (System Prompt)**
The agent's brain — defines who it is, what it does, 
how it communicates, and what rules it follows.
This is where your role, task decomposition, output 
format, edge cases, and error handling instructions live.

**2. Tools**
Actions the agent can execute — searching the web, 
reading/writing Google Sheets, sending emails, calling 
APIs, querying databases. Each tool is one "Action" 
credit when used.

**3. Knowledge**
Documents, files, or data sources the agent can 
reference when answering. Uploaded as .md, .pdf, .txt, 
.csv, .docx, .xlsx, or synced from Google Drive, 
SharePoint, Notion, or Confluence.
Requires Pro plan for ingestion.

**4. Triggers**
What starts the agent — a user message, a scheduled 
time (e.g. Monday 10am), a webhook, or another agent 
passing it a task.
Scheduled triggers require Pro plan.

---

## Step-by-Step: Building an Agent from Scratch

### Step 1 — Create a New Agent
- Go to app.relevanceai.com
- Click "Agents" in left sidebar
- Click "+ New Agent" or use "Invent" to generate 
  one from a plain language description
- Give it a name

### Step 2 — Write the System Prompt
- Click "Prompt" in left sidebar
- Paste your system prompt in the text field
- Structure it clearly:
  - ROLE — who the agent is
  - TRIGGER CONDITIONS — when it activates
  - TASK DECOMPOSITION — numbered steps it follows
  - OUTPUT FORMAT — exactly how it responds
  - EDGE CASES — unusual situations handled
  - ERROR HANDLING — what to do when things fail
- Use {{variable_name}} syntax to reference 
  knowledge base or tool outputs inline

### Step 3 — Add Tools
- Click "Tools" in left sidebar
- Click "+ Add tool"
- Choose from built-in tools:
  - Web search
  - Google Sheets read/write
  - Send email
  - HTTP request (any API)
  - Code interpreter
  - And 2,000+ more via integrations
- For Google Sheets specifically:
  - Select Google Sheets tool
  - Connect your Google account via OAuth
  - Specify sheet URL and tab name
  - Set read or write permissions
- Each tool generates a variable you can 
  reference in your prompt

### Step 4 — Add Knowledge (Pro plan required)
- Click "Knowledge" in left sidebar
- Two options:
  A. Upload knowledge — drag and drop .md, .pdf, 
     .txt, .csv, .docx, .xlsx files (max 5 at once)
  B. Connect a source — Google Drive, SharePoint, 
     Notion, Confluence (auto-syncs)
- After upload, choose how agent uses it:
  - "Add all to prompt" — loads entire content into 
    context every call (good for small static docs)
  - "Allow agent to search" — RAG-based retrieval, 
    agent queries only what it needs (better for 
    large or growing datasets)
- Copy the variable {{_knowledge.name}} and 
  reference it in your system prompt

### Step 5 — Set Triggers
- Click "Triggers" in left sidebar
- Options:
  - Manual — agent only runs when you chat with it
  - Scheduled — set day, time, frequency 
    (requires Pro plan)
  - Webhook — triggered by external event
  - Agent trigger — another agent starts this one
- For Monday 10am schedule:
  - Select "Scheduled"
  - Set recurrence: Weekly
  - Day: Monday
  - Time: 10:00am
  - Timezone: Asia/Kolkata (IST)

### Step 6 — Configure Model
- Click "Advanced" in left sidebar
- Select LLM model:
  - Performance optimized = faster, cheaper 
    (Claude Haiku equivalent)
  - Quality optimized = smarter, slower 
    (Claude Sonnet equivalent)
- Add BYOK (Bring Your Own Key):
  - Go to Settings → Integrations
  - Select Anthropic (or OpenAI, Google)
  - Paste your API key
  - Agent now uses your key — no Vendor Credits consumed

### Step 7 — Test the Agent
- Click "Run" tab at top
- Type a test message in the chat
- Watch the agent's steps execute in real time
- Check tool calls, outputs, and sheet writes
- Iterate on the prompt if output is wrong

### Step 8 — Set Memory (optional)
- Click "Memory" in left sidebar
- Two types:
  - In-session — agent remembers within one 
    conversation only
  - Persistent — agent remembers across sessions 
    (stores key facts from past conversations)
- For most task-specific agents like Nolan AI, 
  Google Sheets serves as external memory — 
  no need to enable persistent memory

### Step 9 — Set Alerts (optional)
- Click "Alerts" in left sidebar
- Get notified when agent runs, errors, or 
  completes a task
- Useful for Monday search run — get an email 
  confirming topics were generated

### Step 10 — Save and Publish
- Click "Save" (top right) after every change
- Click "Publish" when ready to go live
- Share link with user or embed in a webpage

---

## Key Settings to Know

**Variables**
Use {{variable_name}} anywhere in your prompt to 
inject dynamic values — tool outputs, knowledge 
content, user inputs.

**Evals**
Test your agent against predefined scenarios. 
Define what a "good" output looks like, run evals, 
see pass/fail. Available under the "Evaluate" tab.
Set up before going live — not after.

**Workforce Canvas**
Connect multiple agents visually — one agent's 
output becomes another's input. Used for multi-agent 
pipelines (e.g. Search Engine Agent → Script 
Generation Agent).
Available on Pro plan and above.

---

## Plans — What You Need for What

| Feature | Free | Pro ($19/mo) |
|---|---|---|
| Build agents | ✅ | ✅ |
| Web search tool | ✅ | ✅ |
| Google Sheets tool | ✅ | ✅ |
| Manual triggers | ✅ | ✅ |
| Knowledge base ingestion | ❌ | ✅ |
| Scheduled triggers | ❌ | ✅ |
| BYOK (your own API key) | ❌ | ✅ |
| Actions/month | 200 | 2,500 |
| Workforce canvas | ❌ | ✅ |

---

## Credit System

**Actions** = every tool call the agent makes
(1 sheet read = 1 Action, 1 web search = 1 Action)

**Vendor Credits** = LLM cost passed through
(tokens consumed by the model per call)

**With BYOK** = Vendor Credits bypassed entirely,
LLM costs go directly to your Anthropic account
(roughly $0.50-1.00/month for Rishi's agents)

---

## Common Mistakes to Avoid

1. Not saving after changes — always click Save 
   before testing or leaving the page
2. Pasting knowledge as text without a knowledge 
   table — always upload as a file or use the 
   knowledge section, not inline in the prompt
3. Using "Add all to prompt" for large datasets — 
   use "Allow agent to search" for sheets/docs 
   that will grow over time
4. Forgetting to reference the knowledge variable 
   in the prompt — upload alone is not enough, 
   must add {{_knowledge.name}} to the prompt
5. Not setting IST timezone on scheduled triggers — 
   defaults to UTC, runs at wrong time in India
6. Testing without saving — run tab uses the 
   last saved version, not your unsaved edits

---

## For Rishi's Two Agents Specifically

**Search Engine Agent (Nolan AI)**
- Prompt: Part 1 of search_agent_prompt.md
- Knowledge: Upload nolan_search_knowledge_base.md
- Tools: Google Sheets (Master Topics R+W, 
  Criteria Filter Rules Read, Scripts R+W, 
  Error Management W), Web Search
- Trigger: Scheduled — Monday 10am IST
- Model: Performance optimized
- BYOK: Anthropic API key

**Script Generation Agent (Nolan AI)**
- Prompt: Part 1 of script_agent_prompt.md
- Knowledge: Upload script knowledge base file
- Tools: Web Search, YouTube Audio Library Search,
  Error Management (Write only)
- Trigger: Manual (on-demand only)
- Model: Quality optimized (heavier creative task)
- BYOK: Same Anthropic API key

