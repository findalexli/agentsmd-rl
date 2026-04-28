#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trafficserver

# Idempotency guard
if grep -qF "- In the description of classes, functions, and member variables, convey the" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -308,6 +308,38 @@ SMDebug(dbg_ctl, "Processing request for URL: %s", url);
 - UPPER_CASE for macros and constants: `HTTP_SM_SET_DEFAULT_HANDLER`
 - Private member variables have the `m_` prefix.
 
+**Doxygen Comments:**
+
+When adding doxygen comments:
+
+- `@brief` is assumed for the first sentence, so give a brief summary right
+  after `/** ` without using `@brief`.
+- In the description of classes, functions, and member variables, convey the
+  responsibility of the item being described (its role and intent), not just
+  what the code obviously does.
+- Use `@a <name>` to reference a function argument by name in prose
+  (e.g. "If @a size is zero..."). Use `@c <text>` for inline code or
+  constants (e.g. `@c true`, `@c NULL`, `@c MyEnum::VALUE`).
+- Use `@ref`, `@see`, or `@sa` to cross-reference related types or functions
+  when that helps convey how items interact.
+- Use `@param` with `[in]`, `[out]`, or `[in,out]` to indicate the
+  parameter's direction, followed by a description of its meaning.
+- Use `@return` to describe the semantics of the returned value. Don't
+  restate the type; that is obvious from the signature and rendered docs.
+- Use `@note` for non-obvious caveats and `@warning` for hazards (e.g. lock
+  ordering, lifetime, or threading constraints).
+- Use `@code` ... `@endcode` for embedded usage examples.
+- For templates, document type parameters with `@tparam`.
+
+Conventions specific to this codebase:
+
+- Every new header file should start with a `/** @file` block (see existing
+  headers in `include/` for the standard license/section layout).
+- Prefer trailing briefs for data members and enumerators, e.g.
+  `int max_conns{0}; ///< Maximum concurrent connections.`
+- Use single-line `///` briefs for short function or type docs where a full
+  `/** ... */` block would be overkill.
+
 **Modern C++ Patterns (Preferred):**
 ```cpp
 // GOOD - Modern C++20
PATCH

echo "Gold patch applied."
