#!/usr/bin/env bash
# Gold solution: applies the deploy.ts patch from cloudflare/workers-sdk#13072.
# Inlined as a HEREDOC — never fetched from external URLs.
set -euo pipefail

cd /workspace/workers-sdk

DEPLOY_FILE="packages/wrangler/src/versions/deploy.ts"

# Idempotency guard: the post-fix code contains the comment line below.
if grep -q "skip fetching the" "$DEPLOY_FILE" 2>/dev/null; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/wrangler/src/versions/deploy.ts b/packages/wrangler/src/versions/deploy.ts
index 397cdff7f2..c7d4e73c47 100644
--- a/packages/wrangler/src/versions/deploy.ts
+++ b/packages/wrangler/src/versions/deploy.ts
@@ -362,15 +362,23 @@ async function promptVersionsToDeploy(
 	versionCache: VersionCache,
 	yesFlag: boolean
 ): Promise<VersionId[]> {
+	// If the user has already specified all versions they want to deploy and
+	// has passed --yes (so there's no interactive prompt), skip fetching the
+	// full deployable-versions list and only fetch the specific versions needed.
+	const skipDeployableVersionsFetch =
+		yesFlag && defaultSelectedVersionIds.length > 0;
+
 	await spinnerWhile({
-		startMessage: "Fetching deployable versions",
+		startMessage: "Fetching versions",
 		async promise() {
-			await fetchDeployableVersions(
-				complianceConfig,
-				accountId,
-				workerName,
-				versionCache
-			);
+			if (!skipDeployableVersionsFetch) {
+				await fetchDeployableVersions(
+					complianceConfig,
+					accountId,
+					workerName,
+					versionCache
+				);
+			}
 			await fetchVersions(
 				complianceConfig,
 				accountId,
PATCH

# Add the changeset (process rule per AGENTS.md).
mkdir -p .changeset
cat > .changeset/versions-deploy-skip-deployable-fetch.md <<'CHANGESET'
---
"wrangler": patch
---

Skip unnecessary `GET /versions?deployable=true` API call in `wrangler versions deploy` when all version IDs are explicitly provided and `--yes` is passed

When deploying a specific version non-interactively (e.g. `wrangler versions deploy <id> --yes`), Wrangler previously always fetched the full list of deployable versions to populate the interactive selection prompt — even though the prompt is skipped entirely when `--yes` is used and all versions are already specified. The deployable-versions list is now only fetched when actually needed (i.e. when no version IDs are provided, or when running interactively).
CHANGESET

echo "Patch applied."
