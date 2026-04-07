#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'Read @.cursor/rules/linear.mdc' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'PATCH'
diff --git a/.cursor/rules/linear.mdc b/.cursor/rules/linear.mdc
new file mode 100644
index 00000000000..45c5eab1688
--- /dev/null
+++ b/.cursor/rules/linear.mdc
@@ -0,0 +1,53 @@
+---
+alwaysApply: true
+---
+
+# Linear Issue Management
+
+When working with Linear issues:
+
+1. **Retrieve issue details** before starting work using `mcp__linear-server__get_issue`
+2. **Check for sub-issues**: If the issue has sub-issues, retrieve and review ALL sub-issues using `mcp__linear-server__list_issues` with `parentId` filter before starting work
+3. **Update issue status** when completing tasks using `mcp__linear-server__update_issue`
+4. **MUST add completion comment** using `mcp__linear-server__create_comment`
+
+## Creating Issues
+
+When creating new Linear issues using `mcp__linear-server__create_issue`, **MUST add the `claude code` label** to indicate the issue was created by Claude Code.
+
+## Completion Comment (REQUIRED)
+
+**Every time you complete an issue, you MUST add a comment summarizing the work done.** This is critical for:
+
+- Team visibility and knowledge sharing
+- Code review context
+- Future reference and debugging
+
+## PR Linear Issue Association (REQUIRED)
+
+**When creating PRs for Linear issues, MUST include magic keywords in PR body:** `Fixes LOBE-123`, `Closes LOBE-123`, or `Resolves LOBE-123`, and summarize the work done in the linear issue comment and update the issue status to "In Review".
+
+## IMPORTANT: Per-Issue Completion Rule
+
+**When working with multiple issues (e.g., parent issue with sub-issues), you MUST update status and add comment for EACH issue IMMEDIATELY after completing it.** Do NOT wait until all issues are done to update them in batch.
+
+**Workflow for EACH individual issue:**
+
+1. Complete the implementation for this specific issue
+2. Run type check: `bun run type-check`
+3. Run related tests if applicable
+4. Create PR if needed
+5. **IMMEDIATELY** update issue status to **"In Review"** (NOT "Done"): `mcp__linear-server__update_issue`
+6. **IMMEDIATELY** add completion comment: `mcp__linear-server__create_comment`
+7. Only then move on to the next issue
+
+**Note:** Issue status should be set to **"In Review"** when PR is created. The status will be updated to **"Done"** only after the PR is merged (usually handled by Linear-GitHub integration or manually).
+
+**Wrong approach:**
+
+- Complete Issue A -> Complete Issue B -> Complete Issue C -> Update all statuses -> Add all comments
+- Mark issue as "Done" immediately after creating PR
+
+**Correct approach:**
+
+- Complete Issue A -> Create PR -> Update A status to "In Review" -> Add A comment -> Complete Issue B -> ...
diff --git a/CLAUDE.md b/CLAUDE.md
index 78b661311e7..17d52a87d8a 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -57,55 +57,9 @@ see @.cursor/rules/typescript.mdc
 - **Dev**: Translate `locales/zh-CN/namespace.json` and `locales/en-US/namespace.json` locales file only for dev preview
 - DON'T run `pnpm i18n`, let CI auto handle it

-## Linear Issue Management (ignore if not installed linear mcp)
+## Linear Issue Management(ignore if not installed linear mcp)

-When working with Linear issues:
-
-1. **Retrieve issue details** before starting work using `mcp__linear-server__get_issue`
-2. **Check for sub-issues**: If the issue has sub-issues, retrieve and review ALL sub-issues using `mcp__linear-server__list_issues` with `parentId` filter before starting work
-3. **Update issue status** when completing tasks using `mcp__linear-server__update_issue`
-4. **MUST add completion comment** using `mcp__linear-server__create_comment`
-
-### Creating Issues
-
-When creating new Linear issues using `mcp__linear-server__create_issue`, **MUST add the `claude code` label** to indicate the issue was created by Claude Code.
-
-### Completion Comment (REQUIRED)
-
-**Every time you complete an issue, you MUST add a comment summarizing the work done.** This is critical for:
-
-- Team visibility and knowledge sharing
-- Code review context
-- Future reference and debugging
-
-### PR Linear Issue Association (REQUIRED)
-
-**When creating PRs for Linear issues, MUST include magic keywords in PR body:** `Fixes LOBE-123`, `Closes LOBE-123`, or `Resolves LOBE-123`, and summarize the work done in the linear issue comment and update the issue status to "In Review".
-
-### IMPORTANT: Per-Issue Completion Rule
-
-**When working with multiple issues (e.g., parent issue with sub-issues), you MUST update status and add comment for EACH issue IMMEDIATELY after completing it.** Do NOT wait until all issues are done to update them in batch.
-
-**Workflow for EACH individual issue:**
-
-1. Complete the implementation for this specific issue
-2. Run type check: `bun run type-check`
-3. Run related tests if applicable
-4. Create PR if needed
-5. **IMMEDIATELY** update issue status to **"In Review"** (NOT "Done"): `mcp__linear-server__update_issue`
-6. **IMMEDIATELY** add completion comment: `mcp__linear-server__create_comment`
-7. Only then move on to the next issue
-
-**Note:** Issue status should be set to **"In Review"** when PR is created. The status will be updated to **"Done"** only after the PR is merged (usually handled by Linear-GitHub integration or manually).
-
-**Wrong approach:**
-
-- Complete Issue A -> Complete Issue B -> Complete Issue C -> Update all statuses -> Add all comments
-- Mark issue as "Done" immediately after creating PR
-
-**Correct approach:**
-
-- Complete Issue A -> Create PR -> Update A status to "In Review" -> Add A comment -> Complete Issue B -> ...
+Read @.cursor/rules/linear.mdc when working with Linear issues.

 ## Rules Index

