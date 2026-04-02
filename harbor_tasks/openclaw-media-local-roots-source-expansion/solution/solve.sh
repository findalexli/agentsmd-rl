#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency check: if appendLocalMediaParentRoots already ignores mediaSources, skip
if grep -q '_mediaSources.*readonly string' src/media/local-roots.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/agents/tools/media-tool-shared.ts b/src/agents/tools/media-tool-shared.ts
index 777499bce9ee..6b65c595b5e1 100644
--- a/src/agents/tools/media-tool-shared.ts
+++ b/src/agents/tools/media-tool-shared.ts
@@ -1,6 +1,5 @@
 import { type Api, type Model } from "@mariozechner/pi-ai";
 import type { OpenClawConfig } from "../../config/config.js";
-import { appendLocalMediaParentRoots } from "../../media/local-roots.js";
 import { getDefaultLocalRoots } from "../../media/web-media.js";
 import type { ImageModelConfig } from "./image-tool.helpers.js";
 import type { ToolModelConfig } from "./model-config.helpers.js";
@@ -56,15 +55,14 @@ function applyAgentDefaultModelConfig(
 export function resolveMediaToolLocalRoots(
   workspaceDirRaw: string | undefined,
   options?: { workspaceOnly?: boolean },
-  mediaSources?: readonly string[],
+  _mediaSources?: readonly string[],
 ): string[] {
   const workspaceDir = normalizeWorkspaceDir(workspaceDirRaw);
   if (options?.workspaceOnly) {
     return workspaceDir ? [workspaceDir] : [];
   }
   const roots = getDefaultLocalRoots();
-  const scopedRoots = workspaceDir ? Array.from(new Set([...roots, workspaceDir])) : [...roots];
-  return appendLocalMediaParentRoots(scopedRoots, mediaSources);
+  return workspaceDir ? Array.from(new Set([...roots, workspaceDir])) : [...roots];
 }

 export function resolvePromptAndModelOverride(
diff --git a/src/media/local-roots.ts b/src/media/local-roots.ts
index acb3aab3cf67..1b5e1bbe9930 100644
--- a/src/media/local-roots.ts
+++ b/src/media/local-roots.ts
@@ -1,23 +1,14 @@
 import path from "node:path";
 import { resolveAgentWorkspaceDir } from "../agents/agent-scope.js";
-import {
-  resolveEffectiveToolFsRootExpansionAllowed,
-  resolveEffectiveToolFsWorkspaceOnly,
-} from "../agents/tool-fs-policy.js";
 import type { OpenClawConfig } from "../config/config.js";
 import { resolveStateDir } from "../config/paths.js";
-import { safeFileURLToPath } from "../infra/local-file-access.js";
 import { resolvePreferredOpenClawTmpDir } from "../infra/tmp-openclaw-dir.js";
-import { resolveUserPath } from "../utils.js";

 type BuildMediaLocalRootsOptions = {
   preferredTmpDir?: string;
 };

 let cachedPreferredTmpDir: string | undefined;
-const HTTP_URL_RE = /^https?:\/\//i;
-const DATA_URL_RE = /^data:/i;
-const WINDOWS_DRIVE_RE = /^[A-Za-z]:[\\/]/;

 function resolveCachedPreferredTmpDir(): string {
   if (!cachedPreferredTmpDir) {
@@ -63,60 +54,24 @@ export function getAgentScopedMediaLocalRoots(
   return roots;
 }

-function resolveLocalMediaPath(source: string): string | undefined {
-  const trimmed = source.trim();
-  if (!trimmed || HTTP_URL_RE.test(trimmed) || DATA_URL_RE.test(trimmed)) {
-    return undefined;
-  }
-  if (trimmed.startsWith("file://")) {
-    try {
-      return safeFileURLToPath(trimmed);
-    } catch {
-      return undefined;
-    }
-  }
-  if (trimmed.startsWith("~")) {
-    return resolveUserPath(trimmed);
-  }
-  if (path.isAbsolute(trimmed) || WINDOWS_DRIVE_RE.test(trimmed)) {
-    return path.resolve(trimmed);
-  }
-  return undefined;
-}
-
+/**
+ * @deprecated Kept for plugin-sdk compatibility. Media sources no longer widen allowed roots.
+ */
 export function appendLocalMediaParentRoots(
   roots: readonly string[],
-  mediaSources?: readonly string[],
+  _mediaSources?: readonly string[],
 ): string[] {
-  const appended = Array.from(new Set(roots.map((root) => path.resolve(root))));
-  for (const source of mediaSources ?? []) {
-    const localPath = resolveLocalMediaPath(source);
-    if (!localPath) {
-      continue;
-    }
-    const parentDir = path.dirname(localPath);
-    if (parentDir === path.parse(parentDir).root) {
-      continue;
-    }
-    const normalizedParent = path.resolve(parentDir);
-    if (!appended.includes(normalizedParent)) {
-      appended.push(normalizedParent);
-    }
-  }
-  return appended;
+  return Array.from(new Set(roots.map((root) => path.resolve(root))));
 }

-export function getAgentScopedMediaLocalRootsForSources(params: {
+export function getAgentScopedMediaLocalRootsForSources({
+  cfg,
+  agentId,
+  mediaSources: _mediaSources,
+}: {
   cfg: OpenClawConfig;
   agentId?: string;
   mediaSources?: readonly string[];
 }): readonly string[] {
-  const roots = getAgentScopedMediaLocalRoots(params.cfg, params.agentId);
-  if (resolveEffectiveToolFsWorkspaceOnly({ cfg: params.cfg, agentId: params.agentId })) {
-    return roots;
-  }
-  if (!resolveEffectiveToolFsRootExpansionAllowed({ cfg: params.cfg, agentId: params.agentId })) {
-    return roots;
-  }
-  return appendLocalMediaParentRoots(roots, params.mediaSources);
+  return getAgentScopedMediaLocalRoots(cfg, agentId);
 }

PATCH

echo "Patch applied successfully."
