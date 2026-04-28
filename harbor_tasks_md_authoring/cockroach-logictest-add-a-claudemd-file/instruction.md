# logictest: add a CLAUDE.md file

Source: [cockroachdb/cockroach#162102](https://github.com/cockroachdb/cockroach/pull/162102)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `pkg/sql/logictest/CLAUDE.md`

## What to add / change

This file provides guidance to Claude Code when working with logic tests. It covers running tests, test file syntax (statements, queries, variables, conditional execution), common configurations, CCL tests, mixed-version testing with cockroach-go-testserver, and iterative development workflows.

Epic: None
Release note: None

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
