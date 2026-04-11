#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for distinctive line from VOUCHED.td)
if [ -f ".github/VOUCHED.td" ] && grep -q 'adamdotdevin' .github/VOUCHED.td 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/.github/ISSUE_TEMPLATE/config.yml b/.github/ISSUE_TEMPLATE/config.yml
index 459ce25d05b9..52eec90991fe 100644
--- a/.github/ISSUE_TEMPLATE/config.yml
+++ b/.github/ISSUE_TEMPLATE/config.yml
@@ -1,4 +1,4 @@
-blank_issues_enabled: true
+blank_issues_enabled: false
 contact_links:
   - name: 💬 Discord Community
     url: https://discord.gg/opencode
diff --git a/.github/VOUCHED.td b/.github/VOUCHED.td
new file mode 100644
index 000000000000..2bdc9f6cecd8
--- /dev/null
+++ b/.github/VOUCHED.td
@@ -0,0 +1,17 @@
+# Vouched contributors for this project.
+#
+# See https://github.com/mitchellh/vouch for details.
+#
+# Syntax:
+#   - One handle per line (without @), sorted alphabetically.
+#   - Optional platform prefix: platform:username (e.g., github:user).
+#   - Denounce with minus prefix: -username or -platform:username.
+#   - Optional details after a space following the handle.
+adamdotdevin
+fwang
+iamdavidhill
+jayair
+kommander
+r44vc0rp
+rekram1-node
+thdxr
diff --git a/.github/workflows/compliance-close.yml b/.github/workflows/compliance-close.yml
new file mode 100644
index 000000000000..5b424d0adfa7
--- /dev/null
+++ b/.github/workflows/compliance-close.yml
@@ -0,0 +1,86 @@
+name: compliance-close
+
+on:
+  schedule:
+    # Run every 30 minutes to check for expired compliance windows
+    - cron: "*/30 * * * *"
+  workflow_dispatch:
+
+permissions:
+  contents: read
+  issues: write
+  pull-requests: write
+
+jobs:
+  close-non-compliant:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Close non-compliant issues and PRs after 2 hours
+        uses: actions/github-script@v7
+        with:
+          script: |
+            const { data: items } = await github.rest.issues.listForRepo({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              labels: 'needs:compliance',
+              state: 'open',
+              per_page: 100,
+            });
+
+            if (items.length === 0) {
+              core.info('No open issues/PRs with needs:compliance label');
+              return;
+            }
+
+            const now = Date.now();
+            const twoHours = 2 * 60 * 60 * 1000;
+
+            for (const item of items) {
+              const isPR = !!item.pull_request;
+              const kind = isPR ? 'PR' : 'issue';
+
+              const { data: comments } = await github.rest.issues.listComments({
+                owner: context.repo.owner,
+                repo: context.repo.repo,
+                issue_number: item.number,
+              });
+
+              const complianceComment = comments.find(c => c.body.includes('<!-- issue-compliance -->'));
+              if (!complianceComment) continue;
+
+              const commentAge = now - new Date(complianceComment.created_at).getTime();
+              if (commentAge < twoHours) {
+                core.info(`${kind} #${item.number} still within 2-hour window (${Math.round(commentAge / 60000)}m elapsed)`);
+                continue;
+              }
+
+              const closeMessage = isPR
+                ? 'This pull request has been automatically closed because it was not updated to meet our [contributing guidelines](../blob/dev/CONTRIBUTING.md) within the 2-hour window.\n\nFeel free to open a new pull request that follows our guidelines.'
+                : 'This issue has been automatically closed because it was not updated to meet our [contributing guidelines](../blob/dev/CONTRIBUTING.md) within the 2-hour window.\n\nFeel free to open a new issue that follows our issue templates.';
+
+              await github.rest.issues.createComment({
+                owner: context.repo.owner,
+                repo: context.repo.repo,
+                issue_number: item.number,
+                body: closeMessage,
+              });
+
+              if (isPR) {
+                await github.rest.pulls.update({
+                  owner: context.repo.owner,
+                  repo: context.repo.repo,
+                  pull_number: item.number,
+                  state: 'closed',
+                });
+              } else {
+                await github.rest.issues.update({
+                  owner: context.repo.owner,
+                  repo: context.repo.repo,
+                  issue_number: item.number,
+                  state: 'closed',
+                  state_reason: 'not_planned',
+                });
+              }
+
+              core.info(`Closed non-compliant ${kind} #${item.number} after 2-hour window`);
+            }
diff --git a/.github/workflows/duplicate-issues.yml b/.github/workflows/duplicate-issues.yml
index cbe8df5175b0..87e655fe4bf7 100644
--- a/.github/workflows/duplicate-issues.yml
+++ b/.github/workflows/duplicate-issues.yml
@@ -21,7 +21,7 @@ jobs:
       - name: Install opencode
         run: curl -fsSL https://opencode.ai/install | bash

