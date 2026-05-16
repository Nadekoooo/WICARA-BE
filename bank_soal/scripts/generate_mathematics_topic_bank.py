import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GRAPH_PATH = ROOT / "backend" / "app" / "modules" / "curriculum" / "data" / "wicara_kurikulum_merdeka_graph_complete.json"
SEED_DIR = ROOT / "backend" / "bank_soal" / "seeds"


PHASE_GROUPS = {
    "elementary": {"phases": {"A", "B", "C"}, "grade_band": "elementary", "level_short": "el"},
    "junior_high": {"phases": {"D"}, "grade_band": "junior_high", "level_short": "jh"},
    "senior_high": {"phases": {"E", "F"}, "grade_band": "senior_high", "level_short": "sh"},
}


ASSESSMENT_VARIANTS = {
    "pretest": {
        "short": "pre",
        "helper_text": "Choose the topic that best matches the key skill or idea.",
        "prompt_templates": [
            "Which topic best matches this prerequisite skill: {description}?",
            "Before starting this strand, which topic would assess {description}?",
            "Which topic should a learner know first for {description}?",
        ],
    },
    "daily_quiz": {
        "short": "daily",
        "helper_text": "Pick the topic that best matches the idea.",
        "prompt_templates": [
            "Which topic is about {description}?",
            "A quick review of {description} belongs to which topic?",
            "Which topic should be reviewed for {description}?",
        ],
    },
    "posttest": {
        "short": "post",
        "helper_text": "Choose the topic that best fits the full mathematical idea.",
        "prompt_templates": [
            "After learning this strand, which topic best fits {description}?",
            "Which topic most directly applies to {description}?",
            "Which topic best represents this learned idea: {description}?",
        ],
    },
    "workspace_quiz": {
        "short": "work",
        "helper_text": "Pick the best topic match.",
        "prompt_templates": [
            "Topic for {description}?",
            "Which topic matches {description}?",
            "Which topic fits {description}?",
        ],
    },
}


