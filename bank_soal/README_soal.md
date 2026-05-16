# Bank Soal MVP Specification

## 1. Purpose

Folder `backend/bank_soal/` menyimpan spesifikasi dan seed awal bank soal WICARA. Bank soal ini menjadi source of truth untuk pretest, posttest, daily quiz, dan workspace quiz sebelum sistem AI question generation siap.

Target MVP:

- backend bisa import JSON bank soal ke database
- backend bisa memilih soal untuk daily quiz berdasarkan konsep, level, bahasa, dan mastery state
- mobile tidak membaca file JSON langsung, tetapi menerima soal melalui API backend
- format JSON tetap cukup stabil agar bisa dipakai ulang untuk mobile fixture/test bila diperlukan

## 2. Recommended File Layout

```text
backend/bank_soal/
  README.md
  schema/
    question_bank.schema.json
  scripts/
    generate_mathematics_topic_bank.py
    generate_science_topic_banks.py
  seeds/
    mathematics.elementary.all_topics.v1.json
    mathematics.junior_high.all_topics.v1.json
    mathematics.senior_high.all_topics.v1.json
    mathematics.elementary.multiplication_equal_groups.v1.json
    ipas.elementary.all_topics.v1.json
    ipa.junior_high.all_topics.v1.json
    fisika.senior_high.all_topics.v1.json
    kimia.senior_high.all_topics.v1.json
    biologi.senior_high.all_topics.v1.json
```

Current generated state:

- `*.all_topics.v1.json` files are breadth-first topic coverage derived from the curriculum graph
- `mathematics.elementary.multiplication_equal_groups.v1.json` is a focused concept seed
- generators now emit separate `pretest`, `daily_quiz`, `posttest`, and `workspace_quiz` items per concept

These generated packs are baseline coverage, not yet deep production-quality concept banks.

## 3. JSON Is The MVP Format

Gunakan JSON sebagai format awal.

Reason:

- nested options dan rubric lebih aman dibanding CSV
- bisa divalidasi dengan JSON Schema
- mudah di-import ke database
- mudah dibuat fixture untuk test mobile/backend
- cocok untuk multi-bahasa, metadata konsep, difficulty, dan assessment type

CSV/spreadsheet boleh dipakai nanti sebagai authoring tool, tetapi hasil akhirnya tetap diekspor ke JSON tervalidasi.

## 4. MVP Question Count

Jumlah minimum ini cukup untuk demo yang tidak terasa terlalu repetitif, tetapi tetap realistis untuk dibuat cepat.

| Subject | Level | Concepts MVP | Pretest | Daily Quiz | Posttest | Workspace Quiz | Total Minimum |
|---|---|---:|---:|---:|---:|---:|---:|
| Matematika | SD | 3 | 6 | 9 | 10 | 3 | 28 |
| Matematika | SMP | 3 | 6 | 9 | 10 | 3 | 28 |
| Fisika | SMA | 2 | 4 | 6 | 6 | 2 | 18 |
| Kimia | SMA | 2 | 4 | 6 | 6 | 2 | 18 |
| Biologi | SMA | 2 | 4 | 6 | 6 | 2 | 18 |

Recommended MVP scope:

| Priority | Scope | Why |
|---|---|---|
| P0 | Matematika SD + Matematika SMP | Matches current hardcoded mobile packs. |
| P1 | Daily quiz selector using Matematika only | Proves adaptive loop without broad content work. |
| P2 | Fisika/Kimia/Biologi skeleton | Prevents selected subjects from feeling empty. |

Minimum per concept:

| Assessment Type | Minimum Per Concept | Notes |
|---|---:|---|
| `pretest` | 2 | One easy prerequisite probe, one medium diagnosis. |
| `daily_quiz` | 3 | One due review, one weak concept, one recently learned variant. |
| `posttest` | 3 | Stronger coverage after module completion. |
| `workspace_quiz` | 1 | Inline formative check inside workspace. |

## 5. Top-Level JSON Structure

Each seed file should use this shape:

```json
{
  "version": "2026-05-16",
  "source": "wicara_question_bank_seed_v1",
  "language": "en",
  "subject_code": "mathematics",
  "education_level": "elementary",
  "grade_band": "elementary",
  "items": []
}
```

Top-level fields:

| Field | Required | Description |
|---|---|---|
| `version` | yes | Seed version date or semantic version. |
| `source` | yes | Human-readable source identifier. |
| `language` | yes | Default language for all items unless overridden. Current generated baseline seeds use `en`. |
| `subject_code` | yes | Canonical subject code from the active curriculum/seed set, e.g. `mathematics`, `ipas`, `ipa`, `fisika`, `kimia`, `biologi`. |
| `education_level` | yes | `elementary`, `junior_high`, or `senior_high`. |
| `grade_band` | yes | Current generated seeds use `elementary`, `junior_high`, or `senior_high`. |
| `items` | yes | List of question items. |

