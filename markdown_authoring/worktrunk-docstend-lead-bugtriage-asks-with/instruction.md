# docs(tend): lead bug-triage asks with `wt -vv` diagnostic

Source: [max-sixty/worktrunk#2415](https://github.com/max-sixty/worktrunk/pull/2415)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/running-tend/SKILL.md`

## What to add / change

## Summary

Per maintainer feedback in [#2410](https://github.com/max-sixty/worktrunk/issues/2410#issuecomment-4318490230), reframe the Issue Triage section so the **primary ask is `wt -vv <command>`**. The diagnostic report covers wt/git/OS versions, shell integration, `wt config show`, `git worktree list --porcelain`, and a full git trace in one file, plus a `gh gist create --web …` hint, so a single gist URL replaces what was previously chained across multiple round-trips. `wt --version` and `wt config show` remain as narrower asks for the cases where the full diagnostic is overkill.

## Test plan

- [ ] Maintainer confirms framing matches the intent in [#2410](https://github.com/max-sixty/worktrunk/issues/2410#issuecomment-4318490230).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
