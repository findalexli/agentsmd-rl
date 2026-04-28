# Allow TypeScript 6 with the Pulumi Node.js SDK

## Symptom

A user trying to consume `@pulumi/pulumi` from a project that uses
**TypeScript 6** sees one of two things:

1. `npm`/`yarn` emits a peer-dependency warning because the SDK currently
   declares the typescript peer dependency as `>= 3.8.3 < 6` — version `6.0.0`
   does not satisfy that range. Many users treat peer warnings as adoption
   blockers, especially in CI pipelines that fail on `npm` warnings.
2. The SDK's own side-by-side compatibility test harness (under
   `sdk/nodejs/tests/sxs_ts_test/`) cannot test against TypeScript 6 at all:
   `make sxs_tests` (which is driven by the `TSC_SUPPORTED_VERSIONS` variable
   in `sdk/nodejs/Makefile`) only runs against `~3.8.3 ^3 ^4`, so we have no
   guarantee that the SDK keeps typechecking under TS 6.

The expected behaviour is:

- The published `@pulumi/pulumi` package's `peerDependencies.typescript`
  range accepts every TypeScript major from `3.8.3` up to (but not including)
  TypeScript 7.
- `make sxs_tests` (in `sdk/nodejs/`) runs the side-by-side test against
  TypeScript 6 in addition to the existing versions, and it passes.
- The TypeScript-6 side-by-side test compiles cleanly even though TypeScript
  6 has deprecated `moduleResolution: "node"`. This means the test must use
  `module` and `moduleResolution` settings that are still supported under
  TypeScript 6 — see the [TypeScript 6.0 release
  notes](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)
  for the supported replacements for the deprecated `node` resolver.
- Existing TypeScript versions (`~3.8.3`, `^3`, `^4`) must keep working —
  no regressions on the older versions.
- The `ts-node` peer-dependency range must not be narrowed by your change.

## How the side-by-side test harness works

`sdk/nodejs/Makefile` defines a pattern rule of the form
`sxs_test_%`. The `%` is the TypeScript version (e.g. `^4`) and is also
the **slug appended to the filenames the rule reads from**. The rule runs
inside `sdk/nodejs/tests/sxs_ts_test/` and:

1. Copies a per-version `package<version>.json` to `package.json` so that
   `yarn install` resolves the correct TypeScript version. The existing
   per-version files are `package~3.8.3.json`, `package^3.json`, and
   `package^4.json`.
2. Runs `yarn install`, then `yarn run tsc` to typecheck `index.ts`.

To extend coverage to TypeScript 6, follow the existing convention:

- Add a new TypeScript-6 entry to `TSC_SUPPORTED_VERSIONS` using the same
  yarn-style version slug shape as the existing entries (so `^6` matches
  `^3` / `^4`).
- Add a matching per-version package file following the existing
  `package<version>.json` naming convention (which you can infer from the
  files already present for `~3.8.3`, `^3`, and `^4`), mirroring the
  structure of the existing `package^4.json` but pinning typescript to
  the new major.

Because TS 6 deprecates the classic `"node"` module resolver, the build
needs to use a tsconfig whose `module`/`moduleResolution` settings are
still supported under TS 6. The Makefile rule should pick up an optional
per-version tsconfig override automatically when one is present, falling
back to the default `tsconfig.json` otherwise (so the older versions stay
unaffected). The natural name for that override follows the same per-version
filename convention (using `tsconfig` as the prefix instead of
`package`, so the agent can derive the expected filename).

For CommonJS projects (no `"type": "module"` in `package.json`, as is the
case here), the appropriate replacement for the deprecated `"node"` module
resolution is documented in the TypeScript 6.0 release notes linked above.

## Repo conventions

This repo's `CLAUDE.md` / `AGENTS.md` state that **most PRs require a
changelog entry**. Pending entries live under `changelog/pending/` as YAML
files with a `changes:` list. For an SDK Node.js fix, the entry should
have `type: fix` and `scope: sdk/nodejs`.

Files you change must continue to lint cleanly under the SDK's tooling
(see Code Style Requirements below).

## Code Style Requirements

- The Node.js SDK is linted with **biome**. Anything biome considers
  invalid in `sdk/nodejs/biome.json`, `sdk/nodejs/package.json`, or any
  newly added `tsconfig*.json` will fail CI. If you add a new
  `tsconfig*.json` that uses comments (which biome flags as invalid in
  `.json` files), make sure biome is configured to ignore it.
- The Node.js SDK Makefile is the source of truth for which TypeScript
  versions are tested. Do not skip linting (`mise exec -- make lint`).

## Out of scope

- Do not change the existing peer-dependency entry for `ts-node`.
- Do not refactor unrelated parts of the SDK or the test harness — make
  the smallest set of changes that delivers the behaviour above.
- Do not edit generated proto files or the contents of
  `sdk/nodejs/bin/`.
