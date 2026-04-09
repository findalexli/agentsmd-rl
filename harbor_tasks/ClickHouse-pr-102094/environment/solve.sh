#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already solved (idempotency)
if grep -q "the empty string cannot be used as a separator" src/Interpreters/TokenizerFactory.cpp; then
    echo "Task already solved."
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
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
diff --git a/tests/queries/0_stateless/03403_function_tokens.sql b/tests/queries/0_stateless/03403_function_tokens.sql
index bbf7ff6117c2..c1b87d983825 100644
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

echo "Task solved."
