# docs(release): integrate cargo-semver-checks into release workflow

Source: [max-sixty/worktrunk#2235](https://github.com/max-sixty/worktrunk/pull/2235)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/release/SKILL.md`

## What to add / change

Now that worktrunk has a downstream library consumer, the release workflow should verify library API compatibility before the version bump is chosen.

Adds a new step 4 that runs `cargo semver-checks check-release -p worktrunk` before deciding the release type. Renumbers the subsequent steps. Adds a "Library API Compatibility" section explaining what the output means and when each bump level is required (pre-1.0: breaking changes require at least a minor bump).

The check complements — doesn't replace — the existing commit review. It validates the chosen bump is non-breaking; the commit review still decides patch vs. minor when no breakage exists.

> _This was written by Claude Code on behalf of @max-sixty_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
