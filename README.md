# WICARA FastAPI Backend Execution Plan

## Current Backend Quickstart

Install the backend dependencies into the active Python 3.11+ environment:

```powershell
python -m pip install -e ".[test]"
```

Create a local `.env` from the example file and adjust the database or Supabase values:

```powershell
Copy-Item .env.example .env
```

Run database migrations when PostgreSQL is available:

```powershell
alembic upgrade head
```

Seed or refresh the curriculum and question bank data used by Daily Evaluation V2:

```powershell
python -m app.modules.question_bank.seed
```

Preview the import without committing database changes:

```powershell
python -m app.modules.question_bank.seed --dry-run --strict
```

Run the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

Run tests:

```powershell
python -m pytest
```

Current implemented API surface:

- `GET /health`
- `POST /api/v1/auth/supabase`
- `POST /api/v1/auth/sign-in`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/google`
- `GET /api/v1/auth/me`
- `GET /api/v1/me`
- `GET /api/v1/me/profile`
- `PUT /api/v1/me/profile/onboarding`
- `GET /api/v1/subjects`
- `GET /api/v1/knowledge-map?subject=matematika`
- `GET /api/v1/knowledge-map/concepts/{concept_code}`
- `POST /api/v1/learning-goals`
- `GET /api/v1/learning-goals/{learning_goal_id}`
- `GET /api/v1/pretests/{learning_goal_id}`
- `POST /api/v1/pretests/{assessment_session_id}/answers`
- `POST /api/v1/pretests/{assessment_session_id}/reasoning`
- `GET /api/v1/home`
- `GET /api/v1/learning-queue`
- `GET /api/v1/tracks`
- `GET /api/v1/tracks/{track_id}/modules`
- `PATCH /api/v1/tracks/{track_id}/modules/{module_id}/state`
- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces/{workspace_id}`
- `POST /api/v1/workspaces/{workspace_id}/events`
- `GET /api/v1/daily-evaluations/today`
- `POST /api/v1/daily-evaluations/{assessment_session_id}/answers`
- `GET /api/v1/media-artifacts`
- `GET /api/v1/media-artifacts/{artifact_id}`
- `GET /api/v1/media-artifacts/{artifact_id}/status`
- `GET /api/v1/reports/weekly/latest`

## 1. Executive Summary

WICARA needs a FastAPI backend that can replace the current Flutter mock repositories first, then grow into the adaptive tutoring system described in the architecture reference. The first shippable backend supports [Implemented] auth/onboarding/pretest repository contracts and [Mocked] learning goal generation with durable records. The full adaptive system - graph traversal, mixed input diagnosis, Manim video generation, reports, and spaced review - is [Proposed] and should be introduced behind explicit service boundaries. Backend implementation must not modify `mobile/` until a later integration task asks for API-backed repositories.

First vertical slice: FastAPI skeleton, PostgreSQL connection, accounts/profile models, auth endpoints, onboarding endpoint, and tests.

## 2. Source-of-Truth Findings

| Source | Finding | Planning Impact |
|---|---|---|
| `AGENTS.md` | [Implemented] Workspace rules require current-state first, explicit labels, and no mobile edits unless requested. | Backend implementation has started; keep future changes scoped and current-state driven. |
| `TechImple_Django_Adaptive_Canvas_v6_unified_input.md` | [Proposed] Detailed backend architecture now targets FastAPI, SQLAlchemy/Alembic, unified `InputEvent`, mastery, graph, sessions, Manim/TTS/FFmpeg, Celery, Redis. | Use as advanced architecture reference, not as proof of current implementation. |
| `techdoc.md` | [Inferred] Mobile-aligned API contracts and DB models exist for auth, onboarding, pretest, home, queue, workspace, canvas, media, reports, knowledge map. | Use these contracts as the first API shape. |
| `plan.md` | [Historical] `mobile/` started as the latest mock product with mock repos and local state. | Replace mock-backed flows incrementally; backend now exists for auth/profile and curriculum map APIs. |
| `backend-plan-prompt.md` | [Proposed] Planning prompt now points to `appPlan.md` and FastAPI. | Future implementation agents should start from this file. |
| `mobile/lib/main.dart` | [Implemented] `WicaraApp` receives `MockAuthRepository`, `MockOnboardingRepository`, `MockPretestRepository`. | Only these three contracts are immediately swappable. |
| `mobile/lib/src/app/app_routes.dart` | [Implemented] Routes: `/`, `/auth/sign-in`, `/onboarding`, `/learning-goal`, `/pretest`, `/home`, `/workspace-modules`. | API groups must support this product journey. |
| `mobile/lib/src/features/**/domain` | [Implemented] Domain contracts exist only for auth, onboarding, pretest. | Other APIs are inferred from UI state. |
| `mobile/lib/src/features/home/presentation/app_home_page.dart` | [Mocked] Home, queue, gallery, daily evaluation, reports, profile, knowledge map are local UI/state. | Backend can expose APIs, but mobile clients do not exist yet. |
| `mobile/lib/src/features/workspace/presentation/workspace_modules_page.dart` | [Mocked] Chat, explanation, quiz, video generation, canvas sent events are local state. | Workspace backend should be event-driven before AI generation. |
| `mobile/lib/src/features/pretest/presentation/widgets/fishbone_canvas.dart` | [Implemented] Canvas captures local strokes, shapes, eraser, attachment flag, grid, zoom/pan, save version, send version. | Backend should not persist stroke history; when the learner sends canvas work, mobile exports it as an image attachment for chatbot/evaluation. |

