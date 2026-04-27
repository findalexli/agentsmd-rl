#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

if grep -q 'getDashboardContextFormData = (search: string)' superset-frontend/src/pages/Chart/index.tsx 2>/dev/null; then
  echo "[solve.sh] gold patch already applied — skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/src/pages/Chart/index.tsx b/superset-frontend/src/pages/Chart/index.tsx
index 3f8d28ce2dc2..46acccad36a4 100644
--- a/superset-frontend/src/pages/Chart/index.tsx
+++ b/superset-frontend/src/pages/Chart/index.tsx
@@ -85,11 +85,11 @@ const getDashboardPageContext = (pageId?: string | null) => {
   return getItem(LocalStorageKeys.DashboardExploreContext, {})[pageId] || null;
 };

-const getDashboardContextFormData = () => {
-  const dashboardPageId = getUrlParam(URL_PARAMS.dashboardPageId);
+const getDashboardContextFormData = (search: string) => {
+  const dashboardPageId = getUrlParam(URL_PARAMS.dashboardPageId, search);
   const dashboardContext = getDashboardPageContext(dashboardPageId);
   if (dashboardContext) {
-    const sliceId = getUrlParam(URL_PARAMS.sliceId) || 0;
+    const sliceId = getUrlParam(URL_PARAMS.sliceId, search) || 0;
     const {
       colorScheme,
       labelsColor,
@@ -141,7 +141,7 @@ export default function ExplorePage() {
       fetchGeneration.current += 1;
       const generation = fetchGeneration.current;
       const exploreUrlParams = getParsedExploreURLParams(loc);
-      const dashboardContextFormData = getDashboardContextFormData();
+      const dashboardContextFormData = getDashboardContextFormData(loc.search);

       const isStale = () => generation !== fetchGeneration.current;

diff --git a/superset-frontend/src/utils/urlUtils.ts b/superset-frontend/src/utils/urlUtils.ts
index 4b218201144e..dedc20c83302 100644
--- a/superset-frontend/src/utils/urlUtils.ts
+++ b/superset-frontend/src/utils/urlUtils.ts
@@ -38,22 +38,35 @@ export type UrlParamType = 'string' | 'number' | 'boolean' | 'object' | 'rison';
 export type UrlParam = (typeof URL_PARAMS)[keyof typeof URL_PARAMS];
 export function getUrlParam(
   param: UrlParam & { type: 'string' },
+  search?: string,
 ): string | null;
 export function getUrlParam(
   param: UrlParam & { type: 'number' },
+  search?: string,
 ): number | null;
 export function getUrlParam(
   param: UrlParam & { type: 'boolean' },
+  search?: string,
 ): boolean | null;
 export function getUrlParam(
   param: UrlParam & { type: 'object' },
+  search?: string,
 ): object | null;
-export function getUrlParam(param: UrlParam & { type: 'rison' }): object | null;
+export function getUrlParam(
+  param: UrlParam & { type: 'rison' },
+  search?: string,
+): string | object | null;
 export function getUrlParam(
   param: UrlParam & { type: 'rison | string' },
+  search?: string,
 ): string | object | null;
-export function getUrlParam({ name, type }: UrlParam): unknown {
-  const urlParam = new URLSearchParams(window.location.search).get(name);
+export function getUrlParam(
+  { name, type }: UrlParam,
+  search?: string,
+): unknown {
+  const urlParam = new URLSearchParams(search ?? window.location.search).get(
+    name,
+  );
   switch (type) {
     case 'number':
       if (!urlParam) {
PATCH

echo "[solve.sh] gold patch applied successfully."
