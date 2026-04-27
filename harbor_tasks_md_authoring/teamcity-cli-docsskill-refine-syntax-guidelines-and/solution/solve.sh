#!/usr/bin/env bash
set -euo pipefail

cd /workspace/teamcity-cli

# Idempotency guard
if grep -qF "**Do not guess subcommands, flags, or syntax.** Only use commands and flags docu" "skills/teamcity-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/teamcity-cli/SKILL.md b/skills/teamcity-cli/SKILL.md
@@ -7,8 +7,6 @@ description: Use when working with TeamCity CI/CD or when user provides a TeamCi
 
 # TeamCity CLI (`tc`)
 
-Interact with TeamCity CI/CD servers using the `tc` command-line tool.
-
 ## Quick Start
 
 ```bash
@@ -19,7 +17,9 @@ tc run log <id> --failed          # View failed build log
 
 ## Before Running Commands
 
-**Do not guess flags or syntax.** Only use flags in the [Command Reference](references/commands.md). If unsure, run `tc <command> --help` first. If a command doesn't support what you need, fall back to `tc api /app/rest/...`.
+**Do not guess subcommands, flags, or syntax.** Only use commands and flags documented in the [Command Reference](references/commands.md) or shown by `tc <command> --help`. If a command doesn't support what you need, fall back to `tc api /app/rest/...`.
+
+**Terminology:** There is no `build`, `pipeline`, or `config` subcommand. Builds are **runs** (`tc run`). Build configurations are **jobs** (`tc job`).
 
 ## Core Commands
 
PATCH

echo "Gold patch applied."
