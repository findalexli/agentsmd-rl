#!/usr/bin/env bash
set -euo pipefail

TARGET="/repo/src/transformers/tokenization_utils_tokenizers.py"

# Idempotency check: if from_str is already used in the elif branch, patch is applied
if grep -q 'minimal_tokenizer_json' "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git -C /repo apply - <<'PATCH'
diff --git a/src/transformers/tokenization_utils_tokenizers.py b/src/transformers/tokenization_utils_tokenizers.py
index f056b4d54f2d..afca202127be 100644
--- a/src/transformers/tokenization_utils_tokenizers.py
+++ b/src/transformers/tokenization_utils_tokenizers.py
@@ -118,7 +118,32 @@ def convert_to_native_format(cls, trust_remote_code=False, **kwargs):
         elif fast_tokenizer_file is not None and os.path.isfile(fast_tokenizer_file):
             # we extract vocab/merges and pass decoder/pre_tokenizer/post_processor
             # from the file so the reconstructed tokenizer matches the tokenizer.json
-            tok_from_file = TokenizerFast.from_file(fast_tokenizer_file)
+            with open(fast_tokenizer_file, encoding="utf-8") as tokenizer_handle:
+                tokenizer_json = json.load(tokenizer_handle)
+
+            # Build a minimal tokenizer (empty vocab/merges) to cheaply extract post_processor,
+            # padding and truncation as Rust objects — avoids parsing the full vocab via from_file.
+            # This optimization applies to BPE, WordPiece, and WordLevel only:
+            # - Unigram (SentencePiece) requires a non-empty vocab to initialize correctly in Rust
+            #   (e.g. AlbertTokenizer, CamembertTokenizer, LlamaTokenizer, T5Tokenizer); passing an
+            #   empty vocab causes "Unable to load vocab EmptyVocabulary". TODO: investigate if keeping
+            #   just the UNK token is sufficient to make Unigram work with a minimal vocab.
+            # - Older tokenizer.json formats (e.g. XLNetTokenizer, DistilBertTokenizer) omit the
+            #   "type" field in the "model" section, so we cannot determine the model type from JSON.
+            # In both cases we fall back to the original from_file path (no performance improvement).
+            model_type = tokenizer_json.get("model", {}).get("type")
+            if model_type not in (None, "Unigram"):
+                minimal_tokenizer_json = dict(tokenizer_json)
+                minimal_model = dict(tokenizer_json["model"])
+                minimal_model["vocab"] = {}
+                if model_type == "BPE":
+                    minimal_model["merges"] = []
+                minimal_tokenizer_json["model"] = minimal_model
+                minimal_tokenizer_json["added_tokens"] = []
+                tok_from_file = TokenizerFast.from_str(json.dumps(minimal_tokenizer_json))
+            else:
+                tok_from_file = TokenizerFast.from_file(fast_tokenizer_file)
+
             local_kwargs["post_processor"] = tok_from_file.post_processor
             local_kwargs["tokenizer_padding"] = tok_from_file.padding
             local_kwargs["tokenizer_truncation"] = tok_from_file.truncation
@@ -130,9 +155,6 @@ def convert_to_native_format(cls, trust_remote_code=False, **kwargs):
             if tok_from_file.padding is not None:
                 local_kwargs["_json_padding"] = tok_from_file.padding

-            with open(fast_tokenizer_file, encoding="utf-8") as tokenizer_handle:
-                tokenizer_json = json.load(tokenizer_handle)
-
             # Extract precompiled SentencePiece charsmap from tokenizer.json normalizer
             # when present (e.g. T5 tokenizers converted with SentencePiece >= 2.x).
             normalizer_config = tokenizer_json.get("normalizer")

PATCH

echo "Patch applied successfully."
