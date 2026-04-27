# Use of Require Components instead of Bundles

Source: [sickn33/antigravity-awesome-skills#132](https://github.com/sickn33/antigravity-awesome-skills/pull/132)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bevy-ecs-expert/SKILL.md`

## What to add / change

Skill name : bevy-ecs-expert
Type of Change : Documentation Update

It's best practice since 0.15 to use `Require Components` instead of `Bundles`. Required Components are cached on the archetype graph, meaning computing what required components are necessary for a given type of insert only happens once.

Source : https://bevy.org/news/bevy-0-15/#required-components

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
