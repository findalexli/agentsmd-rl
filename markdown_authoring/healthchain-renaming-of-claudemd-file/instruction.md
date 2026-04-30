# renaming of claude.md file

Source: [healthchainai/HealthChain#176](https://github.com/healthchainai/HealthChain/pull/176)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description
Renamed the claude md file to have a lower case md as it needed for Claude Code


Closes #

## Type of Change
- [x] 🐛 Bug fix (non-breaking)
- [ ] ✨ New feature (non-breaking)
- [ ] 💥 Breaking change
- [ ] 📚 Documentation
- [ ] 🧪 Tests only
- [ ] 🔴 Core change (requires RFC)


## Testing
Test locally with Claude code

- [x] `uv run pytest` passes locally and generates no additional warnings or errors.
- [x] Added / updated tests to cover the changes.
- [x] Manually tested (describe how)


## Checklist
- [x] I have read [`CONTRIBUTING.md`](https://github.com/dotimplement/HealthChain/blob/main/CONTRIBUTING.md) and followed the guidelines.
- [x] I have linked all relevant Issues / Discussions / RFCs.
- [x] I have updated documentation where needed.
- [x] I understand all code changes and can explain the design decisions and trade-offs.
- [x] I am available to respond to review feedback.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
