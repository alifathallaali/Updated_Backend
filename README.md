# PharmaLens AI — FastAPI Backend

This repository contains the PharmaLens AI backend, governed DatasetVersion processing, and an asynchronous upload pipeline backed by Supabase Storage.

## Upload architecture

```text
Browser
  -> POST /api/upload-sessions (short-lived Supabase signed upload token)
  -> Supabase Storage TUS resumable upload (6 MB chunks)
  -> POST /api/upload-sessions/complete
  -> upload_jobs database queue
  -> Render background worker
  -> multi-sheet Excel reading / mapping / quality / curated Parquet
  -> status = ready or failed
```

The API does not keep an HTTP request open while Pandas processes a large workbook. The frontend polls `GET /api/upload-sessions/{job_id}` and supports progress, retry, and cancel.

### Upload endpoints

```text
POST /api/upload-sessions
POST /api/upload-sessions/complete
GET  /api/upload-sessions/{job_id}
POST /api/upload-sessions/{job_id}/retry
POST /api/upload-sessions/{job_id}/cancel
```

The upload session validates extension and enforces a 500 MB limit. `idempotency_key` prevents accidental duplicate jobs. Supabase Storage is the primary store; Cloudflare R2 is optional compatibility fallback and is not required.

## Multi-sheet Excel support

For `.xlsx` and `.xls`, the worker reads every non-empty sheet, concatenates the rows, and adds a `source_sheet` field to each row. Mapping preserves that field, and it is carried into the curated Parquet and downstream provenance. Empty sheets are ignored; a workbook with no non-empty sheets fails clearly.

## Render services

Create two services from the same repository:

### Web service

```text
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Background worker

```text
Build: pip install -r requirements.txt
Start: python worker.py
```

Both services must share the same environment variables and database.

## Required environment variables

```env
DATABASE_URL=...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

The Supabase Storage bucket must already exist with the name `uploads`. The service role is kept only on the backend. The backend creates signed upload tokens; the browser never receives the service-role key. Supabase's storage hostname is used for resumable uploads.

The existing `R2_*` variables are optional and can be left empty when using Supabase only.

## Database migration

Run once against the existing Supabase/Postgres database:

```text
migrations/20260914_upload_jobs.sql
```

## Existing capabilities preserved

- Supabase JWT authentication and workspace isolation
- Dataset Registry with versioning
- Mapping and Data Quality
- Multi-sheet Excel ingestion with source-sheet provenance
- Product catalog and Product Engines
- Product Runs and Achievement from governed DatasetVersion
- AI Copilot and reports
- V0.1 notebook/source integration map: `docs/PHARMALENS_V01_INTEGRATION.md`

## Validation

```bash
python -m compileall -q app worker.py
```

Protected endpoints require `Authorization: Bearer <supabase-access-token>`.

## Intelligence Engine and Copilot

The existing endpoint remains the single Copilot endpoint:

```text
POST /api/copilot/ask
```

It accepts the existing `workspace_id` and `message` fields plus optional structured context:

```json
{
  "workspace_id": 1,
  "message": "Why are we below target?",
  "data_context": "Actual=850; Target=1000; Gap=-150",
  "analysis_type": "achievement",
  "workspace": "Target Setting",
  "filters": {"month": "November", "channel": "AM"}
}
```

The centralized provider order is **Gemini → Groq → OpenRouter**. The existing OpenAI configuration remains an optional compatibility fallback after those providers. Provider failures are logged server-side and returned to the client as a clean HTTP 503 when all providers fail. Successful responses retain the frontend-compatible `content` field and also include `reply`, `provider_used`, and `fallback_used`.

The system prompt enforces DATA → INTELLIGENCE → DECISION → ACTION, same-language responses, evidence-only numerical claims, structured sections, pharmaceutical commercial safety, and prompt-injection protection. `data_context` is explicitly treated as untrusted data and cannot override system instructions.

Run the provider tests with:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
