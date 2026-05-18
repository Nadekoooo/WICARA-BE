# WICARA — Technical Implementation Specification v6
**Adaptive AI Tutor for Underserved ASEAN Learners**  
*UI 1 — WICARA ASEAN | University of Indonesia | ASEAN AI Hackathon 2026*

---

## 1. Vision & Core Problem

Across ASEAN, two problems compound each other: the **language barrier** and a **deeper diagnostic failure**. Quality learning resources are often English-first, while many students also do not know which prerequisite concept they are missing. A student confused by derivatives may actually be missing foundational algebra, exponents, multiplication fluency, graph interpretation, or function notation. Giving them a derivative explanation immediately, even in their language, can deepen confusion because the real gap is earlier in the prerequisite chain.

WICARA solves this by acting as an adaptive AI tutor that can:

1. Find the student's *exact* knowledge gap using adaptive diagnostic probing against a prerequisite graph.
2. Let students express their thinking through **chat, image upload, micro-quiz answers, and an always-on canvas**.
3. Explain from the gap point using native-language explanations, local cultural analogies, generated Manim visuals, and synchronized voiceover.
4. Continuously update a student-specific mastery graph, including when the student enters temporary prerequisite sub-sessions.

The core product claim is not simply "AI chatbot for education." The core claim is **prerequisite-first, graph-driven, multimodal adaptive tutoring for underserved ASEAN learners**.

---

## 2. Research-Backed Foundation

WICARA's selling point should preserve the research language from the original concept. These terms are not decoration; they explain why the product is more than a generic chatbot.

| Research / Pedagogical Base | How WICARA Uses It | Product Impact |
|---|---|---|
| **Knowledge Space Theory (KST)**, similar to the idea behind ALEKS-style adaptive assessment | The pretest is not a fixed exam. It adaptively probes prerequisite concepts and estimates what the student already knows. | WICARA can infer knowledge state efficiently instead of asking every possible question. |
| **Educational Knowledge Graph (EKG) research** | Curriculum concepts are represented as nodes, prerequisite relationships as directed edges, and student mastery as per-node state. | The tutor knows *why* a student is blocked and what concept should come before the target topic. |
| **Graph of Graphs** | WICARA connects subject graphs through cross-subject edges, such as Math ratios enabling Physics speed and velocity. | Mastering a Math node can unlock a Physics node automatically. |
| **5E STEAM learning cycle** | Each learning loop follows Engage, Explore, Explain, Elaborate, and Evaluate. | Lessons are structured pedagogically, not just generated as random chat responses. |
| **Dynamic prerequisite backtracking** | If a student fails because of a deeper prerequisite, the system temporarily moves down the graph. | The tutor repairs the true root cause before returning to the parent topic. |
| **Ebbinghaus forgetting curve model** | Daily Evaluation prioritizes concepts approaching a forgetting threshold using recency and mastery score. | WICARA supports retention, not only one-time completion. |
| **Spaced repetition** | Recently mastered but decaying concepts are reintroduced in short daily reviews. | Students maintain long-term mastery across the graph. |

This foundation should remain visible in the technical document because it is part of WICARA's competitive positioning.

---

## 3. System Architecture Overview

WICARA is an **adaptive learning workspace**, not a fixed sequence of pages. The main student experience is a persistent **Chat + Canvas workspace** where the student can type, draw, upload a problem, answer an adaptive question, or ask for help at any moment.

The backend treats all of those actions as evidence attached to the same adaptive session. A typed answer, a multiple-choice selection, a photo of a worksheet, and a partially solved equation on the canvas are all routed through the same diagnosis and mastery pipeline.

### 3.1 Core Architecture Layers

| Layer | Responsibility | Example |
|---|---|---|
| **Input Layer** | Accepts student text, question images, screenshots, canvas strokes, canvas snapshots, and micro-quiz answers. | Student uploads a photo, writes steps on canvas, then asks "why is this wrong?" |
| **Pre-processing Layer** | Converts raw inputs into usable signals through OCR, canvas parsing, and intent parsing. | OCR extracts the problem, Canvas Parser reads partial work, Intent Parser detects a derivative question. |
| **Session Router** | Decides whether the input belongs to the current topic, needs a micro-explanation, requires clarification, or should open a sub-session. | A side question about exponents during derivatives becomes a temporary prerequisite sub-session. |
| **Adaptive Pretest / Local Probe Engine** | Uses KST-inspired probing to estimate knowledge state across the Educational Knowledge Graph. | WICARA checks 2–3 nearby prerequisite nodes before teaching the target concept. |
| **Target Concept Detector** | Identifies the main learning target from student input or selected map node. | A worksheet photo is classified as "Derivatives: power rule." |
| **Path Engine** | Chooses the next learning node based on mastery, confidence, prerequisite distance, and curriculum priority. | If the student has a small algebra gap, the path repairs algebra before derivatives. |
| **Mastery State Engine** | Updates concept state, score, attempts, confidence, and evidence references. | Canvas evidence can increase or decrease confidence in a node. |
| **5E STEAM Adaptive Course Loop** | Runs Engage → Explore → Explain → Elaborate → Evaluate, with backtracking when needed. | A local-context explanation is followed by practice and a checkpoint. |
| **Error Analyzer** | Classifies mistakes as misconception, prerequisite gap, unclear work, or off-topic input. | Wrong exponent manipulation triggers Dynamic Prerequisite Backtracking. |
| **Media Generator** | Creates Manim animations, language-specific TTS, and compressed video via FFmpeg. | A derivative tangent-line scene is generated with Indonesian labels and voiceover. |
| **Report Engine** | Produces learning reports comparing pretest, post-test, solved gaps, and next recommendations. | Student sees which prerequisite gap was fixed and what to study next. |

