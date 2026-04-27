#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git comman" "plugins/compound-engineering/AGENTS.md" && grep -qF "description: \"Write or regenerate a value-first pull-request description (title " "plugins/compound-engineering/skills/ce-pr-description/SKILL.md" && grep -qF "`ce-pr-description` returns a `{title, body_file}` block (body in an OS temp fil" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/AGENTS.md b/plugins/compound-engineering/AGENTS.md
@@ -102,6 +102,12 @@ Skill content loaded at trigger time is carried in every subsequent message —
 - [ ] Use imperative/infinitive form (verb-first instructions)
 - [ ] Avoid second person ("you should") - use objective language ("To accomplish X, do Y")
 
+### Rationale Discipline
+
+Every line in `SKILL.md` loads on every invocation. Include rationale only when it changes what the agent does at runtime — if behavior wouldn't differ without the sentence, cut it.
+
+Keep rationale at the highest-level location that covers it; restate behavioral directives at the point they take effect. A 500-line skill shouldn't hinge on the agent remembering line 9 by line 400. Portability notes, defenses against mistakes the agent wasn't going to make, and meta-commentary about this repo's authoring rules belong in commit messages or `docs/solutions/`, not in the skill body.
+
 ### Cross-Platform User Interaction
 
 - [ ] When a skill needs to ask the user a question, instruct use of the platform's blocking question tool and name the known equivalents (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini)
@@ -136,7 +142,7 @@ Why: shell-heavy exploration causes avoidable permission prompts in sub-agent wo
 
 - [ ] Never instruct agents to use `find`, `ls`, `cat`, `head`, `tail`, `grep`, `rg`, `wc`, or `tree` through a shell for routine file discovery, content search, or file reading
 - [ ] Describe tools by capability class with platform hints — e.g., "Use the native file-search/glob tool (e.g., Glob in Claude Code)" — not by Claude Code-specific tool names alone
-- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no action chaining (`cmd1 && cmd2`, `cmd1 ; cmd2`) and no error suppression (`2>/dev/null`, `|| true`). Boolean conditions within if/while guards (`[ -n "$X" ] || [ -n "$Y" ]`) are fine — that is normal conditional logic, not action chaining. Simple pipes (e.g., `| jq .field`) and output redirection (e.g., `> file`) are acceptable when they don't obscure failures
+- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no action chaining (`cmd1 && cmd2`, `cmd1 ; cmd2`) and no error suppression (`2>/dev/null`, `|| true`). Two narrow exceptions: boolean conditions within if/while guards (`[ -n "$X" ] || [ -n "$Y" ]`) are fine — that is normal conditional logic, not action chaining. **Value-producing preparatory commands** (`VAR=$(cmd1) && cmd2 "$VAR"`) are also fine when `cmd2` strictly consumes `cmd1`'s output and splitting would require manually threading the value through model context across bash calls (e.g., `BODY_FILE=$(mktemp -u) && cat > "$BODY_FILE" <<EOF ... EOF`). Simple pipes (e.g., `| jq .field`) and output redirection (e.g., `> file`) are acceptable when they don't obscure failures
 - [ ] **Pre-resolution exception:** `!` backtick pre-resolution commands run at skill load time, not at agent runtime. They may use chaining (`&&`, `||`), error suppression (`2>/dev/null`), and fallback sentinels (e.g., `|| echo '__NO_CONFIG__'`) to produce a clean, parseable value for the model. This is the preferred pattern for environment probes (CLI availability, config file reads) that would otherwise require runtime shell calls with chaining. Example: `` !`command -v codex >/dev/null 2>&1 && echo "AVAILABLE" || echo "NOT_FOUND"` ``
 - [ ] Do not encode shell recipes for routine exploration when native tools can do the job; encode intent and preferred tool classes instead
 - [ ] For shell-only workflows (e.g., `gh`, `git`, `bundle show`, project CLIs), explicit command examples are acceptable when they are simple, task-scoped, and not chained together
diff --git a/plugins/compound-engineering/skills/ce-pr-description/SKILL.md b/plugins/compound-engineering/skills/ce-pr-description/SKILL.md
@@ -1,12 +1,12 @@
 ---
 name: ce-pr-description
