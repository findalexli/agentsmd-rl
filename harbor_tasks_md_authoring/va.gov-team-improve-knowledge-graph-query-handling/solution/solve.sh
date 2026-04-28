#!/usr/bin/env bash
set -euo pipefail

cd /workspace/va.gov-team

# Idempotency guard
if grep -qF "**Symptom:** You asked a question about teams, products, or research, and Copilo" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -10,6 +10,20 @@ The repository serves as a central hub for:
 - **Issue tracking** for platform and product development
 - **Knowledge management** for Veterans Affairs digital services
 
+<critical_tool_calling_instructions>
+  Execute tool calls efficiently without excessive narration or explanation before calling tools.
+  After gathering necessary information through tools, synthesize and present your answer.
+
+  **Important**: If you've made multiple tool calls and gathered sufficient information to answer the user's question,
+  provide your answer rather than making additional redundant calls. You don't need to wait for a "complete" signal—
+  use your judgment to determine when you have enough information.
+
+  If a file is too large and gets truncated (e.g., knowledge-graph.json), switch strategies:
+  - Use code search tools instead of getfile
+  - Query for specific sections or nodes
+  - State limitations: "Based on available data..." if results are incomplete
+</critical_tool_calling_instructions>
+
 ## Knowledge Graph — Products, Teams, Research & Organizational Context
 
 ### What It Is
