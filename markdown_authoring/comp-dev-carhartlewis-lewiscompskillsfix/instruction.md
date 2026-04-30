# [dev] [carhartlewis] lewis/comp-skills-fix

Source: [trycompai/comp#2679](https://github.com/trycompai/comp/pull/2679)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/audit-design-system/SKILL.md`
- `.agents/skills/audit-hooks/SKILL.md`
- `.agents/skills/audit-rbac/SKILL.md`
- `.agents/skills/audit-tests/SKILL.md`
- `.agents/skills/better-auth-best-practices/SKILL.md`
- `.agents/skills/code/SKILL.md`
- `.agents/skills/cursor-usage/SKILL.md`
- `.agents/skills/data/SKILL.md`
- `.agents/skills/essentials/SKILL.md`
- `.agents/skills/forms/SKILL.md`
- `.agents/skills/infra/SKILL.md`
- `.agents/skills/new-feature-setup/SKILL.md`
- `.agents/skills/prisma/SKILL.md`
- `.agents/skills/production-readiness/SKILL.md`
- `.agents/skills/prompt-engineering/SKILL.md`
- `.agents/skills/stale-worktree-cleanup/SKILL.md`
- `.agents/skills/trigger-advanced-tasks/SKILL.md`
- `.agents/skills/trigger-basic/SKILL.md`
- `.agents/skills/trigger-config/SKILL.md`
- `.agents/skills/trigger-realtime/SKILL.md`
- `.agents/skills/trigger-scheduled-tasks/SKILL.md`
- `.agents/skills/ui/SKILL.md`
- `.claude/agents/test-writer.md`
- `.claude/skills/audit-design-system/SKILL.md`
- `.claude/skills/audit-hooks/SKILL.md`
- `.claude/skills/audit-rbac/SKILL.md`
- `.claude/skills/audit-tests/SKILL.md`
- `.claude/skills/code/SKILL.md`
- `.claude/skills/cursor-usage/SKILL.md`
- `.claude/skills/data/SKILL.md`
- `.claude/skills/essentials/SKILL.md`
- `.claude/skills/forms/SKILL.md`
- `.claude/skills/infra/SKILL.md`
- `.claude/skills/new-feature-setup/SKILL.md`
- `.claude/skills/prisma/SKILL.md`
- `.claude/skills/production-readiness/SKILL.md`
- `.claude/skills/prompt-engineering/SKILL.md`
- `.claude/skills/trigger-advanced-tasks/SKILL.md`
- `.claude/skills/trigger-basic/SKILL.md`
- `.claude/skills/trigger-config/SKILL.md`
- `.claude/skills/trigger-realtime/SKILL.md`
- `.claude/skills/trigger-scheduled-tasks/SKILL.md`
- `.claude/skills/ui/SKILL.md`
- `.cursor/rules/data.mdc`
- `.cursor/rules/forms.mdc`
- `.cursor/rules/infra.mdc`
- `.cursor/rules/prisma.mdc`
- `.cursor/rules/prompt-engineering.mdc`
- `.cursor/rules/trigger.advanced-tasks.mdc`
- `.cursor/rules/trigger.basic.mdc`
- `.cursor/rules/trigger.realtime.mdc`
- `AGENTS.md`

## What to add / change

This is an automated pull request to merge lewis/comp-skills-fix into dev.
It was created by the [Auto Pull Request] action.

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds comprehensive project rules and agent skills to standardize design system usage, data patterns, RBAC, testing, and Trigger.dev across the monorepo. Also switches all docs and skills to `bun`/`bunx` commands and clarifies prioritizing `@trycompai/design-system` over legacy `@trycompai/ui`.

- **New Features**
  - Introduced AGENTS.md with guidance on tooling (`bun`), code style, auth, API/RBAC, design system, data fetching, testing, DB, and Git.
  - Added skills under `.agents/skills` and mirrored in `.claude/skills` for DS migration to `@trycompai/design-system` (replacing `@trycompai/ui` and `lucide-react`), hooks/data (SWR, `apiClient`), RBAC/audit logs, forms (RHF + Zod), Prisma, infra, UI rules, code standards, prompt practices, and Trigger.dev (basic, advanced, realtime, scheduled, config).
  - Added composite skills: production-readiness (RBAC, hooks, design system, tests + typecheck), new-feature-setup, and stale-worktree-cleanup.
  - Standardized commands to `bun`/`bunx` (typecheck, tests); clarified DS over legacy UI; updated rules/examples (data hook adds `updateTask`, Prisma regen includes `apps/portal`, Trigger.dev tags max 128 chars, improved wait.until example, realtime install via `bun add`).
  - No app code or dependencies changed.

<sup>Written for co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
