# build: make cc/no-PCH cxx implicit-depend on dep outputs

## Problem

After a local WebKit rebuild, the second `build:release:local` run triggers a spurious full relink. C files (compiled via the `cc` rule) and C++ files without precompiled headers (no-PCH `cxx`) only have **order-only** dependencies on dep library outputs (`depOutputs` like `libJavaScriptCore.a`). This means their compile edges don't re-run when a dep is rebuilt, even though the dep's sub-build may have rewritten forwarding headers as an undeclared side effect. The result: compile edges lag one build behind, and the next build sees stale objects and relinks everything.

## Expected Behavior

`depOutputs` (the `lib*.a` files from dependency builds) should be **implicit** inputs for `cc` and no-PCH `cxx` edges, not order-only. This way, when a dep library is rebuilt (and its forwarding headers potentially changed), all affected compile edges re-run immediately instead of lagging one build behind. Codegen headers should remain order-only since they are declared Ninja outputs with `restat` and depfile tracking is exact for them.

The `scripts/build/CLAUDE.md` documentation must also be updated to reflect this change in dependency strategy.

## Files to Look At

- `scripts/build/bun.ts` — `emitBun()` assembles the build graph; the `depOrderOnly` variable and its usage in `cc()`/`cxx()` calls need to change
- `scripts/build/compile.ts` — `CompileOpts` interface docs describe when to use `implicitInputs` vs `orderOnlyInputs`
- `scripts/build/CLAUDE.md` — Ninja primer and Gotchas sections document the dependency strategy