## 3. Backend Scope and Non-Scope

### In Scope

| Item | Label | Scope |
|---|---|---|
| FastAPI backend skeleton | Proposed | `app/main.py`, routers, settings, DB session, Alembic, tests. |
| Auth and account session | Inferred | Password sign-in and Google sign-in contract compatible with Flutter. |
| Learner profile/onboarding | Inferred | Persist current `OnboardingProfile` fields and selected subjects. |
| Learning goals and pretest bootstrap | Inferred | Store raw topic, create initial pretest session, return status. |
| Assessment attempts | Inferred | Store MC answer, confidence, reasoning, optional image evidence reference, evaluation result. |
| Unified `InputEvent` | Proposed | Canonical event table for text, MC answer, image evidence, and mixed input. |
| Canvas image attachment | Inferred/Proposed | Mobile keeps canvas editing local; backend receives only exported image evidence when the user sends it. |
| Home/queue/track read APIs | Inferred | Return data currently hardcoded in UI. |
| Media artifact job model | Proposed | Queue/status rows before real Manim rendering. |
| Knowledge graph and mastery | Proposed | PostgreSQL adjacency list plus learner state. |
| Reports and streaks | Inferred | Derived from persisted activity, not manually entered. |

### Non-Scope

| Item | Label | Reason |
|---|---|---|
| Mobile implementation edits | Implemented rule | User asked not to modify `mobile/` for planning. |
| Full unrestricted chatbot | Proposed non-goal | Session router must keep learning context and create sub-sessions when needed. |
| Full LMS/admin product | Proposed non-goal | WICARA is a learning engine, not a school management suite. |
| Production OAuth launch | Deferred | Google endpoint can validate ID tokens later; MVP can use a controlled stub. |
| Real Manim rendering in Milestone 1 | Deferred | First ship durable job records and status API. |

### Deferred

| Item | Label | First Dependency |
|---|---|---|
| OCR and symbolic image parser | Proposed | Image evidence and input events exist. |
| Gemini grading and tutor response | Proposed | Assessment attempts and service interfaces exist. |
| SSE/WebSocket streaming | Proposed | REST endpoints and job status lifecycle exist. |
| Cross-subject graph unlock | Proposed | Single-subject graph and mastery state work. |
| Real TTS/FFmpeg media pipeline | Proposed | Media artifact and render job model exists. |

## 4. Proposed Backend Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Async-friendly API framework, OpenAPI by default, good Pydantic integration. |
| API | REST first, optional SSE/WebSocket later | Current mobile contracts are request/response; streaming is only needed for tutor/media progress. |
| ORM | SQLAlchemy 2.x | Explicit relational model, PostgreSQL support, testable repositories. |
| Migrations | Alembic | Versioned DB migration workflow for SQLAlchemy. |
| Schemas | Pydantic v2 | Request/response validation and generated OpenAPI schema. |
| Database | PostgreSQL | Stores accounts, profiles, assessments, graph, mastery, image/media references, reports. |
| Auth | JWT access token initially | Matches current mobile `token` field and keeps client swap simple. |
| Async jobs | Celery + Redis | Durable workers for OCR, AI grading, Manim, TTS, FFmpeg, reports. |
| Cache/session | Redis | Job status cache, rate limits, LLM/media cache, short-lived session data. |
| Media storage | object storage abstraction | Local filesystem in dev, S3-compatible store later. |
| AI integration | Gemini, Google Vision/Tesseract, Google TTS, Manim, FFmpeg | Proposed engines from architecture reference. |
| Observability | `/health`, structured logs, job status, metrics hooks | Required for debugging async media and AI workflows. |

## 5. Planned Backend Directory Structure

The repository already contains the current FastAPI skeleton, account/profile module, curriculum module, migrations, and tests. The structure below is the target shape for future milestones; some modules listed here are still planned.

