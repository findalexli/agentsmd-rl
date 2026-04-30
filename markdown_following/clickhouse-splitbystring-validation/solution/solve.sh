#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already applied
if git diff HEAD | grep -q "the empty string cannot be used as a separator"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/src/Interpreters/TokenizerFactory.cpp b/src/Interpreters/TokenizerFactory.cpp
index df04063759f4..b94ba4684818 100644
--- a/src/Interpreters/TokenizerFactory.cpp
+++ b/src/Interpreters/TokenizerFactory.cpp
@@ -190,12 +190,20 @@ static void registerTokenizers(TokenizerFactory & factory)
         auto array = castAs<Array>(args[0], "separators");
         std::vector<String> values;
         for (const auto & value : array)
-            values.emplace_back(castAs<String>(value, "separator"));
+        {
+            const auto & value_as_string = castAs<String>(value, "separator");
+            if (value_as_string.empty())
+                throw Exception(
+                    ErrorCodes::BAD_ARGUMENTS,
+                    "Incorrect parameter of tokenizer '{}': the empty string cannot be used as a separator",
+                    SplitByStringTokenizer::getExternalName());
+            values.emplace_back(value_as_string);
+        }

         if (values.empty())
             throw Exception(
                 ErrorCodes::BAD_ARGUMENTS,
-                "Incorrect parameter of tokenizer '{}': separators cannot be empty",
+                "Incorrect parameter of tokenizer '{}': the separators argument cannot be empty",
                 SplitByStringTokenizer::getExternalName());

         return std::make_unique<SplitByStringTokenizer>(values);
PATCH

echo "Patch applied successfully"
