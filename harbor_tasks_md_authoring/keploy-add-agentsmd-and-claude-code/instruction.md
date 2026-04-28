# Add AGENTS.md and Claude Code skills for agent-assisted contribution

Source: [keploy/keploy#4071](https://github.com/keploy/keploy/pull/4071)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/keploy-docs/SKILL.md`
- `.claude/skills/keploy-e2e-test/SKILL.md`
- `.claude/skills/keploy-pr-workflow/SKILL.md`
- `AGENTS.md`

## What to add / change

## Describe the changes that are made

- Add `AGENTS.md` at the repo root — a grounded reference for AI agents and new contributors covering project purpose, build/run/lint/test commands (including the required `viper_bind_struct` tag), the Linux/Windows/macOS platform-support matrix, key directories, and contribution conventions.
- Add `.claude/skills/keploy-docs/SKILL.md` — when and how to update the `keploy/docs` site (Docusaurus 2 layout, versioned docs, the CI checks, local repro).
- Add `.claude/skills/keploy-e2e-test/SKILL.md` — how to verify a change end-to-end using keploy's own record/replay against a real sample app, matching what CI already runs.
- Add `.claude/skills/keploy-pr-workflow/SKILL.md` — PR/issue conventions, customer-data hygiene rules, Conventional Commits + DCO sign-off, and destructive-git guardrails.

Pure documentation — no Go code, no configuration, no runtime or build behavior changes. Nothing in `cli/`, `pkg/`, `cmd/`, or any workflow under `.github/workflows/` is touched.

> ask claude to use the skill 

## Links & References

**Closes:** #4070

### 🔗 Related PRs
- NA

### 🐞 Related Issues
- #4070

### 📄 Related Documents
- [`CONTRIBUTING.md`](../blob/main/CONTRIBUTING.md)
- [`.github/CI_CONTRIBUTING.md`](../blob/main/.github/CI_CONTRIBUTING.md)
- [`.github/PULL_REQUEST_TEMPLATE.md`](../blob/main/.github/PULL_REQUEST_TEMPLATE.md)

## What type of PR is this? (check all applicable)
- [ ] 📦 Chore
- [ ] 🍕 Feature
- [ 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
