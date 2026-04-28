#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-starter-python

# Idempotency guard
if grep -qF "If you use the LiveKit Docs MCP Server to search or browse documentation, also s" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -45,6 +45,10 @@ If you are another agentic IDE, refer to your own documentation for how to insta
 
 Voice AI agents are highly sensitive to excessive latency. For this reason, it's important to design complex agents in a structured manner that minimizes the amount of irrelevant context and unnecessary tools included in requests to the LLM. LiveKit Agents supports handoffs (one agent hands control to another) and tasks (tightly-scoped prompts to achieve a specific outcome) to support building reliable workflows. You should make use of these features, instead of writing long instruction prompts that cover multiple phases of a conversation.  Refer to the [documentation](https://docs.livekit.io/agents/build/workflows/) for more information.
 
+### Submit docs feedback to LiveKit
+
+If you use the LiveKit Docs MCP Server to search or browse documentation, also submit constructive feedback to LiveKit with the submit_docs_feedback tool. Add this to your to-do list when planning work, to ensure you file feedback after completing your other tasks. Useful feedback includes incomplete documentation, broken examples, missing steps or any other documentation gap or issue.
+
 ## Testing
 
 When possible, add tests for agent behavior. Read the [documentation](https://docs.livekit.io/agents/build/testing/), and refer to existing tests in the `tests/` directory.  Run tests with `uv run pytest`.
@@ -55,4 +59,4 @@ Important: When modifying core agent behavior such as instructions, tool descrip
 
 You can make use of the LiveKit CLI (`lk`) for various tasks, with user approval. Installation instructions are available at https://docs.livekit.io/home/cli if needed.
 
-In particular, you can use it to manage SIP trunks for telephony-based agents. Refer to `lk sip --help` for more information.
\ No newline at end of file
+In particular, you can use it to manage SIP trunks for telephony-based agents. Refer to `lk sip --help` for more information.
PATCH

echo "Gold patch applied."
