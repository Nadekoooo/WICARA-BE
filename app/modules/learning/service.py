from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentSession,
    LearnerConceptState,
    LearningGoal,
    LearningTrack,
    TrackModule,
)
from app.modules.learning.schemas import (
    AssessmentOptionRead,
    AssessmentQuestionRead,
    DailyEvaluationAnswerResponse,
    DailyEvaluationResponse,
    KnowledgeStateResponse,
    LearningGoalCreateResponse,
    LearningGoalRead,
    PretestReadResponse,
    SubmitAnswerResponse,
    TrackListResponse,
    TrackModuleRead,
    TrackRead,
)


PRETEST_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Prerequisite probe",
        "prompt": (
            "A student wants to learn derivatives, but their graph approaches y = 3 "
            "as x gets closer to 2 from both sides. What should WICARA check first?"
        ),
        "helper": "Choose the prerequisite signal that best guides the first learning path.",
        "concept_hints": ["intuitive_limits", "limit", "bilangan_rasional"],
        "correct": "B",
        "options": [
            ("A", "Start derivative rules immediately"),
            ("B", "Check whether the learner understands limits from graphs"),
            ("C", "Skip prerequisite diagnosis and generate a video"),
            ("D", "Mark calculus as mastered from one topic request"),
        ],
    },
    {
        "topic": "Learning path diagnosis",
        "prompt": (
            "A learner can apply a formula after seeing it, but cannot explain why "
            "the formula works. What should the adaptive track do next?"
        ),
        "helper": "Pick the action that keeps the path prerequisite-first.",
        "concept_hints": ["functions", "bilangan_bulat"],
        "correct": "C",
        "options": [
            ("A", "Increase difficulty because the formula was copied correctly"),
            ("B", "Skip explanation and only give more multiple-choice questions"),
            ("C", "Add a short concept-building module before harder practice"),
            ("D", "Remove the concept from the learning map"),
        ],
    },
]


DAILY_REVIEW_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Spaced review",
        "prompt": (
            "You answered a concept correctly today after struggling yesterday. "
            "What is the best next step?"
        ),
        "helper": "Use memory strength to decide.",
        "concept_hints": ["bilangan_rasional", "intuitive_limits"],
        "correct": "A",
        "options": [
            ("A", "Review it again after a short delay"),
            ("B", "Mark it mastered forever immediately"),
            ("C", "Remove it from all future practice"),
            ("D", "Only study brand new concepts now"),
        ],
    },
    {
        "topic": "Application",
        "prompt": (
            "A student can solve derivative rules but misses word problems. "
            "What should they review next?"
        ),
        "helper": "Pick the next learning action.",
        "concept_hints": ["applications_derivatives", "functions", "bilangan_bulat"],
        "correct": "B",
        "options": [
            ("A", "Repeat only memorized derivative formulas"),
            ("B", "Practice translating situations into equations"),
            ("C", "Skip application questions until later"),
            ("D", "Review unrelated facts without checking the gap"),
        ],
    },
    {
        "topic": "Concept decay",
        "prompt": (
            "A learner mastered a prerequisite last week, but confidence is dropping. "
            "How should WICARA schedule it?"
        ),
        "helper": "Choose the retention-oriented action.",
        "concept_hints": ["functions", "bilangan_rasional"],
        "correct": "D",
        "options": [
            ("A", "Ignore it because it was once mastered"),
            ("B", "Reset the full track to the beginning"),
            ("C", "Only show new concepts today"),
            ("D", "Add a short review question before the next module"),
        ],
    },
]


