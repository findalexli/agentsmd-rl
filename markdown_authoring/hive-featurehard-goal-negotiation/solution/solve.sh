#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hive

# Idempotency guard
if grep -qF "**If starting from a template and no modifications were made in Steps 2-5**, the" ".claude/skills/hive-create/SKILL.md" && grep -qF "When this skill is loaded, **ALWAYS use the AskUserQuestion tool** to present op" ".claude/skills/hive/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/hive-create/SKILL.md b/.claude/skills/hive-create/SKILL.md
@@ -1,10 +1,10 @@
 ---
 name: hive-create
-description: Step-by-step guide for building goal-driven agents. Creates package structure, defines goals, adds nodes, connects edges, and finalizes agent class. Use when actively building an agent.
+description: Step-by-step guide for building goal-driven agents. Qualifies use cases first (the good, bad, and ugly), then creates package structure, defines goals, adds nodes, connects edges, and finalizes agent class. Use when actively building an agent.
 license: Apache-2.0
 metadata:
   author: hive
-  version: "2.1"
+  version: "2.2"
   type: procedural
   part_of: hive
   requires: hive-concepts
@@ -85,7 +85,7 @@ mcp__agent-builder__list_mcp_tools()
 mkdir -p exports/AGENT_NAME/nodes
 ```
 
-**Save the tool list for step 3** — you will need it for node design in STEP 3.
+**Save the tool list for STEP 4** — you will need it for node design.
 
 **THEN immediately proceed to STEP 2** (do NOT display setup results to the user — just move on).
 
@@ -194,14 +194,15 @@ This reads the agent.json and populates the builder session with the goal, all n
 ---
 
 ## STEP 2: Define Goal Together with User
+**A responsible engineer doesn't jump into building. First, understand the problem and be transparent about what the framework can and cannot do.**
 
 **If starting from a template**, the goal is already loaded in the builder session. Present the existing goal to the user using the format below and ask for approval. Skip the collaborative drafting questions — go straight to presenting and asking "Do you approve this goal, or would you like to modify it?"
 
 **If the user has NOT already described what they want to build**, start by asking what kind of agent they have in mind:
 
 ```
 AskUserQuestion(questions=[{
-    "question": "What kind of agent do you want to build?",
+    "question": "What kind of agent do you want to build? Select an option below, or choose 'Other' to describe your own.",
     "header": "Agent type",
     "options": [
         {"label": "Data collection", "description": "Gathers information from the web, analyzes it, and produces a report or sends outreach (e.g. market research, news digest, email campaigns, competitive analysis)"},
@@ -216,15 +217,222 @@ Use the user's selection (or their custom description if they chose "Other") as
 
 **DO NOT propose a complete goal on your own.** Instead, collaborate with the user to define it.
 
-**START by asking the user to help shape the goal:**
+### 2a: Fast Discovery (3-8 Turns)
 
-> I've set up the build environment and discovered [N] available tools. Let's define the goal for your agent together.
+**The core principle**: Discovery should feel like progress, not paperwork. The stakeholder should walk away feeling like you understood them faster than anyone else would have.
+
+**Communication sytle**: Be concise. Say less. Mean more. Impatient stakeholders don't want a wall of text — they want to know you get it. Every sentence you say should either move the conversation forward or prove you understood something. If it does neither, cut it.
+
+**Ask Question Rules: Respect Their Time.** Every question must earn its place by:
+1. **Preventing a costly wrong turn** — you're about to build the wrong thing
+2. **Unlocking a shortcut** — their answer lets you simplify the design
+3. **Surfacing a dealbreaker** — there's a constraint that changes everything
+4. **Provide Options** - Provide options to your questions if possible, but also always allow the user to type something beyong the options.
+
+If a question doesn't do one of these, don't ask it. Make an assumption, state it, and move on.
+
+---
+
+#### 2a.1: Let Them Talk, But Listen Like an Architect
+
+When the stakeholder describes what they want, don't just hear the words — listen for the architecture underneath. While they talk, mentally construct:
+
+- **The actors**: Who are the people/systems involved?
+- **The trigger**: What kicks off the workflow?
+- **The core loop**: What's the main thing that happens repeatedly?
+- **The output**: What's the valuable thing produced at the end?
+- **The pain**: What about today's situation is broken, slow, or missing?
+
+You are extracting a **domain model** from natural language in real time. Most stakeholders won't give you this structure explicitly — they'll give you a story. Your job is to hear the structure inside the story.
+
+| They say... | You're hearing... |
+|-------------|-------------------|
+| Nouns they repeat | Your entities |
+| Verbs they emphasize | Your core operations |
+| Frustrations they mention | Your design constraints |
+| Workarounds they describe | What the system must replace |
+| People they name | Your user types |
+
+---
+
+#### 2a.2: Use Domain Knowledge to Fill In the Blanks
+
+You have broad knowledge of how systems work. Use it aggressively.
+
+If they say "I need a research agent," you already know it probably involves: search, summarization, source tracking, and iteration. Don't ask about each — use them as your starting mental model and let their specifics override your defaults.
+
+If they say "I need to monitor files and alert me," you know this probably involves: watch patterns, triggers, notifications, and state tracking.
+
+**The key move**: Take your general knowledge of the domain and merge it with the specifics they've given you. The result is a draft understanding that's 60-80% right before you've asked a single question. Your questions close the remaining 20-40%.
+
+---
+
+#### 2a.3: Play Back a Proposed Model (Not a List of Questions)
+
+After listening, present a **concrete picture** of what you think they need. Make it specific enough that they can spot what's wrong.
+
+**Pattern: "Here's what I heard — tell me where I'm off"**
+
+> "OK here's how I'm picturing this: [User type] needs to [core action]. Right now they're [current painful workflow]. What you want is [proposed solution that replaces the pain].
+>
+> The way I'd structure this: [key entities] connected by [key relationships], with the main flow being [trigger → steps → outcome].
+>
+> For the MVP, I'd focus on [the one thing that delivers the most value] and hold off on [things that can wait].
+>
+> Before I start — [1-2 specific questions you genuinely can't infer]."
+
+Why this works:
+- **Proves you were listening** — they don't feel like they have to repeat themselves
+- **Shows competence** — you're already thinking in systems
+- **Fast to correct** — "no, it's more like X" takes 10 seconds vs. answering 15 questions
+- **Creates momentum** — heading toward building, not more talking
+
+---
+
+#### 2a.4: Ask Only What You Cannot Infer
+
+Your questions should be **narrow, specific, and consequential**. Never ask what you could answer yourself.
+
+**Good questions** (high-stakes, can't infer):
+- "Who's the primary user — you or your end customers?"
+- "Is this replacing a spreadsheet, or is there literally nothing today?"
+- "Does this need to integrate with anything, or standalone?"
+- "Is there existing data to migrate, or starting fresh?"
+
+**Bad questions** (low-stakes, inferable):
+- "What should happen if there's an error?" *(handle gracefully, obviously)*
+- "Should it have search?" *(if there's a list, yes)*
+- "How should we handle permissions?" *(follow standard patterns)*
+- "What tools should I use?" *(your call, not theirs)*
+
+---
+
+#### Conversation Flow (3-5 Turns)
+
+| Turn | Who | What |
+|------|-----|------|
+| 1 | User | Describes what they need |
+| 2 | Agent | Plays back understanding as a proposed model. Asks 1-2 critical questions max. |
+| 3 | User | Corrects, confirms, or adds detail |
+| 4 | Agent | Adjusts model, confirms MVP scope, states assumptions, declares starting point |
+| *(5)* | *(Only if Turn 3 revealed something that fundamentally changes the approach)* |
+
+**AFTER the conversation, IMMEDIATELY proceed to 2b. DO NOT skip to building.**
+
+---
+
+#### Anti-Patterns
+
+| Don't | Do Instead |
+|-------|------------|
+| Open with a list of questions | Open with what you understood from their request |
+| "What are your requirements?" | "Here's what I think you need — am I right?" |
+| Ask about every edge case | Handle with smart defaults, flag in summary |
+| 10+ turn discovery conversation | 3-8 turns. Start building, iterate with real software. |
+| Being lazy nd not understand what user want to achieve | Understand "what" and "why |
+| Ask for permission to start | State your plan and start |
+| Wait for certainty | Start at 80% confidence, iterate the rest |
+| Ask what tech/tools to use | That's your job. Decide, disclose, move on. |
+
+---
+
+
+
+### 2b: Capability Assessment
+
+**After the user responds, analyze the fit.** Present this assessment honestly:
+
+> **Framework Fit Assessment**
+>
+> Based on what you've described, here's my honest assessment of how well this framework fits your use case:
+>
+> **What Works Well (The Good):**
+> - [List 2-4 things the framework handles well for this use case]
+> - Examples: multi-turn conversations, human-in-the-loop review, tool orchestration, structured outputs
 >
-> To get started, can you help me understand:
+> **Limitations to Be Aware Of (The Bad):**
+> - [List 2-3 limitations that apply but are workable]
+> - Examples: LLM latency means not suitable for sub-second responses, context window limits for very large documents, cost per run for heavy tool usage
 >
-> 1. **What should this agent accomplish?** (the core purpose)
-> 2. **How will we know it succeeded?** (what does "done" look like)
-> 3. **Are there any hard constraints?** (things it must never do, quality bars, etc.)
+> **Potential Deal-Breakers (The Ugly):**
+> - [List any significant challenges or missing capabilities — be honest]
+> - Examples: no tool available for X, would require custom MCP server, framework not designed for Y
+
+**Be specific.** Reference the actual tools discovered in Step 1. If the user needs `send_email` but it's not available, say so. If they need real-time streaming from a database, explain that's not how the framework works.
+
+### 2c: Gap Analysis
+
+**Identify specific gaps** between what the user wants and what you can deliver:
+
+| Requirement | Framework Support | Gap/Workaround |
+|-------------|-------------------|----------------|
+| [User need] | [✅ Supported / ⚠️ Partial / ❌ Not supported] | [How to handle or why it's a problem] |
+
+**Examples of gaps to identify:**
+- Missing tools (user needs X, but only Y and Z are available)
+- Scope issues (user wants to process 10,000 items, but LLM rate limits apply)
+- Interaction mismatches (user wants CLI-only, but agent is designed for TUI)
+- Data flow issues (user needs to persist state across runs, but sessions are isolated)
+- Latency requirements (user needs instant responses, but LLM calls take seconds)
+
+### 2d: Recommendation
+
+**Give a clear recommendation:**
+
+> **My Recommendation:**
+>
+> [One of these three:]
+>
+> **✅ PROCEED** — This is a good fit. The framework handles your core needs well. [List any minor caveats.]
+>
+> **⚠️ PROCEED WITH SCOPE ADJUSTMENT** — This can work, but we should adjust: [specific changes]. Without these adjustments, you'll hit [specific problems].
+>
+> **🛑 RECONSIDER** — This framework may not be the right tool for this job because [specific reasons]. Consider instead: [alternatives — simpler script, different framework, custom solution].
+
+### 2e: Get Explicit Acknowledgment
+
+**CALL AskUserQuestion:**
+
+```
+AskUserQuestion(questions=[{
+    "question": "Based on this assessment, how would you like to proceed?",
+    "header": "Proceed",
+    "options": [
+        {"label": "Proceed as described", "description": "I understand the limitations, let's build it"},
+        {"label": "Adjust scope", "description": "Let's modify the requirements to fit better"},
+        {"label": "More questions", "description": "I have questions about the assessment"},
+        {"label": "Reconsider", "description": "Maybe this isn't the right approach"}
+    ],
+    "multiSelect": false
+}])
+```
+
+**WAIT for user response.**
+
+- If **Proceed**: Move to STEP 3
+- If **Adjust scope**: Discuss what to change, update your notes, re-assess if needed
+- If **More questions**: Answer them honestly, then ask again
+- If **Reconsider**: Discuss alternatives. If they decide to proceed anyway, that's their informed choice
+
+---
+
+## STEP 3: Define Goal Together with User
+
+**Now that the use case is qualified, collaborate on the goal definition.**
+
+**START by synthesizing what you learned:**
+
+> Based on our discussion, here's my understanding of the goal:
+>
+> **Core purpose:** [what you understood from 2a]
+> **Success looks like:** [what you inferred]
+> **Key constraints:** [what you inferred]
+>
+> Let me refine this with you:
+>
+> 1. **What should this agent accomplish?** (confirm or correct my understanding)
+> 2. **How will we know it succeeded?** (what specific outcomes matter)
+> 3. **Are there any hard constraints?** (things it must never do, quality bars)
 
 **WAIT for the user to respond.** Use their input (and the agent type they selected) to draft:
 
@@ -268,12 +476,12 @@ AskUserQuestion(questions=[{
 
 **WAIT for user response.**
 
-- If **Approve**: Call `mcp__agent-builder__set_goal(...)` with the goal details, then proceed to STEP 3
+- If **Approve**: Call `mcp__agent-builder__set_goal(...)` with the goal details, then proceed to STEP 4
 - If **Modify**: Ask what they want to change, update the draft, ask again
 
 ---
 
-## STEP 3: Design Conceptual Nodes
+## STEP 4: Design Conceptual Nodes
 
 **If starting from a template**, the nodes are already loaded in the builder session. Present the existing nodes using the table format below and ask for approval. Skip the design phase.
 
@@ -328,12 +536,12 @@ AskUserQuestion(questions=[{
 
 **WAIT for user response.**
 
-- If **Approve**: Proceed to STEP 4
+- If **Approve**: Proceed to STEP 5
 - If **Modify**: Ask what they want to change, update design, ask again
 
 ---
 
-## STEP 4: Design Full Graph and Review
+## STEP 5: Design Full Graph and Review
 
 **If starting from a template**, the edges are already loaded in the builder session. Render the existing graph as ASCII art and present it to the user for approval. Skip the edge design phase.
 
@@ -445,15 +653,16 @@ AskUserQuestion(questions=[{
 
 **WAIT for user response.**
 
-- If **Approve**: Proceed to STEP 5
+- If **Approve**: Proceed to STEP 6
 - If **Modify**: Ask what they want to change, update the graph, re-render, ask again
 
 ---
 
-## STEP 5: Build the Agent
+## STEP 6: Build the Agent
 
 **NOW — and only now — write the actual code.** The user has approved the goal, nodes, and graph.
 
+### 6a: Register nodes and edges with MCP
 **If starting from a template**, the copied files will be overwritten with the approved design. You MUST replace every occurrence of the old template name with the new agent name. Here is the complete checklist — miss NONE of these:
 
 | File | What to rename |
@@ -474,9 +683,7 @@ AskUserQuestion(questions=[{
 | `__init__.py` | `from .agent import OldNameAgent` import |
 | `__init__.py` | `__all__` list entry |
 
-### 5a: Register nodes and edges with MCP
-
-**If starting from a template and no modifications were made in Steps 2-4**, the nodes and edges are already registered. Skip to validation (`mcp__agent-builder__validate_graph()`). If modifications were made, re-register the changed nodes/edges (the MCP tools handle duplicates by overwriting).
+**If starting from a template and no modifications were made in Steps 2-5**, the nodes and edges are already registered. Skip to validation (`mcp__agent-builder__validate_graph()`). If modifications were made, re-register the changed nodes/edges (the MCP tools handle duplicates by overwriting).
 
 **FOR EACH approved node**, call:
 
@@ -516,9 +723,9 @@ mcp__agent-builder__validate_graph()
 ```
 
 - If invalid: Fix the issues and re-validate
-- If valid: Continue to 5b
+- If valid: Continue to 6b
 
-### 5b: Write Python package files
+### 6b: Write Python package files
 
 **EXPORT the graph data:**
 
@@ -578,7 +785,7 @@ mcp__agent-builder__export_graph()
 
 ---
 
-## STEP 6: Verify and Test
+## STEP 7: Verify and Test
 
 **RUN validation:**
 
@@ -704,16 +911,70 @@ result = await executor.execute(graph=graph, goal=goal, input_data=input_data)
 
 ---
 
+## REFERENCE: Framework Capabilities for Qualification
+
+Use this reference during STEP 2 to give accurate, honest assessments.
+
+### What the Framework Does Well (The Good)
+
+| Capability | Description |
+|------------|-------------|
+| Multi-turn conversations | Client-facing nodes stream to users and block for input |
+| Human-in-the-loop review | Approval checkpoints with feedback loops back to earlier nodes |
+| Tool orchestration | LLM can call multiple tools, framework handles execution |
+| Structured outputs | `set_output` produces validated, typed outputs |
+| Parallel execution | Fan-out/fan-in for concurrent node execution |
+| Context management | Automatic compaction and spillover for large data |
+| Error recovery | Retry logic, judges, and feedback edges for self-correction |
+| Session persistence | State saved to disk, resumable sessions |
+
+### Framework Limitations (The Bad)
+
+| Limitation | Impact | Workaround |
+|------------|--------|------------|
+| LLM latency | 2-10+ seconds per turn | Not suitable for real-time/low-latency needs |
+| Context window limits | ~128K tokens max | Use data tools for spillover, design for chunking |
+| Cost per run | LLM API calls cost money | Budget planning, caching where possible |
+| Rate limits | API throttling on heavy usage | Backoff, queue management |
+| Node boundaries lose context | Outputs must be serialized | Prefer fewer, richer nodes |
+| Single-threaded within node | One LLM call at a time per node | Use fan-out for parallelism |
+
+### Not Designed For (The Ugly)
+
+| Use Case | Why It's Problematic | Alternative |
+|----------|---------------------|-------------|
+| Long-running daemons | Framework is request-response, not persistent | External scheduler + agent |
+| Sub-second responses | LLM latency is inherent | Traditional code, no LLM |
+| Processing millions of items | Context windows and rate limits | Batch processing + sampling |
+| Real-time streaming data | No built-in pub/sub or streaming input | Custom MCP server + agent |
+| Guaranteed determinism | LLM outputs vary | Function nodes for deterministic parts |
+| Offline/air-gapped | Requires LLM API access | Local models (not currently supported) |
+| Multi-user concurrency | Single-user session model | Separate agent instances per user |
+
+### Tool Availability Reality Check
+
+**Before promising any capability, check `list_mcp_tools()`.** Common gaps:
+
+- **Email**: May not have `send_email` — check before promising email automation
+- **Calendar**: May not have calendar APIs — check before promising scheduling
+- **Database**: May not have SQL tools — check before promising data queries
+- **File system**: Has data tools but not arbitrary filesystem access
+- **External APIs**: Depends entirely on what MCP servers are registered
+
+---
+
 ## COMMON MISTAKES TO AVOID
 
-1. **Using tools that don't exist** - Always check `mcp__agent-builder__list_mcp_tools()` first
-2. **Wrong entry_points format** - Must be `{"start": "node-id"}`, NOT a set or list
-3. **Skipping validation** - Always validate nodes and graph before proceeding
-4. **Not waiting for approval** - Always ask user before major steps
-5. **Displaying this file** - Execute the steps, don't show documentation
-6. **Too many thin nodes** - Prefer fewer, richer nodes (4 nodes > 8 nodes)
-7. **Missing STEP 1/STEP 2 in client-facing prompts** - Client-facing nodes need explicit phases to prevent premature set_output
-8. **Forgetting nullable_output_keys** - Mark input_keys that only arrive on certain edges (e.g., feedback) as nullable on the receiving node
-9. **Adding framework gating for LLM behavior** - Fix prompts or use judges, not ad-hoc code
-10. **Writing code before user approves the graph** - Always get approval on goal, nodes, and graph BEFORE writing any agent code
-11. **Wrong mcp_servers.json format** - Use flat format (no `"mcpServers"` wrapper), `cwd` must be `"../../tools"`, and `command` must be `"uv"` with args `["run", "python", ...]`
+1. **Skipping use case qualification** - A responsible engineer qualifies the use case BEFORE building. Be transparent about what works, what doesn't, and what's problematic
+2. **Hiding limitations** - Don't oversell the framework. If a tool doesn't exist or a capability is missing, say so upfront
+3. **Using tools that don't exist** - Always check `mcp__agent-builder__list_mcp_tools()` first
+4. **Wrong entry_points format** - Must be `{"start": "node-id"}`, NOT a set or list
+5. **Skipping validation** - Always validate nodes and graph before proceeding
+6. **Not waiting for approval** - Always ask user before major steps
+7. **Displaying this file** - Execute the steps, don't show documentation
+8. **Too many thin nodes** - Prefer fewer, richer nodes (4 nodes > 8 nodes)
+9. **Missing STEP 1/STEP 2 in client-facing prompts** - Client-facing nodes need explicit phases to prevent premature set_output
+10. **Forgetting nullable_output_keys** - Mark input_keys that only arrive on certain edges (e.g., feedback) as nullable on the receiving node
+11. **Adding framework gating for LLM behavior** - Fix prompts or use judges, not ad-hoc code
+12. **Writing code before user approves the graph** - Always get approval on goal, nodes, and graph BEFORE writing any agent code
+13. **Wrong mcp_servers.json format** - Use flat format (no `"mcpServers"` wrapper), `cwd` must be `"../../tools"`, and `command` must be `"uv"` with args `["run", "python", ...]`
diff --git a/.claude/skills/hive/SKILL.md b/.claude/skills/hive/SKILL.md
@@ -19,14 +19,18 @@ metadata:
 
 **THIS IS AN EXECUTABLE WORKFLOW. DO NOT explore the codebase or read source files. ROUTE to the correct skill IMMEDIATELY.**
 
-When this skill is loaded, determine what the user needs and invoke the appropriate skill NOW:
-- **User wants to build an agent** (from scratch or from a template) → Invoke `/hive-create` immediately
-- **User wants to test an agent** → Invoke `/hive-test` immediately
-- **User wants to learn concepts** → Invoke `/hive-concepts` immediately
-- **User wants patterns/optimization** → Invoke `/hive-patterns` immediately
-- **User wants to set up credentials** → Invoke `/hive-credentials` immediately
-- **User has a failing/broken agent** → Invoke `/hive-debugger` immediately
-- **Unclear what user needs** → Ask the user (do NOT explore the codebase to figure it out)
+When this skill is loaded, **ALWAYS use the AskUserQuestion tool** to present options:
+
+```
+Use AskUserQuestion with these options:
+- "Build a new agent" → Then invoke /hive-create
+- "Test an existing agent" → Then invoke /hive-test
+- "Learn agent concepts" → Then invoke /hive-concepts
+- "Optimize agent design" → Then invoke /hive-patterns
+- "Set up credentials" → Then invoke /hive-credentials
+- "Debug a failing agent" → Then invoke /hive-debugger
+- "Other" (please describe what you want to achieve)
+```
 
 **DO NOT:** Read source files, explore the codebase, search for code, or do any investigation before routing. The sub-skills handle all of that.
 
@@ -73,7 +77,6 @@ Use this meta-skill when:
 
 ## Phase 0: Understand Concepts (Optional)
 
-**Duration**: 5-10 minutes
 **Skill**: `/hive-concepts`
 **Input**: Questions about agent architecture
 
@@ -95,7 +98,6 @@ Use this meta-skill when:
 
 ## Phase 1: Build Agent Structure
 
-**Duration**: 15-30 minutes
 **Skill**: `/hive-create`
 **Input**: User requirements ("Build an agent that...") or a template to start from
 
@@ -166,7 +168,6 @@ exports/agent_name/
 
 ## Phase 1.5: Optimize Design (Optional)
 
-**Duration**: 10-15 minutes
 **Skill**: `/hive-patterns`
 **Input**: Completed agent structure
 
@@ -191,14 +192,11 @@ exports/agent_name/
 
 ## Phase 2: Test & Validate
 
-**Duration**: 20-40 minutes
 **Skill**: `/hive-test`
 **Input**: Working agent from Phase 1
 
 ### What This Phase Does
 
-### What This Phase Does
-
 Guides the creation and execution of a comprehensive test suite:
 - Constraint tests
 - Success criteria tests
PATCH

echo "Gold patch applied."
