#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if [ -f script/raw-changelog.ts ]; then
    echo "Patch already applied."
    exit 0
fi

# 1. Create the new raw-changelog.ts file (extracted from old changelog.ts)
cat > script/raw-changelog.ts <<'RAWEOF'
#!/usr/bin/env bun

import { $ } from "bun"
import { parseArgs } from "util"

type Release = {
  tag_name: string
  draft: boolean
}

type Commit = {
  hash: string
  author: string | null
  message: string
  areas: Set<string>
}

type User = Map<string, Set<string>>
type Diff = {
  sha: string
  login: string | null
  message: string
}

const repo = process.env.GH_REPO ?? "anomalyco/opencode"
const bot = ["actions-user", "opencode", "opencode-agent[bot]"]
const team = [
  ...(await Bun.file(new URL("../.github/TEAM_MEMBERS", import.meta.url))
    .text()
    .then((x) => x.split(/\r?\n/).map((x) => x.trim()))
    .then((x) => x.filter((x) => x && !x.startsWith("#")))),
  ...bot,
]
const order = ["Core", "TUI", "Desktop", "SDK", "Extensions"] as const
const sections = {
  core: "Core",
  tui: "TUI",
  app: "Desktop",
  tauri: "Desktop",
  sdk: "SDK",
  plugin: "SDK",
  "extensions/zed": "Extensions",
  "extensions/vscode": "Extensions",
  github: "Extensions",
} as const

function ref(input: string) {
  if (input === "HEAD") return input
  if (input.startsWith("v")) return input
  if (input.match(/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/)) return `v${input}`
  return input
}

async function latest() {
  const data = await $`gh api "/repos/${repo}/releases?per_page=100"`.json()
  const release = (data as Release[]).find((item) => !item.draft)
  if (!release) throw new Error("No releases found")
  return release.tag_name.replace(/^v/, "")
}

async function diff(base: string, head: string) {
  const list: Diff[] = []
  for (let page = 1; ; page++) {
    const text =
      await $`gh api "/repos/${repo}/compare/${base}...${head}?per_page=100&page=${page}" --jq '.commits[] | {sha: .sha, login: .author.login, message: .commit.message}'`.text()
    const batch = text
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line) as Diff)
    if (batch.length === 0) break
    list.push(...batch)
    if (batch.length < 100) break
  }
  return list
}

function section(areas: Set<string>) {
  const priority = ["core", "tui", "app", "tauri", "sdk", "plugin", "extensions/zed", "extensions/vscode", "github"]
  for (const area of priority) {
    if (areas.has(area)) return sections[area as keyof typeof sections]
  }
  return "Core"
}

function reverted(commits: Commit[]) {
  const seen = new Map<string, Commit>()

  for (const commit of commits) {
    const match = commit.message.match(/^Revert "(.+)"$/)
    if (match) {
      const msg = match[1]!
      if (seen.has(msg)) seen.delete(msg)
      else seen.set(commit.message, commit)
      continue
    }

    const revert = `Revert "${commit.message}"`
    if (seen.has(revert)) {
      seen.delete(revert)
      continue
    }

    seen.set(commit.message, commit)
  }

  return [...seen.values()]
}

