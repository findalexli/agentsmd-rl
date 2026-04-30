#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-message-queue

# Idempotency guard
if grep -qF "AMQ uses two env vars for routing: `AM_ROOT` (which mailbox tree) and `AM_ME` (w" "skills/amq-cli/SKILL.md" && grep -qF "| `phase:research` | **Before reading**: check if you've already submitted your " "skills/amq-spec/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/amq-cli/SKILL.md b/skills/amq-cli/SKILL.md
@@ -1,15 +1,19 @@
 ---
 name: amq-cli
-version: 1.8.0
+version: 1.9.0
 description: >-
-  Send and receive messages between coding agents via AMQ CLI.
-  TRIGGER when: "message codex/claude", "send to partner agent",
-  "check inbox", "drain messages", "co-op mode", "AMQ",
-  "cross-project peers", "agent coordination", "wake agent",
-  "swarm join", "diagnose delivery".
-  DO NOT TRIGGER: RabbitMQ/Kafka design, Kubernetes networking,
-  CI/CD pipelines, Slack bots, or single-agent tasks with no partner.
-  For collaborative spec/design, consider /spec.
+  Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use
+  this skill whenever you need to send messages to another agent (codex, claude,
+  or any named handle), check your inbox, drain queued messages, set up co-op
+  mode between agents, join a swarm team, route messages across projects, or
+  diagnose delivery issues. Also use it when you receive a message and need to
+  know how to reply, ack, or handle priority. Covers any multi-agent
+  coordination task where agents need to talk to each other — review requests,
+  questions, status updates, decision threads, wake notifications, and
+  orchestrator integration (Symphony, Kanban). For collaborative spec/design
+  workflows specifically, prefer the /amq-spec skill which provides structured
+  phase-by-phase guidance. Not intended for distributed systems design
+  (RabbitMQ, Kafka), CI/CD pipelines, or single-agent tasks with no partner.
 metadata:
   short-description: Inter-agent messaging via AMQ CLI
   compatibility: claude-code, codex-cli
@@ -28,28 +32,30 @@ Requires `amq` binary in PATH. Install:
 curl -fsSL https://raw.githubusercontent.com/avivsinai/agent-message-queue/main/scripts/install.sh | bash
 ```
 
-## Environment Rules (IMPORTANT)
+## Environment Rules
 
-When running inside `coop exec`, the environment is already configured:
+AMQ uses two env vars for routing: `AM_ROOT` (which mailbox tree) and `AM_ME` (which agent). Getting these wrong means messages go to the wrong place or silently disappear, so it matters to let the CLI handle them rather than guessing.
 
-- **Always use `amq` from PATH** — never `./amq`, `../amq`, or absolute paths
-- **Never override `AM_ROOT` or `AM_ME`** — they are set by `coop exec`
-- **Never pass `--root` or `--me` flags** — env vars handle routing
-- **Just run commands as-is**: `amq send --to codex --body "hello"`
+**Inside `coop exec`** — everything is pre-configured. Just run bare commands:
+```bash
+amq send --to codex --body "hello"     # correct
+amq send --me claude --to codex ...    # wrong — --me overrides the env
+./amq send ...                         # wrong — use amq from PATH
+```
+The reason: `coop exec` sets `AM_ROOT` and `AM_ME` precisely for the session. Passing `--root` or `--me` overrides that and can route to the wrong mailbox.
+
+**Outside `coop exec`** — resolve the root from config, don't hardcode it:
+```bash
+eval "$(amq env --me claude)"          # reads .amqrc chain, sets both vars
+
+# Or pin per-command without polluting the shell (useful in scripts):
+AM_ME=claude AM_ROOT=$(amq env --json | jq -r .root) amq send --to codex --body "hello"
+```
+Why not hardcode? The root path depends on the config chain (project `.amqrc` → `AMQ_GLOBAL_ROOT` → `~/.amqrc`). Hardcoding skips this and breaks when the project moves or config changes.
 
-When running **outside** `coop exec` (e.g. new conversation, manual terminal):
+**Global fallback**: Orchestrator-spawned agents often start outside the repo root where no project `.amqrc` exists. Set `AMQ_GLOBAL_ROOT` or `~/.amqrc` so `amq env` and `amq doctor` still resolve the correct queue.
 
-- **Use `amq env` to resolve the root** — it reads the full chain (project `.amqrc`, `AMQ_GLOBAL_ROOT`, `~/.amqrc`) and returns the resolved root:
-  ```bash
-  eval "$(amq env --me claude)"          # sets AM_ME + AM_ROOT from resolved config
-  ```
-- Or resolve and pin explicitly per command (never hardcode the root — read it from `amq env`):
-  ```bash
-  AM_ME=claude AM_ROOT=$(amq env --json | jq -r .root) amq send --to codex --body "hello"
-  ```
-- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.
-- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agent-mail`. Only use a session path if the target agent is also in that session.
-- **Global fallback**: external orchestrators often start outside the repo root. In that case, set `AMQ_GLOBAL_ROOT` or `~/.amqrc` so `amq env`, `amq doctor`, and integration commands resolve the same queue.
+**Session pitfall**: `coop exec` defaults to `--session collab` (i.e., `.agent-mail/collab`). Outside `coop exec`, the base root is `.agent-mail` (no session suffix). These are different mailbox trees — don't mix them up.
 
 ### Root Resolution Truth-Table
 