```text
backend/
  pyproject.toml
  alembic.ini
  README.md
  app/
    main.py
    api/
      v1/
        router.py
        auth.py
        onboarding.py
        learning_goals.py
        pretests.py
        home.py
        workspaces.py
        media.py
        reports.py
    core/
      config.py
      security.py
      celery_app.py
      errors.py
      logging.py
    db/
      base.py
      session.py
      migrations/
    modules/
      accounts/
      curriculum/
      graph/
      mastery/
      sessions/
      inputs/
      assessments/
      explanations/
      media/
      reports/
      observability/
  tests/
    api/
    services/
    contracts/
```

| Path | Responsibility | First Files |
|---|---|---|
| `backend/app/main.py` | FastAPI application factory and router include. | `main.py` |
| `backend/app/api/v1/` | HTTP route modules grouped by mobile feature area. | `router.py`, `auth.py`, `onboarding.py`, `pretests.py` |
| `backend/app/core/` | Settings, security, error envelope, Celery app, logging. | `config.py`, `security.py`, `errors.py`, `celery_app.py` |
| `backend/app/db/` | SQLAlchemy base/session and Alembic integration. | `base.py`, `session.py` |
| `backend/app/modules/accounts/` | User accounts, auth service, profile service. | `models.py`, `schemas.py`, `service.py`, `repository.py` |
| `backend/app/modules/assessments/` | Pretest/daily/quiz sessions and attempts. | `models.py`, `schemas.py`, `service.py` |
| `backend/app/modules/inputs/` | Unified evidence pipeline for text, answers, and image-backed canvas evidence. | `models.py`, `schemas.py`, `service.py` |
| `backend/tests/` | API, service, migration, contract tests. | `test_health.py`, `test_auth_api.py` |

## 6. Domain Modules

| Module | Purpose | Owned Tables | Primary Endpoints | Service Responsibilities | Dependencies | TechImple Alignment | First Milestone |
|---|---|---|---|---|---|---|---|
| Accounts | Identity and token sessions. | `user_accounts`, optional `auth_sessions` | `POST /api/v1/auth/sign-in`, `POST /api/v1/auth/google`, `GET /api/v1/me` | Validate credentials, create user/session DTO, issue token. | DB, security config. | TechImple had student profile foundation; FastAPI implementation uses JWT and Pydantic. | M1 |
| Curriculum/Profile | Learner profile and subject selection. | `learner_profiles`, `subjects`, `learner_subjects` | `GET /api/v1/subjects`, `PUT /api/v1/me/profile/onboarding` | Save profile, bind selected subjects, mark onboarding complete. | Accounts. | Aligns with onboarding phase and curriculum binding. | M1-M2 |
| Learning Sessions and Tracks | Convert goals into tracks/modules and sessions. | `learning_goals`, `learning_tracks`, `track_modules`, `learning_sessions` | `POST /api/v1/learning-goals`, `GET /api/v1/tracks`, `GET /api/v1/tracks/{id}/modules` | Store raw topic, create pretest session, create initial track/module records. | Curriculum, graph, mastery. | Aligns with parent/child sessions and path engine. | M2-M5 |
| Unified Inputs | Canonical evidence abstraction. | `input_events` | `POST /api/v1/workspaces/{id}/events`, future `POST /api/v1/sessions/{id}/input` | Normalize text, MC, image evidence, and mixed input into event records. | Sessions, assessments, image assets. | Directly implements `InputEvent` contract. | M3-M6 |
| Canvas image evidence | Treat canvas as a mobile-local drawing surface that exports an image when sent. | optional `image_assets` later | `POST /api/v1/workspaces/{id}/events` with `image_asset_id` or image metadata | Link exported images to workspace/input events; do not persist stroke batches or versioned canvas history. | Inputs, media storage. | Implements image-backed canvas evidence without backend canvas state. | M6 |
| Assessments/Pretest | Adaptive and formative assessment storage. | `assessment_sessions`, `assessment_questions`, `assessment_options`, `assessment_attempts` | `GET /api/v1/pretests/{goal_id}`, `POST /api/v1/pretests/{session_id}/answers`, `POST /api/v1/pretests/{session_id}/reasoning` | Create sessions/questions, persist answer/reasoning, return KnowledgeState-compatible result. | Accounts, goals, mastery, inputs. | Aligns with KST-inspired assessment and mixed answer modes. | M3-M4 |
| Knowledge Graph | Subject concepts and prerequisites. | `knowledge_concepts`, `concept_edges` | `GET /api/v1/knowledge-map?subject=math` | Seed graph nodes/edges, expose learner-specific graph DTO. | Curriculum, mastery. | Uses Postgres adjacency list first; Neo4j later only if needed. | M8 |
| Mastery | Learner-specific concept state. | `learner_concept_states` | Internal first; exposed via home/map/report APIs. | Update mastery, confidence, review dates, readiness status. | Assessments, graph, inputs. | Aligns with mastery formula and graph propagation. | M4-M8 |
| Explanations | Tutor response generation. | `explanation_requests` optional later, prompt versions | `POST /api/v1/workspaces/{id}/events` response; future stream endpoint | Generate text response, classify intent, decide inline vs sub-session. | Inputs, sessions, AI. | Aligns with session router and localized explanation engine. | Deferred after M6 |
| Media/Manim Video | Generated video artifacts and render jobs. | `media_artifacts`, `manim_render_jobs` | `POST /api/v1/workspaces/{id}/generate-video`, `GET /api/v1/media-artifacts`, `GET /api/v1/media-artifacts/{id}` | Create artifact/job, track lifecycle, store URLs/transcript/notes/errors. | Sessions, object storage, Celery. | Aligns with Manim/TTS/FFmpeg pipeline. | M7 |
| Reports/Streaks | Learning reports and activity streaks. | `learning_reports`, `streak_ledgers` | `GET /api/v1/reports/weekly/latest`, `GET /api/v1/daily-evaluations/today` | Aggregate attempts/events, build weekly summaries, calculate streaks. | Assessments, mastery, sessions. | Aligns with forgetting curve and report engine. | M9 |
| Observability | Runtime and job health. | optional `job_logs`, metrics backend later | `GET /api/v1/health`, `GET /api/v1/health/jobs` | Check FastAPI, DB, Redis, Celery, media, AI provider status. | All infra. | Aligns with explicit health checks. | M1, expanded later |

