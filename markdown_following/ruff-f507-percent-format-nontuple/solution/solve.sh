#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'ResolvedPythonType' crates/ruff_linter/src/rules/pyflakes/rules/strings.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    cargo build --bin ruff 2>&1
    exit 0
fi

# Apply the main code and fixture patch
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
+        // etc. resolve to \`Unknown\` and are not flagged because they could be
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

# Update the snapshot file with the expected new F507 errors
cat > crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap <<'SNAPSHOT'
---
source: crates/ruff_linter/src/rules/pyflakes/mod.rs
---
F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
 --> F50x.py:5:1
  |
3 | '%(foo)s %s' % {'foo': 'bar'}  # F506
4 | '%j' % (1,)  # F509
5 | '%s %s' % (1,)  # F507
  | ^^^^^^^^^^^^^^
6 | '%s %s' % (1, 2, 3)  # F507
7 | '%(bar)s' % {}  # F505
  |

F507 `%`-format string has 2 placeholder(s) but 3 substitution(s)
 --> F50x.py:6:1
  |
4 | '%j' % (1,)  # F509
5 | '%s %s' % (1,)  # F507
6 | '%s %s' % (1, 2, 3)  # F507
  | ^^^^^^^^^^^^^^^^^^^
7 | '%(bar)s' % {}  # F505
8 | '%(bar)s' % {'bar': 1, 'baz': 2}  # F504
  |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:10:1
   |
 8 | '%(bar)s' % {'bar': 1, 'baz': 2}  # F504
 9 | '%(bar)s' % (1, 2, 3)  # F502
10 | '%s %s' % {'k': 'v'}  # F503
   | ^^^^^^^^^^^^^^^^^^^^
11 | '%(bar)*s' % {'bar': 'baz'}  # F506, F508
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:22:1
   |
20 | # ok *args and **kwargs
21 | a = []
22 | '%s %s' % [*a]
   | ^^^^^^^^^^^^^^
23 | '%s %s' % (*a,)
24 | k = {}
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:29:1
   |
27 | '%s' % {1, 2, 3}
28 | # F507: literal non-tuple RHS with multiple positional placeholders
29 | '%s %s' % 42  # F507
   | ^^^^^^^^^^^^
30 | '%s %s' % 3.14  # F507
31 | '%s %s' % "hello"  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:30:1
   |
28 | # F507: literal non-tuple RHS with multiple positional placeholders
29 | '%s %s' % 42  # F507
30 | '%s %s' % 3.14  # F507
   | ^^^^^^^^^^^^^^
31 | '%s %s' % "hello"  # F507
32 | '%s %s' % b"hello"  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:31:1
   |
29 | '%s %s' % 42  # F507
30 | '%s %s' % 3.14  # F507
31 | '%s %s' % "hello"  # F507
   | ^^^^^^^^^^^^^^^^^
32 | '%s %s' % b"hello"  # F507
33 | '%s %s' % True  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:32:1
   |
30 | '%s %s' % 3.14  # F507
31 | '%s %s' % "hello"  # F507
32 | '%s %s' % b"hello"  # F507
   | ^^^^^^^^^^^^^^^^^^
33 | '%s %s' % True  # F507
34 | '%s %s' % None  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:33:1
   |
31 | '%s %s' % "hello"  # F507
32 | '%s %s' % b"hello"  # F507
33 | '%s %s' % True  # F507
   | ^^^^^^^^^^^^^^
34 | '%s %s' % None  # F507
35 | '%s %s' % ...  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:34:1
   |
32 | '%s %s' % b"hello"  # F507
33 | '%s %s' % True  # F507
34 | '%s %s' % None  # F507
   | ^^^^^^^^^^^^^^
35 | '%s %s' % ...  # F507
36 | '%s %s' % f"hello {name}"  # F507
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:35:1
   |
33 | '%s %s' % True  # F507
34 | '%s %s' % None  # F507
35 | '%s %s' % ...  # F507
   | ^^^^^^^^^^^^^
36 | '%s %s' % f"hello {name}"  # F507
37 | # F507: ResolvedPythonType catches compound expressions with known types
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:36:1
   |
34 | '%s %s' % None  # F507
35 | '%s %s' % ...  # F507
36 | '%s %s' % f"hello {name}"  # F507
   | ^^^^^^^^^^^^^^^^^^^^^^^^^
37 | # F507: ResolvedPythonType catches compound expressions with known types
38 | '%s %s' % -1  # F507 (unary op on int -> int)
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:38:1
   |
36 | '%s %s' % f"hello {name}"  # F507
37 | # F507: ResolvedPythonType catches compound expressions with known types
38 | '%s %s' % -1  # F507 (unary op on int -> int)
   | ^^^^^^^^^^^^
39 | '%s %s' % (1 + 2)  # F507 (int + int -> int)
40 | '%s %s' % (not x)  # F507 (not -> bool)
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:39:1
   |
37 | # F507: ResolvedPythonType catches compound expressions with known types
38 | '%s %s' % -1  # F507 (unary op on int -> int)
39 | '%s %s' % (1 + 2)  # F507 (int + int -> int)
   | ^^^^^^^^^^^^^^^^^
40 | '%s %s' % (not x)  # F507 (not -> bool)
41 | '%s %s' % ("a" + "b")  # F507 (str + str -> str)
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:40:1
   |
38 | '%s %s' % -1  # F507 (unary op on int -> int)
39 | '%s %s' % (1 + 2)  # F507 (int + int -> int)
40 | '%s %s' % (not x)  # F507 (not -> bool)
   | ^^^^^^^^^^^^^^^^^
41 | '%s %s' % ("a" + "b")  # F507 (str + str -> str)
42 | '%s %s' % (1 if True else 2)  # F507 (int if ... else int -> int)
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:41:1
   |
39 | '%s %s' % (1 + 2)  # F507 (int + int -> int)
40 | '%s %s' % (not x)  # F507 (not -> bool)
41 | '%s %s' % ("a" + "b")  # F507 (str + str -> str)
   | ^^^^^^^^^^^^^^^^^^^^^
42 | '%s %s' % (1 if True else 2)  # F507 (int if ... else int -> int)
43 | # ok: single placeholder with literal RHS
   |

F507 `%`-format string has 2 placeholder(s) but 1 substitution(s)
  --> F50x.py:42:1
   |
40 | '%s %s' % (not x)  # F507 (not -> bool)
41 | '%s %s' % ("a" + "b")  # F507 (str + str -> str)
42 | '%s %s' % (1 if True else 2)  # F507 (int if ... else int -> int)
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
43 | # ok: single placeholder with literal RHS
44 | '%s' % 42
   |
SNAPSHOT

# Rebuild ruff with the fix applied (incremental — only strings.rs changed).
cargo build --bin ruff
