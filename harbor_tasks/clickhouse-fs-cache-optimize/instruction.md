# Optimize Filesystem Cache Loading on Server Startup

## Problem

The filesystem cache loading process during ClickHouse server startup has inefficient lock contention. The current implementation in `FileCache::loadMetadataForKeys` acquires and releases locks for every individual segment file, which significantly slows down startup when many cached files exist.

## Current Behavior

In `src/Interpreters/Cache/FileCache.cpp`, the `loadMetadataForKeys` function currently:
1. Iterates over each key directory
2. For each segment file within the key, acquires a write lock
3. Checks if the segment fits in the cache while holding the lock
4. Constructs `FileSegment` objects while still holding locks
5. Logs warnings for each file that doesn't fit individually

This per-segment locking pattern creates contention and slows down the loading process.

## Required Changes

You need to restructure `loadMetadataForKeys` in `FileCache.cpp` to use a three-phase loading approach that minimizes lock contention:

### Phase 1: Scan and Parse (No Lock)
- Scan all segment files for a given key
- Parse offset, size, and kind from each filename
- Store the parsed information in a temporary structure

### Phase 2: Add Segments (Single Lock Acquisition)
- Acquire the write lock once for all segments of this key
- Call `canFit()` and `add()` for each segment while holding the lock
- Store the returned iterator pointers

### Phase 3: Construct FileSegments (No Lock)
- Construct `FileSegment` objects using the stored information
- Emplace them into the key metadata
- No locks should be held during this phase

## Additional Changes

1. **Parameter Renaming**: Rename the `best_effort` parameter to `is_initial_load` in:
   - `IFileCachePriority.h`
   - `LRUFileCachePriority.h`
   - `SLRUFileCachePriority.h` and `.cpp`
   - `SplitFileCachePriority.h` and `.cpp`

2. **Consistency Check**: Add a call to `main_priority->check(cache_state_guard.lock())` at the end of `loadMetadataImpl` after all metadata is loaded.

3. **Batch Logging**: Change from logging each file that doesn't fit individually to accumulating a count and logging once per key with the total count.

## Key Files

- `src/Interpreters/Cache/FileCache.cpp` - Main file containing `loadMetadataForKeys`
- `src/Interpreters/Cache/IFileCachePriority.h` - Interface with `add()` and `canFit()` methods
- `src/Interpreters/Cache/LRUFileCachePriority.h` - LRU implementation
- `src/Interpreters/Cache/SLRUFileCachePriority.h/.cpp` - SLRU implementation
- `src/Interpreters/Cache/SplitFileCachePriority.h/.cpp` - Split priority implementation

## Notes

- The `SegmentToLoad` struct should have fields: `offset`, `size`, `kind`, `path`, and `cache_it`
- In SLRU cache priority, the `is_initial_load` flag should allow segments to fit in either the probationary or protected queue during initial load
- Use `std::vector<SegmentToLoad>` to collect segments before processing them in batches
- The lock scope should be minimized to only cover the actual cache priority operations

Follow the Allman brace style (opening brace on a new line) as required by ClickHouse coding conventions.
