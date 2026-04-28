# Add .github/copilot-instructions.md for agent onboarding

Source: [go-debos/debos#604](https://github.com/go-debos/debos/pull/604)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Onboards repository to GitHub Copilot coding agent by adding comprehensive build, test, and architecture instructions to reduce exploration time and build failures.

## Key Content

**System Dependencies & Build Sequence**
- Critical system packages required: `libglib2.0-dev`, `libostree-dev`, `pkg-config`
- Complete build sequence with mandatory ostree pre-build step (`go build github.com/sjoerdsimons/ostree-go/pkg/otbuiltin`) before main build
- Linting setup with golangci-lint v2.3.1

**Project Structure**
- Action-based architecture overview with lifecycle: Verify → PreMachine → Run → Cleanup → PostMachine
- Lifecycle differs when running with or without fakemachine (PreMachine vs PreNoMachine)
- Directory layout: `cmd/debos/` (entry point), `actions/` (15+ action implementations), `tests/` (integration recipes), `docker/` (container builds)
- CI/CD pipeline breakdown: 6 jobs (golangci, test matrix, build, unit-tests, recipe-tests, example-recipes)

**Testing & Validation**
- Unit tests for complex subroutines, integration tests for action behavior
- Requirement to run relevant integration tests before submitting changes, especially for modified actions
- Docker command examples for running integration tests locally
- 8-step validation checklist including integration test requirements
- New features must be exercised in integration tests

**Common Issues & Documentation**
- Pre-building ostree prevents intermittent CGO build failures
- Existing TODOs/HACKs explicitly docu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
