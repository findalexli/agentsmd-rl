# fix(factory): read accessToken from auth.json, not token

Source: [popmechanic/VibesOS#62](https://github.com/popmechanic/VibesOS/pull/62)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/factory/SKILL.md`

## What to add / change

## Summary

The factory skill's SKILL.md referenced \`~/.vibes/auth.json['token']\` in two places. That key doesn't exist — the CLI auth helper writes \`{ accessToken, refreshToken, idToken, expiresAt }\`. An agent following SKILL verbatim ended up with an empty \`TOKEN\` variable and every factory-worker call 401'd with \"Missing authorization\".

Both snippets now read \`accessToken\`. The pre-flight snippet also switched from grep-based extraction to the same python3 json.load parse the deploy snippet uses, for consistency.

## Caught by

Prod QA on 2026-04-20 while running the 3-command recovery for a tenant app whose token engine needed re-initializing. I worked around by hand-substituting \`accessToken\`, then followed up with this PR so the next agent run doesn't hit it.

## Test plan

- [x] \`grep -n \"'token'\" skills/factory/SKILL.md\` returns no matches.
- [ ] Running through the factory skill end-to-end with a live login cache produces a non-empty \`TOKEN\` and the configure/initialize curls succeed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
