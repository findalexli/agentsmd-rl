#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "? fetcher.formData.get(\"favorite\") === \"true\"" "skills/react-router-data-mode/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/react-router-data-mode/SKILL.md b/skills/react-router-data-mode/SKILL.md
@@ -72,7 +72,9 @@ ReactDOM.createRoot(root).render(<RouterProvider router={router} />);
 
 ```tsx
 const fetcher = useFetcher();
-const optimistic = fetcher.formData?.get("favorite") === "true" ?? isFavorite;
+const optimistic = fetcher.formData
+  ? fetcher.formData.get("favorite") === "true"
+  : isFavorite;
 
 <fetcher.Form method="post" action={`/favorites/${id}`}>
   <button>{optimistic ? "★" : "☆"}</button>
PATCH

echo "Gold patch applied."
