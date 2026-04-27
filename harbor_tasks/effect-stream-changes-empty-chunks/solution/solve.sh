#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

if grep -q 'if (Chunk.isEmpty(newChunk)) return writer(newLast)' packages/effect/src/internal/stream.ts; then
  echo "patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/shiny-bottles-tap.md b/.changeset/shiny-bottles-tap.md
new file mode 100644
index 00000000000..a112ce5008c
--- /dev/null
+++ b/.changeset/shiny-bottles-tap.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+prevent Stream.changes from writing empty chunks
diff --git a/packages/effect/src/internal/stream.ts b/packages/effect/src/internal/stream.ts
index 998ff55a484..8c2d46d3d8b 100644
--- a/packages/effect/src/internal/stream.ts
+++ b/packages/effect/src/internal/stream.ts
@@ -1397,6 +1397,7 @@ export const changesWith = dual<
             return [Option.some(output), pipe(outputs, Chunk.append(output))] as const
           }
         )
+        if (Chunk.isEmpty(newChunk)) return writer(newLast)
         return core.flatMap(
           core.write(newChunk),
           () => writer(newLast)
PATCH

git add -A
git -c user.email=solve@local -c user.name=solve commit -m "apply gold patch" >/dev/null

echo "patch applied"
grep -n 'if (Chunk.isEmpty(newChunk)) return writer(newLast)' packages/effect/src/internal/stream.ts
ls .changeset/shiny-bottles-tap.md
