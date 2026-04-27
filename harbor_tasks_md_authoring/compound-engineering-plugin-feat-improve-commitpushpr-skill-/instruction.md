# feat: improve commit-push-pr skill with net-result focus and badging

Source: [EveryInc/compound-engineering-plugin#380](https://github.com/EveryInc/compound-engineering-plugin/pull/380)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/AGENTS.md`
- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

Adds three improvements to the **git-commit-push-pr** skill:

**Net-result writing principle** — new "Describe the net result, not the journey" guidance that steers agents away from including work-product details (bugs found during dev, debugging steps, iteration history) in PR descriptions. The diff already contains the fix; narrating the journey implies a separate concern for reviewers.

**Compound Engineering badge** — appends a Compound Engineering badge footer with model/harness/version attribution that matches what `ce:work` did already. Includes a skip-if-present guard so that already add a badge don't cause duplicates.

**Existing PR handling** — adds Step 3 to detect an existing PR before committing. On re-runs, the skill commits and pushes normally, then asks (via platform question tools) whether to update the description instead of failing on `gh pr create`.

## Test plan
- Verify Step 3 routing: no-PR path goes through Steps 4-8, existing-PR path skips to Step 7 existing PR flow
- Verify badge subsection is referenced by both the new-PR and existing-PR update paths
- Check cross-platform question tool names match plugin compliance checklist

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