## 7. Database Model Plan

| Order | Table | Purpose | Depends On | MVP Fields |
|---|---|---|---|---|
| 1 | `user_accounts` | Identity, role, provider. | none | `id`, `email`, `phone`, `password_hash`, `auth_provider`, `provider_subject`, `role`, `display_name`, `status`, timestamps |
| 2 | `learner_profiles` | Onboarding profile. | `user_accounts` | `id`, `user_id`, `full_name`, `country_name`, `grade_level`, `preferred_language`, `study_goal`, `daily_study_time_label`, `onboarding_completed_at` |
| 3 | `subjects` | Available subject catalog. | none | `id`, `code`, `name`, `is_active` |
| 4 | `learner_subjects` | Learner selected subjects. | `user_accounts`, `subjects` | `id`, `user_id`, `subject_id`, `created_at` |
| 5 | `knowledge_concepts` | Graph nodes. | `subjects` | `id`, `subject_id`, `code`, `title`, `description`, `grade_band`, `metadata` |
| 6 | `concept_edges` | Prerequisite/cross-topic edges. | `knowledge_concepts` | `id`, `from_concept_id`, `to_concept_id`, `edge_type`, `weight` |
| 7 | `learner_concept_states` | Per-learner mastery state. | `user_accounts`, `knowledge_concepts` | `id`, `user_id`, `concept_id`, `status`, `mastery_score`, `confidence_score`, `last_evaluated_at`, `next_review_at`, `evidence_count` |
| 8 | `learning_goals` | Raw topic request. | `user_accounts`, `subjects` | `id`, `user_id`, `raw_topic`, `normalized_topic`, `subject_id`, `status`, timestamps |
| 9 | `learning_tracks` | Personalized path. | `user_accounts`, `learning_goals` | `id`, `user_id`, `learning_goal_id`, `title`, `subtitle`, `status`, `progress_percent`, `current_module_id` |
| 10 | `track_modules` | Track units. | `learning_tracks`, `knowledge_concepts` | `id`, `track_id`, `concept_id`, `title`, `description`, `estimated_minutes`, `difficulty_label`, `sort_order`, `status` |
| 11 | `learning_sessions` | Parent/child learning or assessment sessions. | `user_accounts`, `track_modules`, `knowledge_concepts` | `id`, `user_id`, `parent_session_id`, `track_id`, `module_id`, `target_concept_id`, `session_type`, `status`, `current_stage`, `context_json` |
| 12 | `assessment_sessions` | Pretest/daily/quiz grouping. | `user_accounts`, `learning_tracks`, `track_modules` | `id`, `user_id`, `track_id`, `module_id`, `learning_goal_id`, `session_type`, `status`, `title`, timestamps |
| 13 | `assessment_questions` | Question definitions. | `assessment_sessions`, `knowledge_concepts` | `id`, `session_id`, `concept_id`, `step_label`, `topic`, `prompt`, `helper_text`, `difficulty_label`, `sort_order`, `metadata` |
| 14 | `assessment_options` | MC options. | `assessment_questions` | `id`, `question_id`, `option_key`, `label`, `text`, `is_correct`, `sort_order` |
| 15 | `image_assets` | Exported images from canvas/uploads when evidence needs durable storage. | `user_accounts` | `id`, `user_id`, `source`, `mime_type`, `storage_url`, `width`, `height`, `metadata`, `created_at` |
| 16 | `input_events` | Canonical evidence. | `learning_sessions`, `assessment_sessions`, `image_assets` | `id`, `user_id`, `learning_session_id`, `assessment_session_id`, `parent_session_id`, `concept_id`, `event_type`, `text_payload`, `selected_option_id`, `image_asset_id`, `raw_payload`, `parsed_problem`, `parsed_work`, `confidence`, `created_at` |
| 17 | `assessment_attempts` | Learner answer and evaluation. | `assessment_sessions`, `assessment_questions`, `assessment_options`, `image_assets`, `input_events` | `id`, `session_id`, `question_id`, `selected_option_id`, `confidence`, `explanation_text`, `used_canvas`, `image_asset_id`, `input_event_id`, `score`, `evaluated_result`, `submitted_at` |
| 18 | `workspace_sessions` | Active module workspace. | `user_accounts`, `learning_tracks`, `track_modules` | `id`, `user_id`, `track_id`, `module_id`, `current_topic`, `content_mode`, `status`, timestamps |
| 19 | `workspace_events` | Chat/canvas-image/quiz/media timeline. | `workspace_sessions`, `image_assets`, `media_artifacts` | `id`, `workspace_session_id`, `event_index`, `event_type`, `actor_type`, `text_payload`, `image_asset_id`, `media_artifact_id`, `metadata`, `created_at` |
| 20 | `media_artifacts` | Generated media visible in workspace/gallery. | `user_accounts`, `workspace_sessions`, `learning_tracks`, `track_modules`, `knowledge_concepts` | `id`, `user_id`, `workspace_session_id`, `track_id`, `module_id`, `concept_id`, `artifact_type`, `title`, `subtitle`, `duration_seconds`, `status`, `storage_url`, `thumbnail_url`, `transcript_text`, `note_markdown`, `generation_payload`, timestamps |
| 21 | `manim_render_jobs` | Dedicated video render/debug record. | `media_artifacts` | `id`, `artifact_id`, `source_session_id`, `source_module_id`, `source_concept_id`, `scene_template`, `scene_spec_json`, `render_params_json`, `status`, `language`, `voice`, `script_text`, `transcript_text`, `subtitle_url`, `manim_output_url`, `merged_video_url`, `compressed_video_url`, `thumbnail_url`, `duration_seconds`, `ffmpeg_metadata_json`, `error_detail`, `retry_count`, timestamps |
| 22 | `learning_reports` | Weekly/periodic aggregation. | `user_accounts` | `id`, `user_id`, `period_start`, `period_end`, `report_type`, `summary_json`, `created_at` |
| 23 | `streak_ledgers` | Daily activity ledger. | `user_accounts` | `id`, `user_id`, `activity_date`, `activity_type`, `created_at` |

