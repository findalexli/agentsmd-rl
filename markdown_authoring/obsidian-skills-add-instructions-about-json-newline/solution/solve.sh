#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-skills

# Idempotency guard
if grep -qF "In JSON, newline characters inside strings **must** be represented as `\\n`. Do *" "skills/json-canvas/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/json-canvas/SKILL.md b/skills/json-canvas/SKILL.md
@@ -69,6 +69,20 @@ Text nodes contain Markdown content.
 }
 ```
 
+#### Newline Escaping (Common Pitfall)
+
+In JSON, newline characters inside strings **must** be represented as `\n`. Do **not** use the literal sequence `\\n` in a `.canvas` file—Obsidian will render it as the characters `\` and `n` instead of a line break.
+
+Examples:
+
+```json
+{ "type": "text", "text": "Line 1\nLine 2" }
+```
+
+```json
+{ "type": "text", "text": "Line 1\\nLine 2" }
+```
+
 | Attribute | Required | Type | Description |
 |-----------|----------|------|-------------|
 | `text` | Yes | string | Plain text with Markdown syntax |
PATCH

echo "Gold patch applied."
