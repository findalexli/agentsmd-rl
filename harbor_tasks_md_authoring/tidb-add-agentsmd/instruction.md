# *: add AGENTS.md

Source: [pingcap/tidb#66021](https://github.com/pingcap/tidb/pull/66021)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--

Thank you for contributing to TiDB!

PR Title Format:
1. pkg [, pkg2, pkg3]: what's changed
2. *: what's changed

-->

### What problem does this PR solve?
<!--

Please create an issue first to describe the problem.

There MUST be one line starting with "Issue Number:  " and
linking the relevant issues via the "close" or "ref".

For more info, check https://pingcap.github.io/tidb-dev-guide/contribute-to-tidb/contribute-code.html#referring-to-an-issue.

-->

Issue Number: ref #65936 ref #18023

Problem Summary:

- The feature branch `feature/release-8.5-materialized-view` does not have a repo-level `AGENTS.md`, which makes it easy for agents/automation to miss repository conventions (e.g. `make bazel_prepare`, license headers) and introduce avoidable CI failures.


### What changed and how does it work?

- Sync `AGENTS.md` from `upstream/master` into `feature/release-8.5-materialized-view`.


### Check List

Tests <!-- At least one of them must be included. -->

- [ ] Unit test
- [ ] Integration test
- [ ] Manual test (add detailed scripts or steps below)
- [x] No need to test
  > - [x] I checked and no code files have been changed.


Side effects

- [ ] Performance regression: Consumes more CPU
- [ ] Performance regression: Consumes more Memory
- [ ] Breaking backward compatibility

Documentation

- [ ] Affects user behaviors
- [ ] Contains syntax changes
- [ ] Contains variable changes
- [ ] Contains experimental features
- [ ] Changes MySQL compatibility

### Release 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
