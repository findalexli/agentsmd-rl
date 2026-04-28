# feat: add error handling guidance to SKILL.md

Source: [alibaba-flyai/flyai-skill#19](https://github.com/alibaba-flyai/flyai-skill/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/flyai/SKILL.md`

## What to add / change

## Summary

- Add `## Error Handling` section to SKILL.md
- Four-step strategy: Validate → Diagnose → Adapt → Be transparent
- Provides general guidance for AI agents to handle errors and edge cases

Related: #12 #13 #14 #17 #18

## Test results

Tested against `flyai-cli@1.0.14`:

| Test case | Expected | Actual |
|-----------|----------|--------|
| Past date `2025-01-01` for flight | Error or empty | Silently returns today's flights |
| Invalid city `asdfgh` for flight | Error | Returns flights from Vaasa (Finland) |
| `火星` (Mars) for hotel | Error or empty | Returns hotels in New Delhi |
| Wrong date format `20260501` | stderr error | stdout JSON `{"status":1,"message":"not found flight solution"}` |
| Nonexistent city for POI | Same as above | stdout JSON `{"status":1,"message":"not found poi"}` |
| Past date `2020-01-01` for train | Error or empty | Silently returns today's trains |

## Test plan

- [ ] Verify SKILL.md renders correctly in markdown
- [ ] Confirm no changes to existing sections

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
