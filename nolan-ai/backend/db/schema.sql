-- Nolan AI — Postgres schema (Supabase)
-- Translates the original Google Sheets tabs into explicit Postgres types.
-- Run against a Supabase project (or any Postgres 14+) to provision all 6 tables.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------

create type topic_source as enum ('agent', 'rishi');

create type topic_status as enum (
    'pending_to_pick',
    'picked',
    'rejected',
    'completed'
);

create type topic_reject_reason as enum (
    'too_complex',
    'cannot_demonstrate_at_home',
    'already_everywhere',
    'not_his_style',
    'other'
);

create type topic_category as enum (
    'academic_curriculum',
    'vedic_mythological',
    'indian_storytelling',
    'everyday_indian_life',
    'open_web_communities',
    'academic_research'
);

create type content_pillar as enum (
    'misconception_corrector',
    'hidden_physics_revealer'
);

create type script_language as enum ('hinglish', 'english');

create type script_complexity as enum ('simple', 'layered', 'deep');

create type error_severity as enum ('critical', 'medium', 'low');

create type feedback_q1 as enum (
    'yes_exactly_how_i_talk',
    'close_needs_small_fixes',
    'no_sounds_like_someone_else'
);

create type feedback_q2 as enum (
    'natural',
    'slightly_formal',
    'too_formal'
);

create type feedback_q3 as enum (
    'perfect_mix',
    'more_hindi_needed',
    'more_english_needed',
    'prefer_full_english'
);

create type feedback_q4 as enum (
    'right_length',
    'too_short',
    'too_long'
);

create type feedback_q5 as enum (
    'paired_easier_on_set',
    'separate_tracks_cleaner',
    'no_preference'
);

create type feedback_q6 as enum (
    'looks_right',
    'missing_details',
    'wrong_camera'
);

create type feedback_q7 as enum (
    'very_useful',
    'good_starting_point',
    'not_useful'
);

-- ---------------------------------------------------------------------------
-- 1. Master Topics
-- ---------------------------------------------------------------------------

create table master_topics (
    topic_id        uuid primary key default gen_random_uuid(),
    topic_title     text not null,
    category        topic_category not null,
    sub_area        text not null,
    description     text not null,
    pillar          content_pillar,
    source          topic_source not null default 'agent',
    status          topic_status not null default 'pending_to_pick',
    reason          topic_reject_reason,
    reason_notes    text,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),

    constraint reason_only_when_rejected
        check (status = 'rejected' or reason is null)
);

create index idx_master_topics_status on master_topics (status);
create index idx_master_topics_category_created on master_topics (category, created_at desc);

-- ---------------------------------------------------------------------------
-- 2. Criteria Filter Rules — Rishi-editable, read by Search Agent every run
-- ---------------------------------------------------------------------------

create table criteria_filter_rules (
    rule_id      serial primary key,
    rule_text    text not null,
    is_active    boolean not null default true,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- 3. Scripts — one row per generated script, linked to Master Topics
-- ---------------------------------------------------------------------------

create table scripts (
    script_id            uuid primary key default gen_random_uuid(),
    topic_id             uuid not null references master_topics (topic_id),
    topic_title          text not null,
    language             script_language not null,
    complexity           script_complexity not null,
    duration_seconds     integer not null,
    audio_script         text not null,
    video_script         text not null,
    hook_1               text not null,
    hook_2               text not null,
    hook_3               text not null,
    caption_1            text not null,
    caption_2            text not null,
    caption_3            text not null,
    hashtags             text not null,
    text_overlay_start   text not null,
    text_overlay_mid     text not null,
    audio_suggestion     text not null,
    reflection_passed    boolean not null default false,
    posted               boolean not null default false,
    posted_at            timestamptz,
    instagram_media_id   text,
    date_generated        timestamptz not null default now(),

    constraint posted_at_requires_posted
        check (posted_at is null or posted)
);

create index idx_scripts_topic_id on scripts (topic_id);
create index idx_scripts_posted on scripts (posted, posted_at);

-- ---------------------------------------------------------------------------
-- 4. Error Management
-- ---------------------------------------------------------------------------

create table error_management (
    error_id       bigserial primary key,
    agent_name     text not null,
    action_name    text not null,
    severity       error_severity not null,
    error_details  text not null,
    occurred_at    timestamptz not null default now()
);

create index idx_error_management_occurred_at on error_management (occurred_at desc);
create index idx_error_management_severity on error_management (severity);

-- ---------------------------------------------------------------------------
-- 5. Analytics — per-reel Instagram Graph API metrics
-- ---------------------------------------------------------------------------

create table analytics (
    reel_id           uuid primary key default gen_random_uuid(),
    topic_id          uuid not null references master_topics (topic_id),
    script_id         uuid references scripts (script_id),
    date_posted       timestamptz not null,
    views             integer,
    reach             integer,
    avg_watch_time_s  numeric(6, 2),
    completion_pct    numeric(5, 2),
    follows           integer,
    likes             integer,
    shares            integer,
    saves             integer,
    comments          integer,
    skip_rate_pct     numeric(5, 2),
    share_rate_pct    numeric(5, 2),
    like_rate_pct     numeric(5, 2),
    save_rate_pct     numeric(5, 2),
    age_breakdown     jsonb,
    gender_breakdown  jsonb,
    country_breakdown jsonb,
    partial_data      boolean not null default false,
    date_fetched      timestamptz not null default now()
);

create index idx_analytics_topic_id on analytics (topic_id);
create index idx_analytics_date_posted on analytics (date_posted desc);

-- ---------------------------------------------------------------------------
-- 6. Feedback Responses — script-validation.html submissions
-- ---------------------------------------------------------------------------

create table feedback_responses (
    response_id    uuid primary key default gen_random_uuid(),
    topic_id       uuid references master_topics (topic_id),
    script_id      uuid references scripts (script_id),
    q1_sounds_like_rishi   feedback_q1,
    q2_formality           feedback_q2,
    q3_hinglish_ratio       feedback_q3,
    q4_length               feedback_q4,
    q5_format               feedback_q5,
    q6_camera               feedback_q6,
    camera_notes            text,
    q7_supporting_outputs   feedback_q7,
    extra_notes             text,
    submitted_at            timestamptz not null default now(),
    reviewed                boolean not null default false
);

create index idx_feedback_responses_reviewed on feedback_responses (reviewed);
create index idx_feedback_responses_topic_id on feedback_responses (topic_id);
