"""Behavioral checks for comp-dev-carhartlewis-lewiscompskillsfix (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/comp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-design-system/SKILL.md')
    assert '3. **Icons**: Use `@trycompai/design-system/icons` (Carbon icons), NOT `lucide-react`. Check with `node -e "const i = require(\'@trycompai/design-system/icons\'); console.log(Object.keys(i).filter(k => ' in text, "expected to find: " + '3. **Icons**: Use `@trycompai/design-system/icons` (Carbon icons), NOT `lucide-react`. Check with `node -e "const i = require(\'@trycompai/design-system/icons\'); console.log(Object.keys(i).filter(k => '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-design-system/SKILL.md')
    assert '2. **Always check DS exports first** before reaching for `@trycompai/ui`. Run `node -e "console.log(Object.keys(require(\'@trycompai/design-system\')))"` to check.' in text, "expected to find: " + '2. **Always check DS exports first** before reaching for `@trycompai/ui`. Run `node -e "console.log(Object.keys(require(\'@trycompai/design-system\')))"` to check.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-design-system/SKILL.md')
    assert '1. **`@trycompai/design-system`** is the primary component library. `@trycompai/ui` is legacy — only use as last resort when no DS equivalent exists.' in text, "expected to find: " + '1. **`@trycompai/design-system`** is the primary component library. `@trycompai/ui` is legacy — only use as last resort when no DS equivalent exists.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-hooks/SKILL.md')
    assert 'description: Audit & fix hooks and API usage patterns — eliminate server actions, raw fetch, and stale patterns' in text, "expected to find: " + 'description: Audit & fix hooks and API usage patterns — eliminate server actions, raw fetch, and stale patterns'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-hooks/SKILL.md')
    assert '9. **Callback props for data refresh** (`onXxxAdded`, `onSuccess`) → remove, rely on SWR cache sharing' in text, "expected to find: " + '9. **Callback props for data refresh** (`onXxxAdded`, `onSuccess`) → remove, rely on SWR cache sharing'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-hooks/SKILL.md')
    assert 'Audit the specified files for hook and API usage compliance. **Fix every issue found immediately.**' in text, "expected to find: " + 'Audit the specified files for hook and API usage compliance. **Fix every issue found immediately.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-rbac/SKILL.md')
    assert '`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`' in text, "expected to find: " + '`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-rbac/SKILL.md')
    assert '1. **Every mutation element** (button, form submit, toggle, switch, file upload) MUST be gated with `usePermissions` from `@/hooks/use-permissions`. If not:' in text, "expected to find: " + '1. **Every mutation element** (button, form submit, toggle, switch, file upload) MUST be gated with `usePermissions` from `@/hooks/use-permissions`. If not:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-rbac/SKILL.md')
    assert "1. **Every mutation endpoint** (POST, PATCH, PUT, DELETE) MUST have `@RequirePermission('resource', 'action')`. If missing, **add it**." in text, "expected to find: " + "1. **Every mutation endpoint** (POST, PATCH, PUT, DELETE) MUST have `@RequirePermission('resource', 'action')`. If missing, **add it**."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-tests/SKILL.md')
    assert 'Check that unit tests exist and pass for permission-gated components. **Write missing tests immediately.**' in text, "expected to find: " + 'Check that unit tests exist and pass for permission-gated components. **Write missing tests immediately.**'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-tests/SKILL.md')
    assert 'Use `setMockPermissions`, `ADMIN_PERMISSIONS`, `AUDITOR_PERMISSIONS` from test utils.' in text, "expected to find: " + 'Use `setMockPermissions`, `ADMIN_PERMISSIONS`, `AUDITOR_PERMISSIONS` from test utils.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/audit-tests/SKILL.md')
    assert '- **Component testing**: `@testing-library/react` + `@testing-library/jest-dom`' in text, "expected to find: " + '- **Component testing**: `@testing-library/react` + `@testing-library/jest-dom`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/better-auth-best-practices/SKILL.md')
    assert '- [Init Options Source](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)' in text, "expected to find: " + '- [Init Options Source](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/better-auth-best-practices/SKILL.md')
    assert '- `bunx @better-auth/cli@latest generate` - Generate schema for Prisma/Drizzle' in text, "expected to find: " + '- `bunx @better-auth/cli@latest generate` - Generate schema for Prisma/Drizzle'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/better-auth-best-practices/SKILL.md')
    assert '- `bunx @better-auth/cli@latest migrate` - Apply schema (built-in adapter)' in text, "expected to find: " + '- `bunx @better-auth/cli@latest migrate` - Apply schema (built-in adapter)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code/SKILL.md')
    assert 'description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"' in text, "expected to find: " + 'description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code/SKILL.md')
    assert 'const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };' in text, "expected to find: " + 'const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code/SKILL.md')
    assert 'const TaskSchema = z.object({ id: z.string(), title: z.string() });' in text, "expected to find: " + 'const TaskSchema = z.object({ id: z.string(), title: z.string() });'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cursor-usage/SKILL.md')
    assert 'Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdow' in text, "expected to find: " + 'Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdow'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cursor-usage/SKILL.md')
    assert "**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly." in text, "expected to find: " + "**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cursor-usage/SKILL.md')
    assert 'The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.' in text, "expected to find: " + 'The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/data/SKILL.md')
    assert 'description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"' in text, "expected to find: " + 'description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/data/SKILL.md')
    assert 'export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {' in text, "expected to find: " + 'export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/data/SKILL.md')
    assert 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {' in text, "expected to find: " + 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/essentials/SKILL.md')
    assert 'export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {' in text, "expected to find: " + 'export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/essentials/SKILL.md')
    assert '**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.' in text, "expected to find: " + '**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/essentials/SKILL.md')
    assert '**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.' in text, "expected to find: " + '**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/forms/SKILL.md')
    assert 'description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"' in text, "expected to find: " + 'description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/forms/SKILL.md')
    assert "import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';" in text, "expected to find: " + "import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';"[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/forms/SKILL.md')
    assert '<Button type="button" onClick={() => append({ name: \'\' })}>Add</Button>' in text, "expected to find: " + '<Button type="button" onClick={() => append({ name: \'\' })}>Add</Button>'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/infra/SKILL.md')
    assert 'description: "Use when working with packages, dependencies, monorepo structure, or build configuration"' in text, "expected to find: " + 'description: "Use when working with packages, dependencies, monorepo structure, or build configuration"'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/infra/SKILL.md')
    assert '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system' in text, "expected to find: " + '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/infra/SKILL.md')
    assert '- **Empty interface extends**: Use `type X = SomeType` instead' in text, "expected to find: " + '- **Empty interface extends**: Use `type X = SomeType` instead'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-feature-setup/SKILL.md')
    assert 'description: Use when starting a new feature, Linear ticket, or bugfix in this repo — establishes the branch + worktree + env + DB + dev-server conventions so the work is immediately ready to code wit' in text, "expected to find: " + 'description: Use when starting a new feature, Linear ticket, or bugfix in this repo — establishes the branch + worktree + env + DB + dev-server conventions so the work is immediately ready to code wit'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-feature-setup/SKILL.md')
    assert 'Use the `stale-worktree-cleanup` skill when worktrees accumulate. It handles both `git worktree remove` and dropping the `compdev_<slug>` database in one pass. Never leave orphan databases — they pile' in text, "expected to find: " + 'Use the `stale-worktree-cleanup` skill when worktrees accumulate. It handles both `git worktree remove` and dropping the `compdev_<slug>` database in one pass. Never leave orphan databases — they pile'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-feature-setup/SKILL.md')
    assert "- Non-active worktrees need a different `PORT` to avoid collision — add `PORT=3001` (or `3334`, etc.) to the worktree's `.env.local`. `.env.local` is not symlinked and stays per-worktree." in text, "expected to find: " + "- Non-active worktrees need a different `PORT` to avoid collision — add `PORT=3001` (or `3334`, etc.) to the worktree's `.env.local`. `.env.local` is not symlinked and stays per-worktree."[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prisma/SKILL.md')
    assert 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\')")) // ❌ Missing ::text' in text, "expected to find: " + 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\')")) // ❌ Missing ::text'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prisma/SKILL.md')
    assert '**Schema changes happen in `packages/db`, then regenerate types in each app.**' in text, "expected to find: " + '**Schema changes happen in `packages/db`, then regenerate types in each app.**'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prisma/SKILL.md')
    assert 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\'::text)"))' in text, "expected to find: " + 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\'::text)"))'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/production-readiness/SKILL.md')
    assert 'description: Run all audit checks (RBAC, hooks, design system, tests) and verify build' in text, "expected to find: " + 'description: Run all audit checks (RBAC, hooks, design system, tests) and verify build'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/production-readiness/SKILL.md')
    assert 'Output a Production Readiness Report summarizing all fixes applied and build status.' in text, "expected to find: " + 'Output a Production Readiness Report summarizing all fixes applied and build status.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/production-readiness/SKILL.md')
    assert 'bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app' in text, "expected to find: " + 'bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prompt-engineering/SKILL.md')
    assert "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)" in text, "expected to find: " + "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)"[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prompt-engineering/SKILL.md')
    assert '✅ Good: "Summarize the following article in three bullet points, focusing on key findings"' in text, "expected to find: " + '✅ Good: "Summarize the following article in three bullet points, focusing on key findings"'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/prompt-engineering/SKILL.md')
    assert '✅ Good: "Debug this Python function that should return the sum of even numbers in a list"' in text, "expected to find: " + '✅ Good: "Debug this Python function that should return the sum of even numbers in a list"'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/stale-worktree-cleanup/SKILL.md')
    assert "This repo's `.githooks/post-checkout` creates a per-worktree Postgres database (`compdev_<slug>`) on every `git worktree add`. Git has no `pre-worktree-remove` hook, so dead databases pile up over tim" in text, "expected to find: " + "This repo's `.githooks/post-checkout` creates a per-worktree Postgres database (`compdev_<slug>`) on every `git worktree add`. Git has no `pre-worktree-remove` hook, so dead databases pile up over tim"[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/stale-worktree-cleanup/SKILL.md')
    assert 'description: Use when cleaning up old git worktrees, removing worktrees whose branches have merged or been abandoned, or dropping orphaned compdev_* Postgres databases. Triggers on "clean up worktrees' in text, "expected to find: " + 'description: Use when cleaning up old git worktrees, removing worktrees whose branches have merged or been abandoned, or dropping orphaned compdev_* Postgres databases. Triggers on "clean up worktrees'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/stale-worktree-cleanup/SKILL.md')
    assert "Then query the DB for `compdev_*` databases. The management URL is the main worktree's `DATABASE_URL` with the database path swapped to `postgres`:" in text, "expected to find: " + "Then query the DB for `compdev_*` databases. The management URL is the main worktree's `DATABASE_URL` with the database path swapped to `postgres`:"[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-advanced-tasks/SKILL.md')
    assert 'Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.' in text, "expected to find: " + 'Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-advanced-tasks/SKILL.md')
    assert '// Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same' in text, "expected to find: " + '// Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-advanced-tasks/SKILL.md')
    assert "const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });" in text, "expected to find: " + "const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });"[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-basic/SKILL.md')
    assert '> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.' in text, "expected to find: " + '> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-basic/SKILL.md')
    assert '- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output' in text, "expected to find: " + '- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-basic/SKILL.md')
    assert '> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.' in text, "expected to find: " + '> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-config/SKILL.md')
    assert "Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled." in text, "expected to find: " + "Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled."[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-config/SKILL.md')
    assert '{ name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },' in text, "expected to find: " + '{ name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-config/SKILL.md')
    assert '- **External packages**: Add modules with native addons to the `build.external` array' in text, "expected to find: " + '- **External packages**: Add modules with native addons to the `build.external` array'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-realtime/SKILL.md')
    assert 'function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {' in text, "expected to find: " + 'function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-realtime/SKILL.md')
    assert 'function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {' in text, "expected to find: " + 'function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-realtime/SKILL.md')
    assert '- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup' in text, "expected to find: " + '- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.' in text, "expected to find: " + 'Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },' in text, "expected to find: " + 'cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });' in text, "expected to find: " + 'await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui/SKILL.md')
    assert 'description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."' in text, "expected to find: " + 'description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui/SKILL.md')
    assert '<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">' in text, "expected to find: " + '<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui/SKILL.md')
    assert "import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';" in text, "expected to find: " + "import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';"[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/test-writer.md')
    assert '- Run the test after writing to verify it passes: `cd apps/app && bunx vitest run path/to/file.test.tsx`' in text, "expected to find: " + '- Run the test after writing to verify it passes: `cd apps/app && bunx vitest run path/to/file.test.tsx`'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/test-writer.md')
    assert '- **Run**: `cd apps/app && bunx vitest run path/to/test`' in text, "expected to find: " + '- **Run**: `cd apps/app && bunx vitest run path/to/test`'[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-design-system/SKILL.md')
    assert '5. Run build to verify: `bunx turbo run typecheck --filter=@trycompai/app`' in text, "expected to find: " + '5. Run build to verify: `bunx turbo run typecheck --filter=@trycompai/app`'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-hooks/SKILL.md')
    assert '4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/app`' in text, "expected to find: " + '4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/app`'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-rbac/SKILL.md')
    assert '4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app`' in text, "expected to find: " + '4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app`'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-tests/SKILL.md')
    assert '- **Run**: `cd apps/app && bunx vitest run`' in text, "expected to find: " + '- **Run**: `cd apps/app && bunx vitest run`'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-tests/SKILL.md')
    assert '5. Run: `cd apps/app && bunx vitest run`' in text, "expected to find: " + '5. Run: `cd apps/app && bunx vitest run`'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/code/SKILL.md')
    assert 'description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"' in text, "expected to find: " + 'description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/code/SKILL.md')
    assert 'const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };' in text, "expected to find: " + 'const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/code/SKILL.md')
    assert 'const TaskSchema = z.object({ id: z.string(), title: z.string() });' in text, "expected to find: " + 'const TaskSchema = z.object({ id: z.string(), title: z.string() });'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cursor-usage/SKILL.md')
    assert 'Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdow' in text, "expected to find: " + 'Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdow'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cursor-usage/SKILL.md')
    assert "**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly." in text, "expected to find: " + "**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly."[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cursor-usage/SKILL.md')
    assert 'The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.' in text, "expected to find: " + 'The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/data/SKILL.md')
    assert 'description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"' in text, "expected to find: " + 'description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"'[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/data/SKILL.md')
    assert 'export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {' in text, "expected to find: " + 'export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/data/SKILL.md')
    assert 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {' in text, "expected to find: " + 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/essentials/SKILL.md')
    assert 'export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {' in text, "expected to find: " + 'export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/essentials/SKILL.md')
    assert '**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.' in text, "expected to find: " + '**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/essentials/SKILL.md')
    assert '**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.' in text, "expected to find: " + '**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/forms/SKILL.md')
    assert 'description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"' in text, "expected to find: " + 'description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"'[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/forms/SKILL.md')
    assert "import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';" in text, "expected to find: " + "import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';"[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/forms/SKILL.md')
    assert '<Button type="button" onClick={() => append({ name: \'\' })}>Add</Button>' in text, "expected to find: " + '<Button type="button" onClick={() => append({ name: \'\' })}>Add</Button>'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/infra/SKILL.md')
    assert 'description: "Use when working with packages, dependencies, monorepo structure, or build configuration"' in text, "expected to find: " + 'description: "Use when working with packages, dependencies, monorepo structure, or build configuration"'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/infra/SKILL.md')
    assert '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system' in text, "expected to find: " + '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/infra/SKILL.md')
    assert '- **Empty interface extends**: Use `type X = SomeType` instead' in text, "expected to find: " + '- **Empty interface extends**: Use `type X = SomeType` instead'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/new-feature-setup/SKILL.md')
    assert '- Always run typecheck before declaring a change done (`bunx turbo run typecheck --filter=<pkg>`)' in text, "expected to find: " + '- Always run typecheck before declaring a change done (`bunx turbo run typecheck --filter=<pkg>`)'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prisma/SKILL.md')
    assert 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\')")) // ❌ Missing ::text' in text, "expected to find: " + 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\')")) // ❌ Missing ::text'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prisma/SKILL.md')
    assert '**Schema changes happen in `packages/db`, then regenerate types in each app.**' in text, "expected to find: " + '**Schema changes happen in `packages/db`, then regenerate types in each app.**'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prisma/SKILL.md')
    assert 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\'::text)"))' in text, "expected to find: " + 'id String @id @default(dbgenerated("generate_prefixed_cuid(\'usr\'::text)"))'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/production-readiness/SKILL.md')
    assert 'bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app' in text, "expected to find: " + 'bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/production-readiness/SKILL.md')
    assert 'cd apps/app && bunx vitest run' in text, "expected to find: " + 'cd apps/app && bunx vitest run'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prompt-engineering/SKILL.md')
    assert "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)" in text, "expected to find: " + "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)"[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prompt-engineering/SKILL.md')
    assert '✅ Good: "Summarize the following article in three bullet points, focusing on key findings"' in text, "expected to find: " + '✅ Good: "Summarize the following article in three bullet points, focusing on key findings"'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prompt-engineering/SKILL.md')
    assert '✅ Good: "Debug this Python function that should return the sum of even numbers in a list"' in text, "expected to find: " + '✅ Good: "Debug this Python function that should return the sum of even numbers in a list"'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-advanced-tasks/SKILL.md')
    assert 'Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.' in text, "expected to find: " + 'Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-advanced-tasks/SKILL.md')
    assert '// Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same' in text, "expected to find: " + '// Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-advanced-tasks/SKILL.md')
    assert "const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });" in text, "expected to find: " + "const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });"[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-basic/SKILL.md')
    assert '> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.' in text, "expected to find: " + '> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-basic/SKILL.md')
    assert '- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output' in text, "expected to find: " + '- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output'[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-basic/SKILL.md')
    assert '> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.' in text, "expected to find: " + '> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.'[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-config/SKILL.md')
    assert "Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled." in text, "expected to find: " + "Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled."[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-config/SKILL.md')
    assert '{ name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },' in text, "expected to find: " + '{ name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },'[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-config/SKILL.md')
    assert '- **External packages**: Add modules with native addons to the `build.external` array' in text, "expected to find: " + '- **External packages**: Add modules with native addons to the `build.external` array'[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-realtime/SKILL.md')
    assert 'function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {' in text, "expected to find: " + 'function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-realtime/SKILL.md')
    assert 'function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {' in text, "expected to find: " + 'function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {'[:80]


def test_signal_111():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-realtime/SKILL.md')
    assert '- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup' in text, "expected to find: " + '- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup'[:80]


def test_signal_112():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.' in text, "expected to find: " + 'Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.'[:80]


def test_signal_113():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },' in text, "expected to find: " + 'cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },'[:80]


def test_signal_114():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/trigger-scheduled-tasks/SKILL.md')
    assert 'await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });' in text, "expected to find: " + 'await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });'[:80]


def test_signal_115():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui/SKILL.md')
    assert 'description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."' in text, "expected to find: " + 'description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."'[:80]


def test_signal_116():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui/SKILL.md')
    assert '<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">' in text, "expected to find: " + '<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">'[:80]


def test_signal_117():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui/SKILL.md')
    assert "import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';" in text, "expected to find: " + "import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';"[:80]


def test_signal_118():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data.mdc')
    assert 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {' in text, "expected to find: " + 'const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {'[:80]


def test_signal_119():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data.mdc')
    assert 'await apiClient.put(`/v1/tasks/${taskId}`, input, organizationId);' in text, "expected to find: " + 'await apiClient.put(`/v1/tasks/${taskId}`, input, organizationId);'[:80]


def test_signal_120():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data.mdc')
    assert 'return { tasks: data ?? [], createTask, updateTask, mutate };' in text, "expected to find: " + 'return { tasks: data ?? [], createTask, updateTask, mutate };'[:80]


def test_signal_121():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/forms.mdc')
    assert 'const passwordSchema = z.object({' in text, "expected to find: " + 'const passwordSchema = z.object({'[:80]


def test_signal_122():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/forms.mdc')
    assert 'const profileSchema = z.object({' in text, "expected to find: " + 'const profileSchema = z.object({'[:80]


def test_signal_123():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/infra.mdc')
    assert '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system' in text, "expected to find: " + '│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system'[:80]


def test_signal_124():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/prisma.mdc')
    assert 'bun run -F apps/portal db:generate' in text, "expected to find: " + 'bun run -F apps/portal db:generate'[:80]


def test_signal_125():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/prompt-engineering.mdc')
    assert '## The 6 Core Techniques' in text, "expected to find: " + '## The 6 Core Techniques'[:80]


def test_signal_126():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trigger.advanced-tasks.mdc')
    assert "import { logger, task, usage } from '@trigger.dev/sdk';" in text, "expected to find: " + "import { logger, task, usage } from '@trigger.dev/sdk';"[:80]


def test_signal_127():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trigger.advanced-tasks.mdc')
    assert '- Max 10 tags per run, 1-128 characters each' in text, "expected to find: " + '- Max 10 tags per run, 1-128 characters each'[:80]


def test_signal_128():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trigger.basic.mdc')
    assert 'await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });' in text, "expected to find: " + 'await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });'[:80]


def test_signal_129():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trigger.basic.mdc')
    assert '// Wait until a future date' in text, "expected to find: " + '// Wait until a future date'[:80]


def test_signal_130():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trigger.realtime.mdc')
    assert 'bun add @trigger.dev/react-hooks' in text, "expected to find: " + 'bun add @trigger.dev/react-hooks'[:80]


def test_signal_131():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Auth lives in `apps/api` (NestJS).** The API is the single source of truth for authentication via better-auth. All apps and packages that need to authenticate (app, portal, device-agent, etc.) MUS' in text, "expected to find: " + '- **Auth lives in `apps/api` (NestJS).** The API is the single source of truth for authentication via better-auth. All apps and packages that need to authenticate (app, portal, device-agent, etc.) MUS'[:80]


def test_signal_132():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`' in text, "expected to find: " + '`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`'[:80]


def test_signal_133():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **After editing any frontend component**: Run the `audit-design-system` skill to catch `@trycompai/ui` or `lucide-react` imports that should be migrated' in text, "expected to find: " + '- **After editing any frontend component**: Run the `audit-design-system` skill to catch `@trycompai/ui` or `lucide-react` imports that should be migrated'[:80]

