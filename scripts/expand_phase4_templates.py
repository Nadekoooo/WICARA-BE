from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "wicara_mvp_10_manim_templates" / "templates" / "manim"
SAMPLE_ROOT = ROOT / "wicara_mvp_10_manim_templates" / "specs" / "samples"
REGISTRY_PATH = ROOT / "app" / "modules" / "learning" / "template_registry.json"
MAP_PATH = ROOT / "app" / "modules" / "learning" / "concept_type_template_map_phase4.json"
SUMMARY_PATH = ROOT / "MANIM_PHASE4_FAMILY_EXPANSION.md"


EXPANSION = [
    {
        "template_id": "manim.probability_tree.v1",
        "slug": "probability_tree",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Peluang dengan Diagram",
        "subtitle": "Hubungan kemungkinan kejadian.",
        "concept_types": ["probability_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.scientific_inquiry_data.v1",
        "slug": "scientific_inquiry_data",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Inkuiri Ilmiah dan Data",
        "subtitle": "Baca data lalu simpulkan pola.",
        "concept_types": ["scientific_inquiry_process", "scientific_inquiry_data_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.financial_growth.v1",
        "slug": "financial_growth",
        "class_name": "SequencePatternTemplate",
        "base_sample_template_id": "manim.sequence_pattern.v1",
        "title": "Pertumbuhan Nilai Keuangan",
        "subtitle": "Model nilai bertambah per periode.",
        "concept_types": ["financial_growth_model"],
        "family": "sequence_family",
    },
    {
        "template_id": "manim.data_representation.v1",
        "slug": "data_representation",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Representasi Data",
        "subtitle": "Visualkan data agar mudah dibaca.",
        "concept_types": ["data_representation_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.statistics_center_spread.v1",
        "slug": "statistics_center_spread",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Pemusatan dan Penyebaran Data",
        "subtitle": "Bandingkan pusat data dan sebarannya.",
        "concept_types": ["center_spread_statistics"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.geometry_transform.v1",
        "slug": "geometry_transform",
        "class_name": "GeometryAreaVolumeTemplate",
        "base_sample_template_id": "manim.geometry_area_volume.v1",
        "title": "Transformasi Geometri",
        "subtitle": "Lihat bentuk sebelum dan sesudah transformasi.",
        "concept_types": ["congruence_similarity_transform"],
        "family": "geometry_family",
    },
    {
        "template_id": "manim.exponential_growth.v1",
        "slug": "exponential_growth",
        "class_name": "SequencePatternTemplate",
        "base_sample_template_id": "manim.sequence_pattern.v1",
        "title": "Pertumbuhan Eksponensial",
        "subtitle": "Pola pertumbuhan berlipat dari waktu ke waktu.",
        "concept_types": ["exponential_growth_model"],
        "family": "sequence_family",
    },
    {
        "template_id": "manim.function_mapping.v1",
        "slug": "function_mapping",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Relasi dan Fungsi",
        "subtitle": "Pemetaan input ke output secara konsisten.",
        "concept_types": ["function_mapping_representation"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.geometry_measurement.v1",
        "slug": "geometry_measurement",
        "class_name": "GeometryAreaVolumeTemplate",
        "base_sample_template_id": "manim.geometry_area_volume.v1",
        "title": "Pengukuran Geometri",
        "subtitle": "Gunakan ukuran untuk hitung luas dan volume.",
        "concept_types": ["geometry_measurement_area_volume", "area_perimeter_volume_model"],
        "family": "geometry_family",
    },
    {
        "template_id": "manim.geometry_theorem.v1",
        "slug": "geometry_theorem",
        "class_name": "GeometryAreaVolumeTemplate",
        "base_sample_template_id": "manim.geometry_area_volume.v1",
        "title": "Hubungan Sudut Geometri",
        "subtitle": "Gunakan sifat geometri untuk pembuktian dasar.",
        "concept_types": ["angle_relationship_geometry"],
        "family": "geometry_family",
    },
    {
        "template_id": "manim.heat_energy_machine.v1",
        "slug": "heat_energy_machine",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Kalor dan Energi",
        "subtitle": "Lacak perpindahan energi pada sistem.",
        "concept_types": ["heat_energy_transfer_model", "heat_temperature_transfer_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.wave_optics.v1",
        "slug": "wave_optics",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Gelombang dan Optik",
        "subtitle": "Amati pola gelombang pada representasi grafik.",
        "concept_types": ["wave_oscillation_model", "wave_sound_light_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.stoichiometry_board.v1",
        "slug": "stoichiometry_board",
        "class_name": "EquationBalanceTemplate",
        "base_sample_template_id": "manim.equation_balance.v1",
        "title": "Stoikiometri dan Kesetaraan",
        "subtitle": "Seimbangkan persamaan untuk hitung kuantitas.",
        "concept_types": ["stoichiometry_mole_calculation"],
        "family": "equation_family",
    },
    {
        "template_id": "manim.elementary_number_line_place_value.v1",
        "slug": "elementary_number_line_place_value",
        "class_name": "NumberLineQuantityTemplate",
        "base_sample_template_id": "manim.number_line_quantity.v1",
        "title": "Nilai Tempat pada Garis Bilangan",
        "subtitle": "Posisikan bilangan untuk memahami nilainya.",
        "concept_types": ["counting_place_value_number_line"],
        "family": "number_line_family",
    },
    {
        "template_id": "manim.quadratic_model.v1",
        "slug": "quadratic_model",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Model Kuadrat",
        "subtitle": "Analisis bentuk grafik parabola.",
        "concept_types": ["quadratic_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.scatter_association.v1",
        "slug": "scatter_association",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Asosiasi Dua Variabel",
        "subtitle": "Baca kecenderungan dari sebaran data.",
        "concept_types": ["bivariable_association_regression"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.electricity_magnetism.v1",
        "slug": "electricity_magnetism",
        "class_name": "ForceDiagramTemplate",
        "base_sample_template_id": "manim.force_diagram.v1",
        "title": "Listrik dan Magnet",
        "subtitle": "Visualkan interaksi gaya pada rangkaian.",
        "concept_types": ["electricity_magnetism_circuit_model", "electric_circuit_model"],
        "family": "force_family",
    },
    {
        "template_id": "manim.energy_environment_system.v1",
        "slug": "energy_environment_system",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Energi dan Lingkungan",
        "subtitle": "Hubungkan perubahan energi dengan lingkungan.",
        "concept_types": ["environment_energy_system_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.modern_atomic_nuclear.v1",
        "slug": "modern_atomic_nuclear",
        "class_name": "GraphExplanationTemplate",
        "base_sample_template_id": "manim.graph_explanation.v1",
        "title": "Atom Modern dan Inti",
        "subtitle": "Representasi perubahan pada skala atom.",
        "concept_types": ["modern_atomic_nuclear_model"],
        "family": "graph_family",
    },
    {
        "template_id": "manim.chem_reaction_equation.v1",
        "slug": "chem_reaction_equation",
        "class_name": "EquationBalanceTemplate",
        "base_sample_template_id": "manim.equation_balance.v1",
        "title": "Persamaan Reaksi Kimia",
        "subtitle": "Seimbangkan jumlah atom di kedua sisi.",
        "concept_types": ["reaction_equation_conservation"],
        "family": "equation_family",
    },
]

MVP_CONCEPT_MAP = [
    {
        "concept_type": "number_line_quantity_model",
        "primary_template_id": "manim.number_line_quantity.v1",
        "template_candidates": ["manim.number_line_quantity.v1", "manim.elementary_number_line_place_value.v1"],
        "family": "number_line_family",
    },
    {
        "concept_type": "counting_place_value_number_line",
        "primary_template_id": "manim.elementary_number_line_place_value.v1",
        "template_candidates": ["manim.elementary_number_line_place_value.v1", "manim.number_line_quantity.v1"],
        "family": "number_line_family",
    },
    {
        "concept_type": "equation_balance_model",
        "primary_template_id": "manim.equation_balance.v1",
        "template_candidates": ["manim.equation_balance.v1", "manim.chem_reaction_equation.v1"],
        "family": "equation_family",
    },
    {
        "concept_type": "equation_balance_unknown",
        "primary_template_id": "manim.equation_balance.v1",
        "template_candidates": ["manim.equation_balance.v1", "manim.stoichiometry_board.v1"],
        "family": "equation_family",
    },
    {
        "concept_type": "stoichiometry_mole_calculation",
        "primary_template_id": "manim.stoichiometry_board.v1",
        "template_candidates": ["manim.stoichiometry_board.v1", "manim.chem_reaction_equation.v1"],
        "family": "equation_family",
    },
    {
        "concept_type": "reaction_equation_conservation",
        "primary_template_id": "manim.chem_reaction_equation.v1",
        "template_candidates": ["manim.chem_reaction_equation.v1", "manim.stoichiometry_board.v1"],
        "family": "equation_family",
    },
    {
        "concept_type": "fraction_decimal_percent_model",
        "primary_template_id": "manim.fraction_bar_partition.v1",
        "template_candidates": ["manim.fraction_bar_partition.v1", "manim.ratio_proportion.v1"],
        "family": "fraction_ratio_family",
    },
    {
        "concept_type": "fraction_ratio_proportion_scaling",
        "primary_template_id": "manim.ratio_proportion.v1",
        "template_candidates": ["manim.ratio_proportion.v1", "manim.fraction_bar_partition.v1"],
        "family": "fraction_ratio_family",
    },
    {
        "concept_type": "geometry_measurement_area_volume",
        "primary_template_id": "manim.geometry_measurement.v1",
        "template_candidates": ["manim.geometry_measurement.v1", "manim.geometry_area_volume.v1"],
        "family": "geometry_family",
    },
    {
        "concept_type": "area_perimeter_volume_model",
        "primary_template_id": "manim.geometry_measurement.v1",
        "template_candidates": ["manim.geometry_measurement.v1", "manim.geometry_area_volume.v1"],
        "family": "geometry_family",
    },
    {
        "concept_type": "congruence_similarity_transform",
        "primary_template_id": "manim.geometry_transform.v1",
        "template_candidates": ["manim.geometry_transform.v1", "manim.geometry_theorem.v1"],
        "family": "geometry_family",
    },
    {
        "concept_type": "angle_relationship_geometry",
        "primary_template_id": "manim.geometry_theorem.v1",
        "template_candidates": ["manim.geometry_theorem.v1", "manim.geometry_transform.v1"],
        "family": "geometry_family",
    },
    {
        "concept_type": "shape_identification_geometry",
        "primary_template_id": "manim.geometry_area_volume.v1",
        "template_candidates": ["manim.geometry_area_volume.v1", "manim.geometry_measurement.v1"],
        "family": "geometry_family",
    },
    {
        "concept_type": "sequence_pattern_generalization",
        "primary_template_id": "manim.sequence_pattern.v1",
        "template_candidates": ["manim.sequence_pattern.v1", "manim.exponential_growth.v1"],
        "family": "sequence_family",
    },
    {
        "concept_type": "pattern_sequence_generalization",
        "primary_template_id": "manim.sequence_pattern.v1",
        "template_candidates": ["manim.sequence_pattern.v1", "manim.financial_growth.v1"],
        "family": "sequence_family",
    },
    {
        "concept_type": "financial_growth_model",
        "primary_template_id": "manim.financial_growth.v1",
        "template_candidates": ["manim.financial_growth.v1", "manim.exponential_growth.v1"],
        "family": "sequence_family",
    },
    {
        "concept_type": "exponential_growth_model",
        "primary_template_id": "manim.exponential_growth.v1",
        "template_candidates": ["manim.exponential_growth.v1", "manim.financial_growth.v1"],
        "family": "sequence_family",
    },
    {
        "concept_type": "probability_model",
        "primary_template_id": "manim.probability_tree.v1",
        "template_candidates": ["manim.probability_tree.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "data_representation_model",
        "primary_template_id": "manim.data_representation.v1",
        "template_candidates": ["manim.data_representation.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "center_spread_statistics",
        "primary_template_id": "manim.statistics_center_spread.v1",
        "template_candidates": ["manim.statistics_center_spread.v1", "manim.scatter_association.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "function_mapping_representation",
        "primary_template_id": "manim.function_mapping.v1",
        "template_candidates": ["manim.function_mapping.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "quadratic_model",
        "primary_template_id": "manim.quadratic_model.v1",
        "template_candidates": ["manim.quadratic_model.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "bivariable_association_regression",
        "primary_template_id": "manim.scatter_association.v1",
        "template_candidates": ["manim.scatter_association.v1", "manim.data_representation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "scientific_inquiry_process",
        "primary_template_id": "manim.scientific_inquiry_data.v1",
        "template_candidates": ["manim.scientific_inquiry_data.v1", "manim.data_representation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "scientific_inquiry_data_model",
        "primary_template_id": "manim.scientific_inquiry_data.v1",
        "template_candidates": ["manim.scientific_inquiry_data.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "wave_oscillation_model",
        "primary_template_id": "manim.wave_optics.v1",
        "template_candidates": ["manim.wave_optics.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "wave_sound_light_model",
        "primary_template_id": "manim.wave_optics.v1",
        "template_candidates": ["manim.wave_optics.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "heat_energy_transfer_model",
        "primary_template_id": "manim.heat_energy_machine.v1",
        "template_candidates": ["manim.heat_energy_machine.v1", "manim.motion_kinematics.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "heat_temperature_transfer_model",
        "primary_template_id": "manim.heat_energy_machine.v1",
        "template_candidates": ["manim.heat_energy_machine.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "electricity_magnetism_circuit_model",
        "primary_template_id": "manim.electricity_magnetism.v1",
        "template_candidates": ["manim.electricity_magnetism.v1", "manim.force_diagram.v1"],
        "family": "force_family",
    },
    {
        "concept_type": "electric_circuit_model",
        "primary_template_id": "manim.electricity_magnetism.v1",
        "template_candidates": ["manim.electricity_magnetism.v1", "manim.force_diagram.v1"],
        "family": "force_family",
    },
    {
        "concept_type": "environment_energy_system_model",
        "primary_template_id": "manim.energy_environment_system.v1",
        "template_candidates": ["manim.energy_environment_system.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
    {
        "concept_type": "modern_atomic_nuclear_model",
        "primary_template_id": "manim.modern_atomic_nuclear.v1",
        "template_candidates": ["manim.modern_atomic_nuclear.v1", "manim.graph_explanation.v1"],
        "family": "graph_family",
    },
]


def _alias_list(slug: str) -> list[str]:
    return [
        f"manim.{slug}",
        f"manim.{slug}_v1",
        f"{slug}_v1",
        slug,
    ]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_sample(template_id: str) -> dict:
    sample_path = SAMPLE_ROOT / template_id / "sample_01.json"
    return _load_json(sample_path)


def _write_template_wrapper(slug: str, class_name: str) -> str:
    file_name = f"{slug}_v1.py"
    out_path = TEMPLATE_DIR / file_name
    content = (
        f"from core_templates import {class_name}\n\n\n"
        f"class GeneratedTemplate({class_name}):\n"
        f"    SPEC = dict({class_name}.SPEC)\n"
    )
    out_path.write_text(content, encoding="utf-8")
    return str(out_path.relative_to(ROOT)).replace("\\", "/")


def _write_sample(expand_row: dict) -> None:
    payload = deepcopy(_load_sample(expand_row["base_sample_template_id"]))
    payload["id"] = f"sample_{expand_row['slug']}"
    payload["template_id"] = expand_row["template_id"]
    payload["node_id"] = f"phase4_{expand_row['concept_types'][0]}"
    payload["title"] = expand_row["title"]
    payload["subtitle"] = expand_row["subtitle"]

    sample_dir = SAMPLE_ROOT / expand_row["template_id"]
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_path = sample_dir / "sample_01.json"
    sample_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _update_registry(path_map: dict[str, str]) -> None:
    payload = _load_json(REGISTRY_PATH)
    rows = payload.get("templates", [])
    if not isinstance(rows, list):
        raise ValueError("template_registry.json templates must be list")

    by_id = {str(row.get("template_id", "")).strip().lower(): row for row in rows if isinstance(row, dict)}

    for item in EXPANSION:
        template_id = item["template_id"]
        slug = item["slug"]
        class_name = item["class_name"]
        base_schema = item["base_sample_template_id"]
        entry = {
            "template_id": template_id,
            "template_path": path_map[template_id],
            "scene_class": "GeneratedTemplate",
            "schema_id": base_schema,
            "aliases": _alias_list(slug),
            "family": item["family"],
            "phase": "phase4_expansion",
            "base_family_template_id": base_schema,
        }
        by_id[template_id] = entry

    merged = [by_id[key] for key in sorted(by_id.keys())]
    payload["templates"] = merged
    REGISTRY_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_concept_map() -> None:
    payload = {
        "version": "phase4_top30_v1",
        "source": "manim_family_expansion_phase4",
        "notes": [
            "Top30-style routing map for manim concept types.",
            "Each concept type provides primary_template_id and fallback candidates.",
        ],
        "routes": MVP_CONCEPT_MAP,
    }
    MAP_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_summary() -> None:
    lines = [
        "# MANIM Phase 4 Family Expansion",
        "",
        "Phase 4 expands from MVP 10 to a **30-template registry** by reusing existing template families.",
        "",
        "## New Template Count",
        f"- Added wrappers: **{len(EXPANSION)}**",
        "- Total registry target after phase 4: **30 templates**",
        "",
        "## Family Breakdown (new wrappers)",
    ]
    family_counts: dict[str, int] = {}
    for row in EXPANSION:
        family = row["family"]
        family_counts[family] = family_counts.get(family, 0) + 1
    for family, count in sorted(family_counts.items()):
        lines.append(f"- `{family}`: {count}")
    lines += [
        "",
        "## New Templates",
    ]
    for row in EXPANSION:
        lines.append(
            f"- `{row['template_id']}` (base schema: `{row['base_sample_template_id']}`, class: `{row['class_name']}`)"
        )
    lines += [
        "",
        "## Concept-Type Routing Artifact",
        "- `app/modules/learning/concept_type_template_map_phase4.json`",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    path_map: dict[str, str] = {}
    for item in EXPANSION:
        template_path = _write_template_wrapper(item["slug"], item["class_name"])
        path_map[item["template_id"]] = template_path
        _write_sample(item)

    _update_registry(path_map)
    _write_concept_map()
    _write_summary()
    print(f"Generated {len(EXPANSION)} template wrappers + samples.")
    print(f"Updated registry: {REGISTRY_PATH}")
    print(f"Created concept map: {MAP_PATH}")
    print(f"Created summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
