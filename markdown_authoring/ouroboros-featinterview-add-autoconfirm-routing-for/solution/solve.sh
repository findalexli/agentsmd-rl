#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "- The user can correct at any time by saying \"that's wrong\" \u2014 re-send correction" "skills/interview/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/interview/SKILL.md b/skills/interview/SKILL.md
@@ -105,12 +105,41 @@ MCP (question generator) ←→ You (answerer + router) ←→ User (human judgm
    ```
    Returns a session ID and the first question.
 
-2. **For each question from MCP, apply 3-Path Routing:**
+2. **For each question from MCP, apply the routing paths below:**
 
-   **PATH 1 — Code Confirmation** (describe current state, user confirms):
+   **PATH 1 — Code Answer** (describe current state from codebase):
    When the question asks about existing tech stack, frameworks, dependencies,
    current patterns, architecture, or file structure:
    - Use Read/Glob/Grep to find the factual answer
+   - **Description, not prescription**: "The project uses JWT" is fact.
+     "The new feature should also use JWT" is a DECISION — route to PATH 2.
+   - Evaluate confidence and choose sub-path:
+
+   **PATH 1a — Auto-confirm** (high-confidence factual, no user block):
+   When ALL of the following are true:
+   - The answer is found as an **exact match** in a manifest or config file
+     (e.g., `pyproject.toml`, `package.json`, `Dockerfile`, `go.mod`, `.env.example`)
+   - The answer is **purely descriptive** — it describes what exists, not what
+     the new feature should do
+   - There is **no ambiguity** — a single, clear answer (not multiple candidates)
+
+   Then:
+   - Send the answer to MCP immediately with `[from-code][auto-confirmed]` prefix
+   - Display a brief notification to the user (do NOT block):
+     `"ℹ️ Auto-confirmed: Python 3.12, FastAPI framework (pyproject.toml)"`
+   - The user can correct at any time by saying "that's wrong" — re-send correction to MCP
+   - Increment the auto-confirm counter (see Dialectic Rhythm Guard below)
+
+   Examples of auto-confirmable facts:
+   - Programming language (from pyproject.toml, package.json, go.mod)
+   - Framework (from dependencies in manifest)
+   - Python/Node version (from config files)
+   - Package manager (from lock files present)
+   - CI/CD tool (from .github/workflows/, Jenkinsfile, etc.)
+
+   **PATH 1b — Code Confirmation** (medium/low confidence, user confirms):
+   When the codebase has relevant information but confidence is not high enough
+   for auto-confirm (inferred from patterns, multiple candidates, or no manifest match):
    - Present findings to user as a **confirmation question** via AskUserQuestion:
      ```json
      {
@@ -125,10 +154,8 @@ MCP (question generator) ←→ You (answerer + router) ←→ User (human judgm
        }]
      }
      ```
-   - NEVER auto-send without user seeing and confirming
    - Prefix answer with `[from-code]` when sending to MCP
-   - **Description, not prescription**: "The project uses JWT" is fact.
-     "The new feature should also use JWT" is a DECISION — route to PATH 2.
+   - Increment the auto-confirm counter (see Dialectic Rhythm Guard below)
 
    **PATH 2 — Human Judgment** (decisions only humans can make):
    When the question asks about goals, vision, acceptance criteria, business logic,
@@ -175,7 +202,10 @@ MCP (question generator) ←→ You (answerer + router) ←→ User (human judgm
    Tool: ouroboros_interview
    Arguments:
      session_id: <session ID>
-     answer: "[from-code] JWT-based auth in src/auth/jwt.py" or "[from-user] Stripe Billing" or "[from-research] Stripe: 100 read ops/sec live mode"
+     answer: "[from-code][auto-confirmed] Python 3.12, FastAPI (pyproject.toml)"
+             or "[from-code] JWT-based auth in src/auth/jwt.py"
+             or "[from-user] Stripe Billing"
+             or "[from-research] Stripe: 100 read ops/sec live mode"
    ```
    MCP records the answer, generates the next question, and returns it.
 
