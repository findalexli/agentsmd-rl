# Add Copilot cloud agent onboarding instructions

Source: [rr-wfm/MSBuild.Sdk.SqlProj#903](https://github.com/rr-wfm/MSBuild.Sdk.SqlProj/pull/903)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` with focused, repository-specific guidance for first-time Copilot cloud agent sessions.

## What this includes

- A concise map of repository purpose and layout.
- Clear pointers for where to make changes (SDK targets/props, DacpacTool CLI, templates).
- A CI-aligned validation sequence to run from the repo root.
- CI workflow alignment notes (`./.github/workflows/main.yml`).
- Coding/style expectations based on existing analyzer and `.editorconfig` rules.
- Practical tips to keep agent changes minimal and targeted.

## Follow-up adjustments from review

- Replaced CI-specific absolute paths with portable repository-relative paths.
- Removed the onboarding troubleshooting/errors section to keep the instructions focused on stable, evergreen guidance.

## Validation

- Updated instructions were revalidated with parallel review/security checks after feedback changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
