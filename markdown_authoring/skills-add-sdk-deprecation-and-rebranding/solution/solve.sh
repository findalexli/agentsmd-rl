#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "> **\u26a0\ufe0f MIGRATION NOTICE**: The [Old Service Name] has been rebranded to **[New S" ".github/skills/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/skill-creator/SKILL.md b/.github/skills/skill-creator/SKILL.md
@@ -167,6 +167,60 @@ See `references/azure-sdk-patterns.md` for detailed patterns including:
 - **Java**: Builder pattern, `PagedIterable`/`PagedFlux`, Reactor types
 - **TypeScript**: `PagedAsyncIterableIterator`, `AbortSignal`, browser considerations
 
+### Handling Deprecated or Rebranded SDKs
+
+When an Azure SDK has been deprecated or rebranded, update skills to guide users toward the current package while maintaining backward compatibility:
+
+**1. Add a migration notice at the top of the skill:**
+
+```markdown
+> **⚠️ MIGRATION NOTICE**: The [Old Service Name] has been rebranded to **[New Service Name]**. While the package `old-package-name` remains available for compatibility, **new projects should use `new-package-name`** which provides the latest features and updates.
+>
+> **For new projects**: Use the `new-package-name` package instead.
+>
+> **This skill remains valid** for existing projects using `old-package-name`, but be aware you're using the legacy package name. The API patterns shown here are compatible with both packages.
+```
+
+**2. Show both installation options:**
+
+```markdown
+## Installation
+
+### Legacy Package (Old Name)
+
+\`\`\`xml
+<dependency>
+    <groupId>com.azure</groupId>
+    <artifactId>azure-old-package</artifactId>
+    <version>4.2.0</version>
+</dependency>
+\`\`\`
+
+### Recommended Package (New Name)
+
+**For new projects, use the rebranded package:**
+
+\`\`\`xml
+<dependency>
+    <groupId>com.azure</groupId>
+    <artifactId>azure-new-package</artifactId>
+    <version>1.0.0</version>
+</dependency>
+\`\`\`
+
+> **Note**: The API patterns in this skill apply to both packages. Replace package names and imports as needed when using `azure-new-package`.
+```
+
+**3. When to create a new skill vs. update existing:**
+
+- **Update existing skill** if the API is largely compatible (same or similar class/method names)
+- **Create new skill + migration guide** if the API changed significantly (use `references/migration.md`)
+- **Always cross-reference** between old and new skills
+
+**Examples:**
+- `azure-ai-formrecognizer-java` → `azure-ai-documentintelligence` (rebranded service)
+- `azure-communication-callingserver-java` → `azure-communication-callautomation` (deprecated, with migration guide)
+
 ### Example: Azure SDK Skill Structure
 
 ```markdown
PATCH

echo "Gold patch applied."
