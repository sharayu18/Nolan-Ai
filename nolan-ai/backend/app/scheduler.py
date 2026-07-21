"""Cron triggers — the scheduled half of each agent's Trigger Conditions.

- Search Engine Agent: Monday 10am, full weekly search run — currently
  DISABLED (Anthropic API costs money per run; use POST /topics/run-search
  or the "Run search now" button instead until this is turned back on)
- Analytics & Feedback Agent: weekly digest just before the Monday run
  (sequencing only — the digest does not feed data into the Search
  Agent's ranking logic, per HANDOFF.md's open call to sanity-check),
  plus an hourly sweep for reels that just crossed the 48h-since-Posted
  mark
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agents.analytics_agent import AnalyticsAgentError, AnalyticsFeedbackAgent
from app.agents.search_agent import SearchAgentError, SearchEngineAgent
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)


def run_monday_search() -> None:
    db = SessionLocal()
    try:
        SearchEngineAgent(db).run_weekly_search()
    except SearchAgentError:
        logger.exception("Monday search run failed — see Error Management for details.")
    finally:
        db.close()


def run_weekly_digest() -> None:
    db = SessionLocal()
    try:
        digest = AnalyticsFeedbackAgent(db).weekly_digest()
        for flag in digest.flags:
            AnalyticsFeedbackAgent(db).send_flag_alert(flag)
    except Exception:  # noqa: BLE001 — digest failure is non-critical, log and move on
        logger.exception("Weekly digest generation failed.")
    finally:
        db.close()


def run_analytics_fetch_sweep() -> None:
    db = SessionLocal()
    try:
        AnalyticsFeedbackAgent(db).fetch_due_reels()
    except AnalyticsAgentError:
        logger.exception("Analytics fetch sweep stopped — Instagram auth issue.")
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(
        run_weekly_digest,
        CronTrigger(day_of_week="mon", hour=9, minute=45),
        id="weekly_digest",
        replace_existing=True,
    )
    # run_monday_search is intentionally not scheduled — disabled to avoid
    # unattended Anthropic API spend. Trigger it manually via
    # POST /topics/run-search (or the "Run search now" button) instead.
    scheduler.add_job(
        run_analytics_fetch_sweep,
        CronTrigger(minute=0),  # hourly — catches reels as they cross the 48h mark
        id="analytics_fetch_sweep",
        replace_existing=True,
    )
    return scheduler
