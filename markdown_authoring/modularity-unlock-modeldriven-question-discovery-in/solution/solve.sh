#!/usr/bin/env bash
set -euo pipefail

cd /workspace/modularity

# Idempotency guard
if grep -qF "Ask the user about each gap individually using `AskUserQuestion`. Skip what's cl" "skills/high-level-design/SKILL.md" && grep -qF "4. **Discover what you still need.** You know the Balanced Coupling model. You k" "skills/review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/high-level-design/SKILL.md b/skills/high-level-design/SKILL.md
@@ -40,7 +40,14 @@ Follow these steps strictly. Each step requires explicit user approval before mo
 Read the functional requirements file. Then:
 
 1. **Restate the functional requirements** in your own words. Organize them into cohesive functional areas.
-2. **Identify what's unclear.** List every ambiguity, missing piece, or assumption you'd need to make. Ask the user about each one individually using `AskUserQuestion` with concrete options where possible.
+2. **Discover what's missing for coupling-aware design.** Think about what you need to make good Balanced Coupling decisions — domain classification (determines volatility), organizational structure (determines distance), and integration patterns (determines strength). Identify gaps in the requirements, especially:
+   - Business areas where core vs supporting vs generic classification is ambiguous — propose your interpretation and ask the user to confirm or correct
+   - Organizational constraints that affect module boundaries (team ownership, deployment units, shared infrastructure)
+   - Strategic direction that affects where volatility will be highest and where to invest design effort
+   - Integration requirements where the appropriate coupling strength is unclear
+
+   Ask the user about each gap individually using `AskUserQuestion`. Skip what's clear from the requirements. Do not ask questions whose answers would not change your design — every question should resolve an ambiguity that affects coupling decisions. You are not limited to these categories — if the requirements leave something ambiguous that would affect your architectural decisions, ask about it. Ground questions in specific requirements you read.
+
 3. **Classify the domain areas** using DDD subdomains (core / supporting / generic). This determines volatility and where to invest design effort. Analyze the requirements and propose classifications yourself. Present them as a table:
 
 | Subdomain | Classification | Rationale |
diff --git a/skills/review/SKILL.md b/skills/review/SKILL.md
@@ -30,16 +30,28 @@ Always use `AskUserQuestion` for user input. Follow these principles:
 
 ### Step 1: Understand the Problem Domain
 
-1. Read all functional requirements documents available in the `docs/` folder. Understand the problem domain, business capabilities, and the system's intended behavior before looking at any code.
-2. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I'll tell you which path", "Specific components — I'll name them". If the user picks a specific scope, follow up to collect details. Otherwise, explore the project structure to identify the major modules, services, and their boundaries.
-3. Read the code. Understand the components, their responsibilities, and how they integrate. Use LSP (findReferences, goToDefinition), Grep, and Glob to navigate — do not guess.
-4. Use `AskUserQuestion` to ask about anything you cannot determine from the code or requirements alone. Ask each question separately — one at a time.
+1. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I'll tell you which path", "Specific components — I'll name them". If the user picks a specific scope, follow up to collect details.
 
-   **Domain classification**: Header: "Domain". First, ask the user (free text) which business areas/components are core (competitive advantage, high volatility), supporting, or generic subdomains. Do not list all discovered components as options. If they mention many areas, either group them and ask follow-up `AskUserQuestion` prompts that classify 2–4 areas at a time, or focus on the top 2–4 most important areas they highlight.
+2. **Read before asking.** Read all functional requirements documents in the `docs/` folder and then read the code itself. Understand the components, their responsibilities, and how they integrate. Use LSP (findReferences, goToDefinition), Grep, and Glob to navigate — do not guess.
 
-   **Team structure**: Header: "Teams". Options: "Same team — Single team owns everything", "Multiple teams — Different teams own different parts", "Mixed / not sure".
+3. **Surface your understanding.** Before asking domain questions, present a brief synthesis of what you learned from the code and requirements:
+   - Components you found and their responsibilities
+   - Integration patterns you observed (shared types, API calls, database access, event flows)
+   - Your best guess at domain classification (core / supporting / generic) with reasoning and confidence level — low confidence areas are the strongest candidates for follow-up questions
+   - Assumptions you're making about team structure, deployment topology, or design intent
 
-   **Known pain points**: Header: "Pain points". Options: "Yes — I'll describe them", "Not that I know of", "Not sure". If the user identifies pain points, follow up for details before proceeding.
+   Use `AskUserQuestion` to validate. Header: "Summary". Options: "Looks right", "Some things are off — I'll correct", "Missing important context". If the user corrects or adds context, incorporate it before proceeding.
+
+4. **Discover what you still need.** You know the Balanced Coupling model. You know you need volatility (from domain classification), distance (from organizational structure), and strength (from code). Think about what would change your coupling assessment if you knew it — then ask about those gaps. One question at a time via `AskUserQuestion`. Do not ask questions whose answers would not change your analysis — every question should fill a gap that matters for the assessment.
+
+   Common information gaps to consider (skip any you can already answer from code, requirements, or the user's corrections above):
+   - **Domain classification gaps** — areas where you can't tell if something is core (competitive advantage, high volatility) vs supporting vs generic. Propose your best guess and ask the user to confirm or correct.
+   - **Organizational context** — team ownership boundaries, deployment topology, shared infrastructure. These affect effective distance beyond what code structure shows.
+   - **Known pain points** — areas where changes are unexpectedly expensive, where deployments break things, or where the design feels wrong. These focus the analysis where it matters most.
+   - **Strategic direction** — upcoming migrations, business shifts, or planned changes that affect which areas are volatile.
+   - **Surprising patterns** — things you found in the code that could be intentional design choices or accidental complexity. Ask before assuming.
+
+   You are not limited to these categories. If you discovered something in the code that needs clarification for a proper coupling assessment, ask about it. Ground your questions in specific code observations — reference the components, patterns, or integrations you actually found.
 
 ### Step 2: Map Integrations
 
PATCH

echo "Gold patch applied."