TOKEN_MAP = {
    "akar": "roots",
    "aljabar": "algebra",
    "anuitas": "annuities",
    "antar": "between",
    "aplikasi": "applications",
    "aritmetika": "arithmetic",
    "asosiatif": "associative",
    "asosiasi": "association",
    "awal": "introductory",
    "bangun": "shapes",
    "barisan": "sequences",
    "batang": "bar",
    "bebas": "independent",
    "bentuk": "forms",
    "berat": "weight",
    "berkembang": "growing",
    "bernilai": "valued",
    "berpangkat": "powers",
    "bersyarat": "conditional",
    "besar": "large",
    "besar": "large",
    "biasa": "common",
    "bivariat": "bivariate",
    "bola": "spheres",
    "box": "box",
    "bulat": "integers",
    "bunga": "interest",
    "busur": "arcs",
    "cacah": "whole",
    "campuran": "mixed",
    "cartesius": "cartesian",
    "chart": "chart",
    "data": "data",
    "dasar": "basic",
    "datar": "plane",
    "decimals": "decimals",
    "desimal": "decimals",
    "diagram": "charts",
    "dilatasi": "dilations",
    "distributif": "distributive",
    "domain": "domain",
    "dot": "dot",
    "dua": "two",
    "ekspresi": "expressions",
    "eksponensial": "exponential",
    "ekuivalen": "equivalent",
    "estimasi": "estimation",
    "evaluasi": "evaluation",
    "faktorisasi": "factorization",
    "faktor": "factors",
    "finansial": "financial",
    "flow": "flow",
    "frekuensi": "frequency",
    "fungsi": "functions",
    "garis": "lines",
    "geometri": "geometry",
    "grafik": "graphs",
    "harapan": "expected",
    "histogram": "histograms",
    "hubungan": "relationships",
    "hitung": "calculation",
    "imajiner": "imaginary",
    "informal": "informal",
    "investasi": "investment",
    "irasional": "irrational",
    "jangkauan": "range",
    "jaring": "nets",
    "juring": "sectors",
    "kacah": "whole",
    "kategorikal": "categorical",
    "kejadian": "events",
    "keliling": "perimeter",
    "kelipatan": "multiples",
    "kemudian": "then",
    "kerucut": "cones",
    "kesebangunan": "similarity",
    "keterbagian": "divisibility",
    "kocomain": "codomain",
    "kodomain": "codomain",
    "kombinasi": "combinations",
    "komparasi": "comparison",
    "komposisi": "composition",
    "komutatif": "commutative",
    "kongruenan": "congruence",
    "konversi": "conversions",
    "koordinat": "coordinates",
    "korelasi": "correlation",
    "kosinus": "cosine",
    "kuadrat": "quadratic",
    "kuadran": "quadrant",
    "kuantitas": "quantities",
    "kuartil": "quartiles",
    "lingkaran": "circles",
    "linear": "linear",
    "lingkungan": "environment",
    "lingkup": "scope",
    "literasi": "literacy",
    "luas": "area",
    "majemuk": "compound",
    "matematika": "mathematics",
    "matrix": "matrices",
    "matriks": "matrices",
    "mean": "mean",
    "membandingkan": "comparing",
    "membesar": "increasing",
    "median": "median",
    "media": "media",
    "mengenal": "recognizing",
    "mengecil": "decreasing",
    "mod": "mode",
    "model": "models",
    "modulus": "mode",
    "modus": "mode",
    "nilai": "value",
    "nirkriteria": "criterion-free",
    "nonlinear": "nonlinear",
    "numerik": "numeric",
    "numerikal": "numeric",
    "operasi": "operations",
    "panjang": "length",
    "pangkat": "powers",
    "pecahan": "fractions",
    "peluang": "probability",
    "pembagian": "division",
    "pembayaran": "payments",
    "pembulatan": "rounding",
    "pemodelan": "modeling",
    "pencar": "scatter",
    "pengaruh": "effects",
    "pengukuran": "measurement",
    "penjumlahan": "addition",
    "penyajian": "representation",
    "penyelesaian": "solutions",
    "penyelidikan": "investigation",
    "perbandingan": "comparison",
    "percent": "percent",
    "periode": "period",
    "permukaan": "surface",
    "permutasi": "permutations",
    "persamaan": "equations",
    "persen": "percent",
    "pertanyaan": "questions",
    "pertidaksamaan": "inequalities",
    "peta": "maps",
    "pictogram": "pictograms",
    "piktogram": "pictograms",
    "pinjaman": "loans",
    "plot": "plot",
    "pola": "patterns",
    "populasi": "population",
    "posisi": "position",
    "prisma": "prisms",
    "proporsi": "proportion",
    "puluhan": "tens",
    "quadratic": "quadratic",
    "quartile": "quartile",
    "range": "range",
    "rasio": "ratio",
    "real": "real",
    "refleksi": "reflections",
    "relasi": "relations",
    "relatif": "relative",
    "representasi": "representations",
    "rotasi": "rotations",
    "ruang": "solid",
    "saling": "mutually",
    "sampai": "up to",
    "sampel": "sample",
    "satu": "one",
    "sebab": "cause",
    "sederhana": "simple",
    "segitiga": "triangles",
    "sehari": "everyday",
    "sejajar": "parallel",
    "sekawan": "set",
    "senilai": "equivalent",
    "sifat": "properties",
    "simetri": "symmetry",
    "sinus": "sine",
    "siku": "right",
    "skala": "scale",
    "smp": "junior high",
    "spldv": "two-variable linear systems",
    "spltv": "three-variable linear systems",
    "statistika": "statistics",
    "sudut": "angles",
    "suhu": "temperature",
    "suku": "rate",
    "sumbu": "axes",
    "syarat": "condition",
    "sistem": "systems",
    "tabung": "cylinders",
    "tabel": "tables",
    "tak": "not",
    "taksiran": "estimation",
    "tangen": "tangent",
    "teorema": "theorem",
    "tempat": "place",
    "tiga": "three",
    "tidak": "unknown",
    "titik": "points",
    "translasi": "translations",
    "transformasi": "transformations",
    "trigonometri": "trigonometry",
    "tunggal": "simple",
    "uang": "money",
    "ukuran": "size",
    "variabel": "variables",
    "visual": "visual",
    "volume": "volume",
    "waktu": "time",
}


