# feat: add nosql-expert skill for distributed database patterns

Source: [sickn33/antigravity-awesome-skills#23](https://github.com/sickn33/antigravity-awesome-skills/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/nosql-expert/SKILL.md`

## What to add / change

## Description

Adds a new **`nosql-expert`** skill focused on the architectural patterns of distributed databases (Cassandra, DynamoDB).

**Why this skill is valuable:**
This skill focuses on the **underlying system design**:
- "Query-First" mental models and Access Pattern modeling.
- Handling partition keys and avoiding Hot Partitions.
- Advanced patterns like Single-Table Design and Denormalization strategies.

This fills the gap for "NoSQL System Design" knowledge in the repository, helping agents design schemas *before* implementation.

## Checklist

- [x] My skill follows the [creation guidelines](https://github.com/sickn33/antigravity-awesome-skills/tree/main/skills/skill-creator)
- [x] I have run [validate_skills.py](cci:7://file:///c:/Users/ian/Desktop/PROJECT/antigravity-awesome-skills/scripts/validate_skills.py:0:0-0:0)

## Type of Change

- [x] New Skill

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
