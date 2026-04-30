# fix: check action log before asking about user interactions

Source: [saffron-health/libretto#59](https://github.com/saffron-health/libretto/pull/59)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/libretto/SKILL.md`
- `packages/libretto/skill/SKILL.md`

## What to add / change

## Summary
- Instead of always asking the user a confusing question about incorporating manual browser interactions, the skill now checks `npx libretto actions --source user` first
- If there are recorded user interactions, it lists them and asks if the user wants them incorporated
- If there are none, it skips the question entirely

## Test plan
- [ ] Run a libretto session with no manual interactions → verify question #2 is skipped
- [ ] Run a libretto session with manual clicks/fills → verify the agent lists them and asks

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
