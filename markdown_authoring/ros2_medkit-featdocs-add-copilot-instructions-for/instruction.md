# feat(docs): Add Copilot instructions for project context and guidelines

Source: [selfpatch/ros2_medkit#74](https://github.com/selfpatch/ros2_medkit/pull/74)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

# Pull Request

<!-- Thanks for contributing to ros2_medkit! -->

## Summary

- Define project architecture, tech stack (C++23, ROS 2 Jazzy), and domain model
- Outline build, test, and coverage workflows
- Establish code style, REST API patterns, and error handling strategies
- Add design principles (modularity, DI, thread safety) and code review guidelines
- Specify documentation maintenance and requirements traceability

---

## Issue

Link the related issue (required):

- closes #73 

---

## Type

- [ ] Bug fix
- [ ] New feature or tests
- [ ] Breaking change
- [x] Documentation only

---

## Testing

-

---

## Checklist

- [x] Breaking changes are clearly described (and announced in docs / changelog if needed)
- [x] Tests were added or updated if needed
- [x] Docs were updated if behavior or public API changed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
