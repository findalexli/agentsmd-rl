# Add AGENTS.md

Source: [cytoscape/cytoscape.js#3445](https://github.com/cytoscape/cytoscape.js/pull/3445)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Ref: Add AGENTS.md #3441

**Cross-references to related issues.**  If there is no existing issue that describes your bug or feature request, then [create an issue](https://github.com/cytoscape/cytoscape.js/issues/new/choose) before making your pull request.

Associated issues: 

- #3441 

**Notes re. the content of the pull request.** Give context to reviewers or serve as a general record of the changes made.  Add a screenshot or video to demonstrate your new feature, if possible.

- Adds AGENTS.md for use by Codex, Claude, Copilot, etc.
- Doesn't change any API so may as well be included in a patch release.

**Checklist**

Author:

- [x] The proper base branch has been selected.  New features go on `unstable`.  Bug-fix patches can go on either `unstable` or `master`.
- [ ] N/A -- Automated tests have been included in this pull request, if possible, for the new feature(s) or bug fix.  Check this box if tests are not pragmatically possible (e.g. rendering features could include screenshots or videos instead of automated tests).
- [x] The associated GitHub issues are included (above).
- [x] Notes have been included (above).
- [x] For new or updated API, the `index.d.ts` Typescript definition file has been appropriately updated.

Reviewers:

- [ ] All automated checks are passing (green check next to latest commit).
- [ ] At least one reviewer has signed off on the pull request.
- [ ] For bug fixes:  Just after this pull request is merged, it should be

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
