#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/opencode"
FILE="$REPO/packages/opencode/src/skill/index.ts"

# Idempotency: check if already applied
if grep -q 'const config = yield\* Config\.Service' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd "$REPO"
git apply - <<'PATCH'
diff --git a/packages/opencode/src/skill/index.ts b/packages/opencode/src/skill/index.ts
index aa3829683a5..e92e45b1ce4 100644
--- a/packages/opencode/src/skill/index.ts
+++ b/packages/opencode/src/skill/index.ts
@@ -63,16 +63,23 @@ export namespace Skill {
     readonly available: (agent?: Agent.Info) => Effect.Effect<Info[]>
   }

-  const add = async (state: State, match: string) => {
-    const md = await ConfigMarkdown.parse(match).catch(async (err) => {
-      const message = ConfigMarkdown.FrontmatterError.isInstance(err)
-        ? err.data.message
-        : `Failed to parse skill ${match}`
-      const { Session } = await import("@/session")
-      Bus.publish(Session.Event.Error, { error: new NamedError.Unknown({ message }).toObject() })
-      log.error("failed to load skill", { skill: match, err })
-      return undefined
-    })
+  const add = Effect.fnUntraced(function* (state: State, match: string, bus: Bus.Interface) {
+    const md = yield* Effect.tryPromise({
+      try: () => ConfigMarkdown.parse(match),
+      catch: (err) => err,
+    }).pipe(
+      Effect.catch(
+        Effect.fnUntraced(function* (err) {
+          const message = ConfigMarkdown.FrontmatterError.isInstance(err)
+            ? err.data.message
+            : `Failed to parse skill ${match}`
+          const { Session } = yield* Effect.promise(() => import("@/session"))
+          yield* bus.publish(Session.Event.Error, { error: new NamedError.Unknown({ message }).toObject() })
+          log.error("failed to load skill", { skill: match, err })
+          return undefined
+        }),
+      ),
+    )

     if (!md) return

@@ -94,80 +101,115 @@ export namespace Skill {
       location: match,
       content: md.content,
     }
-  }
+  })

-  const scan = async (state: State, root: string, pattern: string, opts?: { dot?: boolean; scope?: string }) => {
-    return Glob.scan(pattern, {
-      cwd: root,
-      absolute: true,
-      include: "file",
-      symlink: true,
-      dot: opts?.dot,
-    })
-      .then((matches) => Promise.all(matches.map((match) => add(state, match))))
-      .catch((error) => {
-        if (!opts?.scope) throw error
+  const scan = Effect.fnUntraced(function* (
+    state: State,
+    bus: Bus.Interface,
+    root: string,
+    pattern: string,
+    opts?: { dot?: boolean; scope?: string },
+  ) {
+    const matches = yield* Effect.tryPromise({
+      try: () =>
+        Glob.scan(pattern, {
+          cwd: root,
+          absolute: true,
+          include: "file",
+          symlink: true,
+          dot: opts?.dot,
+        }),
+      catch: (error) => error,
+    }).pipe(
+      Effect.catch((error) => {
+        if (!opts?.scope) return Effect.die(error)
         log.error(`failed to scan ${opts.scope} skills`, { dir: root, error })
-      })
-  }
+        return Effect.succeed([] as string[])
+      }),
+    )
+
+    yield* Effect.forEach(matches, (match) => add(state, match, bus), {
+      concurrency: "unbounded",
+      discard: true,
+    })
+  })