## 6. Question Item Format

```json
{
  "id": "math_sd_multiplication_pre_001",
  "subject_code": "mathematics",
  "concept_code": "multiplication_equal_groups",
  "concept_title": "Multiplication as equal groups",
  "education_level": "elementary",
  "grade_band": "elementary",
  "language": "en",
  "assessment_types": ["pretest"],
  "question_type": "multiple_choice",
  "difficulty": "easy",
  "cognitive_level": "understand",
  "prompt": "Mila has 4 boxes. Each box has 3 crayons. How many crayons are there altogether?",
  "helper_text": "Use equal groups to find the total.",
  "options": [
    {"label": "A", "text": "7"},
    {"label": "B", "text": "12"},
    {"label": "C", "text": "14"},
    {"label": "D", "text": "16"}
  ],
  "answer_key": "B",
  "explanation": "There are 4 equal groups of 3 crayons, so 4 x 3 = 12.",
  "rubric": {
    "correct": "Learner understands multiplication as equal groups.",
    "common_misconceptions": [
      "Adds the two numbers directly instead of multiplying.",
      "Confuses number of groups with total objects."
    ]
  },
  "tags": ["multiplication", "equal_groups", "story_problem", "pretest"],
  "status": "active",
  "metadata": {
    "source_pack": "baseline_generated",
    "estimated_seconds": 45
  }
}
```

## 7. Required Fields

Every item must include:

| Field | Type | Rule |
|---|---|---|
| `id` | string | Unique and stable. Do not reuse after content changes meaningfully. |
| `subject_code` | string | Must match backend curriculum subject code. |
| `concept_code` | string | Must map to backend `knowledge_concepts.code` when possible. |
| `concept_title` | string | Human-readable fallback if concept does not exist yet. |
| `education_level` | string | `elementary`, `junior_high`, `senior_high`. |
| `grade_band` | string | Current generated seeds use `elementary`, `junior_high`, or `senior_high`. |
| `language` | string | `id`, `en`, etc. Current generated baseline seeds use `en`. |
| `assessment_types` | array | Any of `pretest`, `posttest`, `daily_quiz`, `workspace_quiz`. |
| `question_type` | string | MVP: `multiple_choice`. |
| `difficulty` | string | `easy`, `medium`, `hard`. |
| `prompt` | string | The learner-facing question. |
| `options` | array | Required for `multiple_choice`; current WICARA bank contract uses exactly 4. |
| `answer_key` | string | Must match one option label. |
| `explanation` | string | Shown after answer or stored for tutor/report. |
| `status` | string | `draft`, `reviewed`, `active`, `retired`. MVP selector should only use `active`. |

## 8. Optional Fields

| Field | Purpose |
|---|---|
| `helper_text` | Hint or instruction displayed under question. |
| `cognitive_level` | `remember`, `understand`, `apply`, `analyze`. |
| `rubric` | Used for explanation, review, and AI grading later. |
| `tags` | Selector and coverage metadata. |
| `metadata` | Source notes, timing, import provenance, legacy ID. |

## 9. ID Naming Convention

Use stable lowercase IDs:

```text
{subject}_{level}_{concept_short}_{assessment}_{number}
```

Examples:

```text
math_sd_multiplication_pre_001
math_sd_multiplication_daily_001
math_sd_multiplication_post_001
math_smp_algebra_pre_001
math_smp_algebra_workspace_001
```

Avoid IDs that depend on row number in a spreadsheet unless the exported row is stable.

## 10. Assessment Type Rules

| Type | Expected Use | Scoring |
|---|---|---|
| `pretest` | Diagnose prerequisite gaps before track starts. | Updates initial mastery and path. |
| `posttest` | Check understanding after module/track learning. | Strong mastery signal; affects report. |
| `daily_quiz` | Spaced repetition and retention check. | Updates review schedule and mastery. |
| `workspace_quiz` | Inline formative check inside workspace. | Small mastery delta and module evidence. |

Current generated baseline uses **one assessment type per item**. This is the preferred default because it keeps `pretest`, `daily_quiz`, `posttest`, and `workspace_quiz` behavior separate at the item level.

Multi-type reuse is still possible in the schema, but should be used deliberately rather than as the default.

## 11. Daily Quiz Selector Contract

Daily quiz should select from the bank, not from hardcoded templates.

Recommended MVP selector:

```text
Input:
- user_id
- selected subject(s)
- learner concept states
- latest pretest/posttest/daily attempts
- preferred language
- grade/education level

Output:
- assessment_session with 3 questions
```

Selection policy:

| Slot | Rule | Fallback |
|---|---|---|
| 1 | Concept with `next_review_at <= now`. | Starter concept from selected subject. |
| 2 | Lowest mastery/confidence concept. | Medium difficulty question from active track. |
| 3 | Recently completed or active module concept. | Any active daily question matching level/language. |

