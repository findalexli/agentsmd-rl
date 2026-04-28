# Add agents.md onboarding guide for coding agents

Source: [microsoft/DiskANN#765](https://github.com/microsoft/DiskANN/pull/765)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agents.md`

## What to add / change

- [x] Address review feedback on agents.md
- [x] Remove duplicated facts - provide links to source files instead
- [x] Remove sections: Build System, Configuration Files, Critical Patterns & Conventions, Common Workflows, Troubleshooting, Quick Reference, Errors Encountered
- [x] Simplify CI/CD Pipeline to just a link
- [x] Simplify code coverage to mention requirement and link to .codecov.yml
- [x] Remove "Regenerating Baselines" subsection
- [x] Remove "Default Members" and "Important Directories" subsections
- [x] Keep DON'T section, remove DO section
- [x] Add notes about rustfmt/clippy not being installed by default
- [x] Remove papers reference (updating wiki with new architecture)
- [x] File reduced from 788 lines to 157 lines

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/microsoft/DiskANN/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documented%20in%20%5BBest%20practices%20for%20Copilot%20coding%20agent%20in%20your%20repository%5D%28https://gh.io/copilot-coding-agent-tips%29%2E%0A%0A%3COnboard%20this%20repo%3E&assignees=copilot) — coding agent works faster and does higher quality work when set up for your repo.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
