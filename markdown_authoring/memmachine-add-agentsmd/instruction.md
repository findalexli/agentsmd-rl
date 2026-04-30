# Add AGENTS.MD

Source: [MemMachine/MemMachine#814](https://github.com/MemMachine/MemMachine/pull/814)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.MD`

## What to add / change

### Purpose of the change

Add AGENTS.MD to help people who use AI IDE's to understand how to use the API's

### Description

Guide of how to use the REST API / Python SDK and how to make different curl requests

### Type of change

[Please delete options that are not relevant.]

- [ ] Documentation update


### Checklist

[Please delete options that are not relevant.]

- [ ] I have signed the commit(s) within this pull request
- [ ] My code follows the style guidelines of this project (See STYLE_GUIDE.md)
- [ ] I have performed a self-review of my own code
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have checked my code and corrected any misspellings

### Maintainer Checklist

- [ ] Confirmed all checks passed
- [ ] Contributor has signed the commit(s)
- [ ] Reviewed the code
- [ ] Run, Tested, and Verified the change(s) work as expected

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
