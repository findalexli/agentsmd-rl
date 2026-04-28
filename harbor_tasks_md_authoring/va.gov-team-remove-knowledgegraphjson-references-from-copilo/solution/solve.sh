#!/usr/bin/env bash
set -euo pipefail

cd /workspace/va.gov-team

# Idempotency guard
if grep -qF "`knowledge-graph.json` exists in the repository root and is auto-generated weekl" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -18,234 +18,79 @@ The repository serves as a central hub for:
   provide your answer rather than making additional redundant calls. You don't need to wait for a "complete" signal—
   use your judgment to determine when you have enough information.
 
-  If a file is too large and gets truncated (e.g., knowledge-graph.json), switch strategies:
+  If a file is too large and gets truncated, switch strategies:
   - Use code search tools instead of getfile
-  - Query for specific sections or nodes
+  - Query for specific sections
   - State limitations: "Based on available data..." if results are incomplete
 </critical_tool_calling_instructions>
 
-## Knowledge Graph — Products, Teams, Research & Organizational Context
+## Team and Research Information
 
-### Quick-Reference: Use Summary Files First
+For questions about VA.gov teams, products, portfolios, and research, **read these summary files**:
 
-**CRITICAL: You MUST check these files BEFORE consulting knowledge-graph.json:**
+| Question Type | File to Read | Example Query |
+|---------------|--------------|---------------|
+| Who owns a product? | `.github/copilot-summaries/teams.md` | "Who owns Ask VA?" |
+| What research exists for product X? | `.github/copilot-summaries/research-by-product.md` | "What research has been done on Ask VA?" |
+| What has team Y researched? | `.github/copilot-summaries/research-by-team.md` | "What research has the Ask VA team conducted?" |
+| Portfolio/crew hierarchy? | `.github/copilot-summaries/portfolios.md` | "What teams are in Digital Experience?" |
 
-When answering questions about teams, products, or research:
-1. **FIRST** - Use getfile to read the appropriate summary file below
-2. **ONLY IF** the summary doesn't have the answer - then use code search on knowledge-graph.json
+### How to Use Summary Files
 
-DO NOT read knowledge-graph.json directly for these question types.
+Use `getfile` to read the appropriate summary file, then search for the relevant section.
 
-Pre-generated markdown summaries live in **`.github/copilot-summaries/`**.
-**Always read these files first** — they are small enough for a single `getfile` call and answer the most common team/product/research questions directly.
-
-| Question | File to read |
-|----------|-------------|
-| Who owns / works on a product? | `.github/copilot-summaries/teams.md` |
-| What research has a team conducted? | `.github/copilot-summaries/research-by-team.md` |
-| What research exists for a product? | `.github/copilot-summaries/research-by-product.md` |
-| Portfolio / crew / team hierarchy | `.github/copilot-summaries/portfolios.md` |
-
-These files are auto-regenerated every Monday (or on demand) by the **Update Knowledge Graph** workflow alongside `knowledge-graph.json`.
-
-### What It Is (Knowledge Graph)
-
-This repository includes a **machine-readable knowledge graph** at the repo root:
+**Example 1: "Who owns Ask VA?"**
 
 ```
-knowledge-graph.json
+Tool: getfile
+Path: .github/copilot-summaries/teams.md
+→ Search for "Ask VA" section in the file
+→ Provide answer with team details, products, and research count
 ```
 