## 8. API Contract Plan

### Auth APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| POST | `/api/v1/auth/sign-in` | Replace `AuthRepository.signIn`. | `email_or_phone`, `password`, `role` | `user_id`, `display_name`, `role`, `token` |
| POST | `/api/v1/auth/google` | Replace `signInWithGoogle`. | `id_token`, `role` | same session DTO |
| GET | `/api/v1/me` | Fetch current account/profile. | Bearer token | account + profile summary |

### Onboarding/Profile APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| GET | `/api/v1/subjects` | Populate selectable subjects later. | none | subject list |
| PUT | `/api/v1/me/profile/onboarding` | Replace `OnboardingRepository.saveProfile`. | `full_name`, `country`, `grade_level`, `preferred_language`, `selected_subjects`, `study_goal`, `daily_study_time` | profile summary, `onboarding_completed=true` |

### Learning Goal APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| POST | `/api/v1/learning-goals` | Replace local generate-pretest delay. | `raw_topic` | `learning_goal_id`, `status`, `subject`, `pretest_session_id` |
| GET | `/api/v1/learning-goals/{id}` | Poll goal/pretest state. | none | goal status and pretest link |

### Pretest APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| GET | `/api/v1/pretests/{learning_goal_id}` | Return pretest session and questions. | none | `session_id`, question list |
| POST | `/api/v1/pretests/{session_id}/answers` | Replace `submitAnswer`. | `question_id`, `option_id`, `confidence` | accepted attempt ID |
| POST | `/api/v1/pretests/{session_id}/reasoning` | Replace `submitReasoning`. | `question_id`, `option_id`, `confidence`, `explanation`, `used_canvas`, `image_asset_id` | `KnowledgeState` DTO: `skill`, `gap_label`, `message`, `path_title`, `path_meta`, `path_description` |

