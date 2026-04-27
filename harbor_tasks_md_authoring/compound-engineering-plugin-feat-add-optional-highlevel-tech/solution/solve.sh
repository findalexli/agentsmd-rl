#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "2. **Decisions, not code** - Capture approach, boundaries, files, dependencies, " "plugins/compound-engineering/skills/ce-plan-beta/SKILL.md" && grep -qF "- Add implementation code \u2014 no imports, exact method signatures, or framework-sp" "plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan-beta/SKILL.md b/plugins/compound-engineering/skills/ce-plan-beta/SKILL.md
@@ -30,7 +30,7 @@ Do not proceed until you have a clear planning input.
 ## Core Principles
 
 1. **Use requirements as the source of truth** - If `ce:brainstorm` produced a requirements document, planning should build from it rather than re-inventing behavior.
-2. **Decisions, not code** - Capture approach, boundaries, files, dependencies, risks, and test scenarios. Do not pre-write implementation code or shell command choreography.
+2. **Decisions, not code** - Capture approach, boundaries, files, dependencies, risks, and test scenarios. Do not pre-write implementation code or shell command choreography. Pseudo-code sketches or DSL grammars that communicate high-level technical design are welcome when they help a reviewer validate direction — but they must be explicitly framed as directional guidance, not implementation specification.
 3. **Research before structuring** - Explore the codebase, institutional learnings, and external guidance when warranted before finalizing the plan.
 4. **Right-size the artifact** - Small work gets a compact plan. Large work gets more structure. The philosophy stays the same at every depth.
 5. **Separate planning from execution discovery** - Resolve planning-time questions here. Explicitly defer execution-time unknowns to implementation.
@@ -267,7 +267,33 @@ Avoid:
 - Units that span multiple unrelated concerns
 - Units that are so vague an implementer still has to invent the plan
 
-#### 3.4 Define Each Implementation Unit
+#### 3.4 High-Level Technical Design (Optional)
+
+Before detailing implementation units, decide whether an overview would help a reviewer validate the intended approach. This section communicates the *shape* of the solution — how pieces fit together — without dictating implementation.
+
+**When to include it:**
+
+| Work involves... | Best overview form |
+|---|---|
+| DSL or API surface design | Pseudo-code grammar or contract sketch |
+| Multi-component integration | Mermaid sequence or component diagram |
+| Data pipeline or transformation | Data flow sketch |
+| State-heavy lifecycle | State diagram |
+| Complex branching logic | Flowchart |
+| Single-component with non-obvious shape | Pseudo-code sketch |
+
+**When to skip it:**
+- Well-patterned work where prose and file paths tell the whole story
+- Straightforward CRUD or convention-following changes
+- Lightweight plans where the approach is obvious
+
+Choose the medium that fits the work. Do not default to pseudo-code when a diagram communicates better, and vice versa.
+
+Frame every sketch with: *"This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce."*
+
+Keep sketches concise — enough to validate direction, not enough to copy-paste into production.
+
+#### 3.5 Define Each Implementation Unit
 
 For each unit, include:
 - **Goal** - what this unit accomplishes
@@ -276,6 +302,7 @@ For each unit, include:
 - **Files** - exact file paths to create, modify, or test
 - **Approach** - key decisions, data flow, component boundaries, or integration notes
 - **Execution note** - optional, only when the unit benefits from a non-default execution posture such as test-first or characterization-first work
+- **Technical design** - optional pseudo-code or diagram when the unit's approach is non-obvious and prose alone would leave it ambiguous. Frame explicitly as directional guidance, not implementation specification
 - **Patterns to follow** - existing code or conventions to mirror
 - **Test scenarios** - specific behaviors, edge cases, and failure paths to cover
 - **Verification** - how an implementer should know the unit is complete, expressed as outcomes rather than shell command scripts
@@ -289,7 +316,7 @@ Use `Execution note` sparingly. Good uses include:
 
 Do not expand units into literal `RED/GREEN/REFACTOR` substeps.
 
