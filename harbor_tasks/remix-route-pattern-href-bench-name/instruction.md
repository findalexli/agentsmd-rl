# Make `href` benchmark identifiable when comparing branches

You are working in `/workspace/remix`, a checkout of the `remix-run/remix`
monorepo. The package `@remix-run/route-pattern` provides URL pattern
matching, and its benchmarks live under `packages/route-pattern/bench/`.

## Background

The `href` benchmark is intended to be used with vitest's `--compare`
workflow as documented in `packages/route-pattern/bench/README.md`:

```
git checkout main
pnpm bench comparison.bench.ts --outputJson=main.json

git checkout feature-branch
pnpm bench comparison.bench.ts --compare=main.json
```

When you compare two runs, vitest groups results by the name passed to each
`bench(name, …)` call. Today the `href` benchmark file passes the same
hard-coded name (the literal string `"bench"`) for every `bench(…)` call,
so a JSON snapshot taken on `main` and a run on a feature branch are
indistinguishable in the comparison output — they both show up under
`"bench"`.

## What to fix

Edit the relevant file under `packages/route-pattern/bench/` so that the
name passed to every `bench(…)` call reflects the **current git state** of
the working tree, in the form:

```
<branch> (<short-commit>)
```

where:

- `<branch>` is the output of `git rev-parse --abbrev-ref HEAD` (trimmed)
- `<short-commit>` is the output of `git rev-parse --short HEAD` (trimmed,
  the abbreviated 7+ hex-character SHA)

Example: if the current branch is `main` and the short commit is
`a2245ea`, every bench should be registered with the name
`"main (a2245ea)"`.

### Requirements

- The bench name must be derived **at module-load time** from the actual
  git state — running the file in a different commit or different branch
  must produce a different name. Do not hard-code a string.
- Use Node's built-in child-process facility to invoke `git`. The repo's
  code-style guide requires that Node built-in modules be imported with
  the `node:` prefix (e.g. `import { execSync } from 'node:child_process'`).
- If the `git` invocations throw (e.g. the current working directory is
  not inside a git repository), fall back to the literal name
  `"bench"` so the file remains usable in non-git contexts.
- Do not change the existing `describe(…)` blocks or any of the
  `pattern.href(…)` calls — the only thing that needs to change is the
  name passed to `bench(…)`.
- Keep all imports of `@remix-run/route-pattern` and `vitest` working as
  they do today.

## Code Style Requirements

This repo enforces its style via Prettier and ESLint. Before finishing,
make sure your edit follows the conventions documented in `AGENTS.md`,
including:

- **Imports**: include `.ts` extensions on local imports; use the `node:`
  prefix for Node built-ins.
- **Variables**: prefer `let` for locals; use `const` only at module
  scope; never use `var`.
- **Functions**: prefer regular function declarations over arrow
  functions for top-level helpers.
- **Formatting**: Prettier defaults for this repo are `printWidth: 100`,
  no semicolons, single quotes, 2-space indentation.
- **Comments**: only add non-JSDoc comments when the code is doing
  something surprising or non-obvious. A short JSDoc on a new helper
  describing what it returns is fine.
