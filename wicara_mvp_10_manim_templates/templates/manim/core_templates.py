from manim import *
import os
import math
import re
import textwrap
from pathlib import Path

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.helper import remove_bookmarks
    from manim_voiceover.services.base import SpeechService
    from manim_voiceover.services.gtts import GTTSService
    try:
        from openai import OpenAI
    except ImportError:
        OpenAI = None
except ImportError:
    VoiceoverScene = Scene
    SpeechService = None
    remove_bookmarks = lambda text: text
    GTTSService = None
    OpenAI = None

LANGUAGE_ALIASES = {
    "id": "id",
    "id-id": "id",
    "indonesian": "id",
    "bahasa": "id",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "vi": "vi",
    "vi-vn": "vi",
    "vietnamese": "vi",
    "ms": "ms",
    "ms-my": "ms",
    "malay": "ms",
    "ja": "ja",
    "ja-jp": "ja",
    "japanese": "ja",
}

I18N_LABELS = {
    "default_title": {
        "id": "Penjelasan Konsep",
        "en": "Concept Explanation",
        "vi": "Giai thich khai niem",
    },
    "summary_title": {
        "id": "Kesimpulan",
        "en": "Summary",
        "vi": "Tong ket",
    },
    "step_prefix": {
        "id": "Langkah",
        "en": "Step",
        "vi": "Buoc",
    },
    "ratio_context_default": {
        "id": "Konteks rasio",
        "en": "Ratio context",
        "vi": "Boi canh ty le",
    },
    "graph_function_default": {
        "id": "grafik fungsi",
        "en": "function graph",
        "vi": "do thi ham so",
    },
    "moving_point_default": {
        "id": "titik",
        "en": "point",
        "vi": "diem",
    },
    "object_default": {
        "id": "Benda",
        "en": "Object",
        "vi": "Vat the",
    },
    "motion_graph_default": {
        "id": "Grafik gerak",
        "en": "Motion graph",
        "vi": "Do thi chuyen dong",
    },
    "highlight_prefix": {
        "id": "Sorot:",
        "en": "Highlight:",
        "vi": "Noi bat:",
    },
    "direction_to": {
        "id": "ke",
        "en": "to",
        "vi": "ve",
    },
    "resultant_label": {
        "id": "Resultan",
        "en": "Resultant",
        "vi": "Hop luc",
    },
}

I18N_PHRASES = {
    "Ide utama": {
        "en": "Main idea",
        "vi": "Y chinh",
    },
    "Garis bilangan membantu membandingkan posisi dan nilai angka.": {
        "en": "A number line helps compare number positions and values.",
        "vi": "Truc so giup so sanh vi tri va gia tri cua cac so.",
    },
    "Garis bilangan": {
        "en": "Number line",
        "vi": "Truc so",
    },
    "Tandai angka": {
        "en": "Mark the numbers",
        "vi": "Danh dau cac so",
    },
    "Setiap angka ditempatkan sesuai posisinya di garis bilangan.": {
        "en": "Each number is placed at its position on the number line.",
        "vi": "Moi so duoc dat dung vi tri tren truc so.",
    },
    "Bandingkan": {
        "en": "Compare",
        "vi": "So sanh",
    },
    "Arah panah menunjukkan perpindahan dari angka kiri ke angka kanan.": {
        "en": "The arrow direction shows movement from the left number to the right number.",
        "vi": "Huong mui ten cho thay su di chuyen tu so ben trai sang so ben phai.",
    },
    "Model blok": {
        "en": "Block model",
        "vi": "Mo hinh khoi",
    },
    "Setiap kotak kecil mewakili satu benda atau satu satuan.": {
        "en": "Each small block represents one object or one unit.",
        "vi": "Moi o nho dai dien cho mot vat hoac mot don vi.",
    },
    "Gabungkan jumlah": {
        "en": "Combine quantities",
        "vi": "Gop so luong",
    },
    "Kita melihat dua kelompok lalu menyatukannya menjadi satu hasil.": {
        "en": "We observe two groups and combine them into one result.",
        "vi": "Ta quan sat hai nhom roi gop lai thanh mot ket qua.",
    },
    "Bagian dari keseluruhan": {
        "en": "Part of a whole",
        "vi": "Phan cua tong the",
    },
    "Pecahan menunjukkan berapa bagian yang diambil dari satu keseluruhan.": {
        "en": "Fractions show how many parts are taken from a whole.",
        "vi": "Phan so cho biet bao nhieu phan duoc lay tu mot tong the.",
    },
    "Bandingkan bagian": {
        "en": "Compare parts",
        "vi": "So sanh phan",
    },
    "Walau jumlah potongannya berbeda, bagian yang diwarnai bisa sama besar.": {
        "en": "Even with different partitions, highlighted parts can represent the same value.",
        "vi": "Du so phan chia khac nhau, phan duoc to mau van co the bang nhau.",
    },
    "Apa itu rasio?": {
        "en": "What is a ratio?",
        "vi": "Ty le la gi?",
    },
    "Rasio membandingkan dua kuantitas dalam satu situasi.": {
        "en": "A ratio compares two quantities in the same context.",
        "vi": "Ty le so sanh hai dai luong trong cung mot boi canh.",
    },
    "Persamaan = seimbang": {
        "en": "Equation = balance",
        "vi": "Phuong trinh = can bang",
    },
    "Tanda sama dengan berarti ruas kiri dan kanan memiliki nilai yang setara.": {
        "en": "The equals sign means the left and right sides have equivalent values.",
        "vi": "Dau bang cho biet ve trai va ve phai co gia tri tuong duong.",
    },
    "Pola bertumbuh": {
        "en": "Growing pattern",
        "vi": "Mau hinh tang dan",
    },
    "Setiap suku dapat dilihat sebagai gambar atau jumlah yang berubah teratur.": {
        "en": "Each term can be seen as a visual or a quantity that changes regularly.",
        "vi": "Moi so hang co the xem nhu hinh anh hoac gia tri thay doi deu dan.",
    },
    "Apa itu luas?": {
        "en": "What is area?",
        "vi": "Dien tich la gi?",
    },
    "Luas adalah banyaknya daerah yang ditutupi oleh satuan persegi.": {
        "en": "Area is the amount of surface covered by square units.",
        "vi": "Dien tich la phan be mat duoc phu boi cac don vi vuong.",
    },
    "Apa yang dilihat?": {
        "en": "What do we see?",
        "vi": "Ta thay gi?",
    },
    "Grafik menunjukkan hubungan antara nilai x dan nilai f(x).": {
        "en": "The graph shows the relationship between x and f(x).",
        "vi": "Do thi cho thay moi quan he giua x va f(x).",
    },
    "Titik bergerak": {
        "en": "Moving point",
        "vi": "Diem chuyen dong",
    },
    "Saat x berubah, posisi titik di grafik ikut berubah.": {
        "en": "When x changes, the point position on the graph also changes.",
        "vi": "Khi x thay doi, vi tri diem tren do thi cung thay doi.",
    },
    "Laju perubahan lokal": {
        "en": "Local rate of change",
        "vi": "Toc do thay doi cuc bo",
    },
    "Gerak terhadap waktu": {
        "en": "Motion over time",
        "vi": "Chuyen dong theo thoi gian",
    },
    "Kita lihat benda bergerak, lalu hubungkan dengan grafik posisinya.": {
        "en": "We observe motion first, then connect it to a position graph.",
        "vi": "Ta quan sat vat chuyen dong roi lien he voi do thi vi tri.",
    },
    "Benda bergerak": {
        "en": "Object in motion",
        "vi": "Vat the chuyen dong",
    },
    "Posisi benda berubah seiring waktu.": {
        "en": "The object's position changes over time.",
        "vi": "Vi tri cua vat thay doi theo thoi gian.",
    },
    "Grafik posisi": {
        "en": "Position graph",
        "vi": "Do thi vi tri",
    },
    "Grafik menunjukkan hubungan antara waktu dan posisi.": {
        "en": "The graph shows the relationship between time and position.",
        "vi": "Do thi cho thay moi quan he giua thoi gian va vi tri.",
    },
    "Gaya sebagai panah": {
        "en": "Forces as arrows",
        "vi": "Luc duoc bieu dien bang mui ten",
    },
    "Panjang panah menunjukkan besar gaya, arah panah menunjukkan arah gaya.": {
        "en": "Arrow length shows force magnitude, and arrow direction shows force direction.",
        "vi": "Do dai mui ten cho biet do lon luc, huong mui ten cho biet huong luc.",
    },
    "Gaya-gaya bekerja": {
        "en": "Forces acting",
        "vi": "Cac luc tac dung",
    },
    "Setiap panah menunjukkan gaya yang bekerja pada benda.": {
        "en": "Each arrow represents a force acting on the object.",
        "vi": "Moi mui ten the hien mot luc tac dung len vat the.",
    },
    "Resultan gaya": {
        "en": "Resultant force",
        "vi": "Hop luc",
    },
    "Gaya berlawanan dikurangkan untuk mendapatkan resultannya.": {
        "en": "Opposing forces are subtracted to get the resultant force.",
        "vi": "Cac luc nguoc chieu duoc tru de tim hop luc.",
    },
    "awal": {
        "en": "start",
        "vi": "bat dau",
    },
    "akhir": {
        "en": "end",
        "vi": "ket thuc",
    },
}


# ============================================================
# WICARA MVP 10 MANIM TEMPLATES — CLEAN VERSION
# ============================================================
# Run examples:
#   manim -ql wicara_mvp_10_clean.py NumberLineQuantityTemplate
#   manim -ql wicara_mvp_10_clean.py GraphExplanationTemplate
#   manim -ql wicara_mvp_10_clean.py ForceDiagramTemplate
#
# Design goal:
# - Longer educational flow, not too short.
# - Fixed layout zones.
# - One active explanation card at a time.
# - No text stacking.
# - Clean final frame.
# - SceneSpec-driven defaults.
# ============================================================


# ============================================================
# SHARED HELPERS
# ============================================================

