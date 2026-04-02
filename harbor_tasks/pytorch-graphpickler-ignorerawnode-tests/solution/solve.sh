#!/usr/bin/env bash
set -euo pipefail

TARGET="/workspace/pytorch/test/fx/test_graph_pickler.py"

# Idempotency: check if TestIgnoreRawNode already exists
if grep -q "class TestIgnoreRawNode" "$TARGET" 2>/dev/null; then
    echo "solve.sh: patch already applied"
    exit 0
fi

cd /workspace/pytorch
git apply - <<'PATCH'
diff --git a/test/fx/test_graph_pickler.py b/test/fx/test_graph_pickler.py
index 4ea99bb4138c1..35c55b1d7d880 100644
--- a/test/fx/test_graph_pickler.py
+++ b/test/fx/test_graph_pickler.py
@@ -873,6 +873,60 @@ def forward(self, x):
         self.assertIs(state["type"], torch.Tensor)


+@unittest.skipUnless(HAS_DILL, "dill not available")
+class TestIgnoreRawNode(TestCase):
+    """Tests for the ignore_raw_node option in GraphPickler.Options."""
+
+    def setUp(self):
+        super().setUp()
+        from torch.fx._graph_pickler import GraphPickler, Options
+        from torch._subclasses.fake_tensor import FakeTensorMode
+        from torch.fx.experimental.symbolic_shapes import ShapeEnv
+
+        self.GraphPickler = GraphPickler
+        self.Options = Options
+        self.fake_mode = FakeTensorMode(shape_env=ShapeEnv())
+
+    def _make_graph_with_raw_node_in_meta(self):
+        """Return a graph module whose first call_function node has a raw
+        torch.fx.Node stored in its metadata under the key 'raw_ref'."""
+
+        class M(torch.nn.Module):
+            def forward(self, x):
+                return x + 1
+
+        gm = symbolic_trace(M())
+        call_node = next(
+            (n for n in gm.graph.nodes if n.op == "call_function"), None
+        )
+        self.assertIsNotNone(call_node)
+        # Store a raw Node reference in meta – this is the problematic case.
+        call_node.meta["raw_ref"] = call_node
+        return gm
+
+    def test_raw_node_in_meta_raises_by_default(self):
+        """Pickling should raise AssertionError when a raw Node is in metadata
+        and ignore_raw_node is False (the default)."""
+        gm = self._make_graph_with_raw_node_in_meta()
+        with self.assertRaises(AssertionError) as cm:
+            self.GraphPickler.dumps(gm)
+        self.assertIn("raw Node", str(cm.exception))
+
+    def test_raw_node_in_meta_with_ignore_raw_node(self):
+        """With ignore_raw_node=True, pickling should succeed and the raw Node
+        should be replaced with None after round-trip deserialization."""
+        gm = self._make_graph_with_raw_node_in_meta()
+        options = self.Options(ignore_raw_node=True)
+        data = self.GraphPickler.dumps(gm, options)
+        restored = self.GraphPickler.loads(data, self.fake_mode)
+        self.assertIsInstance(restored, torch.fx.GraphModule)
+        call_node = next(
+            (n for n in restored.graph.nodes if n.op == "call_function"), None
+        )
+        self.assertIsNotNone(call_node)
+        self.assertIsNone(call_node.meta.get("raw_ref"))
+
+
 if __name__ == "__main__":
     from torch.testing._internal.common_utils import run_tests

PATCH

echo "solve.sh: patch applied successfully"
