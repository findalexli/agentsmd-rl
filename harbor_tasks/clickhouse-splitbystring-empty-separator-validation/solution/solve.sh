#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for empty separator validation in splitByString tokenizer
cat <<'PATCH' | git apply -
diff --git a/src/Interpreters/TokenizerFactory.cpp b/src/Interpreters/TokenizerFactory.cpp
index 308c592eec00..777086521db7 100644
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