def clamp_text(text, max_chars=90):
    text = "" if text is None else str(text)
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def wrap_text(text, width=42):
    text = "" if text is None else str(text)
    return "\n".join(textwrap.wrap(text, width=width))


def safe_text(text, max_chars=120, width=42):
    return wrap_text(clamp_text(text, max_chars=max_chars), width=width)


def require(spec, key):
    if key not in spec or spec[key] in (None, "", []):
        raise ValueError(f"Missing required field: {key}")
    return spec[key]


def direction_vector(direction):
    direction = str(direction).lower()
    mapping = {
        "right": RIGHT,
        "left": LEFT,
        "up": UP,
        "down": DOWN,
    }
    if direction not in mapping:
        raise ValueError(f"Invalid direction: {direction}")
    return mapping[direction]


def build_function(function_spec):
    ftype = function_spec.get("type", "linear")
    p = function_spec.get("params", {})

    if ftype == "linear":
        m = float(p.get("m", 1))
        b = float(p.get("b", 0))
        return lambda x: m * x + b

    if ftype == "quadratic":
        a = float(p.get("a", 1))
        b = float(p.get("b", 0))
        c = float(p.get("c", 0))
        return lambda x: a * x**2 + b * x + c

    if ftype == "cubic":
        a = float(p.get("a", 1))
        b = float(p.get("b", 0))
        c = float(p.get("c", 0))
        d = float(p.get("d", 0))
        return lambda x: a * x**3 + b * x**2 + c * x + d

    if ftype == "exponential":
        a = float(p.get("a", 1))
        base = float(p.get("base", 2))
        k = float(p.get("k", 1))
        c = float(p.get("c", 0))
        return lambda x: a * (base ** (k * x)) + c

    if ftype == "sine":
        a = float(p.get("a", 1))
        b = float(p.get("b", 1))
        c = float(p.get("c", 0))
        d = float(p.get("d", 0))
        return lambda x: a * math.sin(b * x + c) + d

    raise ValueError(f"Unsupported function type: {ftype}")


def numerical_slope(f, x, h=1e-4):
    return (f(x + h) - f(x - h)) / (2 * h)


def _voiceover_lang_for_gtts(language: str) -> str:
    normalized = str(language or "").strip().lower()
    mapped = LANGUAGE_ALIASES.get(normalized, normalized.split("-")[0] if normalized else "id")
    if mapped in {"id", "en", "vi", "ms", "ja"}:
        return mapped
    return "en"


def _split_voiceover_script(script: str, max_chars: int = 220) -> list[str]:
    text = " ".join(str(script or "").split())
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    segments: list[str] = []
    for part in parts:
        cleaned = part.strip()
        if not cleaned:
            continue
        if len(cleaned) <= max_chars:
            segments.append(cleaned)
            continue

        words = cleaned.split(" ")
        chunk: list[str] = []
        size = 0
        for word in words:
            word_len = len(word)
            if chunk and (size + 1 + word_len) > max_chars:
                segments.append(" ".join(chunk).strip())
                chunk = [word]
                size = word_len
            else:
                chunk.append(word)
                size = word_len if not chunk[:-1] else size + 1 + word_len
        if chunk:
            segments.append(" ".join(chunk).strip())
    return [segment for segment in segments if segment]


def _normalize_tts_provider(value) -> str:
    normalized = str(value or "").strip().lower()
    mapping = {
        "gtts": "gtts_voiceover",
        "gtts_voiceover": "gtts_voiceover",
        "openai": "openai_voiceover",
        "openai_tts": "openai_voiceover",
        "openai_voiceover": "openai_voiceover",
        "none": "none",
    }
    return mapping.get(normalized, "gtts_voiceover")


if SpeechService is not None and OpenAI is not None:
    class OpenAIFallbackVoiceoverService(SpeechService):
        def __init__(
            self,
            *,
            api_key: str | None = None,
            model_primary: str = "gpt-4o-mini-tts",
            model_fallback: str = "tts-1",
            voice_primary: str = "marin",
            voice_fallback: str = "alloy",
            response_format: str = "mp3",
            instructions: str = "",
            **kwargs,
        ):
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model_primary = model_primary
            self.model_fallback = model_fallback
            self.voice_primary = voice_primary
            self.voice_fallback = voice_fallback
            self.response_format = str(response_format or "wav").lower()
            self.instructions = " ".join(str(instructions or "").split())
            super().__init__(**kwargs)

        def _request_tts(self, *, model: str, voice: str, input_text: str, output_path: Path):
            payload = {
                "model": model,
                "voice": voice,
                "input": input_text,
                "response_format": self.response_format,
            }
            if self.instructions and model.startswith("gpt-4o-mini-tts"):
                payload["instructions"] = self.instructions
            with self.client.audio.speech.with_streaming_response.create(**payload) as response:
                response.stream_to_file(output_path)

        def generate_from_text(self, text: str, cache_dir: str = None, path: str = None, **kwargs) -> dict:
            cache_root = Path(cache_dir) if cache_dir is not None else Path(self.cache_dir)
            input_text = remove_bookmarks(text)
            speed = kwargs.get("speed", 1.0)
            input_data = {
                "input_text": input_text,
                "service": "openai_speech_api",
                "config": {
                    "model_primary": self.model_primary,
                    "model_fallback": self.model_fallback,
                    "voice_primary": self.voice_primary,
                    "voice_fallback": self.voice_fallback,
                    "response_format": self.response_format,
                    "speed": speed,
                },
            }
            cached_result = self.get_cached_result(input_data, cache_root)
            if cached_result is not None:
                return cached_result

            extension = self.response_format if self.response_format != "pcm" else "wav"
            audio_file = path or f"{self.get_audio_basename(input_data)}.{extension}"
            output_path = cache_root / audio_file

            used_model = self.model_primary
            used_voice = self.voice_primary
            try:
                self._request_tts(
                    model=self.model_primary,
                    voice=self.voice_primary,
                    input_text=input_text,
                    output_path=output_path,
                )
            except Exception:
                used_model = self.model_fallback
                used_voice = self.voice_fallback
                self._request_tts(
                    model=self.model_fallback,
                    voice=self.voice_fallback,
                    input_text=input_text,
                    output_path=output_path,
                )

            return {
                "input_text": text,
                "input_data": input_data,
                "original_audio": audio_file,
                "tts_engine": "openai_speech_api",
                "model": used_model,
                "voice": used_voice,
            }
else:
    OpenAIFallbackVoiceoverService = None


