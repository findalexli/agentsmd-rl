# refactor(skills): rename and expand Java backend patterns to Spring Boot

Source: [TheSoftwareHouse/copilot-collections#56](https://github.com/TheSoftwareHouse/copilot-collections/pull/56)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/tsh-implementing-backend/SKILL.md`
- `.github/skills/tsh-implementing-backend/references/java-patterns.md`
- `.github/skills/tsh-implementing-backend/references/java-spring-boot-patterns.md`

## What to add / change

- move reference to
- add async messaging patterns for Spring Cloud Stream
- document native compilation workflow with GraalVM

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