PHRASE_OVERRIDES = {
    "bilangan_cacah_sampai_999": "Whole numbers up to 999",
    "nilai_tempat_ratusan_puluhan_satuan": "Place value with hundreds, tens, and ones",
    "garis_bilangan_dan_perbandingan_bilangan": "Number lines and comparing numbers",
    "penjumlahan_dan_pengurangan_bilangan_cacah": "Addition and subtraction of whole numbers",
    "pecahan_satuan_sederhana": "Simple unit fractions",
    "persamaan_sederhana_penjumlahan_pengurangan": "Simple addition and subtraction equations",
    "pola_berulang_dan_pola_bilangan": "Repeating patterns and number patterns",
    "pengukuran_panjang_berat_waktu_suhu_sederhana": "Simple measurement of length, weight, time, and temperature",
    "mengenal_uang_dan_nilai": "Money and value",
    "bangun_datar_dasar": "Basic plane shapes",
    "bangun_ruang_dasar": "Basic solid shapes",
    "data_piktogram_dan_tabel_sederhana": "Simple pictograms and tables",
    "bilangan_cacah_sampai_10000": "Whole numbers up to 10,000",
    "operasi_perkalian_dan_pembagian_bilangan_cacah": "Multiplication and division of whole numbers",
    "operasi_hitung_campuran_bilangan_cacah": "Mixed operations with whole numbers",
    "pecahan_senilai_dan_perbandingan_pecahan": "Equivalent fractions and comparing fractions",
    "operasi_pecahan_sederhana": "Simple fraction operations",
    "bilangan_desimal_sederhana": "Simple decimals",
    "faktor_kelipatan_dan_keterbagian_awal": "Factors, multiples, and basic divisibility",
    "pola_bilangan_membesar_dan_mengecil": "Increasing and decreasing number patterns",
    "kalimat_matematika_dan_nilai_tidak_diketahui": "Math sentences and unknown values",
    "pengukuran_satuan_baku_dan_konversi_sederhana": "Standard units and simple conversions",
    "keliling_dan_luas_persegi_persegi_panjang": "Perimeter and area of squares and rectangles",
    "sudut_garis_dan_hubungan_sederhana": "Angles, lines, and simple relationships",
    "sifat_bangun_datar_dan_simetri": "Properties of plane shapes and symmetry",
    "data_tabel_piktogram_dan_diagram_batang": "Tables, pictograms, and bar charts",
    "peluang_sehari_hari_informal": "Informal everyday probability",
    "bilangan_cacah_sampai_1000000": "Whole numbers up to 1,000,000",
    "operasi_bilangan_cacah_sampai_100000": "Operations with whole numbers up to 100,000",
    "pecahan_desimal_dan_persen": "Fractions, decimals, and percent",
    "operasi_pecahan_desimal_dan_persen": "Operations with fractions, decimals, and percent",
    "rasio_dan_proporsi_satuan": "Ratio and unit proportion",
    "skala_peta_dan_perbandingan": "Map scale and comparison",
    "fpb_kpk_dan_faktorisasi": "Greatest common factors, least common multiples, and factorization",
    "pola_bilangan_perkalian_dan_pembagian": "Multiplication and division patterns",
    "ekspresi_aljabar_awal": "Introductory algebraic expressions",
    "persamaan_sederhana_bilangan_cacah": "Simple equations with whole numbers",
    "koordinat_kartesius_kuadran_satu": "Cartesian coordinates in the first quadrant",
    "luas_volume_dan_jaring_jaring_bangun_ruang": "Area, volume, and nets of solid shapes",
    "lingkaran_keliling_dan_luas_awal": "Introductory circumference and area of circles",
    "transformasi_refleksi_translasi_rotasi_dilatasi_awal": "Introductory reflections, translations, rotations, and dilations",
    "data_mean_median_modus_awal": "Introductory mean, median, and mode",
    "diagram_lingkaran_dan_interpretasi_data": "Pie charts and data interpretation",
    "peluang_sederhana": "Simple probability",
    "literasi_finansial_sd": "Elementary financial literacy",
    "bilangan_bulat": "Integers",
    "bilangan_rasional": "Rational numbers",
    "bilangan_irasional": "Irrational numbers",
    "bilangan_desimal": "Decimals",
    "operasi_aritmetika_bilangan_real": "Arithmetic operations with real numbers",
    "estimasi_dan_pembulatan": "Estimation and rounding",
    "literasi_finansial_dasar": "Basic financial literacy",
    "faktorisasi_prima": "Prime factorization",
    "rasio": "Ratio",
    "skala": "Scale",
    "proporsi": "Proportion",
    "laju_perubahan_sederhana": "Simple rate of change",
    "pola_bilangan": "Number patterns",
    "generalisasi_pola": "Pattern generalization",
    "bentuk_aljabar": "Algebraic expressions",
    "sifat_komutatif_asosiatif_distributif": "Commutative, associative, and distributive properties",
    "bentuk_aljabar_ekuivalen": "Equivalent algebraic expressions",
    "relasi": "Relations",
    "fungsi_dasar": "Basic functions",
    "domain_kodomain_range": "Domain, codomain, and range",
    "representasi_fungsi": "Function representations",
    "fungsi_linear_dan_nonlinear_secara_grafik": "Linear and nonlinear functions from graphs",
    "persamaan_linear_satu_variabel": "One-variable linear equations",
    "pertidaksamaan_linear_satu_variabel": "One-variable linear inequalities",
    "model_masalah_persamaan_linear": "Word problems with linear equations",
    "sistem_persamaan_linear_dua_variabel": "Two-variable systems of linear equations",
    "aplikasi_spldv": "Applications of two-variable linear systems",
    "luas_lingkaran": "Area of circles",
    "luas_permukaan_prisma_tabung_bola_limas_kerucut": "Surface area of prisms, cylinders, spheres, pyramids, and cones",
    "volume_prisma_tabung_bola_limas_kerucut": "Volume of prisms, cylinders, spheres, pyramids, and cones",
    "perubahan_proporsional_ukuran_bangun": "Proportional change in shape size",
    "jaring_jaring_bangun_ruang": "Nets of solid shapes",
    "hubungan_antar_sudut": "Relationships between angles",
    "sudut_dalam_segitiga": "Interior angles of triangles",
    "kekongruenan": "Congruence",
    "kesebangunan": "Similarity",
    "teorema_pythagoras": "The Pythagorean theorem",
    "jarak_dua_titik_koordinat": "Distance between two coordinate points",
    "refleksi": "Reflections",
    "translasi": "Translations",
    "rotasi": "Rotations",
    "dilatasi": "Dilations",
    "pertanyaan_statistika": "Statistical questions",
    "pengumpulan_dan_penyajian_data": "Data collection and representation",
    "diagram_batang": "Bar charts",
    "diagram_lingkaran": "Pie charts",
    "mean": "Mean",
    "median": "Median",
    "modus": "Mode",
    "jangkauan_data": "Data range",
    "sampel_dan_populasi": "Samples and populations",
    "membandingkan_dua_kelompok_data": "Comparing two data sets",
    "peluang_dasar": "Basic probability",
    "frekuensi_relatif": "Relative frequency",
    "frekuensi_harapan": "Expected frequency",
    "sifat_bilangan_berpangkat": "Properties of exponents",
    "pangkat_pecahan": "Fractional exponents",
    "barisan_aritmetika": "Arithmetic sequences",
    "deret_aritmetika": "Arithmetic series",
    "barisan_geometri": "Geometric sequences",
    "deret_geometri": "Geometric series",
    "bunga_tunggal": "Simple interest",
    "bunga_majemuk": "Compound interest",
    "sistem_persamaan_linear_tiga_variabel": "Three-variable systems of linear equations",
    "sistem_pertidaksamaan_linear_dua_variabel": "Two-variable systems of linear inequalities",
    "daerah_penyelesaian_pertidaksamaan_linear": "Solution regions of linear inequalities",
    "persamaan_kuadrat": "Quadratic equations",
    "fungsi_kuadrat": "Quadratic functions",
    "akar_real_dan_imajiner_persamaan_kuadrat": "Real and imaginary roots of quadratic equations",
    "grafik_fungsi_kuadrat": "Graphs of quadratic functions",
    "persamaan_eksponensial_basis_sama": "Exponential equations with the same base",
    "fungsi_eksponensial": "Exponential functions",
    "aplikasi_model_eksponensial": "Applications of exponential models",
    "perbandingan_trigonometri_segitiga_siku_siku": "Trig ratios in right triangles",
    "sinus_kosinus_tangen": "Sine, cosine, and tangent",
    "aplikasi_trigonometri_siku_siku": "Applications of right-triangle trigonometry",
    "kuartil": "Quartiles",
    "jangkauan_interkuartil": "Interquartile range",
    "box_plot": "Box plots",
    "histogram": "Histograms",
    "dot_plot": "Dot plots",
    "diagram_pencar": "Scatter plots",
    "hubungan_dua_variabel_numerik": "Relationships between two numeric variables",
    "evaluasi_laporan_statistika_media": "Evaluating statistical reports in media",
    "peluang_kejadian_majemuk": "Probability of compound events",
    "frekuensi_harapan_kejadian_majemuk": "Expected frequency of compound events",
    "kejadian_saling_lepas": "Mutually exclusive events",
    "kejadian_saling_bebas": "Independent events",
    "model_pinjaman_dan_investasi": "Loan and investment models",
    "model_bunga_majemuk_lanjut": "Advanced compound interest models",
    "anuitas": "Annuities",
    "pengaruh_suku_bunga_dan_periode_pembayaran": "Effects of interest rates and payment periods",
    "data_dalam_bentuk_matriks": "Data in matrix form",
    "operasi_matriks_dasar": "Basic matrix operations",
    "fungsi_invers": "Inverse functions",
    "komposisi_fungsi": "Function composition",
    "transformasi_fungsi": "Function transformations",
    "pemodelan_fungsi_linear_kuadrat_eksponensial": "Modeling with linear, quadratic, and exponential functions",
    "teorema_lingkaran": "Circle theorems",
    "panjang_busur_lingkaran": "Arc length",
    "luas_juring_lingkaran": "Area of sectors",
    "koordinat_posisi_pada_permukaan_bumi": "Coordinates on Earth's surface",
    "jarak_dua_tempat_di_permukaan_bumi": "Distance between two places on Earth's surface",
    "penyelidikan_statistika_bivariat": "Bivariate statistical investigations",
    "asosiasi_variabel_kategorikal": "Associations between categorical variables",
    "asosiasi_variabel_numerikal": "Associations between numerical variables",
    "model_linear_terbaik": "Best-fit linear models",
    "korelasi_dan_sebab_akibat": "Correlation and causation",
    "peluang_bersyarat": "Conditional probability",
    "permutasi": "Permutations",
    "kombinasi": "Combinations",
    "kejadian_saling_bebas_dengan_peluang_bersyarat": "Independent events and conditional probability",
}


