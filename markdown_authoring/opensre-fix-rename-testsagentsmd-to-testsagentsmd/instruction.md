# fix: rename tests/AGENTS.MD to tests/AGENTS.md

Source: [Tracer-Cloud/opensre#979](https://github.com/Tracer-Cloud/opensre/pull/979)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `tests/AGENTS.md`

## What to add / change

Fixes #827

<!-- Add issue number above --> 

#### Describe the changes you have made in this PR -
The tests directory uses `AGENTS.MD` (uppercase extension) while the repo root uses `AGENTS.md`. Renamed for consistency.

## Code Understanding and AI Usage

**Did you use AI assistance (ChatGPT, Claude, Copilot, etc.) to write any part of this code?**
- [x] No, I wrote all the code myself
- [ ] Yes, I used AI assistance (continue below)



**Explain your implementation approach:**
- The tests directory had `AGENTS.MD` (uppercase extension) while the repo root uses `AGENTS.md`. Renamed the filename for consistency.



---

## Checklist before requesting a review
- [x] I have added proper PR title and linked to the issue
- [x] I have performed a self-review of my code
- [x] **I can explain the purpose of every function, class, and logic block I added**
- [x] I understand why my changes work and have tested them thoroughly
- [ ] I have considered potential edge cases and how my code handles them
- [ ] If it is a core feature, I have added thorough tests
- [x] My code follows the project's style guidelines and conventions

---

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