-description: "Write or regenerate a value-first pull-request description (title + body) for the current branch's commits or for a specified PR. Use when the user says 'write a PR description', 'refresh the PR description', 'regenerate the PR body', 'rewrite this PR', 'freshen the PR', 'update the PR description', 'draft a PR body for this diff', 'describe this PR properly', 'generate the PR title', or pastes a GitHub PR URL / #NN / number. Also used internally by git-commit-push-pr (single-PR flow) and ce-pr-stack (per-layer stack descriptions) so all callers share one writing voice. Input is a natural-language prompt. A PR reference (a full GitHub PR URL, `pr:561`, `#561`, or a bare number alone) picks a specific PR; anything else is treated as optional steering for the default 'describe my current branch' mode. Returns structured {title, body} for the caller to apply via gh pr edit or gh pr create — this skill never edits the PR itself and never prompts for confirmation."
+description: "Write or regenerate a value-first pull-request description (title + body) for the current branch's commits or for a specified PR. Use when the user says 'write a PR description', 'refresh the PR description', 'regenerate the PR body', 'rewrite this PR', 'freshen the PR', 'update the PR description', 'draft a PR body for this diff', 'describe this PR properly', 'generate the PR title', or pastes a GitHub PR URL / #NN / number. Also used internally by git-commit-push-pr (single-PR flow) and ce-pr-stack (per-layer stack descriptions) so all callers share one writing voice. Input is a natural-language prompt. A PR reference (a full GitHub PR URL, `pr:561`, `#561`, or a bare number alone) picks a specific PR; anything else is treated as optional steering for the default 'describe my current branch' mode. Returns structured {title, body_file} (body written to an OS temp file) for the caller to apply via gh pr edit or gh pr create — this skill never edits the PR itself and never prompts for confirmation."
 argument-hint: "[PR ref e.g. pr:561 | #561 | URL] [free-text steering]"
 ---
 
 # CE PR Description
 
-Generate a conventional-commit-style title and a value-first body describing a pull request's work. Returns structured `{title, body}` for the caller to apply — this skill never invokes `gh pr edit` or `gh pr create`, and never prompts for interactive confirmation.
+Generate a conventional-commit-style title and a value-first body describing a pull request's work. Returns structured `{title, body_file}` for the caller to apply — this skill never invokes `gh pr edit` or `gh pr create`, and never prompts for interactive confirmation.
 
 Why a separate skill: several callers need the same writing logic without the single-PR interactive scaffolding that lives in `git-commit-push-pr`. `ce-pr-stack`'s splitting workflow runs this once per layer as a batch; `git-commit-push-pr` runs it inside its full-flow and refresh-mode paths. Extracting keeps one source of truth for the writing principles.
 
@@ -49,9 +49,9 @@ Steering text is always optional. If present, incorporate it alongside the diff-
 Return a structured result with two fields:
 
 - **`title`** -- conventional-commit format: `type: description` or `type(scope): description`. Under 72 characters. Choose `type` based on intent (feat/fix/refactor/docs/chore/perf/test), not file type. Pick the narrowest useful `scope` (skill or agent name, CLI area, or shared label); omit when no single label adds clarity.
-- **`body`** -- markdown following the writing principles below.
+- **`body_file`** -- absolute path to an OS temp file (created via `mktemp`) containing the body markdown that follows the writing principles below. Do not emit the body inline in the return.
 
-The caller decides whether to apply via `gh pr edit`, `gh pr create`, or discard. This skill does NOT call those commands itself.
+The caller decides whether to apply via `gh pr edit`, `gh pr create`, or discard, reading the body from `body_file` (e.g., `--body "$(cat "$BODY_FILE")"`). This skill does NOT call those commands itself. No cleanup is required — `mktemp` files live in OS temp storage, which the OS reaps on its own schedule.
 
 ---
 
@@ -122,7 +122,7 @@ gh pr view <pr-ref> --json number,state,title,body,baseRefName,baseRefOid,headRe
 
 Key JSON fields: `headRefOid` (PR head SHA — prefer over indexing into `commits`), `baseRefOid` (base-branch SHA), `headRepository` + `headRepositoryOwner` (PR source repo), `isCrossRepository`. There is no `baseRepository` field — the base repo is the one queried by `gh pr view` itself.
 
-If the returned `state` is not `OPEN`, report `"PR <number> is <state> (not open); cannot regenerate description"` and exit gracefully without output. Callers expecting `{title, body}` must handle this empty case.
+If the returned `state` is not `OPEN`, report `"PR <number> is <state> (not open); cannot regenerate description"` and exit gracefully without output. Callers expecting `{title, body_file}` must handle this empty case.
 
 **Determine whether the PR lives in the current working directory's repo** by parsing the URL's `<owner>/<repo>` path segments and comparing against `git remote get-url origin` (strip `.git` suffix; handle both `git@github.com:owner/repo` and `https://github.com/owner/repo` forms). If the URL repo matches `origin`'s repo, route to the local-git path (Case A). Otherwise route to the API-only path (Case B). Bare numbers and `#NN` forms implicitly target the current repo → Case A.
 