def create_learning_goal(
    session: Session,
    *,
    user: UserAccount,
    raw_topic: str,
    subject_code: str | None,
) -> LearningGoalCreateResponse:
    ensure_curriculum_seeded(session)
    subject = _resolve_subject(session, subject_code=subject_code, user=user)
    concept = _pick_concept(session, subject=subject, raw_topic=raw_topic)

    normalized_topic = _normalize_topic(raw_topic)
    goal = LearningGoal(
        user_id=user.id,
        subject_id=subject.id,
        target_concept_id=concept.id if concept else None,
        raw_topic=raw_topic.strip(),
        normalized_topic=normalized_topic,
        status="pretest_ready",
        metadata_json={"source": "learning_goal_api", "generation": "deterministic_seed"},
    )
    session.add(goal)
    session.flush()

    track = _create_track(session, user=user, goal=goal, subject=subject, concept=concept)
    pretest = _create_assessment_session(
        session,
        user=user,
        learning_goal=goal,
        track=track,
        session_type="pretest",
        title=f"Pretest for {normalized_topic}",
        templates=PRETEST_TEMPLATES,
    )
    session.commit()

    return LearningGoalCreateResponse(
        learning_goal_id=goal.id,
        status=goal.status,
        subject=subject.name,
        subject_code=subject.code,
        pretest_session_id=pretest.id,
        track_id=track.id,
    )


def read_learning_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID,
) -> LearningGoalRead | None:
    goal = session.scalar(
        select(LearningGoal)
        .where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
        .options(selectinload(LearningGoal.track), selectinload(LearningGoal.assessment_sessions))
    )
    if goal is None:
        return None
    subject = session.get(Subject, goal.subject_id)
    pretest = next(
        (item for item in goal.assessment_sessions if item.session_type == "pretest"),
        None,
    )
    return LearningGoalRead(
        id=goal.id,
        raw_topic=goal.raw_topic,
        normalized_topic=goal.normalized_topic,
        status=goal.status,
        subject_code=subject.code if subject else "",
        pretest_session_id=pretest.id if pretest else None,
        track_id=goal.track.id if goal.track else None,
    )


def get_pretest_for_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID,
) -> PretestReadResponse | None:
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.learning_goal_id == learning_goal_id,
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "pretest",
        )
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        return None
    return PretestReadResponse(
        session_id=assessment.id,
        learning_goal_id=learning_goal_id,
        title=assessment.title,
        status=assessment.status,
        questions=[question_to_schema(question) for question in assessment.questions],
    )


def submit_answer(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
    explanation: str = "",
    used_canvas: bool = False,
) -> tuple[AssessmentAttempt, bool]:
    assessment, question, option = _resolve_submission_targets(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
    )
    attempt = AssessmentAttempt(
        session_id=assessment.id,
        question_id=question.id,
        selected_option_id=option.id,
        confidence=confidence,
        explanation_text=explanation.strip(),
        used_canvas=used_canvas,
        score=1.0 if option.is_correct else 0.0,
        evaluated_result={
            "verdict": "CORRECT" if option.is_correct else "INCORRECT",
            "grading": "deterministic_seed",
        },
    )
    session.add(attempt)
    _update_mastery(session, user=user, question=question, is_correct=option.is_correct)
    session.commit()
    session.refresh(attempt)
    return attempt, option.is_correct


def submit_answer_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
) -> SubmitAnswerResponse:
    attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
    )
    return SubmitAnswerResponse(attempt_id=attempt.id, is_correct=is_correct)


def submit_reasoning_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
    explanation: str,
    used_canvas: bool,
) -> KnowledgeStateResponse:
    _attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
        explanation=explanation,
        used_canvas=used_canvas,
    )
    assessment = session.get(AssessmentSession, assessment_session_id)
    if assessment:
        assessment.status = "completed"
        assessment.completed_at = datetime.now(UTC)
        if assessment.learning_goal_id:
            goal = session.get(LearningGoal, assessment.learning_goal_id)
            if goal:
                goal.status = "track_ready"
        if assessment.track_id:
            track = session.get(LearningTrack, assessment.track_id)
            if track:
                track.status = "active"
                track.progress_percent = 8
        session.commit()

    if is_correct:
        return KnowledgeStateResponse(
            skill="Ready concept: prerequisite reading",
            gap_label="READY",
            message=(
                "Your pretest evidence is enough to start the generated path. "
                "WICARA will still keep early prerequisites in review."
            ),
            path_title="Personalized path generated",
            path_meta="20-28 min | 3 modules",
            path_description="Start with the detected prerequisite, then move into the requested topic.",
        )
    return KnowledgeStateResponse(
        skill="Missing prerequisite: concept diagnosis",
        gap_label="GAP",
        message=(
            "The gap looks like jumping to the target topic before confirming the "
            "prerequisite signal. The path will repair that first."
        ),
        path_title="Prerequisite-first path generated",
        path_meta="18-24 min | 3 modules",
        path_description="Review the missing foundation, then return to your original learning goal.",
    )


