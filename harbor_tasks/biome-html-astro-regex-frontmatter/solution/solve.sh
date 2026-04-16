#!/bin/bash
set -e

cd /workspace/biome_repo

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/crates/biome_html_parser/src/lexer/mod.rs b/crates/biome_html_parser/src/lexer/mod.rs
index 6ef828130134..51ab85f9c3e8 100644
--- a/crates/biome_html_parser/src/lexer/mod.rs
+++ b/crates/biome_html_parser/src/lexer/mod.rs
@@ -1674,15 +1674,6 @@ impl QuotesSeen {
             return;
         }

-        // Handle escape sequences: a `\` that is not itself escaped toggles the
-        // escape flag for the next character.
-        if byte == b'\\' {
-            self.escaped = !self.escaped;
-            self.prev_byte = Some(byte);
-            self.prev_non_ws_byte = Some(byte);
-            return;
-        }
-
         // If the current byte is escaped, it cannot act as a string delimiter
         // or comment opener.
         let was_escaped = self.escaped;
@@ -1746,6 +1737,15 @@ impl QuotesSeen {
             self.prev_non_ws_byte = Some(b'/');
         }

+        // Handle escape sequences: a `\` that is not itself escaped toggles the
+        // escape flag for the next character.
+        if byte == b'\\' {
+            self.escaped = !self.escaped;
+            self.prev_byte = Some(byte);
+            self.prev_non_ws_byte = Some(byte);
+            return;
+        }
+
         // Track string delimiters.
         match byte {
             b'"' | b'\'' | b'`' => {
@@ -2101,4 +2101,19 @@ const f = "something" "#;
             "regex literal containing dashes must not confuse the tracker"
         );
     }
+
+    /// A regex literal containing an escaped character followed by a quantifier
+    /// must close cleanly. This mirrors `/\d{4}/`, which previously regressed
+    /// in Astro frontmatter scanning.
+    #[test]
+    fn issue_9187_regex_with_escape_and_quantifier() {
+        let source = r"const test = /\d{4}/
+";
+        let mut quotes_seen = QuotesSeen::new();
+        track(source, &mut quotes_seen);
+        assert!(
+            quotes_seen.is_empty(),
+            "regex literal containing an escape and quantifier must close cleanly"
+        );
+    }
 }
diff --git a/.changeset/fix-astro-frontmatter-regex.md b/.changeset/fix-astro-frontmatter-regex.md
new file mode 100644
index 000000000000..04228ee36ae9
--- /dev/null
+++ b/.changeset/fix-astro-frontmatter-regex.md
@@ -0,0 +1,5 @@
+---
+"@biomejs/biome": patch
+---
+
+Fixed [#9696](https://github.com/biomejs/biome/issues/9696): Astro frontmatter now correctly parses regular expression literals like `/\d{4}/`.
diff --git a/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro b/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro
new file mode 100644
index 000000000000..e6bf797735c9
--- /dev/null
+++ b/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro
@@ -0,0 +1,5 @@
+---
+const RE = /\d{4}/
+---
+
+<div />
diff --git a/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro.snap b/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro.snap
new file mode 100644
index 000000000000..b50246d28b
--- /dev/null
+++ b/crates/biome_html_parser/tests/html_specs/ok/astro/issue_9696.astro.snap
@@ -0,0 +1,68 @@
+---
+source: crates/biome_html_parser/tests/spec_test.rs
+assertion_line: 145
+expression: snapshot
+---
+
+## Input
+
+```astro
+---
+const RE = /\d{4}/
+---
+
+<div />
+
+```
+
+
+## AST
+
+```
+HtmlRoot {
+    bom_token: missing (optional),
+    frontmatter: AstroFrontmatterElement {
+        l_fence_token: FENCE@0..3 "---" [] [],
+        content: AstroEmbeddedContent {
+            content_token: HTML_LITERAL@3..23 "const RE = /\\d{4}/\n" [Newline("\n")] [],
+        },
+        r_fence_token: FENCE@23..26 "---" [] [],
+    },
+    directive: missing (optional),
+    html: HtmlElementList [
+        HtmlSelfClosingElement {
+            l_angle_token: L_ANGLE@26..29 "<" [Newline("\n"), Newline("\n")] [],
+            name: HtmlTagName {
+                value_token: HTML_LITERAL@29..33 "div" [] [Whitespace(" ")],
+            },
+            attributes: HtmlAttributeList [],
+            slash_token: SLASH@33..34 "/" [] [],
+            r_angle_token: R_ANGLE@34..35 ">" [] [],
+        },
+    ],
+    eof_token: EOF@35..36 "" [Newline("\n")] [],
+}
+```
+
+## CST
+
+```
+0: HTML_ROOT@0..36
+  0: (empty)
+  1: ASTRO_FRONTMATTER_ELEMENT@0..26
+    0: FENCE@0..3 "---" [] []
+    1: ASTRO_EMBEDDED_CONTENT@3..23
+      0: HTML_LITERAL@3..23 "const RE = /\\d{4}/\n" [Newline("\n")] []
+    2: FENCE@23..26 "---" [] []
+  2: (empty)
+  3: HTML_ELEMENT_LIST@26..35
+    0: HTML_SELF_CLOSING_ELEMENT@26..35
+      0: L_ANGLE@26..29 "<" [Newline("\n"), Newline("\n")] []
+      1: HTML_TAG_NAME@29..33
+        0: HTML_LITERAL@29..33 "div" [] [Whitespace(" ")]
+      2: HTML_ATTRIBUTE_LIST@33..33
+      3: SLASH@33..34 "/" [] []
+      4: R_ANGLE@34..35 ">" [] []
+  4: EOF@35..36 "" [Newline("\n")] []
+
+```
PATCH

# Verify the patch applied
grep -q "issue_9187_regex_with_escape_and_quantifier" crates/biome_html_parser/src/lexer/mod.rs && echo "Patch applied successfully"