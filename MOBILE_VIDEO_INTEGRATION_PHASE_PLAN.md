# Mobile Video Integration Phase Plan (Aligned to Current BE + Mobile)

## Scope
- Fokus hanya integrasi video generation (Manim) antara `wicara-mobile-brian` dan `WICARA-BE`.
- Tidak mencakup pretest/posttest/adaptive engine selain kebutuhan payload video.
- Format kerja: **1 phase = 1 prompt**.

---

## Current Reality Check

### Backend (WICARA-BE)
Status: **READY**

Sudah tersedia:
- `POST /api/v1/workspaces/{workspace_id}/generate-video`
- `GET /api/v1/animation/status/{job_id}`
- `GET /api/v1/media-artifacts`
- `GET /api/v1/media-artifacts/{artifact_id}`
- `GET /api/v1/media-artifacts/{artifact_id}/status`

Catatan penting BE:
- Endpoint `generate-video` **wajib** menerima `template_id` + `spec_json`.
- `spec_json` divalidasi ketat oleh schema template (`template_validation.py`).
- Jika payload salah, job bisa langsung `failed` (validation error), jadi mobile harus kirim payload valid.

### Mobile (wicara-mobile-brian)
Status: **NOT INTEGRATED**

Kondisi saat ini:
- Workspace masih simulasi timer (`videoLoading -> videoReady`) + event `generation_mode=simulated_mobile_timer`.
- `WorkspaceRepository` belum punya method `generateVideo` / `getAnimationStatus`.
- Domain model workspace belum punya model queue/status/artifact video.
- Home gallery belum fetch data backend; UI masih placeholder.
- Belum ada package video player untuk playback URL backend.

---

## Decision Gate (Wajib Sebelum Implement)

### Gate A — Sumber `template_id` + `spec_json`
Karena BE tidak bisa generate job tanpa payload valid, pilih salah satu:
1. **MVP Hardcoded by module** (paling cepat): mobile mapping `module/topic -> template_id + spec_json`.
2. **Server-generated payload**: endpoint baru BE untuk generate payload dari context chat/konsep.
3. **Hybrid**: mobile kirim minimal context, BE isi payload final.

Rekomendasi untuk fase ini: **Opsi 1 (MVP hardcoded by module)** supaya integrasi jalan dulu.

### Gate B — Video player
Pilih stack player mobile (contoh: `video_player` + optional wrapper UI).

---

## Phase 1 — Mobile Contract Wiring
### Goal
Mobile bisa hit endpoint video BE secara typed (queue + status).

### Changes
- Tambah model domain workspace:
  - `WorkspaceGenerateVideoResponse`
  - `AnimationJobStatusResponse`
  - `WorkspaceMediaArtifact` (subset dari `MediaArtifactRead`)
- Extend `WorkspaceRepository`:
  - `generateVideo(...)`
  - `getAnimationStatus(...)`
- Implement call di `ApiWorkspaceRepository`:
  - `POST /api/v1/workspaces/{workspace_id}/generate-video`
  - `GET /api/v1/animation/status/{job_id}`

### Acceptance
- Mobile berhasil mendapatkan `job_id`, `artifact_id`, `status`.
- Mobile berhasil membaca status job by `job_id`.

### Prompt
`Kerjakan Phase 1 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 2 — Replace Simulated Workspace Flow
### Goal
Hapus simulasi timer dan pakai flow queue backend nyata.

### Changes
- Refactor `workspace_modules_page.dart`:
  - Hapus `Timer(1350ms)` simulasi.
  - Tap `Generate video` -> call `generateVideo(...)`.
  - Simpan `job_id`, `artifact_id`, `template_id` di state lokal.
- **Jangan append manual event simulasi dari mobile**; backend sudah menulis event `media_generated`.

### Acceptance
- Generate video benar-benar membuat job di backend.
- UI tidak pernah langsung `ready` tanpa polling.

### Prompt
`Kerjakan Phase 2 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 3 — Job Polling + Error State
### Goal
Lifecycle status robust sampai final (`ready` / `failed`).

### Changes
- Poll `GET /api/v1/animation/status/{job_id}` tiap 2–3 detik.
- Mapping status:
  - `queued|processing` -> loading/progress
  - `ready` -> tampil artifact card
  - `failed` -> tampil error + retry
- Guard:
  - stop polling on dispose
  - stop polling on final state
  - timeout fail-safe (mis. 5 menit)

### Acceptance
- Tidak ada loading tanpa akhir.
- Error reason backend kebaca jelas di UI.

### Prompt
`Kerjakan Phase 3 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 4 — Workspace Playback Card (Real Artifact)
### Goal
Workspace menampilkan hasil video nyata dari backend.

### Changes
- Ganti `_GeneratedWorkspaceVideoCard` statis dengan data backend:
  - `title`, `subtitle`
  - `thumbnail_url`
  - `duration_seconds` / `duration_label`
  - `video_url`
- Integrasi package video player untuk play URL.
- Handle `video_url == null` tanpa crash.

### Acceptance
- Video yang `ready` bisa diputar dari URL backend.
- Thumbnail/durasi/title tidak hardcoded.

### Prompt
`Kerjakan Phase 4 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 5 — Home Gallery From `/media-artifacts`
### Goal
Gallery di Home memakai artifact nyata, bukan placeholder.

### Changes
- Extend `HomeRepository` + `ApiHomeRepository`:
  - method fetch list artifacts
  - optional fetch detail artifact
- Ubah tab gallery untuk render data API.
- Empty state hanya saat `items=[]` dari backend.

### Acceptance
- Artifact dari workspace muncul di gallery user.
- Detail gallery menampilkan data video yang sama dengan backend.

### Prompt
`Kerjakan Phase 5 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 6 — Payload Strategy Hardening
### Goal
Mengurangi risiko 422 validation dari `template_id/spec_json`.

### Changes
- Implement MVP mapping payload di mobile:
  - `module/topic -> template_id + spec_json` valid schema.
- Tambah fallback strategy:
  - jika mapping tidak ada -> disable tombol generate + message yang jelas.
- Log request metadata minimal (`template_id`, `language`) untuk debug.

### Acceptance
- Generate tidak gagal hanya karena payload kosong/invalid.
- Semua module yang disupport punya payload valid.

### Prompt
`Kerjakan Phase 6 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Phase 7 — QA & Runbook Update
### Goal
Dokumentasi test sesuai flow backend nyata.

### Changes
- Update `test.md` (bagian video saja):
  - create/resume workspace
  - generate video
  - poll status
  - verify workspace card
  - verify gallery sync
- Tambah checklist ops:
  - worker running
  - queue backend configured
  - storage bucket exists
  - media public/private URL behavior

### Acceptance
- Tim bisa retest end-to-end tanpa instruksi dari chat.

### Prompt
`Kerjakan Phase 7 dari MOBILE_VIDEO_INTEGRATION_PHASE_PLAN.md`

---

## Out of Scope
- Refactor besar UI Home/Workspace di luar video.
- Generasi konten LLM non-video.
- Perubahan arsitektur backend queue/render selain kebutuhan integrasi mobile.

---

## Execution Order
1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6
7. Phase 7

