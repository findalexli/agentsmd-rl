#!/bin/bash
set -e

cd /workspace/ClickHouse

# Idempotency check: if fix already applied, exit
if grep -q "the empty string cannot be used as a separator" src/Interpreters/TokenizerFactory.cpp; then
    echo "Fix already applied, exiting"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
From 94b91bf8dcfb0c0be5c97026fcb019229001c772 Mon Sep 17 00:00:00 2001
Subject: [PATCH] Extend argument validation in `splitByString` tokenizer

---
 src/Interpreters/TokenizerFactory.cpp             | 10 +++++++++-
 .../0_stateless/03403_function_tokens.sql           |  2 ++
 2 files changed, 11 insertions(+), 1 deletion(-)

diff --git a/src/Interpreters/TokenizerFactory.cpp b/src/Interpreters/TokenizerFactory.cpp
index 63315231f4bb..408a1eec748d 100644
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

echo "Fix applied successfully"
