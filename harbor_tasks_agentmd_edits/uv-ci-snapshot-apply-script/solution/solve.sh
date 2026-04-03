#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'INSTA_PENDING_DIR' .github/workflows/test.yml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/test.yml b/.github/workflows/test.yml
index 1ca7e682ab497..2234882f6fbae 100644
--- a/.github/workflows/test.yml
+++ b/.github/workflows/test.yml
@@ -98,6 +98,9 @@ jobs:
           UV_INTERNAL__TEST_NOCOW_FS: /tmpfs
           UV_INTERNAL__TEST_ALT_FS: /tmpfs
           UV_INTERNAL__TEST_LOWLINKS_FS: /minix
+          # Write pending snapshots to a separate directory for artifact upload
+          INSTA_UPDATE: new
+          INSTA_PENDING_DIR: ${{ github.workspace }}/pending-snapshots
         run: |
           cargo nextest run \
             --cargo-profile fast-build \
@@ -105,6 +108,16 @@ jobs:
             --workspace \
             --profile ci-linux

+      - name: "Upload pending snapshots"
+        if: ${{ failure() }}
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
+        with:
+          name: pending-snapshots-linux
+          path: pending-snapshots/
+          if-no-files-found: ignore
+          include-hidden-files: true
+          retention-days: 14
+
   cargo-test-macos:
     timeout-minutes: 20
     # Only run macOS tests on main without opt-in
@@ -151,6 +164,9 @@ jobs:
           # HFS+ RAM disk does not support copy-on-write and is on a different device
           UV_INTERNAL__TEST_NOCOW_FS: ${{ env.HFS_MOUNT }}
           UV_INTERNAL__TEST_ALT_FS: ${{ env.HFS_MOUNT }}
+          # Write pending snapshots to a separate directory for artifact upload
+          INSTA_UPDATE: new
+          INSTA_PENDING_DIR: ${{ github.workspace }}/pending-snapshots
         run: |
           cargo nextest run \
             --cargo-profile fast-build \
@@ -159,6 +175,16 @@ jobs:
             --workspace \
             --profile ci-macos

+      - name: "Upload pending snapshots"
+        if: ${{ failure() }}
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
+        with:
+          name: pending-snapshots-macos
+          path: pending-snapshots/
+          if-no-files-found: ignore
+          include-hidden-files: true
+          retention-days: 14
+
   cargo-test-windows:
     timeout-minutes: 15
     runs-on: github-windows-2025-x86_64-16
@@ -216,6 +242,9 @@ jobs:
           UV_LINK_MODE: copy
           RUST_BACKTRACE: 1
           UV_INTERNAL__TEST_LOWLINKS_FS: "C:\\uv"
+          # Write pending snapshots to a separate directory for artifact upload
+          INSTA_UPDATE: new
+          INSTA_PENDING_DIR: ${{ github.workspace }}/pending-snapshots
         shell: bash
         run: |
           cargo nextest run \
@@ -225,3 +254,13 @@ jobs:
             --workspace \
             --profile ci-windows \
             --partition hash:${{ matrix.partition }}/3
