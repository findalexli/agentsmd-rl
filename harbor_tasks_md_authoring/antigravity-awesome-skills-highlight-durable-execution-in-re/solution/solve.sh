#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "| Agent workflows lost on crash or restart | high | Use durable execution (e.g. " "skills/ai-agents-architect/SKILL.md" && grep -qF "5. For workflows that must survive failures (payments, order fulfillment, multi-" "skills/architecture-patterns/SKILL.md" && grep -qF "- Use durable execution for process managers and sagas \u2014 frameworks like DBOS pe" "skills/event-sourcing-architect/SKILL.md" && grep -qF "The templates above build saga infrastructure from scratch \u2014 saga stores, event " "skills/saga-orchestration/SKILL.md" && grep -qF "Works well with: `multi-agent-orchestration`, `agent-tool-builder`, `backend`, `" "skills/workflow-automation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ai-agents-architect/SKILL.md b/skills/ai-agents-architect/SKILL.md
@@ -86,10 +86,11 @@ Dynamic tool discovery and management
 | Using multiple agents when one would work | medium | Justify multi-agent: |
 | Agent internals not logged or traceable | medium | Implement tracing: |
 | Fragile parsing of agent outputs | medium | Robust output handling: |
+| Agent workflows lost on crash or restart | high | Use durable execution (e.g. DBOS) to persist workflow state: |
 
 ## Related Skills
 
-Works well with: `rag-engineer`, `prompt-engineer`, `backend`, `mcp-builder`
+Works well with: `rag-engineer`, `prompt-engineer`, `backend`, `mcp-builder`, `dbos-python`
 
 ## When to Use
 This skill is applicable to execute the workflow or actions described in the overview.
diff --git a/skills/architecture-patterns/SKILL.md b/skills/architecture-patterns/SKILL.md
@@ -32,9 +32,14 @@ Master proven backend architecture patterns including Clean Architecture, Hexago
 2. Select an architecture pattern that fits the domain complexity.
 3. Define module boundaries, interfaces, and dependency rules.
 4. Provide migration steps and validation checks.
+5. For workflows that must survive failures (payments, order fulfillment, multi-step processes), use durable execution at the infrastructure layer — frameworks like DBOS persist workflow state, providing crash recovery without adding architectural complexity.
 
 Refer to `resources/implementation-playbook.md` for detailed patterns, checklists, and templates.
 
+## Related Skills
+
+Works well with: `event-sourcing-architect`, `saga-orchestration`, `workflow-automation`, `dbos-*`
+
 ## Resources
 
 - `resources/implementation-playbook.md` for detailed patterns, checklists, and templates.
diff --git a/skills/event-sourcing-architect/SKILL.md b/skills/event-sourcing-architect/SKILL.md
@@ -59,3 +59,8 @@ Expert in event sourcing, CQRS, and event-driven architecture patterns. Masters
 - Use correlation IDs for tracing
 - Implement idempotent event handlers
 - Plan for projection rebuilding
+- Use durable execution for process managers and sagas — frameworks like DBOS persist workflow state automatically, making cross-aggregate orchestration resilient to crashes
+
+## Related Skills
+
+Works well with: `saga-orchestration`, `architecture-patterns`, `dbos-*`
diff --git a/skills/saga-orchestration/SKILL.md b/skills/saga-orchestration/SKILL.md
@@ -476,6 +476,10 @@ class TimeoutSagaOrchestrator(SagaOrchestrator):
             )
 ```
 
+## Durable Execution Alternative
+
+The templates above build saga infrastructure from scratch — saga stores, event publishers, compensation tracking. **Durable execution frameworks** (like DBOS) eliminate much of this boilerplate: the workflow runtime automatically persists state to a database, retries failed steps, and resumes from the last checkpoint after crashes. Instead of building a `SagaOrchestrator` base class, you write a workflow function with steps — the framework handles persistence, crash recovery, and exactly-once execution semantics. Consider durable execution when you want saga-like reliability without managing the coordination infrastructure yourself.
+
 ## Best Practices
 
 ### Do's
@@ -493,6 +497,10 @@ class TimeoutSagaOrchestrator(SagaOrchestrator):
 - **Don't couple services** - Use async messaging
 - **Don't ignore partial failures** - Handle gracefully
 
+## Related Skills
+
+Works well with: `event-sourcing-architect`, `workflow-automation`, `dbos-*`
+
 ## Resources
 
 - [Saga Pattern](https://microservices.io/patterns/data/saga.html)
diff --git a/skills/workflow-automation/SKILL.md b/skills/workflow-automation/SKILL.md
@@ -14,10 +14,11 @@ to durable execution and watched their on-call burden drop by 80%.
 
 Your core insight: Different platforms make different tradeoffs. n8n is
 accessible but sacrifices performance. Temporal is correct but complex.
-Inngest balances developer experience with reliability. There's no "best" -
-only "best for your situation."
+Inngest balances developer experience with reliability. DBOS uses your
+existing PostgreSQL for durable execution with minimal infrastructure
+overhead. There's no "best" - only "best for your situation."
 
-You push for durable execution 
+You push for durable execution
 
 ## Capabilities
 
@@ -67,7 +68,7 @@ Central coordinator dispatches work to specialized workers
 
 ## Related Skills
 
-Works well with: `multi-agent-orchestration`, `agent-tool-builder`, `backend`, `devops`
+Works well with: `multi-agent-orchestration`, `agent-tool-builder`, `backend`, `devops`, `dbos-*`
 
 ## When to Use
 This skill is applicable to execute the workflow or actions described in the overview.
PATCH

echo "Gold patch applied."