@@ -344,21 +344,31 @@ Assemble the body in this order:
 
 ---
 
-## Step 9: Return `{title, body}`
+## Step 9: Return `{title, body_file}`
 
-Return the composed title and body to the caller. Do not call `gh pr edit`, `gh pr create`, or any other mutating command. Do not ask the user to confirm. The caller owns apply.
+Write the composed body to an OS temp file, then return the title and the file path. Do not call `gh pr edit`, `gh pr create`, or any other mutating command. Do not ask the user to confirm — the caller owns apply.
 
-Format the return as a clearly labeled block so the caller can extract cleanly:
+```bash
+BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/ce-pr-body.XXXXXX") && cat > "$BODY_FILE" <<'__CE_PR_BODY_END__' && echo "$BODY_FILE"
+<the composed body markdown goes here, verbatim>
+__CE_PR_BODY_END__
+```
+
+The quoted sentinel `'__CE_PR_BODY_END__'` keeps `$VAR`, backticks, `${...}`, and any literal `EOF` inside the body from being expanded or clashing with the terminator. Keep `echo "$BODY_FILE"` chained with `&&` so a failed `mktemp` or write never yields a success exit status with a path to a missing file.
+
+Format the return as a clearly labeled block the caller can extract cleanly:
 
 ```
 === TITLE ===
 <title line>
 
-=== BODY ===
-<body markdown>
+=== BODY_FILE ===
+<absolute path to the mktemp body file>
 ```
 
-If Step 1 exited gracefully (closed/merged PR, invalid range, empty commit list), return no title or body — just the reason string.
+Do not emit the body markdown in the return block — the caller reads it from `BODY_FILE`.
+
+If Step 1 exited gracefully (closed/merged PR, invalid range, empty commit list), do not create a body file — just return the reason string.
 
 ---
 
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -69,24 +69,21 @@ Read the current PR description to drive the compare-and-confirm step later:
 gh pr view --json body --jq '.body'
 ```
 
-**Generate the updated title and body** — load the `ce-pr-description` skill with the PR URL from DU-2 (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when invoked from a worktree or subdirectory where the current repo is ambiguous. If the user provided a focus (e.g., "include the benchmarking results"), append it as free-text steering after the URL. The skill returns a `{title, body}` block without applying or prompting.
+**Generate the updated title and body** — load the `ce-pr-description` skill with the PR URL from DU-2 (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when invoked from a worktree or subdirectory where the current repo is ambiguous. If the user provided a focus (e.g., "include the benchmarking results"), append it as free-text steering after the URL. The skill returns a `{title, body_file}` block (body in an OS temp file) without applying or prompting.
 
-If `ce-pr-description` returns a "not open" or other graceful-exit message instead of a `{title, body}` pair, report that message and stop.
+If `ce-pr-description` returns a "not open" or other graceful-exit message instead of a `{title, body_file}` pair, report that message and stop.
 
 **Evidence decision:** `ce-pr-description` preserves any existing `## Demo` or `## Screenshots` block from the current body by default. If the user's focus asks to refresh or remove evidence, pass that intent as steering text — the skill will honor it. If no evidence block exists and one would benefit the reader, invoke `ce-demo-reel` separately to capture, then re-invoke `ce-pr-description` with updated steering that references the captured evidence.
 
-**Compare and confirm** — briefly explain what the new description covers differently from the old one. This helps the user decide whether to apply; the description itself does not narrate these differences.
+**Compare and confirm** — briefly explain what the new description covers differently from the old one. This helps the user decide whether to apply; the description itself does not narrate these differences. Summarize from the body already in context (from the bash call that wrote `body_file`); do not `cat` the temp file, which would re-emit the body.
 
 - If the user provided a focus, confirm it was addressed.
 - Ask the user to confirm before applying.
 
-If confirmed, apply with the returned title and body:
+If confirmed, apply with the returned title and body file:
 
 ```bash
-gh pr edit --title "<returned title>" --body "$(cat <<'EOF'
-<returned body>
-EOF
-)"
+gh pr edit --title "<returned title>" --body "$(cat "<returned body_file>")"
 ```
 
 Report the PR URL.
@@ -137,7 +134,7 @@ Priority order for commit messages and PR titles:
 
 Use the current branch and existing PR check from context. If the branch is empty, report detached HEAD and stop.
 
