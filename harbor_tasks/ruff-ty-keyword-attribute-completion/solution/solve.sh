#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if is_name_like_token already exists, skip
if grep -q 'fn is_name_like_token' crates/ty_ide/src/completion.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_ide/src/completion.rs b/crates/ty_ide/src/completion.rs
index 1c8761df82ca0..b01564d04611e 100644
--- a/crates/ty_ide/src/completion.rs
+++ b/crates/ty_ide/src/completion.rs
@@ -724,7 +724,7 @@ impl<'m> ContextCursor<'m> {
         // keywords), but it indicates that the user has typed
         // `import`. This is useful to know in some contexts. And this
         // applies also to the other keywords.
-        if !matches!(last.kind(), TokenKind::Name) && !last.kind().is_keyword() {
+        if !is_name_like_token(last) {
             return None;
         }
         // This one's weird, but if the cursor is beyond
@@ -1717,7 +1717,6 @@ impl<'t> CompletionTargetTokens<'t> {
     /// Look for the best matching token pattern at the given offset.
     fn find(cursor: &ContextCursor<'t>) -> Option<CompletionTargetTokens<'t>> {
         static OBJECT_DOT_EMPTY: [TokenKind; 1] = [TokenKind::Dot];
-        static OBJECT_DOT_NON_EMPTY: [TokenKind; 2] = [TokenKind::Dot, TokenKind::Name];

         let before = cursor.tokens_before;
         Some(
@@ -1732,10 +1731,10 @@ impl<'t> CompletionTargetTokens<'t> {
                     object,
                     attribute: None,
                 }
-            } else if let Some([_dot, attribute]) =
-                token_suffix_by_kinds(before, OBJECT_DOT_NON_EMPTY)
+            } else if let [.., object, dot, attribute] = before
+                && dot.kind() == TokenKind::Dot
+                && is_name_like_token(attribute)
             {
-                let object = before[..before.len() - 2].last()?;
                 CompletionTargetTokens::PossibleObjectDot {
                     object,
                     attribute: Some(attribute),
@@ -2439,6 +2438,15 @@ fn token_suffix_by_kinds<const N: usize>(
     }))
 }

+/// Returns `true` if the token is a `Name` or a keyword.
+///
+/// Keywords are included because the lexer will lex a partially-typed
+/// attribute name as a keyword token when it happens to match one
+/// (e.g., `{1}.is` lexes `is` as `TokenKind::Is` rather than `TokenKind::Name`).
+fn is_name_like_token(token: &Token) -> bool {
+    matches!(token.kind(), TokenKind::Name) || token.kind().is_keyword()
+}
+
 /// Returns the "kind" of a completion using just its type information.
 ///
 /// This is meant to be a very general classification of this completion.
@@ -4778,6 +4786,20 @@ Re<CURSOR>
         builder.build().contains("add").not_contains("values");
     }

+    #[test]
+    fn attribute_access_set_keyword_prefix() {
+        let builder = completion_test_builder(
+            "\
+{1}.is<CURSOR>
+",
+        );
+
+        builder
+            .build()
+            .contains("isdisjoint")
+            .not_contains("isinstance");
+    }
+
     #[test]
     fn attribute_parens() {
         let builder = completion_test_builder(

PATCH

echo "Patch applied successfully."
