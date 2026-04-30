# feat(acp): add opt-in flag for question tool

## Problem

The ACP (Agent Client Protocol) server currently exposes the `QuestionTool` unconditionally. This is problematic because not all ACP clients support interactive question prompts. The tool should be disabled by default for ACP clients unless explicitly opted in.

## Requirements

1. **Add environment variable flag in `packages/opencode/src/flag/flag.ts`**:
   - Add `OPENCODE_ENABLE_QUESTION_TOOL` as a truthy flag in the `Flag` namespace
   - The flag should read from the `OPENCODE_ENABLE_QUESTION_TOOL` environment variable

2. **Update the tool registry gating logic in `packages/opencode/src/tool/registry.ts`**:
   - QuestionTool should remain enabled for `app`, `cli`, and `desktop` clients (existing behavior)
   - QuestionTool should be disabled for `acp` client by default
   - QuestionTool should be enabled for `acp` when `Flag.OPENCODE_ENABLE_QUESTION_TOOL` is truthy

3. **Update documentation in `packages/opencode/src/acp/README.md`**:
   - Add a "Question Tool Opt-In" section that:
     - States that ACP excludes `QuestionTool` by default
     - Shows the command `OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp`
     - Includes a warning to "Enable this only for ACP clients that support interactive question prompts"

4. **Update the environment variable glossary in `.opencode/agent/translator.md`**:
   - Add `OPENCODE_ENABLE_QUESTION_TOOL` to the list of environment variables

## Safety Note

The default ACP behavior should remain unchanged (QuestionTool excluded). The tool should only be available when explicitly opted in via the environment variable.

## Enable Example

```bash
OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp
```

Only enable this for ACP clients that support interactive question prompts.
