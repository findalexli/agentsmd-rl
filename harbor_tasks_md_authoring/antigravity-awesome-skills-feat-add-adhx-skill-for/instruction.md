# feat: add adhx skill for X/Twitter post reading

Source: [sickn33/antigravity-awesome-skills#396](https://github.com/sickn33/antigravity-awesome-skills/pull/396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/adhx/SKILL.md`

## What to add / change

# Pull Request Description

Adds the **ADHX** community skill for fetching X/Twitter posts as clean LLM-friendly JSON.

ADHX (https://adhx.com) is an open-source Claude Code skill that converts any x.com, twitter.com, or adhx.com link into structured JSON data with full article content, author info, and engagement metrics. No scraping or browser required. Works with both regular tweets and long-form X Articles.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

- [x] **Standards**: Reviewed against the repository contributor standards and security guardrails.
- [x] **Metadata**: `SKILL.md` frontmatter is present and valid in the submitted file.
- [x] **Risk Label**: `risk: safe` is set.
- [x] **Triggers**: The "When to use" guidance is specific to the ADHX workflow.
- [x] **Security**: N/A (not an offensive skill).
- [x] **Safety scan**: No risky token-like examples beyond normal install usage; maintainer review requested via CI.
- [x] **Automated Skill Review**: Required for `SKILL.md` changes and expected to run after fork approval.
- [x] **Local Test**: Install and usage examples are present for local verification.
- [x] **Repo Checks**: Source-only PR; repository CI will validate the change.
- [x] **Source-Only PR**: No generated registry artifacts are included.
- [x] **Credits**: Source is attributed to https://github.com/itsmemeworks/adhx.
- [x] **Maintainer Edits**: Enabled.

## What This A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
