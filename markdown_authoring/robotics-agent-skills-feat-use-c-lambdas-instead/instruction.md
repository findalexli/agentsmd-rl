# feat: use c++ lambdas instead of std::bind

Source: [arpitg1304/robotics-agent-skills#1](https://github.com/arpitg1304/robotics-agent-skills/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ros2/SKILL.md`

## What to add / change

Make the C++ patterns compilable and use C++ lambdas instead of std::bind.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
