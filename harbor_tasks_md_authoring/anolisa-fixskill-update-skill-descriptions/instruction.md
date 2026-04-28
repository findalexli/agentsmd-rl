# fix(skill): update skill descriptions

Source: [alibaba/anolisa#182](https://github.com/alibaba/anolisa/pull/182)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/os-skills/ai/install-claude-code/SKILL.md`
- `src/os-skills/ai/install-openclaw/SKILL.md`
- `src/os-skills/devops/kernel-dev/SKILL.md`
- `src/os-skills/system-admin/backup-restore/SKILL.md`
- `src/os-skills/system-admin/storage-resize/SKILL.md`

## What to add / change

## Description

更新部分skill的描述信息：适用于通用Linux系统

## Related Issue

closes #79 

## Type of Change

<!-- Check all that apply. -->

- [x] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional change)
- [ ] Performance improvement
- [ ] CI/CD or build changes

## Scope

<!-- Which sub-project does this PR affect? -->

- [ ] `cosh` (copilot-shell)
- [ ] `sec-core` (agent-sec-core)
- [x] `skill` (os-skills)
- [ ] `sight` (agentsight)
- [ ] Multiple / Project-wide

## Checklist

<!-- Check all that apply. -->

- [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
- [x] My code follows the project's code style
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have updated the documentation accordingly
- [ ] For `cosh`: Lint passes, type check passes, and tests pass
- [ ] For `sec-core` (Rust): `cargo clippy -- -D warnings` and `cargo fmt --check` pass
- [ ] For `sec-core` (Python): Ruff format and pytest pass
- [x] For `skill`: Skill directory structure is valid and shell scripts pass syntax check
- [ ] For `sight`: `cargo clippy -- -D warnings` and `cargo fmt --check` pass
- [ ] Lock files are up to date (`package-lock.json` / `Cargo.lock`)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
