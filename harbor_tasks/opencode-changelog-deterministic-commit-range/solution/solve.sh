#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if fix is already applied
if grep -q 'async function latest' script/changelog.ts 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.gitignore b/.gitignore
index c287d91ac122..52a5a0459626 100644
--- a/.gitignore
+++ b/.gitignore
@@ -25,6 +25,7 @@ target
 
 # Local dev files
 opencode-dev
+UPCOMING_CHANGELOG.md
 logs/
 *.bun-build
 tsconfig.tsbuildinfo
diff --git a/.opencode/command/changelog.md b/.opencode/command/changelog.md
index 271e7eba1866..f0ff1e422dee 100644
--- a/.opencode/command/changelog.md
+++ b/.opencode/command/changelog.md
@@ -2,22 +2,43 @@
 model: opencode/kimi-k2.5
 ---
 
-create UPCOMING_CHANGELOG.md
-
-it should have sections
-
-```
-## TUI
-
-## Desktop
-
-## Core
-
-## Misc
-```
-
-fetch the latest github release for this repository to determine the last release version.
-
-find each PR that was merged since the last release
-
-for each PR spawn a subagent to summarize what the PR was about. focus on user facing changes. if it was entirely internal or code related you can ignore it. also skip docs updates. each subagent should append its summary to UPCOMING_CHANGELOG.md into the appropriate section.
+Create `UPCOMING_CHANGELOG.md` from the structured changelog input below.
+If `UPCOMING_CHANGELOG.md` already exists, ignore its current contents completely.
+Do not preserve, merge, or reuse text from the existing file.
+
+Any command arguments are passed directly to `bun script/changelog.ts`.
+Use `--from` / `-f` and `--to` / `-t` to preview a specific release range.
+
+The input already contains the exact commit range since the last non-draft release.
+The commits are already filtered to the release-relevant packages and grouped into
+the release sections. Do not fetch GitHub releases, PRs, or build your own commit list.
+The input may also include a `## Community Contributors Input` section.
+
+Before writing any entry you keep, inspect the real diff with
+`git show --stat --format='' <hash>` or `git show --format='' <hash>` so the
+summary reflects the actual user-facing change and not just the commit message.
+Do not use `git log` or author metadata when deciding attribution.
+
+Rules:
+
+- Write the final file with sections in this order:
+  `## Core`, `## TUI`, `## Desktop`, `## SDK`, `## Extensions`
+- Only include sections that have at least one notable entry
+- Keep one bullet per commit you keep
+- Skip commits that are entirely internal, CI, tests, refactors, or otherwise not user-facing
+- Start each bullet with a capital letter
+- Prefer what changed for users over what code changed internally
+- Do not copy raw commit prefixes like `fix:` or `feat:` or trailing PR numbers like `(#123)`
+- Community attribution is deterministic: only preserve an existing `(@username)` suffix from the changelog input
+- If an input bullet has no `(@username)` suffix, do not add one
+- Never add a new `(@username)` suffix from `git show`, commit authors, names, or email addresses
+- If no notable entries remain and there is no contributor block, write exactly `No notable changes.`
+- If no notable entries remain but there is a contributor block, omit all release sections and return only the contributor block
+- If the input contains `## Community Contributors Input`, append the block below that heading to the end of the final file verbatim
+- Do not add, remove, rewrite, or reorder contributor names or commit titles in that block
+- Do not derive the thank-you section from the main summary bullets
+- Do not include the heading `## Community Contributors Input` in the final file
+
+## Changelog Input
+
+!`bun script/changelog.ts $ARGUMENTS`
diff --git a/script/changelog.ts b/script/changelog.ts
index 5fc30a228bfb..3c3a659e7154 100755
--- a/script/changelog.ts
+++ b/script/changelog.ts
@@ -1,33 +1,11 @@
 #!/usr/bin/env bun
 
 import { $ } from "bun"
-import { createOpencode } from "@opencode-ai/sdk/v2"
 import { parseArgs } from "util"
