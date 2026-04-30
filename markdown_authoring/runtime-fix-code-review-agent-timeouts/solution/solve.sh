#!/usr/bin/env bash
set -euo pipefail

cd /workspace/runtime

# Idempotency guard
if grep -qF "4. Present a single unified review to the user, noting when an issue was flagged" ".github/skills/code-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/code-review/SKILL.md b/.github/skills/code-review/SKILL.md
@@ -82,15 +82,17 @@ Now read the PR description, labels, linked issues (in full), author information
 When the environment supports launching sub-agents with different models (e.g., the `task` tool with a `model` parameter), run the review in parallel across multiple model families to get diverse perspectives. Different models catch different classes of issues. If the environment does not support this, proceed with a single-model review.
 
 **How to execute (when supported):**
-1. Inspect the available model list and select one model from each distinct model family (e.g., one Anthropic Claude, one Google Gemini, one OpenAI GPT). Use at least 2 and at most 4 models. **Model selection rules:**
+1. Inspect the available model list and select models from 2-3 distinct model families, up to 3 sub-agent models total. If fewer than 2 eligible families are available, use what is available. **Model selection rules:**
    - Pick only from models explicitly listed as available in the environment. Do not guess or assume model names.
-   - From each family, pick the model with the highest capability tier (prefer "premium" or "standard" over "fast/cheap").
+   - From each selected family, pick the model with the highest capability tier (prefer "premium" or "standard" over "fast/cheap").
    - Never pick models labeled "mini", "fast", or "cheap" for code review.
-   - If multiple standard-tier models exist in the same family (e.g., `gpt-5` and `gpt-5.1`), pick the one with the highest version number.
    - Do not select the same model that is already running the primary review (i.e., your own model). The goal is diverse perspectives from different model families.
+   - **Do not use `gpt-5.4`** — it has known reliability issues causing sub-agent timeouts in >90% of affected runs. For the OpenAI/GPT family, prefer `gpt-5.3-codex` if it is explicitly listed as available; otherwise, fall back to the highest-version non-blocked GPT model that satisfies the other rules here.
+   - If multiple standard-tier models exist in the same family (excluding blocked models above), pick the one with the highest version number. Prefer "-codex" variants over general-purpose for code review tasks.
 2. Launch a sub-agent for each selected model in parallel, giving each the same review prompt: the PR diff, the review rules from this skill, and instructions to produce findings in the severity format defined above.
 3. Wait for all agents to complete, then synthesize: deduplicate findings that appear across models, elevate issues flagged by multiple models (higher confidence), and include unique findings from individual models that meet the confidence bar. **Timeout handling:** If a sub-agent has not completed after 10 minutes and you have results from other agents, proceed with the results you have. Do not block the review indefinitely waiting for a single slow model. Note in the output which models contributed.
-4. Present a single unified review to the user, noting when an issue was flagged by multiple models.
+4. Present a single unified review to the user, noting when an issue was flagged by multiple models. **After posting the review, immediately exit.** Do not wait for any remaining sub-agents. Do not attempt retries if the comment was posted successfully. The review is complete once the post operation succeeds or returns a comment URL.
+
 
 ---
 
PATCH

echo "Gold patch applied."
