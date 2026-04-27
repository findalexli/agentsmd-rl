# improve content-consistency-validator skill structure + add skill-review CI

Source: [jeremylongshore/claude-code-plugins-plus-skills#347](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/347)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md`

## What to add / change

hey @jeremylongshore, thanks for building this marketplace. really like the scale of `340+` plugins with the CCPI package manager + interactive tutorials. Kudos on passing `1.6k` stars! I've just starred it.

ran your content-consistency-validator skill through agent evals and spotted a few quick wins that took it from `~80%` to `~95%` performance:

- added concrete bash commands for source discovery, data extraction + cross-source comparison so the agent can execute immediately

- replaced prose output section with a copy-paste report template showing executive summary table, comparison matrix + action items format

- added extraction verification checkpoint before comparison step to catch empty sources early

also added a lightweight GitHub Action that auto-reviews any skill.md changed in a PR (includes min permissions, uses a pinned action version, only posts a review comment).

this means that it gives you and your contributors an instant quality signal before you have to review yourself (no signup, no tokens needed).

these were easy changes to bring the skill in line with what **performs well against Anthropic's best practices**. honest disclosure, I work at tessl.io where we build tooling around this. not a pitch, just fixes that were straightforward to make! happy to answer any questions on the changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