@@ -193,11 +223,17 @@ MCP (question generator) ←→ You (answerer + router) ←→ User (human judgm
 
 #### Dialectic Rhythm Guard
 
-Track consecutive PATH 1/PATH 4 (code/research confirmation) answers. If 3
-consecutive questions were answered via PATH 1 or PATH 4, the next question MUST
-be routed to PATH 2 (directly to user), even if it appears code- or
-research-answerable. This preserves the Socratic dialectic rhythm — the interview
-is with the human, not the codebase or external docs.
+Track consecutive non-user answers (PATH 1a auto-confirms, PATH 1b code
+confirmations, and PATH 4 research confirmations). If **3 consecutive questions**
+were answered without direct user judgment (PATH 1a, 1b, or PATH 4), the next
+question MUST be routed to **PATH 2** (directly to user), even if it appears
+code- or research-answerable.
+
+This preserves the Socratic dialectic rhythm — the interview is with the human,
+not the codebase or external docs. Auto-confirmed answers especially need this
+guard: if the AI answers too many questions on its own, the user loses awareness
+of what the AI is assuming about their project.
+
 Reset the counter whenever user answers directly (PATH 2 or PATH 3).
 
 #### Retry on Failure
@@ -241,33 +277,40 @@ If the MCP tool is NOT available, fall back to agent-based interview:
 **You (main session)** are a Socratic facilitator:
 - Read `src/ouroboros/agents/socratic-interviewer.md` to understand the interview methodology
 - You CAN use Read/Glob/Grep to scan the codebase for answering MCP questions
-- You present every MCP question to the user (as confirmation or direct question)
-- You NEVER skip a question or auto-send without user seeing it
-- You NEVER make decisions on behalf of the user
+- For high-confidence factual questions (PATH 1a), auto-confirm and notify the user
+- For all other questions, present to user as confirmation or direct question
+- You NEVER make decisions on behalf of the user — auto-confirm is for FACTS only
+- The Dialectic Rhythm Guard prevents over-automation: after 3 consecutive
+  non-user answers, the next question MUST go directly to the user
 
 ## Example Session
 
 ```
 User: ooo interview Add payment module to existing project
 
 MCP Q1: "Is this a greenfield or brownfield project?"
-→ [Scanning... pyproject.toml, src/ found]
-→ Auto-answer: "Brownfield, Python/FastAPI project"
+→ PATH 1a: exact match in pyproject.toml + src/ directory
+→ ℹ️ Auto-confirmed: Brownfield, Python 3.12 / FastAPI (pyproject.toml)
+→ [from-code][auto-confirmed] sent to MCP (counter: 1)
 
 MCP Q2: "What payment provider will you use?"
-→ This is a human decision.
+→ PATH 2: human decision — no code can answer this
 → User: "Stripe"
+→ [from-user] sent to MCP (counter reset to 0)
 
 MCP Q3: "What authentication method does the project use?"
-→ [Scanning... src/auth/jwt.py found]
-→ Auto-answer: "JWT-based auth in src/auth/jwt.py"
+→ PATH 1b: found src/auth/jwt.py but inferred (not manifest)
+→ "I found JWT-based auth in src/auth/jwt.py. Is this correct?"
+→ User: "Yes, correct"
+→ [from-code] sent to MCP (counter: 1)
 
 MCP Q4: "How should payment failures affect order state?"
-→ This is a design decision.
+→ PATH 2: design decision
 → User: "Saga pattern for rollback"
+→ [from-user] sent to MCP (counter reset to 0)
 
 MCP Q5: "What are the acceptance criteria for this feature?"
-→ This requires human judgment.
+→ PATH 2: requires human judgment
 → User: "Successful Stripe charge, webhook handling, refund support"
 
 📍 Next: `ooo seed` to crystallize these requirements into a specification
PATCH

echo "Gold patch applied."