@@ -61,16 +67,16 @@ When running **outside** `coop exec` (e.g. new conversation, manual terminal):
 | Inside `coop exec` (no flags) | automatic | `.agent-mail/collab` (default session) |
 | Inside `coop exec --session X` | automatic | `.agent-mail/X` |
 
-## Task Routing — READ THIS FIRST
+## Task Routing
 
-**Before doing anything**, match your task to the right workflow:
+Before diving in, match the task to the right workflow — this avoids wasted effort:
 
-| Your task | What to do | DO NOT |
-|-----------|-----------|--------|
-| **"spec", "design with", "collaborative spec"** | Use the `/spec` command instead. It provides structured phase-by-phase guidance. | Do NOT handle spec tasks from this skill. |
-| **Send a message, review request, question** | Use `amq send` (see Messaging below) | — |
-| **Swarm / agent teams** | Read [references/swarm-mode.md](references/swarm-mode.md), then use `amq swarm` | — |
-| **Received message with labels `workflow:spec`** | Follow the spec skill protocol: do independent research first, then engage on the `spec/<topic>` thread. | Do NOT skip straight to implementation. |
+| Your task | What to do |
+|-----------|-----------|
+| **"spec", "design with", "collaborative spec"** | Use `/amq-spec` instead — it has structured phase-by-phase guidance for parallel-research workflows. |
+| **Send a message, review request, question** | Use `amq send` (see Messaging below) |
+| **Swarm / agent teams** | Read [references/swarm-mode.md](references/swarm-mode.md), then use `amq swarm` |
+| **Received message with labels `workflow:spec`** | Follow the spec skill protocol: do independent research first, then engage on the `spec/<topic>` thread — don't skip straight to implementation. |
 
 ## Quick Start
 
diff --git a/skills/amq-spec/SKILL.md b/skills/amq-spec/SKILL.md
@@ -1,22 +1,25 @@
 ---
 name: amq-spec
-version: 1.2.0
+version: 1.3.0
 description: >-
-  Parallel-research-then-converge design workflow between two agents.
-  TRIGGER when: "spec X with codex/claude", "design X together",
-  "both agents think through X", "brainstorm architecture together",
-  "parallel research then joint proposal", "think through separately
-  then align", "careful thought from both sides before coding".
-  DO NOT TRIGGER: splitting implementation work between agents,
-  sending messages or reviews (see /amq-cli), implementing completed
+  Parallel-research-then-converge design workflow between two agents. Use this
+  skill when the user wants two agents to independently think through a design
+  problem before aligning on a solution — "spec X with codex", "design X
+  together", "both agents think through X", "brainstorm architecture together",
+  "parallel research then joint proposal", "think through separately then
+  align", "careful thought from both sides before coding", or any variation
+  where the user wants collaborative design rather than just splitting
+  implementation work. Also use this when you receive a message labeled
+  workflow:spec and need to know the correct receiver-side protocol. Not for
+  sending simple messages or reviews (use /amq-cli), implementing completed
   designs, or creating document templates.
 argument-hint: "<description of what to design> [with <partner>]"
 metadata:
   short-description: Multi-agent collaborative spec workflow
   compatibility: claude-code, codex-cli
 ---
 
-# /spec — Collaborative Specification Workflow
+# /amq-spec — Collaborative Specification Workflow
 
 This skill defines a structured two-agent specification flow.
 
@@ -43,22 +46,25 @@ If topic/problem are unclear, ask for clarification.
 
 ## First Action: Send problem to partner IMMEDIATELY
 
