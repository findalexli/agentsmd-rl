#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruby-git

# Idempotency guard
if grep -qF "description: \"Scaffolds new and reviews existing Git::Commands::* classes with u" ".github/skills/command-implementation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/command-implementation/SKILL.md b/.github/skills/command-implementation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: command-implementation
-description: "Scaffolds new and reviews existing Git::Commands::* classes with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command from scratch, updating an existing command, or reviewing a command class for correctness."
+description: "Scaffolds new and reviews existing Git::Commands::* classes with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command class from scratch, updating an existing command class, or reviewing a command class for correctness."
 ---
 
 # Command Implementation
PATCH

echo "Gold patch applied."