def _dedupe_voiceover_segments(segments: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for segment in segments:
        cleaned = " ".join(str(segment or "").split())
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


class WicaraTemplateScene(VoiceoverScene):
    SPEC = {}

    def setup(self):
        super().setup()
        self._resolved_language = "id"
        self._voiceover_initialized = False
        self._voiceover_enabled = False
        self._voiceover_segments: list[str] = []
        self._voiceover_index = 0
        self._voiceover_provider = "none"
        self._requested_tts_provider = "gtts_voiceover"
        self._openai_primary_model = "gpt-4o-mini-tts"
        self._openai_fallback_model = "tts-1"
        self._openai_primary_voice = "marin"
        self._openai_fallback_voice = "alloy"
        self._openai_response_format = "mp3"
        self._openai_instructions = ""
        self._openai_fallback_attempted = False

    # --------------------------------------------------------
    # Layout zones
    # --------------------------------------------------------

    def title_zone_y(self):
        return 3.25

    def visual_center(self):
        return LEFT * 2.05 + DOWN * 0.40

    def right_card_center(self):
        return RIGHT * 4.05 + DOWN * 0.30

    def bottom_summary_y(self):
        return -3.18

    # --------------------------------------------------------
    # Text/card helpers
    # --------------------------------------------------------
    def _clean_voice_text(self, value):
        return " ".join(str(value or "").split())

    def _build_structured_voiceover_segments(self, spec):
        segments: list[str] = []
        title = self._clean_voice_text(spec.get("title"))
        subtitle = self._clean_voice_text(spec.get("subtitle"))
        if title and subtitle:
            segments.append(f"{title}. {subtitle}")
        elif title:
            segments.append(title)
        elif subtitle:
            segments.append(subtitle)

        steps = spec.get("steps")
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                default_step_title = (
                    f"{self.tr_key('step_prefix', spec, fallback='Langkah')} {index + 1}"
                )
                step_title = self._clean_voice_text(step.get("title", default_step_title))
                step_body = self._clean_voice_text(step.get("body"))
                if step_title and step_body:
                    if not step_title.endswith((".", "!", "?")):
                        step_title = f"{step_title}."
                    sentence = f"{step_title} {step_body}"
                else:
                    sentence = step_title or step_body
                if sentence:
                    segments.extend(_split_voiceover_script(sentence, max_chars=180))

        summary = self._clean_voice_text(spec.get("summary"))
        if summary:
            segments.extend(_split_voiceover_script(summary, max_chars=200))
        return segments

    def _build_voiceover_segments(self, spec):
        explicit_script = self._clean_voice_text(spec.get("voiceover_script"))
        explicit_segments = _split_voiceover_script(explicit_script)

        # Optional advanced mode: upstream model can pass per-step narration directly.
        structured_segments: list[str] = []
        raw_segments = spec.get("narration_segments")
        if isinstance(raw_segments, list):
            for item in raw_segments:
                if isinstance(item, str):
                    structured_segments.extend(_split_voiceover_script(item, max_chars=180))
                elif isinstance(item, dict):
                    text = self._clean_voice_text(item.get("text"))
                    if text:
                        structured_segments.extend(_split_voiceover_script(text, max_chars=180))

        if not structured_segments:
            structured_segments = self._build_structured_voiceover_segments(spec)

        if explicit_segments and structured_segments:
            # Keep explicit intro but still cover all educational steps.
            return _dedupe_voiceover_segments(explicit_segments + structured_segments)
        if explicit_segments:
            return _dedupe_voiceover_segments(explicit_segments)
        return _dedupe_voiceover_segments(structured_segments)

    def _resolve_tts_provider(self, spec):
        requested = (
            spec.get("tts_provider")
            or spec.get("voiceover_provider")
            or os.getenv("MEDIA_TTS_PROVIDER")
            or "gtts_voiceover"
        )
        normalized = _normalize_tts_provider(requested)
        self._requested_tts_provider = normalized
        return normalized

    def _resolve_openai_voiceover_config(self, spec):
        self._openai_primary_model = str(
            spec.get("tts_model_primary")
            or spec.get("tts_model")
            or os.getenv("MEDIA_OPENAI_TTS_MODEL_PRIMARY")
            or "gpt-4o-mini-tts"
        ).strip()
        self._openai_fallback_model = str(
            spec.get("tts_model_fallback")
            or os.getenv("MEDIA_OPENAI_TTS_MODEL_FALLBACK")
            or "tts-1"
        ).strip()
        self._openai_primary_voice = str(
            spec.get("tts_voice_primary")
            or spec.get("tts_voice")
            or os.getenv("MEDIA_OPENAI_TTS_VOICE_PRIMARY")
            or "marin"
        ).strip()
        self._openai_fallback_voice = str(
            spec.get("tts_voice_fallback")
            or os.getenv("MEDIA_OPENAI_TTS_VOICE_FALLBACK")
            or "alloy"
        ).strip()
        self._openai_response_format = str(
            spec.get("tts_response_format")
            or os.getenv("MEDIA_OPENAI_TTS_RESPONSE_FORMAT")
            or "mp3"
        ).strip().lower()
        self._openai_instructions = " ".join(
            str(
                spec.get("tts_instructions")
                or os.getenv("MEDIA_OPENAI_TTS_INSTRUCTIONS")
                or ""
            ).split()
        )

    def _configure_openai_voiceover(self, spec):
        self._resolve_openai_voiceover_config(spec)
        if OpenAIFallbackVoiceoverService is None:
            return False
        api_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            return False
        self.set_speech_service(
            OpenAIFallbackVoiceoverService(
                api_key=api_key,
                model_primary=self._openai_primary_model,
                model_fallback=self._openai_fallback_model,
                voice_primary=self._openai_primary_voice,
                voice_fallback=self._openai_fallback_voice,
                response_format=self._openai_response_format,
                instructions=self._openai_instructions,
            )
        )
        self._voiceover_provider = "openai_voiceover"
        self._openai_fallback_attempted = False
        return True

    def _configure_gtts_voiceover(self, spec):
        if GTTSService is None:
            return False
        language = self.resolve_language(spec)
        gtts_lang = _voiceover_lang_for_gtts(language)
        self.set_speech_service(GTTSService(lang=gtts_lang))
        self._voiceover_provider = "gtts_voiceover"
        return True

    def _initialize_voiceover(self, spec):
        if self._voiceover_initialized:
            return

        self._voiceover_initialized = True

        segments = self._build_voiceover_segments(spec)
        if not segments:
            self._voiceover_provider = "none"
            return

        provider = self._resolve_tts_provider(spec)
        configured = False
        if provider == "none":
            self._voiceover_provider = "none"
            return
        if provider == "openai_voiceover":
            configured = self._configure_openai_voiceover(spec)
            if not configured:
                configured = self._configure_gtts_voiceover(spec)
        else:
            configured = self._configure_gtts_voiceover(spec)

        if not configured:
            self._voiceover_provider = "none"
            return

        self._voiceover_segments = segments
        self._voiceover_index = 0
        self._voiceover_enabled = True

    def _next_voiceover_segment(self):
        if not self._voiceover_enabled:
            return None
        if self._voiceover_index >= len(self._voiceover_segments):
            return None
        segment = self._voiceover_segments[self._voiceover_index]
        self._voiceover_index += 1
        return segment

    def _play_with_voiceover_segment(self, segment, *args, **kwargs):
        run_time = kwargs.get("run_time")
        try:
            with self.voiceover(text=segment) as tracker:
                updated_kwargs = dict(kwargs)
                if tracker.duration > 0:
                    if run_time is None:
                        updated_kwargs["run_time"] = tracker.duration
                    else:
                        updated_kwargs["run_time"] = max(float(run_time), float(tracker.duration))
                return super().play(*args, **updated_kwargs)
        except Exception:
            if self._voiceover_provider == "openai_voiceover" and not self._openai_fallback_attempted:
                self._openai_fallback_attempted = True
                try:
                    self.set_speech_service(
                        OpenAIFallbackVoiceoverService(
                            api_key=os.getenv("OPENAI_API_KEY"),
                            model_primary=self._openai_fallback_model,
                            model_fallback=self._openai_fallback_model,
                            voice_primary=self._openai_fallback_voice,
                            voice_fallback=self._openai_fallback_voice,
                            response_format=self._openai_response_format,
                        )
                    )
                    return self._play_with_voiceover_segment(segment, *args, **kwargs)
                except Exception:
                    if self._configure_gtts_voiceover(self.SPEC):
                        return self._play_with_voiceover_segment(segment, *args, **kwargs)
            self._voiceover_enabled = False
            return super().play(*args, **kwargs)

    def play_with_voiceover(self, narration_text, *args, **kwargs):
        if not narration_text or not self._voiceover_enabled:
            return self.play(*args, **kwargs)
        narration = self._clean_voice_text(narration_text)
        if not narration:
            return self.play(*args, **kwargs)
        # Keep auto segment cursor aligned to avoid duplicate narration later.
        if self._voiceover_index < len(self._voiceover_segments):
            self._voiceover_index += 1
        return self._play_with_voiceover_segment(narration, *args, **kwargs)

    def play(self, *args, **kwargs):
        segment = self._next_voiceover_segment()
        if not segment:
            return super().play(*args, **kwargs)
        return self._play_with_voiceover_segment(segment, *args, **kwargs)

    def resolve_language(self, spec=None):
        payload = spec if isinstance(spec, dict) else getattr(self, "SPEC", {})
        candidates = [
            payload.get("language"),
            payload.get("locale"),
            payload.get("lang"),
        ]
        for raw in candidates:
            if raw is None:
                continue
            normalized = str(raw).strip().lower()
            if not normalized:
                continue
            lang = LANGUAGE_ALIASES.get(normalized, normalized.split("-")[0])
            if lang in {"id", "en", "vi", "ms", "ja"}:
                self._resolved_language = lang
                return lang
        self._resolved_language = "id"
        return "id"

    def tr_key(self, key, spec=None, fallback=""):
        lang = self.resolve_language(spec)
        values = I18N_LABELS.get(key, {})
        if not values:
            return fallback
        if lang in values:
            return values[lang]
        if lang != "id" and "en" in values:
            return values["en"]
        return values.get("id", fallback)

    def tr_text(self, text, spec=None):
        if text is None:
            return ""
        lang = self.resolve_language(spec)
        if lang == "id":
            return text
        normalized = " ".join(str(text).split())
        if not normalized:
            return str(text)
        values = I18N_PHRASES.get(normalized)
        if not values:
            return str(text)
        return values.get(lang) or values.get("en") or str(text)

    def make_title_block(self, spec):
        self.resolve_language(spec)
        self._initialize_voiceover(spec)
        phase = str(spec.get("phase", "")).upper()
        level = str(spec.get("audience_level", "")).lower()

        if phase in ["A", "B", "C"] or level in ["sd", "elementary"]:
            title_size = 34
            subtitle_size = 19
            subtitle_width = 56
        elif phase in ["E", "F"] or level in ["sma", "high"]:
            title_size = 33
            subtitle_size = 18
            subtitle_width = 62
        else:
            title_size = 33
            subtitle_size = 18
            subtitle_width = 60

        title = Text(
            clamp_text(
                spec.get(
                    "title",
                    self.tr_key("default_title", spec, fallback="Penjelasan Konsep"),
                ),
                50,
            ),
            font_size=title_size,
            weight=BOLD,
        )

        subtitle_text = spec.get("subtitle", "")
        if subtitle_text:
            subtitle = Text(
                wrap_text(clamp_text(subtitle_text, 96), subtitle_width),
                font_size=subtitle_size,
                color=GRAY_A,
                line_spacing=0.82,
            )
            block = VGroup(title, subtitle).arrange(DOWN, buff=0.10)
        else:
            block = VGroup(title)

        block.to_edge(UP, buff=0.22)
        return block

    def make_card(self, title, body, color=BLUE, width=4.75, body_width=34):
        localized_title = self.tr_text(title)
        localized_body = self.tr_text(body)
        title_obj = Text(
            safe_text(localized_title, max_chars=40, width=28),
            font_size=20,
            weight=BOLD,
            color=color,
        )

        body_obj = Text(
            safe_text(localized_body, max_chars=145, width=body_width),
            font_size=15,
            line_spacing=0.84,
            color=WHITE,
        )

        group = VGroup(title_obj, body_obj).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.18,
        )

        box = RoundedRectangle(
            corner_radius=0.18,
            width=max(width, group.width + 0.55),
            height=max(1.15, group.height + 0.46),
            stroke_color=color,
            stroke_opacity=0.78,
            fill_color=BLACK,
            fill_opacity=0.70,
            stroke_width=2,
        )

        group.move_to(box.get_center())
        return VGroup(box, group)

    def place_right_card(self, card):
        card.move_to(self.right_card_center())
        return card

    def place_summary_card(self, card):
        card.to_edge(DOWN, buff=0.28)
        return card

    def replace_card(self, previous_card, next_card, zone="right", narration_text=None):
        if zone == "right":
            self.place_right_card(next_card)
        elif zone == "bottom":
            self.place_summary_card(next_card)

        if previous_card is None:
            self.play_with_voiceover(
                narration_text,
                FadeIn(next_card, shift=LEFT * 0.15),
                run_time=0.55,
            )
        else:
            self.play_with_voiceover(
                narration_text,
                ReplacementTransform(previous_card, next_card),
                run_time=0.50,
            )

        return next_card

    def fade_card(self, card):
        if card is not None:
            self.play(FadeOut(card), run_time=0.32)

    def clean_summary(self, spec, active_card=None, extra_fadeouts=None):
        # Fade out everything currently on screen so the summary gets a clean frame.
        # active_card and extra_fadeouts are kept for API compatibility but are
        # subsumed — self.mobjects already contains them.
        on_screen = list(self.mobjects)
        if on_screen:
            self.play(*[FadeOut(m) for m in on_screen], run_time=0.42)

        summary_card = self.make_card(
            self.tr_key("summary_title", spec, fallback="Kesimpulan"),
            require(spec, "summary"),
            color=GREEN,
            width=8.5,
            body_width=64,
        )
        summary_card.center()
        self.play(FadeIn(summary_card, shift=UP * 0.12), run_time=0.55)
        self.wait(2.0)
        return summary_card

    def render_step_cards(self, spec, active_card=None, max_steps=5):
        steps = require(spec, "steps")

        for i, step in enumerate(steps[:max_steps]):
            step_title = step.get(
                "title",
                f"{self.tr_key('step_prefix', spec, fallback='Langkah')} {i + 1}",
            )
            step_body = step.get("body", "")
            card = self.make_card(
                step_title,
                step_body,
                color=step.get("color", TEAL),
            )
            active_card = self.replace_card(active_card, card)
            self.wait(float(step.get("wait", 0.9)))

        return active_card


