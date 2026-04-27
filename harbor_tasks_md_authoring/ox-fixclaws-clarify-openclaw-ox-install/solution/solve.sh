#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ox

# Idempotency guard
if grep -qF "**wait for their response**. Do not pick a default. Do not guess. Do not" "claws/openclaw/sageox-distill/SKILL.md" && grep -qF "**wait for their response**. Do not pick a default. Do not guess. Do not" "claws/openclaw/sageox-summary/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/claws/openclaw/sageox-distill/SKILL.md b/claws/openclaw/sageox-distill/SKILL.md
@@ -180,16 +180,40 @@ cat ~/.openclaw/memory/sageox-ox-install.json 2>/dev/null
 `auto_update == true`, update ox before proceeding (see "Updating ox from
 git" below).
 
-**If the file does not exist:** prompt the user to choose an install method:
-
-> How do you want to install the `ox` CLI?
+**If the file does not exist:** STOP. This is a one-time decision that
+gets persisted to disk and affects every future run of this skill — the
+user must own it. You **MUST** ask the user which method they want and
+**wait for their response**. Do not pick a default. Do not guess. Do not
+run any install commands yet. Present both options verbatim, then stop
+and wait:
+
+> How do you want to install the `ox` CLI? Pick one — I won't choose for
+> you, because this gets saved to
+> `~/.openclaw/memory/sageox-ox-install.json` and reused every run.
 >
-> 1. **curl install** (recommended) — downloads the latest release tarball
->    and installs the pinned binary. Fastest, no build toolchain needed.
-> 2. **Build from git source** — clones `github.com/sageox/ox` and builds
->    with `make install`. Gives you latest `main`. Requires Go ≥ 1.24.
-
-Ask the user to pick 1 or 2. Save the choice to the memory file.
+> 1. **curl install** — runs the official install script from a pinned
+>    release tag. Fastest, no build toolchain needed. Lands in
+>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`
+>    (macOS). No auto-update; you'll re-run this flow to upgrade.
+> 2. **Build from git source** — clones `github.com/sageox/ox` to a
+>    directory you choose and builds with `make install`. Gives you
+>    latest `main`, and optionally auto-updates on every run. Requires
+>    Go ≥ 1.24.
+>
+> Reply `1` or `2`.
+
+**Blocking rule:** do not proceed until the user replies with `1` or
+`2`. If they say "you choose", "whatever", or try to skip, ask again and
+explain that this is a persisted choice. Once they answer, save it to
+the memory file.
+
+**Do not install `ox` via Homebrew or any package manager** (e.g.
+`brew install sageox/tap/ox`, `apt`, `dnf`, `pacman`). The tap exists
+for general use but is not supported inside OpenClaw skills — only
+`curl` and `git source` are. These two options work the same on macOS
+and Linux; pick based on whether the user wants a pinned release or
+`main` with optional auto-update, **not** based on their operating
+system.
 
 ##### Option 1: curl install
 
diff --git a/claws/openclaw/sageox-summary/SKILL.md b/claws/openclaw/sageox-summary/SKILL.md
@@ -198,16 +198,40 @@ cat ~/.openclaw/memory/sageox-ox-install.json 2>/dev/null
 `auto_update == true`, update ox before proceeding (see "Updating ox from
 git" below).
 
-**If the file does not exist:** prompt the user to choose an install method:
-
-> How do you want to install the `ox` CLI?
+**If the file does not exist:** STOP. This is a one-time decision that
+gets persisted to disk and affects every future run of this skill — the
+user must own it. You **MUST** ask the user which method they want and
+**wait for their response**. Do not pick a default. Do not guess. Do not
+run any install commands yet. Present both options verbatim, then stop
+and wait:
+
+> How do you want to install the `ox` CLI? Pick one — I won't choose for
+> you, because this gets saved to
+> `~/.openclaw/memory/sageox-ox-install.json` and reused every run.
 >
-> 1. **curl install** (recommended) — downloads the latest release tarball
->    and installs the pinned binary. Fastest, no build toolchain needed.
-> 2. **Build from git source** — clones `github.com/sageox/ox` and builds
->    with `make install`. Gives you latest `main`. Requires Go ≥ 1.24.
-
-Ask the user to pick 1 or 2. Save the choice to the memory file.
+> 1. **curl install** — runs the official install script from a pinned
+>    release tag. Fastest, no build toolchain needed. Lands in
+>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`
+>    (macOS). No auto-update; you'll re-run this flow to upgrade.
+> 2. **Build from git source** — clones `github.com/sageox/ox` to a
+>    directory you choose and builds with `make install`. Gives you
+>    latest `main`, and optionally auto-updates on every run. Requires
+>    Go ≥ 1.24.
+>
+> Reply `1` or `2`.
+
+**Blocking rule:** do not proceed until the user replies with `1` or
+`2`. If they say "you choose", "whatever", or try to skip, ask again and
+explain that this is a persisted choice. Once they answer, save it to
+the memory file.
+
+**Do not install `ox` via Homebrew or any package manager** (e.g.
+`brew install sageox/tap/ox`, `apt`, `dnf`, `pacman`). The tap exists
+for general use but is not supported inside OpenClaw skills — only
+`curl` and `git source` are. These two options work the same on macOS
+and Linux; pick based on whether the user wants a pinned release or
+`main` with optional auto-update, **not** based on their operating
+system.
 
 ##### Option 1: curl install
 
PATCH

echo "Gold patch applied."
