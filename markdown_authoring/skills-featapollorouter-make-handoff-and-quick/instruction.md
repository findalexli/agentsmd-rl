# feat(apollo-router): make handoff and quick start skill-first

Source: [apollographql/skills#36](https://github.com/apollographql/skills/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/apollo-router/SKILL.md`

## What to add / change

This updates the `apollo-router` skill to prefer skill references over raw shell commands in the **Next Steps** handoff and **Quick Start** sections.

### Changes
- Handoff now points users to companion skills (`rover`, `apollo-server`, `graphql-schema`, `graphql-operations`) instead of copy-paste CLI commands
- Quick Start rewritten as a skill-oriented workflow with GraphOS-managed and local supergraph paths
- Added ground rules requiring skill-first guidance and command-free defaults

Raw CLI commands are still provided on request 👍

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
