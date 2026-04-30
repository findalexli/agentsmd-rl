#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-governance-toolkit

# Idempotency guard
if grep -qF "- Marketing content disguised as a contribution (e.g., adding the contributor's " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -23,6 +23,11 @@ When external contributors open issues or PRs proposing integration with their o
 - **Verify claims**: If the PR cites benchmarks, adoption numbers, or production deployments, spot-check them. Unverifiable claims are a red flag.
 - **Scope proportionality**: A small or unknown project requesting a large integration surface (new package, new dependency, new CI pipeline) is disproportionate. Suggest they contribute as an example or community link instead.
 - **Dependency risk**: Adding a dependency on an obscure package creates supply chain risk. Prefer vendored examples or optional integrations that don't add to the core dependency tree.
+- **Spam/scam PR filter**: Close immediately with a polite note if the PR/issue is:
+  - Marketing content disguised as a contribution (e.g., adding the contributor's company to COMMUNITY.md or README.md as a "Related Project" when there's no genuine technical integration)
+  - From an account with <5 repos, <5 followers, created <3 months ago that submits promotional content to core docs
+  - Name-dropping awards, magazine features, publications, or rankings instead of providing technical value
+  - Repetitive submissions from the same contributor after previous PR was closed for the same reason (e.g., kevinkaylie/AgentNexus pattern)
 
 ## PR Merge Workflow
 
PATCH

echo "Gold patch applied."
