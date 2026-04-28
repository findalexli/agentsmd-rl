#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "This section outlines the protocol for conducting pull request (PR) reviews to e" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -395,3 +395,42 @@ ensure your understanding is up-to-date.
 
 Furthermore, after pulling changes, the local knowledge base may be out of sync.
 You should run `npm run ai:build-kb` to re-embed the latest changes into the database.
+
+## 6. Pull Request Review Protocol
+
+This section outlines the protocol for conducting pull request (PR) reviews to ensure feedback is consistent, constructive, and aligned with the Neo.mjs project's standards.
+
+### 6.1. General Guidelines
+- Always provide feedback in a **constructive and polite tone**.
+- Focus on helping contributors improve their code while maintaining the project's standards.
+- Avoid personal criticism; keep feedback objective, actionable, and specific.
+
+### 6.2. Verification Steps
+1. **Check Against Coding Guidelines:**
+   - Verify that the PR adheres to the project's coding standards as defined in `.github/CODING_GUIDELINES.md`.
+   - Pay special attention to JSDoc comments, formatting, naming conventions, and reactivity rules.
+
+2. **Run Tests:**
+   - Execute the project's test suite (e.g., `npm test`) to ensure no regressions are introduced.
+   - If tests fail, include the failure details in the review and suggest fixes.
+
+3. **Check Completeness:**
+   - Ensure the PR includes all necessary updates, such as documentation, tests, and examples.
+   - Verify that the PR description is clear and provides sufficient context for the changes.
+
+4. **Assess Code Quality:**
+   - Review the code for readability, maintainability, and adherence to Neo.mjs architectural principles.
+   - Ensure the code is free of unnecessary complexity and aligns with the framework's reactivity model.
+
+### 6.3. Standard Review Comment Format
+Use the following format for review comments to ensure clarity and consistency:
+
+1. **Summary of Findings:**
+   - Begin with a brief summary of the overall review, highlighting strengths and areas for improvement.
+
+2. **Line-by-Line Comments:**
+   - Provide specific feedback for each issue, referencing the relevant line(s) of code.
+   - Use the following structure:
+     - **What is the issue?**
+     - **Why is it an issue?**
+     - **How can it be improved?**
PATCH

echo "Gold patch applied."
