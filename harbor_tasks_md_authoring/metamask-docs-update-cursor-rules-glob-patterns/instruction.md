# Update cursor rules glob patterns

Source: [MetaMask/metamask-docs#2878](https://github.com/MetaMask/metamask-docs/pull/2878)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/content-types.mdc`
- `.cursor/rules/editorial-voice.mdc`
- `.cursor/rules/markdown-formatting.mdc`
- `.cursor/rules/product-embedded-wallets.mdc`
- `.cursor/rules/product-metamask-connect.mdc`
- `.cursor/rules/product-services.mdc`
- `.cursor/rules/product-smart-accounts-kit.mdc`
- `.cursor/rules/product-snaps.mdc`
- `.cursor/rules/terminology.mdc`

## What to add / change

# Description

<!-- Describe the changes made in your pull request (PR). -->

Cursor appears not to be applying all rules properly, possibly because of bad glob patterns. This PR updates to proper syntax (seems to be confusing for many: https://forum.cursor.com/t/correct-way-to-specify-rules-globs/71752).

Before:
<img width="560" height="222" alt="Screenshot 2026-04-22 at 4 21 21 PM" src="https://github.com/user-attachments/assets/09c48242-ba6a-4718-8610-f25125759052" />

After:
<img width="424" height="216" alt="Screenshot 2026-04-22 at 4 21 28 PM" src="https://github.com/user-attachments/assets/a87540a9-955c-4c21-9002-a585d1f5f0fd" />


## Checklist

<!-- Complete the following checklist before merging your PR. -->

- [ ] If this PR updates or adds documentation content that changes or adds technical meaning, it has received an approval from an engineer or DevRel from the relevant team.
- [ ] If this PR updates or adds documentation content, it has received an approval from a technical writer.

## External contributor checklist

<!-- If you are an external contributor (outside of the MetaMask organization), complete the following checklist. -->

- [ ] I've read the [contribution guidelines](https://github.com/MetaMask/metamask-docs/blob/main/CONTRIBUTING.md).
- [ ] I've created a new issue (or assigned myself to an existing issue) describing what this PR addresses.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk since chang

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
