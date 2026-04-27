#!/bin/bash
# Gold solution: applies the exact patch from TryGhost/Ghost#27346.
# Idempotent — re-running is a no-op once the patch is in place.
set -euo pipefail

cd /workspace/Ghost

# Idempotency: if the distinctive added line is already present in AGENTS.md,
# the patch has already been applied — exit cleanly.
if grep -q "Enable corepack to use the correct pnpm version" AGENTS.md 2>/dev/null; then
    echo "Patch already applied — skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codex/environments/environment.toml b/.codex/environments/environment.toml
index dbc010629b0..4117f9ab49a 100644
--- a/.codex/environments/environment.toml
+++ b/.codex/environments/environment.toml
@@ -4,5 +4,5 @@ name = "Ghost"

 [setup]
 script = '''
-pnpm setup
+pnpm run setup
 '''
diff --git a/.github/scripts/enforce-package-manager.js b/.github/scripts/enforce-package-manager.js
index 138cb4122fb..0fa339aa56a 100644
--- a/.github/scripts/enforce-package-manager.js
+++ b/.github/scripts/enforce-package-manager.js
@@ -16,7 +16,7 @@ Use one of these instead:
   pnpm install

 Common command replacements:
-  yarn setup   -> pnpm setup
+  yarn setup   -> pnpm run setup
   yarn dev     -> pnpm dev
   yarn test    -> pnpm test
   yarn lint    -> pnpm lint
diff --git a/AGENTS.md b/AGENTS.md
index ffbe9175c6e..d39c42a6232 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -42,8 +42,8 @@ Two categories of apps:

 ### Development
 ```bash
-pnpm                           # Install dependencies
-pnpm setup                     # First-time setup (installs deps + submodules)
+corepack enable pnpm           # Enable corepack to use the correct pnpm version
+pnpm run setup                 # First-time setup (installs deps + submodules)
 pnpm dev                       # Start development (Docker backend + host frontend dev servers)
 ```

diff --git a/docs/README.md b/docs/README.md
index 04a01e6e534..f5c1583eca5 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -30,7 +30,8 @@ git remote add origin git@github.com:<YourUsername>/Ghost.git

 ```bash
 # Install dependencies and initialize submodules
-pnpm setup
+corepack enable pnpm
+pnpm run setup
 ```

 #### 3. Start Ghost
diff --git a/e2e/README.md b/e2e/README.md
index daf2810a21b..7ade4c09e07 100644
--- a/e2e/README.md
+++ b/e2e/README.md
@@ -6,7 +6,7 @@ This test suite runs automated browser tests against a running Ghost instance to

 ### Prerequisites
 - Docker and Docker Compose installed
-- Node.js and pnpm installed
+- Node.js installed (pnpm is managed via corepack — run `corepack enable pnpm` first)

 ### Running Tests
 To run the test, within this `e2e` folder run:
PATCH

echo "Patch applied successfully."
