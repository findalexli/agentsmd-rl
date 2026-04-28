#!/usr/bin/env bash
set -euo pipefail

cd /workspace/actionbook

# Idempotency guard
if grep -qF "When Actionbook data does not work as expected, direct browser access to the tar" "skills/actionbook/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/actionbook/SKILL.md b/skills/actionbook/SKILL.md
@@ -236,3 +236,21 @@ Executable workflow scripts for common patterns:
 - **Search by task**: Describe what you want to accomplish, not just the element (e.g., "linkedin send message" not "linkedin message button")
 - **Follow the order**: Execute steps in sequence as provided in the manual
 - **Trust the selectors**: Actionbook selectors are verified and maintained
+
+## Fallback Strategy
+
+This section describes situations where Actionbook may not provide the required information and the available fallback approaches.
+
+### When Fallback is Needed
+
+Actionbook stores pre-computed page data captured at indexing time. This data may become outdated as websites evolve. The following signals indicate that fallback may be necessary:
+
+- **Selector execution failure** - The returned CSS/XPath selector does not match any element on the current page.
+- **Element mismatch** - The selector matches an element, but the element type or behavior does not match the expected interaction method.
+- **Multiple selector failures** - Several element selectors from the same action fail consecutively.
+
+These conditions are not signaled in Actionbook API responses. They can only be detected during browser automation execution when selectors fail to locate the expected elements.
+
+### Fallback Approaches
+
+When Actionbook data does not work as expected, direct browser access to the target website allows for real-time retrieval of current page structure, element information, and interaction capabilities.
PATCH

echo "Gold patch applied."
