# Add .github/copilot-instructions.md with PR review guidelines

Source: [go-git/go-git#2040](https://github.com/go-git/go-git/pull/2040)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds Copilot review instructions to guide automated PR reviews toward high-signal feedback aligned with the project's quality bar.

## What's included

- **Review priorities** — bias toward correctness, security, compatibility, and maintainability over style nits
- **Tests** — prefer table-driven tests; flag bloat and missing edge/failure coverage
- **Git compatibility** — require behavior to be verified against `git/git`, not assumed
- **Repository contents** — flag large files, binaries, and files added then removed within the same PR
- **Go APIs** — flag non-idiomatic naming, unnecessary abstractions, missing docs on exported symbols
- **Encoding/decoding** — require fuzz tests for any new encode/decode paths handling external input

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
