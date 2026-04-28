# docs: require following PR template in AGENTS.md

Source: [apache/opendal#7219](https://github.com/apache/opendal/pull/7219)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# Which issue does this PR close?

N/A.

# Rationale for this change

Our agent guidance did not explicitly require using OpenDAL's pull request template when creating PRs.
This change adds that requirement so future PR creation stays consistent with repository expectations.

# What changes are included in this PR?

- Add a new `Pull Request Requirements` section in `AGENTS.md`.
- Add one rule: always follow OpenDAL's pull request template when creating a PR.

# Are there any user-facing changes?

No.

# AI Usage Statement

This PR was prepared with Codex (GPT-5), with human review before submission.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