### Home and Queue APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| GET | `/api/v1/home` | Replace hardcoded dashboard. | none | display name, streak, next queue item, daily evaluation summary, active tracks |
| GET | `/api/v1/tracks` | Replace tracks tab. | filters optional | track list |
| GET | `/api/v1/tracks/{track_id}/modules` | Replace queue/module cards. | none | ordered modules with status and metadata |
| GET | `/api/v1/daily-evaluations/today` | Replace daily eval local questions. | none | assessment session and questions |
| POST | `/api/v1/daily-evaluations/{session_id}/answers` | Submit daily evaluation. | question answer payload | evaluation result and updated review state |

### Workspace, Unified Input, and Canvas Image APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| POST | `/api/v1/workspaces` | Create/resume module workspace. | `track_id`, `module_id` | workspace state and timeline |
| GET | `/api/v1/workspaces/{workspace_id}` | Load active timeline. | none | topic, events, last sent image, latest media |
| POST | `/api/v1/workspaces/{workspace_id}/events` | Submit text/quiz/canvas-image/media event. | `event_type`, actor, text/media payload, optional `image_asset_id` | event + optional tutor response |
| POST | `/api/v1/assets/images` | Optional future upload for exported canvas image evidence. | image file or signed-upload metadata | `image_asset_id`, storage metadata |

### Media/Gallery/Manim APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| POST | `/api/v1/workspaces/{workspace_id}/generate-video` | Queue generated video. | `module_id`, `concept_id`, `mode`, `language` | `artifact_id`, `job_id`, `status=queued` |
| GET | `/api/v1/media-artifacts` | Replace gallery tab. | filters optional | artifact cards |
| GET | `/api/v1/media-artifacts/{artifact_id}` | Video detail. | none | playable URLs, transcript, notes, job status |
| GET | `/api/v1/media-artifacts/{artifact_id}/status` | Poll render status. | none | status, progress, error if failed |

### Report and Knowledge Map APIs

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| GET | `/api/v1/reports/weekly/latest` | Replace learning report screen. | none | report metrics, trends, notes |
| GET | `/api/v1/knowledge-map` | Replace map UI data. | `subject=math` | nodes, edges, learner statuses |
| GET | `/api/v1/streaks/current` | Optional focused streak endpoint. | none | current streak, ledger summary |

## 9. Service Layer Plan

| Service | Responsibility | Inputs | Outputs | Initial Mock Strategy |
|---|---|---|---|---|
| `AuthService` | Authenticate, create account session, issue JWT. | sign-in DTO, Google token DTO | `AuthSession` DTO | Password accepts seeded/test user; Google validates later. |
| `ProfileService` | Save onboarding profile and subjects. | profile DTO | profile summary | Real DB writes from M1. |
| `LearningGoalService` | Store topic and bootstrap pretest. | raw topic, user | goal + pretest session | Rule-based subject guess, fixed first question. |
| `PretestService` | Create pretest, persist answer/reasoning, return KnowledgeState. | answers, reasoning, optional image ref | attempt, KnowledgeState | Deterministic evaluator first, AI later. |
| `SessionRouterService` | Decide next action for workspace input. | latest `InputEvent`, active session | route decision | Echo/choice-based response first. |
| `InputEventService` | Normalize evidence into canonical event. | text, MC, image, mixed payload | `input_event_id` | Store raw/parsed payload with no AI parse initially. |
| `ImageAssetService` | Store or reference exported images from canvas/uploads. | image file or upload metadata | `image_asset_id` | Local/object-storage reference only; no canvas stroke history. |
| `MasteryService` | Update learner concept state. | attempts, parser output | status/mastery update | Fixed rule mapping for first pretest. |
| `PathEngineService` | Build next modules/queue. | goal, graph, mastery | track/modules | Seeded Calculus path first. |
| `ExplanationService` | Generate tutor text and explanation artifacts. | input event, context | response text, prompt metadata | Static templates until Gemini integration. |
| `ManimMediaService` | Create media artifact and render job. | workspace/module/concept/language | artifact/job status | Queue job row; worker can mark mock `READY`. |
| `ReportService` | Build weekly report and streak summary. | events, attempts, mastery | report DTO | Aggregate deterministic DB data. |
| `ObservabilityService` | Health checks and job diagnostics. | infra clients | status payload | Real DB/Redis checks when configured. |

## 10. Async Jobs and Media Pipeline

