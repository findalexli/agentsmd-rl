#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "// See: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attri" "skills/csharp/coding-standards/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp/coding-standards/SKILL.md b/skills/csharp/coding-standards/SKILL.md
@@ -604,7 +604,14 @@ public void FormatMessage()
     var message = new string(buffer.Slice(0, written));
 }
 
-// SkipLocalsInit with stackalloc and Span<T>
+// SkipLocalsInit with stackalloc - skips zero-initialization for performance
+// By default, .NET zero-initializes all locals (.locals init flag). This can have
+// measurable overhead with stackalloc. Use [SkipLocalsInit] when:
+//   - You write to the buffer before reading (like FormatInto below)
+//   - Profiling shows zero-init as a bottleneck
+// ⚠️ WARNING: Reading before writing returns garbage data (see docs example)
+// Requires: <AllowUnsafeBlocks>true</AllowUnsafeBlocks> in .csproj
+// See: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/general#skiplocalsinit-attribute
 using System.Runtime.CompilerServices;
 [SkipLocalsInit]
 public void FormatMessage()
PATCH

echo "Gold patch applied."
