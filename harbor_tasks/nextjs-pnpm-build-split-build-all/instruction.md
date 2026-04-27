# Split `pnpm build` so it no longer drags in the Rust/Turbopack build

## Repository

You are working in `/workspace/nextjs`, a checkout of the
[`vercel/next.js`](https://github.com/vercel/next.js) monorepo at a
specific base commit. The repo uses pnpm workspaces and Turborepo
(`turbo` 2.8.x). Read `AGENTS.md` (root of the repo) — it documents
how agents should build, test, and lint this workspace; the rules in
that file apply to your work on this task.

## Background

The repo currently has a single top-level command for building everything:

```bash
pnpm build       # turbo run build --remote-cache-timeout 60 --summarize true
```

This drives Turborepo to run the `build` task in every workspace
package. One of those packages, `@next/swc` (a workspace member that
wraps the Rust/Turbopack native binary), defines its own `build` task
that invokes a helper which compiles or fetches the native `.node`
binary. Concretely, today every `pnpm build` includes a `@next/swc`
build step whose command resolves to `node maybe-build-native.mjs`.

That coupling is painful for contributors who already have a
locally-compiled Turbopack binary they want to keep using: there is no
way to run the JS build without the helper also running, possibly
discarding their custom build.

## What you need to deliver

After your change, the workspace must offer **two** distinct top-level
build commands with the following observable behavior:

### `pnpm build` — JS only

`pnpm build` (i.e. `turbo run build` with the existing flags) must
plan a graph in which **no `@next/swc` task runs `node
maybe-build-native.mjs`**. Equivalently: when you run

```bash
turbo run build --dry-run=json
```

and look at the tasks for `package == "@next/swc"`, none of them may
have `command == "node maybe-build-native.mjs"`. (If a `@next/swc#build`
entry still appears in the plan because the global graph references it,
its `command` must be the empty placeholder `<NONEXISTENT>` rather than
a real command.)

The other root scripts (`build`, `clean`, `dev`, etc.) must still
exist and still work the same way — only the meaning of `build` for the
`@next/swc` package changes.

### `pnpm build-all` — JS + Rust

A new top-level pnpm script named exactly `build-all` must exist. When
invoked, it must drive Turborepo to run **both** the regular `build`
graph **and** the native-build graph for `@next/swc`. Concretely:

- The script must invoke `turbo run` with two task names as positional
  arguments (in addition to the same flags the existing `build`
  script passes).
- One of those task names must be `build` (so JS packages still build).
- The other must select a task in `@next/swc` whose command is
  `node maybe-build-native.mjs`. That task must be named
  `build-native-auto` and must live in `@next/swc`. Its turbo task
  definition should preserve the same `inputs`, `env`, and `outputs`
  the previous `@next/swc#build` task had (so caching keeps working
  identically).
- After your change, `turbo run build build-native-auto --dry-run=json`
  must list a task whose `taskId` is `@next/swc#build-native-auto`
  with `command == "node maybe-build-native.mjs"`.

The `@next/swc` package must therefore no longer have a `build` script
at all (otherwise `pnpm build` would still pick it up).

## Update agent / contributor docs

`AGENTS.md` (root of the repo) is the single source of truth for what
build command an agent should run in various situations (after a
branch switch, before CI push, when changes span multiple packages,
etc.). Several places in that file currently tell agents to run
`pnpm build` for full bootstrap-style rebuilds. Those places must now
direct readers to `pnpm build-all` instead — JS-only `pnpm build` is
no longer enough for "full" rebuilds. The "Build Commands" section
also needs to mention the new command alongside the old one. The file
must end up containing the literal string `pnpm build-all`.

(Other AGENTS.md edits are at your discretion; the only hard
requirement is that the documented bootstrap/branch-switch command is
updated and `pnpm build-all` is mentioned.)

## Out of scope

- Do NOT rename, change, or delete any other `@next/swc` script
  (`build-native`, `build-native-release`, `build-wasm`, etc.).
- Do NOT change the `inputs`/`outputs`/`env` of unrelated turbo task
  definitions.
- You do not need to run `pnpm install`, run any actual build, or
  produce any compiled output. The verifier only inspects the turbo
  task graph via `turbo --dry-run` and reads workspace JSON files.

## How to verify locally

`turbo` is installed globally in the environment. From
`/workspace/nextjs`:

```bash
turbo run build --dry-run=json | python3 -c '
import json, sys
d = json.load(sys.stdin)
for t in d["tasks"]:
    if t["package"] == "@next/swc":
        print(t["taskId"], "->", t.get("command"))
'
```

Before your change you will see `@next/swc#build -> node
maybe-build-native.mjs`. After your change, no `@next/swc` task in
that output may have `node maybe-build-native.mjs` as its command. Then:

```bash
turbo run build build-native-auto --dry-run=json
```

must additionally produce a `@next/swc#build-native-auto` task whose
command is `node maybe-build-native.mjs`.
