# feat(acp): add opt-in flag for question tool

## Problem

The ACP (Agent Client Protocol) server currently exposes the `QuestionTool` unconditionally. This is problematic because not all ACP clients support interactive question prompts. The tool should be disabled by default for ACP clients unless explicitly opted in.

## Requirements

1. **Add an environment variable flag** `OPENCODE_ENABLE_QUESTION_TOOL` that controls whether QuestionTool is available.

2. **Update the tool registry gating logic**:
   - QuestionTool should remain enabled for `app`, `cli`, and `desktop` clients (existing behavior)
   - QuestionTool should be disabled for `acp` client by default
   - QuestionTool should be enabled for `acp` when `OPENCODE_ENABLE_QUESTION_TOOL=1` is set

3. **Update documentation**:
   - Add a "Question Tool Opt-In" section to the ACP README explaining the flag and how to enable it
   - Add `OPENCODE_ENABLE_QUESTION_TOOL` to the environment variable glossary in the project documentation

## Safety Note

The default ACP behavior should remain unchanged (QuestionTool excluded). The tool should only be available when explicitly opted in via the environment variable.

## Enable Example

```bash
OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp
```

Only enable this for ACP clients that support interactive question prompts.