### 3.2 Unified Input Contract: Chat and Canvas Are the Same Source of Evidence

The most important UX and backend rule: **chat and canvas are not separate modes**. They are two interfaces connected to the same adaptive input pipeline. From the system's perspective, a typed chat answer, a drawing on the canvas, a multiple-choice tap, an uploaded image, and a canvas annotation are all normalized into the same object: an `InputEvent`.

This means **canvas is always available, but never mandatory**. If a student does not like using the canvas, they can answer entirely through chat. If they prefer writing math by hand, they can answer on the canvas. If the task is visual, they can upload a photo and mark it up. WICARA evaluates whichever evidence is available and routes it through the same diagnosis, mastery, and feedback pipeline.

This applies during:

- onboarding support,
- adaptive pretest,
- prerequisite probing,
- diagnosis,
- 5E learning loop,
- explanation,
- practice,
- verification,
- post-test,
- daily evaluation,
- temporary sub-session,
- and learning report review.

Every adaptive question therefore supports multiple answer channels:

| Answer Channel | Student Experience | Backend Treatment |
|---|---|---|
| **Chat text** | Student types: "x^2 becomes 2x" or explains reasoning in words. | Stored as text evidence in the same `InputEvent`. |
| **Canvas work** | Student writes equations, draws graphs, or shows step-by-step work. | Canvas strokes and snapshot are parsed as visual/math evidence. |
| **Multiple-choice tap** | Student selects option A/B/C/D. | Stored as structured answer evidence. |
| **Image upload** | Student uploads a worksheet, textbook problem, or screenshot. | OCR and image understanding extract the problem and context. |
| **Mixed input** | Student uploads a worksheet, circles part of it, writes on canvas, then asks in chat. | All evidence is merged into one multimodal `InputEvent`. |

So for product clarity: **the student is never forced to use canvas**. Canvas is an optional but powerful diagnostic layer. Chat alone is enough for answering adaptive questions, continuing a lesson, asking for clarification, or completing a quiz. Canvas becomes useful when the student wants to show partial working, graphs, handwritten math, diagrams, or a marked-up problem.

Examples:

| Student Action | System Interpretation |
|---|---|
| Student answers a pretest question by typing in chat. | The answer is evaluated normally and updates the adaptive pretest state. |
| Student answers the same question by drawing equations on the canvas. | Canvas snapshot and stroke order are attached to the assessment attempt. |
| Student solves only the first two steps of a derivative problem. | Partial work is inspected; WICARA may detect correct setup but wrong exponent rule. |
| Student circles a part of a worksheet photo and asks "ini kenapa?" | Image crop, chat text, and canvas annotation become the same input event. |
| Student asks a side question during a lesson. | Context Checker decides whether to answer inline, clarify, or open a temporary sub-session. |
| Student writes a wrong prerequisite step repeatedly. | Error Analyzer triggers Dynamic Prerequisite Backtracking. |

This unified input model is what makes the product feel like a flexible tutor instead of a rigid quiz app. The student can interact naturally, while the backend still keeps a rigorous Educational Knowledge Graph, mastery state, and evidence trail.

### 3.3 Temporary Sub-Sessions Are Real Mastery Updates

Temporary sub-sessions are not disposable chats. They update the same Educational Knowledge Graph and the same `student_concept_mastery` table as the parent session.

Example:

1. The parent target is `Derivatives`.
2. Canvas work reveals confusion with `Exponents`.
3. WICARA pauses the derivative session and starts a child session for `Exponents`.
4. The child session still uses the same chat, canvas, assessment engine, and mastery state engine.
5. If the student improves, the `Exponents` node is updated.
6. WICARA resumes the parent `Derivatives` session with better context.

This is how the product feels flexible to the student while remaining rigorous and graph-driven in the backend.

---

### 3.4 Unified Input Event Model

Because chat and canvas are the same source of evidence, the backend should not store them as unrelated systems. WICARA should store every student interaction as a normalized multimodal event.

```sql
input_events (
  id UUID PRIMARY KEY,
  student_id UUID,
  session_id UUID,
  parent_session_id UUID NULL,
  concept_id UUID NULL,
  event_type TEXT,              -- CHAT_TEXT | CANVAS_STROKE | CANVAS_SNAPSHOT | MC_ANSWER | IMAGE_UPLOAD | MIXED
  text_payload TEXT NULL,
  selected_option TEXT NULL,
  image_asset_id UUID NULL,
  canvas_snapshot_id UUID NULL,
  canvas_stroke_batch_id UUID NULL,
  parsed_problem JSONB NULL,
  parsed_work JSONB NULL,
  confidence FLOAT NULL,
  created_at TIMESTAMP
)
```

The adaptive engines consume `input_events`, not only chat messages. This allows WICARA to spot partial problem-solving evidence, such as a correct setup with an incorrect algebraic transformation, while still supporting students who prefer plain text chat.

