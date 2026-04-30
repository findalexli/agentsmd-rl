# docs: update copilot instructions

Source: [joshjohanning/github-misc-scripts#131](https://github.com/joshjohanning/github-misc-scripts/pull/131)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

**Script guidelines and best practices:**

* Expanded requirements for scripts in both `gh-cli` and `scripts` directories, including input validation, meaningful error messages, use of pagination, preference for `--jq` in `gh api` commands, inclusion of specific GraphQL headers, and folder organization for complex scripts.
* Added instructions to keep descriptions concise, avoid periods in bullet points, and updated section headings for clarity.
* Added requirement to support custom hostnames for GitHub Enterprise instances in scripts when relevant.

**Commit message guidelines:**

* Introduced a new section detailing the Conventional Commits specification, including recommended types, scopes, formatting, and how to indicate breaking changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