async function commits(from: string, to: string) {
  const base = ref(from)
  const head = ref(to)

  const data = new Map<string, { login: string | null; message: string }>()
  for (const item of await diff(base, head)) {
    data.set(item.sha, { login: item.login, message: item.message.split("\n")[0] ?? "" })
  }

  const log =
    await $`git log ${base}..${head} --format=%H -- packages/opencode packages/sdk packages/plugin packages/desktop packages/app sdks/vscode packages/extensions github`.text()

  const list: Commit[] = []
  for (const hash of log.split("\n").filter(Boolean)) {
    const item = data.get(hash)
    if (!item) continue
    if (item.message.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue

    const diff = await $`git diff-tree --no-commit-id --name-only -r ${hash}`.text()
    const areas = new Set<string>()

    for (const file of diff.split("\n").filter(Boolean)) {
      if (file.startsWith("packages/opencode/src/cli/cmd/")) areas.add("tui")
      else if (file.startsWith("packages/opencode/")) areas.add("core")
      else if (file.startsWith("packages/desktop/src-tauri/")) areas.add("tauri")
      else if (file.startsWith("packages/desktop/") || file.startsWith("packages/app/")) areas.add("app")
      else if (file.startsWith("packages/sdk/") || file.startsWith("packages/plugin/")) areas.add("sdk")
      else if (file.startsWith("packages/extensions/")) areas.add("extensions/zed")
      else if (file.startsWith("sdks/vscode/") || file.startsWith("github/")) areas.add("extensions/vscode")
    }

    if (areas.size === 0) continue

    list.push({
      hash: hash.slice(0, 7),
      author: item.login,
      message: item.message,
      areas,
    })
  }

  return reverted(list)
}

async function contributors(from: string, to: string) {
  const base = ref(from)
  const head = ref(to)

  const users: User = new Map()
  for (const item of await diff(base, head)) {
    const title = item.message.split("\n")[0] ?? ""
    if (!item.login || team.includes(item.login)) continue
    if (title.match(/^(ignore:|test:|chore:|ci:|release:)/i)) continue
    if (!users.has(item.login)) users.set(item.login, new Set())
    users.get(item.login)!.add(title)
  }

  return users
}

async function published(to: string) {
  if (to === "HEAD") return
  const body = await $`gh release view ${ref(to)} --repo ${repo} --json body --jq .body`.text().catch(() => "")
  if (!body) return

  const lines = body.split(/\r?\n/)
  const start = lines.findIndex((line) => line.startsWith("**Thank you to "))
  if (start < 0) return
  return lines.slice(start).join("\n").trim()
}

async function thanks(from: string, to: string, reuse: boolean) {
  const release = reuse ? await published(to) : undefined
  if (release) return release.split(/\r?\n/)

  const users = await contributors(from, to)
  if (users.size === 0) return []

  const lines = [`**Thank you to ${users.size} community contributor${users.size > 1 ? "s" : ""}:**`]
  for (const [name, commits] of users) {
    lines.push(`- @${name}:`)
    for (const commit of commits) lines.push(`  - ${commit}`)
  }
  return lines
}

function format(from: string, to: string, list: Commit[], thanks: string[]) {
  const grouped = new Map<string, string[]>()
  for (const title of order) grouped.set(title, [])

  for (const commit of list) {
    const title = section(commit.areas)
    const attr = commit.author && !team.includes(commit.author) ? ` (@${commit.author})` : ""
    grouped.get(title)!.push(`- \`${commit.hash}\` ${commit.message}${attr}`)
  }

  const lines = [`Last release: ${ref(from)}`, `Target ref: ${to}`, ""]

  if (list.length === 0) {
    lines.push("No notable changes.")
  }

  for (const title of order) {
    const entries = grouped.get(title)
    if (!entries || entries.length === 0) continue
    lines.push(`## ${title}`)
    lines.push(...entries)
    lines.push("")
  }

  if (thanks.length > 0) {
    if (lines.at(-1) !== "") lines.push("")
    lines.push("## Community Contributors Input")
    lines.push("")
    lines.push(...thanks)
  }

  if (lines.at(-1) === "") lines.pop()
  return lines.join("\n")
}

if (import.meta.main) {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      from: { type: "string", short: "f" },
      to: { type: "string", short: "t", default: "HEAD" },
      help: { type: "boolean", short: "h", default: false },
    },
  })

  if (values.help) {
    console.log(`
Usage: bun script/raw-changelog.ts [options]

Options:
  -f, --from <version>   Starting version (default: latest non-draft GitHub release)
  -t, --to <ref>         Ending ref (default: HEAD)
  -h, --help             Show this help message

Examples:
  bun script/raw-changelog.ts
  bun script/raw-changelog.ts --from 1.0.200
  bun script/raw-changelog.ts -f 1.0.200 -t 1.0.205
`)
    process.exit(0)
  }

  const to = values.to!
  const from = values.from ?? (await latest())
  const list = await commits(from, to)
  console.log(format(from, to, list, await thanks(from, to, !values.from)))
}
RAWEOF

# 2. Replace changelog.ts with the new thin wrapper
cat > script/changelog.ts <<'CHANGEOF'
#!/usr/bin/env bun

import { rm } from "fs/promises"
import path from "path"
import { parseArgs } from "util"

const root = path.resolve(import.meta.dir, "..")
const file = path.join(root, "UPCOMING_CHANGELOG.md")
const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    from: { type: "string", short: "f" },
    to: { type: "string", short: "t" },
    variant: { type: "string", default: "low" },
    quiet: { type: "boolean", default: false },
    print: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
})
const args = [...positionals]

if (values.from) args.push("--from", values.from)
if (values.to) args.push("--to", values.to)