## 4. Updated Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Client | Flutter | Cross-platform, mobile-first, low-spec Android support. |
| Always-On Canvas | Flutter `CustomPainter` / canvas widget | Captures strokes, eraser events, canvas snapshots, annotations, and step-by-step working. |
| Backend | FastAPI | Matches the team's backend stack; provides async-first APIs, OpenAPI generation, dependency injection, and Pydantic validation. |
| ORM / Migrations | SQLAlchemy 2.x + Alembic | Provides explicit relational modeling, migrations, and PostgreSQL-first data access. |
| Realtime / Streaming | FastAPI ASGI with SSE or WebSocket endpoints | Streams tutor responses, session updates, media job status, and canvas-aware feedback. |
| Task Queue | Celery + Redis | Handles OCR, Manim rendering, TTS generation, FFmpeg compression, report generation, and async LLM jobs. |
| Database | PostgreSQL | Stores student profiles, sessions, mastery state, Educational Knowledge Graph, curriculum binding, canvas snapshots, and assessment attempts. |
| Cache | Redis | LLM response cache, session cache, media status cache, rate limiting, and animation availability. |
| LLM | OpenRouter Gemma | Multilingual explanation generation, intent parsing, AI grading, and local analogy generation. |
| OCR | Google Vision API, with Tesseract fallback for MVP/local testing | Extracts text from question photos, screenshots, and rendered canvas snapshots. |
| Animation | Manim | Code-generated, parameterized mathematical animations. |
| Voiceover | Google Cloud TTS | Per-language voiceover with SSML support and timing control. |
| Video Processing | FFmpeg | Merges audio/video and compresses media for low-bandwidth devices. |
| Graph Storage | PostgreSQL adjacency list, optional Neo4j later | MVP stays inside FastAPI/Postgres; Neo4j can be added if graph traversal becomes more complex. |
| API Style | REST + streamed events | REST for state changes; streaming for LLM explanations, progress events, and long-running media jobs. |

### 4.1 FastAPI Project Layout

```text
backend/
  pyproject.toml
  alembic.ini
  app/
    main.py
    api/
      v1/
        router.py
    core/
      config.py
      security.py
      celery_app.py
    db/
      base.py
      session.py
      migrations/
    modules/
      accounts/        # student profile, language, country, grade, curriculum binding
      curriculum/      # curriculum standards, localized concept metadata
      graph/           # Educational Knowledge Graph, prerequisite edges, cross-subject edges
      mastery/         # per-student mastery state and graph propagation
      sessions/        # parent sessions, temporary sub-sessions, session router, context checker
      inputs/          # text, image, OCR, canvas strokes, canvas snapshots, intent parsing
      assessments/     # pretest, local probes, micro-quiz, verification, post-test, daily evaluation
      explanations/    # LLM prompts, local analogy bank, tutor response generation
      media/           # Manim, TTS, FFmpeg, generated video assets
      reports/         # learning reports, pre/post comparison, recommendations
      observability/   # health checks, metrics, structured logs
```

---

## 5. Full Student Flow

### Phase 0 — Onboarding

**Purpose:** Capture the minimum context required to personalize the graph and explanations.

**Student provides:**

- name,
- country,
- grade level,
- language preference,
- activated subjects.

**Backend actions in FastAPI:**

- Create `StudentProfile`.
- Bind the student to a curriculum, for example Indonesia → Kurikulum Merdeka.
- Initialize subject graph states.
- Create the first `LearningSession` for adaptive pretest.

### Phase 1 — Adaptive Pretest Using Knowledge Space Theory

The pretest is modeled on the spirit of **Knowledge Space Theory (KST)**. It is not a fixed 50-question exam. It is an adaptive probing session that estimates the student's knowledge state across the graph with fewer questions.

**How it works:**

- The engine starts from strategically selected mid-level nodes.
- If the student answers correctly, it probes upward or infers some prerequisites as likely mastered.
- If the student answers incorrectly, it probes downward toward prerequisites.
- After enough evidence, the engine classifies nodes as `MASTERED`, `GAP`, or `UNKNOWN`.
- The result becomes the first version of the student's Knowledge State Report.

**Always-on canvas behavior:**

During pretest, the student can answer through:

- multiple-choice selection,
- typed short answer,
- canvas solution,
- uploaded image,
- or mixed text + canvas.

This matters because some students can show understanding better through written work than through typing. WICARA should not force all reasoning into a text box.

### Phase 2 — Learning Map Generation Using Educational Knowledge Graph

WICARA implements an **Educational Knowledge Graph (EKG)**, where concepts are nodes and prerequisite relationships are directed edges.

#### Level 1 — Subject Graph

Each subject has its own prerequisite graph. For Math, a simplified chain may include:

- Integers
- Fractions
- Ratios
- Proportions
- Linear equations
- Functions
- Derivatives

The graph is not just visual. It determines which nodes are ready, blocked, or in progress.

#### Level 2 — Cross-Subject Graph / Graph of Graphs

The **Graph of Graphs** connects concepts across subjects. For example:

| Source Concept | Target Concept | Why it matters |
|---|---|---|
| Math: Ratios and Proportions | Physics: Speed and Velocity | Speed requires proportional reasoning. |
| Math: Functions | Physics: Motion Graphs | Motion graphs require function interpretation. |
| Math: Exponential Functions | Chemistry: Reaction Rates | Some rate concepts depend on exponential reasoning. |
| Math: Statistics and Probability | Biology: Genetics | Punnett squares and probability require statistical reasoning. |