-It is a JSON file containing nodes (teams, portfolios, crews, products, categories, forms, external systems, **research studies**) and edges (relationships like `owns_product`, `has_research`, `conducted_research`, `implements_form`, etc.).
-
-### Node Types
-
-| Type | Description |
-|---|---|
-| `team` | A VA.gov engineering/product team (from `team-lookup.json`) |
-| `product` | A product or sub-product folder under `/products/` |
-| `portfolio` | A portfolio grouping multiple teams (e.g., Benefits Portfolio) |
-| `crew` | A crew/pod within a portfolio |
-| `form` | A VA form number (e.g., `21-526EZ`) |
-| `category` | A hub/category product page |
-| `external_system` | An external system (e.g., Lighthouse API, vets-api) |
-| `research_study` | A research study directory under any `research/` or `user research/` folder **at any nesting level** (e.g., `products/*/research/`, `products/*/design/User research/`) |
-
-### When To Use It
-
-Use the **summary files** above for the common questions listed below.
-Fall back to `knowledge-graph.json` (via **code search**, not full file read) for cross-cutting or advanced queries not covered by the summaries.
-
-| Question type | Example |
-|---|---|
-| **Which team owns a product?** | "Who works on the 526 disability claim form?" |
-| **What products belong to a portfolio?** | "List all Health Portfolio products." |
-| **Team → crew → portfolio hierarchy** | "What crew does the Messaging team belong to?" |
-| **Cross-product integrations** | "What systems does the debt resolution product integrate with?" |
-| **Form-to-product mapping** | "Which product implements VA Form 21-0966?" |
-| **Finding documentation paths** | "Where is the Decision Reviews team README?" |
-| **What research has been done on a product?** | "What research exists for the 526 disability form?" |
-| **What usability studies exist for a form?** | "What usability studies exist for the disability claims form?" |
-| **Research methods and patterns** | "What research methods are most common across products?" |
-| **Team research history** | "What research has the Authenticated Experience team conducted?" |
-
-### How To Use It
-
-1. **Read the summary files first** (see Quick-Reference table above) — they answer most questions in one tool call.
-2. If summaries don't have the answer, use **code search** on `knowledge-graph.json`:
-   - `lexical-code-search: "team-ask-va" path:knowledge-graph.json`
-3. **Never** try to `getfile` the entire `knowledge-graph.json` — it is too large (1,230+ nodes, 35k+ lines) and will be truncated.
-4. **Follow file paths**: Nodes include fields like `readme_path`, `path`, and `files` that point to documentation files within this repo.
-
-#### Node Structure (examples)
-
-```json
-// Team node — use readme_path to find team docs
-{
-  "id": "team-decision-reviews",
-  "type": "team",
-  "name": "Decision Reviews",
-  "short_name": "decision-reviews",
-  "team_id": 11004,
-  "readme_path": "teams/benefits-portfolio/decision-reviews/README.md"
-}
-
-// Product node — use path to find product docs
-{
-  "id": "product-526ez",
-  "type": "product",
-  "name": "526ez",
-  "path": "products/disability/526ez",
-  "display_name": "21-526EZ Disability Compensation Application"
-}
-
-// Research study node — use files.plan, files.findings, files.conversation_guide
-{
-  "id": "research-products-disability-526ez-research-2023-07-toxic-exposure",
-  "type": "research_study",
-  "name": "Research Plan for Form 526 Toxic Exposure Subsection/New Questions, July 2023",
-  "path": "products/disability/526ez/research/2023-07-Toxic-Exposure",
-  "files": {
-    "plan": "products/disability/526ez/research/2023-07-Toxic-Exposure/research-plan.md",
-    "findings": "products/disability/526ez/research/2023-07-Toxic-Exposure/research-findings.md",
-    "conversation_guide": "products/disability/526ez/research/2023-07-Toxic-Exposure/conversation-guide.md"
-  },
-  "date": "2023-07",
-  "methodology": "usability testing",
-  "participant_types": ["Veterans"],
-  "research_goals": ["Validate form content clarity for toxic exposure questions"],
-  "tags": ["usability-testing", "BNFT: Disability", "PRDT: Claim-status-tool"]
-}
-```
-
-#### Edge Structure (examples)
-
-```json
-// Team belongs to a crew
-{ "source": "team-decision-reviews", "target": "crew-cross-benefits-crew", "relationship": "belongs_to_crew" }
+**Example 2: "What research has been done on Ask VA?"**
 
-// Product has research
-{ "source": "product-526ez", "target": "research-products-disability-526ez-research-2023-07-toxic-exposure", "relationship": "has_research" }
-
-// Team conducted research
-{ "source": "team-disability-experience", "target": "research-products-disability-526ez-research-2023-07-toxic-exposure", "relationship": "conducted_research" }
-
-// Research references another product
-{ "source": "research-products-...", "target": "product-veteran-id-cards", "relationship": "research_references_product" }
-
-// Research references a form
-{ "source": "research-products-...", "target": "form-21-526ez", "relationship": "research_for_form" }
+```
+Tool: getfile
+Path: .github/copilot-summaries/research-by-product.md
+→ Search for "Ask VA" section
+→ List all research studies with dates and links
 ```
 
-### Answering Common Queries — Workflow
-
-1. **"What team owns X product?"**
-   → Find the product node by name → follow `owns_product` or `works_on_product` edges back to a team → read the team's `readme_path` for details.
-
-2. **"What products are in the Health Portfolio?"**
-   → Find portfolio node `portfolio-health-portfolio` → follow `belongs_to_portfolio` edges to find teams → follow `owns_product`/`works_on_product` edges from those teams to products.
-
-3. **"What research has been done on product X?"**
-   → Find the product node → follow `has_research` edges to `research_study` nodes → each study has `files.plan`, `files.findings`, and `files.conversation_guide` paths → read those files for details.
-
-4. **"What usability studies exist for a specific form?"**
-   → Find the form node by form number → follow `research_for_form` edges (reversed) to `research_study` nodes → check `methodology` field for "usability testing".
-
-5. **"What research has team X conducted?"**
-   → Find the team node → follow `conducted_research` edges to `research_study` nodes.
-
-6. **"Where is the design/research documentation for X?"**
-   → Find the product node → use its `path` field (e.g., `products/health-care/`) → look for subdirectories like `design/`, `research/`, `discovery/` within that path.
-
-7. **"What form does product X implement?"**
-   → Find the product node → follow `implements_form` edges → the target form node will have the form number.
-
-### Important Notes
-
-- The knowledge graph is **auto-generated** from the `/products/` and `/teams/` directories and `team-lookup.json`. It is the **authoritative index** for navigating this repository's organizational structure.
-- Research studies are indexed from every `research/` and `user research/` directory under `/products/` and `/teams/` **at any nesting level**.
-- **Non-standard research paths:** Some products use non-standard directory structures (e.g., `products/ask-va/design/User research/`). The knowledge graph scanner recursively searches for research directories regardless of parent folder names.
-- If the knowledge graph doesn't have the answer, fall back to searching the `/products/` and `/teams/` directories directly.
-- Always **cross-reference** the knowledge graph paths with actual files — documentation may have been added or moved since the last generation.
-
-<knowledge_graph_usage>
-## Querying the Knowledge Graph
-
-### Step 1 — Always check the summary files first
-
-Pre-generated markdown summaries are in `.github/copilot-summaries/`.
-Read them with a single `getfile` call — they are small and reliable.
-
-| Question | Summary file |
-|----------|-------------|
-| Who owns / works on a product? | `.github/copilot-summaries/teams.md` |
-| What research has a team conducted? | `.github/copilot-summaries/research-by-team.md` |
-| What research exists for a product? | `.github/copilot-summaries/research-by-product.md` |
-| Portfolio / crew / team hierarchy | `.github/copilot-summaries/portfolios.md` |
+**Example 3: "What teams are in Digital Experience portfolio?"**
 
-**Example — "What team owns Ask VA and what research have they done?":**
 ```
