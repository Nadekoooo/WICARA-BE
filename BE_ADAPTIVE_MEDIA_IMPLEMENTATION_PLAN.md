# WICARA BE Adaptive + Media Implementation Plan

## 1. Objective

Build backend flow that is aligned with `techdoc.md`:

- Unified multimodal learning evidence (`chat`, `canvas`, `image`, `mc`, `mixed`) as one `InputEvent`.
- Session router with temporary prerequisite sub-sessions.
- Graph-driven concept mapping and mastery updates.
- Template-first Manim video generation (`template_id + spec JSON`) with async worker.
- Production-safe separation between API runtime and renderer runtime.

## 2. Scope (Phase 1-8)

### In Scope

- Session + evidence persistence.
- Concept routing using curriculum mapping (`node_concept_type_mapping.csv`).
- Assessment verdict + mastery updates.
- Async media job pipeline (`queue -> renderer worker -> storage -> status`).
- Template-first renderer contract (LLM fills JSON spec, not full Manim code).

### Out of Scope (for this iteration)

- Perfect handwriting parsing.
- Full unrestricted chatbot.
- Full 108 concept type coverage in one sprint.
- Final production tuning for all languages/voices.

## 3. Repository/Runtime Shape

Keep in same repo (`WICARA-BE`) but run as separate services:

1. `api` service: FastAPI app (`uvicorn app.main:app`).
2. `worker` service: background media/adaptive jobs.
3. `redis` service: queue + cache.

Recommended structure extension:

```text
app/modules/
  adaptive/
    router.py
    service.py
    schemas.py
    models.py
  media_artifacts/
    api.py
    service.py
    models.py
    worker.py
  curriculum/
    router.py
    service.py
    loaders/
      concept_mapping_loader.py
  llm/
    spec_filler.py
    grader.py
```

## 4. Data Model Plan

Add/extend tables:

1. `learning_sessions`
- `id`, `student_id`, `parent_session_id`, `concept_id`, `session_type`, `status`, timestamps

2. `input_events`
- `id`, `student_id`, `session_id`, `event_type`
- `text_payload`, `selected_option`
- `image_asset_id`, `canvas_snapshot_id`, `canvas_stroke_batch_id`
- `parsed_problem`, `parsed_work`, `confidence`, timestamps

3. `assessment_attempts`
- `id`, `session_id`, `concept_id`, `assessment_type`
- `answer`, `verdict`, `score`, `misconception_type`, `feedback`, `evidence`

4. `student_concept_mastery`
- `student_id`, `concept_id`, `state`, `mastery_score`, `confidence`, `attempts`, `last_reviewed_at`

5. `media_artifacts`
- `id`, `student_id`, `session_id`, `concept_id`
- `template_id`, `spec_json`, `video_url`, `thumbnail_url`, `duration_sec`, `status`

6. `media_jobs`
- `id`, `artifact_id`, `job_type`, `status`, `progress`, `message`, `error`, `started_at`, `finished_at`

## 5. API Plan

### Adaptive + Session

1. `POST /api/v1/sessions/start`
- start parent or child session

2. `POST /api/v1/sessions/{session_id}/input`
- receive unified input event

3. `GET /api/v1/sessions/{session_id}/next-action`
- return router decision (`continue`, `clarify`, `open_subsession`, `generate_media`, etc.)

4. `POST /api/v1/assessments/{session_id}/submit`
- evaluate answer and update mastery

### Media

1. `POST /api/v1/animation/queue`
- input: `session_id`, `concept_id`, `template_id` (optional), `spec_json` (optional), `language`

2. `GET /api/v1/animation/status/{job_id}`
- output: `status`, `progress`, `message`, `video_url`, `thumbnail_url`

3. `GET /api/v1/media-artifacts/{artifact_id}`
- output artifact metadata

## 6. Concept Routing Plan (Curriculum-Driven)

Routing stages:

1. Constraint filter:
- by `subject`, `grade/phase`, active curriculum.

2. Candidate scoring:
- lexical + semantic score using fields from `node_concept_type_mapping.csv`:
  - `label_id`
  - `concept_type`
  - `concept_type_label_id`
  - `visual_pattern`
  - `real_world_anchor_examples`

3. Template resolution:
- pick `default_template_id`.
- if not implemented, use compatibility map to nearest implemented template.

4. Alias dictionary:
- map unseen terms to concept clusters (example: `turunan`, `d/dx`, `derivative` -> function/graph change-rate cluster).

5. Fallback:
- `generic_math_explanation` template when confidence below threshold.

## 7. Template-First Media Plan

Pipeline:

1. API chooses `template_id`.
2. LLM fills template spec JSON only.
3. Backend validates spec against template schema.
4. Worker renders using fixed template class.
5. Worker generates TTS + sync + FFmpeg merge.
6. Upload artifact and mark job `READY`.

