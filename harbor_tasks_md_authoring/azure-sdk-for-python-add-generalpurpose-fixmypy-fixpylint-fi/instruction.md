# Add general-purpose fix-mypy, fix-pylint, fix-sphinx, and fix-black Copilot skills

Source: [Azure/azure-sdk-for-python#45809](https://github.com/Azure/azure-sdk-for-python/pull/45809)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/fix-black/SKILL.md`
- `.github/skills/fix-mypy/SKILL.md`
- `.github/skills/fix-pylint/SKILL.md`
- `.github/skills/fix-sphinx/SKILL.md`

## What to add / change

The existing Copilot skills for mypy and pylint were scoped exclusively to `azure-ai-ml` and used `tox`. This adds fourgeneral-purpose equivalents that work across any package in the repo and use `python -m azpysdk` tooling.

## New skills

- **`.github/skills/fix-mypy/SKILL.md`** — fixes mypy type errors in any package; trigger: `fix mypy issue <url> [in <pkg-path>] [using venv <path>]`
- **`.github/skills/fix-pylint/SKILL.md`** — fixes pylint warnings in any package; trigger: `fix pylint issue <url> [in <pkg-path>] [using venv <path>]`
- **`.github/skills/fix-black/SKILL.md`** — new skill for auto-formatting with black; trigger: `fix black issues`
- fix-sphinx/SKILL.md

## Key differences from `ml/` skills

| | ML skills | New skills |
|---|---|---|
| Scope | `azure-ai-ml` only | Any package path |
| Runner | `tox -e {check} --c .../tox.ini --root .` | `azpysdk {check} --isolate {package_path}` |
| Package prompt | Hardcoded | Prompts user if not provided |

All three skills except black prompt `"Please provide the package path (e.g. sdk/storage/azure-storage-blob)."` when no path is given, and follow the same step-by-step structure (activate venv → install deps → run check → fix → verify → open PR).

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>


## Overview

Create three new general-purpose Copilot skills under `.github/skills/` that work for **any** Azure SDK for Python package (not just `azure-ai-m

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
