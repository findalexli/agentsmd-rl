#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'repair-sdist-cargo-lock' scripts/repair-sdist-cargo-lock.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/build-release-binaries.yml b/.github/workflows/build-release-binaries.yml
index 8e3ebff696d0a..c101f02021e79 100644
--- a/.github/workflows/build-release-binaries.yml
+++ b/.github/workflows/build-release-binaries.yml
@@ -72,6 +72,8 @@ jobs:
           maturin-version: v1.12.6
           command: sdist
           args: --out crates/uv-build/dist -m crates/uv-build/Cargo.toml
+      - name: "Fix Cargo.lock in sdist uv-build"
+        run: python scripts/repair-sdist-cargo-lock.py crates/uv-build/dist/${PACKAGE_NAME}_build-*.tar.gz
       - name: "Test sdist uv-build"
         run: |
           pip install crates/uv-build/dist/${PACKAGE_NAME}_build-*.tar.gz --force-reinstall
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 3f10bdf7893b3..3e987042bebfc 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -77,7 +77,7 @@ jobs:
             [[ "$file" == "pyproject.toml" || "$file" =~ ^crates/.*/pyproject\.toml$ ]] && python_config_changed=1
             [[ "$file" =~ ^\.github/workflows/.*\.yml$ ]] && workflow_changed=1
             [[ "$file" == ".github/workflows/build-release-binaries.yml" || "$file" == ".github/workflows/release.yml" ]] && release_workflow_changed=1
-            [[ "$file" == "scripts/check_uv_wheel_contents.py" || "$file" == "scripts/patch-dist-manifest-checksums.py" ]] && release_build_changed=1
+            [[ "$file" == "scripts/check_uv_wheel_contents.py" || "$file" == "scripts/patch-dist-manifest-checksums.py" || "$file" == "scripts/repair-sdist-cargo-lock.py" ]] && release_build_changed=1
             [[ "$file" == ".github/workflows/ci.yml" ]] && ci_workflow_changed=1
             [[ "$file" == "uv.schema.json" ]] && schema_changed=1
             [[ "$file" =~ ^crates/uv-publish/ || "$file" =~ ^scripts/publish/ || "$file" == "crates/uv/src/commands/publish.rs" ]] && publish_code_changed=1
diff --git a/scripts/repair-sdist-cargo-lock.py b/scripts/repair-sdist-cargo-lock.py
new file mode 100644
index 0000000000000..edc5521dd35f8
--- /dev/null
+++ b/scripts/repair-sdist-cargo-lock.py
@@ -0,0 +1,96 @@
+#!/usr/bin/env python3
+"""Fix the Cargo.lock inside a maturin-generated sdist tarball.
+
+Maturin copies the full workspace Cargo.lock into the sdist, but the sdist
+only contains a subset of workspace crates. This makes `cargo build --locked`
+fail because the lock file references packages not present in the sdist.
+
+This script extracts the sdist, runs `cargo update --workspace` to prune
+the lockfile to only the packages needed by the included crates (without
+changing any pinned versions), and repacks the tarball.
+
+See: https://github.com/astral-sh/uv/issues/18824
+"""
+
+import argparse
+import os
+import subprocess
+import sys
+import tarfile
+import tempfile
+
+
+def fix_sdist_lockfile(sdist_path: str) -> None:
+    sdist_path = os.path.abspath(sdist_path)
+    if not tarfile.is_tarfile(sdist_path):
+        print(f"Error: {sdist_path} is not a valid tar file", file=sys.stderr)
+        sys.exit(1)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        # Extract
+        with tarfile.open(sdist_path, "r:gz") as tar:
+            tar.extractall(tmpdir)
+
+        # Find the extracted directory (e.g., uv_build-0.10.12)
+        entries = os.listdir(tmpdir)
+        if len(entries) != 1:
+            print(
+                f"Error: expected one top-level directory, found: {entries}",
+                file=sys.stderr,
+            )
+            sys.exit(1)
+        extracted_dir = os.path.join(tmpdir, entries[0])
+        top_level_name = entries[0]
+
+        # Check for Cargo.lock
+        cargo_lock = os.path.join(extracted_dir, "Cargo.lock")
+        if not os.path.exists(cargo_lock):
+            print(
+                f"Error: no Cargo.lock found in sdist {top_level_name}", file=sys.stderr
+            )
+            sys.exit(1)
+
+        # Prune Cargo.lock to only packages needed by the included crates.
+        # `cargo update --workspace` removes entries for missing workspace members
+        # while preserving pinned versions for all remaining dependencies.
+        print(f"Pruning Cargo.lock in {top_level_name}...")
+        subprocess.run(
+            ["cargo", "update", "--workspace"],
+            cwd=extracted_dir,
+            check=True,
+        )
+
+        # Verify it works with --locked
+        print("Verifying Cargo.lock with --locked...")
+        result = subprocess.run(
+            ["cargo", "metadata", "--locked", "--format-version=1"],
+            cwd=extracted_dir,
+            capture_output=True,
+        )
+        if result.returncode != 0:
+            print(
+                f"Error: Cargo.lock still out of sync after pruning:\n{result.stderr.decode()}",
+                file=sys.stderr,
+            )
+            sys.exit(1)
+        print("Cargo.lock is consistent.")
+
+        # Repack the tarball
+        print(f"Repacking {sdist_path}...")
+        with tarfile.open(sdist_path, "w:gz") as tar:
+            tar.add(extracted_dir, arcname=top_level_name)
+
+    print("Done.")
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(
+        description="Fix Cargo.lock in a maturin-generated sdist"
+    )
+    parser.add_argument("sdist", help="Path to the sdist .tar.gz file")
+    args = parser.parse_args()
+    fix_sdist_lockfile(args.sdist)
+
+
+if __name__ == "__main__":
+    main()

PATCH

echo "Patch applied successfully."
