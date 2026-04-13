#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'supersede-pr' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create patch file
PATCH_FILE=$(mktemp)

# Write patch using base64 to avoid escape issues
cat > "$PATCH_FILE" << 'PATCH_EOF'
diff --git a/AGENTS.md b/AGENTS.md
index 9aee9cd378f..dcd690867d0 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -23,6 +23,7 @@
 ## Code Style

 - **Imports**: Always use `import type { X }` for types (separate from value imports); use `export type { X }` for type exports; include `.ts` extensions
+- **One-off scripts**: Write one-off scripts in this repo as TypeScript and make them executable natively with modern Node.js (for example, executable `.ts` files)
 - **Variables**: Prefer `let` for locals, `const` only at module scope; never use `var`
 - **Functions**: Use regular function declarations/expressions by default. For callback-based APIs (array methods, Promise callbacks, test callbacks, transaction callbacks, etc.), prefer arrow functions over `function` expressions. When an arrow callback only returns a single expression, use a concise body (`value => expression`) instead of braces/`return`
 - **Object methods**: When defining functions in object literals, use shorthand method syntax (`{ method() {} }`) instead of arrow functions (`{ method: () => {} }`)
@@ -61,3 +62,12 @@
 - **Manual releases**: `pnpm changes:version` updates package.json, CHANGELOG.md, and creates a git commit. Push to `main` and the publish workflow will handle the rest (including tags and GitHub releases).
 - **How publishing works**: The publish workflow checks for change files. If none exist, it runs `pnpm publish --recursive --report-summary`, reads the summary JSON to see what was published, then creates git tags and GitHub releases for each published package.
 - **Test change/release code with preview scripts**: When modifying any change/release code, run `pnpm changes:preview` to test locally. For the release PR script, run `node ./scripts/release-pr.ts --preview`. For the publish script, run `node ./scripts/publish.ts --dry-run` to see what commands would be executed without actually publishing.
