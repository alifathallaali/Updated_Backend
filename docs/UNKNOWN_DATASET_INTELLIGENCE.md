# Unknown Dataset Intelligence

The layer inspects governed schema metadata and suggests compatible exercises.
It uses column names, aliases and limited profile metadata; it does not send raw rows to an LLM.

Outputs include semantic column roles, likely dataset type, schema confidence, ranked exercise suggestions,
missing fields and a clarification prompt when the schema is ambiguous.

This is advisory. The server-side compatibility gate remains authoritative.
