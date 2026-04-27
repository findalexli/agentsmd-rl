# chore: broaden find-docs skill description to cover all developer technologies

Source: [upstash/context7#2224](https://github.com/upstash/context7/pull/2224)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/find-docs/SKILL.md`

## What to add / change

## Summary
- Expanded the `find-docs` skill description from "programming library or framework" to "any developer technology" (libraries, frameworks, languages, SDKs, APIs, CLI tools, cloud services, infrastructure tools, platforms)
- Added explicit common trigger scenarios (API lookups, CLI commands, "how do I" questions, debugging, migration guides, version-specific behavior) to improve auto-invocation matching
- Added catch-all trigger: "whenever documentation accuracy matters or when model knowledge may be outdated"

## Test plan
- [ ] Verify the skill triggers for library/framework queries (existing behavior)
- [ ] Verify the skill now triggers for CLI tool, cloud service, and platform queries
- [ ] Verify the skill triggers for general "how do I" technical questions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
