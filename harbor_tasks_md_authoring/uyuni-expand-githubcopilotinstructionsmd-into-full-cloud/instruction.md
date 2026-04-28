# Expand .github/copilot-instructions.md into full cloud agent onboarding

Source: [uyuni-project/uyuni#11795](https://github.com/uyuni-project/uyuni/pull/11795)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

The prior `.github/copilot-instructions.md` only carried code-review + Gherkin guidance. This rewrite turns it into a primary onboarding document for the Copilot cloud agent working in this polyglot monorepo.

### Contents added
- **Repo map** — per-directory stack/tooling breakdown (`java/`, `web/`, `python/`, `schema/`, `microservices/`, `testsuite/`, packaging dirs).
- **Ground rules** — no workflow edits, respect stack boundaries, no new Struts logic, PostgreSQL-only, no fixup merges, reuse existing frameworks.
- **Per-stack build/lint/test commands**, taken from the actual `.github/workflows/`:
  - Frontend: `npm --prefix web ci --ignore-scripts --save=false`, `lint:production`, `tsc`, Jest with `BABEL_ENV=test`.
  - Java microservices: exact `mvn ... install checkstyle:check` invocations for `uyuni-java-parent`, `uyuni-java-common`, `coco-attestation`.
  - Java main stack: Ant + Ivy via `java/manager-build.xml`, flagged as requiring the openSUSE Uyuni container (defer to CI).
  - Python: `pytest python/test/unit/`, `black`, `pylint`, `python/linting/lint.sh`.
  - Schema: PostgreSQL-only, migrations under `schema/`.
  - Testsuite: `bundle exec rubocop features/*`.
- **Guidance for un-runnable validations** — run everything locally-runnable, explicitly document deferrals, never relax CI.
- **Coding conventions** quick reference linking to `java/buildconf/checkstyle.xml`, `web/eslint.config.js`, `python/linting/pylintrc`, `testsuite/.rubocop.yml`.
- **PR expectations** — P

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