Every selected question should be copied into `assessment_questions` for the session, so future edits to the bank do not change historical attempts.

## 12. Backend Import Mapping

Recommended database mapping:

| JSON Field | Backend Destination |
|---|---|
| `id` | `question_bank_items.external_id` |
| `subject_code` | FK to `subjects.code` |
| `concept_code` | FK to `knowledge_concepts.code`, nullable fallback |
| `prompt` | `question_bank_items.prompt` |
| `helper_text` | `question_bank_items.helper_text` |
| `difficulty` | `question_bank_items.difficulty_label` |
| `assessment_types` | JSON/tags or join table |
| `options[]` | `question_bank_options` |
| `answer_key` | `question_bank_options.is_correct` |
| `explanation` | `question_bank_items.explanation` |
| `rubric` | JSON metadata |
| `status` | `question_bank_items.status` |

If `concept_code` does not exist yet, importer should either:

- fail in strict mode, or
- import with `concept_id = null` and record `concept_code` in metadata.

For current generated packs, prefer strict mode when the concept exists in the curriculum graph and backend concept seeds are aligned. Use fallback mode only for intentionally incomplete packs.

## 13. Mobile Compatibility

Mobile should not read these JSON files directly in production. Backend should expose assessment questions in the existing `PretestQuestion`-compatible DTO:

```json
{
  "id": "uuid-or-bank-derived-id",
  "step_label": "1 / 3",
  "topic": "Multiplication Pretest",
  "prompt": "Mila has 4 boxes. Each box has 3 crayons. How many crayons are there altogether?",
  "helper": "Use equal groups to find the total.",
  "options": [
    {"id": "A", "label": "A", "text": "7"},
    {"id": "B", "label": "B", "text": "12"}
  ]
}
```

Backend may keep richer fields internally, but mobile only needs the delivery DTO. This keeps the bank flexible without forcing mobile to understand import metadata, rubric, tags, or bank status.

## 14. Validation Rules

Before import, every JSON seed should pass:

- file is valid JSON
- top-level `items` is not empty
- every item has unique `id`
- `assessment_types` is not empty
- `options` has exactly 4 items for the current MCQ contract
- exactly one option label matches `answer_key`
- no duplicate option labels within a question
- `status` is one of `draft`, `reviewed`, `active`, `retired`
- `difficulty` is one of `easy`, `medium`, `hard`
- `language` is a supported language code
- active questions must have `explanation`

Coverage validation for MVP:

- each generated `*.all_topics.v1.json` pack has one separated item per concept per assessment type
- each concept in the generated baseline packs currently has:
  - 1 pretest question
  - 1 daily quiz question
  - 1 posttest question
  - 1 workspace quiz question
- Each active MVP concept has at least:
  - 2 pretest questions
  - 3 daily quiz questions
  - 3 posttest questions
  - 1 workspace quiz question

Interpretation:

- the current generated packs satisfy broad baseline coverage
- they do **not** yet satisfy the deeper per-concept target for rich production assessment banks

## 15. First MVP Seed Plan

Initial seed history and current state:

| Current Source | Target Seed |
|---|---|
| Mobile hardcoded multiplication content | `mathematics.elementary.multiplication_equal_groups.v1.json` |
| Curriculum graph math nodes | `mathematics.*.all_topics.v1.json` |
| Curriculum graph IPAS/IPA/science nodes | `ipas.*`, `ipa.*`, `fisika.*`, `kimia.*`, `biologi.*` all-topics seeds |

Current next step after baseline generation:

- deepen each concept from 1 separated item per assessment type into richer concept banks
- replace topic-identification prompts with concept application items where production quality is required

## 16. MVP Acceptance Criteria

Bank soal MVP is ready when:

- JSON seed files validate.
- Backend can import active questions.
- Backend can create a daily evaluation session from bank questions.
- Backend can create pretest and posttest sessions from bank questions.
- Mobile receives the same simple question DTO it already understands.
- Weekly report can distinguish `pretest`, `posttest`, `daily_quiz`, and `workspace_quiz` attempts.
- No scored assessment depends on `HardcodedAssessmentBank` in mobile.

## 17. Open Decisions

| Decision | Recommended MVP |
|---|---|
| JSON or CSV? | JSON. |
| Direct AI-generated daily quiz? | No. Use bank soal first. |
| Can AI help write questions? | Yes, but only into draft bank items that pass validation/review. |
| Should mobile read seed JSON? | No for production; only optional fixtures/tests. |
| Should questions be copied to assessment sessions? | Yes, so historical attempts remain stable. |
| Should posttest reuse pretest questions? | Prefer separate variants. Reuse only for early demo if content is limited. |
