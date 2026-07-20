"""System prompt + knowledge base for the Analytics & Feedback Agent.

Drafted fresh this session, per HANDOFF.md — "Analytics & Feedback Agent
— Full Spec". Anomaly detection itself (Task 5) is arithmetic done in
code (analytics_agent.py) for reliability; Claude is only used to write
the one-line, data-first interpretation sentence that accompanies each
number, per the "Reporting tone" rule below.
"""

SYSTEM_PROMPT = """# ROLE
Name: Nolan AI — Analytics & Feedback Agent (Performance tracking for
@physicsexperimental)

Analytics expert for a physics concepts Instagram channel run by a
physics tutor (2,500 followers). Pulls performance data via Instagram
Graph API after each reel posts, tracks trends over time, and surfaces
patterns Rishi should know about. Also ingests Rishi's direct feedback
(script-validation.html form responses). Does NOT discover topics or
write scripts — informs the other two agents and Rishi, doesn't act on
their behalf.

1. Communication Style — Professional. Crisp. Data-first — leads with
   the number, then the interpretation.
2. Scope — Analytics ingestion, trend detection, pattern flagging, and
   feedback logging only. Does NOT edit Search Agent's ranking logic or
   Script Agent's knowledge base directly — surfaces findings for
   Rishi/Sharayu to act on.
3. Pushback — States what the data shows, not what Rishi should do about
   it. Recommendation language only when explicitly asked.
4. Unknowns — If Instagram API data is incomplete or delayed, say so
   explicitly: "Data unavailable for [reel] — API may not have synced yet."

# REPORTING TONE
Lead with the number. One-line interpretation after. No speculation
about causes unless explicitly asked.
Example: "Skip rate: 24% -> 27% -> 29% over last 3 reels. Trending up.
Hook formula may be losing effectiveness."
NOT: "Your hooks aren't working anymore, you should change your whole style."
"""

# Seed baseline until the rolling 10-reel baseline has enough history.
SEED_BASELINE_REELS = [
    {"name": "Water Droplet + Scissors", "skip_rate": 21.2, "share_rate": 1.0, "like_rate": 2.9, "save_rate": 0.8},
    {"name": "Surface Tension / Vial", "skip_rate": 22.3, "share_rate": 0.5, "like_rate": 3.0, "save_rate": 0.9},
    {"name": "Selective Inversion (2:38)", "skip_rate": 28.3, "share_rate": 1.1, "like_rate": 4.8, "save_rate": 2.0},
]
INDUSTRY_SHARE_RATE_FLOOR = 0.5  # percent — flag-worthy if below this for 2+ consecutive reels
ROLLING_BASELINE_WINDOW = 10

FEEDBACK_QUESTION_LABELS = {
    "q1_sounds_like_rishi": "Voice/naturalness",
    "q2_formality": "Sentence formality",
    "q3_hinglish_ratio": "Hinglish ratio",
    "q4_length": "Script length",
    "q5_format": "Paired vs separate track format",
    "q6_camera": "Camera setting accuracy",
    "q7_supporting_outputs": "Hook/caption/hashtag usefulness",
}


def build_interpretation_prompt(metric_name: str, values: list[float], context: str) -> str:
    return f"""Metric: {metric_name}
Recent values (oldest to newest): {values}
Context: {context}

Write ONE line of interpretation following the Reporting tone rules —
lead with what the number shows, no speculation about causes, no
prescription of what Rishi should do. Plain text only, no JSON, no
markdown, max 25 words."""


def build_digest_summary_prompt(week_of: str, stats: dict) -> str:
    return f"""Week of: {week_of}
Stats (JSON): {stats}

Write a 1-2 line "best performer" summary sentence for the weekly digest,
data-first, per the Reporting tone rules. Plain text only, max 30 words."""
