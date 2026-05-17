# Remotion Template Bundle for All Remotion Concepts

Bundle ini berisi template Remotion + sample spec JSON untuk **semua concept row** yang secara prioritas seharusnya memakai Remotion / Rive / Remotion-or-Manim.

## Isi
- `src/helpers.tsx` — helper UI dan layout Remotion
- `src/templates.tsx` — semua template component Remotion
- `src/registry.tsx` — registry composition untuk Remotion Studio
- `src/index.ts` — entry point `registerRoot`
- `specs/` — sample JSON per concept row
- `docs/REMOTION_TEMPLATE_CONTRACTS.md` — kontrak field dan notes per template
- `docs/REUSE_RATIONALE.md` — justifikasi reuse yang memang make sense
- `docs/remotion_template_index.csv` — index row → template/component
- `package.json`, `tsconfig.json`

## Cara pakai
1. Install dependency:
   ```bash
   npm install
   ```
2. Jalankan studio:
   ```bash
   npm run dev
   ```
3. Buka composition sesuai row / template yang ingin di-render.

## Catatan desain
- Template dibedakan berdasarkan morfologi visual utama: network, flow, timeline, cycle, labeling, lab setup, molecular view, particle view, dsb.
- Reuse hanya dilakukan bila bentuk visual inti benar-benar sama.
- Sample spec sudah ditulis dalam Bahasa Indonesia dan bisa dipakai sebagai titik awal untuk generator LLM/spec-filling.

## Backend integration notes
- Folder ini dipakai backend sebagai runtime project untuk render template `remotion.*`.
- Render command baseline (akan dipanggil worker backend):
  ```bash
  npx remotion render src/index.ts <composition_id> <output_file.mp4> --props=<json_props>
  ```
- Source mapping template -> composition ada di:
- `docs/remotion_template_index.csv`
- `src/registry.tsx`
