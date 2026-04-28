# Update nav-loop SKILL.md with v2 exit signal format

Source: [alekspetrov/navigator#4](https://github.com/alekspetrov/navigator/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/nav-loop/SKILL.md`

## What to add / change

## Summary

Automated PR created by Pilot for task GH-2.

Closes #2

## Changes

GitHub Issue #2: Update nav-loop SKILL.md with v2 exit signal format

## Summary
Update nav-loop skill documentation to use JSON-based exit signals for reliable Pilot detection.

## Changes
Update `skills/nav-loop/SKILL.md` Step 7 (Complete Loop) to emit exit signal as JSON:

```
```pilot-signal
{"v":2,"type":"exit","success":true,"reason":"All criteria met"}
```
```

Also update the "Setting EXIT_SIGNAL" section to show the new format.

## Why
- Text-based `EXIT_SIGNAL: true` can false-match in prose
- JSON in code blocks is unambiguous
- Matches status signal format for consistency

## Acceptance Criteria
- [ ] SKILL.md Step 7 shows JSON exit signal format
- [ ] "Setting EXIT_SIGNAL" section updated
- [ ] Examples updated to use new format

## Related
- Depends on #1 (status_generator.py changes)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