TEMPLATES = [
    "Which math topic best matches this skill: {description}?",
    "A lesson about {description} belongs to which topic?",
    "Which topic would help a student learn about {description}?",
    "Which math topic focuses on {description}?",
]


def slug_title(text: str) -> str:
    return text.lower().replace(",", "").replace("'", "")


def suffix_from_node_id(node_id: str) -> str:
    return "_".join(node_id.split("_")[3:])


def translate_suffix(suffix: str) -> str:
    if suffix in PHRASE_OVERRIDES:
        return PHRASE_OVERRIDES[suffix]

    words = []
    for token in suffix.split("_"):
        words.append(TOKEN_MAP.get(token, token.replace("-", " ")))
    text = " ".join(words).replace("  ", " ").strip()
    return text[:1].upper() + text[1:]


def describe_topic(title: str) -> str:
    lower = title.lower()
    if "place value" in lower:
        return "reading and using place value in numbers"
    if "whole numbers up to" in lower:
        return f"reading, comparing, and using {lower}"
    if "addition and subtraction" in lower:
        return "adding and subtracting whole numbers accurately"
    if "multiplication and division" in lower:
        return "using equal groups, multiplication, and division"
    if "fraction" in lower and "operations" not in lower:
        return "recognizing and comparing fractions"
    if "fraction" in lower and "operations" in lower:
        return "computing with fractions"
    if "decimal" in lower and "operations" not in lower:
        return "understanding decimal values"
    if "percent" in lower:
        return "connecting fractions, decimals, and percent"
    if "ratio" in lower or "proportion" in lower:
        return "comparing quantities using ratios or proportions"
    if "pattern" in lower:
        return "finding and extending patterns"
    if "equation" in lower:
        return "finding unknown values in equations"
    if "inequalit" in lower:
        return "deciding which values make an inequality true"
    if "function" in lower:
        return "matching inputs, outputs, and function rules"
    if "graph" in lower:
        return "reading or drawing graphs"
    if "matrix" in lower:
        return "organizing data and calculations with matrices"
    if "circle" in lower:
        return "reasoning about circles and their measures"
    if "triangle" in lower or "angles" in lower:
        return "reasoning about angles and triangles"
    if "surface area" in lower or "volume" in lower:
        return "measuring three-dimensional shapes"
    if "shape" in lower or "solid" in lower:
        return "recognizing and describing shapes"
    if "coordinate" in lower:
        return "locating points with coordinates"
    if "reflection" in lower or "rotation" in lower or "translation" in lower or "dilation" in lower:
        return "describing geometric transformations"
    if "mean" in lower or "median" in lower or "mode" in lower or "quartile" in lower or "range" in lower:
        return "summarizing data with statistics"
    if "chart" in lower or "plot" in lower or "histogram" in lower or "table" in lower:
        return "reading and representing data"
    if "probability" in lower or "events" in lower or "frequency" in lower:
        return "reasoning about chance and outcomes"
    if "interest" in lower or "loan" in lower or "investment" in lower or "annuit" in lower:
        return "using math in financial situations"
    if "sequence" in lower or "series" in lower:
        return "working with growing number patterns"
    if "exponent" in lower or "exponential" in lower:
        return "working with repeated multiplication and growth"
    if "trig" in lower or "sine" in lower or "cosine" in lower or "tangent" in lower:
        return "using side lengths and angles in right triangles"
    if "permutation" in lower or "combination" in lower:
        return "counting possible arrangements or selections"
    if "correlation" in lower or "association" in lower:
        return "looking for relationships between variables"
    if "financial literacy" in lower or "money" in lower:
        return "making sense of money values and choices"
    return lower


