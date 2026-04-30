# Update Claude skills for Tinker SDK v0.15.0

Source: [thinking-machines-lab/tinker-cookbook#479](https://github.com/thinking-machines-lab/tinker-cookbook/pull/479)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/checkpoints/SKILL.md`
- `.claude/skills/logging/SKILL.md`
- `.claude/skills/manage-skills/SKILL.md`
- `.claude/skills/tinker-cli/SKILL.md`
- `.claude/skills/tinker-sdk/SKILL.md`
- `.claude/skills/tinker-types/SKILL.md`

## What to add / change

## Summary

- **tinker-sdk**: Fix broken init pattern (`TrainingClient(model_name=...)` → `ServiceClient` entry point), add `ServiceClient`, `RestClient`, `forward()`, `forward_backward_custom()`, `SamplingClient` extras (`include_prompt_logprobs`, `get_base_model()`)
- **tinker-types**: Add `LoraConfig`, response types (`ForwardBackwardOutput`, `SampleResponse`, etc.), checkpoint/run types (`TrainingRun`, `Checkpoint`, `ParsedCheckpointTinkerPath`), error type hierarchy
- **tinker-cli**: New Layer 1 skill documenting the `tinker` CLI — `run list/info`, `checkpoint list/info/download/publish/unpublish/set-ttl/delete/push-hf`, `version`
- **checkpoints**: Add REST API and CLI management section (publish, TTL, delete)
- **logging**: Add tracing/profiling section (`@scope`, `trace_iteration`, Gantt charts, `timing_spans.jsonl`, Perfetto traces)
- **manage-skills**: Update Layer 1 inventory to include `tinker-cli`

## Test plan
- [x] Verify all skills are under 200 lines (181, 183, 149, 139, 193, 153)
- [x] Verify API claims match Tinker SDK v0.15.0 source (23/23 verified)
- [x] Verify CLI commands match `tinker` CLI implementation (9/9 verified)
- [x] Verify tracing docs match `tinker_cookbook/utils/trace.py` (9/9 verified)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
