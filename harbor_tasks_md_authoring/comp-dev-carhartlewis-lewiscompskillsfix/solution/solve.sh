#!/usr/bin/env bash
set -euo pipefail

cd /workspace/comp

# Idempotency guard
if grep -qF "3. **Icons**: Use `@trycompai/design-system/icons` (Carbon icons), NOT `lucide-r" ".agents/skills/audit-design-system/SKILL.md" && grep -qF "description: Audit & fix hooks and API usage patterns \u2014 eliminate server actions" ".agents/skills/audit-hooks/SKILL.md" && grep -qF "`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `ta" ".agents/skills/audit-rbac/SKILL.md" && grep -qF "Check that unit tests exist and pass for permission-gated components. **Write mi" ".agents/skills/audit-tests/SKILL.md" && grep -qF "- [Init Options Source](https://github.com/better-auth/better-auth/blob/main/pac" ".agents/skills/better-auth-best-practices/SKILL.md" && grep -qF "description: \"Use when writing TypeScript/React code - covers type safety, compo" ".agents/skills/code/SKILL.md" && grep -qF "Cursor rules provide system-level instructions to the AI to maintain code consis" ".agents/skills/cursor-usage/SKILL.md" && grep -qF "description: \"Use when implementing data fetching, API calls, server/client comp" ".agents/skills/data/SKILL.md" && grep -qF "export default async function Page({ params }: { params: Promise<{ orgId: string" ".agents/skills/essentials/SKILL.md" && grep -qF "description: \"Use when building forms - covers React Hook Form, Zod validation, " ".agents/skills/forms/SKILL.md" && grep -qF "description: \"Use when working with packages, dependencies, monorepo structure, " ".agents/skills/infra/SKILL.md" && grep -qF "description: Use when starting a new feature, Linear ticket, or bugfix in this r" ".agents/skills/new-feature-setup/SKILL.md" && grep -qF "id String @id @default(dbgenerated(\"generate_prefixed_cuid('usr')\")) // \u274c Missin" ".agents/skills/prisma/SKILL.md" && grep -qF "description: Run all audit checks (RBAC, hooks, design system, tests) and verify" ".agents/skills/production-readiness/SKILL.md" && grep -qF "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com" ".agents/skills/prompt-engineering/SKILL.md" && grep -qF "This repo's `.githooks/post-checkout` creates a per-worktree Postgres database (" ".agents/skills/stale-worktree-cleanup/SKILL.md" && grep -qF "Design tasks to be stateless, idempotent, and resilient to failures. Use metadat" ".agents/skills/trigger-advanced-tasks/SKILL.md" && grep -qF "> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Pro" ".agents/skills/trigger-basic/SKILL.md" && grep -qF "Extensions only affect deployment, not local development. Use `external` array f" ".agents/skills/trigger-config/SKILL.md" && grep -qF "function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessT" ".agents/skills/trigger-realtime/SKILL.md" && grep -qF "Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: Extern" ".agents/skills/trigger-scheduled-tasks/SKILL.md" && grep -qF "description: \"Use when building or editing frontend UI components, layouts, styl" ".agents/skills/ui/SKILL.md" && grep -qF "- Run the test after writing to verify it passes: `cd apps/app && bunx vitest ru" ".claude/agents/test-writer.md" && grep -qF "5. Run build to verify: `bunx turbo run typecheck --filter=@trycompai/app`" ".claude/skills/audit-design-system/SKILL.md" && grep -qF "4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/app`" ".claude/skills/audit-hooks/SKILL.md" && grep -qF "4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/api --" ".claude/skills/audit-rbac/SKILL.md" && grep -qF "- **Run**: `cd apps/app && bunx vitest run`" ".claude/skills/audit-tests/SKILL.md" && grep -qF "description: \"Use when writing TypeScript/React code - covers type safety, compo" ".claude/skills/code/SKILL.md" && grep -qF "Cursor rules provide system-level instructions to the AI to maintain code consis" ".claude/skills/cursor-usage/SKILL.md" && grep -qF "description: \"Use when implementing data fetching, API calls, server/client comp" ".claude/skills/data/SKILL.md" && grep -qF "export default async function Page({ params }: { params: Promise<{ orgId: string" ".claude/skills/essentials/SKILL.md" && grep -qF "description: \"Use when building forms - covers React Hook Form, Zod validation, " ".claude/skills/forms/SKILL.md" && grep -qF "description: \"Use when working with packages, dependencies, monorepo structure, " ".claude/skills/infra/SKILL.md" && grep -qF "- Always run typecheck before declaring a change done (`bunx turbo run typecheck" ".claude/skills/new-feature-setup/SKILL.md" && grep -qF "id String @id @default(dbgenerated(\"generate_prefixed_cuid('usr')\")) // \u274c Missin" ".claude/skills/prisma/SKILL.md" && grep -qF "bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app" ".claude/skills/production-readiness/SKILL.md" && grep -qF "Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com" ".claude/skills/prompt-engineering/SKILL.md" && grep -qF "Design tasks to be stateless, idempotent, and resilient to failures. Use metadat" ".claude/skills/trigger-advanced-tasks/SKILL.md" && grep -qF "> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Pro" ".claude/skills/trigger-basic/SKILL.md" && grep -qF "Extensions only affect deployment, not local development. Use `external` array f" ".claude/skills/trigger-config/SKILL.md" && grep -qF "function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessT" ".claude/skills/trigger-realtime/SKILL.md" && grep -qF "Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: Extern" ".claude/skills/trigger-scheduled-tasks/SKILL.md" && grep -qF "description: \"Use when building or editing frontend UI components, layouts, styl" ".claude/skills/ui/SKILL.md" && grep -qF "const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTask" ".cursor/rules/data.mdc" && grep -qF "const passwordSchema = z.object({" ".cursor/rules/forms.mdc" && grep -qF "\u2502   \u251c\u2500\u2500 ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-s" ".cursor/rules/infra.mdc" && grep -qF "bun run -F apps/portal db:generate" ".cursor/rules/prisma.mdc" && grep -qF "## The 6 Core Techniques" ".cursor/rules/prompt-engineering.mdc" && grep -qF "import { logger, task, usage } from '@trigger.dev/sdk';" ".cursor/rules/trigger.advanced-tasks.mdc" && grep -qF "await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });" ".cursor/rules/trigger.basic.mdc" && grep -qF "bun add @trigger.dev/react-hooks" ".cursor/rules/trigger.realtime.mdc" && grep -qF "- **Auth lives in `apps/api` (NestJS).** The API is the single source of truth f" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/audit-design-system/SKILL.md b/.agents/skills/audit-design-system/SKILL.md
@@ -0,0 +1,23 @@
+---
+name: audit-design-system
+description: Audit & fix design system usage — migrate @trycompai/ui and lucide-react to @trycompai/design-system
+---
+
+Audit the specified files for design system compliance. **Fix every issue found immediately.**
+
+## Rules
+
+1. **`@trycompai/design-system`** is the primary component library. `@trycompai/ui` is legacy — only use as last resort when no DS equivalent exists.
+2. **Always check DS exports first** before reaching for `@trycompai/ui`. Run `node -e "console.log(Object.keys(require('@trycompai/design-system')))"` to check.
+3. **Icons**: Use `@trycompai/design-system/icons` (Carbon icons), NOT `lucide-react`. Check with `node -e "const i = require('@trycompai/design-system/icons'); console.log(Object.keys(i).filter(k => k.match(/YourSearch/i)))"`.
+4. **DS components that do NOT accept `className`**: `Text`, `Stack`, `HStack`, `Badge`, `Button` — wrap in `<div>` for custom styling.
+5. **Button**: Use DS `Button` with `loading`, `iconLeft`, `iconRight` props instead of manually rendering spinners/icons.
+6. **Layout**: Use `PageLayout`, `PageHeader`, `Stack`, `HStack`, `Section`, `SettingGroup`.
+7. **Patterns**: Sheet (`Sheet > SheetContent > SheetHeader + SheetBody`), Drawer, Collapsible.
+
+## Process
+1. Read files specified in `$ARGUMENTS`
+2. Find `@trycompai/ui` imports — check if DS equivalent exists
+3. Find `lucide-react` imports — find matching Carbon icons
+4. Migrate components and icons
+5. Run build to verify: `bunx turbo run typecheck --filter=@trycompai/app`
diff --git a/.agents/skills/audit-hooks/SKILL.md b/.agents/skills/audit-hooks/SKILL.md
@@ -0,0 +1,34 @@
+---
+name: audit-hooks
+description: Audit & fix hooks and API usage patterns — eliminate server actions, raw fetch, and stale patterns
+---
+
+Audit the specified files for hook and API usage compliance. **Fix every issue found immediately.**
+
+## Forbidden Patterns (fix immediately)
+
+1. **`useAction` from `next-safe-action`** → replace with SWR hook or custom mutation hook
+2. **Server actions mutating via `@db`** → delete and use API hook instead
+3. **Direct `@db` in client components** → replace with `apiClient` via hook
+4. **Direct `@db` in Next.js pages for mutations** → replace with `serverApi`
+5. **Raw `fetch()` without `credentials: 'include'`** → use `apiClient`
+6. **`window.location.reload()` after mutations** → use SWR `mutate()`
+7. **`router.refresh()` after mutations** → use SWR `mutate()`
+8. **`useEffect` + `apiClient.get` for data fetching** → replace with `useSWR`
+9. **Callback props for data refresh** (`onXxxAdded`, `onSuccess`) → remove, rely on SWR cache sharing
+
+## Required Patterns
+
+- **Client data fetching**: `useSWR` with `apiClient` or custom hook
+- **Client mutations**: custom hooks wrapping `apiClient` with `mutate()` for cache invalidation
+- **Server components**: `serverApi` from `apps/app/src/lib/api-server.ts`
+- **SWR**: `fallbackData` for SSR data, `revalidateOnMount: !initialData`
+- **API response**: lists = `response.data.data`, single = `response.data`
+- **`mutate()` safety**: guard against `undefined` in optimistic update functions
+- **`Array.isArray()` checks**: when consuming SWR data that could be stale
+
+## Process
+1. Read files specified in `$ARGUMENTS`
+2. Find forbidden patterns and fix them
+3. Ensure all data fetching uses SWR hooks
+4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/app`
diff --git a/.agents/skills/audit-rbac/SKILL.md b/.agents/skills/audit-rbac/SKILL.md
@@ -0,0 +1,42 @@
+---
+name: audit-rbac
+description: Audit & fix RBAC and audit log compliance in API endpoints and frontend components
+---
+
+Audit the specified files or directories for RBAC and audit log compliance. **Fix every issue found immediately.**
+
+## Rules
+
+### API Endpoints (NestJS — `apps/api/src/`)
+1. **Every mutation endpoint** (POST, PATCH, PUT, DELETE) MUST have `@RequirePermission('resource', 'action')`. If missing, **add it**.
+2. **Read endpoints** (GET) should have `@RequirePermission('resource', 'read')`. If missing, **add it**.
+3. **Self-endpoints** (e.g., `/me/preferences`) may skip `@RequirePermission` — authentication via `HybridAuthGuard` is sufficient.
+4. **Controller format**: Must use `@Controller({ path: 'name', version: '1' })`, NOT `@Controller('v1/name')`. If wrong, **fix it**.
+5. **Guards**: Use `@UseGuards(HybridAuthGuard, PermissionGuard)` at controller or endpoint level. Never skip PermissionGuard.
+6. **Webhooks**: External webhook endpoints use `@Public()` — no auth required.
+
+### Frontend Components (`apps/app/src/`)
+1. **Every mutation element** (button, form submit, toggle, switch, file upload) MUST be gated with `usePermissions` from `@/hooks/use-permissions`. If not:
+   - **Create/Add buttons**: Wrap with `{hasPermission('resource', 'create') && <Button>...`
+   - **Edit/Delete in dropdown menus**: Wrap the menu item
+   - **Inline form fields on detail pages**: Add `disabled={!canUpdate}`
+   - **Status/property selectors**: Add `disabled={!canUpdate}`
+2. **Actions columns** in tables: hide entire column when user lacks write permission.
+3. **No manual role string parsing** (`role.includes('admin')`) — use `hasPermission()`.
+4. **Nav items**: gate with `canAccessRoute(permissions, 'routeSegment')`.
+5. **Page-level**: call `requireRoutePermission('segment', orgId)` server-side.
+
+### Permission Resources
+`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`
+
+### Multi-Product RBAC
+- Products (compliance, pen testing) are org-level feature flags — NOT RBAC
+- `app:read` gates compliance dashboard; `pentest:read` gates security product
+- Custom roles can grant access to any combination of resources
+- Portal-only resources (`policy`, `compliance`) do NOT grant app access
+
+## Process
+1. Read files specified in `$ARGUMENTS` (or scan the directory)
+2. Check each rule above
+3. **Fix every violation immediately** — don't just report
+4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app`
diff --git a/.agents/skills/audit-tests/SKILL.md b/.agents/skills/audit-tests/SKILL.md
@@ -0,0 +1,30 @@
+---
+name: audit-tests
+description: Audit & fix unit tests for permission-gated components
+---
+
+Check that unit tests exist and pass for permission-gated components. **Write missing tests immediately.**
+
+## Infrastructure
+- **Framework**: Vitest with jsdom
+- **Component testing**: `@testing-library/react` + `@testing-library/jest-dom`
+- **Setup**: `apps/app/src/test-utils/setup.ts`
+- **Permission mocks**: `apps/app/src/test-utils/mocks/permissions.ts`
+- **Run**: `cd apps/app && bunx vitest run`
+
+## Required Test Pattern
+
+Every component importing `usePermissions` MUST have tests covering:
+
+1. **Admin (write) user**: mutation elements visible/enabled
+2. **Auditor (read-only)**: mutation elements hidden/disabled
+3. **Data always visible**: read-only content renders regardless of permissions
+
+Use `setMockPermissions`, `ADMIN_PERMISSIONS`, `AUDITOR_PERMISSIONS` from test utils.
+
+## Process
+1. Find components with `usePermissions` in `$ARGUMENTS`
+2. Check for corresponding `.test.tsx` files
+3. Write missing tests following the pattern above
+4. Fix any failing tests
+5. Run: `cd apps/app && bunx vitest run`
diff --git a/.agents/skills/better-auth-best-practices/SKILL.md b/.agents/skills/better-auth-best-practices/SKILL.md
@@ -11,11 +11,11 @@ description: Configure Better Auth server and client, set up database adapters,
 
 ## Setup Workflow
 
-1. Install: `npm install better-auth`
+1. Install: `bun add better-auth`
 2. Set env vars: `BETTER_AUTH_SECRET` and `BETTER_AUTH_URL`
 3. Create `auth.ts` with database + config
 4. Create route handler for your framework
-5. Run `npx @better-auth/cli@latest migrate`
+5. Run `bunx @better-auth/cli@latest migrate`
 6. Verify: call `GET /api/auth/ok` — should return `{ status: "ok" }`
 
 ---
@@ -32,9 +32,9 @@ Only define `baseURL`/`secret` in config if env vars are NOT set.
 CLI looks for `auth.ts` in: `./`, `./lib`, `./utils`, or under `./src`. Use `--config` for custom path.
 
 ### CLI Commands
-- `npx @better-auth/cli@latest migrate` - Apply schema (built-in adapter)
-- `npx @better-auth/cli@latest generate` - Generate schema for Prisma/Drizzle
-- `npx @better-auth/cli mcp --cursor` - Add MCP to AI tools
+- `bunx @better-auth/cli@latest migrate` - Apply schema (built-in adapter)
+- `bunx @better-auth/cli@latest generate` - Generate schema for Prisma/Drizzle
+- `bunx @better-auth/cli@latest mcp --cursor` - Add MCP to AI tools
 
 **Re-run after adding/changing plugins.**
 
@@ -172,4 +172,4 @@ For separate client/server projects: `createAuthClient<typeof auth>()`.
 - [Options Reference](https://better-auth.com/docs/reference/options)
 - [LLMs.txt](https://better-auth.com/llms.txt)
 - [GitHub](https://github.com/better-auth/better-auth)
-- [Init Options Source](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)
\ No newline at end of file
+- [Init Options Source](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)
diff --git a/.agents/skills/code/SKILL.md b/.agents/skills/code/SKILL.md
@@ -0,0 +1,185 @@
+---
+name: code
+description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"
+---
+
+Source Cursor rule: `.cursor/rules/code.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Code Standards
+
+## TypeScript
+
+### No `any`, No Unsafe Casts
+
+```tsx
+// ✅ Validate with zod
+const TaskSchema = z.object({ id: z.string(), title: z.string() });
+const task = TaskSchema.parse(response.data);
+
+// ✅ Use unknown and narrow
+const parseResponse = (data: unknown): Task => {
+  if (!isTask(data)) throw new Error('Invalid');
+  return data;
+};
+
+// ❌ Never
+const data: any = fetchData();
+const task = response as Task;
+const name = user!.name;
+// @ts-ignore
+```
+
+### Generics Over Any
+
+```tsx
+// ✅ Generic
+const first = <T>(items: T[]): T | undefined => items[0];
+
+// ❌ Any
+const first = (items: any[]): any => items[0];
+```
+
+## React Patterns
+
+### Named Exports, PascalCase
+
+```tsx
+// ✅ Named export, PascalCase file
+// TaskCard.tsx
+export function TaskCard({ task }: TaskCardProps) { ... }
+
+// ❌ Default export, lowercase
+export default function taskCard() { ... }
+```
+
+### Derive State, Avoid useEffect
+
+```tsx
+// ✅ Derived
+const completedCount = tasks.filter(t => t.completed).length;
+
+// ❌ Synced state
+const [count, setCount] = useState(0);
+useEffect(() => {
+  setCount(tasks.filter(t => t.completed).length);
+}, [tasks]);
+```
+
+### When useEffect IS Appropriate
+
+```tsx
+// External subscriptions
+useEffect(() => {
+  const sub = eventSource.subscribe(handler);
+  return () => sub.unsubscribe();
+}, []);
+
+// DOM measurements
+useEffect(() => {
+  setHeight(ref.current?.getBoundingClientRect().height);
+}, []);
+```
+
+### Toasts with Sonner
+
+```tsx
+import { toast } from 'sonner';
+
+toast.success('Task created');
+toast.error('Failed to save');
+toast.promise(saveTask(), {
+  loading: 'Saving...',
+  success: 'Saved!',
+  error: 'Failed',
+});
+```
+
+## File Structure
+
+### Colocate at Route Level
+
+```
+app/(app)/[orgId]/tasks/
+├── page.tsx              # Server component
+├── components/
+│   └── TaskList.tsx      # Client component
+├── hooks/
+│   └── useTasks.ts       # SWR hook
+└── data/
+    └── queries.ts        # Server queries
+```
+
+### Share Only When Reused 3+ Times
+
+```
+src/components/shared/    # Cross-page components
+src/hooks/                # Shared hooks (useApiSWR, useDebounce)
+```
+
+## Code Quality
+
+### File Size Limit: 300 Lines
+
+Split large files into focused components.
+
+### Named Parameters for 2+ Args
+
+```tsx
+// ✅ Named
+const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };
+createTask({ title: 'Review PR', assigneeId: user.id });
+
+// ❌ Positional
+const createTask = (title: string, assigneeId: string) => { ... };
+createTask('Review PR', user.id); // What's the 2nd param?
+```
+
+### Early Returns
+
+```tsx
+// ✅ Early return
+function processTask(task: Task | null) {
+  if (!task) return null;
+  if (task.deleted) return null;
+  return <TaskCard task={task} />;
+}
+
+// ❌ Nested
+function processTask(task) {
+  if (task) {
+    if (!task.deleted) {
+      return <TaskCard task={task} />;
+    }
+  }
+  return null;
+}
+```
+
+### Event Handler Naming
+
+```tsx
+// ✅ Prefix with "handle"
+const handleClick = () => { ... };
+const handleSubmit = (e: FormEvent) => { ... };
+const handleTaskCreate = (task: Task) => { ... };
+```
+
+## Accessibility
+
+```tsx
+// Interactive elements need keyboard support
+<div
+  role="button"
+  tabIndex={0}
+  onClick={handleClick}
+  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
+  aria-label="Delete task"
+>
+  <TrashIcon />
+</div>
+
+// Form inputs need labels
+<label htmlFor="task-name">Task Name</label>
+<input id="task-name" type="text" />
+```
diff --git a/.agents/skills/cursor-usage/SKILL.md b/.agents/skills/cursor-usage/SKILL.md
@@ -0,0 +1,269 @@
+---
+name: cursor-usage
+description: "How to write and manage Cursor rules - invoke with @cursor-usage"
+---
+
+Source Cursor rule: `.cursor/rules/cursor-usage.mdc`.
+Original file scope: `.cursor/rules/*.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Using Cursor Rules
+
+## Overview
+
+Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdown with frontmatter) files.
+
+## Rule File Structure
+
+Each `.mdc` rule file consists of two parts:
+
+### 1. Frontmatter (YAML metadata)
+
+```yaml
+---
+description: Brief overview of what this rule enforces
+globs: **/*.{ts,tsx}
+alwaysApply: true
+---
+```
+
+**Frontmatter Fields:**
+
+- `description`: A clear, concise explanation of the rule's purpose
+- `globs`: Glob pattern to match files where this rule should apply (plain string, no quotes or arrays)
+  - Examples:
+    - `**/*.tsx` - All TSX files
+    - `**/*.{ts,tsx}` - All TS and TSX files
+    - `apps/*/components/**/*.tsx` - All TSX files in any app's components directory
+    - `**/trigger/**/*.ts` - All TS files in trigger directories
+- `alwaysApply`: Boolean indicating if the rule should always be active
+  - `true`: Rule is always active when working on matching files
+  - `false`: Rule can be selectively invoked with `@rule-name`
+
+### 2. Content (Markdown)
+
+The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.
+
+## How Rules Are Applied
+
+### Automatic Application
+
+Rules with `alwaysApply: true` are automatically loaded when:
+
+- You open a file matching the `globs` pattern
+- You're working on code that matches the pattern
+- Cursor AI generates or suggests code for matching files
+
+### Manual Invocation
+
+You can reference specific rules in your prompts:
+
+```
+@design-system create a new button component
+```
+
+This explicitly tells Cursor to apply the design-system rule.
+
+## Best Practices for Writing Rules
+
+### 1. Keep Rules Focused
+
+- Each rule file should cover a specific domain (e.g., design system, API patterns, testing)
+- Avoid mixing unrelated concerns in a single rule file
+- Aim for rules under 500 lines for better AI comprehension
+
+### 2. Provide Concrete Examples
+
+Always include:
+
+- ✅ Good examples (what TO do)
+- ❌ Bad examples (what NOT to do)
+- Real code snippets from your project
+
+```tsx
+// ✅ Good: Use semantic tokens
+<div className="bg-background text-foreground">Content</div>
+
+// ❌ Bad: Hardcoded colors
+<div className="bg-white text-black">Content</div>
+```
+
+### 3. Use Clear Section Headers
+
+Organize content with descriptive headers:
+
+```markdown
+## Core Principles
+
+## Rules
+
+## Examples
+
+## Exceptions
+
+## Common Mistakes
+```
+
+### 4. Define Exceptions Explicitly
+
+If there are cases where rules don't apply, state them clearly:
+
+```markdown
+## Exceptions
+
+The ONLY time you can pass className to a design system component is for:
+
+1. Width utilities: `w-full`, `max-w-md`
+2. Responsive display: `hidden`, `md:block`
+```
+
+### 5. Include Checklists
+
+Provide actionable checklists for validation:
+
+```markdown
+## Code Review Checklist
+
+Before committing:
+
+- [ ] Uses semantic color tokens
+- [ ] Works in both light and dark mode
+- [ ] Fully responsive
+```
+
+## Managing Rules
+
+### Creating a New Rule
+
+1. Create a new `.mdc` file in `.cursor/rules/`
+2. Add appropriate frontmatter
+3. Write clear guidelines with examples
+4. Test by working on matching files
+
+### Updating Existing Rules
+
+1. Edit the `.mdc` file
+2. Rules are automatically reloaded
+3. Test changes with relevant files
+
+### Organizing Rules
+
+Recommended structure:
+
+```
+.cursor/rules/
+├── design-system.mdc       # Component usage, variants, composition
+├── code-standards.mdc      # General code quality rules
+├── typescript-rules.mdc    # TypeScript type safety
+├── react-code.mdc          # React patterns and conventions
+├── data-fetching.mdc       # Server/client data patterns
+└── cursor-usage.mdc        # This file - how to use rules
+```
+
+## Rule Scope with Globs
+
+### Common Glob Patterns
+
+```yaml
+# All TypeScript/TSX files
+globs: **/*.{ts,tsx}
+
+# Only TSX files (React components)
+globs: **/*.tsx
+
+# Only trigger task files
+globs: **/trigger/**/*.ts
+
+# Prisma schema files
+globs: **/*.prisma
+
+# All JSON and TypeScript files
+globs: **/*.{ts,tsx,json}
+```
+
+### Glob Pattern Tips
+
+- Use `**` for recursive directory matching
+- Use `*` for single-level wildcard
+- Use `{ts,tsx}` for multiple extensions
+- No quotes or array brackets needed
+- Be specific to avoid over-applying rules
+
+## Debugging Rules
+
+### Rule Not Applying?
+
+1. Check the `globs` pattern matches your file
+2. Verify frontmatter YAML syntax is correct
+3. Ensure `alwaysApply` is set appropriately
+4. Try manually invoking with `@ruleName`
+
+### Rule Conflicting?
+
+1. Check if multiple rules apply to the same files
+2. Make rules more specific with tighter `globs`
+3. Consolidate related rules into one file
+
+## Advanced Features
+
+### Conditional Rules
+
+Use `alwaysApply: false` for rules that should only apply in specific contexts:
+
+```yaml
+---
+description: Performance optimization guidelines
+globs: **/*.ts
+alwaysApply: false
+---
+```
+
+Invoke with: `@performance-optimization refactor this component`
+
+### Hierarchical Rules
+
+More specific globs take precedence:
+
+- `design-system.mdc` with `globs: **/*.tsx` (broad)
+- `trigger.basic.mdc` with `globs: **/trigger/**/*.ts` (specific)
+
+The specific rule will have more weight for trigger files.
+
+## Quick Reference
+
+### Create a New Rule
+
+```bash
+touch .cursor/rules/my-new-rule.mdc
+```
+
+```yaml
+---
+description: What this rule enforces
+globs: **/*.{ts,tsx}
+alwaysApply: true
+---
+
+# Rule Title
+
+## Guidelines
+
+- Point 1
+- Point 2
+```
+
+### Apply a Rule
+
+- Automatic: Save a file matching the `globs` pattern
+- Manual: Use `@my-new-rule` in your prompt
+
+### Debug a Rule
+
+1. Check file matches `globs` pattern
+2. Verify YAML frontmatter syntax
+3. Look for conflicting rules
+4. Try manual invocation
+
+---
+
+**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly.
diff --git a/.agents/skills/data/SKILL.md b/.agents/skills/data/SKILL.md
@@ -0,0 +1,146 @@
+---
+name: data
+description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"
+---
+
+Source Cursor rule: `.cursor/rules/data.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Data Fetching
+
+## Core Pattern: Server → Client → SWR
+
+### 1. Server Page Fetches Data
+
+```tsx
+// app/(app)/[orgId]/tasks/page.tsx
+export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {
+  const { orgId } = await params; // From URL, NOT session
+  const tasks = await getTasks(orgId);
+  return <TaskListClient organizationId={orgId} initialTasks={tasks} />;
+}
+```
+
+### 2. Client Component Receives Initial Data
+
+```tsx
+// components/TaskListClient.tsx
+'use client';
+
+export function TaskListClient({ organizationId, initialTasks }: Props) {
+  const { tasks, createTask, updateTask } = useTasks({
+    organizationId,
+    initialData: initialTasks,
+  });
+  // Initial render is instant - no loading state
+}
+```
+
+### 3. SWR Hook with fallbackData
+
+```tsx
+// hooks/useTasks.ts
+export function useTasks({ organizationId, initialData }: UseTasksOptions) {
+  const { data, mutate } = useSWR(
+    ['/v1/tasks', organizationId], // Include orgId for cache isolation
+    async ([endpoint, orgId]) => {
+      const response = await apiClient.get(endpoint, orgId);
+      return response.data?.tasks ?? [];
+    },
+    { fallbackData: initialData }
+  );
+
+  const createTask = async (input: CreateTaskInput) => {
+    await apiClient.post('/v1/tasks', input, organizationId);
+    mutate(); // Revalidate
+  };
+
+  const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {
+    await apiClient.put(`/v1/tasks/${taskId}`, input, organizationId);
+    mutate(); // Revalidate
+  };
+
+  return { tasks: data ?? [], createTask, updateTask, mutate };
+}
+```
+
+## API Client
+
+Use `apiClient` from `@/lib/api-client`:
+
+```tsx
+import { apiClient } from '@/lib/api-client';
+
+await apiClient.get<ResponseType>('/v1/endpoint', organizationId);
+await apiClient.post<ResponseType>('/v1/endpoint', body, organizationId);
+await apiClient.put<ResponseType>('/v1/endpoint', body, organizationId);
+await apiClient.delete('/v1/endpoint', organizationId);
+```
+
+## Server vs Client Components
+
+**Layouts = server.** Interactive logic in separate client components.
+
+```tsx
+// layout.tsx (server)
+export default function Layout({ children }) {
+  return (
+    <PageLayout>
+      <PageHeader title="Title" />
+      <ClientTabs /> {/* Client component */}
+      {children}
+    </PageLayout>
+  );
+}
+
+// components/ClientTabs.tsx
+'use client';
+export function ClientTabs() {
+  const router = useRouter();
+  // Interactive logic here
+}
+```
+
+## State Management
+
+**No `nuqs`** - use React state or Next.js patterns:
+
+```tsx
+// ✅ React state for UI
+const [isOpen, setIsOpen] = useState(false);
+
+// ✅ Next.js for URL state
+const router = useRouter();
+const searchParams = useSearchParams();
+
+// ❌ No nuqs
+import { useQueryState } from 'nuqs';
+```
+
+## Rules
+
+```tsx
+// ✅ Always
+const { orgId } = await params;                    // From URL params
+const { data } = useSWR(key, f, { fallbackData }); // With initial data
+await apiClient.get('/v1/endpoint', orgId);        // Use apiClient
+useSWR(['/v1/tasks', orgId], fetcher);            // Include orgId in key
+
+// ❌ Never
+const orgId = session?.activeOrganizationId;       // From session
+const { data } = useSWR('/api/data');              // No initial data
+await fetch('/api/endpoint');                      // Direct fetch
+```
+
+## File Structure
+
+```
+app/(app)/[orgId]/tasks/
+├── page.tsx                 # Server - fetches data
+├── components/
+│   └── TaskListClient.tsx   # Client - receives initialData
+├── hooks/
+│   └── useTasks.ts          # SWR hook with mutations
+└── data/
+    └── queries.ts           # Server-side queries
+```
diff --git a/.agents/skills/essentials/SKILL.md b/.agents/skills/essentials/SKILL.md
@@ -0,0 +1,108 @@
+---
+name: essentials
+description: "Critical rules that must always be followed"
+---
+
+Source Cursor rule: `.cursor/rules/essentials.mdc`.
+Original file scope: `**/*.{ts,tsx}`.
+Original Cursor alwaysApply: `true`.
+
+# Essentials
+
+## Package Manager
+
+Use `bun`, never npm/yarn/pnpm.
+
+```bash
+bun install          # Install deps
+bun add <pkg>        # Add package
+bun run <script>     # Run script
+bunx <cmd>           # Execute binary
+```
+
+## Components
+
+**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.
+
+```tsx
+// ✅ Design system
+import { Button, Card, Input, Select } from '@trycompai/design-system';
+import { Add, Close } from '@trycompai/design-system/icons';
+
+// ❌ Don't use when DS has the component
+import { Button } from '@trycompai/ui/button';
+import { Plus } from 'lucide-react';
+```
+
+**No `className` on DS components** - use variants and props only.
+
+```tsx
+// ✅ Use variants
+<Button variant="destructive" size="sm">Delete</Button>
+
+// ❌ No className overrides
+<Button className="bg-red-500">Delete</Button>
+```
+
+## TypeScript
+
+**No `any`. No unsafe type assertions.**
+
+```tsx
+// ✅ Validate external data with zod
+const TaskSchema = z.object({ id: z.string(), title: z.string() });
+const task = TaskSchema.parse(response.data);
+
+// ❌ Never
+const data: any = fetchData();
+const task = response as Task;
+```
+
+## Data Fetching
+
+**Get `organizationId` from URL params, not session.**
+
+```tsx
+// ✅ From params
+export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {
+  const { orgId } = await params;
+}
+
+// ❌ Not from session
+const session = await auth.api.getSession();
+const orgId = session?.session?.activeOrganizationId;
+```
+
+**Server components fetch, pass to client with SWR `fallbackData`.**
+
+```tsx
+// Server page
+const data = await fetchData(orgId);
+return <ClientComponent initialData={data} />;
+
+// Client component
+const { data } = useSWR(key, fetcher, { fallbackData: initialData });
+```
+
+## State Management
+
+**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.
+
+```tsx
+// ✅ React state for UI
+const [isOpen, setIsOpen] = useState(false);
+
+// ❌ No nuqs
+import { useQueryState } from 'nuqs';
+```
+
+## After Changes
+
+**Always run checks after code changes:**
+
+```bash
+bun run typecheck
+bun run lint
+```
+
+Fix all errors before committing.
diff --git a/.agents/skills/forms/SKILL.md b/.agents/skills/forms/SKILL.md
@@ -0,0 +1,180 @@
+---
+name: forms
+description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"
+---
+
+Source Cursor rule: `.cursor/rules/forms.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Forms: React Hook Form + Zod
+
+**All forms MUST use React Hook Form with Zod validation.**
+
+## Basic Pattern
+
+```tsx
+import { zodResolver } from '@hookform/resolvers/zod';
+import { useForm } from 'react-hook-form';
+import { z } from 'zod';
+import { Button, Input } from '@trycompai/design-system';
+
+// 1. Define schema
+const formSchema = z.object({
+  email: z.string().email('Invalid email'),
+  password: z.string().min(8, 'Min 8 characters'),
+});
+
+// 2. Infer type
+type FormData = z.infer<typeof formSchema>;
+
+// 3. Use in component
+function MyForm() {
+  const {
+    register,
+    handleSubmit,
+    formState: { errors, isSubmitting },
+  } = useForm<FormData>({
+    resolver: zodResolver(formSchema),
+  });
+
+  return (
+    <form onSubmit={handleSubmit(onSubmit)}>
+      <Input {...register('email')} />
+      {errors.email && <p>{errors.email.message}</p>}
+      
+      <Button type="submit" loading={isSubmitting}>
+        Submit
+      </Button>
+    </form>
+  );
+}
+```
+
+## Zod Schema Patterns
+
+```tsx
+const profileSchema = z.object({
+  // Strings
+  name: z.string().min(1, 'Required'),
+  email: z.string().email(),
+  website: z.string().url().optional(),
+  
+  // Numbers (coerce for inputs)
+  age: z.coerce.number().int().min(0),
+  price: z.coerce.number().positive(),
+  
+  // Arrays
+  tags: z.array(z.string()).min(1),
+  
+  // Enums
+  status: z.enum(['active', 'inactive']),
+});
+
+// Cross-field validation
+const passwordSchema = z.object({
+  password: z.string().min(8),
+  confirmPassword: z.string(),
+}).refine(d => d.password === d.confirmPassword, {
+  message: "Passwords don't match",
+  path: ['confirmPassword'],
+});
+```
+
+## Controller for Complex Components
+
+```tsx
+import { Controller } from 'react-hook-form';
+import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';
+
+<Controller
+  name="status"
+  control={control}
+  render={({ field }) => (
+    <Select onValueChange={field.onChange} value={field.value}>
+      <SelectTrigger>{field.value || 'Select...'}</SelectTrigger>
+      <SelectContent>
+        <SelectItem value="active">Active</SelectItem>
+        <SelectItem value="inactive">Inactive</SelectItem>
+      </SelectContent>
+    </Select>
+  )}
+/>
+```
+
+## Form State
+
+```tsx
+const {
+  register,
+  handleSubmit,
+  control,
+  watch,           // Watch field values
+  setValue,        // Set field programmatically
+  reset,           // Reset form
+  setError,        // Set error manually
+  formState: {
+    errors,        // Field errors
+    isSubmitting,  // Submitting
+    isValid,       // All valid
+    isDirty,       // Modified
+  },
+} = useForm<FormData>({
+  resolver: zodResolver(schema),
+  mode: 'onChange', // Validate on change
+});
+```
+
+## Error Handling
+
+```tsx
+const onSubmit = async (data: FormData) => {
+  try {
+    await submitToApi(data);
+  } catch (error) {
+    // Field-specific error
+    setError('email', { message: 'Email taken' });
+    // Or root error
+    setError('root', { message: 'Something went wrong' });
+  }
+};
+
+// Display root error
+{errors.root && <p>{errors.root.message}</p>}
+```
+
+## Dynamic Fields
+
+```tsx
+import { useFieldArray } from 'react-hook-form';
+
+const { fields, append, remove } = useFieldArray({
+  control,
+  name: 'items',
+});
+
+{fields.map((field, index) => (
+  <div key={field.id}>
+    <Input {...register(`items.${index}.name`)} />
+    <Button type="button" onClick={() => remove(index)}>Remove</Button>
+  </div>
+))}
+<Button type="button" onClick={() => append({ name: '' })}>Add</Button>
+```
+
+## Anti-Patterns
+
+```tsx
+// ❌ useState for form fields
+const [email, setEmail] = useState('');
+
+// ❌ Manual validation
+if (email.length < 5) setError('Too short');
+
+// ❌ Missing button type (defaults to submit)
+<Button onClick={handleCancel}>Cancel</Button>
+
+// ✅ Correct
+const { register } = useForm();
+const schema = z.object({ email: z.string().min(5) });
+<Button type="button" onClick={handleCancel}>Cancel</Button>
+```
diff --git a/.agents/skills/infra/SKILL.md b/.agents/skills/infra/SKILL.md
@@ -0,0 +1,135 @@
+---
+name: infra
+description: "Use when working with packages, dependencies, monorepo structure, or build configuration"
+---
+
+Source Cursor rule: `.cursor/rules/infra.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Infrastructure
+
+## Package Manager
+
+**Use `bun`, never npm/yarn/pnpm.**
+
+```bash
+bun install              # Install deps
+bun add <pkg>            # Add package
+bun add -D <pkg>         # Add dev dependency
+bun run <script>         # Run script
+bunx <cmd>               # Execute binary
+```
+
+## Monorepo Structure
+
+```
+comp/
+├── apps/
+│   ├── api/             # NestJS backend
+│   ├── app/             # Next.js main app
+│   └── portal/          # Next.js portal
+├── packages/
+│   ├── db/              # Prisma (@trycompai/db)
+│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system
+│   └── ...
+├── turbo.json
+└── package.json
+```
+
+## Running Commands
+
+```bash
+# Multi-package (via turbo)
+bun run build            # Build all
+bun run lint             # Lint all
+bun run typecheck        # Type check all
+bun run dev              # Dev all
+
+# Single package
+bun run -F apps/app dev
+bun run -F @trycompai/db prisma:generate
+turbo build --filter=@trycompai/ui
+```
+
+## Importing Between Packages
+
+```tsx
+// ✅ Import from package name
+import { Button } from '@trycompai/design-system';
+import { prisma } from '@trycompai/db';
+
+// ❌ Never relative paths across packages
+import { Button } from '../../../packages/ui/src/button';
+```
+
+## Adding Dependencies
+
+```bash
+# To specific package
+bun add axios -F apps/app
+bun add -D vitest -F @trycompai/ui
+
+# To root (dev tools only)
+bun add -D -w prettier typescript
+```
+
+## After Code Changes
+
+**Always run checks:**
+
+```bash
+bun run typecheck
+bun run lint
+```
+
+Fix all errors before committing.
+
+## Common TypeScript Fixes
+
+- **Property does not exist**: Check interface definitions
+- **Type mismatch**: Verify expected vs actual type
+- **Empty interface extends**: Use `type X = SomeType` instead
+
+## Common ESLint Fixes
+
+- **Unused variables**: Remove or prefix with `_`
+- **Any type**: Add proper typing
+- **Empty object type**: Use `type` instead of `interface`
+
+## Creating a New Package
+
+```bash
+mkdir packages/my-package
+```
+
+```json
+// packages/my-package/package.json
+{
+  "name": "@trycompai/my-package",
+  "version": "0.0.0",
+  "private": true,
+  "main": "./src/index.ts",
+  "scripts": {
+    "build": "tsup src/index.ts --format cjs,esm --dts",
+    "typecheck": "tsc --noEmit"
+  }
+}
+```
+
+```json
+// packages/my-package/tsconfig.json
+{
+  "extends": "@trycompai/tsconfig/base.json",
+  "include": ["src"]
+}
+```
+
+## Package Boundaries
+
+**✅ Create packages for:**
+- Code used by 2+ apps
+- Self-contained, focused functionality
+
+**❌ Don't create packages for:**
+- Code only used in one app (colocate instead)
+- App-specific business logic
diff --git a/.agents/skills/new-feature-setup/SKILL.md b/.agents/skills/new-feature-setup/SKILL.md
@@ -0,0 +1,114 @@
+---
+name: new-feature-setup
+description: Use when starting a new feature, Linear ticket, or bugfix in this repo — establishes the branch + worktree + env + DB + dev-server conventions so the work is immediately ready to code without fighting infra. Triggers on "start a new feature", "spin up a worktree", "begin ticket", "new branch".
+---
+
+# New Feature Setup (comp monorepo)
+
+## Overview
+
+This repo has a lot of infrastructure pre-wired into `git worktree add`. Use it. Don't reinvent env copying, database setup, or dependency install flows in every new session.
+
+## When to Use
+
+- User says "start a new feature", "spin up a worktree for X", "begin this Linear ticket", "new branch for …"
+- Before running `bun install` / `bun run db:generate` manually in a new directory
+- Before copying `.env` files around by hand
+
+## When NOT to Use
+
+- User is editing an existing worktree (already set up)
+- Infra repair / debugging of the hook itself (read `.githooks/README.md` instead)
+
+## Workflow
+
+### 1. Create the worktree from `origin/main`
+
+```sh
+cd /Users/mariano/code/comp   # must be the MAIN clone, not another worktree
+git fetch origin main
+git worktree add .worktrees/<short-slug> -b <branch-name> origin/main
+```
+
+- For Linear tickets, use Linear's suggested branch name (`mariano/<ticket-slug>`).
+- For infra / chore work, use `mariano/<short-descriptive-name>` or `chore/<topic>`.
+- The `<short-slug>` on the worktree path should match the branch's suffix (it becomes the Postgres DB slug after `tr '-' '_'`).
+
+### 2. Let the hook do everything else
+
+`git worktree add` fires the `post-checkout` hook at `.githooks/post-checkout`, which runs synchronously:
+
+1. Creates `compdev_<slug>` Postgres database (isolated per worktree)
+2. Links `.env*` files from the main clone (copies the ones with `DATABASE_URL`, rewriting it to the isolated URL; symlinks the rest so API keys auto-propagate)
+3. Runs `bun install`, applies Prisma migrations, regenerates clients
+
+**Do not** run any of these by hand. If the hook logs a failure, diagnose and fix at the source — don't paper over with a manual install.
+
+Skip toggles (rare):
+- `SKIP_WORKTREE_DB=1` — share the main `comp` DB (drift risk; only for read-only worktrees)
+- `SKIP_WORKTREE_SETUP=1` — skip install + migrate + generate (for a "just files" worktree)
+- `SETUP_WORKTREE_WITH_BUILD=1` — also run `bun run build` (adds minutes; only when you need the built artifacts)
+
+### 3. Start the dev server — coordinate with the "active worktree" rule
+
+Trigger.dev's `trigger dev` CLI **cannot** be isolated per worktree. Running `bun run dev` in multiple worktrees stomps on task registration.
+
+- **One active worktree** runs `bun run dev` (full stack with `trigger dev`).
+- **All other worktrees** run:
+  ```sh
+  bun run --filter '@trycompai/app' dev:no-trigger    # Next.js only
+  bun run --filter '@trycompai/api' dev:no-trigger    # NestJS only
+  ```
+- Non-active worktrees need a different `PORT` to avoid collision — add `PORT=3001` (or `3334`, etc.) to the worktree's `.env.local`. `.env.local` is not symlinked and stays per-worktree.
+- When swapping which worktree is active, kill the old full `bun run dev` first so task registration is clean.
+
+### 4. Code the feature
+
+Standard repo conventions apply (see `AGENTS.md`). Highlights:
+- TDD for any non-trivial change (`superpowers:test-driven-development`)
+- Brainstorm before building new UX (`superpowers:brainstorming`)
+- Plans + subagent-driven execution for multi-step work
+- Run `audit-design-system` after any frontend component edit
+- Always run typecheck before declaring a change done (`bunx turbo run typecheck --filter=<pkg>`)
+
+### 5. When done, clean up
+
+Use the `stale-worktree-cleanup` skill when worktrees accumulate. It handles both `git worktree remove` and dropping the `compdev_<slug>` database in one pass. Never leave orphan databases — they pile up silently because git has no `pre-worktree-remove` hook.
+
+## Quick Reference
+
+```sh
+# Spin up a new worktree (does env + DB + install + migrate + generate automatically)
+git worktree add .worktrees/<slug> -b mariano/<branch-name> origin/main
+
+# Start dev — ONLY in the worktree you're actively iterating on
+cd .worktrees/<slug>
+bun run dev
+
+# Start dev in a background worktree (no trigger dev, custom port via .env.local)
+echo "PORT=3001" >> apps/app/.env.local
+bun run --filter '@trycompai/app' dev:no-trigger
+
+# Clean up when branch is done
+# (use the stale-worktree-cleanup skill)
+```
+
+## Red Flags
+
+If you catch yourself doing any of these, stop — the hook should have handled it:
+
+- Running `bun install` manually in a new worktree
+- `cp` or `ln -s` to copy `.env` files into a worktree
+- Writing a script that "creates a database for my branch"
+- Running `bun run db:migrate` in a worktree right after creating it
+- Ignoring a failing `bun run dev` in two worktrees instead of swapping to `dev:no-trigger`
+
+## Common Mistakes
+
+| Mistake | Fix |
+|---|---|
+| Creating the worktree from another worktree instead of the main clone | Always `cd` to `/Users/mariano/code/comp` first |
+| Editing `.env` in a worktree and expecting it to propagate | If it's a symlink, yes; if it's a real copy (has `DATABASE_URL`), no. Check with `ls -la`. |
+| Forgetting to bump `PORT` → two dev servers collide | Put `PORT=<free-port>` in the worktree's `.env.local` |
+| Running `trigger dev` in multiple worktrees | Switch to `dev:no-trigger` in all but one |
+| Not cleaning up → orphan `compdev_*` databases piling up | Use the `stale-worktree-cleanup` skill regularly |
diff --git a/.agents/skills/prisma/SKILL.md b/.agents/skills/prisma/SKILL.md
@@ -0,0 +1,148 @@
+---
+name: prisma
+description: "Prisma schema conventions and migration workflow"
+---
+
+Source Cursor rule: `.cursor/rules/prisma.mdc`.
+Original file scope: `**/*.prisma`.
+Original Cursor alwaysApply: `false`.
+
+# Prisma Schema
+
+## Migration Workflow
+
+**Schema changes happen in `packages/db`, then regenerate types in each app.**
+
+### Step 1: Edit Schema
+
+```bash
+# Schema files are in packages/db/prisma/schema/
+packages/db/prisma/schema/
+├── schema.prisma      # Main schema with datasource
+├── user.prisma        # User models
+├── task.prisma        # Task models
+└── ...
+```
+
+### Step 2: Create Migration
+
+```bash
+# Run from packages/db
+cd packages/db
+bunx prisma migrate dev --name your_migration_name
+```
+
+### Step 3: Regenerate Types in Apps
+
+```bash
+# Each app needs to regenerate Prisma client types
+bun run -F apps/app db:generate
+bun run -F apps/api db:generate
+bun run -F apps/portal db:generate
+
+# Or from root (if configured)
+bun run prisma:generate
+```
+
+### ✅ Always Do This
+
+```bash
+# 1. Make schema changes in packages/db
+# 2. Create migration
+cd packages/db && bunx prisma migrate dev --name add_user_role
+
+# 3. Regenerate types in ALL apps that use the db
+bun run -F apps/app db:generate
+bun run -F apps/api db:generate
+bun run -F apps/portal db:generate
+```
+
+### ❌ Never Do This
+
+```bash
+# Don't edit schema in app directories
+apps/app/prisma/schema.prisma  # ❌ Wrong location
+
+# Don't forget to regenerate types
+bunx prisma migrate dev  # ✅ Created migration
+# ... forgot to run db:generate in apps  # ❌ Types out of sync
+```
+
+## Core Rule
+
+**Always use prefixed CUIDs for IDs** using `generate_prefixed_cuid`.
+
+## ID Pattern
+
+### ✅ Always Do This
+
+```prisma
+model User {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('usr'::text)"))
+  // ... other fields
+}
+
+model Task {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('tsk'::text)"))
+  // ... other fields
+}
+
+model Organization {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('org'::text)"))
+  // ... other fields
+}
+```
+
+### ❌ Never Do This
+
+```prisma
+// Don't use UUID
+model User {
+  id String @id @default(uuid())
+}
+
+// Don't use auto-increment
+model User {
+  id Int @id @default(autoincrement())
+}
+
+// Don't forget ::text cast
+model User {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('usr')")) // ❌ Missing ::text
+}
+```
+
+## Prefix Guidelines
+
+| Entity       | Prefix | Example ID                     |
+| ------------ | ------ | ------------------------------ |
+| User         | `usr`  | `usr_BJRIZLgRPuWt8MvMjkSY82f1` |
+| Organization | `org`  | `org_cK9xMnPqRs2tUvWx3yZa4b5c` |
+| Task         | `tsk`  | `tsk_dE6fGhIj7kLmNoP8qRsT9uVw` |
+| Control      | `ctl`  | `ctl_xY0zAaBb1cDdEe2fFgGh3iIj` |
+| Policy       | `pol`  | `pol_kK4lLmMn5oOpPq6rRsSt7uUv` |
+
+## Rules
+
+1. **Short prefixes** - Use 2-3 characters
+2. **Unique prefixes** - Each model gets its own prefix
+3. **Always cast** - Include `::text` in the function call
+4. **Use dbgenerated** - Wrap the function call in `dbgenerated()`
+
+## Benefits
+
+- Human-readable IDs at a glance (`usr_` vs `org_`)
+- Easy debugging in logs
+- Safe to expose in URLs
+- Unique across all tables
+
+## Checklist
+
+After schema changes:
+
+- [ ] Schema edited in `packages/db/prisma/schema/`
+- [ ] Migration created with `bunx prisma migrate dev`
+- [ ] Types regenerated in `apps/app` with `db:generate`
+- [ ] Types regenerated in `apps/api` with `db:generate`
+- [ ] Types regenerated in `apps/portal` with `db:generate`
+- [ ] New models use prefixed CUID IDs
diff --git a/.agents/skills/production-readiness/SKILL.md b/.agents/skills/production-readiness/SKILL.md
@@ -0,0 +1,21 @@
+---
+name: production-readiness
+description: Run all audit checks (RBAC, hooks, design system, tests) and verify build
+disable-model-invocation: true
+---
+
+Run a comprehensive production readiness check on $ARGUMENTS.
+
+Use parallel subagents to run all four audits simultaneously:
+1. audit-rbac on $ARGUMENTS
+2. audit-hooks on $ARGUMENTS
+3. audit-design-system on $ARGUMENTS
+4. audit-tests on $ARGUMENTS
+
+Then run full monorepo verification:
+```bash
+bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app
+cd apps/app && bunx vitest run
+```
+
+Output a Production Readiness Report summarizing all fixes applied and build status.
diff --git a/.agents/skills/prompt-engineering/SKILL.md b/.agents/skills/prompt-engineering/SKILL.md
@@ -0,0 +1,187 @@
+---
+name: prompt-engineering
+description: "Prompt engineering best practices - invoke with @prompt-engineering"
+---
+
+Source Cursor rule: `.cursor/rules/prompt-engineering.mdc`.
+Original file scope: `.cursor/rules/*.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Prompt Engineering Best Practices
+
+Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
+
+## Core Principles
+
+### 1. Define Success Criteria First
+
+Before writing prompts:
+
+- **Establish clear objectives**: What constitutes a successful response?
+- **Create evaluation metrics**: How will you measure prompt effectiveness?
+- **Draft and iterate**: Start with a first draft and refine based on results
+
+### 2. When to Use Prompt Engineering vs Fine-tuning
+
+Prompt engineering is preferred because:
+
+- **Resource efficient**: Only requires text input, no GPUs
+- **Cost effective**: Uses base model pricing
+- **Maintains updates**: Works across model versions
+- **Time saving**: Instant results vs hours/days for fine-tuning
+- **Minimal data needs**: Works with zero-shot or few-shot
+- **Flexible iteration**: Quick experimentation cycle
+- **Preserves knowledge**: No catastrophic forgetting
+- **Transparent**: Human-readable, easy to debug
+
+---
+
+## The 6 Core Techniques
+
+### 1. Be Clear and Direct
+
+**Principle**: Provide explicit, unambiguous instructions.
+
+```
+❌ Bad: "Tell me about it"
+✅ Good: "Summarize the following article in three bullet points, focusing on key findings"
+
+❌ Bad: "Help with code"
+✅ Good: "Debug this Python function that should return the sum of even numbers in a list"
+```
+
+**Tips**:
+
+- State the task explicitly at the start
+- Specify the desired output format (bullet points, JSON, paragraphs)
+- Include constraints (word count, tone, audience)
+- Mention what to include AND what to exclude
+
+### 2. Use Examples (Multishot Prompting)
+
+**Principle**: Show the model what you want through examples.
+
+```xml
+<examples>
+  <example>
+    <input>The movie was absolutely terrible, waste of time</input>
+    <output>{"sentiment": "negative", "confidence": 0.95}</output>
+  </example>
+  <example>
+    <input>Decent film, not great but watchable</input>
+    <output>{"sentiment": "neutral", "confidence": 0.7}</output>
+  </example>
+  <example>
+    <input>Best movie I've seen this year!</input>
+    <output>{"sentiment": "positive", "confidence": 0.9}</output>
+  </example>
+</examples>
+
+Now analyze: "The special effects were amazing but the plot was confusing"
+```
+
+**Tips**:
+
+- Include 3-5 diverse examples covering edge cases
+- Show examples of BOTH good and bad outputs
+- Match example complexity to your actual use case
+- Order examples from simple to complex
+
+### 3. Let Claude Think (Chain of Thought)
+
+**Principle**: Encourage step-by-step reasoning for complex tasks.
+
+```xml
+<instruction>
+Solve this problem step by step. Show your reasoning before giving the final answer.
+</instruction>
+
+<problem>
+A train leaves Station A at 9:00 AM traveling at 60 mph. Another train leaves
+Station B at 10:00 AM traveling at 80 mph toward Station A. The stations are
+280 miles apart. When will the trains meet?
+</problem>
+
+<thinking>
+[Let Claude work through the problem here]
+</thinking>
+
+<answer>
+[Final answer after reasoning]
+</answer>
+```
+
+**Tips**:
+
+- Use phrases like "Think step by step" or "Explain your reasoning"
+- For complex tasks, explicitly request a thinking section
+- Chain of thought improves accuracy on math, logic, and multi-step problems
+- Can use `<thinking>` tags to separate reasoning from output
+
+### 4. Use XML Tags
+
+**Principle**: Structure prompts with clear delimiters for better parsing.
+
+```xml
+<context>
+You are helping debug a penetration testing tool that automates security scans.
+</context>
+
+<task>
+Analyze the following error log and identify the root cause.
+</task>
+
+<error_log>
+[2024-01-15 10:23:45] ERROR: Connection timeout after 30s
+[2024-01-15 10:23:45] DEBUG: Target: 192.168.1.1:443
+[2024-01-15 10:23:45] DEBUG: Retry attempt 3 of 3
+</error_log>
+
+<output_format>
+Provide your analysis in this format:
+- Root cause: [one sentence]
+- Evidence: [relevant log lines]
+- Recommended fix: [actionable steps]
+</output_format>
+```
+
+**Common XML Tags**:
+
+- `<context>` - Background information
+- `<task>` or `<instruction>` - What to do
+- `<examples>` - Sample inputs/outputs
+- `<constraints>` - Limitations or rules
+- `<output_format>` - Expected response structure
+- `<thinking>` - Reasoning section
+- `<answer>` - Final response
+
+### 5. Give Claude a Role (System Prompts)
+
+**Principle**: Assign a persona to influence response style and expertise.
+
+```xml
+<role>
+You are a senior security researcher with 15 years of experience in penetration
+testing. You specialize in web application security and have discovered multiple
+CVEs. You communicate findings clearly and prioritize actionable recommendations.
+</role>
+
+<task>
+Review this HTTP response and identify potential security vulnerabilities.
+</task>
+```
+
+**Effective Role Elements**:
+
+- Expertise level (senior, expert, specialist)
+- Domain knowledge (security, finance, medicine)
+- Communication style (technical, friendly, formal)
+- Priorities (accuracy, brevity, thoroughness)
+
+### 6. Prefill Claude's Response
+
+**Principle**: Start the response to guide format and direction.
+
+```
+Human: List the top 3 security vulnerabilities in this code.
+```
diff --git a/.agents/skills/stale-worktree-cleanup/SKILL.md b/.agents/skills/stale-worktree-cleanup/SKILL.md
@@ -0,0 +1,174 @@
+---
+name: stale-worktree-cleanup
+description: Use when cleaning up old git worktrees, removing worktrees whose branches have merged or been abandoned, or dropping orphaned compdev_* Postgres databases. Triggers on "clean up worktrees", "delete stale worktrees", "worktrees piling up", "orphaned databases", "remove unused worktree".
+---
+
+# Stale Worktree Cleanup
+
+## Overview
+
+This repo's `.githooks/post-checkout` creates a per-worktree Postgres database (`compdev_<slug>`) on every `git worktree add`. Git has no `pre-worktree-remove` hook, so dead databases pile up over time. This skill defines a safe, reversible process to reap both the worktree directories and their dangling databases together.
+
+**Core principle**: never delete work the user might still want. Classify first, ask second, remove last.
+
+## When to Use
+
+- User says "clean up worktrees", "delete stale worktrees", "remove old worktrees", "worktrees piling up"
+- User mentions orphaned `compdev_*` DBs or running out of disk space from dead `node_modules`
+- Starting a new feature and noticing many old worktree dirs
+
+## When NOT to Use
+
+- User wants to remove ONE specific worktree (just run `git worktree remove <path>` + drop its DB directly — don't load the whole process)
+- User is actively working in a worktree (never touch active work)
+
+## Process
+
+### Step 1 — Inventory
+
+Run these four commands (parallel-safe) and capture the output:
+
+```sh
+git worktree list --porcelain
+gh pr list --author @me --state all --limit 50 --json headRefName,state,url,number
+git branch --no-color | cat
+```
+
+Then query the DB for `compdev_*` databases. The management URL is the main worktree's `DATABASE_URL` with the database path swapped to `postgres`:
+
+```sh
+bun -e '
+  import { Client } from "pg";
+  const raw = require("fs").readFileSync("packages/db/.env", "utf8");
+  const url = raw.match(/^DATABASE_URL=(.*)$/m)[1].replace(/^["\x27]|["\x27]$/g, "");
+  const mgmt = url.replace(/\/[^/?]+(\?|$)/, "/postgres$1");
+  const c = new Client({ connectionString: mgmt });
+  await c.connect();
+  const r = await c.query("SELECT datname FROM pg_database WHERE datname LIKE \x27compdev\\\\_%\x27 ORDER BY 1");
+  for (const row of r.rows) console.log(row.datname);
+  await c.end();
+'
+```
+
+### Step 2 — Classify each worktree
+
+For each worktree (skip the main one):
+
+| Signal | Classification |
+|---|---|
+| Branch merged to main AND clean working tree AND no unpushed commits | **safe** |
+| PR is `CLOSED` (not merged) | **needs-confirm** |
+| Uncommitted changes OR unpushed commits | **needs-confirm** |
+| No matching PR, no merge, has local commits | **keep** (user may still be working on it) |
+| Is the main worktree | **skip** |
+
+Gather per worktree:
+- `cd <path> && git status --porcelain | wc -l` — uncommitted changes count
+- `cd <path> && git log @{upstream}..HEAD --oneline 2>/dev/null | wc -l` — unpushed commits (0 if no upstream)
+- Branch → PR lookup from step 1
+
+### Step 3 — Present to user
+
+Show a table and explicit recommendations. Example:
+
+```
+Path                                    Branch                              PR state  Changes  Recommendation
+.worktrees/sale-45-…                    mariano/sale-45-…                   MERGED    0 / 0    ✅ safe to remove
+.worktrees/old-experiment               mariano/scratch                     —         3 / 0    ⚠ uncommitted — confirm first
+.worktrees/worktree-env-auto-link       mariano/worktree-env-auto-link      OPEN      0 / 0    ⏳ keep (PR open)
+
+Orphan databases (no worktree dir):
+  compdev_abandoned_feature
+  compdev_old_migration_test
+```
+
+Then ask: **"Remove the items marked ✅? Confirm by listing anything you want me to also nuke from the ⚠ / ⏳ set."**
+
+### Step 4 — Remove confirmed items
+
+For each worktree the user approved:
+
+```sh
+# 1. Remove the worktree dir (use --force only if user confirmed dirty-removal)
+git worktree remove "<path>"           # clean case
+git worktree remove --force "<path>"   # only after explicit user OK
+
+# 2. Derive the slug and drop the database
+slug=$(basename "<path>" | tr '[:upper:]' '[:lower:]' | tr '-' '_' | tr -cd 'a-z0-9_')
+bun -e '
+  import { Client } from "pg";
+  const raw = require("fs").readFileSync("packages/db/.env", "utf8");
+  const url = raw.match(/^DATABASE_URL=(.*)$/m)[1].replace(/^["\x27]|["\x27]$/g, "");
+  const mgmt = url.replace(/\/[^/?]+(\?|$)/, "/postgres$1");
+  const c = new Client({ connectionString: mgmt });
+  await c.connect();
+  await c.query(`DROP DATABASE IF EXISTS "compdev_'"$slug"'"`);
+  await c.end();
+  console.log("dropped compdev_'"$slug"'");
+'
+```
+
+For orphan databases (no matching worktree dir), just drop them — no worktree to remove.
+
+**Do NOT** delete the local branch unless the user explicitly asked. Branches can be recreated from `origin` cheaply; worktrees cannot.
+
+### Step 5 — Verify and report
+
+```sh
+git worktree list
+# then re-run the compdev_* query from step 1
+```
+
+Report back:
+- Worktrees removed (paths)
+- Databases dropped (names)
+- Anything skipped and why
+- What's left (still-active worktrees)
+
+## Safety Rules
+
+- **Never remove the main worktree.** Its path is always the first line of `git worktree list --porcelain`.
+- **Never `--force` without confirmation.** Dirty worktrees can contain un-stashed work.
+- **Never `DROP DATABASE` on anything not matching `^compdev_[a-z0-9_]+$`.** Never drop `comp`, `postgres`, or any production-looking name.
+- **Never delete a local branch** as part of cleanup unless the user explicitly asks. Orphaned branches are cheap; lost work isn't.
+- **Never run this inside a worktree you're about to delete.** `cd` to the main worktree first.
+
+## Common Mistakes
+
+| Mistake | Fix |
+|---|---|
+| Dropping the DB but leaving the worktree dir | Run `git worktree prune` then `git worktree remove` |
+| Removing the worktree but leaving the DB (accumulates orphans) | Always do both in the same pass |
+| Using hyphens in the DB name | The hook slug rule is `tr '-' '_'` — always underscores |
+| Running from inside a doomed worktree | `cd` to the main worktree before starting the process |
+| Using `gh pr list` on a branch with no PR | Missing data is not "abandoned" — needs `needs-confirm` classification |
+
+## Red Flags
+
+If any of these show up mid-process, **stop and ask the user**:
+
+- A worktree has unpushed commits AND no PR → might be unreleased work
+- The classification returned >10 "safe to remove" items → unusual volume, double-check
+- `git worktree remove` errors with "working tree is not clean" → never retry with `--force` without explicit consent
+- A `compdev_*` name has weird characters or unexpected format → don't drop
+
+## Quick Reference
+
+```sh
+# List everything
+git worktree list --porcelain
+gh pr list --author @me --state all --limit 50 --json headRefName,state
+
+# Per-worktree inspection
+git -C <path> status --porcelain
+git -C <path> log @{upstream}..HEAD --oneline 2>/dev/null
+
+# Clean removal
+git worktree remove <path>
+
+# Dirty removal (requires user confirmation first)
+git worktree remove --force <path>
+
+# Database drop (run from main worktree)
+# See the bun -e snippets above for the exact invocation
+```
diff --git a/.agents/skills/trigger-advanced-tasks/SKILL.md b/.agents/skills/trigger-advanced-tasks/SKILL.md
@@ -0,0 +1,460 @@
+---
+name: trigger-advanced-tasks
+description: "Comprehensive rules to help you write advanced Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.advanced-tasks.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Advanced Tasks (v4)
+
+**Advanced patterns and features for writing tasks**
+
+## Tags & Organization
+
+```ts
+import { task, tags } from '@trigger.dev/sdk';
+
+export const processUser = task({
+  id: 'process-user',
+  run: async (payload: { userId: string; orgId: string }, { ctx }) => {
+    // Add tags during execution
+    await tags.add(`user_${payload.userId}`);
+    await tags.add(`org_${payload.orgId}`);
+
+    return { processed: true };
+  },
+});
+
+// Trigger with tags
+await processUser.trigger(
+  { userId: '123', orgId: 'abc' },
+  { tags: ['priority', 'user_123', 'org_abc'] }, // Max 10 tags per run
+);
+
+// Subscribe to tagged runs
+for await (const run of runs.subscribeToRunsWithTag('user_123')) {
+  console.log(`User task ${run.id}: ${run.status}`);
+}
+```
+
+**Tag Best Practices:**
+
+- Use prefixes: `user_123`, `org_abc`, `video:456`
+- Max 10 tags per run, 1-128 characters each
+- Tags don't propagate to child tasks automatically
+
+## Concurrency & Queues
+
+```ts
+import { task, queue } from '@trigger.dev/sdk';
+
+// Shared queue for related tasks
+const emailQueue = queue({
+  name: 'email-processing',
+  concurrencyLimit: 5, // Max 5 emails processing simultaneously
+});
+
+// Task-level concurrency
+export const oneAtATime = task({
+  id: 'sequential-task',
+  queue: { concurrencyLimit: 1 }, // Process one at a time
+  run: async (payload) => {
+    // Critical section - only one instance runs
+  },
+});
+
+// Per-user concurrency
+export const processUserData = task({
+  id: 'process-user-data',
+  run: async (payload: { userId: string }) => {
+    // Override queue with user-specific concurrency
+    await childTask.trigger(payload, {
+      queue: {
+        name: `user-${payload.userId}`,
+        concurrencyLimit: 2,
+      },
+    });
+  },
+});
+
+export const emailTask = task({
+  id: 'send-email',
+  queue: emailQueue, // Use shared queue
+  run: async (payload: { to: string }) => {
+    // Send email logic
+  },
+});
+```
+
+## Error Handling & Retries
+
+```ts
+import { task, retry, AbortTaskRunError } from '@trigger.dev/sdk';
+
+export const resilientTask = task({
+  id: 'resilient-task',
+  retry: {
+    maxAttempts: 10,
+    factor: 1.8, // Exponential backoff multiplier
+    minTimeoutInMs: 500,
+    maxTimeoutInMs: 30_000,
+    randomize: false,
+  },
+  catchError: async ({ error, ctx }) => {
+    // Custom error handling
+    if (error.code === 'FATAL_ERROR') {
+      throw new AbortTaskRunError('Cannot retry this error');
+    }
+
+    // Log error details
+    console.error(`Task ${ctx.task.id} failed:`, error);
+
+    // Allow retry by returning nothing
+    return { retryAt: new Date(Date.now() + 60000) }; // Retry in 1 minute
+  },
+  run: async (payload) => {
+    // Retry specific operations
+    const result = await retry.onThrow(
+      async () => {
+        return await unstableApiCall(payload);
+      },
+      { maxAttempts: 3 },
+    );
+
+    // Conditional HTTP retries
+    const response = await retry.fetch('https://api.example.com', {
+      retry: {
+        maxAttempts: 5,
+        condition: (response, error) => {
+          return response?.status === 429 || response?.status >= 500;
+        },
+      },
+    });
+
+    return result;
+  },
+});
+```
+
+## Machines & Performance
+
+```ts
+export const heavyTask = task({
+  id: 'heavy-computation',
+  machine: { preset: 'large-2x' }, // 8 vCPU, 16 GB RAM
+  maxDuration: 1800, // 30 minutes timeout
+  run: async (payload, { ctx }) => {
+    // Resource-intensive computation
+    if (ctx.machine.preset === 'large-2x') {
+      // Use all available cores
+      return await parallelProcessing(payload);
+    }
+
+    return await standardProcessing(payload);
+  },
+});
+
+// Override machine when triggering
+await heavyTask.trigger(payload, {
+  machine: { preset: 'medium-1x' }, // Override for this run
+});
+```
+
+**Machine Presets:**
+
+- `micro`: 0.25 vCPU, 0.25 GB RAM
+- `small-1x`: 0.5 vCPU, 0.5 GB RAM (default)
+- `small-2x`: 1 vCPU, 1 GB RAM
+- `medium-1x`: 1 vCPU, 2 GB RAM
+- `medium-2x`: 2 vCPU, 4 GB RAM
+- `large-1x`: 4 vCPU, 8 GB RAM
+- `large-2x`: 8 vCPU, 16 GB RAM
+
+## Idempotency
+
+```ts
+import { task, idempotencyKeys } from '@trigger.dev/sdk';
+
+export const paymentTask = task({
+  id: 'process-payment',
+  retry: {
+    maxAttempts: 3,
+  },
+  run: async (payload: { orderId: string; amount: number }) => {
+    // Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same
+    const idempotencyKey = await idempotencyKeys.create(`payment-${payload.orderId}`);
+
+    // Ensure payment is processed only once
+    await chargeCustomer.trigger(payload, {
+      idempotencyKey,
+      idempotencyKeyTTL: '24h', // Key expires in 24 hours
+    });
+  },
+});
+
+// Payload-based idempotency
+import { createHash } from 'node:crypto';
+
+function createPayloadHash(payload: any): string {
+  const hash = createHash('sha256');
+  hash.update(JSON.stringify(payload));
+  return hash.digest('hex');
+}
+
+export const deduplicatedTask = task({
+  id: 'deduplicated-task',
+  run: async (payload) => {
+    const payloadHash = createPayloadHash(payload);
+    const idempotencyKey = await idempotencyKeys.create(payloadHash);
+
+    await processData.trigger(payload, { idempotencyKey });
+  },
+});
+```
+
+## Metadata & Progress Tracking
+
+```ts
+import { task, metadata } from '@trigger.dev/sdk';
+
+export const batchProcessor = task({
+  id: 'batch-processor',
+  run: async (payload: { items: any[] }, { ctx }) => {
+    const totalItems = payload.items.length;
+
+    // Initialize progress metadata
+    metadata
+      .set('progress', 0)
+      .set('totalItems', totalItems)
+      .set('processedItems', 0)
+      .set('status', 'starting');
+
+    const results = [];
+
+    for (let i = 0; i < payload.items.length; i++) {
+      const item = payload.items[i];
+
+      // Process item
+      const result = await processItem(item);
+      results.push(result);
+
+      // Update progress
+      const progress = ((i + 1) / totalItems) * 100;
+      metadata
+        .set('progress', progress)
+        .increment('processedItems', 1)
+        .append('logs', `Processed item ${i + 1}/${totalItems}`)
+        .set('currentItem', item.id);
+    }
+
+    // Final status
+    metadata.set('status', 'completed');
+
+    return { results, totalProcessed: results.length };
+  },
+});
+
+// Update parent metadata from child task
+export const childTask = task({
+  id: 'child-task',
+  run: async (payload, { ctx }) => {
+    // Update parent task metadata
+    metadata.parent.set('childStatus', 'processing');
+    metadata.root.increment('childrenCompleted', 1);
+
+    return { processed: true };
+  },
+});
+```
+
+## Advanced Triggering
+
+### Frontend Triggering (React)
+
+```tsx
+'use client';
+import { useTaskTrigger } from '@trigger.dev/react-hooks';
+import type { myTask } from '../trigger/tasks';
+
+function TriggerButton({ accessToken }: { accessToken: string }) {
+  const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });
+
+  return (
+    <button onClick={() => submit({ data: 'from frontend' })} disabled={isLoading}>
+      Trigger Task
+    </button>
+  );
+}
+```
+
+### Large Payloads
+
+```ts
+// For payloads > 512KB (max 10MB)
+export const largeDataTask = task({
+  id: 'large-data-task',
+  run: async (payload: { dataUrl: string }) => {
+    // Trigger.dev automatically handles large payloads
+    // For > 10MB, use external storage
+    const response = await fetch(payload.dataUrl);
+    const largeData = await response.json();
+
+    return { processed: largeData.length };
+  },
+});
+
+// Best practice: Use presigned URLs for very large files
+await largeDataTask.trigger({
+  dataUrl: 'https://s3.amazonaws.com/bucket/large-file.json?presigned=true',
+});
+```
+
+### Advanced Options
+
+```ts
+await myTask.trigger(payload, {
+  delay: '2h30m', // Delay execution
+  ttl: '24h', // Expire if not started within 24 hours
+  priority: 100, // Higher priority (time offset in seconds)
+  tags: ['urgent', 'user_123'],
+  metadata: { source: 'api', version: 'v2' },
+  queue: {
+    name: 'priority-queue',
+    concurrencyLimit: 10,
+  },
+  idempotencyKey: 'unique-operation-id',
+  idempotencyKeyTTL: '1h',
+  machine: { preset: 'large-1x' },
+  maxAttempts: 5,
+});
+```
+
+## Hidden Tasks
+
+```ts
+// Hidden task - not exported, only used internally
+const internalProcessor = task({
+  id: 'internal-processor',
+  run: async (payload: { data: string }) => {
+    return { processed: payload.data.toUpperCase() };
+  },
+});
+
+// Public task that uses hidden task
+export const publicWorkflow = task({
+  id: 'public-workflow',
+  run: async (payload: { input: string }) => {
+    // Use hidden task internally
+    const result = await internalProcessor.triggerAndWait({
+      data: payload.input,
+    });
+
+    if (result.ok) {
+      return { output: result.output.processed };
+    }
+
+    throw new Error('Internal processing failed');
+  },
+});
+```
+
+## Logging & Tracing
+
+```ts
+import { task, logger } from '@trigger.dev/sdk';
+
+export const tracedTask = task({
+  id: 'traced-task',
+  run: async (payload, { ctx }) => {
+    logger.info('Task started', { userId: payload.userId });
+
+    // Custom trace with attributes
+    const user = await logger.trace(
+      'fetch-user',
+      async (span) => {
+        span.setAttribute('user.id', payload.userId);
+        span.setAttribute('operation', 'database-fetch');
+
+        const userData = await database.findUser(payload.userId);
+        span.setAttribute('user.found', !!userData);
+
+        return userData;
+      },
+      { userId: payload.userId },
+    );
+
+    logger.debug('User fetched', { user: user.id });
+
+    try {
+      const result = await processUser(user);
+      logger.info('Processing completed', { result });
+      return result;
+    } catch (error) {
+      logger.error('Processing failed', {
+        error: error.message,
+        userId: payload.userId,
+      });
+      throw error;
+    }
+  },
+});
+```
+
+## Usage Monitoring
+
+```ts
+import { logger, task, usage } from '@trigger.dev/sdk';
+
+export const monitoredTask = task({
+  id: 'monitored-task',
+  run: async (payload) => {
+    // Get current run cost
+    const currentUsage = await usage.getCurrent();
+    logger.info('Current cost', {
+      costInCents: currentUsage.costInCents,
+      durationMs: currentUsage.durationMs,
+    });
+
+    // Measure specific operation
+    const { result, compute } = await usage.measure(async () => {
+      return await expensiveOperation(payload);
+    });
+
+    logger.info('Operation cost', {
+      costInCents: compute.costInCents,
+      durationMs: compute.durationMs,
+    });
+
+    return result;
+  },
+});
+```
+
+## Run Management
+
+```ts
+// Cancel runs
+await runs.cancel('run_123');
+
+// Replay runs with same payload
+await runs.replay('run_123');
+
+// Retrieve run with cost details
+const run = await runs.retrieve('run_123');
+console.log(`Cost: ${run.costInCents} cents, Duration: ${run.durationMs}ms`);
+```
+
+## Best Practices
+
+- **Concurrency**: Use queues to prevent overwhelming external services
+- **Retries**: Configure exponential backoff for transient failures
+- **Idempotency**: Always use for payment/critical operations
+- **Metadata**: Track progress for long-running tasks
+- **Machines**: Match machine size to computational requirements
+- **Tags**: Use consistent naming patterns for filtering
+- **Large Payloads**: Use external storage for files > 10MB
+- **Error Handling**: Distinguish between retryable and fatal errors
+
+Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.
diff --git a/.agents/skills/trigger-basic/SKILL.md b/.agents/skills/trigger-basic/SKILL.md
@@ -0,0 +1,194 @@
+---
+name: trigger-basic
+description: "Only the most important rules for writing basic Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.basic.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Basic Tasks (v4)
+
+**MUST use `@trigger.dev/sdk` (v4), NEVER `client.defineJob`**
+
+## Basic Task
+
+```ts
+import { task } from "@trigger.dev/sdk";
+
+export const processData = task({
+  id: "process-data",
+  retry: {
+    maxAttempts: 10,
+    factor: 1.8,
+    minTimeoutInMs: 500,
+    maxTimeoutInMs: 30_000,
+    randomize: false,
+  },
+  run: async (payload: { userId: string; data: any[] }) => {
+    // Task logic - runs for long time, no timeouts
+    console.log(`Processing ${payload.data.length} items for user ${payload.userId}`);
+    return { processed: payload.data.length };
+  },
+});
+```
+
+## Schema Task (with validation)
+
+```ts
+import { schemaTask } from "@trigger.dev/sdk";
+import { z } from "zod";
+
+export const validatedTask = schemaTask({
+  id: "validated-task",
+  schema: z.object({
+    name: z.string(),
+    age: z.number(),
+    email: z.string().email(),
+  }),
+  run: async (payload) => {
+    // Payload is automatically validated and typed
+    return { message: `Hello ${payload.name}, age ${payload.age}` };
+  },
+});
+```
+
+## Scheduled Task
+
+```ts
+import { schedules } from "@trigger.dev/sdk";
+
+const dailyReport = schedules.task({
+  id: "daily-report",
+  cron: "0 9 * * *", // Daily at 9:00 AM UTC
+  // or with timezone: cron: { pattern: "0 9 * * *", timezone: "America/New_York" },
+  run: async (payload) => {
+    console.log("Scheduled run at:", payload.timestamp);
+    console.log("Last run was:", payload.lastTimestamp);
+    console.log("Next 5 runs:", payload.upcoming);
+
+    // Generate daily report logic
+    return { reportGenerated: true, date: payload.timestamp };
+  },
+});
+```
+
+## Triggering Tasks
+
+### From Backend Code
+
+```ts
+import { tasks } from "@trigger.dev/sdk";
+import type { processData } from "./trigger/tasks";
+
+// Single trigger
+const handle = await tasks.trigger<typeof processData>("process-data", {
+  userId: "123",
+  data: [{ id: 1 }, { id: 2 }],
+});
+
+// Batch trigger
+const batchHandle = await tasks.batchTrigger<typeof processData>("process-data", [
+  { payload: { userId: "123", data: [{ id: 1 }] } },
+  { payload: { userId: "456", data: [{ id: 2 }] } },
+]);
+```
+
+### From Inside Tasks (with Result handling)
+
+```ts
+export const parentTask = task({
+  id: "parent-task",
+  run: async (payload) => {
+    // Trigger and continue
+    const handle = await childTask.trigger({ data: "value" });
+
+    // Trigger and wait - returns Result object, NOT task output
+    const result = await childTask.triggerAndWait({ data: "value" });
+    if (result.ok) {
+      console.log("Task output:", result.output); // Actual task return value
+    } else {
+      console.error("Task failed:", result.error);
+    }
+
+    // Quick unwrap (throws on error)
+    const output = await childTask.triggerAndWait({ data: "value" }).unwrap();
+
+    // Batch trigger and wait
+    const results = await childTask.batchTriggerAndWait([
+      { payload: { data: "item1" } },
+      { payload: { data: "item2" } },
+    ]);
+
+    for (const run of results) {
+      if (run.ok) {
+        console.log("Success:", run.output);
+      } else {
+        console.log("Failed:", run.error);
+      }
+    }
+  },
+});
+
+export const childTask = task({
+  id: "child-task",
+  run: async (payload: { data: string }) => {
+    return { processed: payload.data };
+  },
+});
+```
+
+> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.
+
+## Waits
+
+```ts
+import { task, wait } from "@trigger.dev/sdk";
+
+export const taskWithWaits = task({
+  id: "task-with-waits",
+  run: async (payload) => {
+    console.log("Starting task");
+
+    // Wait for specific duration
+    await wait.for({ seconds: 30 });
+    await wait.for({ minutes: 5 });
+    await wait.for({ hours: 1 });
+    await wait.for({ days: 1 });
+
+    // Wait until a future date
+    await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });
+
+    // Wait for token (from external system)
+    await wait.forToken({
+      token: "user-approval-token",
+      timeoutInSeconds: 3600, // 1 hour timeout
+    });
+
+    console.log("All waits completed");
+    return { status: "completed" };
+  },
+});
+```
+
+> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.
+
+## Key Points
+
+- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output
+- **Type safety**: Use `import type` for task references when triggering from backend
+- **Waits > 5 seconds**: Automatically checkpointed, don't count toward compute usage
+
+## NEVER Use (v2 deprecated)
+
+```ts
+// BREAKS APPLICATION
+client.defineJob({
+  id: "job-id",
+  run: async (payload, io) => {
+    /* ... */
+  },
+});
+```
+
+Use v4 SDK (`@trigger.dev/sdk`), check `result.ok` before accessing `result.output`
diff --git a/.agents/skills/trigger-config/SKILL.md b/.agents/skills/trigger-config/SKILL.md
@@ -0,0 +1,355 @@
+---
+name: trigger-config
+description: "Configure your Trigger.dev project with a trigger.config.ts file"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.config.mdc`.
+Original file scope: `**/trigger.config.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Configuration (v4)
+
+**Complete guide to configuring `trigger.config.ts` with build extensions**
+
+## Basic Configuration
+
+```ts
+import { defineConfig } from "@trigger.dev/sdk";
+
+export default defineConfig({
+  project: "<project-ref>", // Required: Your project reference
+  dirs: ["./trigger"], // Task directories
+  runtime: "node", // "node", "node-22", or "bun"
+  logLevel: "info", // "debug", "info", "warn", "error"
+
+  // Default retry settings
+  retries: {
+    enabledInDev: false,
+    default: {
+      maxAttempts: 3,
+      minTimeoutInMs: 1000,
+      maxTimeoutInMs: 10000,
+      factor: 2,
+      randomize: true,
+    },
+  },
+
+  // Build configuration
+  build: {
+    autoDetectExternal: true,
+    keepNames: true,
+    minify: false,
+    extensions: [], // Build extensions go here
+  },
+
+  // Global lifecycle hooks
+  onStart: async ({ payload, ctx }) => {
+    console.log("Global task start");
+  },
+  onSuccess: async ({ payload, output, ctx }) => {
+    console.log("Global task success");
+  },
+  onFailure: async ({ payload, error, ctx }) => {
+    console.log("Global task failure");
+  },
+});
+```
+
+## Build Extensions
+
+### Database & ORM
+
+#### Prisma
+
+```ts
+import { prismaExtension } from "@trigger.dev/build/extensions/prisma";
+
+extensions: [
+  prismaExtension({
+    schema: "prisma/schema.prisma",
+    version: "5.19.0", // Optional: specify version
+    migrate: true, // Run migrations during build
+    directUrlEnvVarName: "DIRECT_DATABASE_URL",
+    typedSql: true, // Enable TypedSQL support
+  }),
+];
+```
+
+#### TypeScript Decorators (for TypeORM)
+
+```ts
+import { emitDecoratorMetadata } from "@trigger.dev/build/extensions/typescript";
+
+extensions: [
+  emitDecoratorMetadata(), // Enables decorator metadata
+];
+```
+
+### Scripting Languages
+
+#### Python
+
+```ts
+import { pythonExtension } from "@trigger.dev/build/extensions/python";
+
+extensions: [
+  pythonExtension({
+    scripts: ["./python/**/*.py"], // Copy Python files
+    requirementsFile: "./requirements.txt", // Install packages
+    devPythonBinaryPath: ".venv/bin/python", // Dev mode binary
+  }),
+];
+
+// Usage in tasks
+const result = await python.runInline(`print("Hello, world!")`);
+const output = await python.runScript("./python/script.py", ["arg1"]);
+```
+
+### Browser Automation
+
+#### Playwright
+
+```ts
+import { playwright } from "@trigger.dev/build/extensions/playwright";
+
+extensions: [
+  playwright({
+    browsers: ["chromium", "firefox", "webkit"], // Default: ["chromium"]
+    headless: true, // Default: true
+  }),
+];
+```
+
+#### Puppeteer
+
+```ts
+import { puppeteer } from "@trigger.dev/build/extensions/puppeteer";
+
+extensions: [puppeteer()];
+
+// Environment variable needed:
+// PUPPETEER_EXECUTABLE_PATH: "/usr/bin/google-chrome-stable"
+```
+
+#### Lightpanda
+
+```ts
+import { lightpanda } from "@trigger.dev/build/extensions/lightpanda";
+
+extensions: [
+  lightpanda({
+    version: "latest", // or "nightly"
+    disableTelemetry: false,
+  }),
+];
+```
+
+### Media Processing
+
+#### FFmpeg
+
+```ts
+import { ffmpeg } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  ffmpeg({ version: "7" }), // Static build, or omit for Debian version
+];
+
+// Automatically sets FFMPEG_PATH and FFPROBE_PATH
+// Add fluent-ffmpeg to external packages if using
+```
+
+#### Audio Waveform
+
+```ts
+import { audioWaveform } from "@trigger.dev/build/extensions/audioWaveform";
+
+extensions: [
+  audioWaveform(), // Installs Audio Waveform 1.1.0
+];
+```
+
+### System & Package Management
+
+#### System Packages (apt-get)
+
+```ts
+import { aptGet } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  aptGet({
+    packages: ["ffmpeg", "imagemagick", "curl=7.68.0-1"], // Can specify versions
+  }),
+];
+```
+
+#### Additional NPM Packages
+
+Only use this for installing CLI tools, NOT packages you import in your code.
+
+```ts
+import { additionalPackages } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  additionalPackages({
+    packages: ["wrangler"], // CLI tools and specific versions
+  }),
+];
+```
+
+#### Additional Files
+
+```ts
+import { additionalFiles } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  additionalFiles({
+    files: ["wrangler.toml", "./assets/**", "./fonts/**"], // Glob patterns supported
+  }),
+];
+```
+
+### Environment & Build Tools
+
+#### Environment Variable Sync
+
+```ts
+import { syncEnvVars } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  syncEnvVars(async (ctx) => {
+    // ctx contains: environment, projectRef, env
+    return [
+      { name: "SECRET_KEY", value: await getSecret(ctx.environment) },
+      { name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },
+    ];
+  }),
+];
+```
+
+#### ESBuild Plugins
+
+```ts
+import { esbuildPlugin } from "@trigger.dev/build/extensions";
+import { sentryEsbuildPlugin } from "@sentry/esbuild-plugin";
+
+extensions: [
+  esbuildPlugin(
+    sentryEsbuildPlugin({
+      org: process.env.SENTRY_ORG,
+      project: process.env.SENTRY_PROJECT,
+      authToken: process.env.SENTRY_AUTH_TOKEN,
+    }),
+    { placement: "last", target: "deploy" } // Optional config
+  ),
+];
+```
+
+## Custom Build Extensions
+
+```ts
+import { defineConfig } from "@trigger.dev/sdk";
+
+const customExtension = {
+  name: "my-custom-extension",
+
+  externalsForTarget: (target) => {
+    return ["some-native-module"]; // Add external dependencies
+  },
+
+  onBuildStart: async (context) => {
+    console.log(`Build starting for ${context.target}`);
+    // Register esbuild plugins, modify build context
+  },
+
+  onBuildComplete: async (context, manifest) => {
+    console.log("Build complete, adding layers");
+    // Add build layers, modify deployment
+    context.addLayer({
+      id: "my-layer",
+      files: [{ source: "./custom-file", destination: "/app/custom" }],
+      commands: ["chmod +x /app/custom"],
+    });
+  },
+};
+
+export default defineConfig({
+  project: "my-project",
+  build: {
+    extensions: [customExtension],
+  },
+});
+```
+
+## Advanced Configuration
+
+### Telemetry
+
+```ts
+import { PrismaInstrumentation } from "@prisma/instrumentation";
+import { OpenAIInstrumentation } from "@langfuse/openai";
+
+export default defineConfig({
+  // ... other config
+  telemetry: {
+    instrumentations: [new PrismaInstrumentation(), new OpenAIInstrumentation()],
+    exporters: [customExporter], // Optional custom exporters
+  },
+});
+```
+
+### Machine & Performance
+
+```ts
+export default defineConfig({
+  // ... other config
+  defaultMachine: "large-1x", // Default machine for all tasks
+  maxDuration: 300, // Default max duration (seconds)
+  enableConsoleLogging: true, // Console logging in development
+});
+```
+
+## Common Extension Combinations
+
+### Full-Stack Web App
+
+```ts
+extensions: [
+  prismaExtension({ schema: "prisma/schema.prisma", migrate: true }),
+  additionalFiles({ files: ["./public/**", "./assets/**"] }),
+  syncEnvVars(async (ctx) => [...envVars]),
+];
+```
+
+### AI/ML Processing
+
+```ts
+extensions: [
+  pythonExtension({
+    scripts: ["./ai/**/*.py"],
+    requirementsFile: "./requirements.txt",
+  }),
+  ffmpeg({ version: "7" }),
+  additionalPackages({ packages: ["wrangler"] }),
+];
+```
+
+### Web Scraping
+
+```ts
+extensions: [
+  playwright({ browsers: ["chromium"] }),
+  puppeteer(),
+  additionalFiles({ files: ["./selectors.json", "./proxies.txt"] }),
+];
+```
+
+## Best Practices
+
+- **Use specific versions**: Pin extension versions for reproducible builds
+- **External packages**: Add modules with native addons to the `build.external` array
+- **Environment sync**: Use `syncEnvVars` for dynamic secrets
+- **File paths**: Use glob patterns for flexible file inclusion
+- **Debug builds**: Use `--log-level debug --dry-run` for troubleshooting
+
+Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled.
diff --git a/.agents/skills/trigger-realtime/SKILL.md b/.agents/skills/trigger-realtime/SKILL.md
@@ -0,0 +1,281 @@
+---
+name: trigger-realtime
+description: "How to use realtime in your Trigger.dev tasks and your frontend"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.realtime.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Realtime (v4)
+
+**Real-time monitoring and updates for runs**
+
+## Core Concepts
+
+Realtime allows you to:
+
+- Subscribe to run status changes, metadata updates, and streams
+- Build real-time dashboards and UI updates
+- Monitor task progress from frontend and backend
+
+## Authentication
+
+### Public Access Tokens
+
+```ts
+import { auth } from "@trigger.dev/sdk";
+
+// Read-only token for specific runs
+const publicToken = await auth.createPublicToken({
+  scopes: {
+    read: {
+      runs: ["run_123", "run_456"],
+      tasks: ["my-task-1", "my-task-2"],
+    },
+  },
+  expirationTime: "1h", // Default: 15 minutes
+});
+```
+
+### Trigger Tokens (Frontend only)
+
+```ts
+// Single-use token for triggering tasks
+const triggerToken = await auth.createTriggerPublicToken("my-task", {
+  expirationTime: "30m",
+});
+```
+
+## Backend Usage
+
+### Subscribe to Runs
+
+```ts
+import { runs, tasks } from "@trigger.dev/sdk";
+
+// Trigger and subscribe
+const handle = await tasks.trigger("my-task", { data: "value" });
+
+// Subscribe to specific run
+for await (const run of runs.subscribeToRun<typeof myTask>(handle.id)) {
+  console.log(`Status: ${run.status}, Progress: ${run.metadata?.progress}`);
+  if (run.status === "COMPLETED") break;
+}
+
+// Subscribe to runs with tag
+for await (const run of runs.subscribeToRunsWithTag("user-123")) {
+  console.log(`Tagged run ${run.id}: ${run.status}`);
+}
+
+// Subscribe to batch
+for await (const run of runs.subscribeToBatch(batchId)) {
+  console.log(`Batch run ${run.id}: ${run.status}`);
+}
+```
+
+### Streams
+
+```ts
+import { task, metadata } from "@trigger.dev/sdk";
+
+// Task that streams data
+export type STREAMS = {
+  openai: OpenAI.ChatCompletionChunk;
+};
+
+export const streamingTask = task({
+  id: "streaming-task",
+  run: async (payload) => {
+    const completion = await openai.chat.completions.create({
+      model: "gpt-4",
+      messages: [{ role: "user", content: payload.prompt }],
+      stream: true,
+    });
+
+    // Register stream
+    const stream = await metadata.stream("openai", completion);
+
+    let text = "";
+    for await (const chunk of stream) {
+      text += chunk.choices[0]?.delta?.content || "";
+    }
+
+    return { text };
+  },
+});
+
+// Subscribe to streams
+for await (const part of runs.subscribeToRun(runId).withStreams<STREAMS>()) {
+  switch (part.type) {
+    case "run":
+      console.log("Run update:", part.run.status);
+      break;
+    case "openai":
+      console.log("Stream chunk:", part.chunk);
+      break;
+  }
+}
+```
+
+## React Frontend Usage
+
+### Installation
+
+```bash
+bun add @trigger.dev/react-hooks
+```
+
+### Triggering Tasks
+
+```tsx
+"use client";
+import { useTaskTrigger, useRealtimeTaskTrigger } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function TriggerComponent({ accessToken }: { accessToken: string }) {
+  // Basic trigger
+  const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>("my-task", {
+    accessToken,
+  });
+
+  // Trigger with realtime updates
+  const {
+    submit: realtimeSubmit,
+    run,
+    isLoading: isRealtimeLoading,
+  } = useRealtimeTaskTrigger<typeof myTask>("my-task", { accessToken });
+
+  return (
+    <div>
+      <button onClick={() => submit({ data: "value" })} disabled={isLoading}>
+        Trigger Task
+      </button>
+
+      <button onClick={() => realtimeSubmit({ data: "realtime" })} disabled={isRealtimeLoading}>
+        Trigger with Realtime
+      </button>
+
+      {run && <div>Status: {run.status}</div>}
+    </div>
+  );
+}
+```
+
+### Subscribing to Runs
+
+```tsx
+"use client";
+import { useRealtimeRun, useRealtimeRunsWithTag } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  // Subscribe to specific run
+  const { run, error } = useRealtimeRun<typeof myTask>(runId, {
+    accessToken,
+    onComplete: (run) => {
+      console.log("Task completed:", run.output);
+    },
+  });
+
+  // Subscribe to tagged runs
+  const { runs } = useRealtimeRunsWithTag("user-123", { accessToken });
+
+  if (error) return <div>Error: {error.message}</div>;
+  if (!run) return <div>Loading...</div>;
+
+  return (
+    <div>
+      <div>Status: {run.status}</div>
+      <div>Progress: {run.metadata?.progress || 0}%</div>
+      {run.output && <div>Result: {JSON.stringify(run.output)}</div>}
+
+      <h3>Tagged Runs:</h3>
+      {runs.map((r) => (
+        <div key={r.id}>
+          {r.id}: {r.status}
+        </div>
+      ))}
+    </div>
+  );
+}
+```
+
+### Streams with React
+
+```tsx
+"use client";
+import { useRealtimeRunWithStreams } from "@trigger.dev/react-hooks";
+import type { streamingTask, STREAMS } from "../trigger/tasks";
+
+function StreamComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  const { run, streams } = useRealtimeRunWithStreams<typeof streamingTask, STREAMS>(runId, {
+    accessToken,
+  });
+
+  const text = streams.openai
+    .filter((chunk) => chunk.choices[0]?.delta?.content)
+    .map((chunk) => chunk.choices[0].delta.content)
+    .join("");
+
+  return (
+    <div>
+      <div>Status: {run?.status}</div>
+      <div>Streamed Text: {text}</div>
+    </div>
+  );
+}
+```
+
+### Wait Tokens
+
+```tsx
+"use client";
+import { useWaitToken } from "@trigger.dev/react-hooks";
+
+function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {
+  const { complete } = useWaitToken(tokenId, { accessToken });
+
+  return <button onClick={() => complete({ approved: true })}>Approve Task</button>;
+}
+```
+
+### SWR Hooks (Fetch Once)
+
+```tsx
+"use client";
+import { useRun } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function SWRComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  const { run, error, isLoading } = useRun<typeof myTask>(runId, {
+    accessToken,
+    refreshInterval: 0, // Disable polling (recommended)
+  });
+
+  if (isLoading) return <div>Loading...</div>;
+  if (error) return <div>Error: {error.message}</div>;
+
+  return <div>Run: {run?.status}</div>;
+}
+```
+
+## Run Object Properties
+
+Key properties available in run subscriptions:
+
+- `id`: Unique run identifier
+- `status`: `QUEUED`, `EXECUTING`, `COMPLETED`, `FAILED`, `CANCELED`, etc.
+- `payload`: Task input data (typed)
+- `output`: Task result (typed, when completed)
+- `metadata`: Real-time updatable data
+- `createdAt`, `updatedAt`: Timestamps
+- `costInCents`: Execution cost
+
+## Best Practices
+
+- **Use Realtime over SWR**: Recommended for most use cases due to rate limits
+- **Scope tokens properly**: Only grant necessary read/trigger permissions
+- **Handle errors**: Always check for errors in hooks and subscriptions
+- **Type safety**: Use task types for proper payload/output typing
+- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup
diff --git a/.agents/skills/trigger-scheduled-tasks/SKILL.md b/.agents/skills/trigger-scheduled-tasks/SKILL.md
@@ -0,0 +1,126 @@
+---
+name: trigger-scheduled-tasks
+description: "How to write and use scheduled Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.scheduled-tasks.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Scheduled tasks (cron)
+
+Recurring tasks using cron. For one-off future runs, use the **delay** option.
+
+## Define a scheduled task
+
+```ts
+import { schedules } from "@trigger.dev/sdk";
+
+export const task = schedules.task({
+  id: "first-scheduled-task",
+  run: async (payload) => {
+    payload.timestamp; // Date (scheduled time, UTC)
+    payload.lastTimestamp; // Date | undefined
+    payload.timezone; // IANA, e.g. "America/New_York" (default "UTC")
+    payload.scheduleId; // string
+    payload.externalId; // string | undefined
+    payload.upcoming; // Date[]
+
+    payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone });
+  },
+});
+```
+
+> Scheduled tasks need at least one schedule attached to run.
+
+## Attach schedules
+
+**Declarative (sync on dev/deploy):**
+
+```ts
+schedules.task({
+  id: "every-2h",
+  cron: "0 */2 * * *", // UTC
+  run: async () => {},
+});
+
+schedules.task({
+  id: "tokyo-5am",
+  cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },
+  run: async () => {},
+});
+```
+
+**Imperative (SDK or dashboard):**
+
+```ts
+await schedules.create({
+  task: task.id,
+  cron: "0 0 * * *",
+  timezone: "America/New_York", // DST-aware
+  externalId: "user_123",
+  deduplicationKey: "user_123-daily", // updates if reused
+});
+```
+
+### Dynamic / multi-tenant example
+
+```ts
+// /trigger/reminder.ts
+export const reminderTask = schedules.task({
+  id: "todo-reminder",
+  run: async (p) => {
+    if (!p.externalId) throw new Error("externalId is required");
+    const user = await db.getUser(p.externalId);
+    await sendReminderEmail(user);
+  },
+});
+```
+
+```ts
+// app/reminders/route.ts
+export async function POST(req: Request) {
+  const data = await req.json();
+  return Response.json(
+    await schedules.create({
+      task: reminderTask.id,
+      cron: "0 8 * * *",
+      timezone: data.timezone,
+      externalId: data.userId,
+      deduplicationKey: `${data.userId}-reminder`,
+    })
+  );
+}
+```
+
+## Cron syntax (no seconds)
+
+```
+* * * * *
+| | | | └ day of week (0–7 or 1L–7L; 0/7=Sun; L=last)
+| | | └── month (1–12)
+| | └──── day of month (1–31 or L)
+| └────── hour (0–23)
+└──────── minute (0–59)
+```
+
+## When schedules won't trigger
+
+- **Dev:** only when the dev CLI is running.
+- **Staging/Production:** only for tasks in the **latest deployment**.
+
+## SDK management (quick refs)
+
+```ts
+await schedules.retrieve(id);
+await schedules.list();
+await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });
+await schedules.deactivate(id);
+await schedules.activate(id);
+await schedules.del(id);
+await schedules.timezones(); // list of IANA timezones
+```
+
+## Dashboard
+
+Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.
diff --git a/.agents/skills/ui/SKILL.md b/.agents/skills/ui/SKILL.md
@@ -0,0 +1,137 @@
+---
+name: ui
+description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."
+---
+
+Source Cursor rule: `.cursor/rules/ui.mdc`.
+Original Cursor alwaysApply: `true`.
+
+# UI Components
+
+## Design System Priority
+
+1. **First choice:** `@trycompai/design-system`
+2. **Fallback:** `@trycompai/ui` only if DS doesn't have the component
+
+```tsx
+// ✅ Design system
+import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';
+import { Add, Close, ArrowRight } from '@trycompai/design-system/icons';
+
+// ❌ Don't use when DS has it
+import { Button } from '@trycompai/ui/button';
+import { Plus } from 'lucide-react';
+```
+
+## No className on DS Components
+
+DS components don't accept `className`. Use variants and props only.
+
+```tsx
+// ✅ Use variants
+<Button variant="destructive" size="sm" loading={isLoading}>Delete</Button>
+<Button type="submit" iconRight={<ArrowRight size={16} />}>Continue</Button>
+<Badge variant="outline">Active</Badge>
+
+// ❌ TypeScript will error
+<Button className="bg-red-500">Delete</Button>
+```
+
+## Layout with Wrapper Divs
+
+For layout concerns, wrap DS components:
+
+```tsx
+// ✅ Wrapper for width
+<div className="w-full">
+  <Button>Full Width</Button>
+</div>
+
+// ✅ Use Stack for spacing
+<Stack gap="4" direction="row">
+  <Button>First</Button>
+  <Button>Second</Button>
+</Stack>
+```
+
+## Componentize Repeated Patterns
+
+If a pattern appears 2+ times, extract it:
+
+```tsx
+// Repeated? Make a component
+<div className="flex items-center gap-2">
+  <div className="w-2 h-2 rounded-full bg-green-500" />
+  <span className="text-sm">Active</span>
+</div>
+// → Create <StatusDot status="active" />
+```
+
+## Extension Strategy
+
+When you need new styling:
+
+1. **Check existing variants** - component may already support it
+2. **Add a variant** to the component's `cva` definition
+3. **Create a new component** if it's a genuinely new pattern
+
+```tsx
+// Adding a variant
+const badgeVariants = cva("...", {
+  variants: {
+    variant: {
+      // existing...
+      counter: "bg-muted text-muted-foreground tabular-nums font-mono",
+    },
+  },
+});
+```
+
+## Semantic Colors
+
+Use CSS variables, not hardcoded colors:
+
+```tsx
+// ✅ Semantic tokens
+<div className="bg-background text-foreground border-border">
+<div className="bg-muted text-muted-foreground">
+<div className="bg-destructive/10 text-destructive">
+
+// ❌ Hardcoded
+<div className="bg-white text-black">
+<div className="bg-[#059669]">
+```
+
+## Dark Mode
+
+Always support both modes:
+
+```tsx
+// Status colors with dark variants
+<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">
+<div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400">
+```
+
+## Icons
+
+Carbon icons from DS, not lucide:
+
+```tsx
+// ✅ Design system icons with size prop
+import { Add, Close, ChevronDown } from '@trycompai/design-system/icons';
+<Add size={16} />
+
+// ❌ Don't use lucide
+import { Plus, X } from 'lucide-react';
+<Plus className="h-4 w-4" />
+```
+
+## Anti-Patterns
+
+```tsx
+// ❌ Never do these
+<div style={{ display: 'flex' }}>              // Inline styles
+<Button className="bg-red-500">               // className on DS
+<div className="bg-[#059669]">                // Hardcoded colors
+<div className="w-[847px]">                   // Arbitrary values
+```
diff --git a/.claude/agents/test-writer.md b/.claude/agents/test-writer.md
@@ -12,7 +12,7 @@ You write unit tests for React components that use `usePermissions` for RBAC gat
 - **Libraries**: `@testing-library/react` + `@testing-library/jest-dom`
 - **Setup**: `apps/app/src/test-utils/setup.ts`
 - **Permission mocks**: `apps/app/src/test-utils/mocks/permissions.ts`
-- **Run**: `cd apps/app && npx vitest run path/to/test`
+- **Run**: `cd apps/app && bunx vitest run path/to/test`
 
 ## Process
 
@@ -84,4 +84,4 @@ describe('ComponentUnderTest', () => {
 - Mock all external hooks (`useSWR`, `useRouter`, `apiClient`, etc.)
 - Use `screen.queryBy*` for elements that should NOT exist (returns null instead of throwing)
 - Use `screen.getBy*` for elements that MUST exist
-- Run the test after writing to verify it passes: `cd apps/app && npx vitest run path/to/file.test.tsx`
+- Run the test after writing to verify it passes: `cd apps/app && bunx vitest run path/to/file.test.tsx`
diff --git a/.claude/skills/audit-design-system/SKILL.md b/.claude/skills/audit-design-system/SKILL.md
@@ -20,4 +20,4 @@ Audit the specified files for design system compliance. **Fix every issue found
 2. Find `@trycompai/ui` imports — check if DS equivalent exists
 3. Find `lucide-react` imports — find matching Carbon icons
 4. Migrate components and icons
-5. Run build to verify: `npx turbo run typecheck --filter=@trycompai/app`
+5. Run build to verify: `bunx turbo run typecheck --filter=@trycompai/app`
diff --git a/.claude/skills/audit-hooks/SKILL.md b/.claude/skills/audit-hooks/SKILL.md
@@ -31,4 +31,4 @@ Audit the specified files for hook and API usage compliance. **Fix every issue f
 1. Read files specified in `$ARGUMENTS`
 2. Find forbidden patterns and fix them
 3. Ensure all data fetching uses SWR hooks
-4. Run typecheck to verify: `npx turbo run typecheck --filter=@trycompai/app`
+4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/app`
diff --git a/.claude/skills/audit-rbac/SKILL.md b/.claude/skills/audit-rbac/SKILL.md
@@ -39,4 +39,4 @@ Audit the specified files or directories for RBAC and audit log compliance. **Fi
 1. Read files specified in `$ARGUMENTS` (or scan the directory)
 2. Check each rule above
 3. **Fix every violation immediately** — don't just report
