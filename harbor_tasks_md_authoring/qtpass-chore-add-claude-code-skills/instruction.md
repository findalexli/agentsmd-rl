# chore: add Claude Code skills

Source: [IJHack/QtPass#1021](https://github.com/IJHack/QtPass/pull/1021)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/qtpass-docs/SKILL.md`
- `.claude/skills/qtpass-fixing/SKILL.md`
- `.claude/skills/qtpass-github/SKILL.md`
- `.claude/skills/qtpass-linting/SKILL.md`
- `.claude/skills/qtpass-localization/SKILL.md`
- `.claude/skills/qtpass-releasing/SKILL.md`
- `.claude/skills/qtpass-testing/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
Added a suite of new "skills" for the QtPass project, designed to provide comprehensive guidance and best practices across various development and maintenance workflows.

These new skills cover:
- **Documentation (`qtpass-docs`):** Guidelines for managing and updating project documentation, including README, FAQ, CHANGELOG, API documentation, and linting.
- **Bug Fixing (`qtpass-fixing`):** A structured workflow for investigating, reproducing, fixing, testing, and submitting bug fixes, along with common fix patterns and handling static analysis findings.
- **GitHub Interaction (`qtpass-github`):** Instructions for interacting with GitHub, covering PR creation, branch management, merging, commenting, and debugging CI failures.
- **Linting and CI (`qtpass-linting`):** A guide to the CI/CD workflow, emphasizing local GitHub Actions execution with `act`, and detailing the use of various linters and formatters (e.g., Gitleaks, Clang Format, Prettier).
- **Localization (`qtpass-localization`):** A workflow for managing QtPass translations, including updating existing `.ts` files, adding new languages, and addressing common localization issues.
- **Releasing (`qtpass-releasing`):** A step-by-step checklist for the release process, covering version bumping, changelog updates, artifact building, Git tagging, and GitHub releases.
- **Testing (`qtpass-testing`):** A comprehensive guide to unit testing with the Qt Test framework, including test structure, b

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
