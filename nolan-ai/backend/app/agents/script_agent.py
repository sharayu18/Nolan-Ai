"""Script Generation Agent — Tasks 0-21 from script-agent-prompt.md.

Tasks 3-19 (complexity classification through audio suggestion) run as
one structured Claude call. Task 20 (reflection check) is a second call;
on failure the whole script is regenerated, up to 2 attempts total, per
the source doc's "reflection check fails twice on same section -> stop
and alert Rishi" rule (simplified here to whole-script regeneration
rather than section-level, since sections aren't independently addressable
outputs in this JSON schema).
"""
from __future__ import annotations

import json
import logging

import anthropic
from sqlalchemy.orm import Session

from app.agents.prompts.script_agent_prompt import (
    SYSTEM_PROMPT,
    build_generation_prompt,
    build_reflection_prompt,
)
from app.db.models import ErrorSeverity, MasterTopic, Script, ScriptComplexity, ScriptLanguage
from app.services.anthropic_client import call_claude
from app.services.error_logger import log_error

logger = logging.getLogger(__name__)

AGENT_NAME = "Script Generation Agent"
MAX_REFLECTION_ATTEMPTS = 2


class ScriptAgentError(RuntimeError):
    """Critical failure — caller should stop and alert Rishi."""


class ScriptGenerationAgent:
    def __init__(self, db: Session):
        self.db = db

    def generate(self, topic: MasterTopic, language: ScriptLanguage) -> Script:
        if topic is None:
            raise ScriptAgentError(
                "I don't have this topic on record — please confirm the Topic ID "
                "or paste the topic name and description."
            )

        last_notes = ""
        for attempt in range(1, MAX_REFLECTION_ATTEMPTS + 1):
            try:
                package = self._generate_package(topic, language, retry_notes=last_notes)
            except anthropic.APIError as exc:
                log_error(
                    self.db,
                    agent_name=AGENT_NAME,
                    action_name=f"Generate script — Topic {topic.topic_id}",
                    severity=ErrorSeverity.critical,
                    details=str(exc),
                )
                raise ScriptAgentError(f"Script generation failed: {exc}") from exc

            passed, notes = self._reflection_check(package)
            if passed:
                return self._write_script(topic, language, package)

            last_notes = notes
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name=f"Reflection check — Topic {topic.topic_id} (attempt {attempt})",
                severity=ErrorSeverity.low,
                details=notes,
            )

        log_error(
            self.db,
            agent_name=AGENT_NAME,
            action_name=f"Reflection check — Topic {topic.topic_id}",
            severity=ErrorSeverity.critical,
            details=f"Failed reflection check {MAX_REFLECTION_ATTEMPTS} times: {last_notes}",
        )
        raise ScriptAgentError(
            "I'm having trouble with this section. Can you describe the "
            "surprising result in your own words?"
        )

    def _generate_package(
        self, topic: MasterTopic, language: ScriptLanguage, retry_notes: str = ""
    ) -> dict:
        prompt = build_generation_prompt(
            topic.topic_title,
            topic.description,
            language.value,
            topic.pillar.value if topic.pillar else None,
        )
        if retry_notes:
            prompt += f"\n\nPrevious attempt failed reflection check: {retry_notes}\nFix this and regenerate the full script."

        response = call_claude(
            SYSTEM_PROMPT, [{"role": "user", "content": prompt}], use_web_search=False
        )
        package = _parse_json_object(response.text)
        if not package:
            raise ScriptAgentError("Script generation returned an unparseable response.")
        return package

    def _reflection_check(self, package: dict) -> tuple[bool, str]:
        prompt = build_reflection_prompt(package)
        response = call_claude(SYSTEM_PROMPT, [{"role": "user", "content": prompt}])
        result = _parse_json_object(response.text)
        if not result:
            return False, "Reflection check response unparseable."
        return bool(result.get("passed")), result.get("notes", "")

    def _write_script(self, topic: MasterTopic, language: ScriptLanguage, package: dict) -> Script:
        try:
            row = Script(
                topic_id=topic.topic_id,
                topic_title=topic.topic_title,
                language=language,
                complexity=ScriptComplexity(package["complexity"]),
                duration_seconds=int(package["duration_seconds"]),
                audio_script=package["audio_script"],
                video_script=package["video_script"],
                hook_1=package["hook_1"],
                hook_2=package["hook_2"],
                hook_3=package["hook_3"],
                caption_1=package["caption_1"],
                caption_2=package["caption_2"],
                caption_3=package["caption_3"],
                hashtags=package["hashtags"],
                text_overlay_start=package["text_overlay_start"],
                text_overlay_mid=package["text_overlay_mid"],
                audio_suggestion=package["audio_suggestion"],
                reflection_passed=True,
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except Exception as exc:  # noqa: BLE001
            self.db.rollback()
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name=f"Write script to Scripts table — Topic {topic.topic_id}",
                severity=ErrorSeverity.critical,
                details=str(exc),
            )
            raise ScriptAgentError(
                "I ran into an issue saving this script. Please check Error Management or try again shortly."
            ) from exc


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
