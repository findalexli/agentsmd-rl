# Alerting: Add gh in CLAUDE.md

Source: [grafana/grafana#114992](https://github.com/grafana/grafana/pull/114992)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `public/app/features/alerting/unified/CLAUDE.md`

## What to add / change

**What is this feature?**

Adds a `gh` usage guideline to CLAUDE.md, instructing Claude to use the GitHub CLI when retrieving information from GitHub.

**Why do we need this feature?**

**Who is this feature for?**

Devs in alerting (actually Claude ) 


Please check that:
- [ ] It works as expected from a user's perspective.
- [ ] If this is a pre-GA feature, it is behind a feature toggle.
- [ ] The docs are updated, and if this is a [notable improvement](https://grafana.com/docs/writers-toolkit/contribute/release-notes/#how-to-determine-if-content-belongs-in-whats-new), it's added to our [What's New](https://grafana.com/docs/writers-toolkit/contribute/release-notes/) doc.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
