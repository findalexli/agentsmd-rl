#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency)
if grep -q "export function parseWorkflowRunId" src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts b/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
index 8a83972297106..f83c243b5b2f8 100644
--- a/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
+++ b/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts
@@ -22,7 +22,7 @@ import { ChatViewPaneTarget, IChatWidgetService } from '../../../../workbench/con
 import { DEFAULT_LABELS_CONTAINER, IResourceLabel, ResourceLabels } from '../../../../workbench/browser/labels.js';
 import { ActionBar } from '../../../../base/browser/ui/actionbar/actionbar.js';
 import { GitHubCheckConclusion, GitHubCheckStatus, IGitHubCICheck } from '../../github/common/types.js';
-import { GitHubPullRequestCIModel } from '../../github/browser/models/githubPullRequestCIModel.js';
+import { GitHubPullRequestCIModel, parseWorkflowRunId } from '../../github/browser/models/githubPullRequestCIModel.js';
 import { CICheckGroup, buildFixChecksPrompt, getCheckGroup, getCheckStateLabel, getFailedChecks } from './fixCIChecksAction.js';

 const $ = dom.$;
@@ -105,7 +105,7 @@ class CICheckListRenderer implements IListRenderer<ICICheckListItem, ICICheckTem

 		const actions: Action[] = [];

-		if (element.group === CICheckGroup.Failed) {
+		if (element.group === CICheckGroup.Failed && parseWorkflowRunId(element.check.detailsUrl) !== undefined) {
 			actions.push(templateData.elementDisposables.add(new Action(
 				'ci.rerunCheck',
 				localize('ci.rerunCheck', "Rerun Check"),
diff --git a/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts b/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
index bd985e085c6f4..3f0cec668525e 100644
--- a/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
+++ b/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts
@@ -107,7 +107,7 @@ export class GitHubPullRequestCIModel extends Disposable {
  * Extract the GitHub Actions workflow run ID from a check run's details URL.
  * URLs follow the pattern: `https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}`
  */
-function parseWorkflowRunId(detailsUrl: string | undefined): number | undefined {
+export function parseWorkflowRunId(detailsUrl: string | undefined): number | undefined {
 	if (!detailsUrl) {
 		return undefined;
 	}
PATCH

echo "Patch applied successfully"
