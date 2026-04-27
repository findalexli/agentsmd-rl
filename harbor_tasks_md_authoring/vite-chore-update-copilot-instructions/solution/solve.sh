#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vite

# Idempotency guard
if grep -qF "- If this adds a new config option, verify problem can't be solved with smarter " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -2,28 +2,49 @@ This is a TypeScript project that implements a frontend build tooling called Vit
 
 ## Code Standards
 
-### Required Before Each Commit
-
 - Run `pnpm run lint` to ensure that your code adheres to the code standards.
 - Run `pnpm run format` to format your code.
-
-### Development Flow
-
 - Build: `pnpm run build`
 - Test: `pnpm run test` (uses Vitest and Playwright)
 
 ## Repository Structure
 
-- `docs/`: Documentation.
-- `packages/create-vite`: Contains the source code for the `create-vite` command.
-- `packages/plugin-legacy`: Contains the source code for `@vitejs/plugin-legacy`.
-- `packages/vite`: Contains the source code for the Vite core.
+- `docs/`: Documentation
+- `packages/create-vite`: The source code for the `create-vite` command
+- `packages/plugin-legacy`: The source code for the `@vitejs/plugin-legacy` plugin
+- `packages/vite`: The source code for the Vite core
 - `playground/`: E2E tests
 
-## Key Guidelines
+## PR Guidelines
+
+### PR Title & Commit Messages
+
+- Follow the [commit message convention](./commit-convention.md)
+
+### PR Description
+
+- What does this PR solve? - Clear problem/feature description
+- Why was this approach chosen? - Implementation rationale
+- If this is a new feature, include a convincing reason.
+- If this adds a new config option, verify problem can't be solved with smarter defaults, existing options, or a plugin
+- If this is a bug fix, explain what caused the bug - Link to relevant code if possible
+
+### Code Style & Standards
+
+- Code follows TypeScript best practices
+- Maintains existing code structure and organization
+- Comments explain "why", not "what"
+
+### Testing
+
+- Prefer unit tests if it can be tested without using mocks
+- E2E tests should be added in the `playground/` directory
+
+### Documentation
+
+- Update documentation for public API changes
+- Documentation changes go in `docs/` folder
+
+### Other Considerations
 
-1. Follow TypeScript best practices.
-2. Maintain existing code structure and organization.
-3. Write tests for new functionality. Prefer unit tests if it can be tested without using mocks. E2E tests should be added in the `playground/` directory.
-4. Never write comments that explain what the code does. Instead, write comments that explain why the code does what it does.
-5. Suggest changes to the documentation if public API changes are made.
+- No concerning performance impacts
PATCH

echo "Gold patch applied."
