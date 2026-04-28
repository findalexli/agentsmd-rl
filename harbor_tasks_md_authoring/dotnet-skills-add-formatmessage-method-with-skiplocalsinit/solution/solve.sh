#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "var message = new string(buffer.Slice(0, written));" "skills/csharp/coding-standards/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp/coding-standards/SKILL.md b/skills/csharp/coding-standards/SKILL.md
@@ -604,6 +604,16 @@ public void FormatMessage()
     var message = new string(buffer.Slice(0, written));
 }
 
+// SkipLocalsInit with stackalloc and Span<T>
+using System.Runtime.CompilerServices;
+[SkipLocalsInit]
+public void FormatMessage()
+{
+    Span<char> buffer = stackalloc char[256];
+    var written = FormatInto(buffer);
+    var message = new string(buffer.Slice(0, written));
+}
+
 // ✅ GOOD: Memory<T> for async operations (Span can't cross await)
 public async Task<int> ReadDataAsync(
     Memory<byte> buffer,
PATCH

echo "Gold patch applied."
