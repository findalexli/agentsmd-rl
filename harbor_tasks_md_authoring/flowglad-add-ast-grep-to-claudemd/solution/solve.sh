#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flowglad

# Idempotency guard
if grep -qF "ast-grep is a code tool for structural search and replace. It is like syntax-awa" "claude.md" && grep -qF "ast-grep is a code tool for structural search and replace. It is like syntax-awa" "platform/flowglad-next/claude.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/claude.md b/claude.md
@@ -11,4 +11,10 @@ Examples:
 Run the following script EVERY TIME you are in a new context:
 ```bash
 init_claude_code_flowglad_next
-```
\ No newline at end of file
+```
+
+## Resources
+### ast-grep
+Remember that you have `ast-grep` CLI at your disposal.
+
+ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.
\ No newline at end of file
diff --git a/platform/flowglad-next/claude.md b/platform/flowglad-next/claude.md
@@ -30,3 +30,8 @@ Do this in four steps:
 2. Stub tests — see [@new-test-2-planning-stubs.md](llm-prompts/new-test-2-planning-stubs.md)
 3. Prepare global setup — see [@new-test-3-before-each-setup.md](llm-prompts/new-test-3-before-each-setup.md)
 4. Implement tests — see [@new-test-4-implementation.md](llm-prompts/new-test-4-implementation.md)
+
+### ast-grep
+Remember that you have `ast-grep` CLI at your disposal.
+
+ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.
\ No newline at end of file
PATCH

echo "Gold patch applied."
