# PharmaLens AI Integration Status

## Existing versus new

| Concern | Existing implementation | New extension |
|---|---|---|
| Authentication | Supabase JWT and existing `get_current_user` | Reused unchanged |
| Authorization | Workspace membership checks in CRUD/routers | Skills catalog is authenticated; new upload jobs remain workspace-scoped |
| Database | Existing SQLAlchemy/Postgres models | `upload_jobs` migration and model |
| Ingestion | Dataset Registry and canonical service | Supabase TUS upload, background worker, multi-sheet Excel ingestion |
| Product execution | Existing Product Engine Registry | Product Runs continue from governed DatasetVersion |
| Copilot | Existing `/api/copilot` and LLM wrapper | Commercial skill discovery supplies trusted framework context only |
| Commercial skills | Previously not registered | Controlled snapshot under `app/skills/commercial`, source commit recorded |
| Security skills | Previously not registered | Independent metadata registry under `app/skills/security`; not injected into commercial reasoning |
| Dashboard | Existing dashboard route/design system | Not replaced; full AM/Retail dashboard work remains a separate feature phase |
| Reports | Existing report routers/generators | Not replaced |

## Skill sources

- Commercial: `Pharma-commercial-skills`, commit `cf61ede8a0c11fa9b9f6e8f98205b8c4048cac57`.
- Security: `AI-Agent-security-skills`, commit `cba5d66e6fda6123247e2b4baa5fd6c65c7a3bd6`.

The `/api/skills/catalog` endpoint returns metadata only and requires the existing authentication. Skill source documents are not exposed to normal users.

## Commercial reasoning boundary

Commercial skill documents are guidance for choosing an analysis framework. They are not customer evidence. Copilot must separate provided data, calculated outputs, assumptions, and recommendations, and must not fabricate missing commercial values.

## Remaining implementation phases

The prompt describes a broad product program. The following are not claimed complete by this integration:

1. Full AM and Retail canonical schemas and reconciliation engine.
2. Role-scoped dashboard aggregation for Rep, Supervisor, and National Manager.
3. Governed AM/Retail/Achievement Excel generation from one aggregation service.
4. Grounded dashboard insight endpoint using the exact active authorized aggregate.
5. Restricted/licensed dataset classification and export policy across every legacy endpoint.
6. Automated security skill runner and CI release gate.
7. Regression fixtures covering the 25 acceptance cases.

These should be implemented as separate slices after the existing data contracts are confirmed, rather than creating parallel systems.
