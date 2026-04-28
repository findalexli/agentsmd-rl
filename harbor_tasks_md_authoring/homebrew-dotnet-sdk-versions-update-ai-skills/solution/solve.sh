#!/usr/bin/env bash
set -euo pipefail

cd /workspace/homebrew-dotnet-sdk-versions

# Idempotency guard
if grep -qF "description: Fix or update the CI workflow for homebrew-dotnet-sdk-versions. Use" ".aiskills/fix-ci/SKILL.md" && grep -qF "description: Add a new cask to homebrew-dotnet-sdk-versions. Use this skill when" ".aiskills/new-cask/SKILL.md" && grep -qF "description: Create an update PR for an existing cask in homebrew-dotnet-sdk-ver" ".aiskills/update-cask/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.aiskills/fix-ci/SKILL.md b/.aiskills/fix-ci/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: fix-ci
+description: Fix or update the CI workflow for homebrew-dotnet-sdk-versions. Use this skill whenever asked to fix a broken CI, investigate a CI failure, update .github/workflows/ci.yml, or sync CI changes from the official Homebrew cask. Always consult the official Homebrew cask CI as the reference before making any changes.
+---
+
 # SKILL: Fixing CI for homebrew-dotnet-sdk-versions
 
 ## When to use this skill
diff --git a/.aiskills/new-cask/SKILL.md b/.aiskills/new-cask/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: new-cask
+description: Add a new cask to homebrew-dotnet-sdk-versions. Use this skill whenever asked to support a new .NET SDK version or feature band that doesn't have a cask yet, create a stub cask, add a new major/minor/preview release, or add support for a new dotnet-sdk version (e.g. "add dotnet-sdk12-0-100" or "support .NET 11 preview").
+---
+
 # SKILL: Adding a New Cask to homebrew-dotnet-sdk-versions
 
 ## When to use this skill
@@ -193,6 +198,15 @@ brew audit --cask dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}
 
 ### 6. Open the PR
 
+**If you are the repo owner** (pushing directly to origin):
+```bash
+git checkout -b new-cask/dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}
+git add Casks/dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}.rb
+git commit -m "Add support for dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}"
+git push origin new-cask/dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}
+```
+
+**If you are an external contributor** (pushing to your fork):
 ```bash
 git checkout -b new-cask/dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}
 git add Casks/dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}.rb
diff --git a/.aiskills/update-cask/SKILL.md b/.aiskills/update-cask/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: update-cask
+description: Create an update PR for an existing cask in homebrew-dotnet-sdk-versions. Use this skill whenever asked to manually bump a cask to a newer version, update sha256/url/version fields, force-update a cask the auto-updater missed, or open a PR to update a specific dotnet-sdk cask version.
+---
+
 # SKILL: Creating an Update PR for an Existing Cask
 
 ## When to use this skill
PATCH

echo "Gold patch applied."
