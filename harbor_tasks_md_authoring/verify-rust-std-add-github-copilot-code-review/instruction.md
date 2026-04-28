# Add GitHub Copilot code review instructions

Source: [model-checking/verify-rust-std#581](https://github.com/model-checking/verify-rust-std/pull/581)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Add `.github/copilot-instructions.md` to guide GitHub Copilot's automated code reviews for this repository. This will help us triage the coming wave of challenge solutions.

The instructions cover review guidelines for the four types of PRs we receive:
- **Challenge solutions** — formal verification rigor (no vacuous proofs, justified assumptions, contracts matching safety docs), Rust std library code quality standards, and success criteria compliance.
- **New challenge proposals** — template and tracking issue requirements.
- **New tool applications** — CI workflow and book entry requirements.
- **Maintenance** — ensuring existing proofs are not weakened.

Also includes a list of common red flags to watch for (e.g., over-constrained assumptions, missing cfg gates, unapproved tools).

Reference: [Copilot code review custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