-4. Run typecheck to verify: `npx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app`
+4. Run typecheck to verify: `bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app`
diff --git a/.claude/skills/audit-tests/SKILL.md b/.claude/skills/audit-tests/SKILL.md
@@ -10,7 +10,7 @@ Check that unit tests exist and pass for permission-gated components. **Write mi
 - **Component testing**: `@testing-library/react` + `@testing-library/jest-dom`
 - **Setup**: `apps/app/src/test-utils/setup.ts`
 - **Permission mocks**: `apps/app/src/test-utils/mocks/permissions.ts`
-- **Run**: `cd apps/app && npx vitest run`
+- **Run**: `cd apps/app && bunx vitest run`
 
 ## Required Test Pattern
 
@@ -27,4 +27,4 @@ Use `setMockPermissions`, `ADMIN_PERMISSIONS`, `AUDITOR_PERMISSIONS` from test u
 2. Check for corresponding `.test.tsx` files
 3. Write missing tests following the pattern above
 4. Fix any failing tests
-5. Run: `cd apps/app && npx vitest run`
+5. Run: `cd apps/app && bunx vitest run`
diff --git a/.claude/skills/code/SKILL.md b/.claude/skills/code/SKILL.md
@@ -0,0 +1,185 @@
+---
+name: code
+description: "Use when writing TypeScript/React code - covers type safety, component patterns, and file organization"
+---
+
+Source Cursor rule: `.cursor/rules/code.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Code Standards
+
+## TypeScript
+
+### No `any`, No Unsafe Casts
+
+```tsx
+// ✅ Validate with zod
+const TaskSchema = z.object({ id: z.string(), title: z.string() });
+const task = TaskSchema.parse(response.data);
+
+// ✅ Use unknown and narrow
+const parseResponse = (data: unknown): Task => {
+  if (!isTask(data)) throw new Error('Invalid');
+  return data;
+};
+
+// ❌ Never
+const data: any = fetchData();
+const task = response as Task;
+const name = user!.name;
+// @ts-ignore
+```
+
+### Generics Over Any
+
+```tsx
+// ✅ Generic
+const first = <T>(items: T[]): T | undefined => items[0];
+
+// ❌ Any
+const first = (items: any[]): any => items[0];
+```
+
+## React Patterns
+
+### Named Exports, PascalCase
+
+```tsx
+// ✅ Named export, PascalCase file
+// TaskCard.tsx
+export function TaskCard({ task }: TaskCardProps) { ... }
+
+// ❌ Default export, lowercase
+export default function taskCard() { ... }
+```
+
+### Derive State, Avoid useEffect
+
+```tsx
+// ✅ Derived
+const completedCount = tasks.filter(t => t.completed).length;
+
+// ❌ Synced state
+const [count, setCount] = useState(0);
+useEffect(() => {
+  setCount(tasks.filter(t => t.completed).length);
+}, [tasks]);
+```
+
+### When useEffect IS Appropriate
+
+```tsx
+// External subscriptions
+useEffect(() => {
+  const sub = eventSource.subscribe(handler);
+  return () => sub.unsubscribe();
+}, []);
+
+// DOM measurements
+useEffect(() => {
+  setHeight(ref.current?.getBoundingClientRect().height);
+}, []);
+```
+
+### Toasts with Sonner
+
+```tsx
+import { toast } from 'sonner';
+
+toast.success('Task created');
+toast.error('Failed to save');
+toast.promise(saveTask(), {
+  loading: 'Saving...',
+  success: 'Saved!',
+  error: 'Failed',
+});
+```
+
+## File Structure
+
+### Colocate at Route Level
+
+```
+app/(app)/[orgId]/tasks/
+├── page.tsx              # Server component
+├── components/
+│   └── TaskList.tsx      # Client component
+├── hooks/
+│   └── useTasks.ts       # SWR hook
+└── data/
+    └── queries.ts        # Server queries
+```
+
+### Share Only When Reused 3+ Times
+
+```
+src/components/shared/    # Cross-page components
+src/hooks/                # Shared hooks (useApiSWR, useDebounce)
+```
+
+## Code Quality
+
+### File Size Limit: 300 Lines
+
+Split large files into focused components.
+
+### Named Parameters for 2+ Args
+
+```tsx
+// ✅ Named
+const createTask = ({ title, assigneeId }: CreateTaskParams) => { ... };
+createTask({ title: 'Review PR', assigneeId: user.id });
+
+// ❌ Positional
+const createTask = (title: string, assigneeId: string) => { ... };
+createTask('Review PR', user.id); // What's the 2nd param?
+```
+
+### Early Returns
+
+```tsx
+// ✅ Early return
+function processTask(task: Task | null) {
+  if (!task) return null;
+  if (task.deleted) return null;
+  return <TaskCard task={task} />;
+}
+
+// ❌ Nested
+function processTask(task) {
+  if (task) {
+    if (!task.deleted) {
+      return <TaskCard task={task} />;
+    }
+  }
+  return null;
+}
+```
+
+### Event Handler Naming
+
+```tsx
+// ✅ Prefix with "handle"
+const handleClick = () => { ... };
+const handleSubmit = (e: FormEvent) => { ... };
+const handleTaskCreate = (task: Task) => { ... };
+```
+
+## Accessibility
+
+```tsx
+// Interactive elements need keyboard support
+<div
+  role="button"
+  tabIndex={0}
+  onClick={handleClick}
+  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
+  aria-label="Delete task"
+>
+  <TrashIcon />
+</div>
+
+// Form inputs need labels
+<label htmlFor="task-name">Task Name</label>
+<input id="task-name" type="text" />
+```
diff --git a/.claude/skills/cursor-usage/SKILL.md b/.claude/skills/cursor-usage/SKILL.md
@@ -0,0 +1,269 @@
+---
+name: cursor-usage
+description: "How to write and manage Cursor rules - invoke with @cursor-usage"
+---
+
+Source Cursor rule: `.cursor/rules/cursor-usage.mdc`.
+Original file scope: `.cursor/rules/*.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Using Cursor Rules
+
+## Overview
+
+Cursor rules provide system-level instructions to the AI to maintain code consistency, quality, and adherence to project standards. They are stored in the `.cursor/rules/` directory as `.mdc` (Markdown with frontmatter) files.
+
+## Rule File Structure
+
+Each `.mdc` rule file consists of two parts:
+
+### 1. Frontmatter (YAML metadata)
+
+```yaml
+---
+description: Brief overview of what this rule enforces
+globs: **/*.{ts,tsx}
+alwaysApply: true
+---
+```
+
+**Frontmatter Fields:**
+
+- `description`: A clear, concise explanation of the rule's purpose
+- `globs`: Glob pattern to match files where this rule should apply (plain string, no quotes or arrays)
+  - Examples:
+    - `**/*.tsx` - All TSX files
+    - `**/*.{ts,tsx}` - All TS and TSX files
+    - `apps/*/components/**/*.tsx` - All TSX files in any app's components directory
+    - `**/trigger/**/*.ts` - All TS files in trigger directories
+- `alwaysApply`: Boolean indicating if the rule should always be active
+  - `true`: Rule is always active when working on matching files
+  - `false`: Rule can be selectively invoked with `@rule-name`
+
+### 2. Content (Markdown)
+
+The body of the rule file contains the actual guidelines, examples, and instructions written in Markdown format.
+
+## How Rules Are Applied
+
+### Automatic Application
+
+Rules with `alwaysApply: true` are automatically loaded when:
+
+- You open a file matching the `globs` pattern
+- You're working on code that matches the pattern
+- Cursor AI generates or suggests code for matching files
+
+### Manual Invocation
+
+You can reference specific rules in your prompts:
+
+```
+@design-system create a new button component
+```
+
+This explicitly tells Cursor to apply the design-system rule.
+
+## Best Practices for Writing Rules
+
+### 1. Keep Rules Focused
+
+- Each rule file should cover a specific domain (e.g., design system, API patterns, testing)
+- Avoid mixing unrelated concerns in a single rule file
+- Aim for rules under 500 lines for better AI comprehension
+
+### 2. Provide Concrete Examples
+
+Always include:
+
+- ✅ Good examples (what TO do)
+- ❌ Bad examples (what NOT to do)
+- Real code snippets from your project
+
+```tsx
+// ✅ Good: Use semantic tokens
+<div className="bg-background text-foreground">Content</div>
+
+// ❌ Bad: Hardcoded colors
+<div className="bg-white text-black">Content</div>
+```
+
+### 3. Use Clear Section Headers
+
+Organize content with descriptive headers:
+
+```markdown
+## Core Principles
+
+## Rules
+
+## Examples
+
+## Exceptions
+
+## Common Mistakes
+```
+
+### 4. Define Exceptions Explicitly
+
+If there are cases where rules don't apply, state them clearly:
+
+```markdown
+## Exceptions
+
+The ONLY time you can pass className to a design system component is for:
+
+1. Width utilities: `w-full`, `max-w-md`
+2. Responsive display: `hidden`, `md:block`
+```
+
+### 5. Include Checklists
+
+Provide actionable checklists for validation:
+
+```markdown
+## Code Review Checklist
+
+Before committing:
+
+- [ ] Uses semantic color tokens
+- [ ] Works in both light and dark mode
+- [ ] Fully responsive
+```
+
+## Managing Rules
+
+### Creating a New Rule
+
+1. Create a new `.mdc` file in `.cursor/rules/`
+2. Add appropriate frontmatter
+3. Write clear guidelines with examples
+4. Test by working on matching files
+
+### Updating Existing Rules
+
+1. Edit the `.mdc` file
+2. Rules are automatically reloaded
+3. Test changes with relevant files
+
+### Organizing Rules
+
+Recommended structure:
+
+```
+.cursor/rules/
+├── design-system.mdc       # Component usage, variants, composition
+├── code-standards.mdc      # General code quality rules
+├── typescript-rules.mdc    # TypeScript type safety
+├── react-code.mdc          # React patterns and conventions
+├── data-fetching.mdc       # Server/client data patterns
+└── cursor-usage.mdc        # This file - how to use rules
+```
+
+## Rule Scope with Globs
+
+### Common Glob Patterns
+
+```yaml
+# All TypeScript/TSX files
+globs: **/*.{ts,tsx}
+
+# Only TSX files (React components)
+globs: **/*.tsx
+
+# Only trigger task files
+globs: **/trigger/**/*.ts
+
+# Prisma schema files
+globs: **/*.prisma
+
+# All JSON and TypeScript files
+globs: **/*.{ts,tsx,json}
+```
+
+### Glob Pattern Tips
+
+- Use `**` for recursive directory matching
+- Use `*` for single-level wildcard
+- Use `{ts,tsx}` for multiple extensions
+- No quotes or array brackets needed
+- Be specific to avoid over-applying rules
+
+## Debugging Rules
+
+### Rule Not Applying?
+
+1. Check the `globs` pattern matches your file
+2. Verify frontmatter YAML syntax is correct
+3. Ensure `alwaysApply` is set appropriately
+4. Try manually invoking with `@ruleName`
+
+### Rule Conflicting?
+
+1. Check if multiple rules apply to the same files
+2. Make rules more specific with tighter `globs`
+3. Consolidate related rules into one file
+
+## Advanced Features
+
+### Conditional Rules
+
+Use `alwaysApply: false` for rules that should only apply in specific contexts:
+
+```yaml
+---
+description: Performance optimization guidelines
+globs: **/*.ts
+alwaysApply: false
+---
+```
+
+Invoke with: `@performance-optimization refactor this component`
+
+### Hierarchical Rules
+
+More specific globs take precedence:
+
+- `design-system.mdc` with `globs: **/*.tsx` (broad)
+- `trigger.basic.mdc` with `globs: **/trigger/**/*.ts` (specific)
+
+The specific rule will have more weight for trigger files.
+
+## Quick Reference
+
+### Create a New Rule
+
+```bash
+touch .cursor/rules/my-new-rule.mdc
+```
+
+```yaml
+---
+description: What this rule enforces
+globs: **/*.{ts,tsx}
+alwaysApply: true
+---
+
+# Rule Title
+
+## Guidelines
+
+- Point 1
+- Point 2
+```
+
+### Apply a Rule
+
+- Automatic: Save a file matching the `globs` pattern
+- Manual: Use `@my-new-rule` in your prompt
+
+### Debug a Rule
+
+1. Check file matches `globs` pattern
+2. Verify YAML frontmatter syntax
+3. Look for conflicting rules
+4. Try manual invocation
+
+---
+
+**Remember**: Rules are here to help, not hinder. If a rule doesn't make sense for a specific case, discuss with the team and update the rule accordingly.
diff --git a/.claude/skills/data/SKILL.md b/.claude/skills/data/SKILL.md
@@ -0,0 +1,146 @@
+---
+name: data
+description: "Use when implementing data fetching, API calls, server/client components, or SWR hooks"
+---
+
+Source Cursor rule: `.cursor/rules/data.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Data Fetching
+
+## Core Pattern: Server → Client → SWR
+
+### 1. Server Page Fetches Data
+
+```tsx
+// app/(app)/[orgId]/tasks/page.tsx
+export default async function TasksPage({ params }: { params: Promise<{ orgId: string }> }) {
+  const { orgId } = await params; // From URL, NOT session
+  const tasks = await getTasks(orgId);
+  return <TaskListClient organizationId={orgId} initialTasks={tasks} />;
+}
+```
+
+### 2. Client Component Receives Initial Data
+
+```tsx
+// components/TaskListClient.tsx
+'use client';
+
+export function TaskListClient({ organizationId, initialTasks }: Props) {
+  const { tasks, createTask, updateTask } = useTasks({
+    organizationId,
+    initialData: initialTasks,
+  });
+  // Initial render is instant - no loading state
+}
+```
+
+### 3. SWR Hook with fallbackData
+
+```tsx
+// hooks/useTasks.ts
+export function useTasks({ organizationId, initialData }: UseTasksOptions) {
+  const { data, mutate } = useSWR(
+    ['/v1/tasks', organizationId], // Include orgId for cache isolation
+    async ([endpoint, orgId]) => {
+      const response = await apiClient.get(endpoint, orgId);
+      return response.data?.tasks ?? [];
+    },
+    { fallbackData: initialData }
+  );
+
+  const createTask = async (input: CreateTaskInput) => {
+    await apiClient.post('/v1/tasks', input, organizationId);
+    mutate(); // Revalidate
+  };
+
+  const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {
+    await apiClient.put(`/v1/tasks/${taskId}`, input, organizationId);
+    mutate(); // Revalidate
+  };
+
+  return { tasks: data ?? [], createTask, updateTask, mutate };
+}
+```
+
+## API Client
+
+Use `apiClient` from `@/lib/api-client`:
+
+```tsx
+import { apiClient } from '@/lib/api-client';
+
+await apiClient.get<ResponseType>('/v1/endpoint', organizationId);
+await apiClient.post<ResponseType>('/v1/endpoint', body, organizationId);
+await apiClient.put<ResponseType>('/v1/endpoint', body, organizationId);
+await apiClient.delete('/v1/endpoint', organizationId);
+```
+
+## Server vs Client Components
+
+**Layouts = server.** Interactive logic in separate client components.
+
+```tsx
+// layout.tsx (server)
+export default function Layout({ children }) {
+  return (
+    <PageLayout>
+      <PageHeader title="Title" />
+      <ClientTabs /> {/* Client component */}
+      {children}
+    </PageLayout>
+  );
+}
+
+// components/ClientTabs.tsx
+'use client';
+export function ClientTabs() {
+  const router = useRouter();
+  // Interactive logic here
+}
+```
+
+## State Management
+
+**No `nuqs`** - use React state or Next.js patterns:
+
+```tsx
+// ✅ React state for UI
+const [isOpen, setIsOpen] = useState(false);
+
+// ✅ Next.js for URL state
+const router = useRouter();
+const searchParams = useSearchParams();
+
+// ❌ No nuqs
+import { useQueryState } from 'nuqs';
+```
+
+## Rules
+
+```tsx
+// ✅ Always
+const { orgId } = await params;                    // From URL params
+const { data } = useSWR(key, f, { fallbackData }); // With initial data
+await apiClient.get('/v1/endpoint', orgId);        // Use apiClient
+useSWR(['/v1/tasks', orgId], fetcher);            // Include orgId in key
+
+// ❌ Never
+const orgId = session?.activeOrganizationId;       // From session
+const { data } = useSWR('/api/data');              // No initial data
+await fetch('/api/endpoint');                      // Direct fetch
+```
+
+## File Structure
+
+```
+app/(app)/[orgId]/tasks/
+├── page.tsx                 # Server - fetches data
+├── components/
+│   └── TaskListClient.tsx   # Client - receives initialData
+├── hooks/
+│   └── useTasks.ts          # SWR hook with mutations
+└── data/
+    └── queries.ts           # Server-side queries
+```
diff --git a/.claude/skills/essentials/SKILL.md b/.claude/skills/essentials/SKILL.md
@@ -0,0 +1,108 @@
+---
+name: essentials
+description: "Critical rules that must always be followed"
+---
+
+Source Cursor rule: `.cursor/rules/essentials.mdc`.
+Original file scope: `**/*.{ts,tsx}`.
+Original Cursor alwaysApply: `true`.
+
+# Essentials
+
+## Package Manager
+
+Use `bun`, never npm/yarn/pnpm.
+
+```bash
+bun install          # Install deps
+bun add <pkg>        # Add package
+bun run <script>     # Run script
+bunx <cmd>           # Execute binary
+```
+
+## Components
+
+**Use `@trycompai/design-system` first**, `@trycompai/ui` only as fallback.
+
+```tsx
+// ✅ Design system
+import { Button, Card, Input, Select } from '@trycompai/design-system';
+import { Add, Close } from '@trycompai/design-system/icons';
+
+// ❌ Don't use when DS has the component
+import { Button } from '@trycompai/ui/button';
+import { Plus } from 'lucide-react';
+```
+
+**No `className` on DS components** - use variants and props only.
+
+```tsx
+// ✅ Use variants
+<Button variant="destructive" size="sm">Delete</Button>
+
+// ❌ No className overrides
+<Button className="bg-red-500">Delete</Button>
+```
+
+## TypeScript
+
+**No `any`. No unsafe type assertions.**
+
+```tsx
+// ✅ Validate external data with zod
+const TaskSchema = z.object({ id: z.string(), title: z.string() });
+const task = TaskSchema.parse(response.data);
+
+// ❌ Never
+const data: any = fetchData();
+const task = response as Task;
+```
+
+## Data Fetching
+
+**Get `organizationId` from URL params, not session.**
+
+```tsx
+// ✅ From params
+export default async function Page({ params }: { params: Promise<{ orgId: string }> }) {
+  const { orgId } = await params;
+}
+
+// ❌ Not from session
+const session = await auth.api.getSession();
+const orgId = session?.session?.activeOrganizationId;
+```
+
+**Server components fetch, pass to client with SWR `fallbackData`.**
+
+```tsx
+// Server page
+const data = await fetchData(orgId);
+return <ClientComponent initialData={data} />;
+
+// Client component
+const { data } = useSWR(key, fetcher, { fallbackData: initialData });
+```
+
+## State Management
+
+**No `nuqs`** - use React `useState` for UI state, Next.js for URL state.
+
+```tsx
+// ✅ React state for UI
+const [isOpen, setIsOpen] = useState(false);
+
+// ❌ No nuqs
+import { useQueryState } from 'nuqs';
+```
+
+## After Changes
+
+**Always run checks after code changes:**
+
+```bash
+bun run typecheck
+bun run lint
+```
+
+Fix all errors before committing.
diff --git a/.claude/skills/forms/SKILL.md b/.claude/skills/forms/SKILL.md
@@ -0,0 +1,180 @@
+---
+name: forms
+description: "Use when building forms - covers React Hook Form, Zod validation, and form patterns"
+---
+
+Source Cursor rule: `.cursor/rules/forms.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Forms: React Hook Form + Zod
+
+**All forms MUST use React Hook Form with Zod validation.**
+
+## Basic Pattern
+
+```tsx
+import { zodResolver } from '@hookform/resolvers/zod';
+import { useForm } from 'react-hook-form';
+import { z } from 'zod';
+import { Button, Input } from '@trycompai/design-system';
+
+// 1. Define schema
+const formSchema = z.object({
+  email: z.string().email('Invalid email'),
+  password: z.string().min(8, 'Min 8 characters'),
+});
+
+// 2. Infer type
+type FormData = z.infer<typeof formSchema>;
+
+// 3. Use in component
+function MyForm() {
+  const {
+    register,
+    handleSubmit,
+    formState: { errors, isSubmitting },
+  } = useForm<FormData>({
+    resolver: zodResolver(formSchema),
+  });
+
+  return (
+    <form onSubmit={handleSubmit(onSubmit)}>
+      <Input {...register('email')} />
+      {errors.email && <p>{errors.email.message}</p>}
+      
+      <Button type="submit" loading={isSubmitting}>
+        Submit
+      </Button>
+    </form>
+  );
+}
+```
+
+## Zod Schema Patterns
+
+```tsx
+const profileSchema = z.object({
+  // Strings
+  name: z.string().min(1, 'Required'),
+  email: z.string().email(),
+  website: z.string().url().optional(),
+  
+  // Numbers (coerce for inputs)
+  age: z.coerce.number().int().min(0),
+  price: z.coerce.number().positive(),
+  
+  // Arrays
+  tags: z.array(z.string()).min(1),
+  
+  // Enums
+  status: z.enum(['active', 'inactive']),
+});
+
+// Cross-field validation
+const passwordSchema = z.object({
+  password: z.string().min(8),
+  confirmPassword: z.string(),
+}).refine(d => d.password === d.confirmPassword, {
+  message: "Passwords don't match",
+  path: ['confirmPassword'],
+});
+```
+
+## Controller for Complex Components
+
+```tsx
+import { Controller } from 'react-hook-form';
+import { Select, SelectContent, SelectItem, SelectTrigger } from '@trycompai/design-system';
+
+<Controller
+  name="status"
+  control={control}
+  render={({ field }) => (
+    <Select onValueChange={field.onChange} value={field.value}>
+      <SelectTrigger>{field.value || 'Select...'}</SelectTrigger>
+      <SelectContent>
+        <SelectItem value="active">Active</SelectItem>
+        <SelectItem value="inactive">Inactive</SelectItem>
+      </SelectContent>
+    </Select>
+  )}
+/>
+```
+
+## Form State
+
+```tsx
+const {
+  register,
+  handleSubmit,
+  control,
+  watch,           // Watch field values
+  setValue,        // Set field programmatically
+  reset,           // Reset form
+  setError,        // Set error manually
+  formState: {
+    errors,        // Field errors
+    isSubmitting,  // Submitting
+    isValid,       // All valid
+    isDirty,       // Modified
+  },
+} = useForm<FormData>({
+  resolver: zodResolver(schema),
+  mode: 'onChange', // Validate on change
+});
+```
+
+## Error Handling
+
+```tsx
+const onSubmit = async (data: FormData) => {
+  try {
+    await submitToApi(data);
+  } catch (error) {
+    // Field-specific error
+    setError('email', { message: 'Email taken' });
+    // Or root error
+    setError('root', { message: 'Something went wrong' });
+  }
+};
+
+// Display root error
+{errors.root && <p>{errors.root.message}</p>}
+```
+
+## Dynamic Fields
+
+```tsx
+import { useFieldArray } from 'react-hook-form';
+
+const { fields, append, remove } = useFieldArray({
+  control,
+  name: 'items',
+});
+
+{fields.map((field, index) => (
+  <div key={field.id}>
+    <Input {...register(`items.${index}.name`)} />
+    <Button type="button" onClick={() => remove(index)}>Remove</Button>
+  </div>
+))}
+<Button type="button" onClick={() => append({ name: '' })}>Add</Button>
+```
+
+## Anti-Patterns
+
+```tsx
+// ❌ useState for form fields
+const [email, setEmail] = useState('');
+
+// ❌ Manual validation
+if (email.length < 5) setError('Too short');
+
+// ❌ Missing button type (defaults to submit)
+<Button onClick={handleCancel}>Cancel</Button>
+
+// ✅ Correct
+const { register } = useForm();
+const schema = z.object({ email: z.string().min(5) });
+<Button type="button" onClick={handleCancel}>Cancel</Button>
+```
diff --git a/.claude/skills/infra/SKILL.md b/.claude/skills/infra/SKILL.md
@@ -0,0 +1,135 @@
+---
+name: infra
+description: "Use when working with packages, dependencies, monorepo structure, or build configuration"
+---
+
+Source Cursor rule: `.cursor/rules/infra.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Infrastructure
+
+## Package Manager
+
+**Use `bun`, never npm/yarn/pnpm.**
+
+```bash
+bun install              # Install deps
+bun add <pkg>            # Add package
+bun add -D <pkg>         # Add dev dependency
+bun run <script>         # Run script
+bunx <cmd>               # Execute binary
+```
+
+## Monorepo Structure
+
+```
+comp/
+├── apps/
+│   ├── api/             # NestJS backend
+│   ├── app/             # Next.js main app
+│   └── portal/          # Next.js portal
+├── packages/
+│   ├── db/              # Prisma (@trycompai/db)
+│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system
+│   └── ...
+├── turbo.json
+└── package.json
+```
+
+## Running Commands
+
+```bash
+# Multi-package (via turbo)
+bun run build            # Build all
+bun run lint             # Lint all
+bun run typecheck        # Type check all
+bun run dev              # Dev all
+
+# Single package
+bun run -F apps/app dev
+bun run -F @trycompai/db prisma:generate
+turbo build --filter=@trycompai/ui
+```
+
+## Importing Between Packages
+
+```tsx
+// ✅ Import from package name
+import { Button } from '@trycompai/design-system';
+import { prisma } from '@trycompai/db';
+
+// ❌ Never relative paths across packages
+import { Button } from '../../../packages/ui/src/button';
+```
+
+## Adding Dependencies
+
+```bash
+# To specific package
+bun add axios -F apps/app
+bun add -D vitest -F @trycompai/ui
+
+# To root (dev tools only)
+bun add -D -w prettier typescript
+```
+
+## After Code Changes
+
+**Always run checks:**
+
+```bash
+bun run typecheck
+bun run lint
+```
+
+Fix all errors before committing.
+
+## Common TypeScript Fixes
+
+- **Property does not exist**: Check interface definitions
+- **Type mismatch**: Verify expected vs actual type
+- **Empty interface extends**: Use `type X = SomeType` instead
+
+## Common ESLint Fixes
+
+- **Unused variables**: Remove or prefix with `_`
+- **Any type**: Add proper typing
+- **Empty object type**: Use `type` instead of `interface`
+
+## Creating a New Package
+
+```bash
+mkdir packages/my-package
+```
+
+```json
+// packages/my-package/package.json
+{
+  "name": "@trycompai/my-package",
+  "version": "0.0.0",
+  "private": true,
+  "main": "./src/index.ts",
+  "scripts": {
+    "build": "tsup src/index.ts --format cjs,esm --dts",
+    "typecheck": "tsc --noEmit"
+  }
+}
+```
+
+```json
+// packages/my-package/tsconfig.json
+{
+  "extends": "@trycompai/tsconfig/base.json",
+  "include": ["src"]
+}
+```
+
+## Package Boundaries
+
+**✅ Create packages for:**
+- Code used by 2+ apps
+- Self-contained, focused functionality
+
+**❌ Don't create packages for:**
+- Code only used in one app (colocate instead)
+- App-specific business logic
diff --git a/.claude/skills/new-feature-setup/SKILL.md b/.claude/skills/new-feature-setup/SKILL.md
@@ -69,7 +69,7 @@ Standard repo conventions apply (see `CLAUDE.md`). Highlights:
 - Brainstorm before building new UX (`superpowers:brainstorming`)
 - Plans + subagent-driven execution for multi-step work
 - Run `audit-design-system` after any frontend component edit
-- Always run typecheck before declaring a change done (`npx turbo run typecheck --filter=<pkg>`)
+- Always run typecheck before declaring a change done (`bunx turbo run typecheck --filter=<pkg>`)
 
 ### 5. When done, clean up
 
diff --git a/.claude/skills/prisma/SKILL.md b/.claude/skills/prisma/SKILL.md
@@ -0,0 +1,148 @@
+---
+name: prisma
+description: "Prisma schema conventions and migration workflow"
+---
+
+Source Cursor rule: `.cursor/rules/prisma.mdc`.
+Original file scope: `**/*.prisma`.
+Original Cursor alwaysApply: `false`.
+
+# Prisma Schema
+
+## Migration Workflow
+
+**Schema changes happen in `packages/db`, then regenerate types in each app.**
+
+### Step 1: Edit Schema
+
+```bash
+# Schema files are in packages/db/prisma/schema/
+packages/db/prisma/schema/
+├── schema.prisma      # Main schema with datasource
+├── user.prisma        # User models
+├── task.prisma        # Task models
+└── ...
+```
+
+### Step 2: Create Migration
+
+```bash
+# Run from packages/db
+cd packages/db
+bunx prisma migrate dev --name your_migration_name
+```
+
+### Step 3: Regenerate Types in Apps
+
+```bash
+# Each app needs to regenerate Prisma client types
+bun run -F apps/app db:generate
+bun run -F apps/api db:generate
+bun run -F apps/portal db:generate
+
+# Or from root (if configured)
+bun run prisma:generate
+```
+
+### ✅ Always Do This
+
+```bash
+# 1. Make schema changes in packages/db
+# 2. Create migration
+cd packages/db && bunx prisma migrate dev --name add_user_role
+
+# 3. Regenerate types in ALL apps that use the db
+bun run -F apps/app db:generate
+bun run -F apps/api db:generate
+bun run -F apps/portal db:generate
+```
+
+### ❌ Never Do This
+
+```bash
+# Don't edit schema in app directories
+apps/app/prisma/schema.prisma  # ❌ Wrong location
+
+# Don't forget to regenerate types
+bunx prisma migrate dev  # ✅ Created migration
+# ... forgot to run db:generate in apps  # ❌ Types out of sync
+```
+
+## Core Rule
+
+**Always use prefixed CUIDs for IDs** using `generate_prefixed_cuid`.
+
+## ID Pattern
+
+### ✅ Always Do This
+
+```prisma
+model User {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('usr'::text)"))
+  // ... other fields
+}
+
+model Task {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('tsk'::text)"))
+  // ... other fields
+}
+
+model Organization {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('org'::text)"))
+  // ... other fields
+}
+```
+
+### ❌ Never Do This
+
+```prisma
+// Don't use UUID
+model User {
+  id String @id @default(uuid())
+}
+
+// Don't use auto-increment
+model User {
+  id Int @id @default(autoincrement())
+}
+
+// Don't forget ::text cast
+model User {
+  id String @id @default(dbgenerated("generate_prefixed_cuid('usr')")) // ❌ Missing ::text
+}
+```
+
+## Prefix Guidelines
+
+| Entity       | Prefix | Example ID                     |
+| ------------ | ------ | ------------------------------ |
+| User         | `usr`  | `usr_BJRIZLgRPuWt8MvMjkSY82f1` |
+| Organization | `org`  | `org_cK9xMnPqRs2tUvWx3yZa4b5c` |
+| Task         | `tsk`  | `tsk_dE6fGhIj7kLmNoP8qRsT9uVw` |
+| Control      | `ctl`  | `ctl_xY0zAaBb1cDdEe2fFgGh3iIj` |
+| Policy       | `pol`  | `pol_kK4lLmMn5oOpPq6rRsSt7uUv` |
+
+## Rules
+
+1. **Short prefixes** - Use 2-3 characters
+2. **Unique prefixes** - Each model gets its own prefix
+3. **Always cast** - Include `::text` in the function call
+4. **Use dbgenerated** - Wrap the function call in `dbgenerated()`
+
+## Benefits
+
+- Human-readable IDs at a glance (`usr_` vs `org_`)
+- Easy debugging in logs
+- Safe to expose in URLs
+- Unique across all tables
+
+## Checklist
+
+After schema changes:
+
+- [ ] Schema edited in `packages/db/prisma/schema/`
+- [ ] Migration created with `bunx prisma migrate dev`
+- [ ] Types regenerated in `apps/app` with `db:generate`
+- [ ] Types regenerated in `apps/api` with `db:generate`
+- [ ] Types regenerated in `apps/portal` with `db:generate`
+- [ ] New models use prefixed CUID IDs
diff --git a/.claude/skills/production-readiness/SKILL.md b/.claude/skills/production-readiness/SKILL.md
@@ -14,8 +14,8 @@ Use parallel subagents to run all four audits simultaneously:
 
 Then run full monorepo verification:
 ```bash
