# AGENTS: require tracking issue for PRs that apply a workaround

Source: [apache/airflow#65612](https://github.com/apache/airflow/pull/65612)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

PRs that cap a dependency, disable a feature behind a flag, or otherwise defer the real fix were sometimes landing with PR-body text like \"will open a tracking issue\" and nothing concrete linking to the follow-up work — easy to forget, and future readers of the code have no idea why the cap is there.

This change codifies in \`AGENTS.md\` the rule that:

1. A tracking issue must be opened **first**.
2. It must be linked by number in the PR body (not \"will open...\").
3. The issue number must also appear as a **comment at the workaround site in the code** (e.g. \`# TODO(#65609): remove cap after migrating to httpx 1.x\`) so the reference survives the merge and is visible to anyone reading the file later.

Caught during the airflow-ctl 0.1.4rc3 release prep — PR #65607 (httpx cap) was opened with \"will open a tracking issue\" language, then issue #65609 was opened afterwards and retro-linked via a PR comment. Codifying the rule so it does not happen again.

## Test plan
- [X] N/A — doc-only change in \`AGENTS.md\`.

---

##### Was generative AI tooling used to co-author this PR?

- [X] Yes — Claude Opus 4.7 (1M context)

Generated-by: Claude Opus 4.7 (1M context) following [the guidelines](https://github.com/apache/airflow/blob/main/contributing-docs/05_pull_requests.rst#gen-ai-assisted-contributions)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
