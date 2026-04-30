# Fix description formatting error in SKILL.md

Source: [AvdLee/Swift-Concurrency-Agent-Skill#2](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `swift-concurrency/SKILL.md`

## What to add / change

error on opencode after installing this skill. it shows as well on github preview

<img width="1452" height="377" alt="image" src="https://github.com/user-attachments/assets/71b0ae81-a781-496a-8559-eda70830fa1c" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