-If the PR check returned `state: OPEN`, note the URL -- this is the existing-PR flow. Continue to Step 4 and 5 (commit any pending work and push), then go to Step 7 to ask whether to rewrite the description. Only run Step 6 (which generates a new description via `ce-pr-description`) if the user confirms the rewrite; Step 7's existing-PR sub-path consumes the `{title, body}` that Step 6 produces. Otherwise (no open PR), continue through Steps 6, 7, and 8 in order.
+If the PR check returned `state: OPEN`, note the URL -- this is the existing-PR flow. Continue to Step 4 and 5 (commit any pending work and push), then go to Step 7 to ask whether to rewrite the description. Only run Step 6 (which generates a new description via `ce-pr-description`) if the user confirms the rewrite; Step 7's existing-PR sub-path consumes the `{title, body_file}` that Step 6 produces. Otherwise (no open PR), continue through Steps 6, 7, and 8 in order.
 
 ### Step 4: Branch, stage, and commit
 
@@ -205,21 +202,18 @@ When evidence is not possible (docs-only, markdown-only, changelog-only, release
 - **For a new PR** (no existing PR found in Step 3): invoke with `base:<base-remote>/<base-branch>` using the already-resolved base from earlier in this step, so `ce-pr-description` describes the correct commit range even when the branch targets a non-default base (e.g., `develop`, `release/*`). Append any captured-evidence context or user focus as free-text steering (e.g., "include the captured demo: <URL> as a `## Demo` section").
 - **For an existing PR** (found in Step 3): invoke with the full PR URL from the Step 3 context (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when invoked from a worktree or subdirectory; the skill reads the PR's own `baseRefName` so no `base:` override is needed. Append any focus steering as free text after the URL.
 
-`ce-pr-description` returns a `{title, body}` block. It applies the value-first writing principles, commit classification, sizing, narrative framing, writing voice, visual communication, numbering rules, and the Compound Engineering badge footer internally. Use the returned values verbatim in Step 7; do not layer manual edits onto them unless a focused adjustment is required (e.g., splicing an evidence block captured in this step that was not passed as steering text).
+`ce-pr-description` returns a `{title, body_file}` block (body in an OS temp file). It applies the value-first writing principles, commit classification, sizing, narrative framing, writing voice, visual communication, numbering rules, and the Compound Engineering badge footer internally. Use the returned values verbatim in Step 7; do not layer manual edits onto them unless a focused adjustment is required (e.g., splicing an evidence block captured in this step that was not passed as steering text — in that case, edit the body file directly before applying).
 
-If `ce-pr-description` returns a graceful-exit message instead of `{title, body}` (e.g., closed PR, no commits to describe, base ref unresolved), report the message and stop — do not create or edit the PR.
+If `ce-pr-description` returns a graceful-exit message instead of `{title, body_file}` (e.g., closed PR, no commits to describe, base ref unresolved), report the message and stop — do not create or edit the PR.
 
 ### Step 7: Create or update the PR
 
 #### New PR (no existing PR from Step 3)
 
-Using the `{title, body}` returned by `ce-pr-description`:
+Using the `{title, body_file}` returned by `ce-pr-description`:
 
 ```bash
-gh pr create --title "<returned title>" --body "$(cat <<'EOF'
-<returned body>
-EOF
-)"
+gh pr create --title "<returned title>" --body "$(cat "<returned body_file>")"
 ```
 
 Keep the title under 72 characters; `ce-pr-description` already emits a conventional-commit title in that range.
@@ -228,13 +222,10 @@ Keep the title under 72 characters; `ce-pr-description` already emits a conventi
 
 The new commits are already on the PR from Step 5. Report the PR URL, then ask whether to rewrite the description.
 
-- If **yes**, run Step 6 now to generate `{title, body}` via `ce-pr-description` (passing the existing PR URL as `pr:`), then apply the returned title and body:
+- If **yes**, run Step 6 now to generate `{title, body_file}` via `ce-pr-description` (passing the existing PR URL as `pr:`), then apply the returned title and body file:
 
   ```bash
-  gh pr edit --title "<returned title>" --body "$(cat <<'EOF'
-  <returned body>
-  EOF
-  )"
+  gh pr edit --title "<returned title>" --body "$(cat "<returned body_file>")"
   ```
 
 - If **no** -- skip Step 6 entirely and finish. Do not run delegation or evidence capture when the user declined the rewrite.
PATCH

echo "Gold patch applied."
