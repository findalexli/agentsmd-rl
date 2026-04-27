#!/usr/bin/env bash
set -euo pipefail

cd /workspace/byterover-cli

# Idempotency guard
if grep -qF "**Overview:** `brv vc` provides git-based version control for your context tree." "src/server/templates/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/server/templates/skill/SKILL.md b/src/server/templates/skill/SKILL.md
@@ -9,7 +9,7 @@ Use the `brv` CLI to manage your project's long-term memory.
 Install: `npm install -g byterover-cli`
 Knowledge is stored in `.brv/context-tree/` as human-readable Markdown files.
 
-**No authentication needed.** `brv query` and `brv curate` work out of the box. Login is only required for cloud sync (`push`/`pull`/`space`) — ignore those if you don't need cloud features.
+**No authentication needed.** `brv query`, `brv curate`, and `brv vc` (local version control) work out of the box. Login is only required for remote sync (`brv vc push`/`brv vc pull`).
 
 ## Workflow
 1.  **Before Thinking:** Run `brv query` to understand existing patterns.
@@ -174,60 +174,131 @@ brv locations -f json
 
 JSON fields: `projectPath`, `contextTreePath`, `isCurrent`, `isActive`, `isInitialized`.
 
-### 6. Cloud Sync (Optional)
-**Overview:** Sync your local knowledge with a team via ByteRover's cloud service. Requires ByteRover authentication.
+### 6. Version Control
+**Overview:** `brv vc` provides git-based version control for your context tree. It uses standard git semantics — branching, committing, merging, history, and conflict resolution — all working locally with no authentication required. Remote sync with a team is optional. The legacy `brv push`, `brv pull`, and `brv space` commands are deprecated — use `brv vc push`, `brv vc pull`, and `brv vc clone`/`brv vc remote add` instead.
 
-**Setup steps:**
-1. Log in: Get an API key from your ByteRover account and authenticate:
+**Use this when:**
+- The user wants to track, commit, or inspect changes to the knowledge base
+- The user wants to branch, merge, or undo knowledge changes
+- The user wants to sync knowledge with a team (push/pull)
+- The user wants to connect to or clone a team space
+- The user asks about knowledge history or diffs
+
+**Do NOT use this when:**
+- The user wants to query or curate knowledge — use `brv query`/`brv curate` instead
+- The user wants to review pending curate operations — use `brv review` instead
+- Version control is not initialized and the user didn't ask to set it up
+
+**Commands:**
+
+Available commands: `init`, `status`, `add`, `commit`, `reset`, `log`, `branch`, `checkout`, `merge`, `config`, `clone`, `remote`, `fetch`, `push`, `pull`.
+
+#### First-Time Setup
+
+**Setup — local (no auth needed):**
+```bash
+brv vc init
+brv vc config user.name "Your Name"
+brv vc config user.email "you@example.com"
+```
+
+**Setup — clone a team space (requires `brv login`):**
 ```bash
 brv login --api-key sample-key-string
+brv vc clone https://byterover.dev/<team>/<space>.git
 ```
-2. List available spaces:
+
+**Setup — connect existing project to a remote (requires `brv login`):**
 ```bash
-brv space list
+brv login --api-key sample-key-string
+brv vc remote add origin https://byterover.dev/<team>/<space>.git
 ```
-Sample output:
+
+#### Local Workflow
+
+**Check status:**
+```bash
+brv vc status
 ```
-brv space list
-1. human-resources-team (team)
-   - a-department (space)
-   - b-department (space)
-2. marketing-team (team)
-   - c-department (space)
-   - d-department (space)
+
+**Stage and commit:**
+```bash
+brv vc add .                     # stage all
+brv vc add notes.md docs/        # stage specific files
+brv vc commit -m "add authentication patterns"
 ```
-3. Connect to a space:
+
+**View history:**
+```bash
+brv vc log
+brv vc log --limit 20
+brv vc log --all
+```
+
+**Unstage or undo:**
+```bash
+brv vc reset                     # unstage all files
+brv vc reset <file>              # unstage a specific file
+brv vc reset --soft HEAD~1       # undo last commit, keep changes staged
+brv vc reset --hard HEAD~1       # discard last commit and changes
+```
+
+#### Branch Management
+
+```bash
+brv vc branch                    # list branches
+brv vc branch feature/auth       # create a branch
+brv vc branch -a                 # list all (including remote-tracking)
+brv vc branch -d feature/auth    # delete a branch
+brv vc checkout feature/auth     # switch branch
+brv vc checkout -b feature/new   # create and switch
+```
+
+**Merge:**
 ```bash
-brv space switch --team human-resources-team --name a-department
+brv vc merge feature/auth        # merge into current branch
+brv vc merge --continue          # continue after resolving conflicts
+brv vc merge --abort             # abort a conflicted merge
 ```
 
-**Cloud sync commands:**
-Once connected, `brv push` and `brv pull` sync with that space.
+**Set upstream tracking:**
 ```bash
-# Pull team updates
-brv pull
+brv vc branch --set-upstream-to origin/main
+```
+
+#### Cloud Sync (Remote Operations)
+
+Requires ByteRover authentication (`brv login`) and a configured remote.
 
-# Push local changes
-brv push
+**Manage remotes:**
+```bash
+brv vc remote                    # show current remote
+brv vc remote add origin <url>   # add a remote
+brv vc remote set-url origin <url>  # update remote URL
+```
+
+**Fetch, pull, and push:**
+```bash
+brv vc fetch                     # fetch remote refs
+brv vc pull                      # fetch + merge remote commits
+brv vc push                      # push commits to cloud
+brv vc push -u origin main       # push and set upstream tracking
 ```
 
-**Switching spaces:**
-- Push local changes first (`brv push`) — switching is blocked if unsaved changes exist.
-- Then switch:
+**Clone a space:**
 ```bash
-brv space switch --team marketing-team --name d-department
+brv vc clone https://byterover.dev/<team>/<space>.git
 ```
-- The switch automatically pulls context from the new space.
 
 ## Data Handling
 
 **Storage**: All knowledge is stored as Markdown files in `.brv/context-tree/` within the project directory. Files are human-readable and version-controllable.
 
 **File access**: The `-f` flag on `brv curate` reads files from the current project directory only. Paths outside the project root are rejected. Maximum 5 files per command, text and document formats only.
 
-**LLM usage**: `brv query` and `brv curate` send context to a configured LLM provider for processing. The LLM sees the query or curate text and any included file contents. No data is sent to ByteRover servers unless you explicitly run `brv push`.
+**LLM usage**: `brv query` and `brv curate` send context to a configured LLM provider for processing. The LLM sees the query or curate text and any included file contents. No data is sent to ByteRover servers unless you explicitly run `brv vc push`.
 
-**Cloud sync**: `brv push` and `brv pull` require authentication (`brv login`) and send knowledge to ByteRover's cloud service. All other commands operate without ByteRover authentication.
+**Cloud sync**: `brv vc push` and `brv vc pull` require authentication (`brv login`) and sync knowledge with ByteRover's cloud service via git. All other commands operate without ByteRover authentication.
 
 ## Error Handling
 **User Action Required:**
PATCH

echo "Gold patch applied."
