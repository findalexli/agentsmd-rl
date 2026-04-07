#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if ! grep -q 'triggerAndPoll' packages/trigger-sdk/src/v3/shared.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/slow-games-drum.md b/.changeset/slow-games-drum.md
new file mode 100644
index 00000000000..c1ab229f862
--- /dev/null
+++ b/.changeset/slow-games-drum.md
@@ -0,0 +1,5 @@
+---
+"@trigger.dev/sdk": patch
+---
+
+Removed triggerAndPoll. It was never recommended so it's been removed.
diff --git a/.cursor/rules/writing-tasks.mdc b/.cursor/rules/writing-tasks.mdc
index 6090b85f090..5116d083e23 100644
--- a/.cursor/rules/writing-tasks.mdc
+++ b/.cursor/rules/writing-tasks.mdc
@@ -431,28 +431,6 @@ export async function POST(request: Request) {
 }
 ```

-### tasks.triggerAndPoll()
-
-Triggers a task and polls until completion. Not recommended for web requests as it blocks until the run completes. Consider using Realtime docs for better alternatives.
-
-```ts
-import { tasks } from "@trigger.dev/sdk/v3";
-import type { emailSequence } from "~/trigger/emails";
-
-export async function POST(request: Request) {
-  const data = await request.json();
-  const result = await tasks.triggerAndPoll<typeof emailSequence>(
-    "email-sequence",
-    {
-      to: data.email,
-      name: data.name,
-    },
-    { pollIntervalMs: 5000 }
-  );
-  return Response.json(result);
-}
-```
-
 ### batch.trigger()

 Triggers multiple runs of different tasks at once, useful when you need to execute multiple tasks simultaneously.
diff --git a/docs/triggering.mdx b/docs/triggering.mdx
index 39dc2c8a178..c96ed1357c8 100644
--- a/docs/triggering.mdx
+++ b/docs/triggering.mdx
@@ -7,12 +7,11 @@ description: "Tasks need to be triggered in order to run."

 Trigger tasks **from your backend**:

-| Function                 | What it does                                                                                     |                               |
-| :----------------------- | :----------------------------------------------------------------------------------------------- | ----------------------------- |
-| `tasks.trigger()`        | Triggers a task and returns a handle you can use to fetch and manage the run.                    | [Docs](#tasks-trigger)        |
-| `tasks.batchTrigger()`   | Triggers a single task in a batch and returns a handle you can use to fetch and manage the runs. | [Docs](#tasks-batchtrigger)   |
-| `tasks.triggerAndPoll()` | Triggers a task and then polls the run until it's complete.                                      | [Docs](#tasks-triggerandpoll) |
-| `batch.trigger()`        | Similar to `tasks.batchTrigger` but allows running multiple different tasks                      | [Docs](#batch-trigger)        |
+| Function               | What it does                                                                                     |                             |
+| :--------------------- | :----------------------------------------------------------------------------------------------- | --------------------------- |
+| `tasks.trigger()`      | Triggers a task and returns a handle you can use to fetch and manage the run.                    | [Docs](#tasks-trigger)      |
+| `tasks.batchTrigger()` | Triggers a single task in a batch and returns a handle you can use to fetch and manage the runs. | [Docs](#tasks-batchtrigger) |
+| `batch.trigger()`      | Similar to `tasks.batchTrigger` but allows running multiple different tasks                      | [Docs](#batch-trigger)      |

 Trigger tasks **from inside a another task**:

@@ -162,40 +161,6 @@ export async function POST(request: Request) {
 }
 ```

