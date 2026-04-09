# Add LLM traces list query example and improve trace discovery docs

## Problem

The LLM traces documentation is missing a concrete example for querying multiple traces with aggregated metrics. The existing `example-llm-trace.md` reference only covers fetching a single trace by ID, but there is no corresponding reference for listing/searching traces with property filters and aggregated latency, token usage, costs, and error counts.

Additionally, the `exploring-llm-traces` skill lacks guidance on how to discover the schema before constructing filters — users currently have no clear workflow for finding what properties and values are available in their project before building trace queries. The "By external identifiers" section is also incomplete, lacking a step-by-step workflow.

## Expected Behavior

1. **New traces list reference**: A new `example-llm-traces-list.md` reference document should provide a two-phase SQL query pattern (Phase 1: find matching trace IDs; Phase 2: fetch aggregated metrics). It should aggregate latency, tokens, costs, and error counts while intentionally omitting large content fields. It should direct users to the single-trace query for detailed content.

2. **Template conversion**: The existing `example-llm-trace.md` reference uses a hardcoded SQL query, but most other references in this directory have already been migrated to Jinja2 templates (`.md.j2`) that use the `render_hogql_example()` helper. This file should be converted to match the existing pattern.

3. **Schema discovery guidance**: The `exploring-llm-traces` SKILL.md should guide users through a schema discovery workflow before constructing filters — explaining how to confirm available events, discover filterable properties, and get actual values. It should also include examples of AND-ed filters and person property filtering.

4. **Cross-references**: Both SKILL.md files should be updated to reference the new query example documents.

## Files to Look At

- `products/llm_analytics/skills/exploring-llm-traces/SKILL.md` — the exploring traces skill that needs schema discovery guidance and expanded filter examples
- `products/posthog_ai/skills/query-examples/SKILL.md` — the query examples index that needs a link to the new reference
- `products/posthog_ai/skills/query-examples/references/example-llm-trace.md` — the single-trace example to convert to a `.j2` template
- `products/posthog_ai/skills/query-examples/references/` — directory of existing `.j2` reference templates to follow as patterns
