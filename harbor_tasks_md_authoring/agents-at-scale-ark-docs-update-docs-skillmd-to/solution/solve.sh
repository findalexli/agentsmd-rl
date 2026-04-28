#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents-at-scale-ark

# Idempotency guard
if grep -qF "- Avoid gerunds: \"Get started\" not \"Getting started,\" \"Customize a layout\" not \"" ".claude/skills/documentation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/documentation/SKILL.md b/.claude/skills/documentation/SKILL.md
@@ -14,7 +14,7 @@ Guidance for structuring Ark documentation using Diataxis adapted for Ark's need
 - Reviewing documentation PRs
 - Restructuring existing documentation
 
-## Ark's Diataxis Structure
+## ARK's Diataxis structure
 
 ```
 docs/content/
@@ -34,9 +34,9 @@ docs/content/
 |----------|----------|-----|
 | Explanation | **Core Concepts** | More accessible |
 
-## The Four Quadrants
+## The four quadrants
 
-### 1. Tutorials (Learning-Oriented)
+### 1. Tutorials (learning-oriented)
 
 **Purpose**: Hands-on lessons for newcomers.
 
@@ -59,19 +59,19 @@ docs/content/
 
 ---
 
-### 2. How-to Guides (Task-Oriented)
+### 2. How-to guides (task-oriented)
 
 **Purpose**: Help competent users complete specific tasks.
 
 **Organized by persona**:
 
-#### Build with Ark (Application Developers)
-- Configure models, create agents, coordinate teams, run queries, add tools
+#### Build with ARK (application developers)
+- Configure models, create agents, coordinate teams, run queries, add tools.
 
-#### Extend Ark (Contributors)
-- Build services locally, implement APIs, build A2A servers, add testing
+#### Extend ARK (contributors)
+- Build services locally, implement APIs, build A2A servers, add tests.
 
-#### Operate Ark (Operators / SRE / Security)
+#### Operate ARK (operators / SRE / security)
 - **Platform operations**: Provisioning, deploying
 - **CI/CD and supply chain**: Build pipelines
 - **Security & assurance**: Pen testing, code analysis
@@ -87,16 +87,16 @@ docs/content/
 
 ---
 
-### 3. Core Concepts (Understanding-Oriented)
+### 3. Core concepts (understanding-oriented)
 
-**Purpose**: Explain what Ark is, how it's designed, and why.
+**Purpose**: Explain what ARK is, how it's designed, and why.
 
 **Topics**:
-- What Ark is and how it works
-- Designing effective agentic systems
-- Platform architecture concepts
-- Extensibility concepts
-- Security and identity concepts
+- What ARK is and how it works.
+- Design effective agentic systems.
+- Platform architecture concepts.
+- Extensibility concepts.
+- Security and identity concepts.
 
 **Writing style**:
 - Discursive: "The reason for X is..."
@@ -110,17 +110,17 @@ docs/content/
 
 ---
 
-### 4. Reference (Information-Oriented)
+### 4. Reference (information-oriented)
 
 **Purpose**: Factual lookup material.
 
 **Organized by type**:
-- **Interfaces**: Ark APIs
-- **Kubernetes API**: CRDs, Resources
-- **Evaluations**: Guides, event-based evaluations
-- **System behaviour**: Query execution, relationships
-- **Operations**: Upgrading, troubleshooting
-- **Project**: Contributors
+- **Interfaces**: ARK APIs.
+- **Kubernetes API**: CRDs, resources.
+- **Evaluations**: Guides, event-based evaluations.
+- **System behavior**: Query execution, relationships.
+- **Operations**: Upgrading, troubleshooting.
+- **Project**: Contributors.
 
 **Writing style**:
 - Austere, factual, neutral
@@ -134,7 +134,7 @@ docs/content/
 
 ---
 
-## Decision Guide
+## Decision guide
 
 ```
 Is the reader LEARNING or WORKING?
@@ -148,19 +148,19 @@ Is the reader LEARNING or WORKING?
     └─ Looking up facts? → REFERENCE
 ```
 
-## Hub Pages
+## Hub pages
 
 Hub pages link to content without moving files:
 
-- `tutorials.mdx` - Lists tutorials in order
-- `how-to-guides.mdx` - Groups by persona
-- `core-concepts.mdx` - Groups by topic
-- `reference/index.mdx` - Groups by type
+- `tutorials.mdx` - Lists tutorials in order.
+- `how-to-guides.mdx` - Groups by persona.
+- `core-concepts.mdx` - Groups by topic.
+- `reference/index.mdx` - Groups by type.
 
 Hub pages should:
-- Explain purpose in one sentence
-- Group links logically
-- Not duplicate content
+- Explain purpose in one sentence.
+- Group links logically.
+- Not duplicate content.
 
 ## Personas
 
@@ -171,14 +171,18 @@ Hub pages should:
 | Platform engineers | How-to (Operate), Reference |
 | Contributors | How-to (Extend), Core Concepts |
 
-## Writing Guidelines
+## Writing guidelines
 
-### General Style
+### Lexicon
+- The product is known as ARK rather than Ark.
+
+
+### General style
 - Be concise and direct.
 - Use simple language.
 - Keep descriptions to 1-2 sentences.
 - Use active voice: "Creates agent" not "Agent is created".
-- Write "Ark" not "ARK".
+- Write "ARK" not "Ark".
 - Use US English.
 - Use Oxford commas in lists.
 
@@ -192,31 +196,31 @@ Hub pages should:
 - Don't capitalize: cloud, internet, machine learning, advanced analytics.
 
 ### Headings
-- Avoid gerunds: "Get started" not "Getting started", "Customize a layout" not "Customizing a layout".
+- Avoid gerunds: "Get started" not "Getting started," "Customize a layout" not "Customizing a layout".
 - Keep titles short and descriptive for search discoverability.
 
 ### Instructions
-- Use imperatives: "Complete the configuration steps."
+- Use imperatives: "Complete the configuration steps".
 - Don't use "please".
-- Don't use passive tense: "Complete the steps" not "The steps should be completed."
+- Don't use passive tense: "Complete the steps" not "The steps should be completed".
 
 ### Links
-- Make hyperlinks descriptive: `Learn how to [contribute to Ark](url).`
-- Don't write: `To contribute, see [here](url).`
+- Make hyperlinks descriptive: `Learn how to [contribute to ARK](url)`.
+- Don't write: `To contribute, see [here](url)`.
 
 ### Avoid
 - Gerunds in headings.
 - Colloquialisms (may not translate across regions/languages).
 - Business speak: "leverage", "utilize", "facilitate".
 
-### What NOT to Mix
+### What not to mix
 
 | Don't put in... | This content... |
 |-----------------|-----------------|
-| Tutorials | Explanations, choices |
-| How-to Guides | Teaching, complete reference |
-| Core Concepts | Instructions, reference |
-| Reference | Instructions, explanations |
+| Tutorials | Explanations, choices. |
+| How-to guides | Teaching, complete reference. |
+| Core concepts | Instructions, reference. |
+| Reference | Instructions, explanations. |
 
 ## References
 
PATCH

echo "Gold patch applied."
