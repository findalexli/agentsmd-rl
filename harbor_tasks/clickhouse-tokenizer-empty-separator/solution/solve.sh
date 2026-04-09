#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if patch already applied (idempotency)
if grep -q "the empty string cannot be used as a separator" src/Interpreters/TokenizerFactory.cpp; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
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
diff --git a/tests/queries/0_stateless/03403_function_tokens.sql b/tests/queries/0_stateless/03403_function_tokens.sql
index 2d2dbde37c9b..d1d0c0608d3b1 100644
--- a/tests/queries/0_stateless/03403_function_tokens.sql
+++ b/tests/queries/0_stateless/03403_function_tokens.sql
@@ -28,6 +28,8 @@ SELECT tokens('a', 'splitByString', toFixedString('c', 1)); -- { serverError ILL
 SELECT tokens('a', 'splitByString', materialize(['c'])); -- { serverError ILLEGAL_COLUMN }
 SELECT tokens('a', 'splitByString', [1, 2]); -- { serverError BAD_ARGUMENTS }
 SELECT tokens('  a  bc d', 'splitByString', []); -- { serverError BAD_ARGUMENTS }
+SELECT tokens('  a  bc d', 'splitByString', ['']); -- { serverError BAD_ARGUMENTS }
+SELECT tokens('  a  bc d', 'splitByString', [' ', '']); -- { serverError BAD_ARGUMENTS }


 SELECT 'Default tokenizer';
PATCH

echo "Patch applied successfully"
