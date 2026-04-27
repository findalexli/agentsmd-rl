# refactor: rewrite amq-cli v1.9.0 and amq-spec v1.3.0 skills

Source: [avivsinai/agent-message-queue#51](https://github.com/avivsinai/agent-message-queue/pull/51)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/amq-cli/SKILL.md`
- `skills/amq-spec/SKILL.md`

## What to add / change

## Summary
- Rewrites both AMQ skills based on eval pipeline findings (12 parallel with/without-skill agent runs, graded by Codex as impartial judge)
- **amq-cli v1.9.0**: Natural description, explain-why environment rules, cleaner task routing
- **amq-spec v1.3.0**: Natural description, reasoning-based Protocol Discipline (replacing 7x NEVER/ALWAYS rules), research-independence check, /amq-spec naming fix, explicit user-approval gate

## Eval Results (corrected per Codex review)
| Skill | Accuracy | Tokens | Time |
|-------|----------|--------|------|
| amq-cli | +7% vs baseline | -11% | -42% |
| amq-spec | +39% vs baseline | -26% | -46% |

## Test plan
- [x] Pre-push hook passed (vet, lint, test, smoke)
- [x] 12 eval runs graded (6 per skill, with/without)
- [x] Codex impartial review of methodology + corrections applied
- [x] Codex final sign-off on rewritten skills
- [x] Skills synced across all locations

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
