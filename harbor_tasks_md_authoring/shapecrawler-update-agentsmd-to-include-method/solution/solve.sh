#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shapecrawler

# Idempotency guard
if grep -qF "- The maximum allowed method Cyclomatic Complexity\u00a0is 10." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -31,6 +31,9 @@ tests/
 
 ### Mandatory Rules
 - **What is an Object?** The project follows the principle that the correct object is a representation of a real-world entity or concept. In its constructor, the class encapsulates properties or another object as “coordinates” that the class instance will use to refer to the real-world entity.
+- **Method complexity**:
+  - The maximum allowed method Cognitive Complexity is 15.
+  - The maximum allowed method Cyclomatic Complexity is 10.
 - **File Size Limit**: Keep files under 500 lines. If a file exceeds this, extract logic into new classes/files.
 - **Naming Conventions**:
    - Class names must be **nouns** (e.g., `Slide`, `Slides`, not `SlideManager` or `SlideService`)
PATCH

echo "Gold patch applied."
