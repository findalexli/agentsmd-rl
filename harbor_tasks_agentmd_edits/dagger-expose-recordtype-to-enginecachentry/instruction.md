# Expose RecordType on EngineCacheEntry

## Problem

The `EngineCacheEntry` type in the Dagger engine exposes metadata about local cache entries (description, size, creation time, usage time, whether actively used), but it does not expose the **record type** of each cache entry. The buildkit cache backend tracks record types (e.g. `regular`, `internal`, `frontend`, `source.local`, `source.git.checkout`, `exec.cachemount`) which are useful for understanding what kind of cached content an entry represents.

Users and tooling that inspect the local cache have no way to distinguish between different types of cache records through the API.

## Expected Behavior

The `EngineCacheEntry` type should expose the record type as a new field, available through the GraphQL API and all SDK bindings. The underlying value comes from the buildkit cache record's `RecordType` field and should be populated when building cache entry results in the engine server.

The GraphQL schema in `docs/docs-graphql/schema.graphqls` should also be updated to include this new field.

## CONTRIBUTING.md is Outdated

While working in this area, note that `CONTRIBUTING.md` contains several outdated CLI commands that no longer match the current Dagger toolchain. The commands for manual testing, integration testing, linting, running the docs server, and generating API docs/bindings all reference old CLI syntax. These should be updated to reflect the current CLI interface.

## Files to Look At

- `core/engine.go` — the `EngineCacheEntry` struct definition
- `engine/server/gc.go` — where cache entries are constructed from buildkit records
- `docs/docs-graphql/schema.graphqls` — the GraphQL schema for the `EngineCacheEntry` type
- `CONTRIBUTING.md` — developer contribution guide with CLI commands
