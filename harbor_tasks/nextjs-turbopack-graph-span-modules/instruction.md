# Missing module count in Turbopack module graph tracing spans

## Problem

The Turbopack module graph construction in Next.js emits tracing spans for performance monitoring, but these spans don't include any information about the number of modules in the graph. This makes it impossible to correlate span duration with graph size or detect regressions where the graph grows unexpectedly.

There are two key places where module graphs are built:

1. **Per-endpoint graph** (`crates/next-api/src/app.rs`): The `AppProject` builds multiple `SingleModuleGraph`s for each endpoint (RSC entry, SSR entries, additional entries). There is currently an `info_span!("module graph for endpoint")` at the end that instruments the async block, but it carries no structured fields about the graph size.

2. **Whole-app graph** (`crates/next-api/src/project.rs`): The `whole_app_module_graph_operation` function builds a base graph and an additional-entries graph. This function has no tracing span at all — graph construction time is invisible in traces.

Additionally, `SingleModuleGraph` (in `turbopack/crates/turbopack-core/src/module_graph/mod.rs`) already tracks `number_of_modules` internally but doesn't expose it as a `turbo_tasks` function, so it can't be easily queried from async contexts.

## Expected behavior

- Both module graph construction sites should emit tracing spans that include a `modules` field with the total number of modules across all contributing graphs.
- `SingleModuleGraph` should expose its module count as a queryable `turbo_tasks` function.
- The span fields should use the deferred-field pattern (declare with `Empty`, record after computation) already used elsewhere in the codebase (e.g., `ProjectContainer::initialize`).
- Module counts should be summed across all `SingleModuleGraph` instances that contribute to the endpoint or app graph.
- The count should only be computed when the span is not disabled, to avoid unnecessary overhead.

## Files to investigate

- `crates/next-api/src/app.rs` — per-endpoint module graph span
- `crates/next-api/src/project.rs` — whole-app module graph (missing span entirely)
- `turbopack/crates/turbopack-core/src/module_graph/mod.rs` — `SingleModuleGraph` struct
