# Add mise-configurator skill for local and CI/CD toolchain setup

Source: [sickn33/antigravity-awesome-skills#523](https://github.com/sickn33/antigravity-awesome-skills/pull/523)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/mise-configurator/SKILL.md`

## What to add / change

# Pull Request Description

## Summary

Adds a new `mise-configurator` skill to generate production-ready `mise.toml` setups for local development and CI/CD pipelines.

## Features

* Local development runtime setup
* CI/CD examples with mise
* Migration from asdf / nvm / pyenv
* Multi-language toolchain support
* Minimal token-efficient prompt design

## Why

Mise adoption is growing quickly and teams need automated reproducible runtime management.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

`Closes #N` or `Fixes #N`

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [ ] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [ ] **Triggers**: The "When to use" section is clear and specific.
- [x] **Limitations**: The skill includes a `## Limitations` (or equivalent accepted constraints) section.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Safety scan**: If this PR adds or modifies `SKILL.md` command guidance, remote/network examples,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
