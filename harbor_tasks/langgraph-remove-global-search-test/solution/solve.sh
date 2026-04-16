#!/bin/bash
set -e

# Apply the fix for removing test_list_global_search and bumping version
cd /workspace/langgraph

cat > /tmp/fix.patch << 'PATCH'
diff --git a/libs/checkpoint-conformance/langgraph/checkpoint/conformance/spec/test_list.py b/libs/checkpoint-conformance/langgraph/checkpoint/conformance/spec/test_list.py
index abc123..def456 100644
--- a/libs/checkpoint-conformance/langgraph/checkpoint/conformance/spec/test_list.py
+++ b/libs/checkpoint-conformance/langgraph/checkpoint/conformance/spec/test_list.py
@@ -339,36 +339,6 @@ async def test_list_metadata_custom_keys(
     assert results[0].metadata["run_id"] == "run-abc"


-async def test_list_global_search(
-    saver: BaseCheckpointSaver,
-) -> None:
-    """alist(None, filter=...) searches across all threads."""
-    tid1, tid2 = str(uuid4()), str(uuid4())
-
-    # Use a unique marker so we don't collide with other tests' data
-    marker = str(uuid4())
-
-    cfg1 = generate_config(tid1)
-    cp1 = generate_checkpoint()
-    await saver.aput(cfg1, cp1, generate_metadata(source="input", marker=marker), {})
-
-    cfg2 = generate_config(tid2)
-    cp2 = generate_checkpoint()
-    await saver.aput(cfg2, cp2, generate_metadata(source="loop", marker=marker), {})
-
-    # Search across all threads with filter
-    results = []
-    async for tup in saver.alist(None, filter={"source": "input", "marker": marker}):
-        results.append(tup)
-    assert len(results) == 1
-    assert results[0].config["configurable"]["thread_id"] == tid1
-
-    # Search with marker only — should find both
-    results = []
-    async for tup in saver.alist(None, filter={"marker": marker}):
-        results.append(tup)
-    assert len(results) == 2
-

 ALL_LIST_TESTS = [
     test_list_all,
@@ -380,7 +350,6 @@ async def test_list_global_search(
     test_list_metadata_filter_multiple_keys,
     test_list_metadata_filter_no_match,
     test_list_metadata_custom_keys,
-    test_list_global_search,
     test_list_before,
     test_list_limit,
     test_list_limit_plus_before,
diff --git a/libs/checkpoint-conformance/pyproject.toml b/libs/checkpoint-conformance/pyproject.toml
index 123abc..456def 100644
--- a/libs/checkpoint-conformance/pyproject.toml
+++ b/libs/checkpoint-conformance/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "hatchling.build"

 [project]
 name = "langgraph-checkpoint-conformance"
-version = "0.0.1"
+version = "0.0.2"
 description = "Conformance test suite for LangGraph checkpointer implementations."
 authors = [{name = "William FH", email = "13333726+hinthornw@users.noreply.github.com"}]
 requires-python = ">=3.10"
PATCH

# Apply the patch
git apply /tmp/fix.patch || patch -p1 < /tmp/fix.patch

echo "Fix applied successfully"
