#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "Use `validateSearch` with `zodValidator` from `@tanstack/zod-adapter` to validat" "ui-v2/src/routes/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/routes/AGENTS.md b/ui-v2/src/routes/AGENTS.md
@@ -29,6 +29,27 @@ export const Route = createFileRoute("/path")({
 });
 ```
 
+## Search Parameters
+
+Use `validateSearch` with `zodValidator` from `@tanstack/zod-adapter` to validate search params:
+
+```ts
+import { zodValidator } from "@tanstack/zod-adapter";
+import { z } from "zod";
+
+const searchSchema = z.object({
+	redirect: z.string().optional(),
+});
+
+export const Route = createFileRoute("/path")({
+	validateSearch: zodValidator(searchSchema),
+	component: function RouteComponent() {
+		const { redirect } = Route.useSearch();
+		// ...
+	},
+});
+```
+
 ## Best Practices
 
 - Explicitly mark promises as ignored with the `void` operator when prefetching
PATCH

echo "Gold patch applied."
