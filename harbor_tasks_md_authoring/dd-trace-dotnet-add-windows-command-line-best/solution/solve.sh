#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dd-trace-dotnet

# Idempotency guard
if grep -qF "On Windows, redirecting to `nul` can create a literal file named \"nul\" instead o" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -241,6 +241,39 @@ tracer/src/Datadog.Trace
 **C/C++ style:**
 - See `.clang-format`; keep consistent naming
 
+## Windows Command Line Best Practices
+
+**CRITICAL: Avoid `>nul` and `2>nul` redirections on Windows**
+
+On Windows, redirecting to `nul` can create a literal file named "nul" instead of redirecting to the NUL device. These files are extremely difficult to delete and cause repository issues.
+
+**Problem commands:**
+```cmd
+findstr /s /i "pattern" "*.cpp" "*.h" 2>nul
+command 2>nul | head -20
+any-command >nul
+```
+
+**Safe alternatives:**
+1. **Don't suppress errors** - Let error output show naturally
+2. **Use full device path**: `2>\\.\NUL` (works reliably but verbose)
+3. **Use PowerShell** for cross-platform compatibility where applicable
+4. **Prefer dedicated tools** over piped bash commands (use Grep, Glob, Read tools instead)
+
+**Examples of safe patterns:**
+```cmd
+# Bad: Creates nul file
+findstr /s /i "DD_TRACE" "*.cpp" 2>nul
+
+# Good: Let errors show
+findstr /s /i "DD_TRACE" "*.cpp"
+
+# Good: Use full device path if suppression is essential
+findstr /s /i "DD_TRACE" "*.cpp" 2>\\.\NUL
+```
+
+**Reference:** See https://github.com/anthropics/claude-code/issues/4928 for details on this Windows limitation.
+
 ## Logging Guidelines
 
 Use clear, customer-facing terminology in log messages to avoid confusion. `Profiler` is ambiguous—it can refer to the .NET profiling APIs we use internally or the Continuous Profiler product.
@@ -350,4 +383,4 @@ Common acronyms used in this repository:
 - **RCM** — Remote Configuration Management
 - **RID** — Runtime Identifier
 - **TFM** — Target Framework Moniker
-- **WAF** — Web Application Firewall
+- **WAF** — Web Application Firewall
\ No newline at end of file
PATCH

echo "Gold patch applied."
