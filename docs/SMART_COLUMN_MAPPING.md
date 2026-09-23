# Smart Column Mapping

The mapper proposes one-to-one source→canonical mappings with confidence, confidence band,
matched alias and a `requiresConfirmation` flag. High confidence begins at 0.90.

The mapping-suggestion endpoint is non-mutating. The user can review/edit before calling the existing
mapping confirmation endpoint, which remains responsible for canonicalization and data-quality validation.

No LLM is required for deterministic matches. A future LLM fallback should receive schema metadata only
and must never silently auto-confirm ambiguous mappings.
