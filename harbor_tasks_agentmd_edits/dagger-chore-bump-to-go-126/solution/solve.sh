#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dagger

# Idempotent: skip if already applied
if grep -q 'GolangVersion = "1.26"' engine/distconsts/consts.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/engine/distconsts/consts.go b/engine/distconsts/consts.go
index 787defe2dec..1ae3aa7986a 100644
--- a/engine/distconsts/consts.go
+++ b/engine/distconsts/consts.go
@@ -27,7 +27,7 @@ const (
 	AlpineVersion = "3.22.1"
 	AlpineImage   = "alpine:" + AlpineVersion

-	GolangVersion = "1.25.7"
+	GolangVersion = "1.26"
 	GolangImage   = "golang:" + GolangVersion + "-alpine"

 	BusyboxVersion = "1.37.0"
diff --git a/toolchains/cli-dev/publish.go b/toolchains/cli-dev/publish.go
index 719d9efe99a..1c403b40a17 100644
--- a/toolchains/cli-dev/publish.go
+++ b/toolchains/cli-dev/publish.go
@@ -229,7 +229,7 @@ func (cli *CliDev) goreleaserBinaries() *dagger.Directory {
 	dir := dag.Directory()
 	for _, os := range oses {
 		for _, arch := range arches {
-			if arch == "arm" && os == "darwin" {
+			if arch == "arm" && (os == "darwin" || os == "windows") {
 				continue
 			}

diff --git a/toolchains/go/main.go b/toolchains/go/main.go
index db2937a6ab9..8c97777c386 100644
--- a/toolchains/go/main.go
+++ b/toolchains/go/main.go
@@ -27,7 +27,7 @@ func New(
 	source *dagger.Directory,
 	// Go version
 	// +optional
-	// +default="1.25.7"
+	// +default="1.26"
 	version string,
 	// Use a custom module cache
 	// +optional
@@ -83,7 +83,7 @@ func New(
 	}
 	if base == nil {
 		packages := []string{
-			"go~" + version,
+			"go-" + version,
 			"ca-certificates",
 			// gcc is needed to run go test -race https://github.com/golang/go/issues/9918 (???)
 			"build-base",

PATCH

# Create the new skills/dagger-chores/SKILL.md
mkdir -p skills/dagger-chores
cat > skills/dagger-chores/SKILL.md <<'SKILL'
---
name: dagger-chores
description: Handle quick, repeatable Dagger repository maintenance chores. Use when the user asks for small operational changes and wants the same established edits and commit style applied quickly.
---

# Dagger Chores

## Go Version Bump

Use this checklist when asked to bump Go.

1. Update the Go version string in `engine/distconsts/consts.go`:
- `GolangVersion = "X.Y.Z"`

2. Update the Go default version string in `toolchains/go/main.go`:
- `// +default="X.Y.Z"` on the `version` argument in `New(...)`

3. Use a short commit message in this format:
- `chore: bump to go <major.minor>`
- Example: `chore: bump to go 1.26`

4. Create a signed commit:
- `git commit -s -m "chore: bump to go <major.minor>"`

5. Tell the user to double-check whether new Go version locations have been introduced since the last bump, and mention they can ask the agent for help finding them.
- Suggested wording: `Please double-check if any additional Go version strings were added in new files; these locations can change over time. If helpful, I can also help search for those locations.`

## Regenerate Generated Files

Use this checklist when asked to regenerate generated files.

1. From the Dagger repo root, create a temp file for command output and store its path in `tmp_log`.

2. Run generation and redirect all output to the temp file:
- `dagger --progress=plain call generate layer export --path . >"$tmp_log" 2>&1`

3. Search the temp file as needed instead of printing full output.

4. Delete the temp file when done.
SKILL

echo "Patch applied successfully."
