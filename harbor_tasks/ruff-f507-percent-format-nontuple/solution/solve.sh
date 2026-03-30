#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
grep -q 'ResolvedPythonType' crates/ruff_linter/src/rules/pyflakes/rules/strings.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py b/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
index 692bda5e19a43..4119de68ebaa2 100644
--- a/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
+++ b/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py
@@ -25,3 +25,30 @@
 '%(k)s' % {**k}
 '%s' % [1, 2, 3]
 '%s' % {1, 2, 3}
+# F507: literal non-tuple RHS with multiple positional placeholders
+'%s %s' % 42  # F507
+'%s %s' % 3.14  # F507
+'%s %s' % "hello"  # F507
+'%s %s' % b"hello"  # F507
+'%s %s' % True  # F507
+'%s %s' % None  # F507
+'%s %s' % ...  # F507
+'%s %s' % f"hello {name}"  # F507
+# F507: ResolvedPythonType catches compound expressions with known types
+'%s %s' % -1  # F507 (unary op on int -> int)
+'%s %s' % (1 + 2)  # F507 (int + int -> int)
+'%s %s' % (not x)  # F507 (not -> bool)
+'%s %s' % ("a" + "b")  # F507 (str + str -> str)
+'%s %s' % (1 if True else 2)  # F507 (int if ... else int -> int)
+# ok: single placeholder with literal RHS
+'%s' % 42
+'%s' % "hello"
+'%s' % True
+# ok: variables/expressions could be tuples at runtime
+'%s %s' % banana
+'%s %s' % obj.attr
+'%s %s' % arr[0]
+'%s %s' % get_args()
+# ok: ternary/binop where one branch could be a tuple -> Unknown
+'%s %s' % (a if cond else b)
+'%s %s' % (a + b)
diff --git a/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs b/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
index 9df61638c40f5..4c5e1140434b2 100644
--- a/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
+++ b/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
@@ -2,6 +2,7 @@ use std::string::ToString;

 use ruff_diagnostics::Applicability;
 use ruff_python_ast::helpers::contains_effect;
+use ruff_python_semantic::analyze::type_inference::{PythonType, ResolvedPythonType};
 use rustc_hash::FxHashSet;

 use ruff_macros::{ViolationMetadata, derive_message_formats};
@@ -757,6 +758,20 @@ pub(crate) fn percent_format_positional_count_mismatch(
                 location,
             );
         }
+    } else if let ResolvedPythonType::Atom(resolved_type) = ResolvedPythonType::from(right) {
+        // If we can infer a concrete non-tuple type for the RHS, it's always
+        // a single positional argument. Variables, attribute accesses, calls,
+        // etc. resolve to `Unknown` and are not flagged because they could be
+        // tuples at runtime.
+        if resolved_type != PythonType::Tuple && summary.num_positional != 1 {
+            checker.report_diagnostic(
+                PercentFormatPositionalCountMismatch {
+                    wanted: summary.num_positional,
+                    got: 1,
+                },
+                location,
+            );
+        }
     }
 }
PATCH