def difficulty_for_phase(phase: str, assessment_type: str) -> str:
    matrix = {
        "A": {"pretest": "easy", "daily_quiz": "easy", "posttest": "easy", "workspace_quiz": "easy"},
        "B": {"pretest": "easy", "daily_quiz": "easy", "posttest": "medium", "workspace_quiz": "easy"},
        "C": {"pretest": "easy", "daily_quiz": "medium", "posttest": "medium", "workspace_quiz": "easy"},
        "D": {"pretest": "medium", "daily_quiz": "medium", "posttest": "hard", "workspace_quiz": "medium"},
        "E": {"pretest": "medium", "daily_quiz": "medium", "posttest": "hard", "workspace_quiz": "medium"},
        "F": {"pretest": "medium", "daily_quiz": "hard", "posttest": "hard", "workspace_quiz": "medium"},
    }
    return matrix[phase][assessment_type]


def cognitive_for_phase(phase: str, assessment_type: str) -> str:
    matrix = {
        "A": {"pretest": "understand", "daily_quiz": "remember", "posttest": "understand", "workspace_quiz": "remember"},
        "B": {"pretest": "understand", "daily_quiz": "remember", "posttest": "apply", "workspace_quiz": "remember"},
        "C": {"pretest": "understand", "daily_quiz": "understand", "posttest": "apply", "workspace_quiz": "remember"},
        "D": {"pretest": "apply", "daily_quiz": "understand", "posttest": "analyze", "workspace_quiz": "understand"},
        "E": {"pretest": "apply", "daily_quiz": "understand", "posttest": "analyze", "workspace_quiz": "understand"},
        "F": {"pretest": "apply", "daily_quiz": "apply", "posttest": "analyze", "workspace_quiz": "understand"},
    }
    return matrix[phase][assessment_type]


