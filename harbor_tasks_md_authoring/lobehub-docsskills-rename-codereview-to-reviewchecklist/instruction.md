# 📝 docs(skills): rename code-review to review-checklist

Source: [lobehub/lobehub#14229](https://github.com/lobehub/lobehub/pull/14229)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/review-checklist/SKILL.md`
- `AGENTS.md`

## What to add / change

#### 💻 Change Type

- [x] 📝 docs

#### 🔗 Related Issue

N/A

#### 🔀 Description of Change

Reposition the `code-review` skill as a recurring-mistakes checklist (not a generic review guide), and rename the directory + skill name accordingly.

- Drop the "Before You Start" prelude — `review-plus` already handles the scan-related reads.
- Drop the "Output Format" trailing block — describes a local-CLI flow no longer used.
- Collapse the redundant `## Checklist` wrapper and promote subsection headers from `###` to `##`.
- Add a `### Code Review` section in `AGENTS.md` pointing to the renamed skill.
- Correct the `pnpm i18n` note: it is slow and run manually before a PR, not auto-handled by CI.

#### 🧪 How to Test

- [x] No tests needed

#### 📝 Additional Information

A companion cloud-repo PR updates the matching symlink and adds a `cloud-review-checklist` skill (cloud-only i18n locale-key trap).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