This means mastering a Math concept can automatically unlock a Physics, Chemistry, or Biology node without forcing the student to retake a separate prerequisite test.

#### Node States

| State | Meaning |
|---|---|
| `MASTERED` | Student has passed pretest, verification, post-test, or repeated review with high confidence. |
| `GAP` | Student has a detected weakness that should be prioritized. |
| `READY` | All prerequisites are sufficiently mastered; the concept can be started. |
| `LOCKED` | One or more prerequisites are not yet mastered. |
| `IN_PROGRESS` | Student is actively learning this node. |
| `REVIEW_DUE` | Node was mastered before but is approaching forgetting threshold. |

### Phase 3 — Targeted Learning Module

Every `READY` or `GAP` node can start a learning module. The module should not be a static lesson. It should be an adaptive loop connected to the student's live evidence stream.

**Module flow:**

1. **Framing** — What the concept is and why it matters.
2. **Diagnose** — Probe the specific sub-gap inside the concept.
3. **Explain** — Generate native-language explanation with local analogy.
4. **Elaborate** — Practice through examples, canvas work, and visual explanation.
5. **Evaluate** — Micro-quiz, canvas answer, or short response.
6. **Update / Backtrack** — Update mastery or move into prerequisite sub-session.

### Phase 4 — Adaptive Course Loop Using 5E STEAM + Backtracking

WICARA's main instructional loop follows the **5E STEAM model**:

| Stage | Role in WICARA | Example |
|---|---|---|
| **Engage** | Introduce the concept with local context or a real-world problem. | Market price changes, scooter speed, crop yield, mobile data usage. |
| **Explore** | Let the student interact with examples before formal explanation. | Student predicts a pattern or tries a small canvas problem. |
| **Explain** | Tutor explains the concept in the student's language. | OpenRouter generates a Bahasa Indonesia explanation with a local analogy. |
| **Elaborate** | Student applies the concept in a new but related context. | Practice question, visual exploration, Manim animation. |
| **Evaluate** | Check understanding and update mastery. | Micro-quiz, canvas solution, short essay, or mixed input. |

The loop includes **Dynamic Prerequisite Backtracking**. If Evaluate shows that the student is not failing the current concept but rather a deeper prerequisite, WICARA moves down the graph temporarily.

### Phase 5 — Manim Animation + Voiceover

Manim is a core differentiator because WICARA does not depend only on pre-recorded video.

**Why Manim:**

- It generates animations from Python code.
- Templates can be parameterized by concept, analogy, language, and numerical example.
- Visuals can be reused with different TTS audio.
- Output is compressed MP4 suitable for low bandwidth.

**Example Manim template library:**

| Template | Concept Coverage |
|---|---|
| `FunctionMachineScene` | Functions, domain, range, input-output. |
| `DerivativeSlopeScene` | Derivatives, tangent lines, rate of change. |
| `LimitsApproachScene` | Limits, continuity, asymptotes. |
| `QuadraticParabolaScene` | Quadratic functions, roots, vertex. |
| `LinearGraphScene` | Linear equations, slope, intercept. |
| `ExponentialGrowthScene` | Exponents, compound growth, exponential functions. |
| `RatioProportionScene` | Ratios, proportions, scaling. |
| `StatisticsDistributionScene` | Mean, median, mode, distribution. |

**Render pipeline:**

1. Explanation Engine selects template and parameters.
2. Celery queues a Manim render job.
3. Manim produces raw MP4.
4. Voiceover script is generated from explanation text.
5. Google Cloud TTS produces language-specific audio.
6. FFmpeg merges audio and video.
7. Final media is compressed and cached.
8. Flutter client receives `READY` status and displays video inline.

### Phase 6 — Daily Evaluation Using Ebbinghaus Forgetting Curve

Daily Evaluation is based on spaced repetition and the **Ebbinghaus forgetting curve model**. It is not random review.

**Question selection algorithm:**

- Candidate pool: all `MASTERED` or recently improved nodes from the last 30 days.
- Priority weight: `time_since_last_review × (1 - mastery_score) × concept_importance`.
- Nodes approaching forgetting threshold are marked `REVIEW_DUE`.
- Questions mix quick multiple-choice and deeper short-answer/canvas tasks.

**Adaptive canvas behavior:**

Daily review can also use canvas. For math and science, the student may solve a short problem on canvas instead of typing. The system can grade the final answer and inspect the intermediate steps.

### Phase 7 — Post-Test and Node Unlock

After a student passes verification, WICARA gives a short post-test to confirm durable mastery.

**Post-test behavior:**

- 3–5 questions on the concept.
- Slightly harder than the verification check.
- Can include MC, typed answer, canvas solution, or mixed mode.
- Pass threshold: recommended 70%.
- On pass: node becomes `MASTERED`.
- On fail: node remains `IN_PROGRESS`; WICARA offers review, alternate explanation, or prerequisite backtracking.

After mastery changes, the graph propagation service checks:

- dependent nodes in the same subject,
- cross-subject edges,
- nodes previously locked but now ready,
- and daily review scheduling.

---

## 6. Input, Canvas, and Partial-Work Intelligence

