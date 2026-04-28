# refactor(sapcc-audit): decompose SKILL.md into references (ADR-186)

Source: [notque/claude-code-toolkit#436](https://github.com/notque/claude-code-toolkit/pull/436)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/sapcc-audit/SKILL.md`
- `skills/sapcc-audit/references/output-templates.md`
- `skills/sapcc-audit/references/phase-1-discover-commands.md`
- `skills/sapcc-audit/references/phase-2-dispatch-agents.md`

## What to add / change

## Summary
- Extract 225 lines of inline content from `skills/sapcc-audit/SKILL.md` into three reference files that load per-phase.
- SKILL.md reduced from 320 → 124 lines (61% reduction). The orchestrator now carries routing intent only; detection commands, dispatch prompts, and output templates load when their phase executes.
- Content preserved verbatim — no behavior change, only progressive disclosure.

## Test plan
- [ ] CI passes
- [ ] `python3 scripts/validate-references.py --skill sapcc-audit` green
- [ ] Manual smoke: invoke sapcc-audit on a sample project

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
