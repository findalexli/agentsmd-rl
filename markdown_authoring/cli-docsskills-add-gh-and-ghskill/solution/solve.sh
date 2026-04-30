#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "description: Manage agent skills with gh skill. Use this skill to discover, prev" "skills/gh-skill/SKILL.md" && grep -qF "description: Patterns for invoking the GitHub CLI (gh) from agents. Covers struc" "skills/gh/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/gh-skill/SKILL.md b/skills/gh-skill/SKILL.md
@@ -0,0 +1,116 @@
+---
+name: gh-skill
+description: Manage agent skills with gh skill. Use this skill to discover, preview, install, update, and publish Agent Skills so an agent can self-manage the skills available in its environment.
+---
+
+# Managing skills with `gh skill`
+
+`gh skill` installs, previews, searches, updates, and publishes
+[Agent Skills](https://agentskills.io). An agent can use it to keep its
+own skill set in sync with one or more GitHub repositories.
+
+The command is also aliased as `gh skills`. Prefer the canonical singular
+`gh skill` in scripts and docs.
+
+## Search
+
+```bash
+gh skill search <query>                                  # free-text search
+gh skill search <query> --owner <org>                    # restrict to one owner
+gh skill search <query> --limit 20 --page 2
+gh skill search <query> --json skillName,repo,description
+```
+
+## Preview before installing
+
+```bash
+gh skill preview <owner>/<repo> <skill-name>
+gh skill preview <owner>/<repo> <skill-name>@v1.2.0   # pin a version
+```
+
+## Install
+
+```bash
+gh skill install <owner>/<repo> <skill-name>
+gh skill install <owner>/<repo> <skill-name>@v1.2.0
+gh skill install <owner>/<repo> skills/<scope>/<skill-name>   # exact path, fastest
+gh skill install ./local-skills-repo --from-local
+```
+
+`<owner>/<repo>` and `<skill-name>` are both required.
+
+Useful flags:
+
+- `--agent <id>` - target host (e.g. `github-copilot`, `claude-code`,
+  `cursor`, `codex`, `gemini-cli`). Repeat for multiple. Default is
+  `github-copilot` when non-interactive. You should know what agent you are,
+  so set this appropriately to install for yourself.
+- `--scope project|user` - `project` (default) writes inside the current
+  git repo; `user` writes to the home directory and applies everywhere.
+- `--pin <ref>` - pin to a tag, branch, or commit SHA. Mutually exclusive
+  with `--from-local` and with inline `@version` syntax.
+- `--allow-hidden-dirs` - also discover skills under dot-directories such
+  as `.claude/skills/`. Don't use this unless you need to, it comes with risks.
+- `--force` - overwrite an existing install.
+
+## Update
+
+```bash
+gh skill update --all          # update every installed skill
+gh skill update <skill>        # update one
+gh skill update <skill> --force
+gh skill update --unpin        # drop the pin and move to latest
+```
+
+## Publish
+
+Publishing turns a repo into a discoverable skill source. Skills are
+discovered with these conventions:
+
+- `skills/<name>/SKILL.md`
+- `skills/<scope>/<name>/SKILL.md`
+- `<name>/SKILL.md` (root-level)
+- `plugins/<scope>/skills/<name>/SKILL.md`
+
+Each `SKILL.md` needs YAML frontmatter:
+
+```yaml
+---
+name: my-skill                # must equal the directory name
+description: One sentence...  # required, recommended <= 1024 chars
+license: MIT                  # optional but recommended
+---
+```
+
+### Validate, then publish
+
+```bash
+gh skill publish --dry-run                 # validate only, no release
+gh skill publish --dry-run ./path/to/repo  # validate a specific dir
+gh skill publish --fix                     # auto-strip install metadata
+gh skill publish --tag v1.0.0              # non-interactive publish
+gh skill publish                           # interactive publish flow
+```
+
+`--fix` and `--dry-run` are mutually exclusive. `--fix` only rewrites
+install-injected `metadata.github-*` keys and does not publish; commit
+the result and re-run `publish`.
+
+The publish flow will:
+
+1. Add the `agent-skills` topic to the repo (so search can find it).
+2. Use `--tag` (or prompt for one in a TTY).
+3. Auto-push any unpushed commits.
+4. Create a GitHub release with auto-generated notes.
+
+Always pass `--tag` so it doesn't fall through to the interactive flow.
+
+## Self-management pattern for agents
+
+A reasonable loop:
+
+1. `gh skill search <topic> --json skillName,repo,namespace`
+2. `gh skill preview <repo> <skill>` to inspect the `SKILL.md`.
+3. `gh skill install <repo> <skill> --agent <host> --pin <ref>` for a
+   reproducible install.
+4. Periodically `gh skill update --all` to refresh.
\ No newline at end of file
diff --git a/skills/gh/SKILL.md b/skills/gh/SKILL.md
@@ -0,0 +1,81 @@
+---
+name: gh
+description: Patterns for invoking the GitHub CLI (gh) from agents. Covers structured output, pagination, repo targeting, search vs list, gh api fallback.
+---
+
+# Reference
+
+## Interactivity policy
+
+`gh` already does the right thing in non-TTY contexts: it skips the pager,
+strips ANSI color, and errors out fast with a helpful message instead of
+prompting (e.g. `must provide --title and --body when not running interactively`).
+You don't need to defensively set `GH_PAGER` or pass `--no-pager` (no such
+flag exists).
+
+## Parsing JSON
+
+Human output from `gh` is column-formatted. If you want structured data:
+
+- Add `--json field1,field2,...` for structured output.
+- Run a command with `--json` and **no field list** to print the full set of
+  available fields, then pick what you need.
+- Use `--jq '<expr>'` for filtering without piping through a separate `jq`.
+- Use `--template '<go-template>'` (alongside `--json`) when you want shaped
+  text output. Note that `--template`/`-T` collides with a body-template flag
+  on a few commands (e.g. `gh pr create -T`, `gh issue create -T`); always
+  check `--help` before assuming which one you're hitting.
+
+## Pagination and silent truncation
+
+List commands cap results.
+
+- `gh issue list`, `gh pr list`, `gh search ...`: pass `-L N` (`--limit N`).
+  The default is usually 30.
+- `gh issue list` / `gh pr list` do not expose aggregate totals like
+  `totalCount` via `--json`. If you need a true total, use `gh api graphql`
+  to query `totalCount`; otherwise, treat `-L` as the cap for the current call.
+- For raw API calls use `gh api --paginate <path>`. Combine with
+  `--jq` and (optionally) `--slurp` to assemble one array.
+
+## Repo targeting
+
+`gh` infers the repo from the cwd's git remotes. 
+
+Pass `--repo OWNER/REPO` (`-R`) to override the resolved CWD repo.
+
+## Search vs list
+
+- `gh search issues|prs|code|repos|commits|users` uses GitHub's search
+  index and accepts the full search syntax (`is:open`, `author:`,
+  `label:`, `repo:owner/name`, `in:title`, ...). Pass the entire query as
+  one quoted string, the same way you would for `--search`:
+  `gh search issues "is:open author:foo repo:cli/cli"`. Prefer it for
+  anything cross-repo or filtered by author/label.
+- `gh issue list --search "..."` and `gh pr list --search "..."` accept
+  the same syntax but are scoped to one repo.
+
+## Fall back to `gh api` for anything `--json` doesn't expose
+
+Sometimes useful data isn't on the typed commands. Examples:
+
+- Review-thread comments on a PR: `gh api repos/{owner}/{repo}/pulls/{n}/comments`
+  (the `--comments` flag on `gh pr view` shows issue-level comments only).
+- Arbitrary GraphQL: `gh api graphql -f query='...' -F var=value`.
+- REST shortcuts: `gh api repos/{owner}/{repo}/...` - note the
+  `{owner}/{repo}` placeholder is filled in for you when run from a repo
+  with detected remotes; pass them literally if you want determinism.
+
+## Authentication
+
+- `gh auth status` prints the active host(s), user, and which env var (if
+  any) is being honored.
+- `gh auth status --json` is supported.
+
+## Other notes
+
+- `gh pr checkout <n>` switches branches. Use `gh pr diff <n>` or
+  `gh pr view <n>` if you only need to read.
+- `NO_COLOR`, `CLICOLOR_FORCE`, and `GH_FORCE_TTY` are honored. Set
+  `GH_FORCE_TTY=1` if you want TTY-style output (colors, tables, the
+  pager, interactivity) inside an agent harness; leave it unset unless needed.
PATCH

echo "Gold patch applied."