WicaraScene = WicaraTemplateScene


# ============================================================
# 1. NUMBER LINE QUANTITY
# ============================================================

class NumberLineQuantityTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_number_line_compare",
        "node_id": "km_d_matematika_bilangan_bulat",
        "template_id": "manim.number_line_quantity.v1",
        "phase": "D",
        "audience_level": "smp",
        "title": "Bilangan pada Garis Bilangan",
        "subtitle": "Semakin ke kanan, nilainya semakin besar.",
        "number_range": {"min": -5, "max": 5, "step": 1},
        "markers": [
            {"value": -3, "label": "-3", "description": "lebih kecil"},
            {"value": 2, "label": "2", "description": "lebih besar"},
        ],
        "highlight_values": [-3, 2],
        "operation": {
            "type": "compare",
            "from": -3,
            "to": 2,
            "label": "2 lebih besar dari -3",
        },
        "steps": [
            {
                "title": "Baca arah garis",
                "body": "Nilai pada garis bilangan makin besar jika bergerak ke kanan.",
                "color": BLUE,
            },
            {
                "title": "Tandai dua angka",
                "body": "-3 berada di kiri, sedangkan 2 berada di kanan.",
                "color": TEAL,
            },
            {
                "title": "Bandingkan posisi",
                "body": "Karena 2 lebih kanan, maka 2 bernilai lebih besar daripada -3.",
                "color": PURPLE,
            },
        ],
        "summary": "Pada garis bilangan, angka di kanan bernilai lebih besar.",
        "voiceover_script": "Perhatikan garis bilangan ini. Angka minus tiga berada di kiri, sedangkan angka dua berada di kanan.",
    }

    def construct(self):
        spec = self.SPEC

        nr = require(spec, "number_range")
        markers = require(spec, "markers")

        min_v = float(nr.get("min", -5))
        max_v = float(nr.get("max", 5))
        step = float(nr.get("step", 1))
        if max_v <= min_v:
            raise ValueError("number_range.max must be greater than min.")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Ide utama",
            "Garis bilangan membantu membandingkan posisi dan nilai angka.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)
        self.wait(0.6)

        number_line = NumberLine(
            x_range=[min_v, max_v, step],
            length=7.8,
            include_numbers=True,
            font_size=19,
        )
        number_line.move_to(LEFT * 2.0 + DOWN * 0.65)

        axis_title = Text(self.tr_text("Garis bilangan"), font_size=22, color=GRAY_A)
        axis_title.next_to(number_line, UP, buff=0.35)

        self.play(Create(number_line), FadeIn(axis_title), run_time=0.9)

        marker_groups = VGroup()
        for marker in markers:
            value = float(marker["value"])
            dot = Dot(number_line.n2p(value), radius=0.075, color=YELLOW)
            label = Text(
                clamp_text(marker.get("label", str(value)), 14),
                font_size=20,
                color=YELLOW,
            ).next_to(dot, UP, buff=0.16)

            desc = marker.get("description")
            if desc:
                desc_mob = Text(
                    clamp_text(desc, 18),
                    font_size=15,
                    color=GRAY_A,
                ).next_to(dot, DOWN, buff=0.16)
                marker_groups.add(VGroup(dot, label, desc_mob))
            else:
                marker_groups.add(VGroup(dot, label))

        marker_card = self.make_card(
            "Tandai angka",
            "Setiap angka ditempatkan sesuai posisinya di garis bilangan.",
            color=TEAL,
        )
        active_card = self.replace_card(active_card, marker_card)

        self.play(
            LaggedStart(*[FadeIn(m) for m in marker_groups], lag_ratio=0.15),
            run_time=0.85,
        )

        op = spec.get("operation", {})
        compare_group = None

        if op:
            start = float(op.get("from", markers[0]["value"]))
            end = float(op.get("to", markers[-1]["value"]))

            arrow = CurvedArrow(
                number_line.n2p(start) + DOWN * 0.82,
                number_line.n2p(end) + DOWN * 0.82,
                angle=-TAU / 6,
                color=BLUE,
                stroke_width=4,
            )

            label = Text(
                clamp_text(op.get("label", ""), 44),
                font_size=19,
                color=BLUE,
            ).next_to(arrow, DOWN, buff=0.14)

            compare_group = VGroup(arrow, label)

            compare_card = self.make_card(
                "Bandingkan",
                "Arah panah menunjukkan perpindahan dari angka kiri ke angka kanan.",
                color=PURPLE,
            )
            active_card = self.replace_card(active_card, compare_card)
            self.play(Create(arrow), FadeIn(label), run_time=0.85)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 2. ELEMENTARY ARITHMETIC BLOCKS
# ============================================================

class ElementaryArithmeticBlocksTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_arithmetic_addition",
        "node_id": "km_a_matematika_penjumlahan_dan_pengurangan_bilangan_cacah",
        "template_id": "manim.elementary_arithmetic_blocks.v1",
        "phase": "A",
        "audience_level": "sd",
        "title": "Menjumlahkan dengan Blok",
        "subtitle": "Penjumlahan berarti menggabungkan dua kelompok benda.",
        "operation_type": "addition",
        "operands": [12, 8],
        "blocks": {"model": "counters"},
        "grouping_steps": [
            {"label": "Kelompok pertama", "value": 12},
            {"label": "Kelompok kedua", "value": 8},
            {"label": "Gabungan", "value": 20},
        ],
        "result": 20,
        "steps": [
            {
                "title": "Dua kelompok",
                "body": "Kelompok biru berisi 12 blok, kelompok hijau berisi 8 blok.",
                "color": BLUE,
            },
            {
                "title": "Gabungkan",
                "body": "Untuk menjumlahkan, kita menghitung semua blok bersama.",
                "color": TEAL,
            },
            {
                "title": "Hasil akhir",
                "body": "Jumlah semua blok adalah 20.",
                "color": GREEN,
            },
        ],
        "summary": "Penjumlahan adalah proses menggabungkan dua kelompok menjadi satu jumlah.",
        "voiceover_script": "Kita punya dua kelompok blok. Saat digabung, semua blok dihitung bersama.",
    }

    def make_blocks(self, count, color=BLUE, max_cols=10, side=0.21):
        count = int(max(0, min(count, 80)))
        blocks = VGroup()

        for i in range(count):
            sq = Square(
                side_length=side,
                stroke_width=1,
                stroke_color=WHITE,
                fill_color=color,
                fill_opacity=0.86,
            )
            row = i // max_cols
            col = i % max_cols
            sq.move_to(RIGHT * col * (side + 0.055) + DOWN * row * (side + 0.055))
            blocks.add(sq)

        blocks.center()
        return blocks

    def construct(self):
        spec = self.SPEC

        op_type = require(spec, "operation_type")
        operands = require(spec, "operands")
        result = int(require(spec, "result"))

        a = int(operands[0])
        b = int(operands[1])

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        symbols = {
            "addition": "+",
            "subtraction": "-",
            "multiplication": "×",
            "division": "÷",
        }
        symbol = symbols.get(op_type, "→")

        equation = Text(
            f"{a} {symbol} {b} = {result}",
            font_size=36,
            weight=BOLD,
            color=YELLOW,
        )
        equation.next_to(title_block, DOWN, buff=0.25)

        self.play(Write(equation), run_time=0.65)

        intro_card = self.make_card(
            "Model blok",
            "Setiap kotak kecil mewakili satu benda atau satu satuan.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        if op_type == "multiplication":
            visual = VGroup()
            rows = min(a, 6)
            cols = max(1, min(b, 10))
            for r in range(rows):
                group = self.make_blocks(cols, color=TEAL, max_cols=cols, side=0.20)
                visual.add(group)
            visual.arrange(DOWN, buff=0.08)
            visual.move_to(self.visual_center())

        elif op_type == "division":
            blocks = self.make_blocks(a, color=PURPLE, max_cols=10, side=0.20)
            people = VGroup()
            for i in range(min(b, 8)):
                person = Circle(radius=0.16, color=YELLOW, fill_opacity=0.82)
                label = Text(str(i + 1), font_size=12).move_to(person)
                people.add(VGroup(person, label))
            people.arrange(RIGHT, buff=0.18)
            people.next_to(blocks, DOWN, buff=0.45)
            visual = VGroup(blocks, people).move_to(self.visual_center())

        else:
            left = self.make_blocks(a, color=BLUE, max_cols=8, side=0.21)
            right = self.make_blocks(b, color=GREEN, max_cols=8, side=0.21)

            left_label = Text(f"{a}", font_size=24, color=BLUE).next_to(left, UP, buff=0.18)
            right_label = Text(f"{b}", font_size=24, color=GREEN).next_to(right, UP, buff=0.18)

            plus = Text("+", font_size=34, weight=BOLD)

            visual = VGroup(
                VGroup(left, left_label),
                plus,
                VGroup(right, right_label),
            ).arrange(RIGHT, buff=0.45)

            visual.move_to(self.visual_center())

        self.play(FadeIn(visual, shift=UP * 0.1), run_time=0.9)

        group_card = self.make_card(
            "Gabungkan jumlah",
            "Kita melihat dua kelompok lalu menyatukannya menjadi satu hasil.",
            color=TEAL,
        )
        active_card = self.replace_card(active_card, group_card)
        self.wait(0.8)

        result_circle = Circle(radius=0.42, color=GREEN, fill_opacity=0.20)
        result_text = Text(str(result), font_size=36, weight=BOLD, color=GREEN).move_to(result_circle)
        result_group = VGroup(result_circle, result_text)
        result_group.next_to(visual, DOWN, buff=0.48)

        self.play(FadeIn(result_group, scale=0.9), run_time=0.65)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 3. FRACTION BAR PARTITION
# ============================================================

class FractionBarPartitionTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_fraction_equivalent",
        "node_id": "km_b_matematika_pecahan_senilai_dan_perbandingan_pecahan",
        "template_id": "manim.fraction_bar_partition.v1",
        "phase": "B",
        "audience_level": "sd",
        "title": "Pecahan Senilai",
        "subtitle": "Bagian yang sama dapat ditulis dengan pecahan berbeda.",
        "representations": ["fraction"],
        "fractions": [
            {"numerator": 1, "denominator": 2, "label": "1/2"},
            {"numerator": 2, "denominator": 4, "label": "2/4"},
        ],
        "partition_count": 4,
        "highlight_parts": [1, 2],
        "equivalences": [{"left": "1/2", "right": "2/4"}],
        "steps": [
            {
                "title": "Bagi sama besar",
                "body": "Pecahan harus dibagi menjadi bagian-bagian yang sama besar.",
                "color": BLUE,
            },
            {
                "title": "Bandingkan warna",
                "body": "Bagian berwarna pada 1/2 dan 2/4 sama panjang.",
                "color": TEAL,
            },
            {
                "title": "Nilainya sama",
                "body": "Karena luas bagian berwarna sama, kedua pecahan senilai.",
                "color": GREEN,
            },
        ],
        "summary": "Pecahan senilai memiliki nilai yang sama walaupun bentuk tulisannya berbeda.",
        "voiceover_script": "Satu per dua dan dua per empat terlihat berbeda, tetapi bagian yang diwarnai sama besar.",
    }

    def make_fraction_bar(self, numerator, denominator, label, color=BLUE):
        numerator = int(numerator)
        denominator = int(denominator)

        if denominator <= 0:
            raise ValueError("denominator must be positive.")

        numerator = max(0, min(numerator, denominator))

        width = 5.35
        height = 0.56
        part_width = width / denominator

        parts = VGroup()
        for i in range(denominator):
            rect = Rectangle(
                width=part_width,
                height=height,
                stroke_color=WHITE,
                stroke_width=1.15,
                fill_color=color if i < numerator else BLACK,
                fill_opacity=0.83 if i < numerator else 0.18,
            )
            rect.move_to(RIGHT * (i - (denominator - 1) / 2) * part_width)
            parts.add(rect)

        label_mob = Text(label, font_size=25, weight=BOLD, color=color)
        label_mob.next_to(parts, LEFT, buff=0.35)

        return VGroup(label_mob, parts)

    def construct(self):
        spec = self.SPEC

        fractions = require(spec, "fractions")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Bagian dari keseluruhan",
            "Pecahan menunjukkan berapa bagian yang diambil dari satu keseluruhan.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        bars = VGroup()
        colors = [BLUE, GREEN, PURPLE]

        for i, fr in enumerate(fractions[:3]):
            numerator = fr["numerator"]
            denominator = fr["denominator"]
            label = fr.get("label", f"{numerator}/{denominator}")
            bars.add(self.make_fraction_bar(numerator, denominator, label, colors[i % len(colors)]))

        bars.arrange(DOWN, aligned_edge=LEFT, buff=0.58)
        bars.move_to(self.visual_center())

        self.play(
            LaggedStart(*[FadeIn(bar, shift=UP * 0.08) for bar in bars], lag_ratio=0.18),
            run_time=1.0,
        )

        compare_card = self.make_card(
            "Bandingkan bagian",
            "Walau jumlah potongannya berbeda, bagian yang diwarnai bisa sama besar.",
            color=TEAL,
        )
        active_card = self.replace_card(active_card, compare_card)

        eqs = []
        for eq in spec.get("equivalences", [])[:2]:
            eqs.append(f"{eq.get('left')} = {eq.get('right')}")

        eq_text = None
        if eqs:
            eq_text = Text(
                "   ".join(eqs),
                font_size=30,
                color=YELLOW,
                weight=BOLD,
            )
            eq_text.next_to(bars, DOWN, buff=0.45)
            self.play(Write(eq_text), run_time=0.6)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 4. RATIO PROPORTION
# ============================================================

class RatioProportionTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_ratio_syrup",
        "node_id": "km_d_matematika_rasio",
        "template_id": "manim.ratio_proportion.v1",
        "phase": "D",
        "audience_level": "smp",
        "title": "Rasio Gula dan Air",
        "subtitle": "Rasio menjaga perbandingan dua kuantitas.",
        "context": "Membuat sirup",
        "quantities": [
            {"label": "Gula", "value": 2, "unit": "sendok"},
            {"label": "Air", "value": 5, "unit": "gelas"},
        ],
        "ratio_pairs": [["Gula", "Air"]],
        "scale_factor": 2,
        "scaling_steps": [
            {"from": "2:5", "to": "4:10", "label": "Dikali 2"},
        ],
        "steps": [
            {
                "title": "Rasio awal",
                "body": "Gula dan air dibandingkan 2 banding 5.",
                "color": BLUE,
            },
            {
                "title": "Skalakan bersama",
                "body": "Jika gula dikali 2, air juga harus dikali 2.",
                "color": TEAL,
            },
            {
                "title": "Proporsi tetap",
                "body": "Perbandingan tetap sama karena keduanya dikalikan faktor yang sama.",
                "color": GREEN,
            },
        ],
        "summary": "Proporsi terjaga jika semua kuantitas dikalikan faktor yang sama.",
        "voiceover_script": "Rasio dua banding lima berarti dua sendok gula dipasangkan dengan lima gelas air.",
    }

    def make_quantity_bar(self, label, value, unit, color, max_value):
        value = float(value)
        width = max(0.75, min(4.65, 4.65 * value / max_value))

        bar = Rectangle(
            width=width,
            height=0.40,
            stroke_color=WHITE,
            fill_color=color,
            fill_opacity=0.84,
        )

        text = Text(
            f"{label}: {value:g} {unit}",
            font_size=21,
            color=color,
            weight=BOLD,
        )
        text.next_to(bar, LEFT, buff=0.25)

        return VGroup(text, bar)

    def construct(self):
        spec = self.SPEC

        quantities = require(spec, "quantities")
        max_value = max(float(q.get("value", 1)) for q in quantities[:4])

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        context = Text(
            clamp_text(
                spec.get(
                    "context",
                    self.tr_key("ratio_context_default", spec, fallback="Konteks rasio"),
                ),
                60,
            ),
            font_size=23,
            color=GRAY_A,
        )
        context.next_to(title_block, DOWN, buff=0.24)
        self.play(FadeIn(context), run_time=0.45)

        intro_card = self.make_card(
            "Apa itu rasio?",
            "Rasio membandingkan dua kuantitas dalam satu situasi.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        colors = [BLUE, GREEN, PURPLE, ORANGE]
        bars = VGroup()

        for i, q in enumerate(quantities[:4]):
            bars.add(
                self.make_quantity_bar(
                    q.get("label", f"Q{i + 1}"),
                    q.get("value", 1),
                    q.get("unit", ""),
                    colors[i % len(colors)],
                    max_value=max_value,
                )
            )

        bars.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        bars.move_to(self.visual_center())

        self.play(
            LaggedStart(*[FadeIn(bar, shift=UP * 0.08) for bar in bars], lag_ratio=0.15),
            run_time=0.9,
        )

        scale_factor = spec.get("scale_factor")
        scale_text = None

        if scale_factor is not None:
            scale_text = Text(
                f"Faktor skala: ×{scale_factor}",
                font_size=27,
                color=YELLOW,
                weight=BOLD,
            )
            scale_text.next_to(bars, DOWN, buff=0.42)
            self.play(Write(scale_text), run_time=0.5)

        for step in spec.get("scaling_steps", [])[:1]:
            transform_text = Text(
                f"{step.get('from')}  →  {step.get('to')}",
                font_size=29,
                color=GREEN,
                weight=BOLD,
            )
            transform_text.next_to(bars, UP, buff=0.34)
            self.play(FadeIn(transform_text, shift=UP * 0.08), run_time=0.5)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 5. EQUATION BALANCE
# ============================================================

class EquationBalanceTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_equation_balance",
        "node_id": "km_d_matematika_persamaan_linear_satu_variabel",
        "template_id": "manim.equation_balance.v1",
        "phase": "D",
        "audience_level": "smp",
        "title": "Persamaan sebagai Timbangan",
        "subtitle": "Operasi di kiri juga harus dilakukan di kanan.",
        "equation": "2x + 3 = 11",
        "left_expression": "2x + 3",
        "right_expression": "11",
        "solution_steps": [
            {
                "operation": "Kurangi 3",
                "left_result": "2x",
                "right_result": "8",
                "explanation": "Kurangi 3 di kedua sisi agar keseimbangan tetap terjaga.",
            },
            {
                "operation": "Bagi 2",
                "left_result": "x",
                "right_result": "4",
                "explanation": "Bagi kedua sisi dengan 2 supaya x berdiri sendiri.",
            },
        ],
        "final_solution": "x = 4",
        "steps": [
            {
                "title": "Jaga dua ruas",
                "body": "Ruas kiri dan ruas kanan harus tetap setara.",
                "color": BLUE,
            },
            {
                "title": "Lakukan operasi sama",
                "body": "Apa yang dilakukan ke kiri juga dilakukan ke kanan.",
                "color": TEAL,
            },
            {
                "title": "Temukan x",
                "body": "Setelah x berdiri sendiri, kita mendapatkan nilainya.",
                "color": GREEN,
            },
        ],
        "summary": "Nilai x ditemukan dengan menjaga kedua ruas tetap setara.",
        "voiceover_script": "Bayangkan persamaan seperti timbangan. Jika satu sisi diubah, sisi lainnya juga harus diubah.",
    }

    def make_balance(self):
        beam = Line(
            LEFT * 2.75,
            RIGHT * 2.75,
            color=GRAY_B,
            stroke_width=7,
        )
        pivot = Triangle(color=GRAY_B, fill_opacity=0.80).scale(0.36)
        pivot.next_to(beam, DOWN, buff=0.02)

        left_anchor = Dot(LEFT * 2.00, radius=0.01, color=GRAY_B)
        right_anchor = Dot(RIGHT * 2.00, radius=0.01, color=GRAY_B)

        left_rope = Line(
            left_anchor.get_center(),
            left_anchor.get_center() + DOWN * 0.70,
            color=GRAY_B,
            stroke_width=3,
        )
        right_rope = Line(
            right_anchor.get_center(),
            right_anchor.get_center() + DOWN * 0.70,
            color=GRAY_B,
            stroke_width=3,
        )

        left_plate = RoundedRectangle(
            corner_radius=0.04,
            width=1.70,
            height=0.15,
            stroke_color=BLUE,
            stroke_width=3,
            fill_color=BLUE_E,
            fill_opacity=0.45,
        ).move_to(left_rope.get_end())
        right_plate = RoundedRectangle(
            corner_radius=0.04,
            width=1.70,
            height=0.15,
            stroke_color=GREEN,
            stroke_width=3,
            fill_color=GREEN_E,
            fill_opacity=0.45,
        ).move_to(right_rope.get_end())

        balance = VGroup(
            beam,
            pivot,
            left_anchor,
            right_anchor,
            left_rope,
            right_rope,
            left_plate,
            right_plate,
        )
        balance.move_to(self.visual_center())
        return balance, pivot, left_plate, right_plate

    def make_plate_text(self, value, plate, color):
        text_mob = Text(str(value), font_size=31, color=color, weight=BOLD)
        text_mob.next_to(plate, UP, buff=0.23)
        text_mob.add_updater(lambda m, target=plate: m.next_to(target, UP, buff=0.23))
        return text_mob

    def construct(self):
        spec = self.SPEC

        equation = require(spec, "equation")
        solution_steps = require(spec, "solution_steps")
        final_solution = require(spec, "final_solution")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        balance, pivot, left_plate, right_plate = self.make_balance()
        self.play(Create(balance), run_time=0.85)

        equation_mob = Text(equation, font_size=34, weight=BOLD, color=YELLOW)
        equation_bg = BackgroundRectangle(
            equation_mob,
            color=BLACK,
            fill_opacity=0.78,
            buff=0.12,
        )
        equation_group = VGroup(equation_bg, equation_mob)
        equation_group.next_to(balance, UP, buff=0.46)
        self.play(FadeIn(equation_group, shift=DOWN * 0.05), run_time=0.6)

        intro_card = self.make_card(
            "Persamaan = seimbang",
            "Tanda sama dengan berarti ruas kiri dan kanan memiliki nilai yang setara.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        left = self.make_plate_text(spec.get("left_expression", ""), left_plate, BLUE)
        right = self.make_plate_text(spec.get("right_expression", ""), right_plate, GREEN)

        self.play(FadeIn(left), FadeIn(right), run_time=0.55)

        current_tilt = 0.0

        def tilt_to(target, run_time=0.35):
            nonlocal current_tilt
            delta = float(target) - float(current_tilt)
            if abs(delta) < 1e-4:
                return
            self.play(
                Rotate(balance, angle=delta, about_point=pivot.get_center()),
                run_time=run_time,
            )
            current_tilt = float(target)

        # Show that this is a dynamic balance, not a static drawing.
        tilt_to(-0.08, run_time=0.28)
        tilt_to(0.05, run_time=0.32)
        tilt_to(0.0, run_time=0.30)

        for step_index, step in enumerate(solution_steps[:4]):
            card = self.make_card(
                step.get("operation", "Operasi"),
                step.get("explanation", ""),
                color=TEAL,
            )
            active_card = self.replace_card(active_card, card)

            lead_tilt = -0.06 if step_index % 2 == 0 else 0.06
            tilt_to(lead_tilt, run_time=0.30)

            new_left = self.make_plate_text(step.get("left_result", ""), left_plate, BLUE)
            new_right = self.make_plate_text(step.get("right_result", ""), right_plate, GREEN)
            new_left.move_to(left)
            new_right.move_to(right)

            self.play(
                ReplacementTransform(left, new_left),
                ReplacementTransform(right, new_right),
                run_time=0.6,
            )
            left = new_left
            right = new_right
            tilt_to(0.0, run_time=0.35)

            self.wait(0.45)

        final = Text(final_solution, font_size=40, color=YELLOW, weight=BOLD)
        final.next_to(balance, DOWN, buff=0.52)
        self.play(Write(final), run_time=0.6)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 6. SEQUENCE PATTERN
# ============================================================

class SequencePatternTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_sequence_pattern",
        "node_id": "km_c_matematika_pola_bilangan_perkalian_dan_pembagian",
        "template_id": "manim.sequence_pattern.v1",
        "phase": "C",
        "audience_level": "sd",
        "title": "Pola Bilangan",
        "subtitle": "Pola dapat diteruskan jika aturan perubahannya diketahui.",
        "terms": [2, 4, 6, 8],
        "visual_pattern_type": "growing_dots",
        "rule": "Tambah 2 setiap langkah",
        "table_values": [
            {"n": 1, "value": 2},
            {"n": 2, "value": 4},
            {"n": 3, "value": 6},
            {"n": 4, "value": 8},
        ],
        "target_term": {"n": 5, "value": 10},
        "steps": [
            {
                "title": "Amati suku",
                "body": "Nilai suku bertambah dari 2, ke 4, ke 6, lalu ke 8.",
                "color": BLUE,
            },
            {
                "title": "Cari perubahan",
                "body": "Setiap langkah bertambah 2.",
                "color": TEAL,
            },
            {
                "title": "Lanjutkan pola",
                "body": "Jika ditambah 2 lagi, suku berikutnya adalah 10.",
                "color": GREEN,
            },
        ],
        "summary": "Aturan pola membantu kita memprediksi suku berikutnya.",
        "voiceover_script": "Lihat deret dua, empat, enam, delapan. Setiap langkah bertambah dua.",
    }

    def make_term_card(self, value, label, color=BLUE):
        value = int(max(0, min(value, 36)))

        dots = VGroup()
        for _ in range(value):
            dots.add(Dot(radius=0.045, color=YELLOW))

        if value > 0:
            cols = max(1, min(6, int(math.ceil(math.sqrt(value)))))
            dots.arrange_in_grid(cols=cols, buff=0.065)

        box = RoundedRectangle(
            width=max(0.90, dots.width + 0.35),
            height=max(0.72, dots.height + 0.42),
            corner_radius=0.12,
            color=color,
            stroke_width=1.4,
            fill_color=BLACK,
            fill_opacity=0.20,
        )

        dots.move_to(box.get_center())
        txt = Text(str(label), font_size=15, color=WHITE).next_to(box, DOWN, buff=0.10)

        return VGroup(box, dots, txt)

    def make_table(self, table_values):
        headers = VGroup(
            Text("n", font_size=18, color=YELLOW),
            Text("nilai", font_size=18, color=YELLOW),
        ).arrange(RIGHT, buff=0.45)

        rows = VGroup()
        for item in table_values[:5]:
            row = VGroup(
                Text(str(item.get("n")), font_size=17),
                Text(str(item.get("value")), font_size=17),
            ).arrange(RIGHT, buff=0.45)
            rows.add(row)

        table = VGroup(headers, rows.arrange(DOWN, buff=0.12, aligned_edge=LEFT))
        table.arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        box = RoundedRectangle(
            width=table.width + 0.4,
            height=table.height + 0.35,
            corner_radius=0.12,
            color=GRAY_B,
            fill_color=BLACK,
            fill_opacity=0.35,
        )
        table.move_to(box)
        return VGroup(box, table)

    def construct(self):
        spec = self.SPEC

        terms = require(spec, "terms")
        rule = require(spec, "rule")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Pola bertumbuh",
            "Setiap suku dapat dilihat sebagai gambar atau jumlah yang berubah teratur.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        term_cards = VGroup()
        for i, term in enumerate(terms[:5]):
            term_cards.add(self.make_term_card(term, f"Suku {i + 1}: {term}", color=BLUE))

        term_cards.arrange(RIGHT, buff=0.24)
        term_cards.scale(0.82)
        term_cards.move_to(LEFT * 2.15 + DOWN * 0.25)

        self.play(
            LaggedStart(*[FadeIn(card, shift=UP * 0.08) for card in term_cards], lag_ratio=0.16),
            run_time=1.0,
        )

        rule_mob = Text(rule, font_size=25, color=YELLOW, weight=BOLD)
        rule_mob.next_to(term_cards, DOWN, buff=0.35)
        self.play(Write(rule_mob), run_time=0.55)

        table_values = spec.get("table_values", [])
        table = None
        if table_values:
            table = self.make_table(table_values)
            table.scale(0.86)
            table.next_to(term_cards, RIGHT, buff=0.55)
            self.play(FadeIn(table, shift=LEFT * 0.12), run_time=0.6)

        target = spec.get("target_term")
        if isinstance(target, dict):
            target_mob = Text(
                f"Suku ke-{target.get('n')}: {target.get('value')}",
                font_size=26,
                color=GREEN,
                weight=BOLD,
            )
            target_mob.next_to(rule_mob, DOWN, buff=0.22)
            self.play(FadeIn(target_mob), run_time=0.5)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 7. GEOMETRY AREA VOLUME
# ============================================================

class GeometryAreaVolumeTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_area_rectangle",
        "node_id": "km_b_matematika_keliling_dan_luas_persegi_persegi_panjang",
        "template_id": "manim.geometry_area_volume.v1",
        "phase": "B",
        "audience_level": "sd",
        "title": "Luas Persegi Panjang",
        "subtitle": "Luas dapat dihitung dari panjang dan lebar.",
        "shape_type": "rectangle",
        "dimensions": {"length": 6, "width": 4, "unit": "cm"},
        "transformations": [
            {"type": "fill_unit_squares", "label": "Isi dengan persegi satuan"},
        ],
        "formula_latex": "L = p \\times l",
        "highlight_features": ["panjang", "lebar", "luas"],
        "steps": [
            {
                "title": "Ukur dua sisi",
                "body": "Persegi panjang punya panjang dan lebar.",
                "color": BLUE,
            },
            {
                "title": "Lihat kotak satuan",
                "body": "Luas menunjukkan banyaknya kotak satuan yang menutup daerah.",
                "color": TEAL,
            },
            {
                "title": "Kalikan",
                "body": "Luas diperoleh dari panjang dikali lebar.",
                "color": GREEN,
            },
        ],
        "summary": "Luas persegi panjang adalah panjang dikali lebar.",
        "voiceover_script": "Untuk mencari luas persegi panjang, kita melihat panjang dan lebarnya.",
    }

    def make_rectangle_grid(self, cols, rows):
        grid = VGroup()
        for r in range(rows):
            for c in range(cols):
                sq = Square(
                    side_length=0.34,
                    stroke_color=GRAY_B,
                    stroke_width=1,
                    fill_color=BLUE,
                    fill_opacity=0.10,
                )
                sq.move_to(RIGHT * c * 0.34 + DOWN * r * 0.34)
                grid.add(sq)
        grid.center()
        return grid

    def construct(self):
        spec = self.SPEC

        shape_type = require(spec, "shape_type")
        dimensions = require(spec, "dimensions")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Apa itu luas?",
            "Luas adalah banyaknya daerah yang ditutupi oleh satuan persegi.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        unit = dimensions.get("unit", "")

        if shape_type in ["rectangle", "persegi_panjang"]:
            length = float(dimensions.get("length", 6))
            width = float(dimensions.get("width", 4))

            shape = Rectangle(width=4.2, height=2.5, color=BLUE, fill_opacity=0.14)

            length_label = Text(f"{length:g} {unit}", font_size=21)
            length_label.next_to(shape, DOWN, buff=0.14)

            width_label = Text(f"{width:g} {unit}", font_size=21)
            width_label.next_to(shape, LEFT, buff=0.14)

            visual = VGroup(shape, length_label, width_label)
            visual.move_to(self.visual_center())

            self.play(Create(shape), FadeIn(length_label), FadeIn(width_label), run_time=0.85)

            grid = self.make_rectangle_grid(cols=int(min(length, 12)), rows=int(min(width, 8)))
            grid.set(width=shape.width, height=shape.height)
            grid.move_to(shape)
            self.play(FadeIn(grid), run_time=0.75)

        elif shape_type in ["triangle", "segitiga"]:
            shape = Polygon(
                LEFT * 2 + DOWN,
                RIGHT * 2 + DOWN,
                UP * 1.4,
                color=BLUE,
                fill_opacity=0.16,
            )
            visual = VGroup(shape).move_to(self.visual_center())
            self.play(Create(shape), run_time=0.85)

        elif shape_type in ["circle", "lingkaran"]:
            shape = Circle(radius=1.45, color=BLUE, fill_opacity=0.16)
            visual = VGroup(shape).move_to(self.visual_center())
            self.play(Create(shape), run_time=0.85)

        else:
            shape = Square(side_length=2.4, color=BLUE, fill_opacity=0.16)
            visual = VGroup(shape).move_to(self.visual_center())
            self.play(Create(shape), run_time=0.85)

        formula = spec.get("formula_latex")
        if formula:
            formula_mob = MathTex(formula, font_size=38, color=YELLOW)
            formula_mob.next_to(visual, DOWN, buff=0.45)
            self.play(Write(formula_mob), run_time=0.6)

        features = spec.get("highlight_features", [])
        if features:
            feature_text = Text(
                f"{self.tr_key('highlight_prefix', spec, fallback='Sorot:')} "
                + ", ".join([str(f) for f in features[:3]]),
                font_size=20,
                color=YELLOW,
            )
            feature_text.next_to(visual, UP, buff=0.28)
            self.play(FadeIn(feature_text), run_time=0.45)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 8. GRAPH EXPLANATION
# ============================================================

class GraphExplanationTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_graph_quadratic_clean",
        "node_id": "km_e_matematika_fungsi_kuadrat",
        "template_id": "manim.graph_explanation.v1",
        "phase": "E",
        "audience_level": "sma",
        "title": "Grafik Fungsi Kuadrat",
        "subtitle": "Parabola membantu kita melihat perubahan nilai fungsi.",
        "formula_latex": "f(x)=x^2",
        "function": {"type": "quadratic", "params": {"a": 1, "b": 0, "c": 0}},
        "x_range": [-3, 3, 1],
        "y_range": [-1, 9, 1],
        "x_label": "x",
        "y_label": "f(x)",
        "graph_label": "kurva fungsi",
        "moving_label": "titik",
        "x_path": [-2, -1, 0, 1, 2],
        "highlight_x": 1,
        "show_slope": True,
        "slope_text": "Kemiringan lokal menunjukkan seberapa cepat nilai fungsi berubah di sekitar titik itu.",
        "steps": [
            {
                "title": "Baca sumbu",
                "body": "Sumbu horizontal menunjukkan nilai x, sedangkan sumbu vertikal menunjukkan nilai f(x).",
                "color": BLUE,
            },
            {
                "title": "Ikuti titik",
                "body": "Saat x berubah, titik pada grafik ikut berpindah sesuai nilai fungsi.",
                "color": TEAL,
            },
            {
                "title": "Lihat kemiringan",
                "body": "Garis singgung membantu melihat laju perubahan lokal pada grafik.",
                "color": RED,
            },
        ],
        "summary": "Grafik membuat hubungan antara x dan f(x) terlihat lebih jelas.",
        "voiceover_script": "Sekarang kita melihat fungsi kuadrat melalui grafik.",
    }

    def make_axes(self, spec):
        x_range = require(spec, "x_range")
        y_range = require(spec, "y_range")

        if len(x_range) != 3:
            raise ValueError("x_range must be [min, max, step].")

        if len(y_range) != 3:
            raise ValueError("y_range must be [min, max, step].")

        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=6.75,
            y_length=3.85,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 16},
        )
        axes.move_to(self.visual_center())

        axis_labels = axes.get_axis_labels(
            x_label=Text(spec.get("x_label", "x"), font_size=20),
            y_label=Text(spec.get("y_label", "y"), font_size=20),
        )

        return axes, axis_labels

    def construct(self):
        spec = self.SPEC

        require(spec, "function")
        require(spec, "x_range")
        require(spec, "y_range")

        f = build_function(spec.get("function", {}))

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        formula = MathTex(spec.get("formula_latex", "f(x)=x"), font_size=34, color=YELLOW)
        formula.next_to(title_block, DOWN, buff=0.18)
        self.play(Write(formula), run_time=0.75)

        axes, axis_labels = self.make_axes(spec)
        self.play(Create(axes), FadeIn(axis_labels), run_time=1.0)

        x_range = spec["x_range"]
        graph = axes.plot(f, x_range=[x_range[0], x_range[1]], color=BLUE)

        graph_label = Text(
            clamp_text(
                spec.get(
                    "graph_label",
                    self.tr_key("graph_function_default", spec, fallback="grafik fungsi"),
                ),
                24,
            ),
            font_size=17,
            color=BLUE,
        )
        graph_label.next_to(axes, DOWN, buff=0.15)

        self.play(Create(graph), FadeIn(graph_label), run_time=1.25)

        active_card = self.replace_card(
            None,
            self.make_card(
                "Apa yang dilihat?",
                "Grafik menunjukkan hubungan antara nilai x dan nilai f(x).",
                color=BLUE,
            ),
        )
        self.wait(0.6)

        x_path = spec.get("x_path", [x_range[0], x_range[1]])
        if len(x_path) < 2:
            x_path = [x_range[0], x_range[1]]

        tracker = ValueTracker(float(x_path[0]))

        dot = always_redraw(
            lambda: Dot(
                axes.c2p(tracker.get_value(), f(tracker.get_value())),
                color=YELLOW,
                radius=0.075,
            )
        )

        dot_label = always_redraw(
            lambda: Text(
                clamp_text(
                    spec.get(
                        "moving_label",
                        self.tr_key("moving_point_default", spec, fallback="titik"),
                    ),
                    18,
                ),
                font_size=15,
                color=YELLOW,
            ).next_to(dot, UP, buff=0.10)
        )

        vertical_line = always_redraw(
            lambda: DashedLine(
                axes.c2p(tracker.get_value(), 0),
                axes.c2p(tracker.get_value(), f(tracker.get_value())),
                stroke_color=YELLOW,
                stroke_opacity=0.52,
                stroke_width=2,
            )
        )

        self.play(FadeIn(dot), FadeIn(dot_label), Create(vertical_line), run_time=0.6)

        active_card = self.replace_card(
            active_card,
            self.make_card(
                "Titik bergerak",
                "Saat x berubah, posisi titik di grafik ikut berubah.",
                color=TEAL,
            ),
        )

        for target_x in x_path[1:]:
            self.play(
                tracker.animate.set_value(float(target_x)),
                run_time=1.0,
                rate_func=smooth,
            )

        tangent_group = None

        if bool(spec.get("show_slope", False)):
            highlight_x = float(spec.get("highlight_x", 1))
            slope = numerical_slope(f, highlight_x)

            tangent_group = axes.get_secant_slope_group(
                x=highlight_x,
                graph=graph,
                dx=0.01,
                secant_line_length=3.5,
                secant_line_color=RED,
            )

            slope_body = spec.get(
                "slope_text",
                f"Kemiringan lokal di x={highlight_x:g} kira-kira {slope:.2f}.",
            )

            active_card = self.replace_card(
                active_card,
                self.make_card("Laju perubahan lokal", slope_body, color=RED),
            )

            self.play(Create(tangent_group), run_time=0.85)
            self.wait(0.7)

        active_card = self.render_step_cards(spec, active_card=active_card)

        self.clean_summary(
            spec,
            active_card=active_card,
            extra_fadeouts=[dot, dot_label, vertical_line],
        )