def make_concept_code(node_id: str) -> str:
    return suffix_from_node_id(node_id)


def question_item(node: dict, group_name: str, assessment_type: str, distractors: list[str], number: int) -> dict:
    suffix = suffix_from_node_id(node["id"])
    title = translate_suffix(suffix)
    description = describe_topic(title)
    templates = ASSESSMENT_VARIANTS[assessment_type]["prompt_templates"]
    template = templates[number % len(templates)]
    options = [title] + distractors[:3]
    random.Random(node["id"]).shuffle(options)
    labels = ["A", "B", "C", "D"]
    option_objs = [{"label": label, "text": text} for label, text in zip(labels, options)]
    answer_key = next(obj["label"] for obj in option_objs if obj["text"] == title)

    return {
        "id": f"math_{PHASE_GROUPS[group_name]['level_short']}_{suffix[:24]}_{ASSESSMENT_VARIANTS[assessment_type]['short']}_{number:03d}",
        "subject_code": "mathematics",
        "concept_code": make_concept_code(node["id"]),
        "concept_title": title,
        "education_level": group_name,
        "grade_band": PHASE_GROUPS[group_name]["grade_band"],
        "language": "en",
        "assessment_types": [assessment_type],
        "question_type": "multiple_choice",
        "difficulty": difficulty_for_phase(node["phase"], assessment_type),
        "cognitive_level": cognitive_for_phase(node["phase"], assessment_type),
        "prompt": template.format(description=description),
        "helper_text": ASSESSMENT_VARIANTS[assessment_type]["helper_text"],
        "options": option_objs,
        "answer_key": answer_key,
        "explanation": f"The correct topic is {title} because it best matches the mathematical idea in the prompt.",
        "rubric": {
            "correct": f"Learner identifies the topic {title} from its core idea.",
            "common_misconceptions": [
                "Chooses a nearby topic from the same strand without checking the key idea.",
                "Focuses on a familiar keyword instead of the full mathematical meaning."
            ]
        },
        "tags": ["mathematics", group_name, node["phase"].lower(), make_concept_code(node["id"]), assessment_type, "topic_identification"],
        "status": "active",
        "metadata": {
            "source_pack": "baseline_generated",
            "estimated_seconds": 45
        }
    }