-import { Script } from "@opencode-ai/script"
 
 type Release = {
   tag_name: string
   draft: boolean
-  prerelease: boolean
-}
-
-export async function getLatestRelease(skip?: string) {
-  const data = await fetch("https://api.github.com/repos/anomalyco/opencode/releases?per_page=100").then((res) => {
-    if (!res.ok) throw new Error(res.statusText)
-    return res.json()
-  })
-
-  const releases = data as Release[]
-  const target = skip?.replace(/^v/, "")
-
-  for (const release of releases) {
-    if (release.draft) continue
-    const tag = release.tag_name.replace(/^v/, "")
-    if (target && tag === target) continue
-    return tag
-  }
-
-  throw new Error("No releases found")
 }
 
 type Commit = {
@@ -37,237 +15,218 @@ type Commit = {
   areas: Set<string>
 }
 
-export async function getCommits(from: string, to: string): Promise<Commit[]> {
-  const fromRef = from.startsWith("v") ? from : `v${from}`
-  const toRef = to === "HEAD" ? to : to.startsWith("v") ? to : `v${to}`
+type User = Map<string, Set<string>>
+type Diff = {
+  sha: string
+  login: string | null
+  message: string
+}
+
+const repo = process.env.GH_REPO ?? "anomalyco/opencode"
+const bot = ["actions-user", "opencode", "opencode-agent[bot]"]
+const team = [
+  ...(await Bun.file(new URL("../.github/TEAM_MEMBERS", import.meta.url))
+    .text()
+    .then((x) => x.split(/\r?\n/).map((x) => x.trim()))
+    .then((x) => x.filter((x) => x && !x.startsWith("#")))),
+  ...bot,
+]
+const order = ["Core", "TUI", "Desktop", "SDK", "Extensions"] as const
+const sections = {
+  core: "Core",
+  tui: "TUI",
+  app: "Desktop",
+  tauri: "Desktop",
+  sdk: "SDK",
+  plugin: "SDK",
+  "extensions/zed": "Extensions",
+  "extensions/vscode": "Extensions",
+  github: "Extensions",
+} as const
+
+function ref(input: string) {
+  if (input === "HEAD") return input
+  if (input.startsWith("v")) return input
+  if (input.match(/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/)) return `v${input}`
+  return input
+}
 
-  // Get commit data with GitHub usernames from the API
-  const compare =
-    await $`gh api "/repos/anomalyco/opencode/compare/${fromRef}...${toRef}" --jq '.commits[] | {sha: .sha, login: .author.login, message: .commit.message}'`.text()
+async function latest() {
+  const data = await $`gh api "/repos/${repo}/releases?per_page=100"`.json()
+  const release = (data as Release[]).find((item) => !item.draft)
+  if (!release) throw new Error("No releases found")
+  return release.tag_name.replace(/^v/, "")
+}
 
-  const commitData = new Map<string, { login: string | null; message: string }>()
-  for (const line of compare.split("\n").filter(Boolean)) {
-    const data = JSON.parse(line) as { sha: string; login: string | null; message: string }
-    commitData.set(data.sha, { login: data.login, message: data.message.split("\n")[0] ?? "" })
+async function diff(base: string, head: string) {
+  const list: Diff[] = []
+  for (let page = 1; ; page++) {
+    const text =
+      await $`gh api "/repos/${repo}/compare/${base}...${head}?per_page=100&page=${page}" --jq '.commits[] | {sha: .sha, login: .author.login, message: .commit.message}'`.text()
+    const batch = text
+      .split("\n")
+      .filter(Boolean)
+      .map((line) => JSON.parse(line) as Diff)
+    if (batch.length === 0) break
+    list.push(...batch)
+    if (batch.length < 100) break
   }
+  return list
+}
 
-  // Get commits that touch the relevant packages
-  const log =
-    await $`git log ${fromRef}..${toRef} --oneline --format="%H" -- packages/opencode packages/sdk packages/plugin packages/desktop packages/app sdks/vscode packages/extensions github`.text()
-  const hashes = log.split("\n").filter(Boolean)
+function section(areas: Set<string>) {
+  const priority = ["core", "tui", "app", "tauri", "sdk", "plugin", "extensions/zed", "extensions/vscode", "github"]
+  for (const area of priority) {
+    if (areas.has(area)) return sections[area as keyof typeof sections]
+  }
+  return "Core"
+}
+
+function reverted(commits: Commit[]) {
+  const seen = new Map<string, Commit>()
+
+  for (const commit of commits) {
+    const match = commit.message.match(/^Revert "(.+)"$/)
+    if (match) {
+      const msg = match[1]!
+      if (seen.has(msg)) seen.delete(msg)
+      else seen.set(commit.message, commit)
+      continue
+    }
+
+    const revert = `Revert "${commit.message}"`
+    if (seen.has(revert)) {
+      seen.delete(revert)
+      continue
+    }
+
+    seen.set(commit.message, commit)
+  }
+
+  return [...seen.values()]
+}
+
+async function commits(from: string, to: string) {
+  const base = ref(from)
+  const head = ref(to)
 
-  const commits: Commit[] = []
-  for (const hash of hashes) {
-    const data = commitData.get(hash)
-    if (!data) continue
+  const data = new Map<string, { login: string | null; message: string }>()
+  for (const item of await diff(base, head)) {
+    data.set(item.sha, { login: item.login, message: item.message.split("\n")[0] ?? "" })
+  }
+
+  const log =
+    await $`git log ${base}..${head} --format=%H -- packages/opencode packages/sdk packages/plugin packages/desktop packages/app sdks/vscode packages/extensions github`.text()
 
-    const message = data.message
-    if (message.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue
+  const list: Commit[] = []
+  for (const hash of log.split("\n").filter(Boolean)) {
+    const item = data.get(hash)
+    if (!item) continue
+    if (item.message.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue
 
-    const files = await $`git diff-tree --no-commit-id --name-only -r ${hash}`.text()
+    const diff = await $`git diff-tree --no-commit-id --name-only -r ${hash}`.text()
     const areas = new Set<string>()
 
-    for (const file of files.split("\n").filter(Boolean)) {
+    for (const file of diff.split("\n").filter(Boolean)) {
       if (file.startsWith("packages/opencode/src/cli/cmd/")) areas.add("tui")
       else if (file.startsWith("packages/opencode/")) areas.add("core")
       else if (file.startsWith("packages/desktop/src-tauri/")) areas.add("tauri")
-      else if (file.startsWith("packages/desktop/")) areas.add("app")
-      else if (file.startsWith("packages/app/")) areas.add("app")
-      else if (file.startsWith("packages/sdk/")) areas.add("sdk")
-      else if (file.startsWith("packages/plugin/")) areas.add("plugin")
+      else if (file.startsWith("packages/desktop/") || file.startsWith("packages/app/")) areas.add("app")
+      else if (file.startsWith("packages/sdk/") || file.startsWith("packages/plugin/")) areas.add("sdk")
       else if (file.startsWith("packages/extensions/")) areas.add("extensions/zed")
-      else if (file.startsWith("sdks/vscode/")) areas.add("extensions/vscode")
-      else if (file.startsWith("github/")) areas.add("github")
+      else if (file.startsWith("sdks/vscode/") || file.startsWith("github/")) areas.add("extensions/vscode")
     }
 
     if (areas.size === 0) continue
 
-    commits.push({
+    list.push({
       hash: hash.slice(0, 7),
-      author: data.login,
-      message,
+      author: item.login,
+      message: item.message,
       areas,
     })
   }
 
-  return filterRevertedCommits(commits)
+  return reverted(list)
 }
 
-function filterRevertedCommits(commits: Commit[]): Commit[] {
-  const revertPattern = /^Revert "(.+)"$/
-  const seen = new Map<string, Commit>()
+async function contributors(from: string, to: string) {
+  const base = ref(from)
+  const head = ref(to)
 
-  for (const commit of commits) {
-    const match = commit.message.match(revertPattern)
-    if (match) {
-      // It's a revert - remove the original if we've seen it
-      const original = match[1]!
-      if (seen.has(original)) seen.delete(original)
-      else seen.set(commit.message, commit) // Keep revert if original not in range
-    } else {
-      // Regular commit - remove if its revert exists, otherwise add
-      const revertMsg = `Revert "${commit.message}"`
-      if (seen.has(revertMsg)) seen.delete(revertMsg)
-      else seen.set(commit.message, commit)
-    }
+  const users: User = new Map()
+  for (const item of await diff(base, head)) {
+    const title = item.message.split("\n")[0] ?? ""
+    if (!item.login || team.includes(item.login)) continue
+    if (title.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue
+    if (!users.has(item.login)) users.set(item.login, new Set())
+    users.get(item.login)!.add(title)
   }
 
-  return [...seen.values()]
+  return users
 }
 
-const sections = {
-  core: "Core",
-  tui: "TUI",
-  app: "Desktop",
-  tauri: "Desktop",
-  sdk: "SDK",
-  plugin: "SDK",
-  "extensions/zed": "Extensions",
-  "extensions/vscode": "Extensions",
-  github: "Extensions",
-} as const
+async function published(to: string) {
+  if (to === "HEAD") return
+  const body = await $`gh release view ${ref(to)} --repo ${repo} --json body --jq .body`.text().catch(() => "")
+  if (!body) return
 
-function getSection(areas: Set<string>): string {
-  // Priority order for multi-area commits
-  const priority = ["core", "tui", "app", "tauri", "sdk", "plugin", "extensions/zed", "extensions/vscode", "github"]
-  for (const area of priority) {
-    if (areas.has(area)) return sections[area as keyof typeof sections]
-  }
-  return "Core"
-}
-
-async function summarizeCommit(opencode: Awaited<ReturnType<typeof createOpencode>>, message: string): Promise<string> {
-  console.log("summarizing commit:", message)
-  const session = await opencode.client.session.create()
-  const result = await opencode.client.session
-    .prompt(
-      {
-        sessionID: session.data!.id,
-        model: { providerID: "opencode", modelID: "claude-sonnet-4-5" },
-        tools: {
-          "*": false,
-        },
-        parts: [
-          {
-            type: "text",
-            text: `Summarize this commit message for a changelog entry. Return ONLY a single line summary starting with a capital letter. Be concise but specific. If the commit message is already well-written, just clean it up (capitalize, fix typos, proper grammar). Do not include any prefixes like "fix:" or "feat:".
-
-Commit: ${message}`,
-          },
-        ],
-      },
-      {
-        signal: AbortSignal.timeout(120_000),
-      },
-    )
-    .then((x) => x.data?.parts?.find((y) => y.type === "text")?.text ?? message)
-  return result.trim()
+  const lines = body.split(/\r?\n/)
+  const start = lines.findIndex((line) => line.startsWith("**Thank you to "))
+  if (start < 0) return
+  return lines.slice(start).join("\n").trim()
 }
 
-export async function generateChangelog(commits: Commit[], opencode: Awaited<ReturnType<typeof createOpencode>>) {
-  // Summarize commits in parallel with max 10 concurrent requests
-  const BATCH_SIZE = 10
-  const summaries: string[] = []
-  for (let i = 0; i < commits.length; i += BATCH_SIZE) {
-    const batch = commits.slice(i, i + BATCH_SIZE)
-    const results = await Promise.all(batch.map((c) => summarizeCommit(opencode, c.message)))
-    summaries.push(...results)
-  }
+async function thanks(from: string, to: string, reuse: boolean) {
+  const release = reuse ? await published(to) : undefined
+  if (release) return release.split(/\r?\n/)
 
-  const grouped = new Map<string, string[]>()
-  for (let i = 0; i < commits.length; i++) {
-    const commit = commits[i]!
-    const section = getSection(commit.areas)
-    const attribution = commit.author && !Script.team.includes(commit.author) ? ` (@${commit.author})` : ""
-    const entry = `- ${summaries[i]}${attribution}`
-
-    if (!grouped.has(section)) grouped.set(section, [])
-    grouped.get(section)!.push(entry)
-  }
+  const users = await contributors(from, to)
+  if (users.size === 0) return []
 
-  const sectionOrder = ["Core", "TUI", "Desktop", "SDK", "Extensions"]
-  const lines: string[] = []
-  for (const section of sectionOrder) {
-    const entries = grouped.get(section)
-    if (!entries || entries.length === 0) continue
-    lines.push(`## ${section}`)
-    lines.push(...entries)
+  const lines = [`**Thank you to ${users.size} community contributor${users.size > 1 ? "s" : ""}:**`]
+  for (const [name, commits] of users) {
+    lines.push(`- @${name}:`)
+    for (const commit of commits) lines.push(`  - ${commit}`)
   }
-
   return lines
 }
 
-export async function getContributors(from: string, to: string) {
-  const fromRef = from.startsWith("v") ? from : `v${from}`
-  const toRef = to === "HEAD" ? to : to.startsWith("v") ? to : `v${to}`
-  const compare =
-    await $`gh api "/repos/anomalyco/opencode/compare/${fromRef}...${toRef}" --jq '.commits[] | {login: .author.login, message: .commit.message}'`.text()
-  const contributors = new Map<string, Set<string>>()
-
-  for (const line of compare.split("\n").filter(Boolean)) {
-    const { login, message } = JSON.parse(line) as { login: string | null; message: string }
-    const title = message.split("\n")[0] ?? ""
-    if (title.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue
+function format(from: string, to: string, list: Commit[], thanks: string[]) {
+  const grouped = new Map<string, string[]>()
+  for (const title of order) grouped.set(title, [])
 
-    if (login && !Script.team.includes(login)) {
-      if (!contributors.has(login)) contributors.set(login, new Set())
-      contributors.get(login)!.add(title)
-    }
+  for (const commit of list) {
+    const title = section(commit.areas)
+    const attr = commit.author && !team.includes(commit.author) ? ` (@${commit.author})` : ""
+    grouped.get(title)!.push(`- \`${commit.hash}\` ${commit.message}${attr}`)
   }
 
-  return contributors
-}
-
-export async function buildNotes(from: string, to: string) {
-  const commits = await getCommits(from, to)
+  const lines = [`Last release: ${ref(from)}`, `Target ref: ${to}`, ""]
 
-  if (commits.length === 0) {
-    return []
+  if (list.length === 0) {
+    lines.push("No notable changes.")
   }
 
-  console.log("generating changelog since " + from)
-
-  const opencode = await createOpencode({ port: 0 })
-  const notes: string[] = []
-
-  try {
-    const lines = await generateChangelog(commits, opencode)
-    notes.push(...lines)
-    console.log("---- Generated Changelog ----")
-    console.log(notes.join("\n"))
-    console.log("-----------------------------")
-  } catch (error) {
-    if (error instanceof Error && error.name === "TimeoutError") {
-      console.log("Changelog generation timed out, using raw commits")
-      for (const commit of commits) {
-        const attribution = commit.author && !team.includes(commit.author) ? ` (@${commit.author})` : ""
-        notes.push(`- ${commit.message}${attribution}`)
-      }
-    } else {
-      throw error
-    }
-  } finally {
-    await opencode.server.close()
+  for (const title of order) {
+    const entries = grouped.get(title)
+    if (!entries || entries.length === 0) continue
+    lines.push(`## ${title}`)
+    lines.push(...entries)
+    lines.push("")
   }
-  console.log("changelog generation complete")
-
-  const contributors = await getContributors(from, to)
-
-  if (contributors.size > 0) {
-    notes.push("")
-    notes.push(`**Thank you to ${contributors.size} community contributor${contributors.size > 1 ? "s" : ""}:**`)
-    for (const [username, userCommits] of contributors) {
-      notes.push(`- @${username}:`)
-      for (const c of userCommits) {
-        notes.push(`  - ${c}`)
-      }
-    }
+
+  if (thanks.length > 0) {
+    if (lines.at(-1) !== "") lines.push("")
+    lines.push("## Community Contributors Input")
+    lines.push("")
+    lines.push(...thanks)
   }
 
-  return notes
+  if (lines.at(-1) === "") lines.pop()
+  return lines.join("\n")
 }
 
-// CLI entrypoint
 if (import.meta.main) {
   const { values } = parseArgs({
     args: Bun.argv.slice(2),
@@ -283,24 +242,20 @@ if (import.meta.main) {
 Usage: bun script/changelog.ts [options]
 
 Options:
-  -f, --from <version>   Starting version (default: latest GitHub release)
+  -f, --from <version>   Starting version (default: latest non-draft GitHub release)
   -t, --to <ref>         Ending ref (default: HEAD)
   -h, --help             Show this help message
 
 Examples:
-  bun script/changelog.ts                     # Latest release to HEAD
-  bun script/changelog.ts --from 1.0.200      # v1.0.200 to HEAD
+  bun script/changelog.ts
+  bun script/changelog.ts --from 1.0.200
   bun script/changelog.ts -f 1.0.200 -t 1.0.205
 `)
     process.exit(0)
   }
 
   const to = values.to!
-  const from = values.from ?? (await getLatestRelease())
-
-  console.log(`Generating changelog: v${from} -> ${to}\n`)
-
-  const notes = await buildNotes(from, to)
-  console.log("\n=== Final Notes ===")
-  console.log(notes.join("\n"))
+  const from = values.from ?? (await latest())
+  const list = await commits(from, to)
+  console.log(format(from, to, list, await thanks(from, to, !values.from)))
 }
diff --git a/script/version.ts b/script/version.ts
index 7bed6d3a9ae6..2fa59fe9f879 100755
--- a/script/version.ts
+++ b/script/version.ts
@@ -6,7 +6,8 @@ import { $ } from "bun"
 const output = [`version=${Script.version}`]
 
 if (!Script.preview) {
-  await $`opencode run --command changelog`.cwd(process.cwd())
+  const sha = process.env.GITHUB_SHA ?? (await $`git rev-parse HEAD`.text()).trim()
+  await $`opencode run --command changelog -- --to ${sha}`.cwd(process.cwd())
   const file = `${process.cwd()}/UPCOMING_CHANGELOG.md`
   const body = await Bun.file(file)
     .text()
PATCH

echo "Fix applied successfully."