def list_tracks(session: Session, *, user: UserAccount) -> TrackListResponse:
    tracks = list(
        session.scalars(
            select(LearningTrack)
            .where(LearningTrack.user_id == user.id)
            .options(selectinload(LearningTrack.modules))
            .order_by(LearningTrack.created_at.desc())
        )
    )
    return TrackListResponse(items=[track_to_schema(track) for track in tracks])


def get_or_create_daily_evaluation(
    session: Session,
    *,
    user: UserAccount,
) -> DailyEvaluationResponse:
    ensure_curriculum_seeded(session)
    today = datetime.now(UTC).date().isoformat()
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "daily_evaluation",
            AssessmentSession.metadata_json["review_date"].as_string() == today,
        )
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        assessment = _create_assessment_session(
            session,
            user=user,
            learning_goal=None,
            track=None,
            session_type="daily_evaluation",
            title="Daily Evaluation",
            templates=DAILY_REVIEW_TEMPLATES,
            metadata={"review_date": today, "policy": "spaced_repetition_mvp"},
        )
        session.commit()
        assessment = session.scalar(
            select(AssessmentSession)
            .where(AssessmentSession.id == assessment.id)
            .options(
                selectinload(AssessmentSession.questions).selectinload(
                    AssessmentQuestion.options
                )
            )
        )
    assert assessment is not None
    return DailyEvaluationResponse(
        session_id=assessment.id,
        title=assessment.title,
        status=assessment.status,
        review_policy={
            "strategy": "spaced_repetition_mvp",
            "basis": "due concepts first, seeded review templates when no due concepts exist",
        },
        questions=[question_to_schema(question) for question in assessment.questions],
    )


def submit_daily_answer_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
) -> DailyEvaluationAnswerResponse:
    attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
    )
    return DailyEvaluationAnswerResponse(
        attempt_id=attempt.id,
        is_correct=is_correct,
        next_review_label="Review tomorrow" if not is_correct else "Review in 3 days",
        mastery_delta=0.08 if is_correct else -0.04,
    )


def ensure_curriculum_seeded(session: Session) -> None:
    if session.scalar(select(Subject.id).limit(1)) is None:
        seed_curriculum(session, commit=False)
        session.flush()


def question_to_schema(question: AssessmentQuestion) -> AssessmentQuestionRead:
    return AssessmentQuestionRead(
        id=str(question.id),
        step_label=question.step_label,
        topic=question.topic,
        prompt=question.prompt,
        helper=question.helper_text,
        options=[
            AssessmentOptionRead(id=str(option.id), label=option.label, text=option.text)
            for option in question.options
        ],
    )


def track_to_schema(track: LearningTrack) -> TrackRead:
    return TrackRead(
        id=track.id,
        learning_goal_id=track.learning_goal_id,
        title=track.title,
        subtitle=track.subtitle,
        status=track.status,
        progress_percent=track.progress_percent,
        modules=[
            TrackModuleRead(
                id=module.id,
                title=module.title,
                description=module.description,
                estimated_minutes=module.estimated_minutes,
                difficulty_label=module.difficulty_label,
                sort_order=module.sort_order,
                status=module.status,
            )
            for module in track.modules
        ],
    )


