# Add comprehensive Copilot instructions for repository onboarding

Source: [jolars/moloch#58](https://github.com/jolars/moloch/pull/58)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Added `.github/copilot-instructions.md` to onboard coding agents to this LaTeX package repository, reducing exploration time and preventing build failures.

## Contents

**Environment & Build System**
- Nix flake requirement and `l3build-wrapped` command format
- All build/test/validation commands with expected execution times
- CTAN package generation process matching CI

**Repository Structure**
- `.dtx` documented source format and `.sty` generation
- Test file organization (`.lvt` inputs, `.tlg` expected outputs)
- Generated vs. source file distinction

**Development Workflows**
- Code change → test → CTAN build sequence
- Test update procedure (`l3build-wrapped save`)
- Conventional commits requirement for semantic-release

**CI/CD Pipeline**
- build-and-test.yml steps for local replication
- release.yml semantic versioning automation
- Version number sync locations (build.lua, doc/moloch.tex, src/*.dtx)

**Troubleshooting**
- Common Nix/l3build errors and solutions
- Test regeneration for intentional output changes

## Key Preventions

- Using system LaTeX tools instead of Nix environment
- Editing generated `.sty` files instead of `.dtx` sources
- Skipping CTAN build validation before PR submission
- Non-conventional commit messages breaking release automation

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

Your task is to "onboard" this repository to Copilot coding agent by adding a .github/copilot-instructions.md file in 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
