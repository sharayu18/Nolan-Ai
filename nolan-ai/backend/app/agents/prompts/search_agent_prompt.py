"""System prompt + knowledge base for the Search Engine Agent.

Ported from nolan-ai/agents/search-agent-prompt.md — "Draft complete, use
as-is" per HANDOFF.md. Category/sub-area rotation and Category 1-2's
explicit ranking are enforced in code (search_agent.py) rather than left
to the LLM, since the source doc calls those out as fixed rules. Categories
3-6 ranking is intentionally NOT hardcoded — kept as a prompted instruction
per HANDOFF.md, so the LLM judges it fresh each run.
"""

from app.db.models import TopicCategory

SYSTEM_PROMPT = """# ROLE
Name: Nolan AI — Search Engine Agent
You are a content topic discovery agent for @physicsexperimental, a
physics concepts Instagram channel run by a physics tutor with 2,500
followers. You find and describe content topic ideas. You do not write
scripts — that is a separate agent's job.

1. Communication Style — Professional. Crisp. Few words.
2. Scope — Topic discovery and filtering only. No marketing, no scripts,
   no posting strategy.
3. Pushback — Defer to Rishi on science. Push back on anything outside
   scope or scientifically unsound.
4. Unknowns — Say "I don't have enough data" not a guess.

# CHANNEL DETAILS
Handle: @physicsexperimental | Followers: ~2,500
Format: Reels, Hinglish + English
Equipment: OnePlus Nord C6, Canon XA11, ring light, tripod
Editing: VN + Instagram | Recording: 30 mins max
Posting: 2 reels/week | Prep: Rough bullet points only

# AUDIENCE INSIGHTS
- Real audience: 25-44 curious Indian adults (not students)
- 93% India, predominantly male
- Share rate 1.0-1.1% vs industry 0.3-0.5%
- Long format reels get heavily penalized
- Counterintuitive surprises outperform educational content
- Highest engagement comes from topics with clearest aha reveal

# NORTH STAR — THE NOLAN PHILOSOPHY
1. Make Rishi the Science Nolan of Instagram. Build suspense. Reveal at
   the end. (Criteria Filter rule 5)
2. Audience led to expect one thing, demonstration flips it at the very
   end. Reveal must feel earned not just informative.

# TWO CONTENT PILLARS
Pillar 1 — Misconception Corrector (student-focused): Science
generalisations that break under edge cases. Things taught as absolute
rules in school that are actually more nuanced.

Pillar 2 — Hidden Physics Revealer (general audience): Everyday object or
situation. Physics always present but never noticed. Builds suspense,
reveals the science.

Neutral fun facts with no misconception and no reveal fail Criteria
Filter rule 6.

# ASTRONOMY & QUANTUM EXCLUSION (Phase 1)
- "Why is the sky blue" -> Allowed (optics, demonstrable)
- "Why do stars twinkle" -> Excluded (hard to demo)
- "How a pinhole camera works" -> Allowed (optics)
- Telescopes, space, subatomic -> Excluded
Rule: if demonstrable with everyday object on camera -> allowed.
"""

# Sub-area ROTATION order (which sub-area gets searched this week — cycles
# weekly) is distinct from the explicit RANKING order for Categories 1-2
# (used to rank passing topics once found). Categories 3-6 have no ranking
# list here — the agent is prompted to judge priority per run.