Key rule:
- LLM must not generate arbitrary Manim Python in production path.

## 8. Voiceover and Duration Plan

Current MVP issue: videos are short due to static waits.

Fix plan:

1. Move template base to `VoiceoverScene`.
2. Use narration segments in spec:
- `narration_segments[]` with stage tags (`intro`, `step_1`, ..., `summary`).
3. Use `with self.voiceover(...) as tracker` and set animation `run_time` against tracker duration.
4. Add duration targets by level:
- SD: 60-100 sec
- SMP: 90-150 sec
- SMA: 120-180 sec
5. Add quality check in worker:
- if below minimum duration threshold, flag for retry or enrichment.

## 9. Execution Phases (1 Prompt = 1 Phase)

Use this section as execution script. Finish phase by phase.
Rule: one chat prompt only for one phase.

### Phase 1 - Foundation, Models, Queue Skeleton

Objective:
- Prepare durable data and async job skeleton.

Deliverables:
- Migrations for `input_events`, `media_artifacts`, `media_jobs`.
- Queue adapter (Redis) and worker bootstrap.
- Basic media status lifecycle (`queued`, `processing`, `ready`, `failed`).

Definition of Done:
- Can create a job row and move status from `queued` to `processing` to `failed/ready` in local test.

Prompt (copy-paste):

```text
Kerjakan PHASE 1 pada WICARA-BE: implement fondasi model + migration untuk input_events, media_artifacts, media_jobs, lalu buat queue/worker skeleton Redis dan status lifecycle job. Jangan sentuh mobile. Sertakan unit test minimal untuk create/update status job.
```

### Phase 2 - Pretest Backend-Driven (Remove Hardcoded Dependency)

Objective:
- Make pretest lifecycle fully backend-owned.

Deliverables:
- Endpoint lifecycle pretest: fetch session/questions, submit answer, finalize.
- Idempotent submit behavior and progress tracking.
- Response contract ready for FE migration.

Definition of Done:
- Pretest attempt rows stored server-side and final result computed from backend state.

Prompt (copy-paste):

```text
Kerjakan PHASE 2 pada WICARA-BE: kuatkan API pretest supaya benar-benar backend-driven (fetch question/session, submit per answer, finalize), simpan semua attempt, dan pastikan idempotent. Buat test API untuk flow pretest lengkap.
```

### Phase 3 - Posttest Module + Mastery Update

Objective:
- Build missing posttest backend module.

Deliverables:
- Create posttest session by module/concept.
- Submit posttest answers and compute result.
- Update `student_concept_mastery` from posttest evidence.

Definition of Done:
- Posttest session/attempt/result available via API and changes mastery state.

Prompt (copy-paste):

```text
Kerjakan PHASE 3 pada WICARA-BE: implement posttest end-to-end (create session, fetch questions, submit answers, result endpoint), lalu update mastery state dari hasil posttest. Tambahkan tests.
```

### Phase 4 - Daily Evaluation from Question Bank

Objective:
- Replace static daily templates with bank-driven selector.

Deliverables:
- `question_bank_items` + options model (or equivalent).
- Seed importer and validation checks.
- Selector policy: due + weak + recent concept.

Definition of Done:
- `GET /daily-evaluations/today` returns bank-backed questions with `selection_policy` and `fallback_reason`.

Prompt (copy-paste):

```text
Kerjakan PHASE 4 pada WICARA-BE: bangun question bank + selector untuk daily evaluation (due concept, weak concept, recently learned), seed importer, validasi kualitas soal, dan expose metadata selection_policy/fallback_reason di API.
```

### Phase 5 - Session Router + Workspace AI Boundary

Objective:
- Move workspace logic from deterministic static response to routed adaptive flow.

Deliverables:
- `SessionRouterService` decisions: continue, clarify, open_subsession, switch_topic.
- `ExplanationService` boundary with provider abstraction and fallback.
- Prompt/version metadata persisted for audit.

Definition of Done:
- Workspace events produce routed next action and auditable tutor response metadata.

Prompt (copy-paste):

```text
Kerjakan PHASE 5 pada WICARA-BE: implement SessionRouterService + ExplanationService boundary untuk workspace events, termasuk mode fallback deterministik yang eksplisit, dan simpan metadata prompt/model/version untuk audit.
```

### Phase 6 - Canvas/Image Evidence Pipeline

Objective:
- Make canvas evidence real, not metadata-only.

Deliverables:
- Image upload endpoint and storage metadata.
- Attach `image_asset_id` into input/assessment evidence.
- Parser stub job with states (`pending`, `parsed`, `failed`).