-      - name: Check for duplicate issues
+      - name: Check duplicates and compliance
         env:
           OPENCODE_API_KEY: ${{ secrets.OPENCODE_API_KEY }}
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
@@ -34,30 +34,84 @@ jobs:
               "webfetch": "deny"
             }
         run: |
-          opencode run -m opencode/claude-haiku-4-5 "A new issue has been created:'
+          opencode run -m opencode/claude-haiku-4-5 "A new issue has been created:

-          Issue number:
-          ${{ github.event.issue.number }}
+          Issue number: ${{ github.event.issue.number }}

-          Lookup this issue and search through existing issues (excluding #${{ github.event.issue.number }}) in this repository to find any potential duplicates of this new issue.
+          Lookup this issue with gh issue view ${{ github.event.issue.number }}.
+
+          You have TWO tasks. Perform both, then post a SINGLE comment (if needed).
+
+          ---
+
+          TASK 1: CONTRIBUTING GUIDELINES COMPLIANCE CHECK
+
+          Check whether the issue follows our contributing guidelines and issue templates.
+
+          This project has three issue templates that every issue MUST use one of:
+
+          1. Bug Report - requires a Description field with real content
+          2. Feature Request - requires a verification checkbox and description, title should start with [FEATURE]:
+          3. Question - requires the Question field with real content
+
+          Additionally check:
+          - No AI-generated walls of text (long, AI-generated descriptions are not acceptable)
+          - The issue has real content, not just template placeholder text left unchanged
+          - Bug reports should include some context about how to reproduce
+          - Feature requests should explain the problem or need
+          - We want to push for having the user provide system description & information
+
+          Do NOT be nitpicky about optional fields. Only flag real problems like: no template used, required fields empty or placeholder text only, obviously AI-generated walls of text, or completely empty/nonsensical content.
+
+          ---
+
+          TASK 2: DUPLICATE CHECK
+
+          Search through existing issues (excluding #${{ github.event.issue.number }}) to find potential duplicates.
           Consider:
           1. Similar titles or descriptions
           2. Same error messages or symptoms
           3. Related functionality or components
           4. Similar feature requests

-          If you find any potential duplicates, please comment on the new issue with:
-          - A brief explanation of why it might be a duplicate
-          - Links to the potentially duplicate issues
-          - A suggestion to check those issues first
+          Additionally, if the issue mentions keybinds, keyboard shortcuts, or key bindings, note the pinned keybinds issue #4997.
+
+          ---
+
+          POSTING YOUR COMMENT:
+
+          Based on your findings, post a SINGLE comment on issue #${{ github.event.issue.number }}. Build the comment as follows:
+
+          If the issue is NOT compliant, start the comment with:
+          <!-- issue-compliance -->
+          Then explain what needs to be fixed and that they have 2 hours to edit the issue before it is automatically closed. Also add the label needs:compliance to the issue using: gh issue edit ${{ github.event.issue.number }} --add-label needs:compliance
+
+          If duplicates were found, include a section about potential duplicates with links.
+
+          If the issue mentions keybinds/keyboard shortcuts, include a note about #4997.
+
+          If the issue IS compliant AND no duplicates were found AND no keybind reference, do NOT comment at all.

           Use this format for the comment:
-          'This issue might be a duplicate of existing issues. Please check:
+
+          [If not compliant:]
+          <!-- issue-compliance -->
+          This issue doesn't fully meet our [contributing guidelines](../blob/dev/CONTRIBUTING.md).
+
+          **What needs to be fixed:**
+          - [specific reasons]
+
+          Please edit this issue to address the above within **2 hours**, or it will be automatically closed.
+
+          [If duplicates found, add:]
+          ---
+          This issue might be a duplicate of existing issues. Please check:
           - #[issue_number]: [brief description of similarity]

-          Feel free to ignore if none of these address your specific case.'
+          [If keybind-related, add:]
+          For keybind-related issues, please also check our pinned keybinds documentation: #4997

-          Additionally, if the issue mentions keybinds, keyboard shortcuts, or key bindings, please add a comment mentioning the pinned keybinds issue #4997:
-          'For keybind-related issues, please also check our pinned keybinds documentation: #4997'
+          [End with if not compliant:]
+          If you believe this was flagged incorrectly, please let a maintainer know.

-          If no clear duplicates are found, do not comment."
+          Remember: post at most ONE comment combining all findings. If everything is fine, post nothing."
diff --git a/.github/workflows/vouch-check-issue.yml b/.github/workflows/vouch-check-issue.yml
new file mode 100644
index 000000000000..94569f47312a
--- /dev/null
+++ b/.github/workflows/vouch-check-issue.yml
@@ -0,0 +1,96 @@
+name: vouch-check-issue
+
+on:
+  issues:
+    types: [opened]
+
+permissions:
+  contents: read
+  issues: write
+
+jobs:
+  check:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Check if issue author is denounced
+        uses: actions/github-script@v7
+        with:
+          script: |
+            const author = context.payload.issue.user.login;
+            const issueNumber = context.payload.issue.number;
+
+            // Skip bots
+            if (author.endsWith('[bot]')) {
+              core.info(`Skipping bot: ${author}`);
+              return;
+            }
+
+            // Read the VOUCHED.td file via API (no checkout needed)
+            let content;
+            try {
+              const response = await github.rest.repos.getContent({
+                owner: context.repo.owner,
+                repo: context.repo.repo,
+                path: '.github/VOUCHED.td',
+              });
+              content = Buffer.from(response.data.content, 'base64').toString('utf-8');
+            } catch (error) {
+              if (error.status === 404) {
+                core.info('No .github/VOUCHED.td file found, skipping check.');
+                return;
+              }
+              throw error;
+            }
+
+            // Parse the .td file for denounced users
+            const denounced = new Map();
+            for (const line of content.split('\n')) {
+              const trimmed = line.trim();
+              if (!trimmed || trimmed.startsWith('#')) continue;
+              if (!trimmed.startsWith('-')) continue;
+
+              const rest = trimmed.slice(1).trim();
+              if (!rest) continue;
+              const spaceIdx = rest.indexOf(' ');
+              const handle = spaceIdx === -1 ? rest : rest.slice(0, spaceIdx);
+              const reason = spaceIdx === -1 ? null : rest.slice(spaceIdx + 1).trim();
+
+              // Handle platform:username or bare username
+              // Only match bare usernames or github: prefix (skip other platforms)
+              const colonIdx = handle.indexOf(':');
+              if (colonIdx !== -1) {
+                const platform = handle.slice(0, colonIdx).toLowerCase();
+                if (platform !== 'github') continue;
+              }
+              const username = colonIdx === -1 ? handle : handle.slice(colonIdx + 1);
+              if (!username) continue;
+
+              denounced.set(username.toLowerCase(), reason);
+            }
+
+            // Check if the author is denounced
+            const reason = denounced.get(author.toLowerCase());
+            if (reason === undefined) {
+              core.info(`User ${author} is not denounced. Allowing issue.`);
+              return;
+            }
+
+            // Author is denounced — close the issue
+            const body = 'This issue has been automatically closed.';
+
+            await github.rest.issues.createComment({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              issue_number: issueNumber,
+              body,
+            });
+
+            await github.rest.issues.update({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              issue_number: issueNumber,
+              state: 'closed',
+              state_reason: 'not_planned',
+            });
+
+            core.info(`Closed issue #${issueNumber} from denounced user ${author}`);
diff --git a/.github/workflows/vouch-check-pr.yml b/.github/workflows/vouch-check-pr.yml
new file mode 100644
index 000000000000..470b8e0a5ad7
--- /dev/null
+++ b/.github/workflows/vouch-check-pr.yml
@@ -0,0 +1,93 @@
+name: vouch-check-pr
+
+on:
+  pull_request_target:
+    types: [opened]
+
+permissions:
+  contents: read
+  pull-requests: write
+
+jobs:
+  check:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Check if PR author is denounced
+        uses: actions/github-script@v7
+        with:
+          script: |
+            const author = context.payload.pull_request.user.login;
+            const prNumber = context.payload.pull_request.number;
+
+            // Skip bots
+            if (author.endsWith('[bot]')) {
+              core.info(`Skipping bot: ${author}`);
+              return;
+            }
+
+            // Read the VOUCHED.td file via API (no checkout needed)
+            let content;
+            try {
+              const response = await github.rest.repos.getContent({
+                owner: context.repo.owner,
+                repo: context.repo.repo,
+                path: '.github/VOUCHED.td',
+              });
+              content = Buffer.from(response.data.content, 'base64').toString('utf-8');
+            } catch (error) {
+              if (error.status === 404) {
+                core.info('No .github/VOUCHED.td file found, skipping check.');
+                return;
+              }
+              throw error;
+            }
+
+            // Parse the .td file for denounced users
+            const denounced = new Map();
+            for (const line of content.split('\n')) {
+              const trimmed = line.trim();
+              if (!trimmed || trimmed.startsWith('#')) continue;
+              if (!trimmed.startsWith('-')) continue;
+
+              const rest = trimmed.slice(1).trim();
+              if (!rest) continue;
+              const spaceIdx = rest.indexOf(' ');
+              const handle = spaceIdx === -1 ? rest : rest.slice(0, spaceIdx);
+              const reason = spaceIdx === -1 ? null : rest.slice(spaceIdx + 1).trim();
+
+              // Handle platform:username or bare username
+              // Only match bare usernames or github: prefix (skip other platforms)
+              const colonIdx = handle.indexOf(':');
+              if (colonIdx !== -1) {
+                const platform = handle.slice(0, colonIdx).toLowerCase();
+                if (platform !== 'github') continue;
+              }
+              const username = colonIdx === -1 ? handle : handle.slice(colonIdx + 1);
+              if (!username) continue;
+
+              denounced.set(username.toLowerCase(), reason);
+            }
+
+            // Check if the author is denounced
+            const reason = denounced.get(author.toLowerCase());
+            if (reason === undefined) {
+              core.info(`User ${author} is not denounced. Allowing PR.`);
+              return;
+            }
+
+            // Author is denounced — close the PR
+            await github.rest.issues.createComment({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              issue_number: prNumber,
+              body: 'This pull request has been automatically closed.',
+            });
+
+            await github.rest.pulls.update({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              pull_number: prNumber,
+              state: 'closed',
+            });
+
+            core.info(`Closed PR #${prNumber} from denounced user ${author}`);
diff --git a/.github/workflows/vouch-manage-by-issue.yml b/.github/workflows/vouch-manage-by-issue.yml
new file mode 100644
index 000000000000..863a8a8465ce
--- /dev/null
+++ b/.github/workflows/vouch-manage-by-issue.yml
@@ -0,0 +1,27 @@
+name: vouch-manage-by-issue
+
+on:
+  issue_comment:
+    types: [created]
+
+concurrency:
+  group: vouch-manage
+  cancel-in-progress: false
+
+permissions:
+  contents: write
+  issues: write
+  pull-requests: read
+
+jobs:
+  manage:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+
+      - uses: mitchellh/vouch/action/manage-by-issue@main
+        with:
+          issue-id: ${{ github.event.issue.number }}
+          comment-id: ${{ github.event.comment.id }}
+        env:
+          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 60b76a95e9f3..4bec009ef467 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -258,3 +258,49 @@ These are not strictly enforced, they are just general guidelines:
 ## Feature Requests

 For net-new functionality, start with a design conversation. Open an issue describing the problem, your proposed approach (optional), and why it belongs in OpenCode. The core team will help decide whether it should move forward; please wait for that approval instead of opening a feature PR directly.
+
+## Trust & Vouch System
+
+This project uses [vouch](https://github.com/mitchellh/vouch) to manage contributor trust. The vouch list is maintained in [`.github/VOUCHED.td`](.github/VOUCHED.td).
+
+### How it works
+
+- **Vouched users** are explicitly trusted contributors.
+- **Denounced users** are explicitly blocked. Issues and pull requests from denounced users are automatically closed. If you have been denounced, you can request to be unvouched by reaching out to a maintainer on [Discord](https://opencode.ai/discord)
+- **Everyone else** can participate normally — you don't need to be vouched to open issues or PRs.
+
+### For maintainers
+
+Collaborators with write access can manage the vouch list by commenting on any issue:
+
+- `vouch` — vouch for the issue author
+- `vouch @username` — vouch for a specific user
+- `denounce` — denounce the issue author
+- `denounce @username` — denounce a specific user
+- `denounce @username <reason>` — denounce with a reason
+- `unvouch` / `unvouch @username` — remove someone from the list
+
+Changes are committed automatically to `.github/VOUCHED.td`.
+
+### Denouncement policy
+
+Denouncement is reserved for users who repeatedly submit low-quality AI-generated contributions, spam, or otherwise act in bad faith. It is not used for disagreements or honest mistakes.
+
+## Issue Requirements
+
+All issues **must** use one of our issue templates:
+
+- **Bug report** — for reporting bugs (requires a description)
+- **Feature request** — for suggesting enhancements (requires verification checkbox and description)
+- **Question** — for asking questions (requires the question)
+
+Blank issues are not allowed. When a new issue is opened, an automated check verifies that it follows a template and meets our contributing guidelines. If an issue doesn't meet the requirements, you'll receive a comment explaining what needs to be fixed and have **2 hours** to edit the issue. After that, it will be automatically closed.
+
+Issues may be flagged for:
+
+- Not using a template
+- Required fields left empty or filled with placeholder text
+- AI-generated walls of text
+- Missing meaningful content
+
+If you believe your issue was incorrectly flagged, let a maintainer know.

PATCH

echo "Patch applied successfully."
