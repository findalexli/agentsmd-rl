# Turbopack: fs.readdir calls not traced by node-file-trace

## Problem

Turbopack's node-file-trace (NFT) infrastructure does not recognize `fs.readdir()` or `fs.readdirSync()` calls as well-known fs module functions. When code uses `fs.readdir` to enumerate directory contents, the NFT analyzer ignores these calls entirely, meaning any files discovered through directory listing are missing from the traced asset graph. This causes incomplete file tracing for deployments and standalone builds that rely on runtime directory scanning.

## Expected Behavior

`fs.readdir()` and `fs.readdirSync()` should be recognized as well-known fs module members, similar to `fs.readFileSync`, `fs.readFile`, etc. When Turbopack encounters these calls during asset tracing, it should analyze the path argument, create a `DirAssetReference` for directory patterns, warn about dynamic (non-statically-analyzable) patterns, and include the referenced directories in the traced output.

## Files to Look At

- `turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs` — maps fs module property names to well-known function kinds via the `fs_module_member` function
- `turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs` — defines the `WellKnownFunctionKind` enum and descriptive names for each variant
- `turbopack/crates/turbopack-ecmascript/src/references/mod.rs` — contains match arms that handle each well-known function kind during asset tracing, creating appropriate references (e.g., `FileAssetReference`, `DirAssetReference`)
