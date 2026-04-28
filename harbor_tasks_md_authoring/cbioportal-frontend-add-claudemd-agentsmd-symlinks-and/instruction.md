# Add CLAUDE.md / AGENTS.md symlinks and document screenshot-artifact workflow

Source: [cBioPortal/cbioportal-frontend#5516](https://github.com/cBioPortal/cbioportal-frontend/pull/5516)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Symlink `CLAUDE.md` and `AGENTS.md` at the repo root to the existing `.github/copilot-instructions.md` so AI coding tools looking for either conventional filename pick up the same guidance (no content duplication to keep in sync).
- Add a new subsection to the Screenshot Testing docs describing the shortcut of pulling the "actual" screenshot from a failing CircleCI job's artifacts when an upstream data source (Genome Nexus, OncoKB, backend) changes. This is much faster than regenerating references locally and guaranteed to match the dockerized CI environment. PR #5514 (CCDS ID fix) is cited as a reference example.

Documentation-only change — no runtime effect, no deploy preview needed.

## Test plan

- [x] `CLAUDE.md` and `AGENTS.md` resolve to `.github/copilot-instructions.md` via symlink
- [x] Screenshot-artifact subsection renders correctly in the markdown

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
