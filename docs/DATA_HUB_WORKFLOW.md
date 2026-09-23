# Data Hub Workflow Integration

Dataset list responses expose the latest version status and a deterministic `nextAction`: profile, review_mapping, wait, retry, or analyze. The UI uses this state to guide the user through Upload → Profile → Mapping/Validation → Ready.

The backend remains authoritative for status; the frontend does not infer readiness from filenames or upload completion alone.
