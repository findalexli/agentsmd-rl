#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'think_end_id=42)' test/registered/unit/constrained/test_base_grammar_backend.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/test/registered/unit/constrained/test_base_grammar_backend.py b/test/registered/unit/constrained/test_base_grammar_backend.py
index d914c87628f0..1f3a7a4f9382 100644
--- a/test/registered/unit/constrained/test_base_grammar_backend.py
+++ b/test/registered/unit/constrained/test_base_grammar_backend.py
@@ -318,7 +318,6 @@ def test_custom_backend_skips_reasoner_wrapping(self):

         args = self._make_server_args("inner_r", reasoning_parser="deepseek")
         tokenizer = MagicMock()
-        tokenizer.think_end_id = 42

         result = create_grammar_backend(args, tokenizer, 32000)
         # Custom backends return early, no reasoner wrapping applied
@@ -386,22 +385,21 @@ def test_reasoner_wrapping_on_builtin_backend(self, mock_outlines_cls):
         mock_outlines_cls.return_value = mock_backend
         args = self._make_server_args("outlines", reasoning_parser="deepseek")
         tokenizer = MagicMock()
-        tokenizer.think_end_id = 42

-        result = create_grammar_backend(args, tokenizer, 32000)
+        result = create_grammar_backend(args, tokenizer, 32000, think_end_id=42)
         self.assertIsInstance(result, ReasonerGrammarBackend)
         self.assertEqual(result.think_end_id, 42)
         self.assertIs(result.grammar_backend, mock_backend)

     @patch("sglang.srt.constrained.outlines_backend.OutlinesGrammarBackend")
     def test_no_reasoner_wrapping_without_think_end_id(self, mock_outlines_cls):
-        """Without think_end_id on tokenizer, no reasoner wrapping."""
+        """Without think_end_id passed in, no reasoner wrapping."""
         mock_backend = MagicMock(spec=BaseGrammarBackend)
         mock_outlines_cls.return_value = mock_backend
         args = self._make_server_args("outlines", reasoning_parser="deepseek")
         tokenizer = MagicMock(spec=[])  # No think_end_id attribute

-        result = create_grammar_backend(args, tokenizer, 32000)
+        result = create_grammar_backend(args, tokenizer, 32000, think_end_id=None)
         self.assertIs(result, mock_backend)

     @patch("sglang.srt.constrained.outlines_backend.OutlinesGrammarBackend")
@@ -411,9 +409,8 @@ def test_no_reasoner_wrapping_without_reasoning_parser(self, mock_outlines_cls):
         mock_outlines_cls.return_value = mock_backend
         args = self._make_server_args("outlines", reasoning_parser=None)
         tokenizer = MagicMock()
-        tokenizer.think_end_id = 42

-        result = create_grammar_backend(args, tokenizer, 32000)
+        result = create_grammar_backend(args, tokenizer, 32000, think_end_id=42)
         self.assertIs(result, mock_backend)

     @patch("sglang.srt.constrained.xgrammar_backend.XGrammarGrammarBackend")

PATCH

echo "Patch applied successfully."
