Fix the filesystem cache metadata loading performance issue on ClickHouse server startup.

## Problem Description

During ClickHouse server startup, the filesystem cache metadata loading is slow because lock acquisition happens repeatedly for each segment file in the cache directory. When loading a cache with many segments, acquiring and releasing locks per-segment creates a contention bottleneck. Additionally, the parameter naming for the initial-load flag is inconsistent across the cache priority interface and its implementations, and segment-level load failures are logged individually rather than being grouped into a summary.

## Requirements

### 1. Parameter Naming

The parameter that controls initial-load behavior must be uniformly named `is_initial_load` across all cache priority classes. Any existing names for this parameter (such as alternative names found in the SLRU implementation) must be replaced.

### 2. Segmented Batch Loading

The metadata loading function must process segments in three distinct phases, each marked by a descriptive comment:

- **Phase 1: scan and parse all segment files** — Scan segment files without holding any locks. Collect the necessary metadata into a temporary structure named `SegmentToLoad` with fields: `UInt64 offset`, `UInt64 size`, `FileSegmentKind kind`, a file path, and an `IFileCachePriority::IteratorPtr cache_it` (to be populated in a later phase). Use a `std::vector<SegmentToLoad> segments` to accumulate entries, adding each one via `segments.push_back`.

- **Phase 2: add all segments for the key under a single write lock** — Acquire the cache write lock once and add all collected segments to the cache priority in a single critical section. The `offset` and `size` variables must be declared inside the per-segment iteration loop, not at function scope where they would persist across iterations.

- **Phase 3: construct FileSegment objects and emplace** — Create FileSegment objects from the collected metadata and insert them into the key's segment map. This phase does not require locks because a single key is loaded by a single thread.

### 3. Failure Tracking

When segments cannot be accommodated due to cache capacity changes (e.g., max size became smaller than before), increment a counter named `failed_to_fit` for each segment that does not fit. After processing all segments for a key, emit a single warning log with the total `failed_to_fit` count instead of logging each failure individually.

### 4. Cache State Verification

After metadata loading completes for all keys, verify the cache priority queue consistency by calling `main_priority->check(cache_state_guard.lock())`.

### 5. Code Style

All changes must follow ClickHouse C++ style guidelines, including:
- Allman brace style (opening braces on new lines)
- No tab characters for indentation
- No trailing whitespace on any line
- Proper include ordering (corresponding header first, then project headers, then standard library headers)
- Every header file must begin with `#pragma once` as its first line

## Success Criteria

- Cache segment loading must batch operations under a single lock acquisition instead of locking per-segment
- The initial-load parameter is consistently named `is_initial_load`
- Loading failures are counted and reported as a single summary per key rather than individual warnings
- Cache consistency is verified after metadata loading
- The code compiles without syntax errors and passes all existing tests
