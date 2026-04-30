# chore(agents): Migrate repo-wide cursor rules to skills

Source: [getsentry/sentry-javascript#19549](https://github.com/getsentry/sentry-javascript/pull/19549)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-ai-integration/SKILL.md`
- `.agents/skills/release/SKILL.md`
- `.agents/skills/upgrade-dep/SKILL.md`
- `.agents/skills/upgrade-otel/SKILL.md`
- `.cursor/rules/adding-a-new-ai-integration.mdc`
- `.cursor/rules/fetch-docs/attributes.mdc`
- `.cursor/rules/fetch-docs/scopes.mdc`
- `.cursor/rules/publishing_release.mdc`
- `.cursor/rules/sdk_dependency_upgrades.mdc`
- `.cursor/rules/upgrade_opentelemetry_instrumentations.mdc`
- `AGENTS.md`

## What to add / change

- Create `/release`, `/upgrade-dep`, `/upgrade-otel` skills from `.cursor/rules/` procedural guides
- Inline `fetch-docs/attributes.mdc` and `fetch-docs/scopes.mdc` as reference links in root `AGENTS.md`
- Delete 5 migrated `.cursor/rules/` files (-250 lines of Cursor-specific format)

Some cursor rules used `alwaysApply: false`, meaning they loaded on-demand. Moving them into `AGENTS.md` (always loaded) would waste context tokens on every interaction. Skills are the right fit — they're on-demand, match the existing pattern (`/e2e`, `/triage-issue`, etc.), and work across all agents.

Part of the `.cursor/rules/` → `AGENTS.md` migration. Remaining files(`adding-a-new-ai-integration.mdc` + browser fetch-docs) will be handled in a follow-up PR with scoped `AGENTS.md` files.

Closes #19550 (added automatically)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
