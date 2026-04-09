import os
import re
import sys

def main():
    opencode_dir = "/workspace/opencode/packages/opencode"
    
    # Check if already applied
    watcher_path = os.path.join(opencode_dir, "src/file/watcher.ts")
    with open(watcher_path, "r") as f:
        if "export class FileWatcherService" in f.read():
            print("Patch already applied.")
            return 0
    
    # 1. Update AGENTS.md
    agents_path = os.path.join(opencode_dir, "AGENTS.md")
    with open(agents_path, "r") as f:
        agents_content = f.read()
    
    # Add Effect.callback note
    agents_content = agents_content.replace(
        "- `Effect.fn` / `Effect.fnUntraced` accept pipeable operators as extra arguments, so avoid unnecessary `flow` or outer `.pipe()` wrappers.",
        """- `Effect.fn` / `Effect.fnUntraced` accept pipeable operators as extra arguments, so avoid unnecessary `flow` or outer `.pipe()` wrappers.
- **`Effect.callback`** (not `Effect.async`) for callback-based APIs. The classic `Effect.async` was renamed to `Effect.callback` in effect-smol/v4."""
    )
    
    # Add new sections
    agents_content += """
## Instance-scoped Effect services

Services that need per-directory lifecycle (created/destroyed per instance) go through the `Instances` LayerMap:

1. Define a `ServiceMap.Service` with a `static readonly layer` (see `FileWatcherService`, `QuestionService`, `PermissionService`, `ProviderAuthService`).
2. Add it to `InstanceServices` union and `Layer.mergeAll(...)` in `src/effect/instances.ts`.
3. Use `InstanceContext` inside the layer to read `directory` and `project` instead of `Instance.*` globals.
4. Call from legacy code via `runPromiseInstance(MyService.use((s) => s.method()))`.

### Instance.bind — ALS context for native callbacks

`Instance.bind(fn)` captures the current Instance AsyncLocalStorage context and returns a wrapper that restores it synchronously when called.

**Use it** when passing callbacks to native C/C++ addons (`@parcel/watcher`, `node-pty`, native `fs.watch`, etc.) that need to call `Bus.publish`, `Instance.state()`, or anything that reads `Instance.directory`.

**Do not need it** for `setTimeout`, `Promise.then`, `EventEmitter.on`, or Effect fibers — Node.js ALS propagates through those automatically.

```typescript
// Native addon callback — needs Instance.bind
const cb = Instance.bind((err, evts) => {
  Bus.publish(MyEvent, { ... })
})
nativeAddon.subscribe(dir, cb)
```

## Flag → Effect.Config migration

Flags in `src/flag/flag.ts` are being migrated from static `truthy(...)` reads to `Config.boolean(...).pipe(Config.withDefault(false))` as their consumers get effectified.

- Effectful flags return `Config<boolean>` and are read with `yield*` inside `Effect.gen`.
- The default `ConfigProvider` reads from `process.env`, so env vars keep working.
- Tests can override via `ConfigProvider.layer(ConfigProvider.fromUnknown({ ... }))`.
- Keep all flags in `flag.ts` as the single registry — just change the implementation from `truthy()` to `Config.boolean()` when the consumer moves to Effect.
"""
    
    with open(agents_path, "w") as f:
        f.write(agents_content)
    print("Updated AGENTS.md")
    
    # 2. Update src/effect/instances.ts
    instances_path = os.path.join(opencode_dir, "src/effect/instances.ts")
    with open(instances_path, "r") as f:
        instances_content = f.read()
    
    instances_content = instances_content.replace(
        'import { PermissionService } from "@/permission/service"',
        'import { PermissionService } from "@/permission/service"\nimport { FileWatcherService } from "@/file/watcher"'
    )
    instances_content = instances_content.replace(
        "export type InstanceServices = QuestionService | PermissionService | ProviderAuthService",
        "export type InstanceServices = QuestionService | PermissionService | ProviderAuthService | FileWatcherService"
    )
    instances_content = instances_content.replace(
        "Layer.fresh(ProviderAuthService.layer),",
        "Layer.fresh(ProviderAuthService.layer),\n    Layer.fresh(FileWatcherService.layer),"
    )
    
    with open(instances_path, "w") as f:
        f.write(instances_content)
    print("Updated instances.ts")
    
    # 3. Rewrite src/file/watcher.ts
    watcher_content = '''import { BusEvent } from "@/bus/bus-event"
import { Bus } from "@/bus"
import { InstanceContext } from "@/effect/instances"
import { Instance } from "@/project/instance"
import z from "zod"
import { Log } from "../util/log"
import { FileIgnore } from "./ignore"
import { Config } from "../config/config"
import path from "path"
// @ts-ignore
import { createWrapper } from "@parcel/watcher/wrapper"
import { lazy } from "@/util/lazy"
import type ParcelWatcher from "@parcel/watcher"
import { readdir } from "fs/promises"
import { git } from "@/util/git"
import { Protected } from "./protected"
import { Flag } from "@/flag/flag"
import { Cause, Effect, Layer, ServiceMap } from "effect"

const SUBSCRIBE_TIMEOUT_MS = 10_000

declare const OPENCODE_LIBC: string | undefined

const log = Log.create({ service: "file.watcher" })

const event = {
  Updated: BusEvent.define(
    "file.watcher.updated",
    z.object({
      file: z.string(),
      event: z.union([z.literal("add"), z.literal("change"), z.literal("unlink")]),
    }),
  ),
}

const watcher = lazy((): typeof import("@parcel/watcher") | undefined => {
  try {
    const binding = require(
      `@parcel/watcher-${process.platform}-${process.arch}${process.platform === "linux" ? `-${OPENCODE_LIBC || "glibc"}` : ""}`,
    )
    return createWrapper(binding) as typeof import("@parcel/watcher")
  } catch (error) {
    log.error("failed to load watcher binding", { error })
    return
  }
})

function getBackend() {
  if (process.platform === "win32") return "windows"
  if (process.platform === "darwin") return "fs-events"
  if (process.platform === "linux") return "inotify"
}

export namespace FileWatcher {
  export const Event = event
  /** Whether the native @parcel/watcher binding is available on this platform. */
  export const hasNativeBinding = () => !!watcher()
}

const init = Effect.fn("FileWatcherService.init")(function* () {})

export namespace FileWatcherService {
  export interface Service {
    readonly init: () => Effect.Effect<void>
  }
}

export class FileWatcherService extends ServiceMap.Service<FileWatcherService, FileWatcherService.Service>()(
  "@opencode/FileWatcher",
) {
  static readonly layer = Layer.effect(
    FileWatcherService,
    Effect.gen(function* () {
      const instance = yield* InstanceContext
      if (yield* Flag.OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER) return FileWatcherService.of({ init })

      log.info("init", { directory: instance.directory })

      const backend = getBackend()
      if (!backend) {
        log.error("watcher backend not supported", { directory: instance.directory, platform: process.platform })
        return FileWatcherService.of({ init })
      }

      const w = watcher()
      if (!w) return FileWatcherService.of({ init })

      log.info("watcher backend", { directory: instance.directory, platform: process.platform, backend })

      const subs: ParcelWatcher.AsyncSubscription[] = []
      yield* Effect.addFinalizer(() => Effect.promise(() => Promise.allSettled(subs.map((sub) => sub.unsubscribe()))))

      const cb: ParcelWatcher.SubscribeCallback = Instance.bind((err, evts) => {
        if (err) return
        for (const evt of evts) {
          if (evt.type === "create") Bus.publish(event.Updated, { file: evt.path, event: "add" })
          if (evt.type === "update") Bus.publish(event.Updated, { file: evt.path, event: "change" })
          if (evt.type === "delete") Bus.publish(event.Updated, { file: evt.path, event: "unlink" })
        }
      })

      const subscribe = (dir: string, ignore: string[]) => {
        const pending = w.subscribe(dir, cb, { ignore, backend })
        return Effect.gen(function* () {
          const sub = yield* Effect.promise(() => pending)
          subs.push(sub)
        }).pipe(
          Effect.timeout(SUBSCRIBE_TIMEOUT_MS),
          Effect.catchCause((cause) => {
            log.error("failed to subscribe", { dir, cause: Cause.pretty(cause) })
            pending.then((s) => s.unsubscribe()).catch(() => {})
            return Effect.void
          }),
        )
      }

      const cfg = yield* Effect.promise(() => Config.get())
      const cfgIgnores = cfg.watcher?.ignore ?? []

      if (yield* Flag.OPENCODE_EXPERIMENTAL_FILEWATCHER) {
        yield* subscribe(instance.directory, [...FileIgnore.PATTERNS, ...cfgIgnores, ...Protected.paths()])
      }

      if (instance.project.vcs === "git") {
        const result = yield* Effect.promise(() =>
          git(["rev-parse", "--git-dir"], {
            cwd: instance.project.worktree,
          }),
        )
        const vcsDir = result.exitCode === 0 ? path.resolve(instance.project.worktree, result.text().trim()) : undefined
        if (vcsDir and not cfgIgnores.includes(".git") and not cfgIgnores.includes(vcsDir)):
          const ignore = (yield* Effect.promise(() => readdir(vcsDir).catch(() => []))).filter(
            (entry) => entry !== "HEAD",
          )
          yield* subscribe(vcsDir, ignore)
      }

      return FileWatcherService.of({ init })
    }).pipe(
      Effect.catchCause((cause) => {
        log.error("failed to init watcher service", { cause: Cause.pretty(cause) })
        return Effect.succeed(FileWatcherService.of({ init }))
      }),
    ),
  )
}
'''
    
    with open(watcher_path, "w") as f:
        f.write(watcher_content)
    print("Updated watcher.ts")
    
    # 4. Update src/flag/flag.ts
    flag_path = os.path.join(opencode_dir, "src/flag/flag.ts")
    with open(flag_path, "r") as f:
        flag_content = f.read()
    
    if "import { Config } from \"effect\"" not in flag_content:
        flag_content = "import { Config } from \"effect\"\n\n" + flag_content
    
    flag_content = flag_content.replace(
        'export const OPENCODE_EXPERIMENTAL_FILEWATCHER = truthy("OPENCODE_EXPERIMENTAL_FILEWATCHER")',
        'export const OPENCODE_EXPERIMENTAL_FILEWATCHER = Config.boolean("OPENCODE_EXPERIMENTAL_FILEWATCHER").pipe(\n    Config.withDefault(false),\n  )'
    )
    
    flag_content = flag_content.replace(
        'export const OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER = truthy("OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER")',
        'export const OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER = Config.boolean(\n    "OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER",\n  ).pipe(Config.withDefault(false))'
    )
    
    with open(flag_path, "w") as f:
        f.write(flag_content)
    print("Updated flag.ts")
    
    # 5. Update src/project/bootstrap.ts
    bootstrap_path = os.path.join(opencode_dir, "src/project/bootstrap.ts")
    with open(bootstrap_path, "r") as f:
        bootstrap_content = f.read()
    
    bootstrap_content = bootstrap_content.replace(
        'import { FileWatcher } from "../file/watcher"',
        'import { FileWatcherService } from "../file/watcher"'
    )
    
    if 'import { runPromiseInstance } from "@/effect/runtime"' not in bootstrap_content:
        bootstrap_content = bootstrap_content.replace(
            'import { Bus } from "../bus"',
            'import { Bus } from "../bus"\nimport { runPromiseInstance } from "@/effect/runtime"'
        )
    
    bootstrap_content = bootstrap_content.replace(
        "FileWatcher.init()",
        "await runPromiseInstance(FileWatcherService.use((service) => service.init()))"
    )
    
    with open(bootstrap_path, "w") as f:
        f.write(bootstrap_content)
    print("Updated bootstrap.ts")
    
    # 6. Update src/project/instance.ts - add bind method
    instance_path = os.path.join(opencode_dir, "src/project/instance.ts")
    with open(instance_path, "r") as f:
        instance_content = f.read()
    
    bind_method = """  /**
   * Captures the current instance ALS context and returns a wrapper that
   * restores it when called. Use this for callbacks that fire outside the
   * instance async context (native addons, event emitters, timers, etc.).
   */
  bind<F extends (...args: any[]) => any>(fn: F): F {
    const ctx = context.use()
    return ((...args: any[]) => context.provide(ctx, () => fn(...args))) as F
  },
"""
    
    instance_content = instance_content.replace(
        "  state<S>(init: () => S,",
        bind_method + "  state<S>(init: () => S,"
    )
    
    with open(instance_path, "w") as f:
        f.write(instance_content)
    print("Updated instance.ts")
    
    print("\nPatch applied successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