@@ -150,6 +164,73 @@ It is a JSON file containing nodes (teams, portfolios, crews, products, categori
 - If the knowledge graph doesn't have the answer, fall back to searching the `/products/` and `/teams/` directories directly.
 - Always **cross-reference** the knowledge graph paths with actual files — documentation may have been added or moved since the last generation.
 
+<knowledge_graph_usage>
+## Querying the Knowledge Graph
+
+The `knowledge-graph.json` file is **large** (1230+ nodes, 2500+ edges, 35k+ lines).
+**Do NOT use `getfile` to read the entire file**—it will be truncated and require multiple attempts.
+
+### Recommended Approach
+
+**Always prefer code search over getfile for knowledge graph queries:**
+
+1. **Lexical search for exact matches:**
+   - Finding specific team: `lexical-code-search: "team-ask-va" path:knowledge-graph.json`
+   - Finding specific product: `lexical-code-search: "product-526ez" path:knowledge-graph.json`
+   - Finding edges: `lexical-code-search: "conducted_research" "team-ask-va" path:knowledge-graph.json`
+
+2. **Semantic search for conceptual queries:**
+   - `semantic-code-search: "What research has the Ask VA team conducted?" in knowledge-graph.json`
+
+3. **Targeted getfile only for specific sections:**
+   - If you need to read a small, known section, you can use getfile
+   - Example: Reading the `_meta` or `statistics` section only
+   - **Never** try to read the entire nodes or edges arrays with getfile
+
+### Query Patterns
+
+| User Question | Best Tool | Example Query |
+|---------------|-----------|---------------|
+| "What team owns X?" | Lexical search | `"product-ask-va" "owns_product"` in knowledge-graph.json |
+| "What research has been done on X?" | Lexical search | `"product-ask-va" "has_research"` in knowledge-graph.json |
+| "Which products are in Y portfolio?" | Lexical search | `"portfolio-digital-experience" "belongs_to_portfolio"` in knowledge-graph.json |
+| "What research methods are used?" | Semantic search | Query about research methodologies in knowledge-graph.json |
+| "Show me graph statistics" | Getfile (targeted) | Read just the `statistics` section |
+
+### Multi-Step Workflow Example
+
+For complex queries like "What team owns Ask VA and what research have they done?":
+
+1. **Find the team node:**
+   ```
+   lexical-code-search: "team-ask-va" path:knowledge-graph.json
+   ```
+
+2. **Find research conducted by the team:**
+   ```
+   lexical-code-search: "team-ask-va" "conducted_research" path:knowledge-graph.json
+   ```
+
+3. **Get research details:**
+   ```
+   lexical-code-search: "research-products-ask-va-design-user-research" path:knowledge-graph.json
+   ```
+
+4. **Read actual research files (optional):**
+   ```
+   getfile: products/ask-va/design/User research/README.md
+   ```
+
+5. **Synthesize answer** combining all findings
+
+### When getfile Gets Truncated
+
+If you attempt `getfile` on knowledge-graph.json and see truncation warnings:
+- **Stop immediately** - don't retry getfile multiple times
+- **Switch to code search** using the patterns above
+- **Provide your answer** based on search results, noting if information is incomplete
+</knowledge_graph_usage>
+
 ## Research Data Integrity Rules
 
 ### CRITICAL: Never Fabricate Research Information
@@ -423,8 +504,68 @@ ruby scripts/cleanup.rb
 
 ## Troubleshooting Common Issues
 
+### Issue: "Copilot didn't answer my question on the first try"
+
+**Symptom:** You asked a question about teams, products, or research, and Copilot made multiple tool calls but provided no answer. You had to ask "What is the answer?" to get a response.
+
+**Root Cause:**
+- Copilot tried to read a large file (like `knowledge-graph.json`) using `getfile` multiple times
+- The file was truncated each time
+- Copilot was waiting for a "complete" signal that never came
+
+**Solution (for users):**
+- Ask a follow-up: "What is the answer?" or "Please summarize what you found"
+- Rephrase your question to be more specific: "Search the knowledge graph for Ask VA team research"
+- Reference specific paths: "Look in products/ask-va/design/User research/"
+
+**Prevention (for Copilot):**
+- **Always use code search for knowledge-graph.json queries** (see `<knowledge_graph_usage>`)
+- After making 3+ tool calls, evaluate if you have enough information to answer
+- Provide partial answers if complete data isn't available: "Based on available information..."
+- State what's missing: "I found X but need to search for Y to complete the answer"
+
+### Issue: "Knowledge graph doesn't have the information I need"
+
+**Solutions:**
+1. **Fall back to directory search:**
+   - Use `lexical-code-search` to find files: `path:/products/ask-va/ readme`
+   - Use `semantic-code-search` for conceptual queries
+
+2. **Check if the knowledge graph is outdated:**
+   - Look for the `_meta.generated` timestamp in knowledge-graph.json
+   - If it's more than a few days old, the graph may need regeneration
+   - Recommend: "The knowledge graph may be outdated. Try running the regenerate workflow."
+
+3. **Verify the information exists:**
+   - Some products may not have research directories
+   - Some teams may not have complete documentation
+   - State limitations clearly: "No research directories were found for this product in the knowledge graph."
+
+### Issue: "File too large" or truncation warnings
+
+**For knowledge-graph.json (1230 nodes):**
+- **Never use getfile** - always use code search (see `<knowledge_graph_usage>`)
+
+**For other large files:**
+- Use `lexical-code-search` to find specific sections
+- Use targeted queries: `path:/specific/file.md section-heading`
+- Read only what you need, not the entire file
+
+### Issue: "404 errors when following links"
+
+**Common causes:**
+- Knowledge graph has outdated paths
+- Files were moved or renamed
+- URLs contain URL-encoded spaces (e.g., `User%20research`)
+
+**Solutions:**
+1. Decode URLs: `User%20research` → `User research`
+2. Search for the file by name: `lexical-code-search: filename.md`
+3. Check parent directory: If `products/ask-va/research/` gives 404, try `products/ask-va/design/User research/`
+4. Recommend regenerating the knowledge graph if paths are consistently wrong
+
 ### "No space left on device" errors
-1. Ensure sparse checkout is properly configured to limit directories  
+1. Ensure sparse checkout is properly configured to limit directories
 2. Use shallow clone (`fetch-depth: 1`)
 3. Switch to larger GitHub Actions runners only if needed (`ubuntu-4-cores-latest`)
 4. Monitor disk usage with `df -h`
PATCH

echo "Gold patch applied."
