#!/usr/bin/env bash
set -euo pipefail

cd /workspace/full-stack-skills

# Idempotency guard
if grep -qF "This skill is organized to match the Ant Design React official documentation str" "skills/ant-design-react/SKILL.md" && grep -qF "\"react-dom\": \"^19.0.0\"," "skills/ant-design-react/templates/project-setup.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ant-design-react/SKILL.md b/skills/ant-design-react/SKILL.md
@@ -22,7 +22,7 @@ Use this skill whenever the user wants to:
 
 ## How to use this skill
 
-This skill is organized to match the Ant Design React official documentation structure (https://4x-ant-design.antgroup.com/docs/react/introduce-cn, https://4x-ant-design.antgroup.com/components/overview-cn/). When working with Ant Design React:
+This skill is organized to match the Ant Design React official documentation structure (https://6x-ant-design.antgroup.com/docs/react/introduce-cn, https://6x-ant-design.antgroup.com/components/overview-cn/). When working with Ant Design React:
 
 1. **Identify the topic** from the user's request:
    - Getting started/快速开始 → `examples/getting-started/installation.md` or `examples/getting-started/basic-usage.md`
@@ -96,10 +96,10 @@ This skill is organized to match the Ant Design React official documentation str
 ### Doc mapping (one-to-one with official documentation)
 
 **Guide (指南)**:
-- See guide files in `examples/guide/` or `examples/getting-started/` → https://4x-ant-design.antgroup.com/docs/react/introduce-cn
+- See guide files in `examples/guide/` or `examples/getting-started/` → https://6x-ant-design.antgroup.com/docs/react/introduce-cn
 
 **Components (组件)**:
-- See component files in `examples/components/` → https://4x-ant-design.antgroup.com/components/overview-cn/
+- See component files in `examples/components/` → https://6x-ant-design.antgroup.com/components/overview-cn/
 
 ## Examples and Templates
 
@@ -156,9 +156,9 @@ Detailed API documentation is available in the `api/` directory, organized to ma
 
 ## Resources
 
-- **Official Website**: https://4x-ant-design.antgroup.com/index-cn
-- **Getting Started**: https://4x-ant-design.antgroup.com/docs/react/introduce-cn
-- **Components**: https://4x-ant-design.antgroup.com/components/overview-cn/
+- **Official Website**: https://6x-ant-design.antgroup.com/index-cn
+- **Getting Started**: https://6x-ant-design.antgroup.com/docs/react/introduce-cn
+- **Components**: https://6x-ant-design.antgroup.com/components/overview-cn/
 - **GitHub Repository**: https://github.com/ant-design/ant-design
 
 ## Keywords
diff --git a/skills/ant-design-react/templates/project-setup.md b/skills/ant-design-react/templates/project-setup.md
@@ -6,9 +6,9 @@
 // package.json
 {
   "dependencies": {
-    "react": "^18.0.0",
-    "react-dom": "^18.0.0",
-    "antd": "^4.24.0"
+    "react": "^19.0.0",
+    "react-dom": "^19.0.0",
+    "antd": "^6.3.0"
   }
 }
 ```
PATCH

echo "Gold patch applied."
