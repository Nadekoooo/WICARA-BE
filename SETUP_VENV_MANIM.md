# WICARA-BE Manim Local Setup

Dokumen ini khusus setup local backend + worker untuk pipeline Manim video generation.

## 1) Create and activate venv

```powershell
cd "C:\Kuliah\Semester 6\Wicara App\final\WICARA-BE"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2) Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[test,render]"
```

Catatan:
1. `render` extra wajib untuk `manim-voiceover[gtts]`.
2. Repo ini mem-pin `setuptools<81` supaya `manim-voiceover` yang masih import `pkg_resources` tetap jalan.

## 3) Prepare env file

```powershell
Copy-Item .env.example .env
```

Minimal config untuk test local manim:
1. `MEDIA_JOB_QUEUE_BACKEND=noop`
2. `MEDIA_STORAGE_BACKEND=local`
3. `MEDIA_STORAGE_PUBLIC_BASE_URL=/media-storage`
4. `MEDIA_TTS_PROVIDER=gtts_voiceover`
5. `MEDIA_TTS_REQUIRED=true` (opsional, tapi disarankan kalau audio wajib ada)

Untuk Supabase pooler, gunakan connection string pooler dari dashboard (host `*.pooler.supabase.com`).

## 4) Run migration

```powershell
alembic upgrade head
```

## 5) Run API and worker

Terminal 1:

```powershell
uvicorn app.main:app --reload
```

Terminal 2:

```powershell
python -m app.workers.media_worker
```

## 6) Verify audio exists in rendered video

```powershell
ffprobe -v error -select_streams a -show_entries stream=index -of json "<path-to-final_video.mp4>"
```

Jika audio ada, field `streams` tidak kosong.

## 7) Common errors and fixes

1. `ModuleNotFoundError: No module named 'pkg_resources'`
Solusi: reinstall dependency render di venv aktif:
```powershell
python -m pip install -e ".[render]"
```

2. `prepared statement "_pg3_0" does not exist` atau `DuplicatePreparedStatement`
Solusi: update ke kode terbaru repo ini. Session/engine sudah men-disable prepared statement otomatis saat host Supabase pooler terdeteksi.

3. Video `ready` tapi tidak ada audio
Solusi:
1. pastikan `manim-voiceover` terpasang (`pip install -e ".[render]"`)
2. set `MEDIA_TTS_REQUIRED=true` agar job gagal jika stream audio tidak ada
3. queue ulang job