-#### 3.5 Keep Planning-Time and Implementation-Time Unknowns Separate
+#### 3.6 Keep Planning-Time and Implementation-Time Unknowns Separate
 
 If something is important but not knowable yet, record it explicitly under deferred implementation notes rather than pretending to resolve it in the plan.
 
@@ -311,12 +338,12 @@ Use one planning philosophy across all depths. Change the amount of detail, not
 - Omit optional sections that add little value
 
 **Standard**
-- Use the full core template
+- Use the full core template, omitting optional sections (including High-Level Technical Design) that add no value for this particular work
 - Usually 3-6 implementation units
 - Include risks, deferred questions, and system-wide impact when relevant
 
 **Deep**
-- Use the full core template plus optional analysis sections
+- Use the full core template plus optional analysis sections where warranted
 - Usually 4-8 implementation units
 - Group units into phases when that improves clarity
 - Include alternatives considered, documentation impacts, and deeper risk treatment when warranted
@@ -396,6 +423,16 @@ deepened: YYYY-MM-DD  # optional, set later by deepen-plan-beta when the plan is
 
 - [Question or unknown]: [Why it is intentionally deferred]
 
+<!-- Optional: Include this section only when the work involves DSL design, multi-component
+     integration, complex data flow, state-heavy lifecycle, or other cases where prose alone
+     would leave the approach shape ambiguous. Omit it entirely for well-patterned or
+     straightforward work. -->
+## High-Level Technical Design
+
+> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*
+
+[Pseudo-code grammar, mermaid diagram, data flow sketch, or state diagram — choose the medium that best communicates the solution shape for this work.]
+
 ## Implementation Units
 
 - [ ] **Unit 1: [Name]**
@@ -416,6 +453,8 @@ deepened: YYYY-MM-DD  # optional, set later by deepen-plan-beta when the plan is
 
 **Execution note:** [Optional test-first, characterization-first, or other execution posture signal]
 
