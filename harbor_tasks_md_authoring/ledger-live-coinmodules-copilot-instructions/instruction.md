# coin-modules copilot instructions

Source: [LedgerHQ/ledger-live#15946](https://github.com/LedgerHQ/ledger-live/pull/15946)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

<!--
Thank you for your contribution! 👍
Please make sure to read CONTRIBUTING.md if you have not already. Pull Requests that do not comply with the rules will be arbitrarily closed.
-->

### ✅ Checklist

<!-- Pull Requests must pass the CI and be code reviewed. Set as Draft if the PR is not ready. -->

- [ ] `npx changeset` was attached.
- [ ] **Covered by automatic tests.** <!-- if not, please explain. (Feature must be tested / Bug fix must bring non-regression) -->
- [x] **Impact of the changes:** <!-- Please take some time to list the impact & what specific areas Quality Assurance (QA) should focus on -->
  - co-pilot instructions

### 📝 Description

Coin-module specific co-pilot instructions, adding:
- architecture
- test requirements

Will be backported to other repository with alpaca specific only.

<!--
| Before        | After         |
| ------------- | ------------- |
|               |               |
-->

### ❓ Context

- **JIRA or GitHub link**: https://ledgerhq.atlassian.net/browse/LIVE-26361
- **ADR link (if any)**: <!-- Attach the relevant architectural decision record if applicable. -->


---

### 🧐 Checklist for the PR Reviewers

<!-- Please do not edit this if you are the PR author -->

- **The code aligns with the requirements** described in the linked JIRA or GitHub issue.
- **The PR description clearly documents the changes** made and explains any technical trade-offs or design decisions.
- **There are no undocumen

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
