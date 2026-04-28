# Fix Benchmark Files in @remix-run/route-pattern

## Problem

The vitest benchmark files for `@remix-run/route-pattern` have issues that cause
benchmarks to produce unreliable results and violate the repository's AGENTS.md
conventions.

When vitest runs benchmarks, it calls the callback function passed to `bench()`
many times during both the calibration and measurement phases. The current
benchmark code creates a `matchers` variable at module scope containing a single
`ArrayMatcher` instance, then uses a `for...of` loop inside `describe()` blocks
to iterate over this variable and register benchmark cases.

This design causes each `bench()` invocation to re-use the same matcher instance,
accumulating duplicate route entries across calibration runs. The result is
inaccurate benchmarks and potential hangs with large route sets.

Additionally, only `ArrayMatcher` is benchmarked — `TrieMatcher` is available in
the same `@remix-run/route-pattern` package but is not included.

The AGENTS.md file at the repository root (lines 34-36) states:

> Do not use `for` loops or conditional statements (`if`, `switch`, etc.) to
> generate test cases within `describe()` blocks.

## Files to Modify

- `packages/route-pattern/bench/simple.bench.ts` — benchmarks ~40 simple routes
- `packages/route-pattern/bench/pathological.bench.ts` — benchmarks ~1,200 generated routes

## Acceptance Criteria

1. Both `ArrayMatcher` and `TrieMatcher` from `@remix-run/route-pattern` must be
   imported and benchmarked in both files.

2. Repeated `bench()` invocations must not accumulate state on a shared matcher
   instance. The setup benchmarks should measure the cost of creating and
   populating a matcher from scratch each run. The match benchmarks should
   measure only match performance — the cost of adding routes to the matcher
   should not be re-measured during each match benchmark run.

3. The `describe()` blocks must comply with the AGENTS.md rule against using
   `for` loops to generate test cases. Each matcher type must be registered
   with an explicit `bench()` call — not generated programmatically from a
   `{ name, matcher }` data structure.

4. All code must pass the repository's Prettier format check.

## Code Style Requirements

This repository enforces strict formatting and code style:

- **Prettier**: printWidth 100, no semicolons, single quotes, spaces (not tabs).
  Run `npx prettier --check <file>` to verify.
- **Variables**: Use `let` for locals, `const` only at module scope; never `var`.
- **Functions**: Use arrow functions only as callbacks. Regular function
  declarations/expressions are the default.
- **TypeScript**: Strict mode, ESNext target, ES2022 modules.

See the full AGENTS.md guide in the repository root for all conventions.
