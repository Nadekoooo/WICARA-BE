# WICARA MVP 10 Manim Templates

Isi pack:
- `templates/manim/core_templates.py`: implementasi 10 renderer MVP.
- `templates/manim/*_v1.py`: wrapper tiap template dengan `GeneratedTemplate` dan `SPEC` default.
- `specs/samples/*/sample_01.json`: contoh SceneSpec.
- `scripts/render_sample.py`: helper render sample.

Cara render:
```bash
python scripts/render_sample.py \
  --template templates/manim/number_line_quantity_v1.py \
  --spec specs/samples/manim.number_line_quantity.v1/sample_01.json \
  --quality=-ql
```

Persiapan environment backend:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Catatan: ini MVP code pack, bukan final production. Tetap cek visual overlap/render environment.
