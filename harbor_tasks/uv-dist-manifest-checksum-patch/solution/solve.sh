#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the script already exists with the key function, skip
if grep -q 'def read_sha256' scripts/patch-dist-manifest-checksums.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 250506aa9306d..3f10bdf7893b3 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -76,8 +76,8 @@ jobs:
             [[ "$file" == "rust-toolchain.toml" || "$file" =~ ^\.cargo/ ]] && rust_config_changed=1
             [[ "$file" == "pyproject.toml" || "$file" =~ ^crates/.*/pyproject\.toml$ ]] && python_config_changed=1
             [[ "$file" =~ ^\.github/workflows/.*\.yml$ ]] && workflow_changed=1
-            [[ "$file" == ".github/workflows/build-release-binaries.yml" ]] && release_workflow_changed=1
-            [[ "$file" == "scripts/check_uv_wheel_contents.py" ]] && release_build_changed=1
+            [[ "$file" == ".github/workflows/build-release-binaries.yml" || "$file" == ".github/workflows/release.yml" ]] && release_workflow_changed=1
+            [[ "$file" == "scripts/check_uv_wheel_contents.py" || "$file" == "scripts/patch-dist-manifest-checksums.py" ]] && release_build_changed=1
             [[ "$file" == ".github/workflows/ci.yml" ]] && ci_workflow_changed=1
             [[ "$file" == "uv.schema.json" ]] && schema_changed=1
             [[ "$file" =~ ^crates/uv-publish/ || "$file" =~ ^scripts/publish/ || "$file" == "crates/uv/src/commands/publish.rs" ]] && publish_code_changed=1
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
index 334840df1af56..ce30e9c38bd06 100644
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -113,12 +113,51 @@ jobs:
       "id-token": "write"
       "packages": "write"

+  synthesize-local-dist-manifest:
+    needs:
+      - plan
+      - custom-build-release-binaries
+    if: ${{ needs.plan.outputs.publishing == 'true' || fromJson(needs.plan.outputs.val).ci.github.pr_run_mode == 'upload' || inputs.tag == 'dry-run' }}
+    runs-on: "depot-ubuntu-latest-4"
+    steps:
+      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
+        with:
+          persist-credentials: false
+          submodules: recursive
+      - name: Install cached dist
+        uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093
+        with:
+          name: cargo-dist-cache
+          path: ~/.cargo/bin/
+      - run: chmod +x ~/.cargo/bin/dist
+      - name: Fetch local artifacts
+        uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093
+        with:
+          pattern: artifacts-*
+          path: target/distrib/
+          merge-multiple: true
+      - name: Generate local dist manifest
+        shell: bash
+        env:
+          TAG: ${{ needs.plan.outputs.tag-flag }}
+        run: |
+          temp_manifest=target/local-dist-manifest.json.tmp
+          dist manifest "$TAG" --output-format=json --no-local-paths --artifacts=local > "$temp_manifest"
+          python3 scripts/patch-dist-manifest-checksums.py --manifest "$temp_manifest" --artifacts-dir target/distrib
+          mv "$temp_manifest" target/distrib/local-dist-manifest.json
+      - name: Upload synthesized local dist manifest
+        uses: actions/upload-artifact@6027e3dd177782cd8ab9af838c04fd81a07f1d47
+        with:
+          name: artifacts-build-local-manifest
+          path: target/distrib/local-dist-manifest.json
+
   # Build and package all the platform-agnostic(ish) things
   build-global-artifacts:
     needs:
       - plan
       - custom-build-release-binaries
       - custom-build-docker
+      - synthesize-local-dist-manifest
     runs-on: "depot-ubuntu-latest-4"
     env:
       GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
diff --git a/scripts/patch-dist-manifest-checksums.py b/scripts/patch-dist-manifest-checksums.py
new file mode 100644
index 0000000000000..d469b98147459
--- /dev/null
+++ b/scripts/patch-dist-manifest-checksums.py
@@ -0,0 +1,75 @@
+#!/usr/bin/env python3
+"""Patch cargo-dist local manifest JSON with sidecar SHA-256 checksums.
+
+This is used by the release workflow when custom local artifact jobs build archives
+outside of cargo-dist. cargo-dist's global installer generation can embed archive
+checksums if they appear in dist-manifest.json, so we synthesize a local manifest
+and then inject the checksums from the uploaded `*.sha256` sidecar files.
+"""
+
+from __future__ import annotations
+
+import argparse
+import json
+import sys
+from pathlib import Path
+
+
+def parse_args() -> argparse.Namespace:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--manifest", type=Path, required=True)
+    parser.add_argument("--artifacts-dir", type=Path, required=True)
+    return parser.parse_args()
+
+
+def read_sha256(path: Path) -> str:
+    line = path.read_text(encoding="utf-8").strip()
+    if not line:
+        raise ValueError(f"empty checksum file: {path}")
+    checksum = line.split()[0]
+    if len(checksum) != 64:
+        raise ValueError(f"unexpected sha256 length in {path}: {checksum!r}")
+    return checksum
+
+
+def main() -> int:
+    args = parse_args()
+
+    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
+    artifacts: dict[str, dict] = manifest["artifacts"]
+
+    patched = 0
+    skipped = 0
+    for checksum_path in sorted(args.artifacts_dir.glob("*.sha256")):
+        artifact_name = checksum_path.name[: -len(".sha256")]
+        artifact = artifacts.get(artifact_name)
+        if artifact is None:
+            print(
+                f"warning: checksum file {checksum_path.name} does not match any artifact in {args.manifest.name}",
+                file=sys.stderr,
+            )
+            skipped += 1
+            continue
+
+        checksum = read_sha256(checksum_path)
+        artifact.setdefault("checksums", {})["sha256"] = checksum
+        patched += 1
+
+    if patched == 0:
+        print(
+            f"error: no artifact checksums were patched from {args.artifacts_dir}",
+            file=sys.stderr,
+        )
+        return 1
+
+    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
+    print(
+        f"patched {patched} artifact checksum(s) in {args.manifest}"
+        + (f" ({skipped} checksum file(s) skipped)" if skipped else ""),
+        file=sys.stderr,
+    )
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())

PATCH

echo "Patch applied successfully."