+
+      - name: "Upload pending snapshots"
+        if: ${{ failure() }}
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
+        with:
+          name: pending-snapshots-windows-${{ matrix.partition }}
+          path: pending-snapshots/
+          if-no-files-found: ignore
+          include-hidden-files: true
+          retention-days: 14
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 5e991aab03f59..12d0a396ed64d 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -114,6 +114,13 @@ cargo test --package <package> --test <test> -- <test_name> -- --exact
 cargo insta review
 ```

+A script is available to update the snapshots based on results in CI. This is useful for updating
+snapshots without re-running the test suite and for updating platform-specific snapshots.
+
+```shell
+./scripts/apply-ci-snapshots.sh
+```
+
 ### Git and Git LFS

 A subset of uv tests require both [Git](https://git-scm.com) and [Git LFS](https://git-lfs.com/) to
diff --git a/Cargo.toml b/Cargo.toml
index df4b6e0597f84..1a895e5a5ba8a 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -318,7 +318,7 @@ http-body-util = { version = "0.1.2" }
 hyper = { version = "1.4.1", features = ["server", "http1"] }
 hyper-util = { version = "0.1.8", features = ["tokio", "server", "http1"] }
 ignore = { version = "0.4.23" }
-insta = { version = "1.40.0", features = ["json", "filters", "redactions"] }
+insta = { version = "1.46.0", features = ["json", "filters", "redactions"] }
 predicates = { version = "3.1.2" }
 rcgen = { version = "0.14.5", features = [
   "crypto",
diff --git a/scripts/apply-ci-snapshots.sh b/scripts/apply-ci-snapshots.sh
new file mode 100755
index 0000000000000..6807011755dea
--- /dev/null
+++ b/scripts/apply-ci-snapshots.sh
@@ -0,0 +1,104 @@
+#!/usr/bin/env bash
+# Download and apply pending insta snapshots from a CI run.
+#
+# Usage:
+#   scripts/apply-ci-snapshots.sh                  # auto-detect PR for current branch
+#   scripts/apply-ci-snapshots.sh <run-id>         # use a specific workflow run ID
+#   scripts/apply-ci-snapshots.sh <run-id> review  # interactively review instead of accepting
+#
+# Requires: gh (GitHub CLI), cargo-insta
+
+set -euo pipefail
+
+for cmd in gh cargo-insta git; do
+    if ! command -v "$cmd" &>/dev/null; then
+        echo "error: '$cmd' is required but not found in PATH" >&2
+        exit 1
+    fi
+done
+
+REPO="astral-sh/uv"
+TMPDIR_BASE="${TMPDIR:-/tmp}"
+DOWNLOAD_DIR="$TMPDIR_BASE/uv-pending-snapshots-$$"
+
+cleanup() {
+    rm -rf "$DOWNLOAD_DIR"
+}
+trap cleanup EXIT
+
+action="${2:-accept}"
+if [[ "$action" != "accept" && "$action" != "review" ]]; then
+    echo "error: action must be 'accept' or 'review', got '$action'" >&2
+    exit 1
+fi
+
+# Resolve the run ID
+if [[ "${1:-}" ]]; then
+    run_id="$1"
+else
+    # Auto-detect: find the latest CI run for the current branch's PR
+    branch="$(git branch --show-current)"
+    if [[ -z "$branch" ]]; then
+        echo "error: not on a branch and no run ID provided" >&2
+        exit 1
+    fi
+
+    pr_number="$(gh pr view "$branch" --repo "$REPO" --json number --jq '.number' 2>/dev/null || true)"
+    if [[ -z "$pr_number" ]]; then
+        echo "error: no PR found for branch '$branch'" >&2
+        exit 1
+    fi
+
+    echo "Found pull request #$pr_number for branch '$branch'..."
+
+    run_id="$(gh run list \
+        --repo "$REPO" \
+        --workflow ci.yml \
+        --branch "$branch" \
+        --limit 1 \
+        --json databaseId \
+        --jq '.[0].databaseId')"
+    if [[ -z "$run_id" ]]; then
+        echo "error: no CI runs found for branch '$branch'" >&2
+        exit 1
+    fi
+    echo "Found latest CI run $run_id"
+fi
+
+# Download all pending-snapshots artifacts from the run
+echo "Downloading pending snapshot artifacts..."
+mkdir -p "$DOWNLOAD_DIR"
+gh run download "$run_id" \
+    --repo "$REPO" \
+    --pattern "pending-snapshots-*" \
+    --dir "$DOWNLOAD_DIR" 2>/dev/null || true
+
+# Check if any artifacts were downloaded
+artifact_count="$(find "$DOWNLOAD_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
+if [[ "$artifact_count" -eq 0 ]]; then
+    echo "No pending snapshot artifacts found in run $run_id."
+    echo "Either the tests passed or no snapshot mismatches occurred."
+    exit 0
+fi
+
+echo "Downloaded $artifact_count artifact(s)"
+
+# Merge all artifacts into a single pending-snapshots directory.
+# Different platforms may produce different snapshots; we collect them all.
+merged_dir="$DOWNLOAD_DIR/_merged"
+mkdir -p "$merged_dir"
+for artifact_dir in "$DOWNLOAD_DIR"/pending-snapshots-*/; do
+    [[ -d "$artifact_dir" ]] || continue
+    cp -rn "$artifact_dir"/* "$merged_dir"/ 2>/dev/null || true
+done
+
+snapshot_count="$(find "$merged_dir" -type f \( -name '*.snap.new' -o -name '*.pending-snap' \) | wc -l | tr -d ' ')"
+if [[ "$snapshot_count" -eq 0 ]]; then
+    echo "No pending snapshot files found in the artifacts."
+    exit 0
+fi
+
+echo "Applying $snapshot_count snapshot change(s)..."
+
+# Use cargo-insta with INSTA_PENDING_DIR to apply the snapshots
+INSTA_PENDING_DIR="$merged_dir" cargo insta "$action" --workspace

PATCH

echo "Patch applied successfully."