+
+## Skills
+
+A skill is a reusable local instruction set stored in a `SKILL.md` file.
+
+### Available skills
+
+- **supersede-pr**: Replace one GitHub PR with another and explicitly close the superseded PR (instead of relying on `Closes #...` keywords). (file: `./skills/supersede-pr/SKILL.md`)
+- **make-pr**: Create GitHub pull requests with clear context, issue/feature bullets, and required usage examples for new or changed APIs. (file: `./skills/make-pr/SKILL.md`)
diff --git a/skills/make-pr/SKILL.md b/skills/make-pr/SKILL.md
new file mode 100644
index 00000000000..2a37854b60f
--- /dev/null
+++ b/skills/make-pr/SKILL.md
@@ -0,0 +1,65 @@
+---
+name: make-pr
+description: Create GitHub pull requests with clear, reviewer-friendly descriptions. Use when asked to open or prepare a PR, especially when the PR needs strong context, related links, and feature usage examples. This skill enforces concise PR structure, avoids redundant sections like validation/testing, and creates the PR with gh CLI.
+---
+
+# Make PR
+
+## Overview
+
+Use this skill to draft and open a PR with consistent, high-signal writing.
+Keep headings sparse and focus on the problem/feature explanation, context links, and practical code examples.
+
+## Workflow
+
+1. Gather context from branch diff and related work.
+- Capture what changed, why it changed, and who it affects.
+- Find related issues/PRs and include links when relevant.
+
+1. Draft the PR body with minimal structure.
+- Start with 1-2 short introductory paragraphs.
+- In those intro paragraphs, include clear bullets describing:
+  - the feature and/or issue addressed
+  - key behavior/API changes
+  - expected impact
+- If the change is extensive, expand to up to 3-4 paragraphs and include background context with related links.
+
+1. Add required usage examples for feature work.
+- If the PR introduces a new feature, include a comprehensive usage snippet.
+- If it replaces or improves an older approach, include before/after examples.
+
+1. Exclude redundant sections.
+- Do not include `Validation`, `Testing`, or other process sections that are already implicit in PR workflow.
+- Do not add boilerplate sections that do not help review.
+
+1. Create the PR.
+- Save the body to a temporary file and run:
+```bash
+gh pr create --base main --head <branch> --title "<title>" --body-file <file>
+```
+
+## Body Template
+
+Use this as a base and fill with concrete repo-specific details:
+
+```md
+<One or two short intro paragraphs explaining the change and why it matters.>
+
+- <Feature/issue addressed>
+- <What changed in behavior or API>
+- <Why this is needed now>
+
+<Optional additional context paragraph(s), up to 3-4 total for large changes, including links to related PRs/issues.>
+
+```ts
+// New feature usage example
+```
+
+```ts
+// Before
+```
+
+```ts
+// After
+```
+```
diff --git a/skills/make-pr/agents/openai.yaml b/skills/make-pr/agents/openai.yaml
new file mode 100644
index 00000000000..ba215b1df55
--- /dev/null
+++ b/skills/make-pr/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Make PR"
+  short_short_description: "Create high-quality GitHub pull requests"
+  default_prompt: "Use $make-pr to draft and create a GitHub pull request with clear context and examples."
diff --git a/skills/supersede-pr/SKILL.md b/skills/supersede-pr/SKILL.md
new file mode 100644
index 00000000000..d82b94e9581
--- /dev/null
+++ b/skills/supersede-pr/SKILL.md
@@ -0,0 +1,54 @@
+---
+name: supersede-pr
+description: Safely replace one GitHub pull request with another. Use when a user says a PR supersedes/replaces an older PR, asks to auto-close a superseded PR, or needs guaranteed closure behavior after merge. This skill explicitly closes the superseded PR with gh CLI and verifies final PR states instead of relying on closing keywords.
+---
+
+# Supersede PR
+
+## Overview
+
+Use this skill to handle PR supersession end-to-end.
+Do not rely on `Closes #<number>` to close another PR. GitHub closing keywords close issues, not pull requests.
+
+## Workflow
+
+1. Identify PR numbers and target repo.
+- Capture `old_pr` (the superseded PR) and `new_pr` (the replacement PR).
+- Resolve the repo with `gh repo view --json nameWithOwner -q .nameWithOwner` when not provided.
+
+1. Create or update the replacement PR first.
+- Open/push the replacement branch.
+- Open the new PR.
+- Include a traceable link in the PR body such as `Supersedes #<old_pr>`.
+
+1. Close the superseded PR explicitly.
+- Run:
+```bash
+./skills/supersede-pr/scripts/close_superseded_pr.ts <old_pr> <new_pr>
+```
+- This adds a comment (`Superseded by #<new_pr>.`) and closes the old PR.
+
+1. Verify states.
+- Confirm the superseded PR is closed:
+```bash
+gh pr view <old_pr> --json state,url
+```
+- Confirm the replacement PR status/checks:
+```bash
+gh pr checks <new_pr>
+```
+
+## Rules
+
+1. Do not use `Closes #<old_pr>` when `<old_pr>` is a pull request.
+- Use `Closes/Fixes` only for issues.
+- Use `Supersedes #<old_pr>` or `Refs #<old_pr>` for PR-to-PR linkage.
+
+1. Prefer explicit closure over implied automation.
+- Always run the close command when the user asks to supersede a PR.
+- Treat closure as incomplete until `gh pr view <old_pr>` returns `CLOSED`.
+
+## Script
+
+Use the bundled script for deterministic closure:
+- `scripts/close_superseded_pr.ts`
diff --git a/skills/supersede-pr/agents/openai.yaml b/skills/supersede-pr/agents/openai.yaml
new file mode 100644
index 00000000000..31253fe0777
--- /dev/null
+++ b/skills/supersede-pr/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Supersede PR"
+  short_description: "Close superseded pull requests safely"
+  default_prompt: "Use $supersede-pr to replace a PR and close the superseded PR safely."
diff --git a/skills/supersede-pr/scripts/close_superseded_pr.ts b/skills/supersede-pr/scripts/close_superseded_pr.ts
new file mode 100755
index 00000000000..1893d045628
--- /dev/null
+++ b/skills/supersede-pr/scripts/close_superseded_pr.ts
@@ -0,0 +1,136 @@
+#!/usr/bin/env node
+import { spawnSync } from 'node:child_process'
+import * as process from 'node:process'
+
+type ParsedArgs = {
+  dryRun: boolean
+  newPr: string
+  oldPr: string
+  repo: string | null
+}
+
+function main(): void {
+  let parsed = parseArgs(process.argv.slice(2))
+  ensureNumericPrNumber(parsed.oldPr, 'old_pr')
+  ensureNumericPrNumber(parsed.newPr, 'new_pr')
+
+  if (parsed.oldPr === parsed.newPr) {
+    fail('old_pr and new_pr must be different.')
+  }
+
+  let repo = parsed.repo ?? ghCapture(['repo', 'view', '--json', 'nameWithOwner', '-q', '.nameWithOwner'])
+  let oldState = ghCapture(['pr', 'view', parsed.oldPr, '--repo', repo, '--json', 'state', '-q', '.state'])
+  let newState = ghCapture(['pr', 'view', parsed.newPr, '--repo', repo, '--json', 'state', '-q', '.state'])
+
+  if (newState !== 'OPEN' && newState !== 'MERGED') {
+    fail(
+      `Replacement PR #${parsed.newPr} is in state '${newState}'. Expected OPEN or MERGED.`,
+    )
+  }
+
+  if (oldState !== 'OPEN') {
+    process.stdout.write(`Superseded PR #${parsed.oldPr} is already ${oldState}. Nothing to do.\n`)
+    return
+  }
+
+  let comment = `Superseded by #${parsed.newPr}.`
+
+  process.stdout.write(`Repo: ${repo}\n`)
+  process.stdout.write(`Closing PR #${parsed.oldPr} with comment: ${comment}\n`)
+
+  if (parsed.dryRun) {
+    process.stdout.write(
+      `[dry-run] gh pr close "${parsed.oldPr}" --repo "${repo}" --comment "${comment}"\n`,
+    )
+    return
+  }
+
+  ghInherit(['pr', 'close', parsed.oldPr, '--repo', repo, '--comment', comment])
+
+  let finalState = ghCapture(['pr', 'view', parsed.oldPr, '--repo', repo, '--json', 'state', '-q', '.state'])
+  if (finalState !== 'CLOSED') {
+    fail(`Failed to close PR #${parsed.oldPr}. Final state: ${finalState}`)
+  }
+
+  process.stdout.write(`Closed PR #${parsed.oldPr} successfully.\n`)
+}
+
+function parseArgs(argv: string[]): ParsedArgs {
+  if (argv.includes('-h') || argv.includes('--help')) {
+    printUsage()
+    process.exit(0)
+  }
+
+  if (argv.length < 2) {
+    printUsage()
+    process.exit(1)
+  }
+
+  let oldPr = argv[0]
+  let newPr = argv[1]
+  let repo: string | null = null
+  let dryRun = false
+  let index = 2
+
+  while (index < argv.length) {
+    let arg = argv[index]
+    if (arg === '--repo') {
+      let next = argv[index + 1]
+      if (!next) {
+        fail('--repo requires a value like owner/repo')
+      }
+      repo = next
+      index += 2
+      continue
+    }
+    if (arg === '--dry-run') {
+      dryRun = true
+      index++
+      continue
+    }
+    fail(`Unknown argument: ${arg}`)
+  }
+
+  return { dryRun, newPr, oldPr, repo }
+}
+
+function printUsage(): void {
+  process.stdout.write(`Usage:
+  close_superseded_pr.ts <old_pr> <new_pr> [--repo <owner/repo>] [--dry-run]
+
+Examples:
+  close_superseded_pr.ts 11085 11087
+  close_superseded_pr.ts 11085 11087 --repo remix-run/remix
+  close_superseded_pr.ts 11085 11087 --dry-run
+`)
+}
+
+function ensureNumericPrNumber(value: string, label: string): void {
+  if (!/^[0-9]+$/.test(value)) {
+    fail(`${label} must be a numeric pull request number.`)
+  }
+}
+
+function ghCapture(args: string[]): string {
+  let result = spawnSync('gh', args, { encoding: 'utf8' })
+  if (result.status !== 0) {
+    let stderr = (result.stderr ?? '').trim()
+    let details = stderr ? `\n${stderr}` : ''
+    fail(`gh ${args.join(' ')} failed.${details}`)
+  }
+  return (result.stdout ?? '').trim()
+}
+
+function ghInherit(args: string[]): void {
+  let result = spawnSync('gh', args, { stdio: 'inherit' })
+  if (result.status !== 0) {
+    fail(`gh ${args.join(' ')} failed with exit code ${result.status ?? 'unknown'}.`)
+  }
+}
+
+function fail(message: string): never {
+  process.stderr.write(`${message}\n`)
+  process.exit(1)
+}
+
+main()
diff --git a/skills/supersede-pr/tsconfig.json b/skills/supersede-pr/tsconfig.json
new file mode 100644
index 00000000000..e4c2a858aba
--- /dev/null
+++ b/skills/supersede-pr/tsconfig.json
@@ -0,0 +1,12 @@
+{
+  "compilerOptions": {
+    "allowJs": false,
+    "module": "NodeNext",
+    "moduleResolution": "NodeNext",
+    "noEmit": true,
+    "strict": true,
+    "target": "ESNext",
+    "verbatimModuleSyntax": true
+  },
+  "include": ["scripts/**/*.ts"]
+}
+
PATCH_EOF

git apply "$PATCH_FILE"
rm "$PATCH_FILE"

# Fix formatting for newly created files
pnpm format skills/make-pr skills/supersede-pr 2>/dev/null || true

echo "Patch applied successfully."
