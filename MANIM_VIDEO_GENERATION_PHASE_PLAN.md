# WICARA BE - Manim Video Generation Phase Plan

Fokus dokumen ini hanya untuk pipeline **video generation**:

- template-based Manim render
- Manim Voiceover (`GTTSService`) + sync di scene
- FFmpeg post-process
- artifact storage + status polling

Di luar scope dokumen ini: pretest, posttest, mastery engine, session router, daily evaluation.

## 1. Target Akhir

User action `generate video` menghasilkan:

1. job tercatat di DB,
2. worker render berdasarkan `template_id + spec_json`,
3. audio voiceover sinkron,
4. video + thumbnail tersimpan,
5. status bisa dipolling sampai `ready/failed`.

## 2. API Contract Minimal (Manim Only)

1. `POST /api/v1/animation/queue`
- input: `workspace_id` (optional), `concept_id` (optional), `template_id`, `spec_json`, `language`, `quality_profile`
- output: `job_id`, `artifact_id`, `status=queued`

2. `GET /api/v1/animation/status/{job_id}`
- output: `status`, `progress`, `message`, `artifact_id`, `video_url`, `thumbnail_url`, `error`

3. `GET /api/v1/media-artifacts/{artifact_id}`
- output metadata artifact lengkap

## 3. Data Model Minimal

1. `media_artifacts`
- `id`, `user_id`, `workspace_id`, `concept_id`
- `template_id`, `spec_json`, `language`, `quality_profile`
- `status`, `video_url`, `thumbnail_url`, `duration_seconds`
- `render_meta_json`, `created_at`, `updated_at`

2. `media_jobs`
- `id`, `artifact_id`, `status`, `progress`, `message`
- `attempt`, `error`, `started_at`, `finished_at`

3. Optional `media_job_logs`
- stream log render per tahap untuk debugging.

## 4. Execution Phases (1 Prompt = 1 Phase)

### Phase 1 - Model, Migration, Endpoint Skeleton

Objective:
- Ngebangun pondasi data + endpoint kosong dulu.

Deliverables:
- migration `media_artifacts` + `media_jobs`
- `POST /animation/queue` create artifact+job (`queued`)
- `GET /animation/status/{job_id}` return status

Definition of Done:
- job bisa dibuat dan dipolling walau worker belum render.

Prompt:

```text
Kerjakan PHASE 1 khusus MANIM di WICARA-BE: buat model+migration media_artifacts dan media_jobs, lalu implement endpoint POST /api/v1/animation/queue dan GET /api/v1/animation/status/{job_id} dengan status queued. Tambahkan test API dasar.
```

### Phase 2 - Queue Worker + Job Lifecycle

Objective:
- Jalanin worker asynchronous yang mengambil job queued.

Deliverables:
- Redis queue adapter
- worker process bootstrap
- lifecycle status: `queued -> processing -> ready/failed`
- progress update per tahap

Definition of Done:
- worker bisa ambil job dummy dan update state sampai terminal.

Prompt:

```text
Kerjakan PHASE 2 khusus MANIM di WICARA-BE: integrasikan Redis queue + worker process untuk media_jobs, implement lifecycle status queued-processing-ready/failed, dan update progress/message per tahap. Sertakan test service/job lifecycle.
```

### Phase 3 - Template Registry + Spec Validation

Objective:
- Pastikan render aman dan deterministic dari template.

Deliverables:
- `template_registry.json` (`template_id -> template_path/class/schema`)
- schema validation per template (Pydantic/JSON Schema)
- compatibility alias (mis. mismatch id taxonomy vs file existing)

Definition of Done:
- queue reject spec invalid sebelum render.

Prompt:

```text
Kerjakan PHASE 3 khusus MANIM di WICARA-BE: buat template_registry.json, validasi spec_json berdasarkan schema tiap template, dan tambahkan compatibility alias untuk template_id yang mismatch. Jika invalid, job langsung failed dengan error terstruktur.
```

### Phase 4 - Render Engine Integration (Manim Only)

Objective:
- Render MP4 beneran dari template + spec.

Deliverables:
- worker panggil runner render (template wrapper + Manim CLI)
- output MP4 tersimpan lokal sementara
- handling timeout/retry minimal

Definition of Done:
- 1 sample spec bisa menghasilkan MP4 valid.

Prompt:

```text
Kerjakan PHASE 4 khusus MANIM di WICARA-BE: sambungkan worker ke engine render template-based Manim (bukan arbitrary codegen), hasilkan MP4 dari template_id+spec_json, dan implement timeout/retry minimal. Tambahkan integration test satu sample template.
```

### Phase 5 - Voiceover + FFmpeg + Duration Policy

Objective:
- Kualitas video: ada narasi sinkron, tidak kependekan.

