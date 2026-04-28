# [codex] docs(skills): standardize officecli install guidance

Source: [iOfficeAI/OfficeCLI#51](https://github.com/iOfficeAI/OfficeCLI/pull/51)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`
- `skills/morph-ppt/SKILL.md`
- `skills/morph-ppt/reference/officecli-pptx-min.md`
- `skills/officecli-academic-paper/SKILL.md`
- `skills/officecli-data-dashboard/SKILL.md`
- `skills/officecli-docx/SKILL.md`
- `skills/officecli-financial-model/SKILL.md`
- `skills/officecli-pitch-deck/SKILL.md`
- `skills/officecli-pptx/SKILL.md`
- `skills/officecli-xlsx/SKILL.md`

## What to add / change

This PR standardizes the OfficeCLI skill installation guidance in the root skill and the specialized skill docs under `skills/`.

Before this change, the skill docs used a mix of installation and manual version-check logic. Some docs compared the local version against GitHub releases and instructed agents to upgrade before use, while other docs used a single shell snippet that was not a correct native path for Windows users. That inconsistency made the install flow noisy and, in practice, easier to get wrong.

The root cause was duplicated install guidance spread across multiple skill documents. As the wording drifted, the docs picked up per-task upgrade checks even though `officecli` already performs its own background update checks during normal use. The duplicated snippets also mixed bootstrap and verification into a single flow, which could fail immediately after first install because the current shell session might not have refreshed `PATH` yet.

This change replaces those duplicated sections with a single simpler pattern:
- the root `SKILL.md` now presents `install if needed` guidance instead of install-plus-upgrade language
- macOS and Linux use the official `install.sh` bootstrap script
- Windows uses the official PowerShell `install.ps1` bootstrap script
- verification is split into a separate `officecli --version` step
- the docs now tell users to open a new terminal and rerun the verify step if `officecli` is still not found after the first install
- the `morph-ppt

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