-**CRITICAL: Do this FIRST, before ANY research, exploration, or code reading.**
-The entire point of the spec workflow is parallel research. Every second you
-spend researching before sending is a second your partner sits idle.
+The entire point of the spec workflow is parallel research — both agents
+exploring the problem independently, then comparing notes. Every second you
+spend researching before sending is a second your partner sits idle waiting
+for the problem statement. That's why the send comes first, even though your
+instinct might be to "research first to give better context."
 
 ```bash
 amq send --to <partner> --kind question \
   --labels workflow:spec,phase:request \
   --thread spec/<topic> --subject "Spec: <topic>" --body "<problem>"
 ```
 
-Send the user's problem description verbatim. Do NOT include your own analysis.
-Do NOT pre-research "to give better context". Send it NOW, then research.
+Send the user's problem description verbatim — your own analysis goes in the
+research phase, not the kickoff. If you pre-analyze, you bias the partner's
+independent research, which defeats the purpose of having two perspectives.
 
-## Label Convention (MANDATORY)
+## Label Convention
 
-Use existing AMQ kinds plus labels to express spec workflow semantics:
+Labels are how both agents and the receiver-side protocol table know which phase the conversation is in. Use existing AMQ kinds plus labels to express spec workflow semantics:
 
 | Phase | Kind | Labels |
 |---|---|---|
@@ -111,27 +117,28 @@ If you receive a message labeled `workflow:spec`, your action depends on the pha
 | Label | Your action |
 |---|---|
 | `phase:request` | Read the problem statement, do your **own independent research first**, then submit findings as `brainstorm` + `phase:research` |
-| `phase:research` | Read thread, start discussion as `brainstorm` + `phase:discuss` |
+| `phase:research` | **Before reading**: check if you've already submitted your own research on this thread. If not, do your own research and submit it first. This preserves research independence — reading the partner's findings before forming your own view contaminates your perspective. Once your research is submitted, read the thread and start discussion as `brainstorm` + `phase:discuss`. |
 | `phase:discuss` | Reply with your analysis, continue discussion until aligned |
-| `phase:draft` | **REVIEW the plan and send feedback** as `review_response` + `phase:review`. Do NOT implement. |
+| `phase:draft` | Review the plan and send feedback as `review_response` + `phase:review`. Your job here is review, not implementation — the plan needs to survive scrutiny before anyone builds it. |
 | `phase:review` | Revise plan if needed, or confirm alignment |
-| `phase:decision` | **STOP. Do NOT implement.** Only the user can authorize implementation. Wait for the initiator to confirm user approval. |
-
-**The partner agent NEVER implements.** Only the initiator presents the plan
-to the user. Implementation starts only after the initiator explicitly tells
-you the user approved and assigns you work.
-
-## Non-Negotiable Rules
-
-- **NEVER** research before sending the problem to your partner. Send FIRST, research SECOND.
-- **NEVER** skip phases or collapse directly to a finished spec.
-- **NEVER** read partner research before submitting your own research.
-- **NEVER** enter plan mode during research if it blocks tool usage.
-- **NEVER** implement when you receive a plan. Review it and send feedback — that's your job.
-- **NEVER** implement before the user approves the final plan in chat. Only the initiator talks to the user.
-- **ALWAYS** use `--thread spec/<topic>` for spec workflow messages.
-- **ALWAYS** use the label convention table above.
-- **ALWAYS** present the final plan to the user and wait for explicit approval.
+| `phase:decision` | Stop. Only the user can authorize implementation. The initiator presents the plan to the user; you wait until the initiator confirms approval and assigns you work. |
+
+**Why the partner doesn't implement**: The spec workflow is a design process.
+The initiator owns the relationship with the user and presents the final plan.
+If the partner implements without approval, the user loses control over what
+gets built. Implementation starts only after the initiator explicitly tells
+you the user approved and assigns work.
+
+## Protocol Discipline
+
+These rules exist because violations silently break the workflow's value proposition:
+
+- **Send before researching** — parallel research is the whole point. Pre-researching wastes your partner's time and biases the outcome toward your initial framing.
+- **Submit your own research before reading partner's** — reading first contaminates your independent perspective. Two agents who read the same code and reach the same conclusion is less valuable than two agents who explore independently and then compare notes.
+- **Don't skip phases** — each phase builds on the previous. Collapsing directly to a finished spec skips the discussion where misunderstandings surface.
+- **Use `spec/<topic>` threads and the label convention** — this is how both agents (and the tooling) know which phase the conversation is in. Without consistent labels, the receiver-side protocol table above breaks.
+- **Don't enter plan mode during research** if it blocks tool usage — you need tools to explore the codebase.
+- **Present the final plan to the user before executing** — the initiator owns the user relationship. After the decision phase, present the plan in chat and wait for explicit approval. Only then assign implementation work to agents.
 
 ## Reference
 
PATCH

echo "Gold patch applied."
