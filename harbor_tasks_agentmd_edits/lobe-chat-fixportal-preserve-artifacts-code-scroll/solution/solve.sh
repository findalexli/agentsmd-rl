#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'isStreamingCode = isMessageGenerating' src/features/Portal/Artifacts/Body/index.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/src/features/Portal/Artifacts/Body/index.tsx b/src/features/Portal/Artifacts/Body/index.tsx
index 50c8e646726..7e0cf9c6608 100644
--- a/src/features/Portal/Artifacts/Body/index.tsx
+++ b/src/features/Portal/Artifacts/Body/index.tsx
@@ -59,14 +59,15 @@ const ArtifactsUI = memo(() => {
     }
   }, [artifactType, artifactCodeLanguage]);

-  // make sure the message and id is valid
-  if (!messageId) return;
-
   // show code when the artifact is not closed or the display mode is code or the artifact type is code
   const showCode =
     !isArtifactTagClosed ||
     displayMode === ArtifactDisplayMode.Code ||
     artifactType === ArtifactType.Code;
+  const isStreamingCode = isMessageGenerating && !isArtifactTagClosed;
+
+  // make sure the message and id is valid
+  if (!messageId) return;

   return (
     <Flexbox
@@ -78,12 +79,15 @@ const ArtifactsUI = memo(() => {
       style={{ overflow: 'hidden' }}
     >
       {showCode ? (
-        <Highlighter
-          language={language || 'txt'}
-          style={{ fontSize: 12, height: '100%', overflow: 'auto' }}
-        >
-          {artifactContent}
-        </Highlighter>
+        <Flexbox flex={1} style={{ minHeight: 0, overflow: 'auto' }}>
+          <Highlighter
+            animated={isStreamingCode}
+            language={language || 'txt'}
+            style={{ fontSize: 12, minHeight: '100%', overflow: 'visible' }}
+          >
+            {artifactContent}
+          </Highlighter>
+        </Flexbox>
       ) : (
         <Renderer content={artifactContent} type={artifactType} />
       )}
diff --git a/AGENTS.md b/AGENTS.md
index 64b0ced6195..8ea38d89156 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -45,7 +45,7 @@ lobehub/
 - New branches should be created from `canary`; PRs should target `canary`
 - Use rebase for git pull
 - Git commit messages should prefix with gitmoji
-- Git branch name format: `username/feat/feature-name`
+- Git branch name format: `feat/feature-name`
 - Use `.github/PULL_REQUEST_TEMPLATE.md` for PR descriptions

 ### Package Management

PATCH

echo "Patch applied successfully."