if (values.help) {
  console.log(`
Usage: bun script/changelog.ts [options]

Generates UPCOMING_CHANGELOG.md by running the opencode changelog command.

Options:
  -f, --from <version>   Starting version (default: latest non-draft GitHub release)
  -t, --to <ref>         Ending ref (default: HEAD)
      --variant <name>   Thinking variant for opencode run (default: low)
      --quiet            Suppress opencode command output unless it fails
      --print            Print the generated UPCOMING_CHANGELOG.md after success
  -h, --help             Show this help message

Examples:
  bun script/changelog.ts
  bun script/changelog.ts --from 1.0.200
  bun script/changelog.ts -f 1.0.200 -t 1.0.205
`)
  process.exit(0)
}

await rm(file, { force: true })

const quiet = values.quiet
const cmd = ["opencode", "run"]
cmd.push("--variant", values.variant)
cmd.push("--command", "changelog", "--", ...args)

const proc = Bun.spawn(cmd, {
  cwd: root,
  stdin: "inherit",
  stdout: quiet ? "pipe" : "inherit",
  stderr: quiet ? "pipe" : "inherit",
})

const [out, err] = quiet
  ? await Promise.all([new Response(proc.stdout).text(), new Response(proc.stderr).text()])
  : ["", ""]
const code = await proc.exited
if (code === 0) {
  if (values.print) process.stdout.write(await Bun.file(file).text())
  process.exit(0)
}

if (quiet) {
  if (out) process.stdout.write(out)
  if (err) process.stderr.write(err)
}

process.exit(code)
CHANGEOF

# 3. Patch .opencode/command/changelog.md and script/version.ts
git apply - <<'PATCH'
diff --git a/.opencode/command/changelog.md b/.opencode/command/changelog.md
index f0ff1e422dee..4cd30a704a4a 100644
--- a/.opencode/command/changelog.md
+++ b/.opencode/command/changelog.md
@@ -1,22 +1,19 @@
 ---
-model: opencode/kimi-k2.5
+model: opencode/gpt-5.4
 ---

 Create `UPCOMING_CHANGELOG.md` from the structured changelog input below.
 If `UPCOMING_CHANGELOG.md` already exists, ignore its current contents completely.
 Do not preserve, merge, or reuse text from the existing file.

-Any command arguments are passed directly to `bun script/changelog.ts`.
-Use `--from` / `-f` and `--to` / `-t` to preview a specific release range.
-
 The input already contains the exact commit range since the last non-draft release.
 The commits are already filtered to the release-relevant packages and grouped into
 the release sections. Do not fetch GitHub releases, PRs, or build your own commit list.
 The input may also include a `## Community Contributors Input` section.

 Before writing any entry you keep, inspect the real diff with
-`git show --stat --format='' <hash>` or `git show --format='' <hash>` so the
-summary reflects the actual user-facing change and not just the commit message.
+`git show --stat --format='' <hash>` or `git show --format='' <hash>` so you can
+understand the actual code changes and not just the commit message (they may be misleading).
 Do not use `git log` or author metadata when deciding attribution.

 Rules:
@@ -38,7 +35,12 @@ Rules:
 - Do not add, remove, rewrite, or reorder contributor names or commit titles in that block
 - Do not derive the thank-you section from the main summary bullets
 - Do not include the heading `## Community Contributors Input` in the final file
+- Focus on writing the least words to get your point across - users will skim read the changelog, so we should be precise
+
+**Importantly, the changelog is for users (who are at least slightly technical), they may use the TUI, Desktop, SDK, Plugins and so forth. Be thorough in understanding flow on effects may not be immediately apparent. e.g. a package upgrade looks internal but may patch a bug. Or a refactor may also stabilise some race condition that fixes bugs for users. The PR title/body + commit message will give you the authors context, usually containing the outcome not just technical detail**
+
+<changelog_input>

-## Changelog Input
+!`bun script/raw-changelog.ts $ARGUMENTS`

-!`bun script/changelog.ts $ARGUMENTS`
+</changelog_input>
diff --git a/script/version.ts b/script/version.ts
index 2fa59fe9f879..3ca4f661d245 100755
--- a/script/version.ts
+++ b/script/version.ts
@@ -7,7 +7,7 @@ const output = [`version=${Script.version}`]

 if (!Script.preview) {
   const sha = process.env.GITHUB_SHA ?? (await $`git rev-parse HEAD`.text()).trim()
-  await $`opencode run --command changelog -- --to ${sha}`.cwd(process.cwd())
+  await $`bun script/changelog.ts --to ${sha}`.cwd(process.cwd())
   const file = `${process.cwd()}/UPCOMING_CHANGELOG.md`
   const body = await Bun.file(file)
     .text()

PATCH

echo "Patch applied successfully."