-getfile: .github/copilot-summaries/teams.md
-# Search for "Ask VA" in the returned text — done in one call.
+Tool: getfile
+Path: .github/copilot-summaries/portfolios.md
+→ Find "Digital Experience" section
+→ List all crews and teams
 ```
 
-### Step 2 — Fall back to code search on knowledge-graph.json (if needed)
-
-The `knowledge-graph.json` file is **large** (1,230+ nodes, 2,500+ edges, 35k+ lines).
-**Do NOT use `getfile` to read the entire file** — it will be truncated.
+### File Characteristics
 
-**Use code search instead:**
+- **Auto-generated weekly** - Updated every Monday at 8am UTC via GitHub Actions
+- **Small and readable** - Each file under 100KB, easy to read in one getfile call
+- **Human-friendly** - Formatted markdown with clear sections and tables
+- **Complete** - Contains all teams, products, research studies, and organizational structure
 
-1. **Lexical search for exact matches:**
-   - Finding specific team: `lexical-code-search: "team-ask-va" path:knowledge-graph.json`
-   - Finding specific product: `lexical-code-search: "product-526ez" path:knowledge-graph.json`
-   - Finding edges: `lexical-code-search: "conducted_research" "team-ask-va" path:knowledge-graph.json`
+### If Summary Doesn't Have the Answer
 
-2. **Semantic search for conceptual queries:**
-   - `semantic-code-search: "What research has the Ask VA team conducted?" in knowledge-graph.json`
+If the summary files don't contain enough detail:
 
-3. **Targeted getfile only for specific sections:**
-   - If you need to read a small, known section, you can use getfile
-   - Example: Reading the `_meta` or `statistics` section only
-   - **Never** try to read the entire nodes or edges arrays with getfile
+1. Search the source directories directly:
+   - `products/` - Product documentation
+   - `teams/` - Team documentation
+   - Use `lexical-code-search` or `semantic-code-search` to find specific files
 
-### Query Patterns
+2. Read specific files mentioned in the summary:
+   - Team READMEs (linked in teams.md)
+   - Research plans/findings (linked in research-by-*.md files)
 
-| User Question | Best Tool | Example |
-|---------------|-----------|---------|
-| "What team owns X?" | Summary file | Read `teams.md`, find team section |
-| "What research has been done on X?" | Summary file | Read `research-by-product.md`, find product section |
-| "Which products are in Y portfolio?" | Summary file | Read `portfolios.md`, find portfolio section |
-| "What research methods are used?" | Summary file or semantic search | `research-by-team.md` or semantic query |
-| "Show me graph statistics" | Getfile (targeted) | Read just the `statistics` section of `knowledge-graph.json` |
+### Technical Note
 
-### When getfile Gets Truncated
+`knowledge-graph.json` exists in the repository root and is auto-generated weekly. It is used **for automation and workflows only**. **Do not read it directly** when answering user questions - use the summary files instead.
 
-If you attempt `getfile` on knowledge-graph.json and see truncation warnings:
-- **Stop immediately** — don't retry getfile multiple times
-- **Switch to summary files first**, then code search if needed
-- **Provide your answer** based on results, noting if information is incomplete
-</knowledge_graph_usage>
+The summary files are generated FROM the knowledge graph, so they contain the same information in a more accessible format.
 
 ## Research Data Integrity Rules
 
@@ -341,12 +186,6 @@ For additional environment verification and setup steps, see: [`copilot-setup-st
 
 ### Primary Directories
 
