# Add Next Step to every skill for sprint chaining

Source: [garagon/nanostack#13](https://github.com/garagon/nanostack/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

Each skill now tells the agent what comes next in the sprint:

- `/think` prompts for `/nano-plan`
- `/nano-plan` prompts for `/review`, `/qa`, `/security` after build
- `/review`, `/qa`, `/security` show remaining steps and prompt for `/ship`
- `/ship` closes the sprint (already generates journal)

No skill auto-executes the next one. They prompt the user to invoke it.

## Context

Real testing showed the agent completing the build after `/nano-plan` and stopping. No review, no QA, no security, no ship. The sprint flow broke because nothing told the agent what comes next.

## Test plan

- [ ] Run `/think` and verify it ends with "Ready for /nano-plan"
- [ ] Run `/nano-plan`, build, verify it ends with next steps list
- [ ] Run `/review` and verify it shows remaining sprint steps

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