def _create_assessment_session(
    session: Session,
    *,
    user: UserAccount,
    learning_goal: LearningGoal | None,
    track: LearningTrack | None,
    session_type: str,
    title: str,
    templates: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> AssessmentSession:
    assessment = AssessmentSession(
        user_id=user.id,
        learning_goal_id=learning_goal.id if learning_goal else None,
        track_id=track.id if track else None,
        session_type=session_type,
        title=title,
        status="active",
        metadata_json=metadata or {"generation": "deterministic_seed"},
    )
    session.add(assessment)
    session.flush()

    for index, template in enumerate(templates, start=1):
        concept = _find_concept_by_hints(session, template["concept_hints"])
        question = AssessmentQuestion(
            session_id=assessment.id,
            concept_id=concept.id if concept else None,
            step_label=f"{index} / {len(templates)}"
            if session_type == "pretest"
            else "Daily Evals",
            topic=str(template["topic"]),
            prompt=str(template["prompt"]),
            helper_text=str(template["helper"]),
            difficulty_label="Medium",
            sort_order=index,
            metadata_json={
                "seed_source": f"{session_type}_template",
                "correct_option_key": template["correct"],
            },
        )
        session.add(question)
        session.flush()

        for option_index, (key, text) in enumerate(template["options"], start=1):
            session.add(
                AssessmentOption(
                    question_id=question.id,
                    option_key=key,
                    label=key,
                    text=text,
                    is_correct=key == template["correct"],
                    sort_order=option_index,
                )
            )
    session.flush()
    return assessment


def _create_track(
    session: Session,
    *,
    user: UserAccount,
    goal: LearningGoal,
    subject: Subject,
    concept: KnowledgeConcept | None,
) -> LearningTrack:
    title = f"{goal.normalized_topic} path"
    track = LearningTrack(
        user_id=user.id,
        learning_goal_id=goal.id,
        title=title,
        subtitle=f"{subject.name} | prerequisite-first adaptive path",
        status="pretest",
        progress_percent=0,
        metadata_json={"generation": "deterministic_seed"},
    )
    session.add(track)
    session.flush()

    modules = _module_templates(goal.normalized_topic, concept)
    for index, module in enumerate(modules, start=1):
        session.add(
            TrackModule(
                track_id=track.id,
                concept_id=concept.id if concept and index == 2 else None,
                title=module["title"],
                description=module["description"],
                estimated_minutes=module["minutes"],
                difficulty_label=module["difficulty"],
                sort_order=index,
                status="ready" if index == 1 else "locked",
                metadata_json={"seed_source": "learning_goal_track"},
            )
        )
    session.flush()
    return track


def _module_templates(
    normalized_topic: str,
    concept: KnowledgeConcept | None,
) -> list[dict[str, Any]]:
    target = concept.title if concept else normalized_topic
    return [
        {
            "title": "Prerequisite checkpoint",
            "description": "Repair the foundation detected by the pretest before starting the main topic.",
            "minutes": 8,
            "difficulty": "Easy",
        },
        {
            "title": target,
            "description": f"Learn {normalized_topic} with chat, canvas evidence, and short checks.",
            "minutes": 14,
            "difficulty": "Medium",
        },
        {
            "title": "Application and review",
            "description": "Apply the concept, then schedule it for spaced repetition.",
            "minutes": 10,
            "difficulty": "Medium",
        },
    ]


def _resolve_subject(
    session: Session,
    *,
    subject_code: str | None,
    user: UserAccount,
) -> Subject:
    candidates = []
    if subject_code:
        candidates.append(subject_code)
    profile = user.learner_profile
    if profile:
        candidates.extend(profile.selected_subjects)
    candidates.extend(["matematika", "math"])

    for candidate in candidates:
        normalized = canonical_subject_code(candidate)
        subject = session.scalar(
            select(Subject).where(Subject.code == normalized, Subject.is_active.is_(True))
        )
        if subject is not None:
            return subject

    subject = session.scalar(select(Subject).where(Subject.is_active.is_(True)))
    if subject is None:
        raise ValueError("Curriculum seed is empty.")
    return subject


def _pick_concept(
    session: Session,
    *,
    subject: Subject,
    raw_topic: str,
) -> KnowledgeConcept | None:
    topic = raw_topic.lower()
    concepts = list(
        session.scalars(
            select(KnowledgeConcept)
            .where(KnowledgeConcept.subject_id == subject.id)
            .order_by(KnowledgeConcept.display_order, KnowledgeConcept.title)
        )
    )
    if not concepts:
        return None
    for concept in concepts:
        haystack = f"{concept.code} {concept.title}".lower()
        if any(token in haystack for token in topic.replace("-", " ").split()):
            return concept
    for hint in ("intuitive_limits", "derivative_definition", "km_d_matematika_bilangan_rasional"):
        for concept in concepts:
            if concept.code == hint:
                return concept
    return concepts[0]


def _find_concept_by_hints(
    session: Session,
    hints: list[str],
) -> KnowledgeConcept | None:
    for hint in hints:
        concept = session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == hint))
        if concept is not None:
            return concept
    return session.scalar(select(KnowledgeConcept).order_by(KnowledgeConcept.display_order))


