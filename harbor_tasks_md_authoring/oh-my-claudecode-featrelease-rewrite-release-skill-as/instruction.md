# feat(release): rewrite release skill as generic repo-aware assistant

Source: [Yeachan-Heo/oh-my-claudecode#2501](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/2501)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/AGENTS.md`
- `skills/release/SKILL.md`

## What to add / change

## Summary

- Replaces the hardcoded oh-my-claudecode release checklist with a repo-agnostic skill that introspects the project and CI on first run
- Caches derived rules in `.omc/RELEASE_RULE.md`; subsequent runs do a delta-check on CI workflow files instead of full re-analysis
- Adds `--refresh` flag to force re-analysis at any time

## What the new skill does

1. **Cache check** — reads `.omc/RELEASE_RULE.md` if it exists, re-analyzes only changed workflow files
2. **Repo analysis** — detects version source files, registry (npm/PyPI/Cargo/Docker), release trigger, test gate, changelog convention, first-time setup gaps
3. **Writes `.omc/RELEASE_RULE.md`** — timestamped, structured cache of all discovered rules
4. **Version selection** — prompts if not provided, shows semver bump preview
5. **Pre-release checklist** — derived from discovered rules, not hardcoded
6. **Release notes guidance** — best-practice guidelines + auto-draft from `git log` by conventional commit type
7. **Execution** — bump → test → commit → annotated tag → push → CI handoff or manual publish
8. **First-time user onboarding** — offers to scaffold a release workflow, explains git tags, flags unignored build artifacts
9. **Verification** — checks CI status and registry publish via `gh` CLI

## Test plan

- [ ] Run `/oh-my-claudecode:release` in a fresh repo with no `.omc/RELEASE_RULE.md` — verify analysis runs and file is created
- [ ] Run again without `--refresh` — verify only delta-check runs, not ful

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