diff --git a/src/libs/swr/index.ts b/src/libs/swr/index.ts
index 6117caf6617..f612d9e3422 100644
--- a/src/libs/swr/index.ts
+++ b/src/libs/swr/index.ts
@@ -1,23 +1,13 @@
 import useSWR, { type SWRHook } from 'swr';
-import useSWRMutation from 'swr/mutation';

 /**
- * This type of request method is relatively flexible data, which will be triggered on the first time
+ * This type of request method is for relatively flexible data, which will be triggered on the first time.
  *
  * Refresh rules have two types:
- *
- * - when the user refocuses, it will be refreshed outside the 5mins interval.
- * - can be combined with refreshXXX methods to refresh data
+ * - When the user refocuses, it will be refreshed outside the 5mins interval.
+ * - Can be combined with refreshXXX methods to refresh data.
  *
  * Suitable for messages, topics, sessions, and other data that users will interact with on the client.
- *
- * 这一类请求方法是相对灵活的数据，会在请求时触发
- *
- * 刷新规则有两种：
- * - 当用户重新聚焦时，在 5mins 间隔外会重新刷新一次
- * - 可以搭配 refreshXXX 这样的方法刷新数据
- *
- * 适用于 messages、topics、sessions 等用户会在客户端交互的数据
  */
 // @ts-ignore
 export const useClientDataSWR: SWRHook = (key, fetch, config) =>
@@ -47,11 +37,8 @@ export const useClientDataSWR: SWRHook = (key, fetch, config) =>
   });

 /**
- * This type of request method is relatively "dead" request mode, which will only be triggered on the first request.
- * it suitable for first time request like `initUserState`
-
- * 这一类请求方法是相对"死"的请求模式，只会在第一次请求时触发。
- * 适用于第一次请求，例如 `initUserState`
+ * This type of request method is a relatively "static" request mode, which will only be triggered on the first request.
+ * Suitable for first time requests like `initUserState`.
  */
 // @ts-ignore
 export const useOnlyFetchOnceSWR: SWRHook = (key, fetch, config) =>
@@ -63,18 +50,27 @@ export const useOnlyFetchOnceSWR: SWRHook = (key, fetch, config) =>
   });

 /**
- * 这一类请求方法用于做操作触发，必须使用 mutate 来触发请求操作，好处是自带了 loading / error 状态。
- * 可以很简单地完成 loading / error 态的交互处理，同时，相同 swr key 的请求会自动共享 loading 态（例如新建助理按钮和右上角的 + 号）
- * 非常适用于新建等操作。
+ * This type of request method is for action triggers. Must use mutate to trigger the request.
+ * Benefits: built-in loading/error states, easy to handle loading/error UI interactions.
+ * Components with the same SWR key will automatically share loading state (e.g., create agent button and the + button in header).
+ * Very suitable for create operations.
  *
- * 使用 useSWRMutation 而非 useSWR，因为 useSWR 即使设置了 revalidateOnMount: false，
- * 在缓存为空时仍会自动调用 fetcher。而 useSWRMutation 只会在手动调用 trigger 时执行。
+ * Uses fallbackData as empty object so SWR thinks initial data exists.
+ * Combined with revalidateOnMount: false, this prevents auto-fetch on mount.
  */
-export const useActionSWR = <T>(key: string | any[], fetcher: () => Promise<T>, config?: any) => {
-  const { trigger, isMutating, ...rest } = useSWRMutation(key, fetcher, config);
-  // Return with legacy property names for backward compatibility
-  return { ...rest, isValidating: isMutating, mutate: trigger };
-};
+// @ts-ignore
+export const useActionSWR: SWRHook = (key, fetch, config) =>
+  useSWR(key, fetch, {
+    // Use empty object as fallback to prevent auto-fetch when cache is empty
+    // Combined with revalidateOnMount: false, SWR won't call fetcher on mount
+    fallbackData: {},
+    refreshWhenHidden: false,
+    refreshWhenOffline: false,
+    revalidateOnFocus: false,
+    revalidateOnMount: false,
+    revalidateOnReconnect: false,
+    ...config,
+  });

 export interface SWRRefreshParams<T, A = (...args: any[]) => any> {
   action: A;
@@ -85,8 +81,8 @@ export type SWRefreshMethod<T> = <A extends (...args: any[]) => Promise<any>>(
   params?: SWRRefreshParams<T, A>,
 ) => ReturnType<A>;

-// 导出带自动同步功能的 hook
+// Export hook with auto-sync functionality
 export { useClientDataSWRWithSync } from './useClientDataSWRWithSync';

-// 导出 scoped mutate（用于自定义 cache provider 场景）
+// Export scoped mutate (for custom cache provider scenarios)
 export { mutate, setScopedMutate } from './mutate';

PATCH

echo "Patch applied successfully."