Definition of Done:
- Assessment/workspace events can reference real uploaded canvas/image assets.

Prompt (copy-paste):

```text
Kerjakan PHASE 6 pada WICARA-BE: implement upload evidence image/canvas, simpan metadata asset, sambungkan image_asset_id ke input_events/assessment_attempts, dan tambahkan parser stub job dengan status parsed/failed.
```

### Phase 7 - Template-First Manim Media Pipeline

Objective:
- Enable real media generation jobs from template spec.

Deliverables:
- `POST /animation/queue` creates artifact + job.
- Worker pipeline: template_id -> spec validation -> render -> upload -> status update.
- `GET /animation/status/{job_id}` returns progress and output URLs.

Definition of Done:
- One real template render request can complete and produce stored artifact URL.

Prompt (copy-paste):

```text
Kerjakan PHASE 7 pada WICARA-BE: implement pipeline video generation template-first (bukan codegen Manim bebas), dari queue job sampai artifact ready, lengkap dengan endpoint queue/status, validasi spec schema, dan update progress.
```

### Phase 8 - Voiceover Quality + Report Propagation + E2E

Objective:
- Improve output quality and ensure state propagation to reports.

Deliverables:
- VoiceoverScene migration for priority templates and duration policy.
- Report aggregation includes pretest/posttest/daily/workspace/media evidence.
- One integration test for full learning flow.

Definition of Done:
- Generated video duration meets target policy and report reflects end-to-end learning events.

Prompt (copy-paste):

```text
Kerjakan PHASE 8 pada WICARA-BE: upgrade kualitas voiceover/durasi template prioritas, pastikan report/knowledge map ter-update dari pretest-posttest-daily-workspace-media, dan buat integration test end-to-end alur belajar.
```

## 10. First Template Coverage Strategy

Do not target all 61 unique manim template IDs immediately.

Start with highest-impact implemented templates:

1. `manim.equation_balance.v1`
2. `manim.graph_explanation.v1`
3. `manim.sequence_pattern.v1`
4. `manim.number_line_quantity.v1`
5. `manim.ratio_proportion.v1`
6. `manim.force_diagram.v1`
7. `manim.motion_kinematics.v1`
8. `manim.fraction_bar_partition.v1`
9. `manim.elementary_arithmetic_blocks.v1`
10. `manim.geometry_area_volume.v1` (or mapped alias to taxonomy id)

Then expand by node-frequency priority from curriculum mapping.

## 11. Gap Coverage vs gap.md

Reference file: `../gap.md`.

Major gap domains in `gap.md` section 4-11:

1. Pretest.
2. Posttest.
3. Workspace chat/AI.
4. Video generation/media.
5. Canvas/multimodal evidence.
6. Adaptive engine/curriculum alignment.
7. Reports/progress/knowledge map.
8. Daily quiz source.

Coverage by this plan:

| Gap Domain (`gap.md`) | Phase | Coverage Status |
|---|---|---|
| Pretest | Phase 2 | Covered |
| Posttest | Phase 3 | Covered |
| Workspace chat/AI | Phase 5 | Covered |
| Video generation/media | Phase 7 | Covered |
| Canvas/multimodal evidence | Phase 6 | Covered |
| Adaptive engine/curriculum alignment | Phase 2 + 4 + 5 | Covered |
| Reports/progress/knowledge map | Phase 8 | Covered |
| Daily quiz source | Phase 4 | Covered |

Summary:

- Coverage for major domain gaps (section 4-11): **8/8**.
- Coverage for minimum build list in `gap.md` section 17: **12/12 mapped** across phases.
- Remaining out-of-scope from `gap.md`: auth hardening, password reset lifecycle, and full FE migration details.

## 12. Risks and Mitigation

1. Short/flat videos
- Mitigation: narration segments + duration policy + quality gates.

2. Invalid JSON specs from small LLM
- Mitigation: strict schema validation + auto-repair prompt + fallback defaults.

3. Template mismatch with taxonomy IDs
- Mitigation: explicit template compatibility map and registry tests.

4. Long render latency
- Mitigation: async queue, quality profiles (`preview` vs `final`), timeout/retry policy.

5. Worker crash affecting API
- Mitigation: isolated runtime process + idempotent job updates.

## 13. Immediate Next Tasks

1. Create `template_registry.json` (implemented templates + schema path + compatibility aliases).
2. Create migration for `media_artifacts` + `media_jobs`.
3. Implement minimal worker loop and Redis queue adapter.
4. Implement `/animation/queue` and `/animation/status/{job_id}`.
5. Define spec schemas for first 3 templates (`equation_balance`, `graph_explanation`, `sequence_pattern`).
6. Migrate first template to `VoiceoverScene` and validate duration improvement.
