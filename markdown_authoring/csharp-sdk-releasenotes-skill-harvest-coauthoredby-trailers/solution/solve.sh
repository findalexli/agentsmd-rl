#!/usr/bin/env bash
set -euo pipefail

cd /workspace/csharp-sdk

# Idempotency guard
if grep -qF "- For Copilot-authored PRs, additionally check the `copilot_work_started` timeli" ".github/skills/prepare-release/SKILL.md" && grep -qF "For Copilot-authored PRs, additionally identify who triggered Copilot using the " ".github/skills/prepare-release/references/categorization.md" && grep -qF "- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determ" ".github/skills/publish-release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/prepare-release/SKILL.md b/.github/skills/prepare-release/SKILL.md
@@ -45,8 +45,8 @@ Sort every PR into one of four categories. See [references/categorization.md](re
 ```
 
 **Attribution rules:**
-- Harvest `Co-authored-by` trailers from all commits in each PR's merge commit
-- For Copilot-authored PRs, check the `copilot_work_started` timeline event to identify the triggering user. That person becomes the primary author; `@Copilot` becomes a co-author
+- Harvest `Co-authored-by` trailers from **all commits** in each PR (not just the merge commit) to identify co-authors. Do this for every PR regardless of primary author.
+- For Copilot-authored PRs, additionally check the `copilot_work_started` timeline event to identify the triggering user. That person becomes the primary author; `@Copilot` becomes a co-author.
 - Omit the co-author parenthetical when there are none
 - Sort entries within each section by merge date (chronological)
 
@@ -187,7 +187,7 @@ Only after explicit user confirmation in Step 11:
 ## Edge Cases
 
 - **PR spans categories**: categorize by primary intent
-- **Copilot timeline missing**: fall back to `Co-authored-by` trailers; if still unclear, use `@Copilot` as primary author
+- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author
 - **No breaking changes**: omit the Breaking Changes section from release notes entirely
 - **Single breaking change**: use the same numbered format as multiple
 - **No user-facing changes**: if all PRs are documentation, tests, or infrastructure, flag that a release may not be warranted and ask the user whether to proceed
diff --git a/.github/skills/prepare-release/references/categorization.md b/.github/skills/prepare-release/references/categorization.md
@@ -49,7 +49,7 @@ Use this simplified format (GitHub auto-links `#PR` and `@user`):
 * Description #PR by @author
 ```
 
-For PRs with co-authors (harvested from `Co-authored-by` commit trailers):
+For PRs with co-authors (harvested from `Co-authored-by` trailers across **all commits** in the PR, not just the merge commit):
 ```
 * Description #PR by @author (co-authored by @user1 @user2)
 ```
@@ -64,7 +64,7 @@ For direct commits without an associated PR (e.g., version bumps merged directly
 * Bump version to v0.1.0-preview.12 by @halter73
 ```
 
-For Copilot-authored PRs, identify who triggered Copilot using the `copilot_work_started` timeline event on the PR. That person becomes the primary author, and @Copilot becomes a co-author:
+For Copilot-authored PRs, additionally identify who triggered Copilot using the `copilot_work_started` timeline event on the PR. That person becomes the primary author, and @Copilot becomes a co-author:
 ```
 * Add trace-level logging for JSON-RPC payloads #1234 by @halter73 (co-authored by @Copilot)
 ```
diff --git a/.github/skills/publish-release/SKILL.md b/.github/skills/publish-release/SKILL.md
@@ -64,7 +64,7 @@ Re-categorize all PRs in the commit range (including any new ones from Step 3).
 
 1. **Re-run the breaking change audit** using the **breaking-changes** skill if new PRs were found that may introduce breaks. Otherwise, carry forward the results from the prepare-release PR.
 2. **Re-categorize** all PRs into sections (What's Changed, Documentation, Tests, Infrastructure).
-3. **Re-attribute** co-authors for any new PRs.
+3. **Re-attribute** co-authors for any new PRs by harvesting `Co-authored-by` trailers from all commits in each PR.
 4. **Update acknowledgements** to include contributors from new PRs.
 
 ### Step 5: Validate README Code Samples
@@ -125,7 +125,7 @@ When the user requests revisions after the initial creation, always rewrite the
 - **PR not found**: if the prepare-release PR cannot be identified, offer to proceed manually by specifying a version and target commit
 - **Draft already exists**: if a draft release with the same tag already exists, offer to update it
 - **PR spans categories**: categorize by primary intent
-- **Copilot timeline missing**: fall back to `Co-authored-by` trailers; if still unclear, use `@Copilot` as primary author
+- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author
 - **No breaking changes**: omit the Breaking Changes section entirely
 - **Single breaking change**: use the same numbered format as multiple
 
PATCH

echo "Gold patch applied."
