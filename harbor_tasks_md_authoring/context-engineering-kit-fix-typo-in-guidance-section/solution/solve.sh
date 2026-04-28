#!/usr/bin/env bash
set -euo pipefail

cd /workspace/context-engineering-kit

# Idempotency guard
if grep -qF "This skill provides guidance for quality focused software development and archit" "plugins/ddd/skills/software-architecture/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/ddd/skills/software-architecture/SKILL.md b/plugins/ddd/skills/software-architecture/SKILL.md
@@ -5,7 +5,7 @@ description: Guide for quality focused software architecture. This skill should
 
 # Software Architecture Development Skill
 
-This skill provides guidence for quality focused software development and architecture. It is based on Clean Architecture and Domain Driven Design principles.
+This skill provides guidance for quality focused software development and architecture. It is based on Clean Architecture and Domain Driven Design principles.
 
 ## Code Style Rules
 
PATCH

echo "Gold patch applied."