### 6.1 Input Evidence Model

Every student action becomes evidence. Evidence is not immediately assumed to be an answer; it may be a question, clarification, partial attempt, note, or off-topic switch.

| Evidence Type | Stored Data | Used By |
|---|---|---|
| Text message | raw text, language, timestamp | Intent Parser, Tutor Chat, Assessment Engine |
| Multiple-choice answer | option key, question id, timestamp | Rule-based grader |
| Short answer | text answer, rubric, concept id | LLM grader |
| Uploaded image | file, OCR text, detected regions | OCR Engine, Target Concept Detector |
| Canvas stroke event | stroke points, color, width, eraser events, order | Canvas Parser |
| Canvas snapshot | rendered image at submit/checkpoint time | OCR, LLM visual inspection, feedback generation |
| Annotation link | relation between chat/image/canvas area | Context Checker |

### 6.2 Canvas Parser Scope

The MVP does not need perfect handwriting recognition. The goal is to capture enough evidence to help the adaptive tutor respond intelligently.

The Canvas Parser should:

- store vector strokes,
- preserve stroke order,
- periodically render snapshots,
- run OCR when possible,
- detect obvious math symbols and layout patterns,
- compare canvas work with expected solution steps when a rubric exists,
- and pass the snapshot plus context to the LLM when symbolic parsing is uncertain.

### 6.3 Partial-Work Detection

Canvas is valuable because it reveals process, not only final answers.

WICARA should detect cases such as:

| Partial Work Pattern | Tutor Response |
|---|---|
| Correct first step, wrong second step | "Your setup is correct, but the exponent rule changes here." |
| Student copied the problem incorrectly | Ask the student to re-check the copied value before grading. |
| Blank canvas for too long | Offer a small hint or ask a clarifying question. |
| Student draws a graph with wrong axis interpretation | Trigger graph-reading micro-explanation. |
| Student repeatedly makes multiplication mistakes | Open temporary multiplication sub-session. |
| Student writes a correct final answer but unclear process | Give credit but ask for one reasoning step if needed. |
| Student uses a valid alternate method | Accept answer and update mastery with explanation. |

This is a major differentiator: WICARA watches the student's reasoning process, similar to a human tutor looking at scratch paper.

---

## 7. Backend Design in FastAPI

### 7.1 Core SQLAlchemy Models

```python
class Concept(Base):
    __tablename__ = "knowledge_concepts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name_default: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(String(32))  # math, physics, chemistry, biology
    difficulty_level: Mapped[int] = mapped_column(Integer)
    curriculum_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConceptTranslation(Base):
    __tablename__ = "concept_translations"
    __table_args__ = (UniqueConstraint("concept_id", "language"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_concepts.id"))
    language: Mapped[str] = mapped_column(String(8))  # id, en, vi, tl, ms
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)


class PrerequisiteEdge(Base):
    __tablename__ = "concept_edges"
    __table_args__ = (UniqueConstraint("concept_id", "prerequisite_id", "edge_type"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_concepts.id"))
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_concepts.id"))
    edge_type: Mapped[str] = mapped_column(String(32), default="prerequisite")
    strength: Mapped[float] = mapped_column(Float, default=1.0)


class LearnerConceptState(Base):
    __tablename__ = "learner_concept_states"
    __table_args__ = (UniqueConstraint("learner_profile_id", "concept_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    learner_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"))
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_concepts.id"))
    state: Mapped[str] = mapped_column(String(32))  # MASTERED, GAP, READY, LOCKED, IN_PROGRESS, REVIEW_DUE
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    learner_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"))
    parent_session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("learning_sessions.id"))
    target_concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("knowledge_concepts.id"))
    session_type: Mapped[str] = mapped_column(String(32))  # pretest, module, temporary_subsession, daily_eval, posttest
    status: Mapped[str] = mapped_column(String(32))  # active, paused, completed, abandoned
    current_stage: Mapped[str | None] = mapped_column(String(32))  # engage, explore, explain, elaborate, evaluate
    context: Mapped[dict] = mapped_column(JSONB, default=dict)


class InputEvent(Base):
    __tablename__ = "input_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_sessions.id"))
    event_type: Mapped[str] = mapped_column(String(32))  # CHAT_TEXT, CANVAS_SNAPSHOT, MC_ANSWER, MIXED
    raw_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    parser_output: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CanvasSnapshot(Base):
    __tablename__ = "canvas_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_sessions.id"))
    preview_asset_url: Mapped[str | None] = mapped_column(Text)
    strokes_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    parser_output: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_sessions.id"))
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_concepts.id"))
    assessment_type: Mapped[str] = mapped_column(String(32))  # pretest, probe, verification, posttest, daily_eval
    answer: Mapped[dict] = mapped_column(JSONB, default=dict)
    verdict: Mapped[str] = mapped_column(String(32))  # correct, partial, incorrect, unclear
    score: Mapped[float] = mapped_column(Float, default=0.0)
    misconception_type: Mapped[str | None] = mapped_column(String(64))
    feedback: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
```