-npx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app
-cd apps/app && npx vitest run
+bunx turbo run typecheck --filter=@trycompai/api --filter=@trycompai/app
+cd apps/app && bunx vitest run
 ```
 
 Output a Production Readiness Report summarizing all fixes applied and build status.
diff --git a/.claude/skills/prompt-engineering/SKILL.md b/.claude/skills/prompt-engineering/SKILL.md
@@ -0,0 +1,187 @@
+---
+name: prompt-engineering
+description: "Prompt engineering best practices - invoke with @prompt-engineering"
+---
+
+Source Cursor rule: `.cursor/rules/prompt-engineering.mdc`.
+Original file scope: `.cursor/rules/*.mdc`.
+Original Cursor alwaysApply: `false`.
+
+# Prompt Engineering Best Practices
+
+Based on [Claude's Prompt Engineering Documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
+
+## Core Principles
+
+### 1. Define Success Criteria First
+
+Before writing prompts:
+
+- **Establish clear objectives**: What constitutes a successful response?
+- **Create evaluation metrics**: How will you measure prompt effectiveness?
+- **Draft and iterate**: Start with a first draft and refine based on results
+
+### 2. When to Use Prompt Engineering vs Fine-tuning
+
+Prompt engineering is preferred because:
+
+- **Resource efficient**: Only requires text input, no GPUs
+- **Cost effective**: Uses base model pricing
+- **Maintains updates**: Works across model versions
+- **Time saving**: Instant results vs hours/days for fine-tuning
+- **Minimal data needs**: Works with zero-shot or few-shot
+- **Flexible iteration**: Quick experimentation cycle
+- **Preserves knowledge**: No catastrophic forgetting
+- **Transparent**: Human-readable, easy to debug
+
+---
+
+## The 6 Core Techniques
+
+### 1. Be Clear and Direct
+
+**Principle**: Provide explicit, unambiguous instructions.
+
+```
+❌ Bad: "Tell me about it"
+✅ Good: "Summarize the following article in three bullet points, focusing on key findings"
+
+❌ Bad: "Help with code"
+✅ Good: "Debug this Python function that should return the sum of even numbers in a list"
+```
+
+**Tips**:
+
+- State the task explicitly at the start
+- Specify the desired output format (bullet points, JSON, paragraphs)
+- Include constraints (word count, tone, audience)
+- Mention what to include AND what to exclude
+
+### 2. Use Examples (Multishot Prompting)
+
+**Principle**: Show the model what you want through examples.
+
+```xml
+<examples>
+  <example>
+    <input>The movie was absolutely terrible, waste of time</input>
+    <output>{"sentiment": "negative", "confidence": 0.95}</output>
+  </example>
+  <example>
+    <input>Decent film, not great but watchable</input>
+    <output>{"sentiment": "neutral", "confidence": 0.7}</output>
+  </example>
+  <example>
+    <input>Best movie I've seen this year!</input>
+    <output>{"sentiment": "positive", "confidence": 0.9}</output>
+  </example>
+</examples>
+
+Now analyze: "The special effects were amazing but the plot was confusing"
+```
+
+**Tips**:
+
+- Include 3-5 diverse examples covering edge cases
+- Show examples of BOTH good and bad outputs
+- Match example complexity to your actual use case
+- Order examples from simple to complex
+
+### 3. Let Claude Think (Chain of Thought)
+
+**Principle**: Encourage step-by-step reasoning for complex tasks.
+
+```xml
+<instruction>
+Solve this problem step by step. Show your reasoning before giving the final answer.
+</instruction>
+
+<problem>
+A train leaves Station A at 9:00 AM traveling at 60 mph. Another train leaves
+Station B at 10:00 AM traveling at 80 mph toward Station A. The stations are
+280 miles apart. When will the trains meet?
+</problem>
+
+<thinking>
+[Let Claude work through the problem here]
+</thinking>
+
+<answer>
+[Final answer after reasoning]
+</answer>
+```
+
+**Tips**:
+
+- Use phrases like "Think step by step" or "Explain your reasoning"
+- For complex tasks, explicitly request a thinking section
+- Chain of thought improves accuracy on math, logic, and multi-step problems
+- Can use `<thinking>` tags to separate reasoning from output
+
+### 4. Use XML Tags
+
+**Principle**: Structure prompts with clear delimiters for better parsing.
+
+```xml
+<context>
+You are helping debug a penetration testing tool that automates security scans.
+</context>
+
+<task>
+Analyze the following error log and identify the root cause.
+</task>
+
+<error_log>
+[2024-01-15 10:23:45] ERROR: Connection timeout after 30s
+[2024-01-15 10:23:45] DEBUG: Target: 192.168.1.1:443
+[2024-01-15 10:23:45] DEBUG: Retry attempt 3 of 3
+</error_log>
+
+<output_format>
+Provide your analysis in this format:
+- Root cause: [one sentence]
+- Evidence: [relevant log lines]
+- Recommended fix: [actionable steps]
+</output_format>
+```
+
+**Common XML Tags**:
+
+- `<context>` - Background information
+- `<task>` or `<instruction>` - What to do
+- `<examples>` - Sample inputs/outputs
+- `<constraints>` - Limitations or rules
+- `<output_format>` - Expected response structure
+- `<thinking>` - Reasoning section
+- `<answer>` - Final response
+
+### 5. Give Claude a Role (System Prompts)
+
+**Principle**: Assign a persona to influence response style and expertise.
+
+```xml
+<role>
+You are a senior security researcher with 15 years of experience in penetration
+testing. You specialize in web application security and have discovered multiple
+CVEs. You communicate findings clearly and prioritize actionable recommendations.
+</role>
+
+<task>
+Review this HTTP response and identify potential security vulnerabilities.
+</task>
+```
+
+**Effective Role Elements**:
+
+- Expertise level (senior, expert, specialist)
+- Domain knowledge (security, finance, medicine)
+- Communication style (technical, friendly, formal)
+- Priorities (accuracy, brevity, thoroughness)
+
+### 6. Prefill Claude's Response
+
+**Principle**: Start the response to guide format and direction.
+
+```
+Human: List the top 3 security vulnerabilities in this code.
+```
diff --git a/.claude/skills/trigger-advanced-tasks/SKILL.md b/.claude/skills/trigger-advanced-tasks/SKILL.md
@@ -0,0 +1,460 @@
+---
+name: trigger-advanced-tasks
+description: "Comprehensive rules to help you write advanced Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.advanced-tasks.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Advanced Tasks (v4)
+
+**Advanced patterns and features for writing tasks**
+
+## Tags & Organization
+
+```ts
+import { task, tags } from '@trigger.dev/sdk';
+
+export const processUser = task({
+  id: 'process-user',
+  run: async (payload: { userId: string; orgId: string }, { ctx }) => {
+    // Add tags during execution
+    await tags.add(`user_${payload.userId}`);
+    await tags.add(`org_${payload.orgId}`);
+
+    return { processed: true };
+  },
+});
+
+// Trigger with tags
+await processUser.trigger(
+  { userId: '123', orgId: 'abc' },
+  { tags: ['priority', 'user_123', 'org_abc'] }, // Max 10 tags per run
+);
+
+// Subscribe to tagged runs
+for await (const run of runs.subscribeToRunsWithTag('user_123')) {
+  console.log(`User task ${run.id}: ${run.status}`);
+}
+```
+
+**Tag Best Practices:**
+
+- Use prefixes: `user_123`, `org_abc`, `video:456`
+- Max 10 tags per run, 1-128 characters each
+- Tags don't propagate to child tasks automatically
+
+## Concurrency & Queues
+
+```ts
+import { task, queue } from '@trigger.dev/sdk';
+
+// Shared queue for related tasks
+const emailQueue = queue({
+  name: 'email-processing',
+  concurrencyLimit: 5, // Max 5 emails processing simultaneously
+});
+
+// Task-level concurrency
+export const oneAtATime = task({
+  id: 'sequential-task',
+  queue: { concurrencyLimit: 1 }, // Process one at a time
+  run: async (payload) => {
+    // Critical section - only one instance runs
+  },
+});
+
+// Per-user concurrency
+export const processUserData = task({
+  id: 'process-user-data',
+  run: async (payload: { userId: string }) => {
+    // Override queue with user-specific concurrency
+    await childTask.trigger(payload, {
+      queue: {
+        name: `user-${payload.userId}`,
+        concurrencyLimit: 2,
+      },
+    });
+  },
+});
+
+export const emailTask = task({
+  id: 'send-email',
+  queue: emailQueue, // Use shared queue
+  run: async (payload: { to: string }) => {
+    // Send email logic
+  },
+});
+```
+
+## Error Handling & Retries
+
+```ts
+import { task, retry, AbortTaskRunError } from '@trigger.dev/sdk';
+
+export const resilientTask = task({
+  id: 'resilient-task',
+  retry: {
+    maxAttempts: 10,
+    factor: 1.8, // Exponential backoff multiplier
+    minTimeoutInMs: 500,
+    maxTimeoutInMs: 30_000,
+    randomize: false,
+  },
+  catchError: async ({ error, ctx }) => {
+    // Custom error handling
+    if (error.code === 'FATAL_ERROR') {
+      throw new AbortTaskRunError('Cannot retry this error');
+    }
+
+    // Log error details
+    console.error(`Task ${ctx.task.id} failed:`, error);
+
+    // Allow retry by returning nothing
+    return { retryAt: new Date(Date.now() + 60000) }; // Retry in 1 minute
+  },
+  run: async (payload) => {
+    // Retry specific operations
+    const result = await retry.onThrow(
+      async () => {
+        return await unstableApiCall(payload);
+      },
+      { maxAttempts: 3 },
+    );
+
+    // Conditional HTTP retries
+    const response = await retry.fetch('https://api.example.com', {
+      retry: {
+        maxAttempts: 5,
+        condition: (response, error) => {
+          return response?.status === 429 || response?.status >= 500;
+        },
+      },
+    });
+
+    return result;
+  },
+});
+```
+
+## Machines & Performance
+
+```ts
+export const heavyTask = task({
+  id: 'heavy-computation',
+  machine: { preset: 'large-2x' }, // 8 vCPU, 16 GB RAM
+  maxDuration: 1800, // 30 minutes timeout
+  run: async (payload, { ctx }) => {
+    // Resource-intensive computation
+    if (ctx.machine.preset === 'large-2x') {
+      // Use all available cores
+      return await parallelProcessing(payload);
+    }
+
+    return await standardProcessing(payload);
+  },
+});
+
+// Override machine when triggering
+await heavyTask.trigger(payload, {
+  machine: { preset: 'medium-1x' }, // Override for this run
+});
+```
+
+**Machine Presets:**
+
+- `micro`: 0.25 vCPU, 0.25 GB RAM
+- `small-1x`: 0.5 vCPU, 0.5 GB RAM (default)
+- `small-2x`: 1 vCPU, 1 GB RAM
+- `medium-1x`: 1 vCPU, 2 GB RAM
+- `medium-2x`: 2 vCPU, 4 GB RAM
+- `large-1x`: 4 vCPU, 8 GB RAM
+- `large-2x`: 8 vCPU, 16 GB RAM
+
+## Idempotency
+
+```ts
+import { task, idempotencyKeys } from '@trigger.dev/sdk';
+
+export const paymentTask = task({
+  id: 'process-payment',
+  retry: {
+    maxAttempts: 3,
+  },
+  run: async (payload: { orderId: string; amount: number }) => {
+    // Automatically scoped to this task run, so if the task is retried, the idempotency key will be the same
+    const idempotencyKey = await idempotencyKeys.create(`payment-${payload.orderId}`);
+
+    // Ensure payment is processed only once
+    await chargeCustomer.trigger(payload, {
+      idempotencyKey,
+      idempotencyKeyTTL: '24h', // Key expires in 24 hours
+    });
+  },
+});
+
+// Payload-based idempotency
+import { createHash } from 'node:crypto';
+
+function createPayloadHash(payload: any): string {
+  const hash = createHash('sha256');
+  hash.update(JSON.stringify(payload));
+  return hash.digest('hex');
+}
+
+export const deduplicatedTask = task({
+  id: 'deduplicated-task',
+  run: async (payload) => {
+    const payloadHash = createPayloadHash(payload);
+    const idempotencyKey = await idempotencyKeys.create(payloadHash);
+
+    await processData.trigger(payload, { idempotencyKey });
+  },
+});
+```
+
+## Metadata & Progress Tracking
+
+```ts
+import { task, metadata } from '@trigger.dev/sdk';
+
+export const batchProcessor = task({
+  id: 'batch-processor',
+  run: async (payload: { items: any[] }, { ctx }) => {
+    const totalItems = payload.items.length;
+
+    // Initialize progress metadata
+    metadata
+      .set('progress', 0)
+      .set('totalItems', totalItems)
+      .set('processedItems', 0)
+      .set('status', 'starting');
+
+    const results = [];
+
+    for (let i = 0; i < payload.items.length; i++) {
+      const item = payload.items[i];
+
+      // Process item
+      const result = await processItem(item);
+      results.push(result);
+
+      // Update progress
+      const progress = ((i + 1) / totalItems) * 100;
+      metadata
+        .set('progress', progress)
+        .increment('processedItems', 1)
+        .append('logs', `Processed item ${i + 1}/${totalItems}`)
+        .set('currentItem', item.id);
+    }
+
+    // Final status
+    metadata.set('status', 'completed');
+
+    return { results, totalProcessed: results.length };
+  },
+});
+
+// Update parent metadata from child task
+export const childTask = task({
+  id: 'child-task',
+  run: async (payload, { ctx }) => {
+    // Update parent task metadata
+    metadata.parent.set('childStatus', 'processing');
+    metadata.root.increment('childrenCompleted', 1);
+
+    return { processed: true };
+  },
+});
+```
+
+## Advanced Triggering
+
+### Frontend Triggering (React)
+
+```tsx
+'use client';
+import { useTaskTrigger } from '@trigger.dev/react-hooks';
+import type { myTask } from '../trigger/tasks';
+
+function TriggerButton({ accessToken }: { accessToken: string }) {
+  const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>('my-task', { accessToken });
+
+  return (
+    <button onClick={() => submit({ data: 'from frontend' })} disabled={isLoading}>
+      Trigger Task
+    </button>
+  );
+}
+```
+
+### Large Payloads
+
+```ts
+// For payloads > 512KB (max 10MB)
+export const largeDataTask = task({
+  id: 'large-data-task',
+  run: async (payload: { dataUrl: string }) => {
+    // Trigger.dev automatically handles large payloads
+    // For > 10MB, use external storage
+    const response = await fetch(payload.dataUrl);
+    const largeData = await response.json();
+
+    return { processed: largeData.length };
+  },
+});
+
+// Best practice: Use presigned URLs for very large files
+await largeDataTask.trigger({
+  dataUrl: 'https://s3.amazonaws.com/bucket/large-file.json?presigned=true',
+});
+```
+
+### Advanced Options
+
+```ts
+await myTask.trigger(payload, {
+  delay: '2h30m', // Delay execution
+  ttl: '24h', // Expire if not started within 24 hours
+  priority: 100, // Higher priority (time offset in seconds)
+  tags: ['urgent', 'user_123'],
+  metadata: { source: 'api', version: 'v2' },
+  queue: {
+    name: 'priority-queue',
+    concurrencyLimit: 10,
+  },
+  idempotencyKey: 'unique-operation-id',
+  idempotencyKeyTTL: '1h',
+  machine: { preset: 'large-1x' },
+  maxAttempts: 5,
+});
+```
+
+## Hidden Tasks
+
+```ts
+// Hidden task - not exported, only used internally
+const internalProcessor = task({
+  id: 'internal-processor',
+  run: async (payload: { data: string }) => {
+    return { processed: payload.data.toUpperCase() };
+  },
+});
+
+// Public task that uses hidden task
+export const publicWorkflow = task({
+  id: 'public-workflow',
+  run: async (payload: { input: string }) => {
+    // Use hidden task internally
+    const result = await internalProcessor.triggerAndWait({
+      data: payload.input,
+    });
+
+    if (result.ok) {
+      return { output: result.output.processed };
+    }
+
+    throw new Error('Internal processing failed');
+  },
+});
+```
+
+## Logging & Tracing
+
+```ts
+import { task, logger } from '@trigger.dev/sdk';
+
+export const tracedTask = task({
+  id: 'traced-task',
+  run: async (payload, { ctx }) => {
+    logger.info('Task started', { userId: payload.userId });
+
+    // Custom trace with attributes
+    const user = await logger.trace(
+      'fetch-user',
+      async (span) => {
+        span.setAttribute('user.id', payload.userId);
+        span.setAttribute('operation', 'database-fetch');
+
+        const userData = await database.findUser(payload.userId);
+        span.setAttribute('user.found', !!userData);
+
+        return userData;
+      },
+      { userId: payload.userId },
+    );
+
+    logger.debug('User fetched', { user: user.id });
+
+    try {
+      const result = await processUser(user);
+      logger.info('Processing completed', { result });
+      return result;
+    } catch (error) {
+      logger.error('Processing failed', {
+        error: error.message,
+        userId: payload.userId,
+      });
+      throw error;
+    }
+  },
+});
+```
+
+## Usage Monitoring
+
+```ts
+import { logger, task, usage } from '@trigger.dev/sdk';
+
+export const monitoredTask = task({
+  id: 'monitored-task',
+  run: async (payload) => {
+    // Get current run cost
+    const currentUsage = await usage.getCurrent();
+    logger.info('Current cost', {
+      costInCents: currentUsage.costInCents,
+      durationMs: currentUsage.durationMs,
+    });
+
+    // Measure specific operation
+    const { result, compute } = await usage.measure(async () => {
+      return await expensiveOperation(payload);
+    });
+
+    logger.info('Operation cost', {
+      costInCents: compute.costInCents,
+      durationMs: compute.durationMs,
+    });
+
+    return result;
+  },
+});
+```
+
+## Run Management
+
+```ts
+// Cancel runs
+await runs.cancel('run_123');
+
+// Replay runs with same payload
+await runs.replay('run_123');
+
+// Retrieve run with cost details
+const run = await runs.retrieve('run_123');
+console.log(`Cost: ${run.costInCents} cents, Duration: ${run.durationMs}ms`);
+```
+
+## Best Practices
+
+- **Concurrency**: Use queues to prevent overwhelming external services
+- **Retries**: Configure exponential backoff for transient failures
+- **Idempotency**: Always use for payment/critical operations
+- **Metadata**: Track progress for long-running tasks
+- **Machines**: Match machine size to computational requirements
+- **Tags**: Use consistent naming patterns for filtering
+- **Large Payloads**: Use external storage for files > 10MB
+- **Error Handling**: Distinguish between retryable and fatal errors
+
+Design tasks to be stateless, idempotent, and resilient to failures. Use metadata for state tracking and queues for resource management.
diff --git a/.claude/skills/trigger-basic/SKILL.md b/.claude/skills/trigger-basic/SKILL.md
@@ -0,0 +1,194 @@
+---
+name: trigger-basic
+description: "Only the most important rules for writing basic Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.basic.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Basic Tasks (v4)
+
+**MUST use `@trigger.dev/sdk` (v4), NEVER `client.defineJob`**
+
+## Basic Task
+
+```ts
+import { task } from "@trigger.dev/sdk";
+
+export const processData = task({
+  id: "process-data",
+  retry: {
+    maxAttempts: 10,
+    factor: 1.8,
+    minTimeoutInMs: 500,
+    maxTimeoutInMs: 30_000,
+    randomize: false,
+  },
+  run: async (payload: { userId: string; data: any[] }) => {
+    // Task logic - runs for long time, no timeouts
+    console.log(`Processing ${payload.data.length} items for user ${payload.userId}`);
+    return { processed: payload.data.length };
+  },
+});
+```
+
+## Schema Task (with validation)
+
+```ts
+import { schemaTask } from "@trigger.dev/sdk";
+import { z } from "zod";
+
+export const validatedTask = schemaTask({
+  id: "validated-task",
+  schema: z.object({
+    name: z.string(),
+    age: z.number(),
+    email: z.string().email(),
+  }),
+  run: async (payload) => {
+    // Payload is automatically validated and typed
+    return { message: `Hello ${payload.name}, age ${payload.age}` };
+  },
+});
+```
+
+## Scheduled Task
+
+```ts
+import { schedules } from "@trigger.dev/sdk";
+
+const dailyReport = schedules.task({
+  id: "daily-report",
+  cron: "0 9 * * *", // Daily at 9:00 AM UTC
+  // or with timezone: cron: { pattern: "0 9 * * *", timezone: "America/New_York" },
+  run: async (payload) => {
+    console.log("Scheduled run at:", payload.timestamp);
+    console.log("Last run was:", payload.lastTimestamp);
+    console.log("Next 5 runs:", payload.upcoming);
+
+    // Generate daily report logic
+    return { reportGenerated: true, date: payload.timestamp };
+  },
+});
+```
+
+## Triggering Tasks
+
+### From Backend Code
+
+```ts
+import { tasks } from "@trigger.dev/sdk";
+import type { processData } from "./trigger/tasks";
+
+// Single trigger
+const handle = await tasks.trigger<typeof processData>("process-data", {
+  userId: "123",
+  data: [{ id: 1 }, { id: 2 }],
+});
+
+// Batch trigger
+const batchHandle = await tasks.batchTrigger<typeof processData>("process-data", [
+  { payload: { userId: "123", data: [{ id: 1 }] } },
+  { payload: { userId: "456", data: [{ id: 2 }] } },
+]);
+```
+
+### From Inside Tasks (with Result handling)
+
+```ts
+export const parentTask = task({
+  id: "parent-task",
+  run: async (payload) => {
+    // Trigger and continue
+    const handle = await childTask.trigger({ data: "value" });
+
+    // Trigger and wait - returns Result object, NOT task output
+    const result = await childTask.triggerAndWait({ data: "value" });
+    if (result.ok) {
+      console.log("Task output:", result.output); // Actual task return value
+    } else {
+      console.error("Task failed:", result.error);
+    }
+
+    // Quick unwrap (throws on error)
+    const output = await childTask.triggerAndWait({ data: "value" }).unwrap();
+
+    // Batch trigger and wait
+    const results = await childTask.batchTriggerAndWait([
+      { payload: { data: "item1" } },
+      { payload: { data: "item2" } },
+    ]);
+
+    for (const run of results) {
+      if (run.ok) {
+        console.log("Success:", run.output);
+      } else {
+        console.log("Failed:", run.error);
+      }
+    }
+  },
+});
+
+export const childTask = task({
+  id: "child-task",
+  run: async (payload: { data: string }) => {
+    return { processed: payload.data };
+  },
+});
+```
+
+> Never wrap triggerAndWait or batchTriggerAndWait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.
+
+## Waits
+
+```ts
+import { task, wait } from "@trigger.dev/sdk";
+
+export const taskWithWaits = task({
+  id: "task-with-waits",
+  run: async (payload) => {
+    console.log("Starting task");
+
+    // Wait for specific duration
+    await wait.for({ seconds: 30 });
+    await wait.for({ minutes: 5 });
+    await wait.for({ hours: 1 });
+    await wait.for({ days: 1 });
+
+    // Wait until a future date
+    await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });
+
+    // Wait for token (from external system)
+    await wait.forToken({
+      token: "user-approval-token",
+      timeoutInSeconds: 3600, // 1 hour timeout
+    });
+
+    console.log("All waits completed");
+    return { status: "completed" };
+  },
+});
+```
+
+> Never wrap wait calls in a Promise.all or Promise.allSettled as this is not supported in Trigger.dev tasks.
+
+## Key Points
+
+- **Result vs Output**: `triggerAndWait()` returns a `Result` object with `ok`, `output`, `error` properties - NOT the direct task output
+- **Type safety**: Use `import type` for task references when triggering from backend
+- **Waits > 5 seconds**: Automatically checkpointed, don't count toward compute usage
+
+## NEVER Use (v2 deprecated)
+
+```ts
+// BREAKS APPLICATION
+client.defineJob({
+  id: "job-id",
+  run: async (payload, io) => {
+    /* ... */
+  },
+});
+```
+
+Use v4 SDK (`@trigger.dev/sdk`), check `result.ok` before accessing `result.output`
diff --git a/.claude/skills/trigger-config/SKILL.md b/.claude/skills/trigger-config/SKILL.md
@@ -0,0 +1,355 @@
+---
+name: trigger-config
+description: "Configure your Trigger.dev project with a trigger.config.ts file"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.config.mdc`.
+Original file scope: `**/trigger.config.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Configuration (v4)
+
+**Complete guide to configuring `trigger.config.ts` with build extensions**
+
+## Basic Configuration
+
+```ts
+import { defineConfig } from "@trigger.dev/sdk";
+
+export default defineConfig({
+  project: "<project-ref>", // Required: Your project reference
+  dirs: ["./trigger"], // Task directories
+  runtime: "node", // "node", "node-22", or "bun"
+  logLevel: "info", // "debug", "info", "warn", "error"
+
+  // Default retry settings
+  retries: {
+    enabledInDev: false,
+    default: {
+      maxAttempts: 3,
+      minTimeoutInMs: 1000,
+      maxTimeoutInMs: 10000,
+      factor: 2,
+      randomize: true,
+    },
+  },
+
+  // Build configuration
+  build: {
+    autoDetectExternal: true,
+    keepNames: true,
+    minify: false,
+    extensions: [], // Build extensions go here
+  },
+
+  // Global lifecycle hooks
+  onStart: async ({ payload, ctx }) => {
+    console.log("Global task start");
+  },
+  onSuccess: async ({ payload, output, ctx }) => {
+    console.log("Global task success");
+  },
+  onFailure: async ({ payload, error, ctx }) => {
+    console.log("Global task failure");
+  },
+});
+```
+
+## Build Extensions
+
+### Database & ORM
+
+#### Prisma
+
+```ts
+import { prismaExtension } from "@trigger.dev/build/extensions/prisma";
+
+extensions: [
+  prismaExtension({
+    schema: "prisma/schema.prisma",
+    version: "5.19.0", // Optional: specify version
+    migrate: true, // Run migrations during build
+    directUrlEnvVarName: "DIRECT_DATABASE_URL",
+    typedSql: true, // Enable TypedSQL support
+  }),
+];
+```
+
+#### TypeScript Decorators (for TypeORM)
+
+```ts
+import { emitDecoratorMetadata } from "@trigger.dev/build/extensions/typescript";
+
+extensions: [
+  emitDecoratorMetadata(), // Enables decorator metadata
+];
+```
+
+### Scripting Languages
+
+#### Python
+
+```ts
+import { pythonExtension } from "@trigger.dev/build/extensions/python";
+
+extensions: [
+  pythonExtension({
+    scripts: ["./python/**/*.py"], // Copy Python files
+    requirementsFile: "./requirements.txt", // Install packages
+    devPythonBinaryPath: ".venv/bin/python", // Dev mode binary
+  }),
+];
+
+// Usage in tasks
+const result = await python.runInline(`print("Hello, world!")`);
+const output = await python.runScript("./python/script.py", ["arg1"]);
+```
+
+### Browser Automation
+
+#### Playwright
+
+```ts
+import { playwright } from "@trigger.dev/build/extensions/playwright";
+
+extensions: [
+  playwright({
+    browsers: ["chromium", "firefox", "webkit"], // Default: ["chromium"]
+    headless: true, // Default: true
+  }),
+];
+```
+
+#### Puppeteer
+
+```ts
+import { puppeteer } from "@trigger.dev/build/extensions/puppeteer";
+
+extensions: [puppeteer()];
+
+// Environment variable needed:
+// PUPPETEER_EXECUTABLE_PATH: "/usr/bin/google-chrome-stable"
+```
+
+#### Lightpanda
+
+```ts
+import { lightpanda } from "@trigger.dev/build/extensions/lightpanda";
+
+extensions: [
+  lightpanda({
+    version: "latest", // or "nightly"
+    disableTelemetry: false,
+  }),
+];
+```
+
+### Media Processing
+
+#### FFmpeg
+
+```ts
+import { ffmpeg } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  ffmpeg({ version: "7" }), // Static build, or omit for Debian version
+];
+
+// Automatically sets FFMPEG_PATH and FFPROBE_PATH
+// Add fluent-ffmpeg to external packages if using
+```
+
+#### Audio Waveform
+
+```ts
+import { audioWaveform } from "@trigger.dev/build/extensions/audioWaveform";
+
+extensions: [
+  audioWaveform(), // Installs Audio Waveform 1.1.0
+];
+```
+
+### System & Package Management
+
+#### System Packages (apt-get)
+
+```ts
+import { aptGet } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  aptGet({
+    packages: ["ffmpeg", "imagemagick", "curl=7.68.0-1"], // Can specify versions
+  }),
+];
+```
+
+#### Additional NPM Packages
+
+Only use this for installing CLI tools, NOT packages you import in your code.
+
+```ts
+import { additionalPackages } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  additionalPackages({
+    packages: ["wrangler"], // CLI tools and specific versions
+  }),
+];
+```
+
+#### Additional Files
+
+```ts
+import { additionalFiles } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  additionalFiles({
+    files: ["wrangler.toml", "./assets/**", "./fonts/**"], // Glob patterns supported
+  }),
+];
+```
+
+### Environment & Build Tools
+
+#### Environment Variable Sync
+
+```ts
+import { syncEnvVars } from "@trigger.dev/build/extensions/core";
+
+extensions: [
+  syncEnvVars(async (ctx) => {
+    // ctx contains: environment, projectRef, env
+    return [
+      { name: "SECRET_KEY", value: await getSecret(ctx.environment) },
+      { name: "API_URL", value: ctx.environment === "prod" ? "api.prod.com" : "api.dev.com" },
+    ];
+  }),
+];
+```
+
+#### ESBuild Plugins
+
+```ts
+import { esbuildPlugin } from "@trigger.dev/build/extensions";
+import { sentryEsbuildPlugin } from "@sentry/esbuild-plugin";
+
+extensions: [
+  esbuildPlugin(
+    sentryEsbuildPlugin({
+      org: process.env.SENTRY_ORG,
+      project: process.env.SENTRY_PROJECT,
+      authToken: process.env.SENTRY_AUTH_TOKEN,
+    }),
+    { placement: "last", target: "deploy" } // Optional config
+  ),
+];
+```
+
+## Custom Build Extensions
+
+```ts
+import { defineConfig } from "@trigger.dev/sdk";
+
+const customExtension = {
+  name: "my-custom-extension",
+
+  externalsForTarget: (target) => {
+    return ["some-native-module"]; // Add external dependencies
+  },
+
+  onBuildStart: async (context) => {
+    console.log(`Build starting for ${context.target}`);
+    // Register esbuild plugins, modify build context
+  },
+
+  onBuildComplete: async (context, manifest) => {
+    console.log("Build complete, adding layers");
+    // Add build layers, modify deployment
+    context.addLayer({
+      id: "my-layer",
+      files: [{ source: "./custom-file", destination: "/app/custom" }],
+      commands: ["chmod +x /app/custom"],
+    });
+  },
+};
+
+export default defineConfig({
+  project: "my-project",
+  build: {
+    extensions: [customExtension],
+  },
+});
+```
+
+## Advanced Configuration
+
+### Telemetry
+
+```ts
+import { PrismaInstrumentation } from "@prisma/instrumentation";
+import { OpenAIInstrumentation } from "@langfuse/openai";
+
+export default defineConfig({
+  // ... other config
+  telemetry: {
+    instrumentations: [new PrismaInstrumentation(), new OpenAIInstrumentation()],
+    exporters: [customExporter], // Optional custom exporters
+  },
+});
+```
+
+### Machine & Performance
+
+```ts
+export default defineConfig({
+  // ... other config
+  defaultMachine: "large-1x", // Default machine for all tasks
+  maxDuration: 300, // Default max duration (seconds)
+  enableConsoleLogging: true, // Console logging in development
+});
+```
+
+## Common Extension Combinations
+
+### Full-Stack Web App
+
+```ts
+extensions: [
+  prismaExtension({ schema: "prisma/schema.prisma", migrate: true }),
+  additionalFiles({ files: ["./public/**", "./assets/**"] }),
+  syncEnvVars(async (ctx) => [...envVars]),
+];
+```
+
+### AI/ML Processing
+
+```ts
+extensions: [
+  pythonExtension({
+    scripts: ["./ai/**/*.py"],
+    requirementsFile: "./requirements.txt",
+  }),
+  ffmpeg({ version: "7" }),
+  additionalPackages({ packages: ["wrangler"] }),
+];
+```
+
+### Web Scraping
+
+```ts
+extensions: [
+  playwright({ browsers: ["chromium"] }),
+  puppeteer(),
+  additionalFiles({ files: ["./selectors.json", "./proxies.txt"] }),
+];
+```
+
+## Best Practices
+
+- **Use specific versions**: Pin extension versions for reproducible builds
+- **External packages**: Add modules with native addons to the `build.external` array
+- **Environment sync**: Use `syncEnvVars` for dynamic secrets
+- **File paths**: Use glob patterns for flexible file inclusion
+- **Debug builds**: Use `--log-level debug --dry-run` for troubleshooting
+
+Extensions only affect deployment, not local development. Use `external` array for packages that shouldn't be bundled.
diff --git a/.claude/skills/trigger-realtime/SKILL.md b/.claude/skills/trigger-realtime/SKILL.md
@@ -0,0 +1,281 @@
+---
+name: trigger-realtime
+description: "How to use realtime in your Trigger.dev tasks and your frontend"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.realtime.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Trigger.dev Realtime (v4)
+
+**Real-time monitoring and updates for runs**
+
+## Core Concepts
+
+Realtime allows you to:
+
+- Subscribe to run status changes, metadata updates, and streams
+- Build real-time dashboards and UI updates
+- Monitor task progress from frontend and backend
+
+## Authentication
+
+### Public Access Tokens
+
+```ts
+import { auth } from "@trigger.dev/sdk";
+
+// Read-only token for specific runs
+const publicToken = await auth.createPublicToken({
+  scopes: {
+    read: {
+      runs: ["run_123", "run_456"],
+      tasks: ["my-task-1", "my-task-2"],
+    },
+  },
+  expirationTime: "1h", // Default: 15 minutes
+});
+```
+
+### Trigger Tokens (Frontend only)
+
+```ts
+// Single-use token for triggering tasks
+const triggerToken = await auth.createTriggerPublicToken("my-task", {
+  expirationTime: "30m",
+});
+```
+
+## Backend Usage
+
+### Subscribe to Runs
+
+```ts
+import { runs, tasks } from "@trigger.dev/sdk";
+
+// Trigger and subscribe
+const handle = await tasks.trigger("my-task", { data: "value" });
+
+// Subscribe to specific run
+for await (const run of runs.subscribeToRun<typeof myTask>(handle.id)) {
+  console.log(`Status: ${run.status}, Progress: ${run.metadata?.progress}`);
+  if (run.status === "COMPLETED") break;
+}
+
+// Subscribe to runs with tag
+for await (const run of runs.subscribeToRunsWithTag("user-123")) {
+  console.log(`Tagged run ${run.id}: ${run.status}`);
+}
+
+// Subscribe to batch
+for await (const run of runs.subscribeToBatch(batchId)) {
+  console.log(`Batch run ${run.id}: ${run.status}`);
+}
+```
+
+### Streams
+
+```ts
+import { task, metadata } from "@trigger.dev/sdk";
+
+// Task that streams data
+export type STREAMS = {
+  openai: OpenAI.ChatCompletionChunk;
+};
+
+export const streamingTask = task({
+  id: "streaming-task",
+  run: async (payload) => {
+    const completion = await openai.chat.completions.create({
+      model: "gpt-4",
+      messages: [{ role: "user", content: payload.prompt }],
+      stream: true,
+    });
+
+    // Register stream
+    const stream = await metadata.stream("openai", completion);
+
+    let text = "";
+    for await (const chunk of stream) {
+      text += chunk.choices[0]?.delta?.content || "";
+    }
+
+    return { text };
+  },
+});
+
+// Subscribe to streams
+for await (const part of runs.subscribeToRun(runId).withStreams<STREAMS>()) {
+  switch (part.type) {
+    case "run":
+      console.log("Run update:", part.run.status);
+      break;
+    case "openai":
+      console.log("Stream chunk:", part.chunk);
+      break;
+  }
+}
+```
+
+## React Frontend Usage
+
+### Installation
+
+```bash
+bun add @trigger.dev/react-hooks
+```
+
+### Triggering Tasks
+
+```tsx
+"use client";
+import { useTaskTrigger, useRealtimeTaskTrigger } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function TriggerComponent({ accessToken }: { accessToken: string }) {
+  // Basic trigger
+  const { submit, handle, isLoading } = useTaskTrigger<typeof myTask>("my-task", {
+    accessToken,
+  });
+
+  // Trigger with realtime updates
+  const {
+    submit: realtimeSubmit,
+    run,
+    isLoading: isRealtimeLoading,
+  } = useRealtimeTaskTrigger<typeof myTask>("my-task", { accessToken });
+
+  return (
+    <div>
+      <button onClick={() => submit({ data: "value" })} disabled={isLoading}>
+        Trigger Task
+      </button>
+
+      <button onClick={() => realtimeSubmit({ data: "realtime" })} disabled={isRealtimeLoading}>
+        Trigger with Realtime
+      </button>
+
+      {run && <div>Status: {run.status}</div>}
+    </div>
+  );
+}
+```
+
+### Subscribing to Runs
+
+```tsx
+"use client";
+import { useRealtimeRun, useRealtimeRunsWithTag } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function SubscribeComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  // Subscribe to specific run
+  const { run, error } = useRealtimeRun<typeof myTask>(runId, {
+    accessToken,
+    onComplete: (run) => {
+      console.log("Task completed:", run.output);
+    },
+  });
+
+  // Subscribe to tagged runs
+  const { runs } = useRealtimeRunsWithTag("user-123", { accessToken });
+
+  if (error) return <div>Error: {error.message}</div>;
+  if (!run) return <div>Loading...</div>;
+
+  return (
+    <div>
+      <div>Status: {run.status}</div>
+      <div>Progress: {run.metadata?.progress || 0}%</div>
+      {run.output && <div>Result: {JSON.stringify(run.output)}</div>}
+
+      <h3>Tagged Runs:</h3>
+      {runs.map((r) => (
+        <div key={r.id}>
+          {r.id}: {r.status}
+        </div>
+      ))}
+    </div>
+  );
+}
+```
+
+### Streams with React
+
+```tsx
+"use client";
+import { useRealtimeRunWithStreams } from "@trigger.dev/react-hooks";
+import type { streamingTask, STREAMS } from "../trigger/tasks";
+
+function StreamComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  const { run, streams } = useRealtimeRunWithStreams<typeof streamingTask, STREAMS>(runId, {
+    accessToken,
+  });
+
+  const text = streams.openai
+    .filter((chunk) => chunk.choices[0]?.delta?.content)
+    .map((chunk) => chunk.choices[0].delta.content)
+    .join("");
+
+  return (
+    <div>
+      <div>Status: {run?.status}</div>
+      <div>Streamed Text: {text}</div>
+    </div>
+  );
+}
+```
+
+### Wait Tokens
+
+```tsx
+"use client";
+import { useWaitToken } from "@trigger.dev/react-hooks";
+
+function WaitTokenComponent({ tokenId, accessToken }: { tokenId: string; accessToken: string }) {
+  const { complete } = useWaitToken(tokenId, { accessToken });
+
+  return <button onClick={() => complete({ approved: true })}>Approve Task</button>;
+}
+```
+
+### SWR Hooks (Fetch Once)
+
+```tsx
+"use client";
+import { useRun } from "@trigger.dev/react-hooks";
+import type { myTask } from "../trigger/tasks";
+
+function SWRComponent({ runId, accessToken }: { runId: string; accessToken: string }) {
+  const { run, error, isLoading } = useRun<typeof myTask>(runId, {
+    accessToken,
+    refreshInterval: 0, // Disable polling (recommended)
+  });
+
+  if (isLoading) return <div>Loading...</div>;
+  if (error) return <div>Error: {error.message}</div>;
+
+  return <div>Run: {run?.status}</div>;
+}
+```
+
+## Run Object Properties
+
+Key properties available in run subscriptions:
+
+- `id`: Unique run identifier
+- `status`: `QUEUED`, `EXECUTING`, `COMPLETED`, `FAILED`, `CANCELED`, etc.
+- `payload`: Task input data (typed)
+- `output`: Task result (typed, when completed)
+- `metadata`: Real-time updatable data
+- `createdAt`, `updatedAt`: Timestamps
+- `costInCents`: Execution cost
+
+## Best Practices
+
+- **Use Realtime over SWR**: Recommended for most use cases due to rate limits
+- **Scope tokens properly**: Only grant necessary read/trigger permissions
+- **Handle errors**: Always check for errors in hooks and subscriptions
+- **Type safety**: Use task types for proper payload/output typing
+- **Cleanup subscriptions**: Backend subscriptions auto-complete, frontend hooks auto-cleanup
diff --git a/.claude/skills/trigger-scheduled-tasks/SKILL.md b/.claude/skills/trigger-scheduled-tasks/SKILL.md
@@ -0,0 +1,126 @@
+---
+name: trigger-scheduled-tasks
+description: "How to write and use scheduled Trigger.dev tasks"
+---
+
+Source Cursor rule: `.cursor/rules/trigger.scheduled-tasks.mdc`.
+Original file scope: `**/trigger/**/*.ts`.
+Original Cursor alwaysApply: `false`.
+
+# Scheduled tasks (cron)
+
+Recurring tasks using cron. For one-off future runs, use the **delay** option.
+
+## Define a scheduled task
+
+```ts
+import { schedules } from "@trigger.dev/sdk";
+
+export const task = schedules.task({
+  id: "first-scheduled-task",
+  run: async (payload) => {
+    payload.timestamp; // Date (scheduled time, UTC)
+    payload.lastTimestamp; // Date | undefined
+    payload.timezone; // IANA, e.g. "America/New_York" (default "UTC")
+    payload.scheduleId; // string
+    payload.externalId; // string | undefined
+    payload.upcoming; // Date[]
+
+    payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone });
+  },
+});
+```
+
+> Scheduled tasks need at least one schedule attached to run.
+
+## Attach schedules
+
+**Declarative (sync on dev/deploy):**
+
+```ts
+schedules.task({
+  id: "every-2h",
+  cron: "0 */2 * * *", // UTC
+  run: async () => {},
+});
+
+schedules.task({
+  id: "tokyo-5am",
+  cron: { pattern: "0 5 * * *", timezone: "Asia/Tokyo", environments: ["PRODUCTION", "STAGING"] },
+  run: async () => {},
+});
+```
+
+**Imperative (SDK or dashboard):**
+
+```ts
+await schedules.create({
+  task: task.id,
+  cron: "0 0 * * *",
+  timezone: "America/New_York", // DST-aware
+  externalId: "user_123",
+  deduplicationKey: "user_123-daily", // updates if reused
+});
+```
+
+### Dynamic / multi-tenant example
+
+```ts
+// /trigger/reminder.ts
+export const reminderTask = schedules.task({
+  id: "todo-reminder",
+  run: async (p) => {
+    if (!p.externalId) throw new Error("externalId is required");
+    const user = await db.getUser(p.externalId);
+    await sendReminderEmail(user);
+  },
+});
+```
+
+```ts
+// app/reminders/route.ts
+export async function POST(req: Request) {
+  const data = await req.json();
+  return Response.json(
+    await schedules.create({
+      task: reminderTask.id,
+      cron: "0 8 * * *",
+      timezone: data.timezone,
+      externalId: data.userId,
+      deduplicationKey: `${data.userId}-reminder`,
+    })
+  );
+}
+```
+
+## Cron syntax (no seconds)
+
+```
+* * * * *
+| | | | └ day of week (0–7 or 1L–7L; 0/7=Sun; L=last)
+| | | └── month (1–12)
+| | └──── day of month (1–31 or L)
+| └────── hour (0–23)
+└──────── minute (0–59)
+```
+
+## When schedules won't trigger
+
+- **Dev:** only when the dev CLI is running.
+- **Staging/Production:** only for tasks in the **latest deployment**.
+
+## SDK management (quick refs)
+
+```ts
+await schedules.retrieve(id);
+await schedules.list();
+await schedules.update(id, { cron: "0 0 1 * *", externalId: "ext", deduplicationKey: "key" });
+await schedules.deactivate(id);
+await schedules.activate(id);
+await schedules.del(id);
+await schedules.timezones(); // list of IANA timezones
+```
+
+## Dashboard
+
+Create/attach schedules visually (Task, Cron pattern, Timezone, Optional: External ID, Dedup key, Environments). Test scheduled tasks from the **Test** page.
diff --git a/.claude/skills/ui/SKILL.md b/.claude/skills/ui/SKILL.md
@@ -0,0 +1,137 @@
+---
+name: ui
+description: "Use when building or editing frontend UI components, layouts, styling, design system usage, colors, dark mode, or icons."
+---
+
+Source Cursor rule: `.cursor/rules/ui.mdc`.
+Original Cursor alwaysApply: `true`.
+
+# UI Components
+
+## Design System Priority
+
+1. **First choice:** `@trycompai/design-system`
+2. **Fallback:** `@trycompai/ui` only if DS doesn't have the component
+
+```tsx
+// ✅ Design system
+import { Button, Card, Input, Sheet, Badge } from '@trycompai/design-system';
+import { Add, Close, ArrowRight } from '@trycompai/design-system/icons';
+
+// ❌ Don't use when DS has it
+import { Button } from '@trycompai/ui/button';
+import { Plus } from 'lucide-react';
+```
+
+## No className on DS Components
+
+DS components don't accept `className`. Use variants and props only.
+
+```tsx
+// ✅ Use variants
+<Button variant="destructive" size="sm" loading={isLoading}>Delete</Button>
+<Button type="submit" iconRight={<ArrowRight size={16} />}>Continue</Button>
+<Badge variant="outline">Active</Badge>
+
+// ❌ TypeScript will error
+<Button className="bg-red-500">Delete</Button>
+```
+
+## Layout with Wrapper Divs
+
+For layout concerns, wrap DS components:
+
+```tsx
+// ✅ Wrapper for width
+<div className="w-full">
+  <Button>Full Width</Button>
+</div>
+
+// ✅ Use Stack for spacing
+<Stack gap="4" direction="row">
+  <Button>First</Button>
+  <Button>Second</Button>
+</Stack>
+```
+
+## Componentize Repeated Patterns
+
+If a pattern appears 2+ times, extract it:
+
+```tsx
+// Repeated? Make a component
+<div className="flex items-center gap-2">
+  <div className="w-2 h-2 rounded-full bg-green-500" />
+  <span className="text-sm">Active</span>
+</div>
+// → Create <StatusDot status="active" />
+```
+
+## Extension Strategy
+
+When you need new styling:
+
+1. **Check existing variants** - component may already support it
+2. **Add a variant** to the component's `cva` definition
+3. **Create a new component** if it's a genuinely new pattern
+
+```tsx
+// Adding a variant
+const badgeVariants = cva("...", {
+  variants: {
+    variant: {
+      // existing...
+      counter: "bg-muted text-muted-foreground tabular-nums font-mono",
+    },
+  },
+});
+```
+
+## Semantic Colors
+
+Use CSS variables, not hardcoded colors:
+
+```tsx
+// ✅ Semantic tokens
+<div className="bg-background text-foreground border-border">
+<div className="bg-muted text-muted-foreground">
+<div className="bg-destructive/10 text-destructive">
+
+// ❌ Hardcoded
+<div className="bg-white text-black">
+<div className="bg-[#059669]">
+```
+
+## Dark Mode
+
+Always support both modes:
+
+```tsx
+// Status colors with dark variants
+<div className="bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">
+<div className="bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400">
+```
+
+## Icons
+
+Carbon icons from DS, not lucide:
+
+```tsx
+// ✅ Design system icons with size prop
+import { Add, Close, ChevronDown } from '@trycompai/design-system/icons';
+<Add size={16} />
+
+// ❌ Don't use lucide
+import { Plus, X } from 'lucide-react';
+<Plus className="h-4 w-4" />
+```
+
+## Anti-Patterns
+
+```tsx
+// ❌ Never do these
+<div style={{ display: 'flex' }}>              // Inline styles
+<Button className="bg-red-500">               // className on DS
+<div className="bg-[#059669]">                // Hardcoded colors
+<div className="w-[847px]">                   // Arbitrary values
+```
diff --git a/.cursor/rules/data.mdc b/.cursor/rules/data.mdc
@@ -52,7 +52,12 @@ export function useTasks({ organizationId, initialData }: UseTasksOptions) {
     mutate(); // Revalidate
   };
 
-  return { tasks: data ?? [], createTask, mutate };
+  const updateTask = async ({ taskId, input }: { taskId: string; input: UpdateTaskInput }) => {
+    await apiClient.put(`/v1/tasks/${taskId}`, input, organizationId);
+    mutate(); // Revalidate
+  };
+
+  return { tasks: data ?? [], createTask, updateTask, mutate };
 }
 ```
 