def choose_distractors(node: dict, titles_by_id: dict[str, str], peers: list[dict]) -> list[str]:
    same_domain = [peer for peer in peers if peer["id"] != node["id"] and peer.get("domain") == node.get("domain")]
    fallback = [peer for peer in peers if peer["id"] != node["id"]]
    pool = same_domain if len(same_domain) >= 3 else fallback
    pool = sorted(pool, key=lambda peer: peer["id"])
    picks = []
    for peer in pool:
        title = titles_by_id[peer["id"]]
        if title not in picks:
            picks.append(title)
        if len(picks) == 3:
            break
    while len(picks) < 3:
        picks.append("None of these")
    return picks


def build_seed(group_name: str, nodes: list[dict]) -> dict:
    titles_by_id = {node["id"]: translate_suffix(suffix_from_node_id(node["id"])) for node in nodes}
    items = []
    ordered_nodes = sorted(nodes, key=lambda n: (n["phase"], n["id"]))
    counters = {assessment_type: 1 for assessment_type in ASSESSMENT_VARIANTS}
    for node in ordered_nodes:
        distractors = choose_distractors(node, titles_by_id, nodes)
        for assessment_type in ("pretest", "daily_quiz", "posttest", "workspace_quiz"):
            items.append(question_item(node, group_name, assessment_type, distractors, counters[assessment_type]))
            counters[assessment_type] += 1

    return {
        "version": "2026-05-16",
        "source": "wicara_question_bank_seed_v1",
        "language": "en",
        "subject_code": "mathematics",
        "education_level": group_name,
        "grade_band": PHASE_GROUPS[group_name]["grade_band"],
        "items": items,
    }


def main() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    nodes = [
        node
        for node in graph["nodes"]
        if node.get("subject") == "matematika" and node.get("is_assessable")
    ]
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    for group_name, config in PHASE_GROUPS.items():
        group_nodes = [node for node in nodes if node["phase"] in config["phases"]]
        seed = build_seed(group_name, group_nodes)
        out_path = SEED_DIR / f"mathematics.{group_name}.all_topics.v1.json"
        out_path.write_text(json.dumps(seed, ensure_ascii=True, indent=2), encoding="utf-8")
        print(f"{out_path.name}: {len(seed['items'])} items")


if __name__ == "__main__":
    main()
