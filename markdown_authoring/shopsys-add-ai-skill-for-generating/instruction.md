# Add AI skill for generating business-focused PR descriptions

Source: [shopsys/shopsys#4537](https://github.com/shopsys/shopsys/pull/4537)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/pr-description/SKILL.md`

## What to add / change

#### Description, the reason for the PR

Writing good PR descriptions that focus on business value rather than code-level changes requires effort and discipline. Developers often default to listing changed files or technical details, which makes it harder for reviewers and product owners to understand the actual impact of a change.

This PR adds a new AI-powered skill (`/pr-description`) that automatically analyzes a pull request diff and generates a description focused on what changed from the user's perspective — the problem, the motivation, and the new behavior. It follows the project's PR template and can be invoked with an existing PR number to update its description directly.

#### Fixes issues
N/A

#### License Agreement for contributions

- [x] I have read and signed [License Agreement for contributions](https://www.shopsys.com/license-agreement)




<!-- Replace -->
----
:globe_with_meridians: Live Preview:
  - https://mg-pr-description-skill.odin.shopsys.cloud
  - https://cz.mg-pr-description-skill.odin.shopsys.cloud
  - https://mg-pr-description-skill.odin.shopsys.cloud/sk
<!-- Replace -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
