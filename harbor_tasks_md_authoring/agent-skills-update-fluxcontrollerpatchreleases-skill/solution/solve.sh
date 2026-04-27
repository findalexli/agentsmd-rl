#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "`gh api graphql -f query='{ repository(owner:\"<o>\",name:\"<r>\") { pullRequest(num" "internal/skills/flux-controller-patch-releases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/internal/skills/flux-controller-patch-releases/SKILL.md b/internal/skills/flux-controller-patch-releases/SKILL.md
@@ -24,6 +24,85 @@ Supported controllers:
 - `source-controller`
 - `source-watcher`
 
+## Important rules
+
+- **Go deep until you block, then switch.** Drive one controller all the way
+  through every step you can do locally — branch, changelog commit, version
+  bump commit, push, open PR — before switching to the next. Only move on
+  when you hit something you cannot progress (CI running, PR awaiting review,
+  tag workflow running). The moment something unblocks (PR merged, CI green,
+  workflow finished), come back to it immediately — do not finish the current
+  controller's local work first if an earlier one is ready to advance.
+- **Never block the conversation on long-running operations.** CI checks,
+  release workflow runs, tag-triggered workflows, and similar waits must be
+  watched in the background so the user can keep steering and so you can pick
+  up any other controller the moment it unblocks. When a background watch
+  completes, report the result and proceed.
+- **Always quote PR/issue links as full URLs** (e.g.
+  `https://github.com/fluxcd/helm-controller/pull/1465`), never the
+  `<owner>/<repo>#<number>` shorthand — full URLs are clickable from the
+  user's terminal, the shorthand is not.
+- **Start background watches on every PR immediately after opening it.** Kick
+  off `gh pr checks <num> -R fluxcd/<repo> --watch` in the background as
+  soon as the PR is created so CI status lands in the conversation the
+  moment it finishes. Do the same for tag-triggered release workflows
+  (`gh run watch <id> -R fluxcd/<repo>` in the background). Do not wait
+  until "everything is pushed" to start watching — start watching the first
+  PR while you prepare the second.
+- **Also start a background approval watch per PR.** `gh pr checks --watch`
+  only covers CI; it does not fire on maintainer approval. Poll the review
+  state in the background so you are notified the moment it flips to
+  APPROVED + CLEAN:
+  ```
+  while :; do
+    state=$(gh pr view <num> -R fluxcd/<repo> --json mergeStateStatus,reviewDecision --jq '.reviewDecision+" "+.mergeStateStatus')
+    case "$state" in "APPROVED CLEAN") echo "$state"; break;; esac
+    sleep 30
+  done
+  ```
+  Run this in the background; when it exits, merge the PR and proceed.
+- Every git commit must use `-s` (sign-off). Never include Co-Authored-By
+  lines, your own name, or any AI attribution in commit messages, PR titles,
+  or PR descriptions. This applies to all PRs, including PRs that update this
+  skill file itself.
+- Always wait for CI to go green before merging any PR.
+- You cannot approve your own PRs. If a PR was opened by the git user driving
+  the session, ask a maintainer to approve it (or confirm it is already
+  approved) before merging.
+- **Merge release PRs yourself** (controller release PRs, changelog cherry-pick
+  PRs) as soon as CI is green **and** a maintainer has approved. No need to
+  ask the user to click merge — act on it immediately so the next step (tag
+  push, etc.) unblocks. This applies only to PRs opened with the user's
+  account during this session.
+- **Review feedback on release PRs is applied by amending**, not by adding
+  new commits. A release PR must stay at exactly two commits
+  (`Add changelog entry for vX.Y.Z` and `Release vX.Y.Z`). When the fix
+  belongs in the changelog, amend the changelog commit; when it belongs in
+  the release bump, amend that one. Use
+  `git reset --soft HEAD~2` + re-commit, or an interactive rebase, then
+  `git push --force-with-lease`.
+- **After applying a review fix, reply `Fixed, thanks!` on the thread and
+  resolve it.** Reply via
+  `gh api repos/<owner>/<repo>/pulls/<n>/comments/<cid>/replies -f body='Fixed, thanks!'`
+  and resolve via the GraphQL `resolveReviewThread` mutation. Find thread
+  IDs with
+  `gh api graphql -f query='{ repository(owner:"<o>",name:"<r>") { pullRequest(number:<n>) { reviewThreads(first:50) { nodes { id isResolved comments(first:1){nodes{databaseId body}} } } } } }'`.
+- Do **not** watch CI on the skill-update PR continuously — it only needs to
+  merge at the very end of the procedure, so check CI right before merging
+  rather than keeping a watch open throughout the session.
+- Tags must be annotated and signed (`git tag -s -m ...`). Never create
+  release tags through the GitHub API — that produces lightweight tags which
+  break `git tag -v` verification.
+- Strictly follow the git commands documented in the release flow below. Do
+  not invent substitutions or skip steps — each step has a reason.
+- **Do not declare a controller "done" until every step in the Release Flow
+  below has been executed for it**, including the final changelog
+  cherry-pick PR back to `main` (step 11). Merging the release PR and
+  tagging is *not* the last step. Before reporting completion, walk through
+  each controller against the numbered steps and confirm each one ran.
+- PRs opened by this procedure use the commit subject as the PR title and an
+  empty body.
+
 ## Preconditions
 
 - Read the upstream procedure at `website/content/en/flux/releases/procedure.md`,
@@ -128,6 +207,17 @@ Rules:
 - Tag from the release series branch merge commit, not from the release prep branch.
 - Cherry-pick only the changelog commit back to `main`, not the release version bump.
 
+## Updating this skill
+
+- Improvements to this skill should land as a single-commit PR on a dedicated
+  branch. When accumulating more changes during a release session, amend and
+  force-push rather than adding new commits.
+- Keep the skill-update PR open during the release session and merge it
+  **last**, after all controller patch releases are done. Session learnings
+  tend to surface throughout the flow; amend them in as they come up.
+- Do not leak session-specific state, downstream/enterprise distribution
+  details, or AI attribution into the skill file.
+
 ## Useful Local Queries
 
 - Release branches:
PATCH

echo "Gold patch applied."
