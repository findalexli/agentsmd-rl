# Add official Qodo skills

Source: [qwibitai/nanoclaw#428](https://github.com/qwibitai/nanoclaw/pull/428)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/get-qodo-rules/SKILL.md`
- `.claude/skills/get-qodo-rules/references/output-format.md`
- `.claude/skills/get-qodo-rules/references/pagination.md`
- `.claude/skills/get-qodo-rules/references/repository-scope.md`
- `.claude/skills/qodo-pr-resolver/SKILL.md`
- `.claude/skills/qodo-pr-resolver/resources/providers.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Adds `/qodo-pr-resolver` — official Qodo skill for fetching and fixing PR review issues interactively or in batch (GitHub, GitLab, Bitbucket, Azure DevOps)
- Adds `/qodo-get-rules` — official Qodo skill for loading org/repo-level coding rules before code tasks

Skills only — no source code changes. Both skills match `qodo-skills@0.3.0` from `claude-plugins-official`.

## Files

| File | Lines | Source |
|------|-------|--------|
| `.claude/skills/qodo-pr-resolver/SKILL.md` | 326 | Official `qodo-ai/qodo-skills` |
| `.claude/skills/qodo-pr-resolver/resources/providers.md` | 329 | Official — GitHub/GitLab/Bitbucket/Azure commands |
| `.claude/skills/qodo-get-rules/SKILL.md` | 122 | Official `qodo-ai/qodo-skills` |
| `.claude/skills/qodo-get-rules/references/output-format.md` | 41 | Official — rules output format |
| `.claude/skills/qodo-get-rules/references/pagination.md` | 33 | Official — API pagination |
| `.claude/skills/qodo-get-rules/references/repository-scope.md` | 26 | Official — scope detection |
| `CLAUDE.md` | +2 | Skills table updated |

## Test plan

- [ ] Run `/qodo-get-rules` without `~/.qodo/config.json` — should exit gracefully with setup instructions
- [ ] Run `/qodo-pr-resolver` on a branch with no open PR — should inform and offer to create one

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
