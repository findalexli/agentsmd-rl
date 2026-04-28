# test: add cursor rules for extension E2E testing

Source: [MetaMask/metamask-extension#36509](https://github.com/MetaMask/metamask-extension/pull/36509)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `test/e2e/.cursor/rules/e2e-testing-guidelines.mdc`

## What to add / change

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been completely filled out, and PR status checks have passed at least once.
-->

## **Description**

Adds cursor rules for extension E2E Testing

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/36509?quickstart=1)

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

If this PR is End-User-Facing, please write a short User-Facing description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and accurately)
-->

CHANGELOG entry: null

## **Related issues**

Fixes:

## **Manual testing steps**
Pull the branch and see if rules are applied

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask Extension Coding Standards](https://

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