CATEGORY_METADATA = {
    TopicCategory.academic_curriculum: {
        "label": "Academic & Curriculum",
        "sub_area_rotation": [
            "NCERT 6-8",
            "NCERT 9-10",
            "NCERT 11-12",
            "ICSE & Cambridge",
            "JEE/NEET past papers",
        ],
        "ranking": [
            "JEE/NEET past papers",
            "NCERT 11-12",
            "NCERT 9-10",
            "NCERT 6-8",
            "ICSE & Cambridge",
        ],
        "instruction": (
            "Search Indian school physics/science textbooks class 6-12. "
            "Find concepts taught as absolute truths with surprising or "
            "counterintuitive scientific reality behind them."
        ),
    },
    TopicCategory.vedic_mythological: {
        "label": "Vedic & Mythological",
        "sub_area_rotation": [
            "Rigveda",
            "Upanishads & Puranas",
            "Indian festival rituals",
            "Folk wisdom & Ayurvedic practices",
        ],
        "ranking": [
            "Rigveda",
            "Folk wisdom & Ayurvedic practices",
            "Indian festival rituals",
            "Upanishads & Puranas",
        ],
        "instruction": (
            "Search Rigveda primarily for natural phenomena with valid "
            "modern physics explanations. Also search festival rituals, "
            "Ayurvedic practices, folk wisdom rooted in real science."
        ),
    },
    TopicCategory.indian_storytelling: {
        "label": "Indian Storytelling",
        "sub_area_rotation": ["Sudha Murthy", "Ruskin Bond", "APJ Kalam", "RK Narayan"],
        "ranking": None,
        "instruction": (
            "Search these authors' work for physics moments. Sudha Murthy "
            "key books: How the Onion Got Its Layers, Daughter from a "
            "Wishing Tree, Grandma's Bag of Stories, Man from the Egg. "
            "Rank passing topics using your own judgment based on Master "
            "Topics history — no fixed priority order for this category."
        ),
    },
    TopicCategory.everyday_indian_life: {
        "label": "Everyday Indian Life",
        "sub_area_rotation": ["Kitchen", "Monsoon", "Commute", "Home", "Market"],
        "ranking": None,
        "instruction": (
            "Search everyday Indian life moments in this sub-area for "
            "hidden physics. Rank passing topics using your own judgment "
            "based on Master Topics history — no fixed priority order for "
            "this category."
        ),
    },
    TopicCategory.open_web_communities: {
        "label": "Open Web & Communities",
        "sub_area_rotation": [
            "Physics Stack Exchange",
            "Quora India",
            "Reddit",
            "Wikipedia",
            "YouTube science channel titles",
        ],
        "ranking": None,
        "instruction": (
            "Search this community/platform for physics questions or "
            "topics with strong curiosity appeal. Rank passing topics "
            "using your own judgment based on Master Topics history — no "
            "fixed priority order for this category."
        ),
    },
    TopicCategory.academic_research: {
        "label": "Academic Research",
        "sub_area_rotation": [
            "Physics misconceptions India (Google Scholar)",
            "Naive physics beliefs adults (ResearchGate)",
            "Science education gaps India",
            "Cognitive science misconceptions",
        ],
        "ranking": None,
        "instruction": (
            "Search this academic source for physics misconception "
            "research. Rank passing topics using your own judgment based "
            "on Master Topics history — no fixed priority order for this "
            "category."
        ),
    },
}

CATEGORY_ROTATION_ORDER = list(CATEGORY_METADATA.keys())

TOPICS_PER_RUN = 5

# Each web search costs real money and adds its full results to this
# request's input tokens — run a handful of well-targeted searches, not
# an exhaustive crawl. (Hard-capped in code too — see anthropic_client.py.)
MAX_SEARCHES_PER_RUN = 5


def build_search_task_prompt(category: TopicCategory, sub_area: str) -> str:
    meta = CATEGORY_METADATA[category]
    return f"""Category this week: {meta['label']}
Sub-area this week: {sub_area}

Instruction: {meta['instruction']}

Run at most {MAX_SEARCHES_PER_RUN} targeted web searches on this sub-area
— pick your queries carefully rather than searching broadly, budget is
limited. Generate up to {TOPICS_PER_RUN} candidate topics for this
sub-area only.

Respond with ONLY a JSON array, no prose, in this exact shape:
[
  {{
    "topic_title": "string",
    "description": "one line",
    "pillar": "misconception_corrector" | "hidden_physics_revealer"
  }}
]"""


def build_criteria_filter_prompt(rules: list[str], topics: list[dict]) -> str:
    numbered_rules = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(rules))
    return f"""Criteria Filter Rules (a topic must PASS every rule):
{numbered_rules}

Candidate topics (JSON):
{topics}

For each topic, decide pass/fail against every rule above. Respond with
ONLY a JSON array, no prose, in this exact shape:
[
  {{
    "topic_title": "string",
    "passes": true | false,
    "failed_rules": [1, 4]
  }}
]"""


def build_ranking_prompt(category: TopicCategory, sub_area: str, topics: list[dict]) -> str:
    meta = CATEGORY_METADATA[category]
    return f"""Category: {meta['label']} | Sub-area: {sub_area}

Passing topics (JSON):
{topics}

Rank these topics best-to-worst for this channel using your own judgment
— audience fit, shareability, clarity of the Nolan-style reveal. There is
no fixed priority order for this category; use your judgment fresh for
this run.

Respond with ONLY a JSON array of topic_title strings, best first."""
