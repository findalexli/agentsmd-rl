#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17320
cat <<'PATCH' | git apply -
diff --git a/.github/workflows/pre-release.yml b/.github/workflows/pre-release.yml
index 26eaa3e637109..454488fedf843 100644
--- a/.github/workflows/pre-release.yml
+++ b/.github/workflows/pre-release.yml
@@ -148,7 +148,7 @@ jobs:
     with:
       name: Run dependency updates
       ref: staging/release-${{ needs.parse-tag.outputs.tag }}
-      run: ./go ${{ needs.parse-tag.outputs.language }}:update${{ needs.parse-tag.outputs.language == 'all' && ' && ./go rust:update' || '' }}
+      run: ./go ${{ needs.parse-tag.outputs.language }}:update
       artifact-name: patch-dep-updates

   calculate-changelog-depth:
diff --git a/rake_tasks/rust.rake b/rake_tasks/rust.rake
index b780d5f0605c3..e6a6d7ac52bfa 100644
--- a/rake_tasks/rust.rake
+++ b/rake_tasks/rust.rake
@@ -57,4 +57,16 @@ task :version, [:version] do |_task, arguments|
     text = File.read(file).gsub(old_version, new_version)
     File.open(file, 'w') { |f| f.puts text }
   end
+
+  # Repin cargo immediately after updating the version so Cargo.Bazel.lock is
+  # never left in a stale state between jobs.  Running CARGO_BAZEL_REPIN=true
+  # against a Cargo.toml whose version has already changed (but whose lockfile
+  # hasn't been updated yet) causes Bazel to detect a mid-evaluation file-hash
+  # conflict and crash (rules_rust extensions.bzl reads the lockfile twice
+  # within the same Bazel evaluation).
+  # reenable is required because Rake::Task#invoke is a no-op if the task has
+  # already run once in this Ruby process (e.g. when multiple tasks are chained
+  # in a single ./go invocation).
+  Rake::Task['rust:update'].reenable
+  Rake::Task['rust:update'].invoke
 end
PATCH

echo "Patch applied successfully"
