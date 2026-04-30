# docs: add AGENT.md with AI coding agent guidance

Source: [openfga/openfga#2905](https://github.com/openfga/openfga/pull/2905)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- Thanks for opening a PR! Here are some quick tips:
If this is your first time contributing, [read our Contributing Guidelines](https://github.com/openfga/.github/blob/main/CONTRIBUTING.md) to learn how to create an acceptable PR for this repo.
By submitting a PR to this repository, you agree to the terms within the [OpenFGA Code of Conduct](https://github.com/openfga/.github/blob/main/CODE_OF_CONDUCT.md)

If your PR is under active development, please submit it as a "draft". Once it's ready, open it up for review.
-->

<!-- Provide a brief summary of the changes -->

## Description
<!-- Provide a detailed description of the changes -->
#### What problem is being solved?
Add comprehensive documentation for AI coding agents including architecture overview, key packages, testing guidelines, and maintenance instructions. Highlights reverseexpand.go as critical for ListObjects and includes guideline to review matrix tests when modifying internal/graph or reverseexpand logic.

#### How is it being solved?

#### What changes are made to solve it?

## References
<!--
Provide a list of any applicable references here (GitHub Issue, [OpenFGA RFC](https://github.com/openfga/rfcs), other PRs, etc..). We prefer an accompanying issue for all non-trivial PRs.

When referencing links, follow these examples:
* closes https://github.com/openfga/{repo}/issues/{issue_number}
* reverts https://github.com/openfga/{repo}/pull/{pr_number}
* followup https://github.com/op

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