| Job | Trigger | Input | Output | MVP Behavior | Future Behavior |
|---|---|---|---|---|---|
| `GeneratePretestJob` | `POST /learning-goals` | user, goal, subject | assessment session/questions | Create deterministic seeded questions synchronously or eager Celery. | Adaptive KST question selection. |
| `ParseImageEvidenceJob` | canvas image sent | image asset ID | parser output JSON | Mark unparsed and keep image reference only. | OCR/math symbol parsing, partial-work detection from image. |
| `GradeAssessmentJob` | answer/reasoning submitted | attempt/input event | score + KnowledgeState | Rule-based answer check. | Gemini/rubric mixed-input grading. |
| `GenerateExplanationJob` | workspace text or explanation choice | session context | tutor response | Static response template. | Gemini localized explanation and analogy. |
| `GenerateManimVideoJob` | generate-video endpoint | artifact/job scene spec | raw Manim MP4 URL | Create job and optional fake ready artifact in dev. | Render Manim scene with parameters. |
| `MergeVoiceoverJob` | Manim render complete | raw video, script, voice | merged video URL | Not run in MVP. | TTS generation and FFmpeg merge. |
| `CompressVideoJob` | merged video complete | video URL, target profile | compressed URL + metadata | Not run in MVP. | Low-bandwidth profiles and thumbnails. |
| `BuildReportJob` | weekly schedule or request | events, attempts, mastery | `learning_reports` row | On-demand deterministic aggregation. | Scheduled report generation with recommendations. |

## 11. Mobile Integration Strategy

| Mobile Contract | Current Mock | Backend Replacement | Notes |
|---|---|---|---|
| `AuthRepository.signIn` | `MockAuthRepository` | `POST /api/v1/auth/sign-in` | Response must keep `userId`, `displayName`, `role`, `token`. |
| `AuthRepository.signInWithGoogle` | `MockAuthRepository` | `POST /api/v1/auth/google` | MVP can return same DTO; real token verification later. |
| `OnboardingRepository.saveProfile` | `MockOnboardingRepository` | `PUT /api/v1/me/profile/onboarding` | Must persist full current `OnboardingProfile`. |
| `LearningGoalPage._generatePretest` | Local delay | `POST /api/v1/learning-goals` then route to pretest | No repo exists yet; add later only when mobile integration is requested. |
| `PretestRepository.submitAnswer` | `MockPretestRepository` | `POST /api/v1/pretests/{session_id}/answers` | Current mobile hardcodes question ID; backend should tolerate client IDs or map them. |
| `PretestRepository.submitReasoning` | `MockPretestRepository` | `POST /api/v1/pretests/{session_id}/reasoning` | Return `KnowledgeState` with exact fields expected by Flutter. |
| Home/queue/report/map | Local UI state | home/tracks/reports/map APIs | Add API clients later after backend stable. |
| Workspace chat/canvas/video | Local UI state | workspace/events/image/media APIs | Canvas editing remains local; sent canvas work is exported as an image event. |