### 7.2 Main API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/onboarding/complete` | Create profile, bind curriculum, initialize graph states. |
| `POST /api/pretest/start` | Start KST-inspired adaptive pretest. |
| `GET /api/pretest/{session_id}/next-question` | Get next adaptive question. |
| `POST /api/pretest/{session_id}/submit` | Submit MC, text, canvas, image, or mixed answer. |
| `POST /api/pretest/{session_id}/finalize` | Compute initial knowledge state and learning map. |
| `GET /api/students/{student_id}/learning-map` | Return Educational Knowledge Graph with student-specific node states. |
| `POST /api/sessions/start` | Start a learning module for a concept. |
| `POST /api/sessions/{session_id}/input` | Submit any input evidence: chat, image, canvas, MC, mixed. |
| `GET /api/sessions/{session_id}/next-action` | Return next tutor action from Session Router. |
| `POST /api/sessions/{session_id}/chat` | Stream context-aware tutor response. |
| `POST /api/sessions/{session_id}/canvas-snapshot` | Upload or save rendered canvas evidence. |
| `POST /api/assessments/{session_id}/submit` | Evaluate pretest, probe, practice, verification, post-test, or daily evaluation answer. |
| `POST /api/animation/queue` | Queue Manim + TTS generation. |
| `GET /api/animation/status/{job_id}` | Check media generation status. |
| `POST /api/evaluation/daily/generate` | Generate spaced repetition review using forgetting curve priority. |
| `POST /api/evaluation/daily/submit` | Evaluate daily review and update mastery. |
| `GET /api/reports/{session_id}` | Return learning report and recommendations. |

---

## 8. Adaptive Algorithms

### 8.1 KST-Inspired Adaptive Pretest

```text
Input: subject graph, student profile, curriculum binding
1. Select mid-level concept nodes based on grade and curriculum.
2. Ask a question for one selected node.
3. If correct, infer nearby prerequisites as likely mastered with confidence discount.
4. If incorrect, move downward to prerequisite nodes.
5. Continue until the system has enough confidence over major graph regions.
6. Mark nodes as MASTERED, GAP, or UNKNOWN.
7. Generate initial learning map.
```

### 8.2 Local Prerequisite Probe

```text
Input: target concept, mastery state, prerequisite graph
1. Fetch nearest prerequisite nodes within depth 1–2.
2. Remove nodes already mastered with high confidence.
3. Select 2–3 high-importance probe questions.
4. Accept answer through MC, text, canvas, image, or mixed input.
5. Evaluate evidence.
6. Classify path:
   - no gap: go directly to target concept
   - light gap: repair prerequisite first, then target
   - large gap: build scaffolded prerequisite path
```

### 8.3 Session Router

```text
Input: latest StudentInput, active session, context, graph state
1. Parse intent and concept.
2. Check whether input belongs to active concept.
3. If same topic: answer inline or continue current stage.
4. If clarification: generate micro-explanation without changing path.
5. If prerequisite gap: open temporary sub-session.
6. If new topic: save current progress and start new sub-session.
7. If unclear: ask a smaller clarifying question.
```

### 8.4 Error Analyzer

| Error Type | Meaning | Action |
|---|---|---|
| Surface misconception | Student is close but has a small misunderstanding. | Regenerate explanation with easier analogy. |
| Missing prerequisite | Student lacks a deeper concept. | Dynamic Prerequisite Backtracking. |
| Ambiguous evidence | Work is unclear or incomplete. | Ask clarifying question or smaller task. |
| Off-topic switch | Student intentionally changes topic. | Save parent progress and open new sub-session. |
| Assessment gaming | Student asks for direct quiz answer. | Provide conceptual guidance but not the answer. |

### 8.5 Graph Traversal Operations

| Operation | Algorithm / Method |
|---|---|
| Prerequisite path | Dijkstra on weighted prerequisite edges, where stronger prerequisites are lower-cost paths. |
| Unlock propagation | BFS upward from newly mastered nodes. |
| Cross-subject unlock | Query cross-subject edges after any mastery update. |
| Review scheduling | Forgetting-curve priority using recency, mastery score, attempts, and concept importance. |
| Dynamic backtracking | Traverse downward from failed concept to nearest low-mastery prerequisite. |

---

## 9. Assessment Engine Detail

The Assessment Engine is shared across adaptive pretest, local probes, practice, verification, post-test, and daily evaluation.

### 9.1 Supported Answer Modes

| Mode | Grading Approach |
|---|---|
| Multiple choice | Rule-based exact match. |
| Typed short answer | LLM evaluates semantic correctness using rubric. |
| Canvas answer | Canvas Parser + OCR + LLM/rubric evaluation. |
| Image answer | OCR + image context + rubric evaluation. |
| Mixed input | Combines typed answer, canvas, image, and selected option as one evidence package. |

### 9.2 LLM Grading Output

```json
{
  "verdict": "CORRECT | PARTIAL | INCORRECT | UNCLEAR",
  "score": 0.0,
  "misconception_type": "string",
  "prerequisite_gap_candidate": "concept_id or null",
  "feedback": "student-facing feedback in the student's language"
}
```

### 9.3 Mastery Score Formula

```text
mastery = weighted_average(
  pretest_or_probe_score × 0.20,
  in_module_practice    × 0.20,
  canvas_evidence       × 0.15,
  verification_score    × 0.25,
  posttest_score        × 0.20
) × recency_decay_factor
```

The exact weights can be tuned, but canvas evidence should remain part of the formula because WICARA's product advantage is understanding the student's reasoning process, not only the final answer.

