# Security Checklist

## Identity
- [ ] Authentication reviewed
- [ ] Session/token lifecycle reviewed
- [ ] OAuth/OIDC flows reviewed

## Authorization
- [ ] Server-side authorization
- [ ] Tenant/company isolation
- [ ] Object-level authorization
- [ ] Admin/privileged actions

## Input/API
- [ ] Schema validation
- [ ] Injection checks
- [ ] SSRF/path traversal checks
- [ ] Rate limits
- [ ] Safe error responses

## Data
- [ ] Sensitive data minimization
- [ ] Database access controls
- [ ] Export/download controls
- [ ] Logs do not expose secrets

## Files
- [ ] Type/size limits
- [ ] Safe storage
- [ ] Parser/OCR risks
- [ ] Download authorization
- [ ] Spreadsheet formula injection

## AI
- [ ] Prompt injection
- [ ] Tool permissions
- [ ] Context/data isolation
- [ ] Output validation
- [ ] Consequential-action confirmation

## Secrets
- [ ] No secrets in source
- [ ] No secrets in frontend
- [ ] CI/CD reviewed
- [ ] Exposed credentials rotated

## Dependencies
- [ ] Vulnerability scan
- [ ] Lockfile reviewed
- [ ] Unnecessary packages removed

## Release gate
- [ ] No unresolved CRITICAL findings
- [ ] No unresolved HIGH findings unless explicitly accepted
- [ ] Security regression tests added
