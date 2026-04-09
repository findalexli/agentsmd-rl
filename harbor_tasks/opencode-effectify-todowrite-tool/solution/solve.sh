#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'Tool.defineEffect' packages/opencode/src/tool/todo.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/session/todo.ts b/packages/opencode/src/session/todo.ts
index 8bb5dc522ad6..2d85ad224f1b 100644
--- a/packages/opencode/src/session/todo.ts
+++ b/packages/opencode/src/session/todo.ts
@@ -82,7 +82,7 @@ export namespace Todo {
     }),
   )

-  const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
+  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
   const { runPromise } = makeRuntime(Service, defaultLayer)

   export async function update(input: { sessionID: SessionID; todos: Info[] }) {
diff --git a/packages/opencode/src/tool/registry.ts b/packages/opencode/src/tool/registry.ts
index 8e21c43e3cd9..b538a9e88018 100644
--- a/packages/opencode/src/tool/registry.ts
+++ b/packages/opencode/src/tool/registry.ts
@@ -34,6 +34,7 @@ import { InstanceState } from "@/effect/instance-state"
 import { makeRuntime } from "@/effect/run-service"
 import { Env } from "../env"
 import { Question } from "../question"
+import { Todo } from "../session/todo"

 export namespace ToolRegistry {
   const log = Log.create({ service: "tool.registry" })
@@ -56,165 +57,167 @@ export namespace ToolRegistry {

   export class Service extends ServiceMap.Service<Service, Interface>()("@opencode/ToolRegistry") {}

-  export const layer: Layer.Layer<Service, never, Config.Service | Plugin.Service | Question.Service> = Layer.effect(
-    Service,
-    Effect.gen(function* () {
-      const config = yield* Config.Service
-      const plugin = yield* Plugin.Service
-
-      const build = <T extends Tool.Info>(tool: T | Effect.Effect<T, never, any>) =>
-        Effect.isEffect(tool) ? tool : Effect.succeed(tool)
-
-      const state = yield* InstanceState.make<State>(
-        Effect.fn("ToolRegistry.state")(function* (ctx) {
-          const custom: Tool.Info[] = []
-
-          function fromPlugin(id: string, def: ToolDefinition): Tool.Info {
-            return {
-              id,
-              init: async (initCtx) => ({
-                parameters: z.object(def.args),
-                description: def.description,
-                execute: async (args, toolCtx) => {
-                  const pluginCtx = {
-                    ...toolCtx,
-                    directory: ctx.directory,
-                    worktree: ctx.worktree,
-                  } as unknown as PluginToolContext
-                  const result = await def.execute(args as any, pluginCtx)
-                  const out = await Truncate.output(result, {}, initCtx?.agent)
-                  return {
-                    title: "",
-                    output: out.truncated ? out.content : result,
-                    metadata: { truncated: out.truncated, outputPath: out.truncated ? out.outputPath : undefined },
-                  }
-                },
-              }),
+  export const layer: Layer.Layer<Service, never, Config.Service | Plugin.Service | Question.Service | Todo.Service> =
+    Layer.effect(
+      Service,
+      Effect.gen(function* () {
+        const config = yield* Config.Service
+        const plugin = yield* Plugin.Service
+
+        const build = <T extends Tool.Info>(tool: T | Effect.Effect<T, never, any>) =>
+          Effect.isEffect(tool) ? tool : Effect.succeed(tool)
+
+        const state = yield* InstanceState.make<State>(
+          Effect.fn("ToolRegistry.state")(function* (ctx) {
+            const custom: Tool.Info[] = []
+
+            function fromPlugin(id: string, def: ToolDefinition): Tool.Info {
+              return {
+                id,
+                init: async (initCtx) => ({
+                  parameters: z.object(def.args),
+                  description: def.description,
+                  execute: async (args, toolCtx) => {
+                    const pluginCtx = {
+                      ...toolCtx,
+                      directory: ctx.directory,
+                      worktree: ctx.worktree,
+                    } as unknown as PluginToolContext
+                    const result = await def.execute(args as any, pluginCtx)
+                    const out = await Truncate.output(result, {}, initCtx?.agent)
+                    return {
+                      title: "",
+                      output: out.truncated ? out.content : result,
+                      metadata: { truncated: out.truncated, outputPath: out.truncated ? out.outputPath : undefined },
+                    }
+                  },
+                }),
+              }
             }
-          }

-          const dirs = yield* config.directories()
-          const matches = dirs.flatMap((dir) =>
-            Glob.scanSync("{tool,tools}/*.{js,ts}", { cwd: dir, absolute: true, dot: true, symlink: true }),
-          )
-          if (matches.length) yield* config.waitForDependencies()
-          for (const match of matches) {
-            const namespace = path.basename(match, path.extname(match))
-            const mod = yield* Effect.promise(
-              () => import(process.platform === "win32" ? match : pathToFileURL(match).href),
+            const dirs = yield* config.directories()
+            const matches = dirs.flatMap((dir) =>
+              Glob.scanSync("{tool,tools}/*.{js,ts}", { cwd: dir, absolute: true, dot: true, symlink: true }),
             )
-            for (const [id, def] of Object.entries<ToolDefinition>(mod)) {
-              custom.push(fromPlugin(id === "default" ? namespace : `${namespace}_${id}`, def))
+            if (matches.length) yield* config.waitForDependencies()
+            for (const match of matches) {
+              const namespace = path.basename(match, path.extname(match))
+              const mod = yield* Effect.promise(
+                () => import(process.platform === "win32" ? match : pathToFileURL(match).href),
+              )
+              for (const [id, def] of Object.entries<ToolDefinition>(mod)) {
+                custom.push(fromPlugin(id === "default" ? namespace : `${namespace}_${id}`, def))
+              }
             }
-          }

-          const plugins = yield* plugin.list()
-          for (const p of plugins) {
-            for (const [id, def] of Object.entries(p.tool ?? {})) {
-              custom.push(fromPlugin(id, def))
-            }
-          }
-
-          return { custom }
-        }),
-      )
-
-      const invalid = yield* build(InvalidTool)
-      const ask = yield* build(QuestionTool)
-      const bash = yield* build(BashTool)
-      const read = yield* build(ReadTool)
-      const glob = yield* build(GlobTool)
-      const grep = yield* build(GrepTool)
-      const edit = yield* build(EditTool)
-      const write = yield* build(WriteTool)
-      const task = yield* build(TaskTool)
-      const fetch = yield* build(WebFetchTool)
-      const todo = yield* build(TodoWriteTool)
-      const search = yield* build(WebSearchTool)
-      const code = yield* build(CodeSearchTool)
-      const skill = yield* build(SkillTool)
-      const patch = yield* build(ApplyPatchTool)
-      const lsp = yield* build(LspTool)
-      const batch = yield* build(BatchTool)
-      const plan = yield* build(PlanExitTool)
-
-      const all = Effect.fn("ToolRegistry.all")(function* (custom: Tool.Info[]) {
-        const cfg = yield* config.get()
-        const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL
-
-        return [
-          invalid,
-          ...(question ? [ask] : []),
-          bash,
-          read,
-          glob,
-          grep,
-          edit,
-          write,
-          task,
-          fetch,
-          todo,
-          search,
-          code,
-          skill,
-          patch,
-          ...(Flag.OPENCODE_EXPERIMENTAL_LSP_TOOL ? [lsp] : []),
-          ...(cfg.experimental?.batch_tool === true ? [batch] : []),
-          ...(Flag.OPENCODE_EXPERIMENTAL_PLAN_MODE && Flag.OPENCODE_CLIENT === "cli" ? [plan] : []),
-          ...custom,
-        ]
-      })
-
-      const ids = Effect.fn("ToolRegistry.ids")(function* () {
-        const s = yield* InstanceState.get(state)
-        const tools = yield* all(s.custom)
-        return tools.map((t) => t.id)
-      })
-
-      const tools = Effect.fn("ToolRegistry.tools")(function* (
-        model: { providerID: ProviderID; modelID: ModelID },
-        agent?: Agent.Info,
-      ) {
-        const s = yield* InstanceState.get(state)
-        const allTools = yield* all(s.custom)
-        const filtered = allTools.filter((tool) => {
-          if (tool.id === "codesearch" || tool.id === "websearch") {
-            return model.providerID === ProviderID.opencode || Flag.OPENCODE_ENABLE_EXA
-          }
-
-          const usePatch =
-            !!Env.get("OPENCODE_E2E_LLM_URL") ||
-            (model.modelID.includes("gpt-") && !model.modelID.includes("oss") && !model.modelID.includes("gpt-4"))
-          if (tool.id === "apply_patch") return usePatch
-          if (tool.id === "edit" || tool.id === "write") return !usePatch
-
-          return true
-        })
-        return yield* Effect.forEach(
-          filtered,
-          Effect.fnUntraced(function* (tool: Tool.Info) {
-            using _ = log.time(tool.id)
-            const next = yield* Effect.promise(() => tool.init({ agent }))
-            const output = {
-              description: next.description,
-              parameters: next.parameters,
-            }
-            yield* plugin.trigger("tool.definition", { toolID: tool.id }, output)
-            return {
-              id: tool.id,
-              description: output.description,
-              parameters: output.parameters,
-              execute: next.execute,
-              formatValidationError: next.formatValidationError,
+            const plugins = yield* plugin.list()
+            for (const p of plugins) {
+              for (const [id, def] of Object.entries(p.tool ?? {})) {
+                custom.push(fromPlugin(id, def))
+              }
             }
+
+            return { custom }
           }),
-          { concurrency: "unbounded" },
         )
-      })

-      return Service.of({ ids, named: { task, read }, tools })
-    }),
-  )
+        const invalid = yield* build(InvalidTool)
+        const ask = yield* build(QuestionTool)
+        const bash = yield* build(BashTool)
+        const read = yield* build(ReadTool)
+        const glob = yield* build(GlobTool)
+        const grep = yield* build(GrepTool)
+        const edit = yield* build(EditTool)
+        const write = yield* build(WriteTool)
+        const task = yield* build(TaskTool)
+        const fetch = yield* build(WebFetchTool)
+        const todo = yield* build(TodoWriteTool)
+        const search = yield* build(WebSearchTool)
+        const code = yield* build(CodeSearchTool)
+        const skill = yield* build(SkillTool)
+        const patch = yield* build(ApplyPatchTool)
+        const lsp = yield* build(LspTool)
+        const batch = yield* build(BatchTool)
+        const plan = yield* build(PlanExitTool)
+
+        const all = Effect.fn("ToolRegistry.all")(function* (custom: Tool.Info[]) {
+          const cfg = yield* config.get()
+          const question =
+            ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL
+
+          return [
+            invalid,
+            ...(question ? [ask] : []),
+            bash,
+            read,
+            glob,
+            grep,
+            edit,
+            write,
+            task,
+            fetch,
+            todo,
+            search,
+            code,
+            skill,
+            patch,
+            ...(Flag.OPENCODE_EXPERIMENTAL_LSP_TOOL ? [lsp] : []),
+            ...(cfg.experimental?.batch_tool === true ? [batch] : []),
+            ...(Flag.OPENCODE_EXPERIMENTAL_PLAN_MODE && Flag.OPENCODE_CLIENT === "cli" ? [plan] : []),
+            ...custom,
+          ]
+        })
+
+        const ids = Effect.fn("ToolRegistry.ids")(function* () {
+          const s = yield* InstanceState.get(state)
+          const tools = yield* all(s.custom)
+          return tools.map((t) => t.id)
+        })
+
+        const tools = Effect.fn("ToolRegistry.tools")(function* (
+          model: { providerID: ProviderID; modelID: ModelID },
+          agent?: Agent.Info,
+        ) {
+          const s = yield* InstanceState.get(state)
+          const allTools = yield* all(s.custom)
+          const filtered = allTools.filter((tool) => {
+            if (tool.id === "codesearch" || tool.id === "websearch") {
+              return model.providerID === ProviderID.opencode || Flag.OPENCODE_ENABLE_EXA
+            }
+
+            const usePatch =
+              !!Env.get("OPENCODE_E2E_LLM_URL") ||
+              (model.modelID.includes("gpt-") && !model.modelID.includes("oss") && !model.modelID.includes("gpt-4"))
+            if (tool.id === "apply_patch") return usePatch
+            if (tool.id === "edit" || tool.id === "write") return !usePatch
+
+            return true
+          })
+          return yield* Effect.forEach(
+            filtered,
+            Effect.fnUntraced(function* (tool: Tool.Info) {
+              using _ = log.time(tool.id)
+              const next = yield* Effect.promise(() => tool.init({ agent }))
+              const output = {
+                description: next.description,
+                parameters: next.parameters,
+              }
+              yield* plugin.trigger("tool.definition", { toolID: tool.id }, output)
+              return {
+                id: tool.id,
+                description: output.description,
+                parameters: output.parameters,
+                execute: next.execute,
+                formatValidationError: next.formatValidationError,
+              }
+            }),
+            { concurrency: "unbounded" },
+          )
+        })
+
+        return Service.of({ ids, named: { task, read }, tools })
+      }),
+    )

   export const defaultLayer = Layer.unwrap(
     Effect.sync(() =>
@@ -222,6 +225,7 @@ export namespace ToolRegistry {
         Layer.provide(Config.defaultLayer),
         Layer.provide(Plugin.defaultLayer),
         Layer.provide(Question.defaultLayer),
+        Layer.provide(Todo.defaultLayer),
       ),
     ),
   )
diff --git a/packages/opencode/src/tool/todo.ts b/packages/opencode/src/tool/todo.ts
index a5e56cb23e43..d10e84931ab0 100644
--- a/packages/opencode/src/tool/todo.ts
+++ b/packages/opencode/src/tool/todo.ts
@@ -1,31 +1,48 @@
 import z from "zod"
+import { Effect } from "effect"
 import { Tool } from "./tool"
 import DESCRIPTION_WRITE from "./todowrite.txt"
 import { Todo } from "../session/todo"

-export const TodoWriteTool = Tool.define("todowrite", {
-  description: DESCRIPTION_WRITE,
-  parameters: z.object({
-    todos: z.array(z.object(Todo.Info.shape)).describe("The updated todo list"),
-  }),
-  async execute(params, ctx) {
-    await ctx.ask({
-      permission: "todowrite",
-      patterns: ["*"],
-      always: ["*"],
-      metadata: {},
-    })
+const parameters = z.object({
+  todos: z.array(z.object(Todo.Info.shape)).describe("The updated todo list"),
+})
+
+type Metadata = {
+  todos: Todo.Info[]
+}
+
+export const TodoWriteTool = Tool.defineEffect<typeof parameters, Metadata, Todo.Service>(
+  "todowrite",
+  Effect.gen(function* () {
+    const todo = yield* Todo.Service

-    await Todo.update({
-      sessionID: ctx.sessionID,
-      todos: params.todos,
-    })
     return {
-      title: `${params.todos.filter((x) => x.status !== "completed").length} todos`,
-      output: JSON.stringify(params.todos, null, 2),
-      metadata: {
-        todos: params.todos,
+      description: DESCRIPTION_WRITE,
+      parameters,
+      async execute(params: z.infer<typeof parameters>, ctx: Tool.Context<Metadata>) {
+        await ctx.ask({
+          permission: "todowrite",
+          patterns: ["*"],
+          always: ["*"],
+          metadata: {},
+        })
+
+        await todo
+          .update({
+            sessionID: ctx.sessionID,
+            todos: params.todos,
+          })
+          .pipe(Effect.runPromise)
+
+        return {
+          title: `${params.todos.filter((x) => x.status !== "completed").length} todos`,
+          output: JSON.stringify(params.todos, null, 2),
+          metadata: {
+            todos: params.todos,
+          },
+        }
       },
-    }
-  },
-})
+    } satisfies Tool.Def<typeof parameters, Metadata>
+  }),
+)
diff --git a/packages/opencode/test/session/prompt-effect.test.ts b/packages/opencode/test/session/prompt-effect.test.ts
index a6fd1f27dbe3..17689cf274ec 100644
--- a/packages/opencode/test/session/prompt-effect.test.ts
+++ b/packages/opencode/test/session/prompt-effect.test.ts
@@ -16,6 +16,7 @@ import { Provider as ProviderSvc } from "../../src/provider/provider"
 import type { Provider } from "../../src/provider/provider"
 import { ModelID, ProviderID } from "../../src/provider/schema"
 import { Question } from "../../src/question"
+import { Todo } from "../../src/session/todo"
 import { Session } from "../../src/session"
 import { LLM } from "../../src/session/llm"
 import { MessageV2 } from "../../src/session/message-v2"
@@ -162,7 +163,12 @@ function makeHttp() {
     status,
   ).pipe(Layer.provideMerge(infra))
   const question = Question.layer.pipe(Layer.provideMerge(deps))
-  const registry = ToolRegistry.layer.pipe(Layer.provideMerge(question), Layer.provideMerge(deps))
+  const todo = Todo.layer.pipe(Layer.provideMerge(deps))
+  const registry = ToolRegistry.layer.pipe(
+    Layer.provideMerge(todo),
+    Layer.provideMerge(question),
+    Layer.provideMerge(deps),
+  )
   const trunc = Truncate.layer.pipe(Layer.provideMerge(deps))
   const proc = SessionProcessor.layer.pipe(Layer.provideMerge(deps))
   const compact = SessionCompaction.layer.pipe(Layer.provideMerge(proc), Layer.provideMerge(deps))
diff --git a/packages/opencode/test/session/snapshot-tool-race.test.ts b/packages/opencode/test/session/snapshot-tool-race.test.ts
index 019cf1a796dd..c192a446bd49 100644
--- a/packages/opencode/test/session/snapshot-tool-race.test.ts
+++ b/packages/opencode/test/session/snapshot-tool-race.test.ts
@@ -39,6 +39,7 @@ import { Permission } from "../../src/permission"
 import { Plugin } from "../../src/plugin"
 import { Provider as ProviderSvc } from "../../src/provider/provider"
 import { Question } from "../../src/question"
+import { Todo } from "../../src/session/todo"
 import { SessionCompaction } from "../../src/session/compaction"
 import { Instruction } from "../../src/session/instruction"
 import { SessionProcessor } from "../../src/session/processor"
@@ -126,7 +127,12 @@ function makeHttp() {
     status,
   ).pipe(Layer.provideMerge(infra))
   const question = Question.layer.pipe(Layer.provideMerge(deps))
-  const registry = ToolRegistry.layer.pipe(Layer.provideMerge(question), Layer.provideMerge(deps))
+  const todo = Todo.layer.pipe(Layer.provideMerge(deps))
+  const registry = ToolRegistry.layer.pipe(
+    Layer.provideMerge(todo),
+    Layer.provideMerge(question),
+    Layer.provideMerge(deps),
+  )
   const trunc = Truncate.layer.pipe(Layer.provideMerge(deps))
   const proc = SessionProcessor.layer.pipe(Layer.provideMerge(deps))
   const compact = SessionCompaction.layer.pipe(Layer.provideMerge(proc), Layer.provideMerge(deps))
diff --git a/packages/opencode/test/tool/tool-define.test.ts b/packages/opencode/test/tool/tool-define.test.ts
index b3ed66c93542..1503eed728f3 100644
--- a/packages/opencode/test/tool/tool-define.test.ts
+++ b/packages/opencode/test/tool/tool-define.test.ts
@@ -27,45 +27,37 @@ describe("Tool.define", () => {
     await tool.init()
     await tool.init()

-    // The original object's execute should never be overwritten
     expect(original.execute).toBe(originalExecute)
   })

   test("object-defined tool does not accumulate wrapper layers across init() calls", async () => {
-    let executeCalls = 0
+    let calls = 0

     const tool = Tool.define(
       "test-tool",
-      makeTool("test", () => executeCalls++),
+      makeTool("test", () => calls++),
     )

-    // Call init() many times to simulate many agentic steps
     for (let i = 0; i < 100; i++) {
       await tool.init()
     }

-    // Resolve the tool and call execute
     const resolved = await tool.init()
-    executeCalls = 0
+    calls = 0

-    // Capture the stack trace inside execute to measure wrapper depth
-    let stackInsideExecute = ""
-    const origExec = resolved.execute
+    let stack = ""
+    const exec = resolved.execute
     resolved.execute = async (args: any, ctx: any) => {
-      const result = await origExec.call(resolved, args, ctx)
-      const err = new Error()
-      stackInsideExecute = err.stack || ""
+      const result = await exec.call(resolved, args, ctx)
+      stack = new Error().stack || ""
       return result
     }

     await resolved.execute(defaultArgs, {} as any)
-    expect(executeCalls).toBe(1)
+    expect(calls).toBe(1)

-    // Count how many times tool.ts appears in the stack.
-    // With the fix: 1 wrapper layer (from the most recent init()).
-    // Without the fix: 101 wrapper layers from accumulated closures.
-    const toolTsFrames = stackInsideExecute.split("\n").filter((l) => l.includes("tool.ts")).length
-    expect(toolTsFrames).toBeLessThan(5)
+    const frames = stack.split("\n").filter((l) => l.includes("tool.ts")).length
+    expect(frames).toBeLessThan(5)
   })

   test("function-defined tool returns fresh objects and is unaffected", async () => {
@@ -74,7 +66,6 @@ describe("Tool.define", () => {
     const first = await tool.init()
     const second = await tool.init()

-    // Function-defined tools return distinct objects each time
     expect(first).not.toBe(second)
   })

@@ -84,7 +75,6 @@ describe("Tool.define", () => {
     const first = await tool.init()
     const second = await tool.init()

-    // Each init() should return a separate object so wrappers don't accumulate
     expect(first).not.toBe(second)
   })

PATCH

echo "Patch applied successfully."
