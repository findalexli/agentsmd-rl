# Fix VectorDB Metadata Race Condition

## Problem

Under concurrent load, the VectorDB collection creation endpoint intermittently throws `DuplicateException` errors during metadata initialization. This is a classic TOCTOU (time-of-check-time-of-use) race condition.

## Symptoms

- When multiple requests simultaneously attempt to create collections in a fresh VectorDB database, some requests fail with duplicate key errors
- The race occurs between checking if metadata storage exists and actually creating it
- One request succeeds in creating the metadata structure while another fails mid-operation
- The failing request encounters an exception indicating that the metadata collection already exists, even though the prior existence check returned false

## Required Behavior

The metadata bootstrap process must be idempotent under concurrent execution. When multiple requests race to initialize the same metadata:

1. One request should successfully create the metadata storage
2. Other concurrent requests should recognize that the metadata is now available and continue normally rather than failing
3. All requests should proceed to create their actual collections successfully

Duplicate errors for actual collection creation must continue to be propagated as errors - only the one-time metadata initialization should handle duplicate scenarios gracefully.

## Context

The VectorDB module follows the standard Appwrite Action pattern with HTTP endpoints under `Http/VectorsDB/Collections/`. Look for the collection creation endpoint implementation.

The issue involves database initialization code that checks for metadata storage existence before attempting creation. The Appwrite database layer uses Utopia Database, which throws specific exception types when duplicate resources are created.

Refer to the module structure and HTTP endpoint conventions documented in the repository's AGENTS.md files.
