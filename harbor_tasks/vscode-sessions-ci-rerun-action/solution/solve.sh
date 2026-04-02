#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency) - look for rerunFailedJobs in fetcher
if grep -q "rerunFailedJobs" src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts b/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
index f9a2721e6d7ff..8a83972297106 100644
--- a/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
+++ b/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
@@ -66,6 +66,7 @@ class CICheckListRenderer implements IListRenderer<ICICheckListItem, ICICheckTem
 	constructor(
 		private readonly _labels: ResourceLabels,
 		private readonly _openerService: IOpenerService,
+		private readonly _getModel: () => GitHubPullRequestCIModel | undefined,
 	) { }

 	renderTemplate(container: HTMLElement): ICICheckTemplateData {
@@ -104,6 +105,18 @@ class CICheckListRenderer implements IListRenderer<ICICheckListItem, ICICheckTem

 		const actions: Action[] = [];

+		if (element.group === CICheckGroup.Failed) {
+			actions.push(templateData.elementDisposables.add(new Action(
+				'ci.rerunCheck',
+				localize('ci.rerunCheck', "Rerun Check"),
+				ThemeIcon.asClassName(Codicon.debugRerun),
+				true,
+				async () => {
+					await this._getModel()?.rerunFailedCheck(element.check);
+				},
+			)));
+		}
+
 		if (element.check.detailsUrl) {
 			actions.push(templateData.elementDisposables.add(new Action(
 				'ci.openOnGitHub',
diff --git a/src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts b/src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts
index c212fa79443d4..3b46c17564ae0 100644
--- a/src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts
+++ b/src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts
@@ -68,6 +68,17 @@ export class GitHubPRCIFetcher {
 		return data.check_runs.map(mapCheckRun);
 	}

+	/**
+	 * Rerun failed jobs in a GitHub Actions workflow run.
+	 */
+	async rerunFailedJobs(owner: string, repo: string, runId: number): Promise<void> {
+		await this._apiClient.request<void>(
+			'POST',
+			`/repos/${e(owner)}/${e(repo)}/actions/runs/${runId}/rerun-failed-jobs`,
+			'githubApi.rerunFailedJobs'
+		);
+	}
+
 	/**
 	 * Get logs/output for a specific check run.
 	 *
diff --git a/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts b/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
index 6a1dd490aaf88..bd985e085c6f4 100644
--- a/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
+++ b/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
@@ -60,6 +60,20 @@ export class GitHubPullRequestCIModel extends Disposable {
 		return this._fetcher.getCheckRunAnnotations(this.owner, this.repo, checkRunId);
 	}

+	/**
+	 * Rerun a failed check by extracting the workflow run ID from its details URL
+	 * and calling the GitHub Actions rerun-failed-jobs API, then refresh status.
+	 */
+	async rerunFailedCheck(check: IGitHubCICheck): Promise<void> {
+		const runId = parseWorkflowRunId(check.detailsUrl);
+		if (!runId) {
+			this._logService.warn(`${LOG_PREFIX} Cannot rerun check "${check.name}": no workflow run ID found in detailsUrl`);
+			return;
+		}
+		await this._fetcher.rerunFailedJobs(this.owner, this.repo, runId);
+		await this.refresh();
+	}
+
 	/**
 	 * Start periodic polling. Each cycle refreshes CI check data.
 	 */
@@ -88,3 +102,16 @@ export class GitHubPullRequestCIModel extends Disposable {
 		super.dispose();
 	}
 }
+
+/**
+ * Extract the GitHub Actions workflow run ID from a check run's details URL.
+ * URLs follow the pattern: `https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}`
+ */
+function parseWorkflowRunId(detailsUrl: string | undefined): number | undefined {
+	if (!detailsUrl) {
+		return undefined;
+	}
+	const match = /\/actions\/runs\/(?<runId>\d+)/.exec(detailsUrl);
+	const runId = match?.groups?.runId;
+	return runId ? parseInt(runId, 10) : undefined;
+}
PATCH

echo "Patch applied successfully"
