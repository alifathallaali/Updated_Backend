# PharmaLens AI — Launch Closure Wave 2 Security Manifest

Canonical base: `PharmaLens AI — POST-CONSUMER-HEALTH CONSOLIDATED CHECKPOINT` (264/264 approved baseline).

Scope: security, tenant isolation, and production configuration only. No business engine or product methodology changes.

## Security posture

The MVP retains backend/service-role mediated database access rather than enabling broad RLS in this wave. Direct `anon` and `authenticated` privileges on protected application tables are revoked by `migrations/20260923_launch_security_posture.sql`. The frontend may use the Supabase public key for Auth only; protected commercial-data access must flow through authenticated FastAPI endpoints. Storage remains private and is accessed through service-role operations or narrowly scoped signed upload/download credentials issued after workspace authorization.

Residual deployment validation: apply the migration to a clean/staging Supabase project and verify grants/bucket privacy live during Wave 3. Do not claim RLS is enabled; it is not.

## Closed gaps

- `/api/files/presign`, dataset presign, dataset server upload: workspace membership required before storage credential or write.
- Dataset/file metadata registration rejects storage keys outside the authorized workspace prefix.
- Upload filenames are normalized to a safe single object-key segment.
- Upload Jobs no longer expose `SUPABASE_SERVICE_ROLE_KEY` to the browser; they issue scoped signed upload credentials.
- Copilot history/append explicitly reject unauthorized workspaces; Copilot ask has a per-user beta limiter.
- Upload entry points have a per-user beta limiter; server-side upload is size bounded.
- Production CORS uses `CORS_ORIGINS` only; wildcard Vercel regex removed.
- Production backend config fails fast when database/Supabase/service-role/CORS/LLM requirements are absent.
- Production frontend API and Supabase public configuration fail explicitly rather than silently using a hard-coded production backend or placeholder credentials.

## Validation

- Security focused: 10/10 PASS.
- Full backend regression: 274/274 PASS (264 canonical + 10 Wave-2 security tests).
- Python compileall: PASS.
- Wave 1 frontend build validation remains OPEN; no claim is made that TypeScript/lint/Next production build passed.
