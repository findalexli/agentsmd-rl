#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if grep -q 'parseFilterParam' code/core/src/manager-api/lib/filter-param.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/code/core/src/manager-api/lib/filter-param.ts b/code/core/src/manager-api/lib/filter-param.ts
new file mode 100644
index 000000000000..3535a471fd47
--- /dev/null
+++ b/code/core/src/manager-api/lib/filter-param.ts
@@ -0,0 +1,39 @@
+/**
+ * Parses a semicolon-separated URL filter parameter into included/excluded arrays.
+ *
+ * Items prefixed with `!` are treated as exclusions.
+ * The `transform` callback converts each raw string to the desired type; returning
+ * `null` or `undefined` silently skips the entry (e.g. for unknown enum values).
+ */
+export const parseFilterParam = <T>(
+  param: string | undefined,
+  transform: (raw: string) => T | null | undefined
+): { included: T[]; excluded: T[] } => {
+  if (!param) {
+    return { included: [], excluded: [] };
+  }
+
+  const included: T[] = [];
+  const excluded: T[] = [];
+
+  param.split(';').forEach((raw) => {
+    if (!raw) {
+      return;
+    }
+
+    const isExcluded = raw.startsWith('!');
+    const value = transform(isExcluded ? raw.slice(1) : raw);
+
+    if (value == null) {
+      return;
+    }
+
+    if (isExcluded) {
+      excluded.push(value);
+    } else {
+      included.push(value);
+    }
+  });
+
+  return { included, excluded };
+};
diff --git a/code/core/src/manager-api/modules/statuses.ts b/code/core/src/manager-api/modules/statuses.ts
index 3997052314b4..a5885dfa497e 100644
--- a/code/core/src/manager-api/modules/statuses.ts
+++ b/code/core/src/manager-api/modules/statuses.ts
@@ -5,40 +5,13 @@ import type {
 } from 'storybook/internal/types';

 import { statusValueShortName, toStatusValue } from '../../shared/status-store/index.ts';
+import { parseFilterParam } from '../lib/filter-param.ts';
 import { fullStatusStore } from '../stores/status.ts';

 export const parseStatusesParam = (
   statusesParam: string | undefined
-): { included: StatusValue[]; excluded: StatusValue[] } => {
-  if (!statusesParam) {
-    return { included: [], excluded: [] };
-  }
-
-  const included: StatusValue[] = [];
-  const excluded: StatusValue[] = [];
-
-  statusesParam.split(';').forEach((rawStatus) => {
-    if (!rawStatus) {
-      return;
-    }
-
-    const isExcluded = rawStatus.startsWith('!');
-    const shortName = isExcluded ? rawStatus.slice(1) : rawStatus;
-    const statusValue = toStatusValue(shortName);
-
-    if (!statusValue) {
-      return; // silently ignore unknown short names
-    }
-
-    if (isExcluded) {
-      excluded.push(statusValue);
-    } else {
-      included.push(statusValue);
-    }
-  });
-
-  return { included, excluded };
-};
+): { included: StatusValue[]; excluded: StatusValue[] } =>
+  parseFilterParam(statusesParam, toStatusValue);

 export const serializeStatusesParam = (
   included: StatusValue[],
diff --git a/code/core/src/manager-api/modules/tags.ts b/code/core/src/manager-api/modules/tags.ts
index f666d1ba09e9..fc5ccd1706b9 100644
--- a/code/core/src/manager-api/modules/tags.ts
+++ b/code/core/src/manager-api/modules/tags.ts
@@ -7,6 +7,7 @@ import type {

 import memoize from 'memoizerific';

+import { parseFilterParam } from '../lib/filter-param.ts';
 import { BUILT_IN_FILTERS, Tag as TagEnum, USER_TAG_FILTER } from '../../shared/constants/tags.ts';

 export const BUILT_IN_URL_TAG_MAP: Record<string, Tag> = {
@@ -17,32 +18,8 @@ export const BUILT_IN_URL_TAG_MAP: Record<string, Tag> = {

 export const parseTagsParam = (
   tagsParam: string | undefined
-): { included: Tag[]; excluded: Tag[] } => {
-  if (!tagsParam) {
-    return { included: [], excluded: [] };
-  }
-
-  const included: Tag[] = [];
-  const excluded: Tag[] = [];
-
-  tagsParam.split(';').forEach((rawTag) => {
-    if (!rawTag) {
-      return;
-    }
-
-    const isExcluded = rawTag.startsWith('!');
-    const normalizedTag = isExcluded ? rawTag.slice(1) : rawTag;
-    const mappedTag = (BUILT_IN_URL_TAG_MAP[normalizedTag] ?? normalizedTag) as Tag;
-
-    if (isExcluded) {
-      excluded.push(mappedTag);
-    } else {
-      included.push(mappedTag);
-    }
-  });
-
-  return { included, excluded };
-};
+): { included: Tag[]; excluded: Tag[] } =>
+  parseFilterParam(tagsParam, (raw) => (BUILT_IN_URL_TAG_MAP[raw] ?? raw) as Tag);

 export const serializeTagsParam = (included: Tag[], excluded: Tag[]): string => {
   if (!included.length && !excluded.length) {

PATCH

echo "Patch applied successfully."
