# feat(acp): add opt-in flag for question tool

## Problem

Custom ACP (Agent Client Protocol) clients can support interactive question prompts, but ACP should stay safe by default. Currently, the `QuestionTool` is only available for `app`, `cli`, and `desktop` clients. ACP clients have no way to opt in to question tool support.

## Expected Behavior

Add an opt-in environment variable named `OPENCODE_ENABLE_QUESTION_TOOL` that allows ACP clients to enable the `QuestionTool`. The default ACP behavior should remain unchanged (no question tool). Existing `app`, `cli`, and `desktop` clients must continue to get `QuestionTool` without any additional configuration.

## Files to Look At

- `packages/opencode/src/flag/flag.ts` — environment variable flags; define the new flag here
- `packages/opencode/src/tool/registry.ts` — tool registration and gating; update the question tool gating
- `packages/opencode/src/acp/README.md` — ACP documentation; document the new opt-in feature
- `.opencode/agent/translator.md` — agent translator config; add the new env var to the env var list

## Requirements

### Flag definition

In `flag.ts`, define a new exported constant `OPENCODE_ENABLE_QUESTION_TOOL` using the `truthy()` helper (following the pattern of existing flags in the file).

### Tool gating

In `registry.ts`, the question tool should be included when:
- The client type is `app`, `cli`, or `desktop` (existing behavior), OR
- The `OPENCODE_ENABLE_QUESTION_TOOL` flag is set (new opt-in for ACP clients)

Introduce a local `const question` variable that evaluates this combined condition, then use it to determine whether to include `QuestionTool` in the tool list.

### Documentation

In the ACP README (`packages/opencode/src/acp/README.md`), add a section titled `### Question Tool Opt-In` that:
- Notes ACP excludes `QuestionTool` by default
- Shows how to enable it: `OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp`
- References `QuestionTool` by name

### Translator config

In `.opencode/agent/translator.md`, add `OPENCODE_ENABLE_QUESTION_TOOL` to the environment variables list (near the existing `OPENCODE_EXPERIMENTAL_PLAN_MODE` entry).
