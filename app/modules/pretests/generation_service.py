from __future__ import annotations

import asyncio
import json
import os
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.curriculum.models import KnowledgeConcept
from app.modules.ai.client import ai_client
from app.modules.ai.config import get_ai_settings
from app.modules.learning.models import (
    AssessmentOption,
    AssessmentQuestion,
    AssessmentQuestionPack,
    AssessmentSession,
)
from app.modules.pretests.question_validator import QuestionValidator

PACK_PROMPT_VERSION = "adaptive_node_pack_v5_retry_validated"
DEFAULT_PACK_GENERATION_MAX_ATTEMPTS = 4


class AdaptivePretestGenerationService:
    def __init__(self, *, validator: QuestionValidator | None = None) -> None:
        self.validator = validator or QuestionValidator()

    def ensure_pack(
        self,
        session: Session,
        *,
        assessment: AssessmentSession,
        concept: KnowledgeConcept,
        language: str = "id",
    ) -> AssessmentQuestionPack:
        existing = session.scalar(
            select(AssessmentQuestionPack)
            .where(
                AssessmentQuestionPack.session_id == assessment.id,
                AssessmentQuestionPack.concept_id == concept.id,
            )
            .options(
                selectinload(AssessmentQuestionPack.questions).selectinload(
                    AssessmentQuestion.options
                )
            )
        )
        if existing is not None:
            return existing

        generated_pack, generation_metadata = self._generate_pack(
            concept=concept,
            language=language,
        )
        self.validator.validate_pack(concept_code=concept.code, pack=generated_pack)
        pack = AssessmentQuestionPack(
            session_id=assessment.id,
            concept_id=concept.id,
            generation_source=generation_metadata["generation_source"],
            llm_provider=generation_metadata["llm_provider"],
            llm_model=generation_metadata["llm_model"],
            prompt_version=PACK_PROMPT_VERSION,
            status="ready",
        )
        session.add(pack)
        session.flush()

        base_sort_order = int(
            session.scalar(
                select(func.count()).select_from(AssessmentQuestion).where(
                    AssessmentQuestion.session_id == assessment.id
                )
            )
            or 0
        )
        for offset, difficulty in enumerate(("easy", "medium", "hard"), start=1):
            payload = generated_pack[difficulty]
            question = AssessmentQuestion(
                session_id=assessment.id,
                pack_id=pack.id,
                concept_id=concept.id,
                step_label="Adaptive Pretest",
                topic=concept.title,
                prompt=payload["prompt"],
                helper_text=payload.get("helper_text", ""),
                difficulty_label=difficulty,
                sort_order=base_sort_order + offset,
                metadata_json={
                    "source": "adaptive_generated_pack",
                    "concept_code": concept.code,
                    "correct_option_key": _correct_label(payload),
                    "explanation": payload["explanation"],
                },
                generation_source=generation_metadata["generation_source"],
                generation_prompt_version=PACK_PROMPT_VERSION,
                llm_metadata_json=generation_metadata,
                expected_reasoning=payload["expected_reasoning"],
                rubric_json=payload.get("rubric", {}),
            )
            session.add(question)
            session.flush()
            for sort_order, option in enumerate(payload["options"], start=1):
                session.add(
                    AssessmentOption(
                        question_id=question.id,
                        option_key=option["label"],
                        label=option["label"],
                        text=option["text"],
                        is_correct=bool(option["is_correct"]),
                        sort_order=sort_order,
                    )
                )
        session.flush()
        return session.scalar(
            select(AssessmentQuestionPack)
            .where(AssessmentQuestionPack.id == pack.id)
            .options(
                selectinload(AssessmentQuestionPack.questions).selectinload(
                    AssessmentQuestion.options
                )
            )
        ) or pack

    @staticmethod
    def question_for_difficulty(
        pack: AssessmentQuestionPack,
        *,
        difficulty: str,
    ) -> AssessmentQuestion:
        for question in pack.questions:
            if question.difficulty_label.lower() == difficulty:
                return question
        raise LookupError(f"Pack is missing {difficulty} question.")

    @staticmethod
    def pack_state(pack: AssessmentQuestionPack) -> dict[str, object]:
        return {
            "pack_id": str(pack.id),
            "questions": {
                question.difficulty_label.lower(): str(question.id)
                for question in pack.questions
            },
        }

    def _fallback_pack(
        self,
        *,
        concept: KnowledgeConcept,
        language: str,
    ) -> dict[str, dict[str, Any]]:
        title = concept.title
        code = concept.code.lower()
        text = f"{code} {title}".lower()
        if "perkalian" in text or "multiplication" in text or "kali" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Ada 3 kantong. Tiap kantong berisi 2 apel. Berapa apel semuanya?", "6", ["5", "6", "7", "8"], "3 kelompok berisi 2 berarti 2 + 2 + 2 = 6."),
                    ("medium", "Rina punya 4 kotak. Setiap kotak berisi 3 pensil. Berapa pensil semuanya?", "12", ["7", "12", "14", "16"], "4 kelompok berisi 3 berarti 3 + 3 + 3 + 3 = 12."),
                    ("hard", "Sebuah kelas punya 6 meja. Tiap meja dipakai 4 siswa. Jika 2 siswa tidak hadir, berapa siswa yang hadir?", "22", ["20", "22", "24", "26"], "6 x 4 = 24 kursi terisi semula, lalu 24 - 2 = 22."),
                ],
            )
        if "penjumlahan" in text or "addition" in text or "tambah" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Budi punya 5 kelereng lalu mendapat 3 lagi. Berapa kelereng Budi sekarang?", "8", ["6", "8", "9", "10"], "5 + 3 = 8."),
                    ("medium", "Ani membaca 18 halaman pagi hari dan 14 halaman sore hari. Berapa halaman yang ia baca?", "32", ["22", "30", "32", "34"], "18 + 14 = 32."),
                    ("hard", "Toko menjual 27 buku Senin, 36 buku Selasa, dan 18 buku Rabu. Berapa total buku terjual?", "81", ["71", "79", "81", "91"], "27 + 36 + 18 = 81."),
                ],
            )
        if "pengurangan" in text or "subtraction" in text or "kurang" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Ada 9 jeruk. 4 jeruk dimakan. Berapa jeruk tersisa?", "5", ["4", "5", "6", "7"], "9 - 4 = 5."),
                    ("medium", "Dari 35 stiker, 17 diberikan ke teman. Berapa stiker tersisa?", "18", ["16", "18", "20", "22"], "35 - 17 = 18."),
                    ("hard", "Sebuah bus berisi 48 penumpang. Di halte pertama turun 19, di halte kedua naik 7. Berapa penumpang sekarang?", "36", ["29", "34", "36", "40"], "48 - 19 + 7 = 36."),
                ],
            )
        if "derivative" in text or "turunan" in text or "differentiation" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Jika $f(x)=x^2$, berapa $f'(x)$?", "$2x$", ["$x$", "$2x$", "$x^3$", "$2$"], "Gunakan aturan pangkat: turunan $x^2$ adalah $2x$."),
                    ("medium", "Diketahui $f(x)=3x^2-4x+5$. Berapa $f'(x)$?", "$6x-4$", ["$3x-4$", "$6x-4$", "$6x+5$", "$x^2-4$"], "Turunkan tiap suku: $3x^2 \\to 6x$, $-4x \\to -4$, dan konstanta $5 \\to 0$."),
                    ("hard", "Kemiringan garis singgung kurva $f(x)=x^3-2x$ di $x=2$ adalah...", "$10$", ["$6$", "$8$", "$10$", "$12$"], "Kemiringan garis singgung adalah $f'(2)$. Karena $f'(x)=3x^2-2$, maka $f'(2)=12-2=10$."),
                ],
            )
        if "limit" in text or "limits" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Hitung $\\lim_{x\\to 2}(x+3)$.", "$5$", ["$2$", "$3$", "$5$", "$6$"], "Substitusi langsung: $2+3=5$."),
                    ("medium", "Hitung $\\lim_{x\\to 3}(x^2-4)$.", "$5$", ["$3$", "$5$", "$9$", "$13$"], "Substitusi langsung: $3^2-4=9-4=5$."),
                    ("hard", "Hitung $\\lim_{x\\to 2}\\frac{x^2-4}{x-2}$.", "$4$", ["$0$", "$2$", "$4$", "Tidak ada"], "Faktorkan $x^2-4=(x-2)(x+2)$, lalu limit menjadi $x+2$ di $x=2$, hasilnya $4$."),
                ],
            )
        if "linear" in text or "equation" in text or "persamaan" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Selesaikan $x+5=12$.", "$x=7$", ["$x=5$", "$x=7$", "$x=12$", "$x=17$"], "Kurangi kedua sisi dengan 5, jadi $x=7$."),
                    ("medium", "Selesaikan $3x-4=11$.", "$x=5$", ["$x=3$", "$x=4$", "$x=5$", "$x=7$"], "Tambah 4 ke kedua sisi: $3x=15$, maka $x=5$."),
                    ("hard", "Selesaikan $2(x-3)+5=17$.", "$x=9$", ["$x=6$", "$x=7$", "$x=9$", "$x=12$"], "Uraikan: $2x-6+5=17$, jadi $2x-1=17$, $2x=18$, maka $x=9$."),
                ],
            )
        if "fraction" in text or "fractions" in text or "pecahan" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Hitung $\\frac{1}{2}+\\frac{1}{4}$.", "$\\frac{3}{4}$", ["$\\frac{1}{6}$", "$\\frac{2}{6}$", "$\\frac{3}{4}$", "$\\frac{2}{4}$"], "Samakan penyebut: $\\frac{1}{2}=\\frac{2}{4}$, jadi $\\frac{2}{4}+\\frac{1}{4}=\\frac{3}{4}$."),
                    ("medium", "Hitung $\\frac{2}{3}\\times\\frac{3}{5}$, lalu sederhanakan.", "$\\frac{2}{5}$", ["$\\frac{5}{8}$", "$\\frac{2}{5}$", "$\\frac{5}{15}$", "$\\frac{3}{10}$"], "Kalikan pembilang dan penyebut: $\\frac{6}{15}$ lalu sederhanakan menjadi $\\frac{2}{5}$."),
                    ("hard", "Sederhanakan $\\frac{3}{4}+\\frac{2}{3}$.", "$\\frac{17}{12}$", ["$\\frac{5}{7}$", "$\\frac{6}{12}$", "$\\frac{13}{12}$", "$\\frac{17}{12}$"], "Penyebut sama 12: $\\frac{9}{12}+\\frac{8}{12}=\\frac{17}{12}$."),
                ],
            )
        if "matrix" in text or "matriks" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    (
                        "easy",
                        "Diketahui matriks $A=\\begin{bmatrix}2&5\\\\1&3\\end{bmatrix}$. Elemen baris ke-1 kolom ke-2 adalah...",
                        "$5$",
                        ["$1$", "$2$", "$3$", "$5$"],
                        "Baris ke-1 adalah $[2,5]$, dan kolom ke-2 pada baris itu bernilai $5$.",
                    ),
                    (
                        "medium",
                        "Jika $A=\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}$ dan $B=\\begin{bmatrix}5&1\\\\2&6\\end{bmatrix}$, maka $A+B$ adalah...",
                        "$\\begin{bmatrix}6&3\\\\5&10\\end{bmatrix}$",
                        [
                            "$\\begin{bmatrix}6&3\\\\5&10\\end{bmatrix}$",
                            "$\\begin{bmatrix}5&2\\\\6&24\\end{bmatrix}$",
                            "$\\begin{bmatrix}4&1\\\\1&2\\end{bmatrix}$",
                            "$\\begin{bmatrix}6&1\\\\2&10\\end{bmatrix}$",
                        ],
                        "Penjumlahan matriks dilakukan elemen-sebaris-sekolom: $1+5=6$, $2+1=3$, $3+2=5$, $4+6=10$.",
                    ),
                    (
                        "hard",
                        "Diketahui $A=\\begin{bmatrix}2&1\\\\0&3\\end{bmatrix}$ dan $v=\\begin{bmatrix}4\\\\5\\end{bmatrix}$. Hasil $Av$ adalah...",
                        "$\\begin{bmatrix}13\\\\15\\end{bmatrix}$",
                        [
                            "$\\begin{bmatrix}8\\\\15\\end{bmatrix}$",
                            "$\\begin{bmatrix}13\\\\15\\end{bmatrix}$",
                            "$\\begin{bmatrix}9\\\\8\\end{bmatrix}$",
                            "$\\begin{bmatrix}6\\\\8\\end{bmatrix}$",
                        ],
                        "Kalikan baris dengan kolom: baris pertama $2(4)+1(5)=13$, baris kedua $0(4)+3(5)=15$.",
                    ),
                ],
            )
        if "data" in text or "statistik" in text or "statistics" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Data nilai: 6, 8, 10. Rata-ratanya adalah...", "8", ["6", "7", "8", "10"], "Rata-rata $=\\frac{6+8+10}{3}=8$."),
                    ("medium", "Data penjualan selama 4 hari adalah 12, 15, 15, dan 18. Median data tersebut adalah...", "15", ["12", "15", "16.5", "18"], "Urutan data sudah $12,15,15,18$. Median dua tengah $=\\frac{15+15}{2}=15$."),
                    ("hard", "Data 4, 6, 6, 8, 11 memiliki jangkauan...", "7", ["5", "6", "7", "11"], "Jangkauan adalah nilai terbesar dikurangi terkecil: $11-4=7$."),
                ],
            )
        if "function" in text or "fungsi" in text:
            return _math_pack(
                concept_code=concept.code,
                title=title,
                rows=[
                    ("easy", "Jika $f(x)=2x+1$, berapa $f(3)$?", "$7$", ["$5$", "$6$", "$7$", "$8$"], "Substitusi $x=3$: $2(3)+1=7$."),
                    ("medium", "Jika $g(x)=x^2-1$, berapa $g(4)$?", "$15$", ["$7$", "$12$", "$15$", "$17$"], "Substitusi $x=4$: $4^2-1=15$."),
                    ("hard", "Jika $f(x)=3x-2$ dan $g(x)=x+5$, berapa $f(g(2))$?", "$19$", ["$7$", "$13$", "$19$", "$21$"], "Hitung $g(2)=7$, lalu $f(7)=3(7)-2=19$."),
                ],
            )
        return _generic_pack(concept_code=concept.code, title=title, language=language)

    def _generate_pack(
        self,
        *,
        concept: KnowledgeConcept,
        language: str,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
        ai_pack, ai_metadata = self._try_generate_pack_with_ai(concept=concept, language=language)
        if ai_pack is not None:
            return ai_pack, ai_metadata
        return self._fallback_pack(concept=concept, language=language), {
            "generation_source": "fallback_generated",
            "llm_provider": "deterministic",
            "llm_model": "template_v1",
            "fallback_reason": "LLM generation is disabled, unavailable, or failed validation after bounded retries.",
            "llm_generation_attempt": ai_metadata,
        }

    def _try_generate_pack_with_ai(
        self,
        *,
        concept: KnowledgeConcept,
        language: str,
    ) -> tuple[dict[str, dict[str, Any]] | None, dict[str, Any]]:
        settings = get_ai_settings()
        if os.getenv("WICARA_PRETEST_LLM_GENERATION", "").strip().lower() not in {
            "1",
            "true",
            "yes",
        }:
            return None, {"llm_attempted": False, "reason": "WICARA_PRETEST_LLM_GENERATION is not enabled."}
        if not settings.gemini_api_key.strip():
            return None, {"llm_attempted": False, "reason": "Gemini API key is not configured."}
        try:
            asyncio.get_running_loop()
            return None, {"llm_attempted": False, "reason": "Generation called inside a running event loop."}
        except RuntimeError:
            pass

        validation_errors: list[str] = []
        max_attempts = _max_generation_attempts()
        for attempt in range(1, max_attempts + 1):
            prompt = _pack_prompt(
                concept=concept,
                language=language,
                previous_errors=validation_errors,
            )
            try:
                response = asyncio.run(
                    ai_client.generate(
                        system_instruction="Return valid JSON only.",
                        user_instruction=prompt,
                        params={"temperature": 0.15, "response_mime_type": "application/json"},
                    )
                )
                payload = json.loads(response.text)
                pack = _extract_pack_payload(payload)
                if not isinstance(pack, dict):
                    validation_errors.append(
                        f"attempt {attempt}: response must be an object with easy, medium, and hard questions."
                    )
                    continue
                self.validator.validate_pack(concept_code=concept.code, pack=pack)
                return pack, {
                    "generation_source": "llm_generated",
                    "llm_provider": response.provider,
                    "llm_model": response.model,
                    "attempt_count": attempt,
                    "prompt_version": PACK_PROMPT_VERSION,
                    "previous_validation_errors": validation_errors,
                }
            except Exception as exc:
                validation_errors.append(f"attempt {attempt}: {exc}")
        return None, {
            "llm_attempted": True,
            "attempt_count": max_attempts,
            "prompt_version": PACK_PROMPT_VERSION,
            "validation_errors": validation_errors,
        }


def _math_pack(
    *,
    concept_code: str,
    title: str,
    rows: list[tuple[str, str, str, list[str], str]],
) -> dict[str, dict[str, Any]]:
    pack: dict[str, dict[str, Any]] = {}
    labels = ["A", "B", "C", "D"]
    for difficulty, prompt, correct, options, explanation in rows:
        pack[difficulty] = {
            "concept_code": concept_code,
            "difficulty": difficulty,
            "question_type": "multiple_choice",
            "prompt": prompt,
            "helper_text": f"Pilih jawaban yang paling tepat untuk {title}.",
            "options": [
                {"label": label, "text": text, "is_correct": text == correct}
                for label, text in zip(labels, options, strict=True)
            ],
            "explanation": explanation,
            "expected_reasoning": explanation,
            "rubric": {
                "correct_answer_score": 1.0,
                "reasoning_score_available": True,
                "canvas_score_available": True,
            },
        }
    return pack


def _generic_pack(
    *,
    concept_code: str,
    title: str,
    language: str,
) -> dict[str, dict[str, Any]]:
    return _math_pack(
        concept_code=concept_code,
        title=title,
        rows=[
            (
                "easy",
                f"Dalam latihan {title}, sebuah nilai awal 12 bertambah 5. Berapa nilai akhirnya?",
                "17",
                ["15", "16", "17", "18"],
                "Hitung perubahan langsung: $12+5=17$.",
            ),
            (
                "medium",
                f"Pada konteks {title}, data berurutan adalah 18, 24, dan 30. Selisih tetap antar data adalah...",
                "6",
                ["4", "6", "8", "12"],
                "Selisihnya $24-18=6$ dan $30-24=6$.",
            ),
            (
                "hard",
                f"Sebuah model sederhana untuk {title} memakai aturan $S=3a+2b$. Jika $a=4$ dan $b=5$, maka $S$ adalah...",
                "22",
                ["17", "20", "22", "26"],
                "Substitusi nilai: $S=3(4)+2(5)=12+10=22$.",
            ),
        ],
    )


def _pack_prompt(
    *,
    concept: KnowledgeConcept,
    language: str,
    previous_errors: list[str] | None = None,
) -> str:
    retry_instruction = ""
    if previous_errors:
        compact_errors = "\n".join(f"- {error}" for error in previous_errors[-6:])
        retry_instruction = f"""

The previous generated pack failed backend validation.
Regenerate the entire pack, do not patch only one field.
Fix these validation errors:
{compact_errors}
""".rstrip()

    return f"""
Generate one adaptive pretest question pack for this existing curriculum concept.

Concept:
- concept_code: {concept.code}
- title: {concept.title}
- description: {concept.description or ''}
- language: {language}

Return JSON shaped exactly as:
{{
  "easy": {{...}},
  "medium": {{...}},
  "hard": {{...}}
}}

Each question object must contain:
- concept_code matching "{concept.code}"
- difficulty: easy, medium, or hard
- question_type: multiple_choice
- prompt
- helper_text
- options: exactly 4 options with label, text, is_correct
- explanation
- expected_reasoning
- rubric

Exactly one option must be correct per question.
Do not invent a new concept_code.
Make every question a concrete problem to solve, not a definition quiz or vague theory check.
Do not ask about test-taking strategy, "which step is best", or generic concept recognition.
Options must be concrete final answers, not descriptions of strategies.
For math concepts, use numeric/algebraic tasks with a definite answer.
For calculus/derivative concepts, ask users to compute derivatives, slopes, tangent values, or apply derivative rules.
Use lightweight Markdown when useful:
- inline math may use $...$
- display math may use $$...$$
- matrices must use LaTeX matrix notation inside math delimiters, for example $A=\\begin{{bmatrix}}1&2\\\\3&4\\end{{bmatrix}}$
- keep prompts short enough for mobile
Options may also contain math notation.
{retry_instruction}
""".strip()


def _correct_label(payload: dict[str, Any]) -> str:
    for option in payload["options"]:
        if option.get("is_correct") is True:
            return str(option["label"])
    return ""


def _extract_pack_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return None
    questions = payload.get("questions")
    return questions if isinstance(questions, dict) else payload


def _max_generation_attempts() -> int:
    raw_value = os.getenv("WICARA_PRETEST_LLM_MAX_ATTEMPTS", "").strip()
    if not raw_value:
        return DEFAULT_PACK_GENERATION_MAX_ATTEMPTS
    try:
        return max(1, min(8, int(raw_value)))
    except ValueError:
        return DEFAULT_PACK_GENERATION_MAX_ATTEMPTS
