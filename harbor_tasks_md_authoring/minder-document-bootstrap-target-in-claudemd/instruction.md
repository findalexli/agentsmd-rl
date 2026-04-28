# Document bootstrap target in CLAUDE.md

Source: [mindersec/minder#5947](https://github.com/mindersec/minder/pull/5947)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
Adds comprehensive documentation for the `make bootstrap` target in CLAUDE.md. This target is essential for initial development environment setup but was not prominently documented in the Prerequisites or workflow sections.

## Changes
- **Reorganized Prerequisites section**: Clarified which tools are installed via `make bootstrap` vs. tools required beforehand (Go, Docker, OpenSSL)
- **Added "Initial Setup" section**: Provides clear step-by-step guidance that bootstrap should be run once after cloning to:
  - Install build tools (sqlc, protoc plugins, mockgen, yq, fga, helm-docs)
  - Initialize configuration files (config.yaml, server-config.yaml)
  - Generate encryption keys (.ssh/ directory)
- **Updated "Useful Make Targets"**: Added bootstrap to the quick reference list

## Motivation
New developers cloning the repository need to run `make bootstrap` before they can build or generate code, but this wasn't clearly documented. This change ensures developers have a smooth onboarding experience and understand the purpose of the bootstrap target.

## Test plan
- [x] Verified CLAUDE.md renders correctly
- [x] Confirmed all information about bootstrap target is accurate by reviewing `.mk/develop.mk`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
