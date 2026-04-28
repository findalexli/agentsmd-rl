# Add Copilot instructions for Ghostwriter repository onboarding

Source: [GhostManager/Ghostwriter#734](https://github.com/GhostManager/Ghostwriter/pull/734)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to enable efficient agent operation by documenting build/test workflows, architecture, and common failure modes.

## Structure

**Repository Overview** - Tech stack (Django 4.2, Python 3.10, React/TypeScript, PostgreSQL 16.4, Hasura GraphQL, Docker Compose) and codebase composition (484 Python files, 76 JS/TS files)

**Environment Setup** - Installation via `ghostwriter-cli-linux install --dev` (5-10 min), includes critical warning about Alpine package mirror network requirements that cause failures in sandboxed environments

**Build/Test/Development**
- Live reload workflow (no rebuild for code changes, rebuild only for dependencies/Dockerfiles)
- Migration commands (always required after model changes)
- Test execution (~45-60s full suite) with `--exclude-tag=GitHub` flag
- Linting: Black (90 char), isort, flake8 (240 max), pylint-django for Python; Prettier + TypeScript strict for JS

**Project Structure** - Django app layout with sizes (`reporting/` 1.7MB, `rolodex/` 836KB, `shepherd/` 780KB, etc.), config organization, frontend in `javascript/`, Docker compose in `compose/`

**CI/CD** - GitHub Actions workflows (main CI runs tests + coverage upload in 5-10 min, CodeQL security scan), no pre-commit hooks

**Common Issues** - Container stuck after startup errors, Alpine install failures, missing migrations, static file loading

**Dependencies** - Key packages listed inline for quick reference

**Constraints** - 139 lines, ~800 words, 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