### 9.4 Recency Decay

```text
recency_decay_factor = f(days_since_last_review, mastery_confidence)
```

The implementation can start simple in MVP, then become more precise. The important technical point is that the Ebbinghaus forgetting curve model informs when a mastered node becomes review-worthy again.

---

## 10. Frontend Screen Map

The frontend should make WICARA feel like one continuous adaptive workspace.

| Screen | What It Shows | Key Interactions |
|---|---|---|
| **Home** | Today's learning queue, daily evaluation card, current streak, continue CTA. | Continue active session, start daily evaluation, open report. |
| **Adaptive Workspace** | Chat, always-on canvas, adaptive question cards, explanation cards, generated media, progress state. | Type, draw, upload photo, answer MC/text/canvas questions, ask tutor, receive streamed response. |
| **Knowledge Map** | Interactive Educational Knowledge Graph with node states and cross-subject edge toggle. | Zoom/pan, tap node, inspect prerequisites, start lesson. |
| **Video Gallery** | Generated Manim videos organized by subject and concept. | Replay video, switch voiceover language if available. |
| **Learning Report** | Pretest vs post-test comparison, fixed gaps, remaining gaps, next recommendation. | Review progress and continue. |

### Adaptive Workspace Behavior

The Adaptive Workspace replaces the idea of a simple chat screen. It is the central place where learning happens.

Required behavior:

- Chat is always available.
- Canvas is always available or one tap away.
- A question card can request MC, text, canvas, image, or mixed answer.
- Student can submit the canvas as the main answer.
- Student can attach canvas work to a typed answer.
- Canvas strokes autosave.
- Canvas snapshots are taken at submission and at important checkpoints.
- Tutor can reference the canvas directly in feedback.
- If the student gets stuck, WICARA can offer hints based on partial work.
- If the student switches topic, the current session is saved instead of lost.

### Scope Guardrail

The student can ask flexible learning-related questions, but WICARA is not a completely unrestricted chatbot. If a request is unrelated to the current subject or learning context, the Session Router should either create a new learning sub-session, ask for clarification, or politely keep the student within the tutoring scope.

---

## 11. Module Catalog

### 11.1 Core MVP Modules

| # | Module | Function |
|---|---|---|
| 1 | Onboarding Engine | Profile, country, language, grade, subject activation, curriculum binding. |
| 2 | Adaptive Pretest Engine | KST-inspired placement assessment across the graph. |
| 3 | Educational Knowledge Graph (EKG) | Two-level graph: subject graphs + cross-subject edges. |
| 4 | Graph of Graphs Engine | Propagates learning across subjects through cross-subject prerequisite edges. |
| 5 | Always-On Input Engine | Captures text, image, screenshot, canvas, MC, and mixed input. |
| 6 | Canvas Parser | Reads canvas strokes, snapshots, partial work, and step order. |
| 7 | OCR Engine | Extracts text from photos, screenshots, and canvas snapshots. |
| 8 | Intent Parser | Detects target concept, question type, clarification, topic switch, or answer submission. |
| 9 | Session Router | Routes input into active session, inline response, clarification, temporary sub-session, or new sub-session. |
| 10 | Context Checker | Decides whether new input belongs to the active concept or a different concept. |
| 11 | Target Concept Detector | Maps student input to curriculum graph nodes. |
| 12 | Local Prerequisite Probe | Checks nearest prerequisite nodes before teaching the target node. |
| 13 | Mastery State Engine | Updates mastery score, confidence, attempts, evidence, and node state. |
| 14 | Path Engine | Chooses the next concept node based on graph and mastery state. |
| 15 | 5E STEAM Course Loop Engine | Runs Engage, Explore, Explain, Elaborate, Evaluate. |
| 16 | Error Analyzer | Classifies mistakes and chooses regenerate, clarify, or backtrack. |
| 17 | Dynamic Prerequisite Backtracking Engine | Moves to deeper prerequisite nodes when needed. |
| 18 | Temporary Sub-session Engine | Creates child sessions and resumes parent sessions. |
| 19 | Localized Explanation Engine | Native-language explanation with cultural analogies. |
| 20 | Assessment Engine | MC, short answer, canvas, image, and mixed answer evaluation. |
| 21 | Verification Engine | Checks understanding before post-test. |
| 22 | Post-Test Engine | Confirms durable mastery and triggers node unlock. |
| 23 | Manim Animation Engine | Generates parameterized math visuals. |
| 24 | Voiceover Engine | Generates per-language TTS audio. |
| 25 | Media Processing Engine | Uses FFmpeg to merge and compress generated media. |

### 11.2 Supporting Modules

| # | Module | Function |
|---|---|---|
| 26 | Daily Evaluation Engine | Spaced repetition and Ebbinghaus forgetting-curve review. |
| 27 | Multilingual & Cultural Context System | Local analogy bank, language detection, native prompt templates. |
| 28 | Session & State Persistence | Resume-anywhere sessions and parent/child session history. |
| 29 | LLM Cost & Performance Control | Redis caching, prompt versioning, token logging, retry limits. |
| 30 | Progress & Mastery Dashboard | Learning queue, streak, mastery progress, review status. |
| 31 | Cross-Subject Unlock Notification | Shows when a mastered node unlocks another subject. |
| 32 | Admin Dashboard | Internal concept graph, prompt, curriculum, and content management. |
| 33 | Observability | Health checks for FastAPI, PostgreSQL, Redis, Celery, LLM, OCR, and media generation. |

