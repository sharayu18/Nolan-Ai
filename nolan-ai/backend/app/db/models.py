"""SQLAlchemy models mirroring backend/db/schema.sql.

Types/enums are explicit and match the Postgres enums 1:1 — see schema.sql
for the DDL these are generated against. Column names use snake_case to
match Postgres convention rather than the original Google Sheets headers.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TopicSource(str, enum.Enum):
    agent = "agent"
    rishi = "rishi"


class TopicStatus(str, enum.Enum):
    pending_to_pick = "pending_to_pick"
    picked = "picked"
    rejected = "rejected"
    completed = "completed"


class TopicRejectReason(str, enum.Enum):
    too_complex = "too_complex"
    cannot_demonstrate_at_home = "cannot_demonstrate_at_home"
    already_everywhere = "already_everywhere"
    not_his_style = "not_his_style"
    other = "other"


class TopicCategory(str, enum.Enum):
    academic_curriculum = "academic_curriculum"
    vedic_mythological = "vedic_mythological"
    indian_storytelling = "indian_storytelling"
    everyday_indian_life = "everyday_indian_life"
    open_web_communities = "open_web_communities"
    academic_research = "academic_research"


class ContentPillar(str, enum.Enum):
    misconception_corrector = "misconception_corrector"
    hidden_physics_revealer = "hidden_physics_revealer"


class ScriptLanguage(str, enum.Enum):
    hinglish = "hinglish"
    english = "english"


class ScriptComplexity(str, enum.Enum):
    simple = "simple"
    layered = "layered"
    deep = "deep"


class ErrorSeverity(str, enum.Enum):
    critical = "critical"
    medium = "medium"
    low = "low"


class FeedbackQ1(str, enum.Enum):
    yes_exactly_how_i_talk = "yes_exactly_how_i_talk"
    close_needs_small_fixes = "close_needs_small_fixes"
    no_sounds_like_someone_else = "no_sounds_like_someone_else"


class FeedbackQ2(str, enum.Enum):
    natural = "natural"
    slightly_formal = "slightly_formal"
    too_formal = "too_formal"


class FeedbackQ3(str, enum.Enum):
    perfect_mix = "perfect_mix"
    more_hindi_needed = "more_hindi_needed"
    more_english_needed = "more_english_needed"
    prefer_full_english = "prefer_full_english"


class FeedbackQ4(str, enum.Enum):
    right_length = "right_length"
    too_short = "too_short"
    too_long = "too_long"


class FeedbackQ5(str, enum.Enum):
    paired_easier_on_set = "paired_easier_on_set"
    separate_tracks_cleaner = "separate_tracks_cleaner"
    no_preference = "no_preference"


class FeedbackQ6(str, enum.Enum):
    looks_right = "looks_right"
    missing_details = "missing_details"
    wrong_camera = "wrong_camera"


class FeedbackQ7(str, enum.Enum):
    very_useful = "very_useful"
    good_starting_point = "good_starting_point"
    not_useful = "not_useful"


def _pg_enum(python_enum: type[enum.Enum], name: str) -> PgEnum:
    return PgEnum(python_enum, name=name, create_type=False)


class MasterTopic(Base):
    __tablename__ = "master_topics"
    __table_args__ = (
        CheckConstraint(
            "status = 'rejected' OR reason IS NULL", name="reason_only_when_rejected"
        ),
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[TopicCategory] = mapped_column(
        _pg_enum(TopicCategory, "topic_category"), nullable=False
    )
    sub_area: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    pillar: Mapped[ContentPillar | None] = mapped_column(
        _pg_enum(ContentPillar, "content_pillar"), nullable=True
    )
    source: Mapped[TopicSource] = mapped_column(
        _pg_enum(TopicSource, "topic_source"), nullable=False, default=TopicSource.agent
    )
    status: Mapped[TopicStatus] = mapped_column(
        _pg_enum(TopicStatus, "topic_status"),
        nullable=False,
        default=TopicStatus.pending_to_pick,
    )
    reason: Mapped[TopicRejectReason | None] = mapped_column(
        _pg_enum(TopicRejectReason, "topic_reject_reason"), nullable=True
    )
    reason_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    scripts: Mapped[list["Script"]] = relationship(back_populates="topic")


class CriteriaFilterRule(Base):
    __tablename__ = "criteria_filter_rules"

    rule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Script(Base):
    __tablename__ = "scripts"
    __table_args__ = (
        CheckConstraint("posted_at IS NULL OR posted", name="posted_at_requires_posted"),
    )

    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("master_topics.topic_id"), nullable=False
    )
    topic_title: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[ScriptLanguage] = mapped_column(
        _pg_enum(ScriptLanguage, "script_language"), nullable=False
    )
    complexity: Mapped[ScriptComplexity] = mapped_column(
        _pg_enum(ScriptComplexity, "script_complexity"), nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_script: Mapped[str] = mapped_column(Text, nullable=False)
    video_script: Mapped[str] = mapped_column(Text, nullable=False)
    hook_1: Mapped[str] = mapped_column(Text, nullable=False)
    hook_2: Mapped[str] = mapped_column(Text, nullable=False)
    hook_3: Mapped[str] = mapped_column(Text, nullable=False)
    caption_1: Mapped[str] = mapped_column(Text, nullable=False)
    caption_2: Mapped[str] = mapped_column(Text, nullable=False)
    caption_3: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[str] = mapped_column(Text, nullable=False)
    text_overlay_start: Mapped[str] = mapped_column(Text, nullable=False)
    text_overlay_mid: Mapped[str] = mapped_column(Text, nullable=False)
    audio_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    reflection_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    posted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    instagram_media_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_generated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    topic: Mapped["MasterTopic"] = relationship(back_populates="scripts")


class ErrorManagement(Base):
    __tablename__ = "error_management"

    error_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    action_name: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[ErrorSeverity] = mapped_column(
        _pg_enum(ErrorSeverity, "error_severity"), nullable=False
    )
    error_details: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Analytics(Base):
    __tablename__ = "analytics"

    reel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("master_topics.topic_id"), nullable=False
    )
    script_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.script_id"), nullable=True
    )
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_watch_time_s: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    completion_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    follows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skip_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    share_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    like_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    save_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    age_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    gender_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    country_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    partial_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_fetched: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FeedbackResponse(Base):
    __tablename__ = "feedback_responses"

    response_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("master_topics.topic_id"), nullable=True
    )
    script_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.script_id"), nullable=True
    )
    q1_sounds_like_rishi: Mapped[FeedbackQ1 | None] = mapped_column(
        _pg_enum(FeedbackQ1, "feedback_q1"), nullable=True
    )
    q2_formality: Mapped[FeedbackQ2 | None] = mapped_column(
        _pg_enum(FeedbackQ2, "feedback_q2"), nullable=True
    )
    q3_hinglish_ratio: Mapped[FeedbackQ3 | None] = mapped_column(
        _pg_enum(FeedbackQ3, "feedback_q3"), nullable=True
    )
    q4_length: Mapped[FeedbackQ4 | None] = mapped_column(
        _pg_enum(FeedbackQ4, "feedback_q4"), nullable=True
    )
    q5_format: Mapped[FeedbackQ5 | None] = mapped_column(
        _pg_enum(FeedbackQ5, "feedback_q5"), nullable=True
    )
    q6_camera: Mapped[FeedbackQ6 | None] = mapped_column(
        _pg_enum(FeedbackQ6, "feedback_q6"), nullable=True
    )
    camera_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    q7_supporting_outputs: Mapped[FeedbackQ7 | None] = mapped_column(
        _pg_enum(FeedbackQ7, "feedback_q7"), nullable=True
    )
    extra_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