+**Technical design:** *(optional -- pseudo-code or diagram when the unit's approach is non-obvious. Directional guidance, not implementation specification.)*
+
 **Patterns to follow:**
 - [Existing file, class, or pattern]
 
@@ -490,11 +529,12 @@ For larger `Deep` plans, extend the core template only when useful with sections
 
 - Prefer path plus class/component/pattern references over brittle line numbers
 - Keep implementation units checkable with `- [ ]` syntax for progress tracking
-- Do not include fenced implementation code blocks unless the plan itself is about code shape as a design artifact
+- Do not include implementation code — no imports, exact method signatures, or framework-specific syntax
+- Pseudo-code sketches and DSL grammars are allowed in the High-Level Technical Design section and per-unit technical design fields when they communicate design direction. Frame them explicitly as directional guidance, not implementation specification
+- Mermaid diagrams are encouraged when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, state diagrams for lifecycle transitions, flowcharts for complex branching logic
 - Do not include git commands, commit messages, or exact test command recipes
 - Do not expand implementation units into micro-step `RED/GREEN/REFACTOR` instructions
 - Do not pretend an execution-time question is settled just to make the plan look complete
-- Include mermaid diagrams when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, state diagrams for lifecycle transitions, flowcharts for complex branching logic
 
 ### Phase 5: Final Review, Write File, and Handoff
 
@@ -508,6 +548,8 @@ Before finalizing, check:
 - If test-first or characterization-first posture was explicit or strongly implied, the relevant units carry it forward with a lightweight `Execution note`
 - Test scenarios are specific without becoming test code
 - Deferred items are explicit and not hidden as fake certainty
+- If a High-Level Technical Design section is included, it uses the right medium for the work, carries the non-prescriptive framing, and does not contain implementation code (no imports, exact signatures, or framework-specific syntax)
+- Per-unit technical design fields, if present, are concise and directional rather than copy-paste-ready
 
 If the plan originated from a requirements document, re-read that document and verify:
 - The chosen approach still matches the product intent
diff --git a/plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md b/plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md
@@ -96,7 +96,8 @@ Map the plan into the current template. Look for these sections, or their neares
 - `Context & Research`
 - `Key Technical Decisions`
 - `Open Questions`
-- `Implementation Units`
+- `High-Level Technical Design` (optional overview — pseudo-code, DSL grammar, mermaid diagram, or data flow)
+- `Implementation Units` (may include per-unit `Technical design` subsections)
 - `System-Wide Impact`
 - `Risks & Dependencies`
 - `Documentation / Operational Notes`
@@ -166,6 +167,17 @@ Use these triggers.
 - Resolved questions have no clear basis in repo context, research, or origin decisions
 - Deferred items are too vague to be useful later
 
+**High-Level Technical Design (when present)**
+- The sketch uses the wrong medium for the work (e.g., pseudo-code where a sequence diagram would communicate better)
+- The sketch contains implementation code (imports, exact signatures, framework-specific syntax) rather than pseudo-code
+- The non-prescriptive framing is missing or weak
+- The sketch does not connect to the key technical decisions or implementation units
+
+**High-Level Technical Design (when absent)** *(Standard or Deep plans only)*
+- The work involves DSL design, API surface design, multi-component integration, complex data flow, or state-heavy lifecycle
+- Key technical decisions would be easier to validate with a visual or pseudo-code representation
+- The approach section of implementation units is thin and a higher-level technical design would provide context
+
 **Implementation Units**
 - Dependency order is unclear or likely wrong
 - File paths or test file paths are missing where they should be explicit
@@ -209,6 +221,11 @@ Use fully-qualified agent names inside Task calls.
 - `compound-engineering:review:architecture-strategist` for design integrity, boundaries, and architectural tradeoffs
 - Add `compound-engineering:research:framework-docs-researcher` or `compound-engineering:research:best-practices-researcher` when the decision needs external grounding beyond repo evidence
 
+**High-Level Technical Design**
+- `compound-engineering:review:architecture-strategist` for validating that the technical design accurately represents the intended approach and identifying gaps
+- `compound-engineering:research:repo-research-analyst` for grounding the technical design in existing repo patterns and conventions
+- Add `compound-engineering:research:best-practices-researcher` when the technical design involves a DSL, API surface, or pattern that benefits from external validation
+
 **Implementation Units / Verification**
 - `compound-engineering:research:repo-research-analyst` for concrete file targets, patterns to follow, and repo-specific sequencing clues
 - `compound-engineering:review:pattern-recognition-specialist` for consistency, duplication risks, and alignment with existing patterns
@@ -268,11 +285,13 @@ Allowed changes:
 - Add missing pattern references, file/test paths, or verification outcomes
 - Expand system-wide impact, risks, or rollout treatment where justified
 - Reclassify open questions between `Resolved During Planning` and `Deferred to Implementation` when evidence supports the change
+- Strengthen, replace, or add a High-Level Technical Design section when the work warrants it and the current representation is weak, uses the wrong medium, or is absent where it would help. Preserve the non-prescriptive framing
+- Strengthen or add per-unit technical design fields where the unit's approach is non-obvious and the current approach notes are thin
 - Add an optional deep-plan section only when it materially improves execution quality
 - Add or update `deepened: YYYY-MM-DD` in frontmatter when the plan was substantively improved
 
 Do **not**:
-- Add fenced implementation code blocks unless the plan itself is about code shape as a design artifact
+- Add implementation code — no imports, exact method signatures, or framework-specific syntax. Pseudo-code sketches and DSL grammars are allowed in both the top-level High-Level Technical Design section and per-unit technical design fields
 - Add git commands, commit choreography, or exact test command recipes
 - Add generic `Research Insights` subsections everywhere
 - Rewrite the entire plan from scratch
PATCH

echo "Gold patch applied."
