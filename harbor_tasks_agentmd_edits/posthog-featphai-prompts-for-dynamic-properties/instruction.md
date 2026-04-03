# Document dynamic person and event properties for the AI agent

## Problem

PostHog's AI agent (the "taxonomy agent") uses tools to discover event and person properties. However, some properties follow dynamic naming patterns — they are generated per survey, feature flag, or product tour (e.g., `$survey_dismissed/{survey_id}`, `$feature/{flag_key}`, `$product_tour_shown/{tour_id}`). These dynamic properties are intentionally excluded from tool results because they'd be too noisy (hundreds of entries), but the AI agent currently has no way to know they exist or how to construct them.

When a user asks a question involving surveys, feature flags, or product tours, the AI agent can't find the relevant properties and gives incomplete or wrong answers.

## Expected Behavior

The AI agent should be informed about dynamic property patterns at multiple levels:

1. **System prompt**: The taxonomy prompt (`PROPERTY_TYPES_PROMPT`) should document the dynamic property patterns so the agent knows they exist even before calling tools.

2. **Tool results**: When the agent retrieves person or event properties via taxonomy tools, the results should include a hint about dynamic patterns that won't appear in the list. Person entity queries should get person-specific hints; event property queries should get event-specific hints.

3. **Omit filter**: The event taxonomy query runner's property filter should be updated to also exclude the newer dynamic patterns (`$feature_enrollment/`, `$feature_interaction/`, `$product_tour_*`) so they don't clutter results when they do appear.

4. **Skill documentation**: The query-examples SKILL.md should reference a new doc explaining these dynamic properties with SQL examples for looking up the IDs needed to construct property names.

## Files to Look At

- `ee/hogai/chat_agent/taxonomy/prompts.py` — defines `PROPERTY_TYPES_PROMPT`, the system prompt for the taxonomy agent
- `ee/hogai/tools/read_taxonomy/core.py` — `execute_taxonomy_query()` dispatches taxonomy tool calls and returns results
- `posthog/hogql_queries/ai/event_taxonomy_query_runner.py` — `_get_omit_filter()` defines which property patterns to exclude from results
- `products/posthog_ai/skills/query-examples/SKILL.md` — index of query examples and reference docs for the AI agent
- `products/posthog_ai/skills/query-examples/references/` — directory for reference documentation files
