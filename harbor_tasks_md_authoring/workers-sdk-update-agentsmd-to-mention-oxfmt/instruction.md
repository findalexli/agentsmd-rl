# Update AGENTS.md to mention oxfmt since we no longer use prettier

Source: [cloudflare/workers-sdk#13053](https://github.com/cloudflare/workers-sdk/pull/13053)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `packages/create-cloudflare/AGENTS.md`

## What to add / change

Minimal update to the AGENTS.md since we no longer use prettier

---

<!--
Please don't delete the checkboxes <3
The following selections do not need to be completed if this PR only contains changes to .md files
-->

- Tests
  - [ ] Tests included/updated
  - [ ] Automated tests not possible - manual testing has been completed as follows:
  - [x] Additional testing not necessary because: I don't think this is testable
- Public documentation
  - [ ] Cloudflare docs PR(s): <!--e.g. <https://github.com/cloudflare/cloudflare-docs/pull/>...-->
  - [x] Documentation not necessary because: minimal infra change

*A picture of a cute animal (not mandatory, but encouraged)*

<!--
Have you read our [Contributing guide](https://github.com/cloudflare/workers-sdk/blob/main/CONTRIBUTING.md)?
In particular, for non-trivial changes, please always engage on the issue or create a discussion or feature request issue first before writing your code.
-->

<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/cloudflare/workers-sdk/pull/13053" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
    <img src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1" alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
