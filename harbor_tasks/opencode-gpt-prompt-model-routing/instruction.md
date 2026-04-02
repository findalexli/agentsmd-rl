# GPT models incorrectly receive the Codex system prompt

## Problem

In `packages/opencode/src/session/system.ts`, the `SystemPrompt.provider()` function routes model IDs to their appropriate system prompts. Currently, all models whose ID contains `"gpt"` (except gpt-4, o1, and o3 variants) are routed to the Codex prompt (`PROMPT_CODEX`).

This is wrong for generic GPT models like `gpt-5.4`. These models are not Codex models and should not receive a Codex-specific system prompt. The Codex prompt is tailored for the Codex CLI agent and includes instructions that don't apply to standard GPT models used through the OpenCode interface.

## Expected behavior

- GPT models whose ID also contains `"codex"` (e.g., `gpt-codex-test`) should continue receiving the Codex prompt
- Other GPT models (whose ID contains `"gpt"` but not `"gpt-4"`, `"o1"`, `"o3"`, or `"codex"`) should receive their own dedicated system prompt that's appropriate for a general-purpose GPT model used in OpenCode

## Relevant files

- `packages/opencode/src/session/system.ts` — the `provider()` function with model routing logic
- `packages/opencode/src/session/prompt/` — directory containing prompt text files for different model families (e.g., `anthropic.txt`, `gemini.txt`, `codex.txt`, `beast.txt`)

## Reproduction

Pass a model object with `api.id` set to `"gpt-5.4"` to `SystemPrompt.provider()`. It returns the Codex prompt instead of a GPT-appropriate prompt.
