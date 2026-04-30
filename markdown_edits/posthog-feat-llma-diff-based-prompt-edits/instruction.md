# Add diff-based edits to prompt publish API

## Problem

The prompt management MCP tool (`posthog:prompt-update`) currently requires sending the entire prompt payload on every update. For large prompts this is inefficient — agents using the tool must transmit the full content even for a one-word change.

## Expected Behavior

The `PATCH /llm-analytics/prompts/name/<name>/` endpoint should accept an optional `edits` field as an alternative to `prompt`. Each edit is a find/replace pair (`old`/`new`) applied sequentially to the current version's content:

- `edits` and `prompt` are mutually exclusive — providing both should return 400
- Providing neither should also return 400
- Each `old` text must match exactly once in the current prompt — 0 matches or 2+ matches should return 400 with the failing edit index
- Edits must work on both string and JSON-structured prompts
- Existing callers sending `prompt` must be unaffected (fully backwards-compatible)

## Files to Look At

- `posthog/api/services/llm_prompt.py` — service layer where a new `apply_prompt_edits()` function should live
- `posthog/api/llm_prompt_serializers.py` — serializers that need the new `edits` field with validation
- `posthog/api/llm_prompt.py` — view that calls the service and handles the new error type
- `products/llm_analytics/mcp/prompts.yaml` — MCP tool definition to update with edits parameter
- `products/llm_analytics/skills/skills-store/SKILL.md` — skill documentation that should be updated to document the new incremental editing workflow

After implementing the code changes, update the relevant skill documentation and MCP tool definitions to reflect the new editing capability. The skills-store SKILL.md should explain how to use the new `edits` parameter with a usage example.
