# WICARA Remotion v2 Animated Template Bundle

Bundle ini adalah rewrite dari template Remotion lama agar sesuai standar video edukasi:

- bukan slide/card statis,
- memakai actor dan event,
- motion berbasis frame Remotion,
- ada active narration panel,
- ada state transition,
- ada final summary overlay,
- spec JSON lengkap untuk semua concept Remotion.

## Cakupan

- Total concept Remotion: **43**
- Source: `concept_type_priority(4).csv`
- Semua spec ada di `specs/*.json`
- Registry composition ada di `src/registry.tsx`

## Cara menjalankan

```bash
npm install
npm run studio
```

Untuk cek daftar composition/spec:

```bash
npm run list
```

## Struktur

```text
src/
  primitives/
    Biology.tsx
    Chemistry.tsx
    Earth.tsx
    Layout.tsx
  Templates.tsx
  registry.tsx
  index.ts
specs/
docs/
  REMOTION_V2_TEMPLATE_CONTRACTS.md
  REUSE_RATIONALE.md
  QUALITY_GATE.md
```

## Catatan penting

File `src/shims.d.ts` disediakan agar `tsc --noEmit` bisa dipakai di environment tanpa install dependency. Di project Remotion asli, setelah `npm install`, dependency React/Remotion akan dipakai normal.