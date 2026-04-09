# Bloom Filter Improvements and Bug Fixes

There are several bugs in the bloom filter implementation that need to be fixed:

## 1. Shared State Bug Between Cache and Writer

The bloom filter in the cache shares its underlying `Arc<BloomFilterInner>` with the writer. This means when the writer mutates the bloom filter (inserts, deletes), those mutations also affect the cached version, leading to incorrect state being persisted.

**Fix needed**: Implement a `deep_clone()` method on `BloomFilter` that creates an independent copy with its own `Arc<BloomFilterInner>`, then use this in `BloomFilterManager::commit()` when inserting into the cache.

## 2. Error Propagation Bug

`ApplyMaterializedLogError::BloomFilterSerializationError` is a unit variant that discards the underlying error information. When serialization fails, the actual error cause is lost.

**Fix needed**: Change `BloomFilterSerializationError` to wrap `BloomFilterError` so error details are preserved.

## 3. Cache Key Mismatch Bug

In `BloomFilterManager`, the `commit()` method uses `bf.id().to_string()` as the cache key, but `get()` uses the last component of the full storage path. This mismatch means cached bloom filters may not be found on lookup.

**Fix needed**: Add a helper method to extract the cache key from the path consistently, and use it in both `commit()` and `get()`.

## 4. Bloom Filter Flush Error Handling

In `RecordSegmentFlusher::flush()`, bloom filter save failures are logged as warnings but don't fail the compaction. This can lead to incomplete segment state being considered successful.

**Fix needed**: Make bloom filter flush errors propagate and fail the compaction.

## 5. Read Path Optimization

Currently, the bloom filter is only used when `use_bloom_filter` is true in the query plan. However, even when not using the bloom filter for queries, we could benefit from the cached version to avoid storage fetches.

**Fix needed**: Split `ensure_bloom_filter()` into two methods:
- `fetch_bloom_filter()` - for when we need to load from storage
- `try_load_bloom_filter_from_cache()` - for when we just want to use the cached version if available

## Files to Modify

- `rust/segment/src/bloom_filter.rs` - Main bloom filter implementation
- `rust/segment/src/blockfile_record.rs` - Record segment writer/reader that uses the bloom filter

## Hints

- The `deep_clone()` method needs to create new `AtomicU64` instances for `live_count` and `stale_count`, not share them
- The `cache_key_from_path()` method should extract just the UUID portion from a full storage path
- The error type change is in `ApplyMaterializedLogError` enum
- Look at how the bloom filter is used in `get_offset_id_for_user_id()` and `get_all_user_ids()` for the read path optimization
