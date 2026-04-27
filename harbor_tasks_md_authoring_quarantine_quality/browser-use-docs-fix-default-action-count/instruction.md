# docs: fix default action count in docs

Source: [browser-use/browser-use#3741](https://github.com/browser-use/browser-use/pull/3741)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Corrected the documented default for max_actions_per_step to 3 to match current behavior. Cleaned minor formatting in AGENTS.md (removed trailing spaces and fixed a tips blockquote).

<sup>Written for commit 2e887d0076f02964dad88c72d4a079d60df7825e. Summary will update automatically on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