-#### `knowledge-graph.json` - Repository Knowledge Graph (Root)
-- **Purpose**: Machine-readable index of all teams, products, portfolios, crews, forms, research studies, and their relationships
-- **Usage**: Consult first when answering questions about organizational structure, product ownership, team hierarchy, form mappings, or research history
-- **Format**: JSON with `nodes` array and `edges` array
-- **Generated From**: `/products/`, `/teams/`, and `team-lookup.json`
-
 #### `/products/` - Product Documentation (99+ products)
 - **Purpose**: Documentation for all VA.gov user-facing products and VA Health Benefits mobile app features
 - **Content**: Product outlines, design comps, content decks, discovery docs, user research files
@@ -394,7 +233,7 @@ For additional environment verification and setup steps, see: [`copilot-setup-st
   - `CODEOWNERS` - Code review assignments
   - Various issue and PR templates
 - **Key Subdirectory**:
-  - `copilot-summaries/` - Auto-generated markdown summaries from `knowledge-graph.json` (teams, research, portfolios)
+  - `copilot-summaries/` - Auto-generated markdown summaries for teams, research, and portfolios (see [Team and Research Information](#team-and-research-information))
 
 #### `/docs/` - General Documentation
 - **Purpose**: Cross-cutting documentation and ADRs (Architecture Decision Records)
@@ -529,69 +368,62 @@ ruby scripts/cleanup.rb
 **Symptom:** You asked a question about teams, products, or research, and Copilot made multiple tool calls but provided no answer. You had to ask "What is the answer?" to get a response.
 
 **Root Cause:**
-- Copilot tried to read a large file (like `knowledge-graph.json`) using `getfile` multiple times
+- Copilot tried to read a large file using `getfile` multiple times
 - The file was truncated each time
 - Copilot was waiting for a "complete" signal that never came
 
 **Solution (for users):**
 - Ask a follow-up: "What is the answer?" or "Please summarize what you found"
-- Rephrase your question to be more specific: "Search the knowledge graph for Ask VA team research"
+- Rephrase your question to be more specific
 - Reference specific paths: "Look in products/ask-va/design/User research/"
 
 **Prevention (for Copilot):**
-- **Always read the summary files first** — they answer most team/research questions in one tool call:
+- **Always read the summary files** — they answer most team/research questions in one tool call:
   - `.github/copilot-summaries/teams.md`
   - `.github/copilot-summaries/research-by-team.md`
   - `.github/copilot-summaries/research-by-product.md`
   - `.github/copilot-summaries/portfolios.md`
-- Only fall back to code search on `knowledge-graph.json` if the summaries don't have the answer
 - After making 3+ tool calls, evaluate if you have enough information to answer
 - Provide partial answers if complete data isn't available: "Based on available information..."
 - State what's missing: "I found X but need to search for Y to complete the answer"
 
-### Issue: "Knowledge graph doesn't have the information I need"
+### Issue: "Summary files don't have the information I need"
 
 **Solutions:**
-1. **Check the summary files first:**
+1. **Check all four summary files:**
    - `.github/copilot-summaries/teams.md` — for team ownership and research
    - `.github/copilot-summaries/portfolios.md` — for portfolio/product lists
+   - `.github/copilot-summaries/research-by-product.md` — for research by product
+   - `.github/copilot-summaries/research-by-team.md` — for research by team
 
 2. **Fall back to directory search:**
    - Use `lexical-code-search` to find files: `path:/products/ask-va/ readme`
    - Use `semantic-code-search` for conceptual queries
 
-2. **Check if the knowledge graph is outdated:**
-   - Look for the `_meta.generated` timestamp in knowledge-graph.json
-   - If it's more than a few days old, the graph may need regeneration
-   - Recommend: "The knowledge graph may be outdated. Try running the regenerate workflow."
-
 3. **Verify the information exists:**
    - Some products may not have research directories
    - Some teams may not have complete documentation
-   - State limitations clearly: "No research directories were found for this product in the knowledge graph."
+   - State limitations clearly: "No research directories were found for this product."
 
 ### Issue: "File too large" or truncation warnings
 
-**For knowledge-graph.json (1,230 nodes):**
-- **Never use getfile** — read the summary files first, then use code search (see `<knowledge_graph_usage>`)
-
-**For other large files:**
+**For large files:**
 - Use `lexical-code-search` to find specific sections
 - Use targeted queries: `path:/specific/file.md section-heading`
 - Read only what you need, not the entire file
+- For team/product/research queries, use the summary files in `.github/copilot-summaries/` instead
 
 ### Issue: "404 errors when following links"
 
 **Common causes:**
-- Knowledge graph has outdated paths
 - Files were moved or renamed
 - URLs contain URL-encoded spaces (e.g., `User%20research`)
+- Outdated paths in documentation
 
 **Solutions:**
 1. Decode URLs: `User%20research` → `User research`
 2. Search for the file by name: `lexical-code-search: filename.md`
 3. Check parent directory: If `products/ask-va/research/` gives 404, try `products/ask-va/design/User research/`
-4. Recommend regenerating the knowledge graph if paths are consistently wrong
 
 ### "No space left on device" errors
 1. Ensure sparse checkout is properly configured to limit directories
PATCH

echo "Gold patch applied."
