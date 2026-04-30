# docs: add two-phase interaction workflow to issue-reply skill

Source: [ant-design/ant-design#57236](https://github.com/ant-design/ant-design/pull/57236)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/issue-reply/SKILL.md`

## What to add / change

### 🤔 This is a ...

- [x] 📝 Site / documentation improvement

### 🔗 Related Issues

N/A

### 💡 Background and Solution

Add a "two-phase interaction workflow" section to the issue-reply Claude skill:

- **Phase 1**: Fetch issues, draft complete handling plans (classification, reply content, label changes) and present to maintainer for review
- **Phase 2**: Discuss and refine plans with maintainer, then execute after confirmation

This ensures no issue replies or closures happen without maintainer approval.

### 📝 Change Log

| Language   | Changelog |
| ---------- | --------- |
| 🇺🇸 English | N/A |
| 🇨🇳 Chinese | N/A |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
