#!/usr/bin/env bash
set -euo pipefail
cd /workspace/next.js

# Idempotent: skip if already applied
grep -q 'amqf_data_start' turbopack/crates/turbo-persistence/src/meta_file.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/src/meta_file.rs b/turbopack/crates/turbo-persistence/src/meta_file.rs
index 019608a791a7cb..8728a38c5570bf 100644
--- a/turbopack/crates/turbo-persistence/src/meta_file.rs
+++ b/turbopack/crates/turbo-persistence/src/meta_file.rs
@@ -229,6 +229,8 @@ pub struct MetaFile {
     /// The offset of the end of the "used keys" AMQF data in the the meta file relative to the end
     /// of the header.
     end_of_used_keys_amqf_data_offset: u32,
+    /// Byte offset of the start of AMQF data within the mmap (= end of the header).
+    amqf_data_start: usize,
     /// The memory mapped file.
     mmap: Mmap,
 }
@@ -244,7 +246,7 @@ impl MetaFile {
     }

     fn open_internal(db_path: PathBuf, sequence_number: u32, path: &Path) -> Result<Self> {
-        let mut file = BufReader::new(File::open(path)?);
+        let mut file = BufReader::new(File::open(path).context("Failed to open meta file")?);
         let magic = file.read_u32::<BE>()?;
         if magic != 0xFE4ADA4A {
             bail!("Invalid magic number");
@@ -281,14 +283,14 @@ impl MetaFile {
         let start_of_used_keys_amqf_data_offset = start_of_amqf_data_offset;
         let end_of_used_keys_amqf_data_offset = file.read_u32::<BE>()?;

-        let offset = file.stream_position()?;
+        let offset = file
+            .stream_position()
+            .context("Failed to get stream position")?;
         let file = file.into_inner();
-        let mut options = MmapOptions::new();
-        options.offset(offset);
-        let mmap = unsafe { options.map(&file) }
-            .with_context(|| format!("Failed to mmap meta file {}", path.display()))?;
+        let mmap = unsafe { MmapOptions::new().map(&file) }.context("Failed to mmap")?;
         #[cfg(unix)]
-        mmap.advise(memmap2::Advice::Random)?;
+        mmap.advise(memmap2::Advice::Random)
+            .context("Failed to advise mmap")?;
         advise_mmap_for_persistence(&mmap)?;
         let file = Self {
             db_path,
@@ -299,6 +301,7 @@ impl MetaFile {
             obsolete_sst_files,
             start_of_used_keys_amqf_data_offset,
             end_of_used_keys_amqf_data_offset,
+            amqf_data_start: offset as usize,
             mmap,
         };
         Ok(file)
@@ -336,7 +339,7 @@ impl MetaFile {
     }

     pub fn amqf_data(&self) -> &[u8] {
-        &self.mmap
+        &self.mmap[self.amqf_data_start..]
     }

     pub fn deserialize_used_key_hashes_amqf(&self) -> Result<Option<qfilter::Filter>> {
diff --git a/turbopack/crates/turbo-persistence/src/mmap_helper.rs b/turbopack/crates/turbo-persistence/src/mmap_helper.rs
index be6a951f0cd6a6..c9ebc3ecb60dc6 100644
--- a/turbopack/crates/turbo-persistence/src/mmap_helper.rs
+++ b/turbopack/crates/turbo-persistence/src/mmap_helper.rs
@@ -1,3 +1,5 @@
+use anyhow::Context;
+
 /// Apply Linux-specific mmap advice flags that should be set on all persistent mmaps.
 ///
 /// - `DontFork`: prevents mmap regions from being copied into child processes on `fork()`, avoiding
@@ -6,8 +8,10 @@
 ///   compressed content that won't benefit from deduplication scanning.
 #[cfg(target_os = "linux")]
 pub fn advise_mmap_for_persistence(mmap: &memmap2::Mmap) -> anyhow::Result<()> {
-    mmap.advise(memmap2::Advice::DontFork)?;
-    mmap.advise(memmap2::Advice::Unmergeable)?;
+    mmap.advise(memmap2::Advice::DontFork)
+        .context("Failed to advise mmap DontFork")?;
+    mmap.advise(memmap2::Advice::Unmergeable)
+        .context("Failed to advise mmap Unmergeable")?;
     Ok(())
 }

PATCH
