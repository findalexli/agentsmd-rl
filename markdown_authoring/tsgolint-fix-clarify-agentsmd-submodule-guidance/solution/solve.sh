#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tsgolint

# Idempotency guard
if grep -qF "- If you are performing a submodule update, make sure to stage and commit the ne" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,7 +4,7 @@ TSGolint is a static analysis tool, based on typescript-go, for implementing and
 
 ## ⚠️ CRITICAL: typescript-go Submodule Warning
 
-**DO NOT COMMIT SUBMODULE CHANGES WHEN FINALIZING WORK**
+**DO NOT COMMIT SUBMODULE POINTER CHANGES**
 
 The `typescript-go/` directory is a Git submodule that references Microsoft's TypeScript Go port.
 
@@ -14,11 +14,11 @@ The `typescript-go/` directory is a Git submodule that references Microsoft's Ty
 - You can freely modify and commit within the `typescript-go/` folder
 - Use normal git commands within the typescript-go directory as needed
 
-### Before Finalizing Work
+### Before Creating a TSGolint Commit
 
-- Convert any typescript-go changes into patch files in the `patches/` directory
-- **NEVER** commit the submodule pointer changes to the TSGolint repository
-- When you see `modified: typescript-go (new commits)` in git status, do NOT stage/commit this change
+- Check `git status` before committing.
+- **NEVER** stage or commit submodule pointer changes unless explicitly performing a `typescript-go` submodule update.
+- If you are performing a submodule update, make sure to stage and commit the new pointer to the upstream typescript-go commit. MAKE SURE this pointer DOES NOT include the additional patches.
 
 ### Creating Permanent Changes
 
@@ -27,7 +27,7 @@ If you need to modify typescript-go functionality permanently:
 1. Test your changes locally in the typescript-go directory
 2. Create a patch file in `patches/` using `git format-patch`
 3. Document the patch purpose in `patches/README.md`
-4. Reset the typescript-go submodule to its original state
+4. Reset the typescript-go submodule only after the patch has been created and the user has approved, or when the task explicitly requires the patch workflow
 5. The patches are applied during project initialization (`just init`) using `git am --3way --no-gpg-sign ../patches/*.patch`
 
 ### Exposing New Functions
PATCH

echo "Gold patch applied."