# ============================================================
# 9. MOTION KINEMATICS
# ============================================================

class MotionKinematicsTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_motion_glb",
        "node_id": "km_e_fisika_gerak_lurus_beraturan",
        "template_id": "manim.motion_kinematics.v1",
        "phase": "E",
        "audience_level": "sma",
        "title": "Gerak Lurus Beraturan",
        "subtitle": "Posisi bertambah sama setiap selang waktu.",
        "scenario": "Gerak lurus beraturan",
        "time_points": [0, 1, 2, 3, 4],
        "position_data": [0, 2, 4, 6, 8],
        "velocity_data": [2, 2, 2, 2, 2],
        "acceleration": 0,
        "graph_type": "position_time",
        "steps": [
            {
                "title": "Kecepatan tetap",
                "body": "Benda menempuh jarak yang sama tiap detik.",
                "color": BLUE,
            },
            {
                "title": "Jejak gerak",
                "body": "Posisi benda bergeser teratur sepanjang lintasan.",
                "color": TEAL,
            },
            {
                "title": "Grafik lurus",
                "body": "Posisi terhadap waktu membentuk garis lurus.",
                "color": GREEN,
            },
        ],
        "summary": "GLB memiliki kecepatan tetap dan percepatan nol.",
        "voiceover_script": "Pada gerak lurus beraturan, posisi bertambah secara teratur setiap waktu.",
    }

    def construct(self):
        spec = self.SPEC

        time_points = require(spec, "time_points")
        position_data = require(spec, "position_data")

        times = [float(x) for x in time_points]
        positions = [float(x) for x in position_data]

        if len(times) != len(positions):
            raise ValueError("time_points and position_data must have same length.")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Gerak terhadap waktu",
            "Kita lihat benda bergerak, lalu hubungkan dengan grafik posisinya.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        track = Line(LEFT * 4.1, RIGHT * 1.0, color=GRAY_B)
        track.move_to(LEFT * 1.55 + UP * 0.70)

        start_label = Text(self.tr_text("awal"), font_size=16, color=GRAY_A).next_to(
            track.get_start(), DOWN, buff=0.12
        )
        end_label = Text(self.tr_text("akhir"), font_size=16, color=GRAY_A).next_to(
            track.get_end(), DOWN, buff=0.12
        )

        car = RoundedRectangle(
            width=0.58,
            height=0.34,
            corner_radius=0.08,
            color=BLUE,
            fill_opacity=0.85,
        )
        car.move_to(track.get_start())

        self.play(Create(track), FadeIn(start_label), FadeIn(end_label), FadeIn(car), run_time=0.7)

        min_pos = min(positions)
        max_pos = max(positions)
        span = max(1e-6, max_pos - min_pos)

        def pos_to_point(p):
            alpha = (p - min_pos) / span
            return interpolate(track.get_start(), track.get_end(), alpha)

        path_points = [pos_to_point(p) for p in positions]
        path = VMobject(color=YELLOW)
        path.set_points_as_corners(path_points)

        active_card = self.replace_card(
            active_card,
            self.make_card("Benda bergerak", "Posisi benda berubah seiring waktu.", color=TEAL),
        )

        self.play(MoveAlongPath(car, path), Create(path), run_time=1.4)

        y_max = max(positions) + 1
        x_step = max(1, (max(times) - min(times)) / 4)

        axes = Axes(
            x_range=[min(times), max(times), x_step],
            y_range=[min(0, min(positions)), y_max, max(1, y_max / 4)],
            x_length=5.1,
            y_length=2.55,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 14},
        )
        axes.move_to(LEFT * 1.55 + DOWN * 1.55)

        graph_points = [axes.c2p(t, p) for t, p in zip(times, positions)]
        graph = VMobject(color=GREEN)
        graph.set_points_as_corners(graph_points)

        graph_label = Text(
            spec.get(
                "scenario",
                self.tr_key("motion_graph_default", spec, fallback="Grafik gerak"),
            ),
            font_size=20,
            color=GREEN,
        )
        graph_label.next_to(axes, UP, buff=0.10)

        active_card = self.replace_card(
            active_card,
            self.make_card("Grafik posisi", "Grafik menunjukkan hubungan antara waktu dan posisi.", color=GREEN),
        )

        self.play(Create(axes), Create(graph), FadeIn(graph_label), run_time=0.95)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)


# ============================================================
# 10. FORCE DIAGRAM
# ============================================================

class ForceDiagramTemplate(WicaraTemplateScene):
    SPEC = {
        "id": "sample_force_resultant",
        "node_id": "km_d_ipa_gaya_dan_resultan_gaya",
        "template_id": "manim.force_diagram.v1",
        "phase": "D",
        "audience_level": "smp",
        "title": "Resultan Gaya",
        "subtitle": "Gaya berlawanan saling mengurangi.",
        "object": {"type": "box", "label": "Kotak"},
        "forces": [
            {"label": "F1", "magnitude": 10, "unit": "N", "direction": "right"},
            {"label": "F2", "magnitude": 4, "unit": "N", "direction": "left"},
        ],
        "resultant": {"magnitude": 6, "unit": "N", "direction": "right"},
        "motion_response": "Benda cenderung bergerak ke kanan.",
        "force_scale": 0.25,
        "steps": [
            {
                "title": "Dua gaya",
                "body": "Kotak mendapat gaya ke kanan dan gaya ke kiri.",
                "color": BLUE,
            },
            {
                "title": "Bandingkan besar",
                "body": "Gaya kanan lebih besar daripada gaya kiri.",
                "color": TEAL,
            },
            {
                "title": "Resultan",
                "body": "Selisih gaya menghasilkan resultan 6 N ke kanan.",
                "color": GREEN,
            },
        ],
        "summary": "Arah resultan gaya menentukan kecenderungan gerak benda.",
        "voiceover_script": "Kotak mendapat gaya ke kanan dan ke kiri. Karena gaya kanan lebih besar, resultannya ke kanan.",
    }

    def construct(self):
        spec = self.SPEC

        obj_spec = require(spec, "object")
        forces = require(spec, "forces")
        resultant = require(spec, "resultant")

        title_block = self.make_title_block(spec)
        self.play(FadeIn(title_block, shift=DOWN * 0.08), run_time=0.6)

        intro_card = self.make_card(
            "Gaya sebagai panah",
            "Panjang panah menunjukkan besar gaya, arah panah menunjukkan arah gaya.",
            color=BLUE,
        )
        active_card = self.replace_card(None, intro_card)

        body_shape = RoundedRectangle(
            width=1.45,
            height=0.85,
            corner_radius=0.12,
            color=BLUE,
            fill_opacity=0.62,
        )

        body_label = Text(
            obj_spec.get("label", self.tr_key("object_default", spec, fallback="Benda")),
            font_size=22,
        ).move_to(body_shape)

        body = VGroup(body_shape, body_label)
        body.move_to(self.visual_center())

        self.play(FadeIn(body), run_time=0.55)

        scale = float(spec.get("force_scale", 0.22))
        force_mobs = VGroup()

        for i, force in enumerate(forces[:4]):
            mag = float(force["magnitude"])
            direction = force.get("direction", "right")
            unit = force.get("unit", "N")
            vec = direction_vector(direction)

            length = max(0.55, min(2.35, mag * scale))

            if direction in ["right", "left"]:
                start = body.get_center()
                start += (RIGHT if direction == "right" else LEFT) * 0.78
                start += UP * (0.26 - i * 0.18)
            else:
                start = body.get_center()
                start += (UP if direction == "up" else DOWN) * 0.48
                start += RIGHT * (i * 0.2)

            arrow = Arrow(
                start,
                start + vec * length,
                buff=0,
                color=YELLOW,
                stroke_width=5,
            )

            label = Text(
                f"{force.get('label', 'F')} = {mag:g} {unit}",
                font_size=18,
                color=YELLOW,
            )

            if direction in ["right", "left"]:
                label.next_to(arrow, UP, buff=0.10)
            else:
                label.next_to(arrow, RIGHT, buff=0.10)

            force_mobs.add(VGroup(arrow, label))

        active_card = self.replace_card(
            active_card,
            self.make_card("Gaya-gaya bekerja", "Setiap panah menunjukkan gaya yang bekerja pada benda.", color=TEAL),
        )

        self.play(
            LaggedStart(*[Create(m) for m in force_mobs], lag_ratio=0.16),
            run_time=0.95,
        )

        rmag = float(resultant["magnitude"])
        rdir = resultant.get("direction", "right")
        runit = resultant.get("unit", "N")
        rvec = direction_vector(rdir)

        start = body.get_center() + DOWN * 1.18
        rarrow = Arrow(
            start,
            start + rvec * max(0.70, min(2.50, rmag * scale)),
            buff=0,
            color=GREEN,
            stroke_width=6,
        )

        direction_word = self.tr_key("direction_to", spec, fallback="ke")
        resultant_label = self.tr_key("resultant_label", spec, fallback="Resultan")
        rlabel = Text(
            f"{resultant_label} = {rmag:g} {runit} {direction_word} {rdir}",
            font_size=22,
            color=GREEN,
            weight=BOLD,
        )
        rlabel.next_to(rarrow, DOWN, buff=0.14)

        active_card = self.replace_card(
            active_card,
            self.make_card("Resultan gaya", "Gaya berlawanan dikurangkan untuk mendapatkan resultannya.", color=GREEN),
        )

        self.play(Create(rarrow), FadeIn(rlabel), run_time=0.7)

        response = spec.get("motion_response", "")
        response_mob = None
        if response:
            response_mob = Text(
                clamp_text(response, 65),
                font_size=21,
                color=GRAY_A,
            )
            response_mob.next_to(rlabel, DOWN, buff=0.20)
            self.play(FadeIn(response_mob), run_time=0.4)

        active_card = self.render_step_cards(spec, active_card=active_card)
        self.clean_summary(spec, active_card=active_card)