diff --git a/.cursor/rules/forms.mdc b/.cursor/rules/forms.mdc
@@ -50,7 +50,7 @@ function MyForm() {
 ## Zod Schema Patterns
 
 ```tsx
-const schema = z.object({
+const profileSchema = z.object({
   // Strings
   name: z.string().min(1, 'Required'),
   email: z.string().email(),
@@ -68,7 +68,7 @@ const schema = z.object({
 });
 
 // Cross-field validation
-const schema = z.object({
+const passwordSchema = z.object({
   password: z.string().min(8),
   confirmPassword: z.string(),
 }).refine(d => d.password === d.confirmPassword, {
diff --git a/.cursor/rules/infra.mdc b/.cursor/rules/infra.mdc
@@ -27,7 +27,7 @@ comp/
 │   └── portal/          # Next.js portal
 ├── packages/
 │   ├── db/              # Prisma (@trycompai/db)
-│   ├── ui/              # UI components (@trycompai/ui)
+│   ├── ui/              # Legacy UI (@trycompai/ui); prefer @trycompai/design-system
 │   └── ...
 ├── turbo.json
 └── package.json
diff --git a/.cursor/rules/prisma.mdc b/.cursor/rules/prisma.mdc
@@ -51,6 +51,7 @@ cd packages/db && bunx prisma migrate dev --name add_user_role
 # 3. Regenerate types in ALL apps that use the db
 bun run -F apps/app db:generate
 bun run -F apps/api db:generate
+bun run -F apps/portal db:generate
 ```
 
 ### ❌ Never Do This
diff --git a/.cursor/rules/prompt-engineering.mdc b/.cursor/rules/prompt-engineering.mdc
@@ -33,7 +33,7 @@ Prompt engineering is preferred because:
 
 ---
 
-## The 8 Core Techniques
+## The 6 Core Techniques
 
 ### 1. Be Clear and Direct
 
diff --git a/.cursor/rules/trigger.advanced-tasks.mdc b/.cursor/rules/trigger.advanced-tasks.mdc
@@ -39,7 +39,7 @@ for await (const run of runs.subscribeToRunsWithTag('user_123')) {
 **Tag Best Practices:**
 
 - Use prefixes: `user_123`, `org_abc`, `video:456`
-- Max 10 tags per run, 1-64 characters each
+- Max 10 tags per run, 1-128 characters each
 - Tags don't propagate to child tasks automatically
 
 ## Concurrency & Queues
@@ -402,7 +402,7 @@ export const tracedTask = task({
 ## Usage Monitoring
 
 ```ts
-import { task, usage } from '@trigger.dev/sdk';
+import { logger, task, usage } from '@trigger.dev/sdk';
 
 export const monitoredTask = task({
   id: 'monitored-task',
diff --git a/.cursor/rules/trigger.basic.mdc b/.cursor/rules/trigger.basic.mdc
@@ -152,8 +152,8 @@ export const taskWithWaits = task({
     await wait.for({ hours: 1 });
     await wait.for({ days: 1 });
 
-    // Wait until specific date
-    await wait.until({ date: new Date("2024-12-25") });
+    // Wait until a future date
+    await wait.until({ date: new Date(Date.now() + 24 * 60 * 60 * 1000) });
 
     // Wait for token (from external system)
     await wait.forToken({
diff --git a/.cursor/rules/trigger.realtime.mdc b/.cursor/rules/trigger.realtime.mdc
@@ -119,7 +119,7 @@ for await (const part of runs.subscribeToRun(runId).withStreams<STREAMS>()) {
 ### Installation
 
 ```bash
-npm add @trigger.dev/react-hooks
+bun add @trigger.dev/react-hooks
 ```
 
 ### Triggering Tasks
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,154 @@
+# Project Rules
+
+## Tooling
+
+- **Package manager**: `bun` (never npm/yarn/pnpm)
+- **Build**: `bun run build` (uses turbo). Filter: `bun run --filter '@trycompai/app' build`
+- **Typecheck**: `bun run typecheck` or `bunx turbo run typecheck --filter=@trycompai/api`
+- **Tests (app)**: `cd apps/app && bunx vitest run`
+- **Tests (api)**: `cd apps/api && bunx jest src/<module> --passWithNoTests`
+- **Lint**: `bun run lint`
+
+## Code Style
+
+- **Max 300 lines per file.** Split into focused modules if exceeded.
+- **No `as any` casts.** Ever. Use proper types, generics, or `unknown` with type guards.
+- **No `@ts-ignore` or `@ts-expect-error`.** Fix the type instead.
+- **Strict TypeScript**: Use zod for runtime validation, generics over `any`.
+- **Early returns** to avoid nested conditionals.
+- **Named parameters** for functions with 2+ arguments.
+- **Event handlers**: prefix with `handle` (e.g., `handleSubmit`).
+
+## Monorepo Structure
+
+```
+apps/
+  api/          # NestJS API (auth, RBAC, business logic)
+  app/          # Next.js frontend (compliance + security products)
+  portal/       # Employee portal
+packages/
+  auth/         # RBAC definitions (permissions.ts) — single source of truth
+  db/           # Prisma schema + client
+  ui/           # Legacy component library (being phased out)
+```
+
+## Authentication & Session
+
+- **Auth lives in `apps/api` (NestJS).** The API is the single source of truth for authentication via better-auth. All apps and packages that need to authenticate (app, portal, device-agent, etc.) MUST go through the API — never run a local better-auth instance or handle auth directly in a frontend app.
+- **Session-based auth only.** No JWT tokens. Cross-subdomain cookies (`.trycomp.ai`) allow sessions to work across all apps.
+- **HybridAuthGuard** supports 3 methods in order: API Key (`x-api-key`), Service Token (`x-service-token`), Session (cookies). `@Public()` skips auth.
+- **Client-side auth**: `authClient` (better-auth client) with `baseURL` pointing to the API, NOT the current app.
+- **Client-side data**: `apiClient` from `@/lib/api-client` (always sends cookies).
+- **Server-side data**: `serverApi` from `@/lib/api-server.ts`.
+- **Server-side session checks**: Proxy to the API's `/api/auth/get-session` endpoint — do NOT instantiate better-auth locally.
+- **Raw `fetch()` to API**: MUST include `credentials: 'include'`, otherwise 401.
+
+## API Architecture
+
+We are migrating away from Next.js server actions toward calling the NestJS API directly.
+
+### Simple CRUD operations
+Client components call the NestJS API via custom SWR hooks. No server action wrapper needed.
+
+### Multi-step orchestration
+When an operation requires multiple API calls (e.g., S3 upload + PATCH), create a Next.js API route (`apps/app/src/app/api/...`) that orchestrates them.
+
+### What NOT to do
+- Do NOT use server actions for new features
+- Do NOT keep server actions as wrappers around API calls
+- Do NOT add direct database (`@db`) access in the Next.js app for mutations — always go through the API
+- Do NOT use `useAction` from `next-safe-action` for new code
+
+### API Client
+- Server-side (Next.js API routes/pages): `serverApi` from `apps/app/src/lib/api-server.ts`
+- Client-side (hooks): `apiClient` / `api` from `@/lib/api-client`
+
+### API Response Format
+- **List endpoints**: `{ data: [...], count, authType, authenticatedUser }` → access via `response.data.data`
+- **Single resource endpoints**: `{ ...entity, authType, authenticatedUser }` → access via `response.data`
+- Both `apiClient` and `serverApi` wrap in `{ data, error, status }`
+
+## RBAC
+
+### Permissions Model
+- Flat `resource:action` model (e.g., `pentest:read`, `control:update`)
+- Single source of truth: `packages/auth/src/permissions.ts`
+- Built-in roles: `owner`, `admin`, `auditor`, `employee`, `contractor`
+- Custom roles: stored in `organization_role` table per organization
+- Multiple roles per user (comma-separated in `member.role`)
+
+### Multi-Product Architecture
+- **Products** (compliance, pen testing) are org-level subscription/feature flags — NOT RBAC
+- **RBAC** controls user access within products
+- `app:read` gates the compliance dashboard; `pentest:read` gates security product
+- Portal-only resources (`policy`, `compliance`) do NOT grant app access
+
+### API Endpoint Requirements
+Every customer-facing API endpoint MUST have:
+```typescript
+@UseGuards(HybridAuthGuard, PermissionGuard)  // at controller or endpoint level
+@RequirePermission('resource', 'action')       // on every endpoint
+```
+- Controller format: `@Controller({ path: 'name', version: '1' })`, NOT `@Controller('v1/name')`
+- `@Public()` for unauthenticated endpoints (webhooks, etc.)
+- The `AuditLogInterceptor` only logs when `@RequirePermission` metadata is present
+
+### Frontend Permission Gating
+- **Nav items**: Gate with `canAccessRoute(permissions, 'routeSegment')`
+- **Rail icons**: Gate product sections (Compliance, Security, Trust, Settings) by permission
+- **Mutation buttons**: Gate with `hasPermission(permissions, 'resource', 'action')`
+- **Page-level**: Every product layout uses `requireRoutePermission('segment', orgId)` server-side
+- **Route permissions**: Defined in `ROUTE_PERMISSIONS` in `apps/app/src/lib/permissions.ts`
+- No manual role string parsing (`role.includes('admin')`) — always use permission checks
+
+### Permission Resources
+`organization`, `member`, `control`, `evidence`, `policy`, `risk`, `vendor`, `task`, `framework`, `audit`, `finding`, `questionnaire`, `integration`, `apiKey`, `trust`, `pentest`, `app`, `compliance`
+
+## Design System
+
+- **Always prefer `@trycompai/design-system`** over `@trycompai/ui`. Check DS exports first.
+- `@trycompai/ui` is the legacy library being phased out — only use as last resort.
+- **Icons**: `@trycompai/design-system/icons` (Carbon icons), NOT `lucide-react`
+- **DS components that do NOT accept `className`**: `Text`, `Stack`, `HStack`, `Badge`, `Button` — wrap in `<div>` for custom styling
+- **Layout**: Use `PageLayout`, `PageHeader`, `Stack`, `HStack`, `Section`, `SettingGroup`
+- **Patterns**: Sheet (`Sheet > SheetContent > SheetHeader + SheetBody`), Drawer, Collapsible
+- **After editing any frontend component**: Run the `audit-design-system` skill to catch `@trycompai/ui` or `lucide-react` imports that should be migrated
+
+## Data Fetching
+
+- **Server components**: Fetch with `serverApi`, pass as `fallbackData` to client
+- **Client components**: `useSWR` with `apiClient` or custom hooks (e.g., `usePolicy`, `useTask`)
+- **SWR hooks**: Use `fallbackData` for SSR initial data, `revalidateOnMount: !initialData`
+- **`mutate()` safety**: Guard against `undefined` in optimistic update functions
+- **`Array.isArray()` checks**: When consuming SWR data that could be stale
+
+## Testing
+
+- **Every new feature MUST include tests.** No exceptions.
+- **TDD preferred**: Write failing tests first, then make them pass.
+- **App tests**: Vitest + @testing-library/react (jsdom environment)
+- **API tests**: Jest with NestJS testing utilities
+- **Permission tests**: Test admin (write) and read-only user scenarios
+- **Run from package dir**: `cd apps/app && bunx vitest run` or `cd apps/api && bunx jest`
+
+## Database
+
+- **Schema**: `packages/db/prisma/schema/` (split into files per model)
+- **IDs**: Always use prefixed CUIDs: `@default(dbgenerated("generate_prefixed_cuid('prefix'::text)"))`
+- **Migrations**: `cd packages/db && bunx prisma migrate dev --name your_name`
+- **Multi-tenancy**: Always scope queries by `organizationId`
+- **Transactions**: Use for operations modifying multiple records
+
+## Git
+
+- **Conventional commits**: `<type>(<scope>): <description>` (imperative, lowercase)
+- **Never use `git stash`** unless explicitly asked
+- **Never skip hooks** (`--no-verify`)
+- **Never force push** to main/master
+
+## Forms
+
+- All forms use **React Hook Form + Zod** validation
+- Define Zod schema first, infer type with `z.infer<typeof schema>`
+- Use `Controller` for complex components (Select, Combobox)
+- Never use `useState` for form field values
PATCH

echo "Gold patch applied."
