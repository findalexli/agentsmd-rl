#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "// Hybrid buffer pattern for transient UTF-8 work. See caveats of SkipLocalsInit" "skills/csharp/coding-standards/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp/coding-standards/SKILL.md b/skills/csharp/coding-standards/SKILL.md
@@ -665,6 +665,35 @@ public async Task ProcessLargeFileAsync(
     }
 }
 
+// Hybrid buffer pattern for transient UTF-8 work. See caveats of SkipLocalsInit in the corresponding section.
+
+[SkipLocalsInit]
+static short GenerateHashCode(string? key)
+{
+    if (key is null) return 0;
+
+    const int StackLimit = 256;
+
+    var enc = Encoding.UTF8;
+    var max = enc.GetMaxByteCount(key.Length);
+
+    byte[]? rented = null;
+    Span<byte> buf = max <= StackLimit
+        ? stackalloc byte[StackLimit]
+        : (rented = ArrayPool<byte>.Shared.Rent(max));
+
+    try
+    {
+        var written = enc.GetBytes(key.AsSpan(), buf);
+        ComputeHash(buf[..written], out var h1, out var h2);
+        return unchecked((short)(h1 ^ h2));
+    }
+    finally
+    {
+        if (rented is not null) ArrayPool<byte>.Shared.Return(rented);
+    }
+}
+
 // ✅ GOOD: Span-based parsing without substring allocations
 public static (string Protocol, string Host, int Port) ParseUrl(ReadOnlySpan<char> url)
 {
PATCH

echo "Gold patch applied."
