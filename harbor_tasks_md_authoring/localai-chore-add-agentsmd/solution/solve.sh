#!/usr/bin/env bash
set -euo pipefail

cd /workspace/localai

# Idempotency guard
if grep -qF "Building and testing the project depends on the components involved and the plat" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,47 @@
+# Build and testing
+
+Building and testing the project depends on the components involved and the platform where development is taking place. Due to the amount of context required it's usually best not to try building or testing the project unless the user requests it. If you must build the project then inspect the Makefile in the project root and the Makefiles of any backends that are effected by changes you are making. In addition the workflows in .github/workflows can be used as a reference when it is unclear how to build or test a component. The primary Makefile contains targets for building inside or outside Docker, if the user has not previously specified a preference then ask which they would like to use.
+
+# Coding style
+
+- The project has the following .editorconfig
+
+```
+root = true
+
+[*]
+indent_style = space
+indent_size = 2
+end_of_line = lf
+charset = utf-8
+trim_trailing_whitespace = true
+insert_final_newline = true
+
+[*.go]
+indent_style = tab
+
+[Makefile]
+indent_style = tab
+
+[*.proto]
+indent_size = 2
+
+[*.py]
+indent_size = 4
+
+[*.js]
+indent_size = 2
+
+[*.yaml]
+indent_size = 2
+
+[*.md]
+trim_trailing_whitespace = false
+```
+
+- Use comments sparingly to explain why code does something, not what it does. Comments are there to add context that would be difficult to deduce from reading the code.
+- Prefer modern Go e.g. use `any` not `interface{}`
+
+# Logging
+
+Use `github.com/mudler/xlog` for logging which has the same API as slog.
PATCH

echo "Gold patch applied."