---

## 12. Knowledge Graph Technical Design

### 12.1 PostgreSQL Schema Concept

The EKG can be implemented in PostgreSQL first using adjacency-list tables. This keeps the MVP simple and aligned with SQLAlchemy. Neo4j can be added later if graph traversal requirements become more complex.

```sql
concepts (
  id UUID PRIMARY KEY,
  name_default TEXT,
  subject TEXT,
  difficulty_level INT,
  curriculum_code TEXT,
  created_at TIMESTAMP
)

concept_translations (
  concept_id UUID REFERENCES concepts(id),
  language TEXT,
  name TEXT,
  description TEXT,
  PRIMARY KEY (concept_id, language)
)

prerequisite_edges (
  concept_id UUID REFERENCES concepts(id),
  prerequisite_id UUID REFERENCES concepts(id),
  strength FLOAT,
  PRIMARY KEY (concept_id, prerequisite_id)
)

cross_subject_edges (
  source_concept_id UUID REFERENCES concepts(id),
  target_concept_id UUID REFERENCES concepts(id),
  source_subject TEXT,
  target_subject TEXT,
  edge_type TEXT,
  confidence FLOAT
)

student_concept_mastery (
  student_id UUID,
  concept_id UUID REFERENCES concepts(id),
  state TEXT,
  mastery_score FLOAT,
  confidence FLOAT,
  last_reviewed_at TIMESTAMP,
  attempts INT,
  PRIMARY KEY (student_id, concept_id)
)
```

### 12.2 Graph Propagation Rules

After every assessment, canvas evaluation, sub-session completion, post-test, or daily review, WICARA should run graph propagation.

Rules:

1. If a concept becomes `MASTERED`, check dependent nodes.
2. If all prerequisites of a dependent node are mastered, mark it `READY`.
3. If a concept's mastery decays below threshold, mark it `REVIEW_DUE` or `GAP` depending on severity.
4. If a cross-subject edge is enabled, check target concept prerequisites.
5. If a child sub-session improves a prerequisite, resume parent session and recalculate path.

---

## 13. Key Differentiators vs Existing Platforms

| Feature | Khan Academy | ALEKS | Ruangguru | **WICARA** |
|---|---|---|---|---|
| Language | English + translations | English-first | Indonesian-first | 5 ASEAN languages, native-generated |
| Prerequisite diagnosis | Partial | Strong KST | Limited | Strong KST-inspired probing + EKG |
| Educational Knowledge Graph | Limited | Knowledge-state model | Limited | Explicit EKG with per-student mastery state |
| Cross-subject graph | No | No | No | Graph of Graphs |
| Always-on canvas | No | No | Limited | Canvas is a diagnostic input source |
| Partial-work understanding | Limited | Limited | Limited | Inspects intermediate reasoning, not only final answer |
| Culturally grounded analogies | Limited | No | Some local content | Per-language local analogy bank |
| Math animations | Pre-recorded | Static / limited | Pre-recorded | Manim-generated, parameterized |
| Voiceover language toggle | Limited | No | Indonesian | Per-language TTS, swappable |
| Daily spaced repetition | Partial | Limited | Limited | Ebbinghaus-modeled daily evaluation |
| Works for low-bandwidth ASEAN context | Partial | No | Partial | Designed for mobile-first low-bandwidth usage |

---

## 14. What WICARA Is Not Building

WICARA is not:

- a generic content library,
- a live tutoring marketplace,
- a full school LMS,
- a perfect handwriting OCR engine in MVP,
- an offline-first product in MVP,
- or an unrestricted general chatbot.

WICARA is building a **curriculum-aware adaptive tutoring engine** that can diagnose, teach, backtrack, generate media, review over time, and update mastery continuously.

---

## 15. Why This Wins

WICARA's innovation is the integration of multiple systems that are usually separate:

1. **Prerequisite-first diagnosis** — the tutor finds the actual missing concept before teaching.
2. **Knowledge Space Theory-inspired pretest** — the system estimates knowledge state efficiently instead of using a fixed exam.
3. **Educational Knowledge Graph** — every concept is part of a graph with prerequisites, mastery state, and unlock logic.
4. **Graph of Graphs** — mastery can propagate across Math, Physics, Chemistry, and Biology.
5. **Always-on Chat + Canvas** — students can ask, draw, upload, and answer naturally throughout the session.
6. **Partial-work intelligence** — the system can respond to the student's process, not only the final answer.
7. **5E STEAM learning loop** — explanations are embedded inside a structured pedagogy.
8. **Dynamic Prerequisite Backtracking** — the tutor can temporarily go easier, fix the root gap, then return.
9. **Manim + TTS media generation** — precise, language-swappable, low-bandwidth visual learning assets.
10. **Ebbinghaus-modeled daily evaluation** — WICARA supports retention and review, not only one-time learning.
11. **FastAPI-ready implementation** — the architecture matches the team's actual backend stack while still supporting async jobs through Celery, Redis, and ASGI.

The result is a product that behaves less like a chatbot and more like a human tutor watching the student's reasoning, identifying the missing prerequisite, teaching in the student's language, and remembering what the student has mastered over time.