-### tasks.triggerAndPoll()
-
-Triggers a single run of a task with the payload you pass in, and any options you specify, and then polls the run until it's complete.
-
-<Warning>
-  We don't recommend using `triggerAndPoll()`, especially inside a web request, as it will block the
-  request until the run is complete. Please see our [Realtime docs](/realtime) for a better way to
-  handle this.
-</Warning>
-
-```ts Your backend
-import { tasks } from "@trigger.dev/sdk/v3";
-import type { emailSequence } from "~/trigger/emails";
-
-//app/email/route.ts
-export async function POST(request: Request) {
-  //get the JSON from the request
-  const data = await request.json();
-
-  // Pass the task type to `triggerAndPoll()` as a generic argument, giving you full type checking
-  const result = await tasks.triggerAndPoll<typeof emailSequence>(
-    "email-sequence",
-    {
-      to: data.email,
-      name: data.name,
-    },
-    { pollIntervalMs: 5000 }
-  );
-
-  //return a success response with the result
-  return Response.json(result);
-}
-```
-
 ### batch.trigger()

 Triggers multiple runs of different tasks with the payloads you pass in, and any options you specify. This is useful when you need to trigger multiple tasks at once.
diff --git a/packages/trigger-sdk/src/v3/shared.ts b/packages/trigger-sdk/src/v3/shared.ts
index 1a05d766cb6..deb3f4f6f1f 100644
--- a/packages/trigger-sdk/src/v3/shared.ts
+++ b/packages/trigger-sdk/src/v3/shared.ts
@@ -490,32 +490,6 @@ export async function batchTriggerAndWait<TTask extends AnyTask>(
   >("tasks.batchTriggerAndWait()", id, items, undefined, options, requestOptions);
 }

-/**
- * Trigger a task by its identifier with the given payload and poll until the run is completed.
- *
- * @example
- *
- * ```ts
- * import { tasks, runs } from "@trigger.dev/sdk/v3";
- * import type { myTask } from "./myTasks"; // Import just the type of the task
- *
- * const run = await tasks.triggerAndPoll<typeof myTask>("my-task", { foo: "bar" }); // The id and payload are fully typesafe
- * console.log(run.output) // The output is also fully typed
- * ```
- *
- * @returns {Run} The completed run, either successful or failed.
- */
-export async function triggerAndPoll<TTask extends AnyTask>(
-  id: TaskIdentifier<TTask>,
-  payload: TaskPayload<TTask>,
-  options?: TriggerOptions & PollOptions,
-  requestOptions?: TriggerApiRequestOptions
-): Promise<RetrieveRunResult<TTask>> {
-  const handle = await trigger(id, payload, options, requestOptions);
-
-  return runs.poll(handle, options, requestOptions);
-}
-
 export async function batchTrigger<TTask extends AnyTask>(
   id: TaskIdentifier<TTask>,
   items: Array<BatchItem<TaskPayload<TTask>>>,
diff --git a/packages/trigger-sdk/src/v3/tasks.ts b/packages/trigger-sdk/src/v3/tasks.ts
index 71cb6acd5b6..078666dc687 100644
--- a/packages/trigger-sdk/src/v3/tasks.ts
+++ b/packages/trigger-sdk/src/v3/tasks.ts
@@ -18,7 +18,6 @@ import {
   createToolTask,
   SubtaskUnwrapError,
   trigger,
-  triggerAndPoll,
   triggerAndWait,
 } from "./shared.js";

@@ -86,7 +85,6 @@ export const toolTask = createToolTask;

 export const tasks = {
   trigger,
-  triggerAndPoll,
   batchTrigger,
   triggerAndWait,
   batchTriggerAndWait,
diff --git a/references/v3-catalog/src/trigger/sdkUsage.ts b/references/v3-catalog/src/trigger/sdkUsage.ts
index 0bca9231e0b..3a75afecb18 100644
--- a/references/v3-catalog/src/trigger/sdkUsage.ts
+++ b/references/v3-catalog/src/trigger/sdkUsage.ts
@@ -14,10 +14,6 @@ export const sdkUsage = task({
       run: $firstRun,
     });

-    await tasks.triggerAndPoll<typeof sdkChild>("sdk-child", {
-      handle,
-    });
-
     const replayedRun = await runs.replay($firstRun.id);

     await runs.cancel(replayedRun.id);

PATCH

echo "Patch applied successfully."
