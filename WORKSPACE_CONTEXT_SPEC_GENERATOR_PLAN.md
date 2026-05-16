# Workspace Context -> Spec Generator -> Mid-Chat Video Plan (Number Line Pilot)

## Goal
Fokus plan ini hanya untuk pipeline video generation dengan urutan berikut:
1. Hardcode context sesi chat ke topik `number_line` (berbasis node kurikulum yang valid).
2. Backend generate spec berdasarkan context workspace.
3. Mobile integrasi ke backend spec generator dan trigger video di tengah percakapan.

---

## Pilot Scope (Single Node, Single Template)
Agar cepat dites end-to-end, pilot hanya pakai 1 node kurikulum:

- `node_id`: `km_d_matematika_bilangan_bulat`
- `label`: Bilangan bulat
- `concept_type`: `number_line_quantity_model`
- `default_template_id`: `manim.number_line_quantity.v1`

Direct prerequisite dari kurikulum:
- `km_c_matematika_bilangan_cacah_sampai_1000000`

Catatan sumber data:
- `wicara_kurikulum_merdeka_graph_complete/curriculum_nodes.csv`
- `wicara_kurikulum_merdeka_graph_complete/curriculum_edges.csv`

---

## Conflict Check (BE/Mobile)
Pendekatan ini tidak bentrok dengan BE/mobile saat ini:

- Mode lama manual (`template_id + spec_json`) tetap dipertahankan.
- Ditambah mode baru `context_auto`.
- Mobile tetap pakai polling/status yang sama; hanya source spec yang pindah ke BE.

---

## Target Flow (Yang Benar)
1. Workspace/chat aktif.
2. Context session di-set ke number line pilot (hardcoded rule).
3. User chat normal.
4. User bisa tekan generate video kapan saja (mid-chat).
5. Mobile kirim request `generation_mode=context_auto`.
6. BE baca context workspace, resolve template, build spec, validate, queue render.
7. Mobile polling status dan tampilkan video artifact.

---

## Data Contract

## 1) Workspace Context Metadata (pilot)
Simpan ke `workspace.metadata_json`:

- `active_node_id`: `km_d_matematika_bilangan_bulat`
- `active_concept_type`: `number_line_quantity_model`
- `active_template_id`: `manim.number_line_quantity.v1`
- `active_prerequisites`: `["km_c_matematika_bilangan_cacah_sampai_1000000"]`
- `context_source`: `hardcoded_number_line_pilot`

## 2) Generate Video Request
Tambah/tegaskan field:

- `generation_mode`: `manual | context_auto` (default `manual` untuk compatibility)

Rules:
- `manual`: FE kirim `template_id + spec_json` (flow lama)
- `context_auto`: FE tidak perlu kirim spec; BE generate dari context

---

## Backend Work

## A. Context Assigner (Hardcoded Pilot)
Di create/resume workspace (atau session initializer):
- Jika mode pilot aktif, assign context number line node di atas.
- Simpan node + prerequisite ke metadata workspace.

Untuk pilot ini, rule boleh deterministic sederhana:
- Hardcode always number_line untuk workspace target test, atau
- Hardcode by keyword sederhana (`garis bilangan`, `number line`, `bilangan`) lalu assign node pilot.

## B. Context-Based Spec Generator
Buat service baru, contoh:
- `app/modules/learning/spec_generator.py`
- fungsi: `generate_spec_from_workspace_context(workspace, language)`

Output minimal:
- `resolved_template_id`
- `spec_json`
- `debug_meta` (node yang terpilih, source rule, dsb)

Untuk pilot, generator cukup khusus untuk:
- `number_line_quantity_model` -> `manim.number_line_quantity.v1`

## C. Endpoint Integration
Di `POST /api/v1/workspaces/{workspace_id}/generate-video`:
- Branch `generation_mode`:
  - `manual`: behavior lama
  - `context_auto`: panggil spec generator BE
- Simpan audit metadata:
  - `spec_source=context_auto_backend`
  - `resolved_node_id`
  - `resolved_template_id`

---

## Mobile Work

## A. Switch to Context Auto Mode
Pada action generate video di workspace/chat:
- Kirim `generation_mode=context_auto`
- Kirim `language` + `quality_profile`
- Jangan build spec number-line di FE untuk pilot path

## B. Mid-Conversation Trigger
Generate video harus bisa dipicu saat chat sedang berjalan, bukan hanya di awal.
Tidak ada dependency ke "chat start" event.

## C. Reuse Existing Polling/Playback
- Tetap pakai polling job status existing
- Tetap pakai render card/video player existing

---

## Phases (1 Prompt = 1 Phase)

## Phase 1 - Hardcode Number-Line Context on Workspace Session
Deliverables:
- Context assignment ke node number-line pilot
- Prerequisite ikut tersimpan di metadata

Acceptance:
- Workspace test selalu punya `active_node_id` number-line pilot.

## Phase 2 - Backend Spec Generator from Workspace Context
Deliverables:
- Module generator spec untuk `manim.number_line_quantity.v1`
- Integrasi validasi payload

Acceptance:
- BE bisa produce spec valid tanpa payload spec dari FE.

## Phase 3 - Integrate `context_auto` Mode in Generate-Video Endpoint
Deliverables:
- Schema/request support `generation_mode`
- Branching logic manual vs context_auto
- Audit metadata source/resolved node/template

Acceptance:
- Request context_auto bisa queue job tanpa `template_id/spec_json`.

## Phase 4 - Mobile Integrate Context Auto Generate
Deliverables:
- FE action generate video kirim mode context_auto
- FE tidak lagi kirim spec hardcoded untuk pilot path

Acceptance:
- Generate video dari workspace berhasil via BE-generated spec.

## Phase 5 - Mid-Chat UX Hardening
Deliverables:
- Trigger video tetap stabil saat percakapan sudah panjang
- Loading/error/retry state rapi

Acceptance:
- User bisa chat dulu, lalu generate video kapan saja di sesi yang sama.

---

## Definition of Done (Pilot)
Pilot selesai jika:
1. Workspace session punya context number-line + prerequisite tersimpan.
2. FE trigger video mid-chat dengan `context_auto`.
3. BE generate spec dari context, lolos validator, dan queue render.
4. Artifact video muncul dan bisa diputar di mobile.
