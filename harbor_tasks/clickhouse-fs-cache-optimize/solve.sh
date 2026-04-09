#!/bin/bash
set -e

cd /workspace/clickhouse

# Apply the gold patch for filesystem cache optimization
cat <<'PATCH' | git apply -
diff --git a/src/Interpreters/Cache/FileCache.cpp b/src/Interpreters/Cache/FileCache.cpp
index d27e71dc1fc3..927475fd90d1 100644
--- a/src/Interpreters/Cache/FileCache.cpp
+++ b/src/Interpreters/Cache/FileCache.cpp
@@ -1801,6 +1801,8 @@ void FileCache::loadMetadataImpl()
     if (first_exception)
         std::rethrow_exception(first_exception);

+    main_priority->check(cache_state_guard.lock());
+
     assertCacheCorrectness();
 }

@@ -1814,8 +1816,6 @@ void FileCache::loadMetadataForKeys(const fs::path & keys_dir, const OriginInfo
         return;
     }

-    UInt64 offset = 0;
-    UInt64 size = 0;
     for (; key_it != fs::directory_iterator(); key_it++)
     {
         const fs::path key_directory = key_it->path();
@@ -1843,25 +1843,39 @@ void FileCache::loadMetadataForKeys(const fs::path & keys_dir, const OriginInfo
             origin_info,
             /* is_initial_load */true);

+        /// Phase 1: scan and parse all segment files for this key (no lock held).
+        struct SegmentToLoad
+        {
+            UInt64 offset;
+            UInt64 size;
+            FileSegmentKind kind;
+            fs::path path;
+            IFileCachePriority::IteratorPtr cache_it; /// filled in phase 2
+        };
+        std::vector<SegmentToLoad> segments;
+
         for (fs::directory_iterator offset_it{key_directory}; offset_it != fs::directory_iterator(); ++offset_it)
         {
             auto offset_with_suffix = offset_it->path().filename().string();
-            auto delim_pos = offset_with_suffix.find('_');
             bool parsed;
-            FileSegmentKind segment_kind = FileSegmentKind::Regular;
+            UInt64 offset = 0;

+            auto delim_pos = offset_with_suffix.find('_');
             if (delim_pos == std::string::npos)
+            {
                 parsed = tryParse<UInt64>(offset, offset_with_suffix);
+            }
             else
             {
                 parsed = tryParse<UInt64>(offset, offset_with_suffix.substr(0, delim_pos));
-
-                if (offset_with_suffix.substr(delim_pos+1) == "persistent")
+
+                if (offset_with_suffix.substr(delim_pos + 1) == "persistent")
                 {
                     /// For compatibility. Persistent files are no longer supported.
                     fs::remove(offset_it->path());
                     continue;
                 }
-                if (offset_with_suffix.substr(delim_pos+1) == "temporary")
+                if (offset_with_suffix.substr(delim_pos + 1) == "temporary")
                 {
                     fs::remove(offset_it->path());
                     continue;
@@ -1871,50 +1885,73 @@ void FileCache::loadMetadataForKeys(const fs::path & keys_dir, const OriginInfo
             if (!parsed)
             {
                 LOG_WARNING(log, "Unexpected file: {}", offset_it->path().string());
-                continue; /// Or just remove? Some unexpected file.
+                continue;
             }

-            size = offset_it->file_size();
+            auto size = offset_it->file_size();
             if (!size)
             {
                 fs::remove(offset_it->path());
                 continue;
             }

-            bool limits_satisfied;
-            IFileCachePriority::IteratorPtr cache_it;
-            size_t size_limit = 0;
+            segments.push_back({offset, size, FileSegmentKind::Regular, offset_it->path(), nullptr});
+        }
+
+        /// Phase 2: add all segments for the key under a single write lock acquisition.
+        /// TODO: we can get rid of this lockCache() if we first load everything in parallel
+        /// without any mutual lock between loading threads, and only after do removeOverflow().
+        /// This will be better because overflow here may
+        /// happen only if cache configuration changed and max_size became less than it was.
+        size_t size_limit = 0;
+        {
+            auto lock = cache_guard.writeLock();
+            auto state_lock = cache_state_guard.lock();
+            size_limit = main_priority->getSizeLimit(state_lock);

+            for (auto & segment : segments)
             {
-                auto lock = cache_guard.writeLock();
-                auto state_lock = cache_state_guard.lock();
-                size_limit = main_priority->getSizeLimit(state_lock);
-
-                limits_satisfied = main_priority->canFit(size, 1, state_lock, /* reservee */nullptr, origin_info, true);
-                if (limits_satisfied)
-                    cache_it = main_priority->add(
-                        key_metadata, offset, size, lock, &state_lock, /* best_effort */true);
-
-                /// TODO: we can get rid of this lockCache() if we first load everything in parallel
-                /// without any mutual lock between loading threads, and only after do removeOverflow().
-                /// This will be better because overflow here may
-                /// happen only if cache configuration changed and max_size because less than it was.
+                if (main_priority->canFit(
+                        segment.size,
+                        /* elements */1,
+                        state_lock,
+                        /* reservee */nullptr,
+                        origin_info,
+                        /* is_initial_load */true))
+                {
+                    segment.cache_it = main_priority->add(
+                        key_metadata,
+                        segment.offset,
+                        segment.size,
+                        lock,
+                        &state_lock,
+                        /* is_initial_load */true);
+                }
             }
+        }

-            if (limits_satisfied)
+        /// Phase 3: construct FileSegment objects and emplace
+        /// (no lock held, because a single key is loaded by a single thread).
+        size_t failed_to_fit = 0;
+        for (auto & segment : segments)
+        {
+            if (segment.cache_it)
             {
                 bool inserted = false;
                 try
                 {
-                    auto file_segment = std::make_shared<FileSegment>(key, offset, size,
-                                                                      FileSegment::State::DOWNLOADED,
-                                                                      CreateFileSegmentSettings(segment_kind),
-                                                                      false,
-                                                                      this,
-                                                                      key_metadata,
-                                                                      cache_it);
-
-                    inserted = key_metadata->emplaceUnlocked(offset, std::make_shared<FileSegmentMetadata>(std::move(file_segment))).second;
+                    auto file_segment = std::make_shared<FileSegment>(
+                        key,
+                        segment.offset,
+                        segment.size,
+                        FileSegment::State::DOWNLOADED,
+                        CreateFileSegmentSettings(segment.kind),
+                        /* background_download_enabled */false,
+                        this,
+                        key_metadata,
+                        segment.cache_it);
+
+                    inserted = key_metadata->emplaceUnlocked(segment.offset, std::make_shared<FileSegmentMetadata>(std::move(file_segment))).second;
                 }
                 catch (...)
                 {
@@ -1924,27 +1961,31 @@ void FileCache::loadMetadataForKeys(const fs::path & keys_dir, const OriginInfo

                 if (inserted)
                 {
-                    LOG_TEST(log, "Added file segment {}:{} (size: {}) with path: {}", key, offset, size, offset_it->path().string());
+                    LOG_TEST(log, "Added file segment {}:{} (size: {}) with path: {}", key, segment.offset, segment.size, segment.path.string());
                 }
                 else
                 {
-                    cache_it->remove(cache_guard.writeLock());
-                    fs::remove(offset_it->path());
+                    segment.cache_it->remove(cache_guard.writeLock());
+                    fs::remove(segment.path);
                     chassert(false);
                 }
             }
             else
             {
-                LOG_WARNING(
-                    log,
-                    "Cache capacity changed (max size: {}), "
-                    "cached file `{}` does not fit in cache anymore (size: {})",
-                    size_limit, offset_it->path().string(), size);
-
-                fs::remove(offset_it->path());
+                ++failed_to_fit;
+                fs::remove(segment.path);
             }
         }

+        if (failed_to_fit)
+        {
+            LOG_WARNING(
+                log,
+                "Cache capacity changed (max size: {}), "
+                "{} file(s) for key {} do not fit in cache anymore",
+                size_limit, failed_to_fit, key);
+        }
+
         if (key_metadata->sizeUnlocked() == 0)
         {
             metadata.removeKey(key, false, false, origin_info.user_id);
diff --git a/src/Interpreters/Cache/IFileCachePriority.h b/src/Interpreters/Cache/IFileCachePriority.h
index 26fe8b0d7c4b..148467fb34cb 100644
--- a/src/Interpreters/Cache/IFileCachePriority.h
+++ b/src/Interpreters/Cache/IFileCachePriority.h
@@ -212,7 +212,7 @@ class IFileCachePriority : private boost::noncopyable
         size_t size,
         const CachePriorityGuard::WriteLock &,
         const CacheStateGuard::Lock *,
-        bool best_effort = false) = 0;
+        bool is_initial_load = false) = 0;

     /// `reservee` is the entry for which are reserving now.
     /// It does not exist, if it is the first space reservation attempt
@@ -223,7 +223,7 @@ class IFileCachePriority : private boost::noncopyable
         const CacheStateGuard::Lock &,
         IteratorPtr reservee = nullptr,
         const OriginInfo & origin_info = {},
-        bool best_effort = false) const = 0;
+        bool is_initial_load = false) const = 0;

     virtual bool tryIncreasePriority(
         Iterator & iterator,
diff --git a/src/Interpreters/Cache/LRUFileCachePriority.h b/src/Interpreters/Cache/LRUFileCachePriority.h
index 52f750393a6f..fc975bb592b3 100644
--- a/src/Interpreters/Cache/LRUFileCachePriority.h
+++ b/src/Interpreters/Cache/LRUFileCachePriority.h
@@ -70,7 +70,7 @@ class LRUFileCachePriority : public IFileCachePriority
         const CacheStateGuard::Lock &,
         IteratorPtr reservee = nullptr,
         const OriginInfo & origin_info = {},
-        bool best_effort = false) const override;
+        bool is_initial_load = false) const override;

     /// Create a queue entry for given key and offset.
     /// Write priority lock is required.
@@ -84,7 +84,7 @@ class LRUFileCachePriority : public IFileCachePriority
         size_t size,
         const CachePriorityGuard::WriteLock &,
         const CacheStateGuard::Lock *,
-        bool best_effort = false) override;
+        bool is_initial_load = false) override;

     bool collectCandidatesForEviction(
         const EvictionInfo & eviction_info,
diff --git a/src/Interpreters/Cache/SLRUFileCachePriority.cpp b/src/Interpreters/Cache/SLRUFileCachePriority.cpp
index 759213e7602f..7e564cd154ca 100644
--- a/src/Interpreters/Cache/SLRUFileCachePriority.cpp
+++ b/src/Interpreters/Cache/SLRUFileCachePriority.cpp
@@ -107,9 +107,9 @@ bool SLRUFileCachePriority::canFit( /// NOLINT
     const CacheStateGuard::Lock & lock,
     IteratorPtr reservee,
     const OriginInfo &,
-    bool best_effort) const
+    bool is_initial_load) const
 {
-    if (best_effort)
+    if (is_initial_load)
         return probationary_queue.canFit(size, elements, lock) || protected_queue.canFit(size, elements, lock);

     if (reservee)
@@ -128,10 +128,10 @@ IFileCachePriority::IteratorPtr SLRUFileCachePriority::add( /// NOLINT
     size_t size,
     const CachePriorityGuard::WriteLock & lock,
     const CacheStateGuard::Lock * state_lock,
-    bool is_startup)
+    bool is_initial_load)
 {
     bool is_protected = false;
-    if (is_startup)
+    if (is_initial_load)
     {
         chassert(size);
         if (!state_lock)
diff --git a/src/Interpreters/Cache/SLRUFileCachePriority.h b/src/Interpreters/Cache/SLRUFileCachePriority.h
index ee2eb2d0fee2..02c8a866d7dc 100644
--- a/src/Interpreters/Cache/SLRUFileCachePriority.h
+++ b/src/Interpreters/Cache/SLRUFileCachePriority.h
@@ -51,7 +51,7 @@ class SLRUFileCachePriority : public IFileCachePriority
         const CacheStateGuard::Lock &,
         IteratorPtr reservee = nullptr,
         const OriginInfo & origin_info = {},
-        bool best_effort = false) const override;
+        bool is_initial_load = false) const override;

     IteratorPtr add( /// NOLINT
         KeyMetadataPtr key_metadata,
@@ -59,7 +59,7 @@ class SLRUFileCachePriority : public IFileCachePriority
         size_t size,
         const CachePriorityGuard::WriteLock &,
         const CacheStateGuard::Lock *,
-        bool is_startup = false) override;
+        bool is_initial_load = false) override;

     bool collectCandidatesForEviction(
         const EvictionInfo & eviction_info,
diff --git a/src/Interpreters/Cache/SplitFileCachePriority.cpp b/src/Interpreters/Cache/SplitFileCachePriority.cpp
index 569964d29375..45a01ff41a15 100644
--- a/src/Interpreters/Cache/SplitFileCachePriority.cpp
+++ b/src/Interpreters/Cache/SplitFileCachePriority.cpp
@@ -170,11 +170,11 @@ IFileCachePriority::IteratorPtr SplitFileCachePriority::add( /// NOLINT
     size_t size,
     const CachePriorityGuard::WriteLock & write_lock,
     const CacheStateGuard::Lock * state_lock,
-    bool best_effort)
+    bool is_initial_load)
 {
     const auto type = getPriorityType(key_metadata->origin.segment_type);
     return priorities_holder.at(type)->add(
-        key_metadata, offset, size, write_lock, state_lock, best_effort);
+        key_metadata, offset, size, write_lock, state_lock, is_initial_load);
 }

 bool SplitFileCachePriority::canFit( /// NOLINT
@@ -183,11 +183,11 @@ bool SplitFileCachePriority::canFit( /// NOLINT
     const CacheStateGuard::Lock & lock,
     IteratorPtr reservee,
     const OriginInfo & origin_info,
-    bool best_effort) const
+    bool is_initial_load) const
 {
     const auto type = getPriorityType(origin_info.segment_type);
     return priorities_holder.at(type)->canFit(
-        size, elements, lock, reservee, origin_info, best_effort);
+        size, elements, lock, reservee, origin_info, is_initial_load);
 }

 EvictionInfoPtr SplitFileCachePriority::collectEvictionInfo(
diff --git a/src/Interpreters/Cache/SplitFileCachePriority.h b/src/Interpreters/Cache/SplitFileCachePriority.h
index 96e6bdf86bba..4306f4462c9b 100644
--- a/src/Interpreters/Cache/SplitFileCachePriority.h
+++ b/src/Interpreters/Cache/SplitFileCachePriority.h
@@ -52,7 +52,7 @@ class SplitFileCachePriority : public IFileCachePriority
         const CacheStateGuard::Lock &,
         IteratorPtr reservee = nullptr,
         const OriginInfo & origin_info = {},
-        bool best_effort = false) const override;
+        bool is_initial_load = false) const override;

     IteratorPtr add( /// NOLINT
         KeyMetadataPtr key_metadata,
@@ -60,7 +60,7 @@ class SplitFileCachePriority : public IFileCachePriority
         size_t size,
         const CachePriorityGuard::WriteLock &,
         const CacheStateGuard::Lock *,
-        bool best_effort = false) override;
+        bool is_initial_load = false) override;

     bool tryIncreasePriority(
         Iterator & iterator,
PATCH

# Verify the patch was applied (idempotency check)
grep -q "main_priority->check(cache_state_guard.lock())" src/Interpreters/Cache/FileCache.cpp || exit 1

echo "Patch applied successfully"
