# Post-Feature Security Workflow

1. Inspect the existing implementation and architecture.
2. Identify changed files and affected interfaces.
3. Run normal tests.
4. Run the Security Review Skill.
5. Run relevant focused skills:
   - authentication-review
   - authorization-review
   - input-validation
   - api-security
   - data-security
   - file-upload-security
   - ai-agent-security
   - secrets-management
   - dependency-security
   - security-testing
6. Fix CRITICAL/HIGH findings.
7. Add regression tests for fixed issues.
8. Re-run tests and security review.
9. Mark:
   - BLOCKED if release-blocking findings remain.
   - APPROVED WITH WARNINGS for accepted lower-risk findings.
   - APPROVED when no release-blocking findings remain.