DTO strategy: backend JSON uses snake_case; Flutter API repositories can map to Dart camelCase/domain models. Error format should be stable:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Please complete your profile.",
    "details": {}
  }
}
```

Session storage expectation: mobile currently has no persisted session layer. Backend should return JWT now; later mobile adds secure storage and attaches `Authorization: Bearer <token>`.

Backward-compatible replacement plan: implement `ApiAuthRepository`, then `ApiOnboardingRepository`, then `ApiPretestRepository`; keep mock repositories selectable during development.

## 12. Implementation Milestones

| Milestone | Deliverables | Acceptance Criteria | Tests | Files Likely Created | Exit Condition |
|---|---|---|---|---|---|
| M1: FastAPI skeleton + accounts/profile | FastAPI app, settings, DB session, Alembic baseline, `user_accounts`, `learner_profiles`, auth/profile endpoints. | `/health`, sign-in, onboarding pass tests; no mobile edits. | `pytest tests/api/test_health.py tests/api/test_auth.py tests/api/test_onboarding.py` | `backend/app/main.py`, `core/*`, `db/*`, `modules/accounts/*` | Current auth/onboarding contracts can be served by API. |
| M2: Subjects/curriculum seed + learning goal | `subjects`, `learner_subjects`, `learning_goals`, seed command/script, goal endpoint. | Goal returns `pretest_ready` or `pretest_pending` with pretest session ID. | API tests plus seed idempotency test. | `modules/curriculum/*`, `modules/sessions/*` | Topic creation can replace local generate delay. |
| M3: Pretest sessions/questions/answers | Assessment models and pretest read/answer endpoints. | `GET /pretests/{goal_id}` returns current mobile-shaped question; answer submit persists attempt. | Contract tests for `PretestQuestion` and `PretestAnswer`. | `modules/assessments/*` | `submitAnswer` can be API-backed. |
| M4: Reasoning + KnowledgeState mock | Reasoning endpoint, deterministic evaluator, initial mastery row updates, track bootstrap. | Returns exact `KnowledgeState` fields and creates first track/modules. | API/service tests for correct DTO and DB writes. | `modules/mastery/*`, `modules/graph/*` partial | `submitReasoning` can be API-backed. |
| M5: Home/tracks summary | Home, tracks, modules APIs from persisted records. | Dashboard/queue data no longer needs hardcoded server assumptions. | API tests for `/home`, `/tracks`, `/tracks/{id}/modules`. | `api/v1/home.py`, sessions services | Home UI has a backend contract. |
| M6: Workspace events + image-backed canvas evidence | Workspace session, events, input events, optional image assets. | Text, quiz, and sent canvas images create `input_events` and `workspace_events`; no stroke/history persistence. | API + serializer tests for workspace/image event DTO. | `modules/inputs/*`, workspace APIs | Workspace timeline is durable and canvas evidence is image-based. |
| M7: Media artifacts + Manim job model | `media_artifacts`, `manim_render_jobs`, generate-video/status/gallery APIs. | Request creates artifact/job with inspectable status and error fields. | Job model and API tests. | `modules/media/*`, Celery app config | Video UI can poll artifact status. |
| M8: Knowledge graph + mastery state | Graph seed, map API, learner states. | Math graph returns nodes/edges/statuses like current UI. | Graph service tests, map API tests. | `modules/graph/*`, `modules/mastery/*` | Knowledge map backed by DB. |
| M9: Reports/streaks + daily evaluation | Daily eval generation/submission, weekly report, streak ledger. | Daily answer updates attempt/mastery/streak; weekly report returns metrics. | Service/API aggregation tests. | `modules/reports/*` | Progress tab has backend data. |

## 13. Test and Verification Plan

| Layer | Test Type | Command | Acceptance |
|---|---|---|---|
| Models | unit/migration | `pytest backend/tests/models` and `alembic upgrade head` | All tables create cleanly; constraints match plan. |
| APIs | integration | `pytest backend/tests/api` | Every endpoint returns documented status and JSON. |
| Services | unit | `pytest backend/tests/services` | Deterministic services cover success/error paths. |
| Serialization | contract | `pytest backend/tests/contracts` | DTOs match Flutter domain models and `techdoc.md`. |
| Jobs | unit/integration | `pytest backend/tests/jobs` with Celery eager mode | Jobs write expected status transitions. |
| OpenAPI | schema check | `python -m scripts.export_openapi` later | OpenAPI includes all v1 routes. |
| Mobile smoke | manual later | run app with API repos later | Auth -> onboarding -> goal -> pretest path works. |

Test data strategy: seed one learner, four subjects, one Math/Calculus concept chain, one learning goal, one pretest session, one workspace, and one media artifact. Keep AI/media tests mocked until provider credentials are explicitly configured.

## 14. Risks and Open Questions

| Risk or Question | Impact | Recommended Decision |
|---|---|---|
| Product: exact curriculum source for Indonesia grade mapping is not defined. | Subject/concept seeds may be incomplete. | Start with minimal Calculus sample from current UI, mark curriculum as seed data. |
| Product: Google sign-in production behavior is undefined. | Auth scope can expand. | Stub compatible endpoint first; add real ID-token verification after credentials are available. |
| Technical: canvas Flutter classes are private UI internals. | Backend stroke DTOs would drift from mobile implementation. | Do not persist strokes; define an exported image contract, including format, max size, compression, and optional upload flow. |
| Technical: Manim/TTS/FFmpeg can be operationally heavy. | Media milestone can block core learning flow. | Model artifact/job records first; make rendering a separate worker milestone. |
| Integration: mobile has no HTTP client or token storage. | Backend cannot be used directly by app yet. | Build backend contracts first; later add API repositories and secure storage. |
| Timeline: full adaptive AI is larger than hackathon MVP. | Overbuilding risk. | Ship deterministic services first with clear AI extension points. |
| Data: graph/mastery quality depends on seeded concepts and rubrics. | Recommendations may be shallow. | Seed one high-quality Math path and keep graph API generic. |

## 15. Execution Checklist

- [x] FastAPI stack confirmed.
- [x] Backend root path confirmed as this repository.
- [x] PostgreSQL connection strategy configured via `WICARA_DATABASE_URL`.
- [x] Supabase JWT auth strategy configured for current auth endpoints.
- [x] Alembic migration workflow configured.
- [x] Profile onboarding endpoint implemented.
- [x] Health and profile tests added.
- [x] Workspace session/event timeline implemented.
- [x] Unified input event model implemented for workspace evidence.
- [ ] Canvas image export/upload contract confirmed.
- [ ] Manim/video artifact model confirmed.
- [ ] First mobile repository replacement confirmed.
- [x] Milestone 1 profile/onboarding acceptance criteria accepted.
- [x] Tests/verification commands known.
- [ ] No mobile changes required for backend Milestone 1.
- [ ] No destructive changes required.

## Final Notes

Before production deployment, confirm:

- database URL and local PostgreSQL availability
- Supabase project URL, JWKS URL, issuer, audience, and anon key
- whether Celery/Redis is configured immediately or deferred until media/jobs milestones
