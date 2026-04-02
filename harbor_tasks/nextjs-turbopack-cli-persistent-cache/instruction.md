# turbopack-cli: Add Persistent Caching Support

## Problem

The standalone `turbopack-cli` binary (used independently of Next.js) currently has no way to opt into the filesystem-backed persistent cache. The `next-napi-bindings` integration already supports persistent caching, but the standalone CLI always starts cold — every incremental run recomputes the full task graph from scratch.

Users running repeated builds with the standalone turbopack binary experience unnecessary slowness because there is no mechanism to persist and reuse computed task results across runs.

## What Needs to Change

The `turbopack-cli` crate at `turbopack/crates/turbopack-cli/` needs to support persistent caching. Specifically:

1. **CLI flags**: Two new flags should be added to the arguments shared by both `dev` and `build` subcommands — one to enable persistent caching, and another to override the default cache directory location.

2. **Git version embedding**: A Cargo build script is needed to embed git version information at compile time. The persistent cache uses the git version as a cache key to ensure safety — when the binary version changes, the cache is invalidated. Look at how `next-napi-bindings` embeds version info for reference.

3. **Backend storage wiring**: Both the dev server and build modules currently hardcode a no-op backing storage for the task backend. They need to be updated to support either real persistent storage or no-op storage based on the new CLI flag. The type system should be updated to accommodate both storage implementations without dynamic dispatch.

4. **Storage mode selection**: When persistent caching is enabled, the initialization code should select the appropriate storage mode based on context — CI and short-lived sessions should defer writes until shutdown, while interactive dev sessions should write continuously. A read-only mode should also be supported via an environment variable.

5. **Cache invalidation warning**: When the cache is invalidated on startup (e.g., due to version mismatch), print a warning to stderr.

6. **Benchmarks and dependencies**: The benchmark code instantiates argument structs directly and needs to be updated for the new fields. Appropriate crate dependencies need to be added to `Cargo.toml`.

## Key Files

- `turbopack/crates/turbopack-cli/src/arguments.rs` — CLI argument definitions
- `turbopack/crates/turbopack-cli/src/dev/mod.rs` — Dev server startup
- `turbopack/crates/turbopack-cli/src/build/mod.rs` — Build command startup
- `turbopack/crates/turbopack-cli/Cargo.toml` — Crate dependencies
- `turbopack/crates/turbopack-cli/benches/small_apps.rs` — Benchmarks

## Hints

- Look at `next-napi-bindings` for reference on the persistent storage initialization pattern.
- The `either` crate can unify two different backing storage implementations behind a single type alias.
- The build script needs to handle CI environments specially (suppress the dirty suffix in version strings).
- Build sessions are always short-lived. Dev sessions are short-lived only in CI.
