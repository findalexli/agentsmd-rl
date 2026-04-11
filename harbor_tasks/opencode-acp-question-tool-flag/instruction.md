# feat(acp): add opt-in flag for question tool

## Problem

Custom ACP (Agent Client Protocol) clients can support interactive question prompts, but ACP should stay safe by default. Currently, the `QuestionTool` is only available for `app`, `cli`, and `desktop` clients. ACP clients have no way to opt in to question tool support.

## Expected Behavior

ACP clients should be able to opt in to `QuestionTool` via an environment flag. The default ACP behavior should remain unchanged (no question tool). Existing `app`, `cli`, and `desktop` clients must continue to get `QuestionTool` without any additional configuration.

## Files to Look At

- `packages/opencode/src/flag/flag.ts` — environment variable flags; a new flag needs to be added here
- `packages/opencode/src/tool/registry.ts` — tool registration and gating; the question tool gating logic needs updating to also check the new flag
- `packages/opencode/src/acp/README.md` — ACP documentation; should document how to enable the question tool for ACP clients
- `.opencode/agent/translator.md` — agent translator config with env var reference list; should include the new env var

## Additional Notes

After making the code changes, update the relevant documentation and configuration files to reflect the new feature. The ACP README should explain how ACP clients can enable the question tool, and the agent translator config should reference the new environment variable.
