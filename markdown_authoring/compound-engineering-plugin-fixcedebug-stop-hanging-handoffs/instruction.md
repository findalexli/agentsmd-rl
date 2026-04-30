# fix(ce-debug): stop hanging handoffs and read full issue thread

Source: [EveryInc/compound-engineering-plugin#646](https://github.com/EveryInc/compound-engineering-plugin/pull/646)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-debug/SKILL.md`

## What to add / change

## Summary

After this change, `ce-debug` does not leave users hanging after a bug fix, reads the full issue thread including the latest comments before investigating, and its option menus no longer offer Proof for cases that do not benefit from iterative doc review. The three fixes address related failure modes of the same skill drifting past its control points: missing context upfront, hanging mid-flow, and trailing off at the end.

## What changed

- **Phase 4 (renamed `Close` to `Handoff`):** the weak parenthetical rule is replaced with an imperative that forbids passive closers like "ready when you are". Phase 4 now splits into two paths: summary only after "Diagnosis only" in Phase 2, summary plus a blocking-question prompt after Phase 3. The menu drops `Done` and `Open in Proof`, leaving only real next actions: commit, document as a learning, post findings to the issue.
- **Phase 2:** the `View in Proof` option is replaced with `Diagnosis only, I'll take it from here`, giving stop-early first-class standing. The firm "Never silently skip the question" rule is anchored directly at the menu-rendering site instead of buried in a "Then offer next steps" prose line that was easy to drift past.
- **Phase 0:** the instruction to read issue input is rewritten to require reading the full thread with particular attention to the latest comments. The `gh issue view` call already fetched comments; the skill just was not telling the agent to use them, which sent investigations down 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