def _resolve_submission_targets(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
) -> tuple[AssessmentSession, AssessmentQuestion, AssessmentOption]:
    assessment = session.scalar(
        select(AssessmentSession)
        .where(AssessmentSession.id == assessment_session_id, AssessmentSession.user_id == user.id)
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        raise LookupError("Assessment session was not found.")

    question = _find_question(assessment.questions, question_id)
    if question is None:
        raise LookupError("Assessment question was not found.")
    option = _find_option(question.options, option_id)
    if option is None:
        raise LookupError("Assessment option was not found.")
    return assessment, question, option


def _find_question(
    questions: list[AssessmentQuestion],
    question_id: str,
) -> AssessmentQuestion | None:
    for question in questions:
        if str(question.id) == question_id:
            return question
    if len(questions) == 1:
        return questions[0]
    return None


def _find_option(
    options: list[AssessmentOption],
    option_id: str,
) -> AssessmentOption | None:
    normalized = option_id.strip()
    for option in options:
        if str(option.id) == normalized or option.option_key == normalized or option.label == normalized:
            return option
    return None


def _update_mastery(
    session: Session,
    *,
    user: UserAccount,
    question: AssessmentQuestion,
    is_correct: bool,
) -> None:
    if question.concept_id is None:
        return
    state = session.scalar(
        select(LearnerConceptState).where(
            LearnerConceptState.user_id == user.id,
            LearnerConceptState.concept_id == question.concept_id,
        )
    )
    if state is None:
        state = LearnerConceptState(
            user_id=user.id,
            concept_id=question.concept_id,
            status="ready",
            mastery_score=0.0,
            confidence_score=0.0,
            evidence_count=0,
        )
        session.add(state)
    delta = 0.18 if is_correct else -0.12
    mastery_score = state.mastery_score or 0.0
    confidence_score = state.confidence_score or 0.0
    state.mastery_score = max(0.0, min(1.0, mastery_score + delta))
    state.confidence_score = max(
        0.0,
        min(1.0, confidence_score + (0.12 if is_correct else -0.08)),
    )
    state.status = "review_due" if not is_correct else ("mastered" if state.mastery_score >= 0.7 else "ready")
    state.evidence_count = (state.evidence_count or 0) + 1
    state.last_evaluated_at = datetime.now(UTC)
    state.next_review_at = datetime.now(UTC) + (timedelta(days=3) if is_correct else timedelta(days=1))


def _normalize_topic(raw_topic: str) -> str:
    cleaned = " ".join(raw_topic.strip().split())
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "Learning goal"
