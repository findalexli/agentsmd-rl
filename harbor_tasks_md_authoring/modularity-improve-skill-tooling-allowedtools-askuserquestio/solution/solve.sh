#!/usr/bin/env bash
set -euo pipefail

cd /workspace/modularity

# Idempotency guard
if grep -qF "| A -> B      | ...                                                             " "skills/document/SKILL.md" && grep -qF "| Header  | Question                                                         | O" "skills/high-level-design/SKILL.md" && grep -qF "**Domain classification**: Header: \"Domain\". First, ask the user (free text) whi" "skills/review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/document/SKILL.md b/skills/document/SKILL.md
@@ -4,7 +4,7 @@ description: >
   Produces modularity review documents in both Markdown and HTML formats.
   Use when writing the final review output from a modularity analysis.
 user-invocable: false
-allowed-tools: Read
+allowed-tools: Read, Write
 ---
 
 # Document
@@ -25,6 +25,7 @@ You produce the final modularity review document in two formats: Markdown (`.md`
 ### Executive Summary
 
 A short paragraph (3-5 sentences) covering:
+
 - What the project does (its core functionality)
 - The overall modularity status (healthy, needs attention, critical issues)
 - The most important finding from the review
@@ -35,8 +36,8 @@ Summarize all key integrations. The table headers MUST link to coupling.dev:
 
 ```markdown
 | Integration | [Strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) | [Distance](https://coupling.dev/posts/dimensions-of-coupling/distance/) | [Volatility](https://coupling.dev/posts/dimensions-of-coupling/volatility/) | [Balanced?](https://coupling.dev/posts/core-concepts/balance/) |
-|---|---|---|---|---|
-| A -> B | ... | ... | ... | ... |
+| ----------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
+| A -> B      | ...                                                                                 | ...                                                                     | ...                                                                         | ...                                                            |
 ```
 
 ### Issues
@@ -50,16 +51,21 @@ For each identified imbalance, write a section:
 **Severity**: [Critical / Significant / Minor]
 
 ### Knowledge Leakage
+
 What knowledge is shared that shouldn't be, or is shared implicitly when it should be explicit. Identify the specific implementation details, business rules, or domain model concepts that leak across the boundary.
 
 ### Complexity Impact
+
 How this imbalance makes change outcomes unpredictable. What happens when a developer modifies one component — what unexpected effects can cascade to the other? How does this exceed cognitive capacity (the 4+/-1 units of working memory)?
 
 ### Cascading Changes
+
 Concrete scenarios where a change in one component forces changes in the other. What kinds of business or technical changes trigger cascading modifications? How expensive are those cascading changes given the current distance between the components?
 
 ### Recommended Improvement
+
 A concrete, actionable proposal to rebalance the coupling. Ground the recommendation in the model:
+
 - To reduce **strength**: introduce integration contracts, anti-corruption layers, facades, published languages
 - To reduce **distance**: co-locate components into the same module/service/bounded context
 - To accept **unbalanced coupling**: demonstrate that volatility is low enough to make the imbalance tolerable
@@ -74,7 +80,7 @@ At the bottom of every review document, include this exact text verbatim — do
 ```markdown
 ---
 
-*This analysis was performed using the [Balanced Coupling](https://coupling.dev) model by [Vlad Khononov](https://vladikk.com).*
+_This analysis was performed using the [Balanced Coupling](https://coupling.dev) model by [Vlad Khononov](https://vladikk.com)._
 ```
 
 ### Severity Criteria
@@ -87,32 +93,33 @@ At the bottom of every review document, include this exact text verbatim — do
 
 **You MUST add hyperlinks to coupling.dev** whenever the document mentions balanced coupling concepts. This applies to BOTH the Markdown and HTML outputs. Do not think about which link to use — use this lookup table:
 
-| Concept mentioned | Link to |
-|---|---|
-| Balanced coupling, the balance rule, the balance formula, `STRENGTH XOR DISTANCE`, modularity vs complexity | https://coupling.dev/posts/core-concepts/balance/ |
-| Integration strength, shared knowledge, levels of coupling strength | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
-| Intrusive coupling, private interfaces, implementation detail leakage | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
-| Functional coupling, duplicated business logic, shared functional requirements | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
-| Model coupling, shared domain model, shared business model | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
-| Contract coupling, integration contracts, facades, DTOs, published language | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
-| Distance, cost of change, physical/logical separation | https://coupling.dev/posts/dimensions-of-coupling/distance/ |
-| Lifecycle coupling, deployment coupling, co-deployment | https://coupling.dev/posts/dimensions-of-coupling/distance/ |
-| Socio-technical distance, team boundaries, organizational structure | https://coupling.dev/posts/dimensions-of-coupling/distance/ |
-| Runtime coupling, synchronous/asynchronous integration | https://coupling.dev/posts/dimensions-of-coupling/distance/ |
-| Volatility, probability of change, rate of change | https://coupling.dev/posts/dimensions-of-coupling/volatility/ |
-| Core subdomain, competitive advantage, high volatility domain | https://coupling.dev/posts/dimensions-of-coupling/volatility/ |
-| Supporting subdomain, generic subdomain, subdomain classification | https://coupling.dev/posts/dimensions-of-coupling/volatility/ |
-| Essential vs accidental volatility | https://coupling.dev/posts/dimensions-of-coupling/volatility/ |
-| Complexity, Cynefin, unpredictable outcomes | https://coupling.dev/posts/core-concepts/complexity/ |
-| Modularity, modular design, clear change outcomes | https://coupling.dev/posts/core-concepts/modularity/ |
-| Coupling (general concept), why coupling matters | https://coupling.dev/posts/core-concepts/coupling/ |
-| Tight coupling, distributed monolith | https://coupling.dev/posts/core-concepts/balance/ |
-| Loose coupling, high cohesion, low cohesion | https://coupling.dev/posts/core-concepts/balance/ |
-| Connascence, degrees of coupling | https://coupling.dev/posts/related-topics/connascence/ |
-| Module coupling, classic coupling model | https://coupling.dev/posts/related-topics/module-coupling/ |
-| Domain-driven design, DDD, bounded contexts, aggregates | https://coupling.dev/posts/related-topics/domain-driven-design/ |
+| Concept mentioned                                                                                           | Link to                                                                 |
+| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
+| Balanced coupling, the balance rule, the balance formula, `STRENGTH XOR DISTANCE`, modularity vs complexity | https://coupling.dev/posts/core-concepts/balance/                       |
+| Integration strength, shared knowledge, levels of coupling strength                                         | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
+| Intrusive coupling, private interfaces, implementation detail leakage                                       | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
+| Functional coupling, duplicated business logic, shared functional requirements                              | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
+| Model coupling, shared domain model, shared business model                                                  | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
+| Contract coupling, integration contracts, facades, DTOs, published language                                 | https://coupling.dev/posts/dimensions-of-coupling/integration-strength/ |
+| Distance, cost of change, physical/logical separation                                                       | https://coupling.dev/posts/dimensions-of-coupling/distance/             |
+| Lifecycle coupling, deployment coupling, co-deployment                                                      | https://coupling.dev/posts/dimensions-of-coupling/distance/             |
+| Socio-technical distance, team boundaries, organizational structure                                         | https://coupling.dev/posts/dimensions-of-coupling/distance/             |
+| Runtime coupling, synchronous/asynchronous integration                                                      | https://coupling.dev/posts/dimensions-of-coupling/distance/             |
+| Volatility, probability of change, rate of change                                                           | https://coupling.dev/posts/dimensions-of-coupling/volatility/           |
+| Core subdomain, competitive advantage, high volatility domain                                               | https://coupling.dev/posts/dimensions-of-coupling/volatility/           |
+| Supporting subdomain, generic subdomain, subdomain classification                                           | https://coupling.dev/posts/dimensions-of-coupling/volatility/           |
+| Essential vs accidental volatility                                                                          | https://coupling.dev/posts/dimensions-of-coupling/volatility/           |
+| Complexity, Cynefin, unpredictable outcomes                                                                 | https://coupling.dev/posts/core-concepts/complexity/                    |
+| Modularity, modular design, clear change outcomes                                                           | https://coupling.dev/posts/core-concepts/modularity/                    |
+| Coupling (general concept), why coupling matters                                                            | https://coupling.dev/posts/core-concepts/coupling/                      |
+| Tight coupling, distributed monolith                                                                        | https://coupling.dev/posts/core-concepts/balance/                       |
+| Loose coupling, high cohesion, low cohesion                                                                 | https://coupling.dev/posts/core-concepts/balance/                       |
+| Connascence, degrees of coupling                                                                            | https://coupling.dev/posts/related-topics/connascence/                  |
+| Module coupling, classic coupling model                                                                     | https://coupling.dev/posts/related-topics/module-coupling/              |
+| Domain-driven design, DDD, bounded contexts, aggregates                                                     | https://coupling.dev/posts/related-topics/domain-driven-design/         |
 
 **Rules:**
+
 - Every coupling concept in the document MUST be linked at least once. If in doubt, link it.
 - In the coupling overview table: the headers are always linked (see template above). Strength values in the table cells (Contract, Model, Functional, Intrusive) MUST also be linked.
 - In issue sections: link the first occurrence of each concept.
@@ -129,6 +136,7 @@ Write both files to `docs/reviews/`:
 ### HTML generation
 
 **You MUST read the template file before generating HTML.** The template is at `${CLAUDE_SKILL_DIR}/assets/template.html`. Read this file, then replace:
+
 - `{{TITLE}}` with the review title (e.g. "Modularity Review")
 - `{{CONTENT}}` with the review body as HTML
 
diff --git a/skills/high-level-design/SKILL.md b/skills/high-level-design/SKILL.md
@@ -7,6 +7,7 @@ description: >
 argument-hint: "[path/to/functional-requirements.md]"
 skills:
   - balanced-coupling
+allowed-tools: Read, Write, Edit, AskUserQuestion, TaskCreate, TaskUpdate
 ---
 
 # High-Level Design
@@ -16,8 +17,10 @@ You design modular high-level architectures from functional requirements and pro
 ## Input
 
 If `$ARGUMENTS` contains a file path, read that file as the functional requirements input.
-If `$ARGUMENTS` is empty or not a valid file path, ask the user: "Please provide the path to the functional requirements file."
-Do not proceed until you have the functional requirements.
+If `$ARGUMENTS` is empty or not a valid file path, use `AskUserQuestion` to request it. Header: "Requirements". Question: "Please provide the path to the functional requirements file."
+Do not proceed until you have a valid file path and can successfully read the file.
+
+Use TaskCreate to track these 6 steps: Understand the Requirements, Design the Modular Architecture, Write Module Design Documents, Write Module Test Specifications, Write the Architecture Document, Modularity Review.
 
 ## Interaction Rules
 
@@ -41,23 +44,23 @@ Read the functional requirements file. Then:
 3. **Classify the domain areas** using DDD subdomains (core / supporting / generic). This determines volatility and where to invest design effort. Analyze the requirements and propose classifications yourself. Present them as a table:
 
 | Subdomain | Classification | Rationale |
-|-----------|---------------|-----------|
-| {area 1} | Core | {why} |
-| {area 2} | Supporting | {why} |
-| {area 3} | Generic | {why} |
+| --------- | -------------- | --------- |
+| {area 1}  | Core           | {why}     |
+| {area 2}  | Supporting     | {why}     |
+| {area 3}  | Generic        | {why}     |
 
 Then ask the user to validate using `AskUserQuestion`:
 
-| Header | Question | Options |
-|--------|----------|---------|
+| Header     | Question                                       | Options                                                                                                                                    |
+| ---------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
 | Subdomains | Do these subdomain classifications look right? | 1. **Approved** - All correct 2. **Some are wrong** - I'll tell you which to change 3. **Missing subdomains** - There are areas not listed |
 
 If the user says some are wrong, ask which ones and what the correct classification should be.
 
 Present your full understanding to the user for validation using `AskUserQuestion`:
 
-| Header | Question | Options |
-|--------|----------|---------|
+| Header   | Question                                                  | Options                                                                                                                                                   |
+| -------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
 | Approval | Does this understanding of the requirements look correct? | 1. **Approved** - Proceed to architecture design 2. **Needs changes** - I'll explain what's wrong 3. **Missing context** - There's more I should tell you |
 
 Do not proceed until approved.
@@ -79,14 +82,14 @@ Using the Balanced Coupling model:
 
 Present the coupling assessment table to the user:
 
-| Integration | Strength | Distance | Volatility | Balanced? | Action |
-|---|---|---|---|---|---|
-| A -> B | Model | High (separate services) | High (core) | No — tight coupling | Reduce strength: introduce contract via API |
+| Integration | Strength | Distance                 | Volatility  | Balanced?           | Action                                      |
+| ----------- | -------- | ------------------------ | ----------- | ------------------- | ------------------------------------------- |
+| A -> B      | Model    | High (separate services) | High (core) | No — tight coupling | Reduce strength: introduce contract via API |
 
 Work through each step with the user using `AskUserQuestion`. Each step requires user approval. Do not proceed to writing design documents until the modular architecture is fully validated by the user.
 
-| Header | Question | Options |
-|--------|----------|---------|
+| Header   | Question                                     | Options                                                                                                                                                  |
+| -------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
 | Approval | Does this modular architecture look correct? | 1. **Approved** - Proceed to design documents 2. **Needs changes** - I'll explain what to adjust 3. **Rethink** - Let's reconsider the module boundaries |
 
 ### Step 3: Write Module Design Documents
@@ -97,31 +100,37 @@ Using the validated architecture from Step 2, for each module create `docs/desig
 # {Module Name}
 
 ## Functional Responsibilities
+
 What this module does — the functionality it implements and the business capabilities it provides.
 
 ## Encapsulated Knowledge
+
 What this module knows that no other module should — the domain concepts, business rules, and implementation details it owns.
 
 ## Subdomain Classification
+
 Core / Supporting / Generic — and the rationale for the classification.
 
 ## Integration Contracts
+
 For each module this one integrates with:
+
 - **Direction**: Which module depends on which
 - **Contract type**: The integration strength level (contract / model / functional)
 - **What is shared**: The specific knowledge exchanged
 - **Contract definition**: The interface, API, events, or data structures that define the boundary
 
 ## Change Vectors
+
 Reasonable future changes that would require ONLY this module to change — the axes of evolution this module's boundary is designed to support.
 ```
 
 Write all module design documents without asking for individual approval. The modular architecture was already approved in Step 2 — the documents are a direct translation of that approved design.
 
 After writing all module documents, present the complete set to the user for review using `AskUserQuestion`:
 
-| Header | Question | Options |
-|--------|----------|---------|
+| Header  | Question                                                         | Options                                                                                                                                                                            |
+| ------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
 | Modules | All module design documents have been written. How do they look? | 1. **Approved** - Proceed to test specifications 2. **Needs changes** - I'll explain which modules need work 3. **Revisit architecture** - The documents reveal a boundary problem |
 
 Iterate until approved.
@@ -134,19 +143,24 @@ For each module, create `docs/design/{module-name}/tests.md` containing:
 # {Module Name} — Test Specification
 
 ## Unit Tests
+
 Tests for the module's internal logic in isolation. Covers business rules, calculations, state transitions, and edge cases.
 
 ## Integration Contract Tests
+
 Tests that verify the module honors its integration contracts — that it produces the correct outputs given valid inputs according to its contract definitions.
 
 ## Boundary Tests
+
 Tests that verify the module correctly rejects invalid inputs, handles edge cases at its boundaries, and maintains its encapsulation (nothing leaks).
 
 ## Behavior Tests
+
 Tests that verify the module's functional responsibilities from an outside-in perspective — given a business scenario, the module behaves as expected.
 ```
 
 Each test section should contain specific, named test cases with:
+
 - **Test name**: A descriptive name
 - **Scenario**: What is being tested
 - **Expected behavior**: What the correct outcome is
@@ -161,24 +175,31 @@ Create `docs/design/architecture.md` containing:
 # Architecture Overview
 
 ## Functional Requirements Summary
+
 Brief summary of the requirements this architecture addresses.
 
 ## Module Map
+
 List of all modules with one-line descriptions.
 
 ## How the Modules Work Together
+
 For each key functional flow / use case:
+
 - Which modules participate
 - How data/control flows between them
 - What contracts govern the interactions
 
 ## Coupling Assessment
+
 The coupling assessment table from the modular architecture analysis, with commentary on the key design decisions and their rationale grounded in the Balanced Coupling model.
 
 ## Design Decisions and Trade-offs
+
 Key architectural decisions, what was considered, what was chosen, and why — grounded in the coupling dimensions and balance rule.
 
 ## Unresolved Risks
+
 Anything the design intentionally leaves open, along with the conditions under which it should be revisited.
 ```
 
@@ -194,11 +215,13 @@ After all documents are written, review your own design for modularity imbalance
 4. **Flag imbalances**: Focus on integrations that are both unbalanced and volatile.
 
 For each issue found, classify its severity:
+
 - **Critical**: High strength + high distance + high volatility.
 - **Significant**: Unbalanced coupling in a moderately volatile area, or implicit coupling that hides integration points.
 - **Minor**: Unbalanced coupling in a low-volatility area, or low cohesion that increases cognitive load but doesn't cause cascading changes.
 
 If there are any Critical or Significant issues:
+
 1. Present the issues to the user with the same structure used in step 2's coupling assessment table, plus a description of the knowledge leakage and recommended improvement for each.
 2. Propose concrete changes to the design to rebalance the coupling.
 3. Once the user approves the changes, update the affected design documents (module designs, test specs, and architecture document).
diff --git a/skills/review/SKILL.md b/skills/review/SKILL.md
@@ -8,23 +8,38 @@ description: >
 skills:
   - balanced-coupling
   - document
+allowed-tools: Read, Grep, Glob, LSP, AskUserQuestion, TaskCreate, TaskUpdate
 ---
 
 # Modularity Review
 
 You analyze codebases for modularity imbalances using the Balanced Coupling model by Vlad Khononov (preloaded from the balanced-coupling skill). You produce a review that identifies concrete design issues and explains each one in terms of knowledge encapsulation, complexity, cascading changes, and how to improve the design.
 
+Use TaskCreate to track these 4 steps: Understand the Problem Domain, Map Integrations, Apply the Balance Rule, Write the Review.
+
+## Interaction Rules
+
+Always use `AskUserQuestion` for user input. Follow these principles:
+
+- **One question at a time.** Never batch multiple questions into one message.
+- **Multiple choice preferred.** Provide 2-4 concrete options. Easier to answer than open-ended.
+- **"Other" is automatic.** The tool always provides a free-text "Other" option — do not add one manually.
+- **Use headers.** Short labels (max 12 chars) like "Scope", "Domain", "Teams", "Pain points".
+
 ## Process
 
 ### Step 1: Understand the Problem Domain
 
 1. Read all functional requirements documents available in the `docs/` folder. Understand the problem domain, business capabilities, and the system's intended behavior before looking at any code.
-2. Ask the user which parts of the codebase to analyze. If no specific scope is given, explore the project structure to identify the major modules, services, and their boundaries.
+2. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I'll tell you which path", "Specific components — I'll name them". If the user picks a specific scope, follow up to collect details. Otherwise, explore the project structure to identify the major modules, services, and their boundaries.
 3. Read the code. Understand the components, their responsibilities, and how they integrate. Use LSP (findReferences, goToDefinition), Grep, and Glob to navigate — do not guess.
-4. Ask the user about anything you cannot determine from the code or requirements documents alone:
-   - **Domain classification**: Which areas are core, supporting, or generic subdomains?
-   - **Team structure**: Are components owned by the same team or different teams? (This affects distance.)
-   - **Known pain points**: Where do changes tend to be difficult or surprising?
+4. Use `AskUserQuestion` to ask about anything you cannot determine from the code or requirements alone. Ask each question separately — one at a time.
+
+   **Domain classification**: Header: "Domain". First, ask the user (free text) which business areas/components are core (competitive advantage, high volatility), supporting, or generic subdomains. Do not list all discovered components as options. If they mention many areas, either group them and ask follow-up `AskUserQuestion` prompts that classify 2–4 areas at a time, or focus on the top 2–4 most important areas they highlight.
+
+   **Team structure**: Header: "Teams". Options: "Same team — Single team owns everything", "Multiple teams — Different teams own different parts", "Mixed / not sure".
+
+   **Known pain points**: Header: "Pain points". Options: "Yes — I'll describe them", "Not that I know of", "Not sure". If the user identifies pain points, follow up for details before proceeding.
 
 ### Step 2: Map Integrations
 
PATCH

echo "Gold patch applied."
