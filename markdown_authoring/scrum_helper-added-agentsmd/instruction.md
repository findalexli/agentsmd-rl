# Added AGENTS.md

Source: [fossasia/scrum_helper#513](https://github.com/fossasia/scrum_helper/pull/513)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agents.md`

## What to add / change

### 📌 Fixes

Fixes #508 

---

### 📝 Summary of Changes
This PR introduces an AGENTS.md file to define best practices for AI-assisted contributions.


---

Added an AGENTS.md file with simple guidelines for AI-assisted contributions, as mentioned. It focuses on understanding the code, avoiding blind copy-paste, proper validation and aligning with the existing project to improve PR quality and reduce maintainer overhead.

---

### ✅ Checklist

- [ ] I’ve tested my changes locally
- [ ] I’ve added tests (if applicable)
- [x] I’ve updated documentation (if applicable)
- [x] My code follows the project’s code style guidelines

---

## Summary by Sourcery

Documentation:
- Document expectations and responsibilities for contributors using AI tools, including validation, architecture fit, and review practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
