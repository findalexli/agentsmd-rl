Fix the fs cache loading performance issue on server startup in ClickHouse.

## Problem

During server startup, the filesystem cache metadata loading in `src/Interpreters/Cache/FileCache.cpp` is slow due to suboptimal lock handling. The current implementation acquires and releases locks repeatedly while processing each segment file, causing unnecessary contention. Each segment is processed individually with separate lock/unlock operations, which becomes a bottleneck when loading large caches.

## Required Changes

### 1. Parameter Naming Consistency

The parameter indicating initial load behavior is inconsistently named across cache priority implementations (`best_effort`, `is_startup`). This should be renamed consistently to `is_initial_load` across all cache priority interface and implementation files:
- `src/Interpreters/Cache/IFileCachePriority.h`
- `src/Interpreters/Cache/LRUFileCachePriority.h`
- `src/Interpreters/Cache/SLRUFileCachePriority.h`
- `src/Interpreters/Cache/SLRUFileCachePriority.cpp`
- `src/Interpreters/Cache/SplitFileCachePriority.h`
- `src/Interpreters/Cache/SplitFileCachePriority.cpp`

### 2. Three-Phase Loading Architecture

Restructure the `loadMetadataForKeys` function to organize loading into distinct logical phases that separate data gathering from data installation:

**Phase 1:** Scan and parse all segment files for a key without holding any locks. This should collect all necessary metadata (offset, size, file path, segment kind) into a temporary structure.

**Phase 2:** Add all collected segments under a single write lock acquisition. This is where the cache priority tracking is updated - do this for all segments at once rather than one at a time.

**Phase 3:** Construct the FileSegment objects and emplace them into the cache. This can be done without holding locks since a single key is loaded by a single thread.

The three phases should be clearly marked with comments in the code to document the architectural approach.

### 3. Tracking Loading Failures

When segments cannot be accommodated in the cache (e.g., due to capacity changes), these failures should be tracked and logged. Instead of logging each failure individually, count them and emit a single summary warning per key with the count of files that did not fit.

### 4. Cache Verification

After metadata loading completes, the cache state should be verified to ensure consistency between the priority queue and the actual cached segments.

### 5. Code Style

All changes should follow ClickHouse C++ style guidelines, including Allman brace style (opening braces on new lines) and proper naming conventions.

## Success Criteria

- Cache loading should use batching rather than per-segment lock acquisition
- The parameter is consistently named `is_initial_load` across all cache priority files
- Loading failures are tracked per-key and logged as a count rather than individually
- Code compiles without syntax errors
- Code follows ClickHouse style guidelines
