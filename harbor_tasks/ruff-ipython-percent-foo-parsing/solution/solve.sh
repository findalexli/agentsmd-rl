#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
grep -q 'IpyEscapeLexContext' crates/ruff_python_parser/src/lexer.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ruff_python_parser/src/lexer.rs b/crates/ruff_python_parser/src/lexer.rs
index 4c9ab6b464d05..b78f8bf55baf1 100644
--- a/crates/ruff_python_parser/src/lexer.rs
+++ b/crates/ruff_python_parser/src/lexer.rs
@@ -434,7 +434,10 @@ impl<'src> Lexer<'src> {
                     && self.nesting == 0 =>
             {
                 // SAFETY: Safe because `c` has been matched against one of the possible escape command token
-                self.lex_ipython_escape_command(IpyEscapeKind::try_from(c).unwrap())
+                self.lex_ipython_escape_command(
+                    IpyEscapeKind::try_from(c).unwrap(),
+                    IpyEscapeLexContext::Assignment,
+                )
             }

             c @ ('%' | '!' | '?' | '/' | ';' | ',')
@@ -448,7 +451,7 @@ impl<'src> Lexer<'src> {
                     IpyEscapeKind::try_from(c).unwrap()
                 };

-                self.lex_ipython_escape_command(kind)
+                self.lex_ipython_escape_command(kind, IpyEscapeLexContext::LogicalLineStart)
             }

             '?' if self.mode == Mode::Ipython => TokenKind::Question,
@@ -1262,7 +1265,11 @@ impl<'src> Lexer<'src> {
     }

     /// Lex a single IPython escape command.
-    fn lex_ipython_escape_command(&mut self, escape_kind: IpyEscapeKind) -> TokenKind {
+    fn lex_ipython_escape_command(
+        &mut self,
+        escape_kind: IpyEscapeKind,
+        context: IpyEscapeLexContext,
+    ) -> TokenKind {
         let mut value = String::new();

         loop {
@@ -1310,6 +1317,27 @@ impl<'src> Lexer<'src> {
                         question_count += 1;
                     }

+                    // Help end tokens (`?` / `??`) are only valid in certain contexts
+                    // (e.g., not within f-strings or parenthesized expressions), and only
+                    // for escape kinds that IPython recognizes as supporting a trailing `?`
+                    // (i.e., `%`, `%%`, `?`, and `??`). For other escape kinds like `!` or
+                    // `/`, the `?` is just part of the command value.
+                    if !context.allows_help_end()
+                        || !matches!(
+                            escape_kind,
+                            IpyEscapeKind::Magic
+                                | IpyEscapeKind::Magic2
+                                | IpyEscapeKind::Help
+                                | IpyEscapeKind::Help2
+                        )
+                    {
+                        value.reserve(question_count as usize);
+                        for _ in 0..question_count {
+                            value.push('?');
+                        }
+                        continue;
+                    }
+
                     // The original implementation in the IPython codebase is based on regex which
                     // means that it's strict in the sense that it won't recognize a help end escape:
                     //   * If there's any whitespace before the escape token (e.g. `%foo ?`)
@@ -1748,6 +1776,18 @@ impl State {
     }
 }

+#[derive(Copy, Clone, Debug)]
+enum IpyEscapeLexContext {
+    Assignment,
+    LogicalLineStart,
+}
+
+impl IpyEscapeLexContext {
+    const fn allows_help_end(self) -> bool {
+        matches!(self, Self::LogicalLineStart)
+    }
+}
+
 #[derive(Copy, Clone, Debug)]
 enum Radix {
     Binary,
@@ -2108,7 +2148,9 @@ pwd = !pwd
 foo = %timeit a = b
 bar = %timeit a % 3
 baz = %matplotlib \
-        inline"
+        inline
+qux = %foo?
+quux = !pwd?"
             .trim();
         assert_snapshot!(lex_jupyter_source(source));
     }
diff --git a/crates/ruff_python_parser/src/parser/tests.rs b/crates/ruff_python_parser/src/parser/tests.rs
index fb1927775479e..20cc04c7011cf 100644
--- a/crates/ruff_python_parser/src/parser/tests.rs
+++ b/crates/ruff_python_parser/src/parser/tests.rs
@@ -115,6 +115,8 @@ p1 = !pwd
 p2: str = !pwd
 foo = %foo \
     bar
+bar = %foo?
+baz = !pwd?

 % foo
 foo = %foo  # comment

PATCH
