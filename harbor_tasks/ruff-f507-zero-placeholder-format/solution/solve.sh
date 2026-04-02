#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'num_positional == 0' crates/ruff_linter/src/rules/pyflakes/rules/strings.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py b/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
index 4119de68ebaa2a..3507bde63097fb 100644
--- a/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
+++ b/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
@@ -52,3 +52,17 @@
 # ok: ternary/binop where one branch could be a tuple → Unknown
 '%s %s' % (a if cond else b)
 '%s %s' % (a + b)
+
+# F507: zero placeholders with literal non-tuple RHS
+'hello' % 42  # F507
+'' % 42  # F507
+'hello' % (1,)  # F507
+# F507: zero placeholders with variable RHS (intentional use is very unlikely)
+banana = 42
+'hello' % banana  # F507
+'' % banana  # F507
+'hello' % unknown_var  # F507
+'hello' % get_value()  # F507
+'hello' % obj.attr  # F507
+# ok: zero placeholders with empty tuple
+'hello' % ()
diff --git a/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs b/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
index 4c5e1140434b28..f9a6472fb99e76 100644
--- a/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
+++ b/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
@@ -772,6 +772,14 @@ pub(crate) fn percent_format_positional_count_mismatch(
                 location,
             );
         }
+    } else if summary.num_positional == 0 {
+        // When the format string has no placeholders, only `()` or `{}` would
+        // succeed at runtime. The chance that this is intentional is very low,
+        // so flag any RHS that isn't an empty tuple or empty dict literal.
+        checker.report_diagnostic(
+            PercentFormatPositionalCountMismatch { wanted: 0, got: 1 },
+            location,
+        );
     }
 }

diff --git a/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap b/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap
index 0989f6c0e3f745..ea2a2590efb6d6 100644
--- a/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap
+++ b/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap
@@ -1,6 +1,5 @@
 ---
 source: crates/ruff_linter/src/rules/pyflakes/mod.rs
-assertion_line: 192
 ---
 F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:5:1
@@ -187,3 +186,90 @@ F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
 43 | # ok: single placeholder with literal RHS
 44 | '%s' % 42
    |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:57:1
+   |
+56 | # F507: zero placeholders with literal non-tuple RHS
+57 | 'hello' % 42  # F507
+   | ^^^^^^^^^^^^
+58 | '' % 42  # F507
+59 | 'hello' % (1,)  # F507
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:58:1
+   |
+56 | # F507: zero placeholders with literal non-tuple RHS
+57 | 'hello' % 42  # F507
+58 | '' % 42  # F507
+   | ^^^^^^^
+59 | 'hello' % (1,)  # F507
+60 | # F507: zero placeholders with variable RHS (intentional use is very unlikely)
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:59:1
+   |
+57 | 'hello' % 42  # F507
+58 | '' % 42  # F507
+59 | 'hello' % (1,)  # F507
+   | ^^^^^^^^^^^^^^
+60 | # F507: zero placeholders with variable RHS (intentional use is very unlikely)
+61 | banana = 42
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:62:1
+   |
+60 | # F507: zero placeholders with variable RHS (intentional use is very unlikely)
+61 | banana = 42
+62 | 'hello' % banana  # F507
+   | ^^^^^^^^^^^^^^^^
+63 | '' % banana  # F507
+64 | 'hello' % unknown_var  # F507
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:63:1
+   |
+61 | banana = 42
+62 | 'hello' % banana  # F507
+63 | '' % banana  # F507
+   | ^^^^^^^^^^^
+64 | 'hello' % unknown_var  # F507
+65 | 'hello' % get_value()  # F507
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:64:1
+   |
+62 | 'hello' % banana  # F507
+63 | '' % banana  # F507
+64 | 'hello' % unknown_var  # F507
+   | ^^^^^^^^^^^^^^^^^^^^^
+65 | 'hello' % get_value()  # F507
+66 | 'hello' % obj.attr  # F507
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:65:1
+   |
+63 | '' % banana  # F507
+64 | 'hello' % unknown_var  # F507
+65 | 'hello' % get_value()  # F507
+   | ^^^^^^^^^^^^^^^^^^^^^
+66 | 'hello' % obj.attr  # F507
+67 | # ok: zero placeholders with empty tuple
+   |
+
+F507 `%`-format string has 0 placeholder(s) but 1 substitution(s)
+  --> F50x.py:66:1
+   |
+64 | 'hello' % unknown_var  # F507
+65 | 'hello' % get_value()  # F507
+66 | 'hello' % obj.attr  # F507
+   | ^^^^^^^^^^^^^^^^^^
+67 | # ok: zero placeholders with empty tuple
+68 | 'hello' % ()
+   |

PATCH
