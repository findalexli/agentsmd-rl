#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lago-front

# Idempotency guard
if grep -qF "**Note**: If Context7 is not installed or not configured, fall back to your trai" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -68,4 +68,76 @@ You are an expert development assistant for the Lago billing system project. Alw
 - Maintain consistent naming conventions (camelCase for variables, PascalCase for components)
 - Use proper error handling with Apollo Client error boundaries
 
+## TypeScript Conventions
+
+### Discriminated Unions Rather Than Conditional Props
+
+We prefer to have our props described with "discrimination" and prevent optional props overuse. Do it as much as possible as it helps understanding the logic of how props are used.
+
+```tsx
+// ❌ Bad - Optional props create ambiguity
+type Props = {
+  authenticated: boolean
+  level?: 'basic' | 'admin'
+}
+
+// ✅ Good - Discriminated union makes the relationship clear
+type Props =
+  | { authenticated: true; level: 'basic' | 'admin' }
+  | { authenticated: false };
+```
+
+### Explicit Function Return Types
+
+Always write the return type of a function explicitly. This improves code readability, helps catch errors early, and makes the codebase more maintainable.
+
+```tsx
+// ❌ Bad - Implicit return type
+const calculateTotal = (items: Item[]) => {
+  return items.reduce((sum, item) => sum + item.price, 0)
+}
+
+// ✅ Good - Explicit return type
+const calculateTotal = (items: Item[]): number => {
+  return items.reduce((sum, item) => sum + item.price, 0)
+}
+```
+
+## Documentation & Library References
+
+### Using Context7 MCP (If Installed)
+
+If the user has Context7 MCP configured, **ALWAYS use it** to fetch up-to-date documentation for third-party libraries before making assumptions or using outdated knowledge:
+
+1. **When to Use Context7**:
+   - When working with React, TypeScript, Vite, Apollo Client, Formik, Yup, Material UI, or any npm package
+   - Before implementing features using external libraries
+   - When debugging library-specific issues
+   - When the user asks questions about library APIs or best practices
+
+2. **How to Use Context7**:
+   - First, resolve the library ID: Use `resolve-library-id` with the library name (e.g., "react", "apollo-client", "@mui/material")
+   - Then, fetch docs: Use `get-library-docs` with the resolved Context7-compatible library ID
+   - Optionally specify a `topic` to focus on specific features (e.g., "hooks", "routing", "forms")
+
+3. **Example Workflow**:
+
+   ```
+   User asks: "How do I use Apollo Client mutations?"
+
+   Step 1: resolve-library-id("apollo-client") → /apollographql/apollo-client
+   Step 2: get-library-docs("/apollographql/apollo-client", topic: "mutations")
+   Step 3: Use the fetched documentation to provide accurate, up-to-date guidance
+   ```
+
+4. **Key Libraries in This Project**:
+   - React 18: `/facebook/react` or `/facebook/react/v18.x.x`
+   - Apollo Client: `/apollographql/apollo-client`
+   - Material UI: `/mui/material-ui`
+   - Formik: `/jaredpalmer/formik`
+   - Vite: `/vitejs/vite`
+   - TypeScript: `/microsoft/TypeScript`
+
+**Note**: If Context7 is not installed or not configured, fall back to your training data knowledge, but always prefer Context7 when available for the most accurate and current information.
+
 Always provide solutions that align with Lago's architecture and use pnpm for any package-related operations.
PATCH

echo "Gold patch applied."
