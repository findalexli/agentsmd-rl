# Added copilot instructions file

Source: [chef/chef-server#4092](https://github.com/chef/chef-server/pull/4092)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

### Description

[Please describe what this change achieves]
Added copilot instructions file
### Issues Resolved

[List any existing issues this PR resolves, or any Discourse or
StackOverflow discussions that are relevant]

### Check List

- [ ] New functionality includes tests
- [ ] All buildkite tests pass
- [ ] Full omnibus build and tests in buildkite pass
- [ ] All commits have been signed-off for the Developer Certificate of Origin. See <https://github.com/chef/chef/blob/main/CONTRIBUTING.md#developer-certification-of-origin-dco>
- [ ] PR title is a worthy inclusion in the CHANGELOG

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