Deliverables:
- semua template prioritas pindah ke `VoiceoverScene`
- TTS pakai `manim_voiceover.services.gtts.GTTSService(lang=...)` (tanpa API key)
- sinkronisasi animasi lewat blok `with self.voiceover(...) as tracker:` di dalam scene
- FFmpeg dipakai untuk thumbnail extraction + metadata probe (bukan merge audio manual)
- duration guardrail (mis. SMP min 90 detik) + warning/soft-fail policy

Definition of Done:
- artifact punya `video_url`, `thumbnail_url`, `duration_seconds` dan lolos quality gate dasar.

Prompt:

```text
Kerjakan PHASE 5 khusus MANIM di WICARA-BE: migrasikan template prioritas ke VoiceoverScene dengan GTTSService multi-bahasa (berdasarkan field language), sinkronkan animasi lewat blok voiceover di scene, gunakan FFmpeg hanya untuk thumbnail+probe, dan simpan duration_seconds + metadata quality gate ke media_artifacts.
```

### Phase 6 - Storage Upload + Artifact Readiness

Objective:
- Hasil render jadi artifact yang bisa dipakai mobile/frontend.

Deliverables:
- upload video/thumbnail ke object storage
- persist public/signed URL
- `GET /media-artifacts/{artifact_id}` final response contract

Definition of Done:
- status `ready` selalu punya URL valid.

Prompt:

```text
Kerjakan PHASE 6 khusus MANIM di WICARA-BE: upload output video+thumbnail ke storage, simpan URL di media_artifacts, finalisasi status ready/failed, dan rapikan response GET /api/v1/media-artifacts/{artifact_id}. Tambahkan test end-to-end queue->ready.
```

### Phase 7 - Hardening, Observability, and Ops

Objective:
- Pipeline siap dipakai tim lain tanpa blind debugging.

Deliverables:
- structured logs by `job_id`/`artifact_id`
- failure taxonomy (`validation_error`, `render_error`, `tts_error`, `ffmpeg_error`, `upload_error`)
- retry policy per error class
- metrics: render time, fail rate, avg duration

Definition of Done:
- kalau job gagal, tim bisa tahu gagal di tahap mana tanpa buka source code.

Prompt:

```text
Kerjakan PHASE 7 khusus MANIM di WICARA-BE: tambahkan observability lengkap (structured log, error taxonomy, retry policy, dan metric render), sehingga tiap failure bisa ditrace per job_id/artifact_id. Lengkapi dengan test untuk error-path utama.
```

## 5. Prioritas Template Awal

Gunakan template yang sudah ada dulu:

1. `manim.equation_balance.v1`
2. `manim.graph_explanation.v1`
3. `manim.sequence_pattern.v1`
4. `manim.number_line_quantity.v1`
5. `manim.ratio_proportion.v1`

Setelah stabil, baru tambah template lain.

## 6. Update Keputusan Arsitektur (May 2026)

Keputusan terbaru untuk voiceover:

1. **Gunakan Option B**: `manim-voiceover + GTTSService` sebagai jalur utama TTS.
2. `language` dari API request jadi source-of-truth pemilihan bahasa voiceover (`lang` gTTS).
3. Sinkronisasi tidak lagi mengandalkan merge audio eksternal; sync ditangani di scene code (`with self.voiceover(...)`).
4. FFmpeg tetap dipakai untuk thumbnail extraction, duration probe, dan tahap media ops lain.

Implikasi langsung dan status implementasi:

1. Jalur `edge_tts` di postprocess sudah dideprecate; postprocess sekarang tidak generate audio eksternal.
2. Dependency runtime sudah diarahkan ke `manim-voiceover[gtts]`.
3. Template base sudah dimigrasikan ke `VoiceoverScene` dengan GTTS multi-bahasa berbasis `language`.
4. Fallback narasi sudah ada: jika `voiceover_script` kosong, gunakan gabungan `title/subtitle/steps/summary`.
5. Error taxonomy tetap pakai `tts_error`; dapat ditambah `voiceover_render_error` jika nanti dibutuhkan lebih granular.

## 7. Gap Coverage (Khusus Video Generation)

Berdasarkan `gap.md`, plan ini meng-cover:

1. Gap video generation/media (section 7) - **Covered penuh**.
2. Gap media gallery artifact nyata (section 10/12) - **Covered** via artifact pipeline.
3. Gap data model media render jobs (section 15) - **Covered**.
4. Gap minimum build list: generate-video endpoint + polling + artifact nyata (section 17) - **Covered**.

Yang sengaja tidak di-cover di dokumen ini:

- AI chat response engine
- pretest/posttest/daily logic
- canvas parser intelligence
- report aggregation non-media

## 8. Status Implementasi (May 2026)

Status pengerjaan phase untuk pipeline Manim:

1. Phase 1 - **Done**
2. Phase 2 - **Done**
3. Phase 3 - **Done**
4. Phase 4 - **Done**
5. Phase 5 - **Done** (VoiceoverScene + GTTS, multi-bahasa)
6. Phase 6 - **Done** (storage upload + URL final artifact)
7. Phase 7 - **Done** (structured log, failure taxonomy, retry policy, worker metrics)
