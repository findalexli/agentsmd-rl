Fix the fs cache loading performance issue on server startup in ClickHouse.

During server startup, the filesystem cache metadata loading in `src/Interpreters/Cache/FileCache.cpp` is slow due to suboptimal lock handling. The current implementation acquires and releases locks repeatedly while processing each segment file, causing unnecessary contention.

The lock contention can be reduced by batching metadata operations. Restructure the loadMetadataForKeys function to organize loading into distinct logical phases that separate data gathering from data installation, so that lock acquisition happens once per batch rather than per segment.

A helper struct is needed to carry segment metadata during the batched loading process. This struct should include fields for offset, size, kind, and an iterator reference. Segments should be collected into a container before being processed, and loading failures should be tracked with a counter that increments when a segment cannot be accommodated.

The parameter indicating initial load behavior is inconsistently named across cache priority implementations, leading to confusion. The parameter name should be consistent across all cache priority header and source files in `src/Interpreters/Cache/`, including IFileCachePriority.h, LRUFileCachePriority.h, SLRUFileCachePriority.h, SLRUFileCachePriority.cpp, SplitFileCachePriority.h, and SplitFileCachePriority.cpp.

After metadata loading completes, a cache correctness verification should be performed to ensure the loaded state is consistent.

Follow ClickHouse C++ style guidelines (Allman braces, proper naming conventions).