-  async function loadSkills(state: State, discovery: Discovery.Interface, directory: string, worktree: string) {
+  const loadSkills = Effect.fnUntraced(function* (
+    state: State,
+    config: Config.Interface,
+    discovery: Discovery.Interface,
+    bus: Bus.Interface,
+    directory: string,
+    worktree: string,
+  ) {
     if (!Flag.OPENCODE_DISABLE_EXTERNAL_SKILLS) {
       for (const dir of EXTERNAL_DIRS) {
         const root = path.join(Global.Path.home, dir)
-        if (!(await Filesystem.isDir(root))) continue
-        await scan(state, root, EXTERNAL_SKILL_PATTERN, { dot: true, scope: "global" })
+        const isDir = yield* Effect.promise(() => Filesystem.isDir(root))
+        if (!isDir) continue
+        yield* scan(state, bus, root, EXTERNAL_SKILL_PATTERN, { dot: true, scope: "global" })
       }

-      for await (const root of Filesystem.up({
-        targets: EXTERNAL_DIRS,
-        start: directory,
-        stop: worktree,
-      })) {
-        await scan(state, root, EXTERNAL_SKILL_PATTERN, { dot: true, scope: "project" })
+      const upDirs = yield* Effect.promise(async () => {
+        const dirs: string[] = []
+        for await (const root of Filesystem.up({
+          targets: EXTERNAL_DIRS,
+          start: directory,
+          stop: worktree,
+        })) {
+          dirs.push(root)
+        }
+        return dirs
+      })
+
+      for (const root of upDirs) {
+        yield* scan(state, bus, root, EXTERNAL_SKILL_PATTERN, { dot: true, scope: "project" })
       }
     }

-    for (const dir of await Config.directories()) {
-      await scan(state, dir, OPENCODE_SKILL_PATTERN)
+    const configDirs = yield* config.directories()
+    for (const dir of configDirs) {
+      yield* scan(state, bus, dir, OPENCODE_SKILL_PATTERN)
     }

-    const cfg = await Config.get()
+    const cfg = yield* config.get()
     for (const item of cfg.skills?.paths ?? []) {
       const expanded = item.startsWith("~/") ? path.join(os.homedir(), item.slice(2)) : item
       const dir = path.isAbsolute(expanded) ? expanded : path.join(directory, expanded)
-      if (!(await Filesystem.isDir(dir))) {
+      const isDir = yield* Effect.promise(() => Filesystem.isDir(dir))
+      if (!isDir) {
         log.warn("skill path not found", { path: dir })
         continue
       }

-      await scan(state, dir, SKILL_PATTERN)
+      yield* scan(state, bus, dir, SKILL_PATTERN)
     }

     for (const url of cfg.skills?.urls ?? []) {
-      for (const dir of await Effect.runPromise(discovery.pull(url))) {
+      const pulledDirs = yield* discovery.pull(url)
+      for (const dir of pulledDirs) {
         state.dirs.add(dir)
-        await scan(state, dir, SKILL_PATTERN)
+        yield* scan(state, bus, dir, SKILL_PATTERN)
       }
     }

     log.info("init", { count: Object.keys(state.skills).length })
-  }
+  })

   export class Service extends ServiceMap.Service<Service, Interface>()("@opencode/Skill") {}

-  export const layer: Layer.Layer<Service, never, Discovery.Service> = Layer.effect(
+  export const layer: Layer.Layer<Service, never, Discovery.Service | Config.Service | Bus.Service> = Layer.effect(
     Service,
     Effect.gen(function* () {
       const discovery = yield* Discovery.Service
+      const config = yield* Config.Service
+      const bus = yield* Bus.Service
       const state = yield* InstanceState.make(
-        Effect.fn("Skill.state")((ctx) =>
-          Effect.gen(function* () {
-            const s: State = { skills: {}, dirs: new Set() }
-            yield* Effect.promise(() => loadSkills(s, discovery, ctx.directory, ctx.worktree))
-            return s
-          }),
-        ),
+        Effect.fn("Skill.state")(function* (ctx) {
+          const s: State = { skills: {}, dirs: new Set() }
+          yield* loadSkills(s, config, discovery, bus, ctx.directory, ctx.worktree)
+          return s
+        }),
       )

       const get = Effect.fn("Skill.get")(function* (name: string) {
@@ -196,7 +238,11 @@ export namespace Skill {
     }),
   )

-  export const defaultLayer: Layer.Layer<Service> = layer.pipe(Layer.provide(Discovery.defaultLayer))
+  export const defaultLayer: Layer.Layer<Service> = layer.pipe(
+    Layer.provide(Discovery.defaultLayer),
+    Layer.provide(Config.defaultLayer),
+    Layer.provide(Bus.layer),
+  )

   export function fmt(list: Info[], opts: { verbose: boolean }) {
     if (list.length === 0) return "No skills are currently available."

PATCH

echo "Patch applied successfully."
