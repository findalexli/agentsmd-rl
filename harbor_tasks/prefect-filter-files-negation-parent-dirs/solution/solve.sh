#!/bin/bash
set -e

cd /workspace/prefect

# Check if already patched (idempotency)
if grep -q "parent_dirs: set\[str\]" src/prefect/utilities/filesystem.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/src/prefect/utilities/filesystem.py b/src/prefect/utilities/filesystem.py
index 92579c444c87..847f0ffde178 100644
--- a/src/prefect/utilities/filesystem.py
+++ b/src/prefect/utilities/filesystem.py
@@ -52,6 +52,20 @@ def filter_files(
     else:
         all_files = set(pathspec.util.iter_tree_files(root))
     included_files = all_files - ignored_files
+
+    # Ensure parent directories of included files are also included,
+    # so that copytree's ignore_func doesn't skip directories containing
+    # files that should be copied.
+    if include_dirs:
+        parent_dirs: set[str] = set()
+        for file_path in included_files:
+            for parent in Path(file_path).parents:
+                parent_str = str(parent)
+                if parent_str == ".":
+                    break
+                parent_dirs.add(parent_str)
+        included_files |= parent_dirs
+
     return included_files


diff --git a/tests/utilities/test_filesystem.py b/tests/utilities/test_filesystem.py
index 820afdb5838c..6fd89f02c37c 100644
--- a/tests/utilities/test_filesystem.py
+++ b/tests/utilities/test_filesystem.py
@@ -118,6 +118,36 @@ async def test_alternate_directory_filter(self, tmpdir, messy_dir, include_dirs)
         )
         assert {f for f in filtered if "pycache" in f} == expected

+    async def test_negation_includes_parent_dirs(self, tmp_path):
+        """Parent directories of negation-included files must be in the result
+        so that copytree's ignore_func does not skip them."""
+        (tmp_path / "workflows").mkdir()
+        (tmp_path / "workflows" / "flow.py").write_text("print('hi')")
+        (tmp_path / "other.txt").write_text("other")
+        (tmp_path / ".prefectignore").write_text("")
+
+        result = filter_files(
+            root=str(tmp_path),
+            ignore_patterns=["*", "!.prefectignore", "!workflows/", "!workflows/*"],
+        )
+        assert "workflows" in result
+        assert any("flow.py" in f for f in result)
+
+    async def test_negation_includes_nested_parent_dirs(self, tmp_path):
+        """All ancestor directories of a deeply-nested negation-included file
+        must appear in the result."""
+        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
+        (tmp_path / "a" / "b" / "c" / "file.py").write_text("print('hi')")
+
+        result = filter_files(
+            root=str(tmp_path),
+            ignore_patterns=["*", "!a/b/c/file.py"],
+        )
+        assert "a" in result
+        assert str(Path("a") / "b") in result
+        assert str(Path("a") / "b" / "c") in result
+        assert str(Path("a") / "b" / "c" / "file.py") in result
+
 class TestPlatformSpecificRelpath:
     @pytest.mark.unix
PATCH

echo "Patch applied successfully"
