#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-design-skills

# Idempotency guard
if grep -qF "1. Display warning to user: \"\u26a0\ufe0f Warning: Implementation may conflict with compon" "figma-to-code/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/figma-to-code/SKILL.md b/figma-to-code/SKILL.md
@@ -80,10 +80,24 @@ Extract:
 - Typography (font family, size, weight)
 - Border radius, shadows, effects
 - Component variant values
+- Component description (usage guidelines)
 ```
 
 **Look for:** Which Figma variables? Spacing values? Hard-coded values?
 
+**Component Description Usage:**
+- If component has a `description` field, treat it as **authoritative usage guidelines**
+- Use the description to understand:
+  - Intended use cases and context
+  - Prop combinations and variants
+  - When to use vs. when not to use
+  - Any constraints or requirements
+- **If implementing usage that conflicts with description guidelines:**
+  1. Display warning to user: "⚠️ Warning: Implementation may conflict with component guidelines: [specific conflict]"
+  2. Explain the conflict clearly
+  3. Proceed with implementation as requested
+  4. Document the deviation in code comments
+
 #### Step 3: Get Screenshot (REQUIRED THIRD)
 ```
 Tool: mcp__figma-desktop__get_screenshot
@@ -370,6 +384,8 @@ export default function PageName() {
 Before providing code, verify:
 
 - [ ] Used metadata → context → screenshot → variables order
+- [ ] Checked component description for usage guidelines
+- [ ] Warned user if implementation conflicts with guidelines
 - [ ] Checked for existing components first
 - [ ] Used composition over creation
 - [ ] Mapped Figma variants to code props
PATCH

echo "Gold patch applied."
