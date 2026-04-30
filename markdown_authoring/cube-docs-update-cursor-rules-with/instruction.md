# docs: update cursor rules with product taxonomy and documentation gui…

Source: [cube-js/cube#10675](https://github.com/cube-js/cube/pull/10675)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/namings-rule.mdc`
- `.cursor/rules/writing-documentation.mdc`

## What to add / change

…dance

Add product taxonomy to naming conventions rule and set it to always apply for docs-mintlify files. Add new writing-documentation rule with guidance on researching the cloud product codebase and Mintlify best practices.

Made-with: Cursor

**Check List**
- [ ] Tests have been run in packages where changes have been made if available
- [ ] Linter has been run for changed code
- [ ] Tests for the changes have been added if not covered yet
- [ ] Docs have been added / updated if required

<!--

Please uncomment and fill the sections below if applicable. This will help the reviewer to get the context quicker.

**Issue Reference this PR resolves**

[For example #12]

**Description of Changes Made (if issue reference is not provided)**

[Description goes here]
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
