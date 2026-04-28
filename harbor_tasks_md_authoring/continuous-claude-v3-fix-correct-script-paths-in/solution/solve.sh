#!/usr/bin/env bash
set -euo pipefail

cd /workspace/continuous-claude-v3

# Idempotency guard
if grep -qF "uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\" ".claude/skills/firecrawl-scrape/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/github_search.py \\" ".claude/skills/github-search/SKILL.md" && grep -qF "(cd opc && uv run python scripts/core/recall_learnings.py --query \"hook patterns" ".claude/skills/help/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/morph_apply.py \\" ".claude/skills/implement_task/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/morph_apply.py \\" ".claude/skills/morph-apply/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/morph_search.py \\" ".claude/skills/morph-search/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/nia_docs.py \\" ".claude/skills/nia-docs/SKILL.md" && grep -qF "uv run python scripts/mcp/perplexity_search.py \\" ".claude/skills/perplexity-search/SKILL.md" && grep -qF "uv run python scripts/core/artifact_query.py \"<query>\" [--outcome SUCCEEDED|FAIL" ".claude/skills/recall-reasoning/SKILL.md" && grep -qF "cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/recall_lea" ".claude/skills/recall/SKILL.md" && grep -qF "cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/store_lear" ".claude/skills/remember/SKILL.md" && grep -qF "uv run python -m runtime.harness scripts/mcp/perplexity_search.py \\" ".claude/skills/research-agent/SKILL.md" && grep -qF "(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/fire" ".claude/skills/research-external/SKILL.md" && grep -qF "| Store learning | `opc/scripts/core/store_learning.py` |" ".claude/skills/system_overview/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/firecrawl-scrape/SKILL.md b/.claude/skills/firecrawl-scrape/SKILL.md
@@ -15,7 +15,7 @@ allowed-tools: [Bash, Read]
 ## Instructions
 
 ```bash
-uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
     --url "https://example.com" \
     --format "markdown"
 ```
@@ -30,11 +30,11 @@ uv run python -m runtime.harness scripts/firecrawl_scrape.py \
 
 ```bash
 # Scrape a page
-uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
     --url "https://docs.python.org/3/library/asyncio.html"
 
 # Search and scrape
-uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
     --search "Python asyncio best practices 2024"
 ```
 
diff --git a/.claude/skills/github-search/SKILL.md b/.claude/skills/github-search/SKILL.md
@@ -15,7 +15,7 @@ allowed-tools: [Bash, Read]
 ## Instructions
 
 ```bash
-uv run python -m runtime.harness scripts/github_search.py \
+uv run python -m runtime.harness scripts/mcp/github_search.py \
     --type "code" \
     --query "your search query"
 ```
@@ -31,12 +31,12 @@ uv run python -m runtime.harness scripts/github_search.py \
 
 ```bash
 # Search code
-uv run python -m runtime.harness scripts/github_search.py \
+uv run python -m runtime.harness scripts/mcp/github_search.py \
     --type "code" \
     --query "authentication language:python"
 
 # Search issues
-uv run python -m runtime.harness scripts/github_search.py \
+uv run python -m runtime.harness scripts/mcp/github_search.py \
     --type "issues" \
     --query "bug label:critical" \
     --owner "anthropics"
diff --git a/.claude/skills/help/SKILL.md b/.claude/skills/help/SKILL.md
@@ -165,7 +165,7 @@ Store and recall learnings across sessions.
 
 ```bash
 # Recall past learnings
-(cd opc && uv run python scripts/recall_learnings.py --query "hook patterns")
+(cd opc && uv run python scripts/core/recall_learnings.py --query "hook patterns")
 
 # Store new learning (via /remember skill)
 /remember "Hook X works by..."
diff --git a/.claude/skills/implement_task/SKILL.md b/.claude/skills/implement_task/SKILL.md
@@ -86,7 +86,7 @@ For implementing code changes, choose based on file size and context:
 **Using morph-apply (recommended for large files):**
 ```bash
 # Fast edit without reading file first
-uv run python -m runtime.harness scripts/morph_apply.py \
+uv run python -m runtime.harness scripts/mcp/morph_apply.py \
     --file "src/auth.ts" \
     --instruction "I will add null check for user" \
     --code_edit "// ... existing code ...
diff --git a/.claude/skills/morph-apply/SKILL.md b/.claude/skills/morph-apply/SKILL.md
@@ -34,7 +34,7 @@ The API intelligently places your edit in the right location.
 
 ### Add error handling
 ```bash
-uv run python -m runtime.harness scripts/morph_apply.py \
+uv run python -m runtime.harness scripts/mcp/morph_apply.py \
     --file "src/auth.py" \
     --instruction "Add error handling to login function" \
     --code_edit "# ... existing code ...
@@ -48,7 +48,7 @@ except AuthError as e:
 
 ### Add logging
 ```bash
-uv run python -m runtime.harness scripts/morph_apply.py \
+uv run python -m runtime.harness scripts/mcp/morph_apply.py \
     --file "src/api.py" \
     --instruction "Add debug logging" \
     --code_edit "# ... existing code ...
@@ -58,7 +58,7 @@ logger.debug(f'Processing request: {request.id}')
 
 ### TypeScript example
 ```bash
-uv run python -m runtime.harness scripts/morph_apply.py \
+uv run python -m runtime.harness scripts/mcp/morph_apply.py \
     --file "src/types.ts" \
     --instruction "Add user validation" \
     --code_edit "// ... existing code ...
diff --git a/.claude/skills/morph-search/SKILL.md b/.claude/skills/morph-search/SKILL.md
@@ -18,19 +18,19 @@ Fast, AI-powered codebase search using WarpGrep. 20x faster than traditional gre
 
 ### Search for code patterns
 ```bash
-uv run python -m runtime.harness scripts/morph_search.py \
+uv run python -m runtime.harness scripts/mcp/morph_search.py \
     --search "authentication" --path "."
 ```
 
 ### Search with regex
 ```bash
-uv run python -m runtime.harness scripts/morph_search.py \
+uv run python -m runtime.harness scripts/mcp/morph_search.py \
     --search "def.*login" --path "./src"
 ```
 
 ### Edit a file
 ```bash
-uv run python -m runtime.harness scripts/morph_search.py \
+uv run python -m runtime.harness scripts/mcp/morph_search.py \
     --edit "/path/to/file.py" --content "new content"
 ```
 
@@ -47,11 +47,11 @@ uv run python -m runtime.harness scripts/morph_search.py \
 
 ```bash
 # Find all async functions
-uv run python -m runtime.harness scripts/morph_search.py \
+uv run python -m runtime.harness scripts/mcp/morph_search.py \
     --search "async def" --path "./src"
 
 # Search for imports
-uv run python -m runtime.harness scripts/morph_search.py \
+uv run python -m runtime.harness scripts/mcp/morph_search.py \
     --search "from fastapi import" --path "."
 ```
 
diff --git a/.claude/skills/nia-docs/SKILL.md b/.claude/skills/nia-docs/SKILL.md
@@ -12,25 +12,25 @@ Search across 3000+ packages (npm, PyPI, Crates, Go) and indexed sources for doc
 
 ### Semantic search in a package
 ```bash
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package fastapi --query "dependency injection"
 ```
 
 ### Search with specific registry
 ```bash
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package react --registry npm --query "hooks patterns"
 ```
 
 ### Grep search for specific patterns
 ```bash
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package sqlalchemy --grep "session.execute"
 ```
 
 ### Universal search across indexed sources
 ```bash
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --search "error handling middleware"
 ```
 
@@ -49,15 +49,15 @@ uv run python -m runtime.harness scripts/nia_docs.py \
 
 ```bash
 # Python library usage
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package pydantic --registry py_pi --query "validators"
 
 # React patterns
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package react --query "useEffect cleanup"
 
 # Find specific function usage
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package express --grep "app.use"
 ```
 
diff --git a/.claude/skills/perplexity-search/SKILL.md b/.claude/skills/perplexity-search/SKILL.md
@@ -28,33 +28,33 @@ Web search with AI-powered answers, deep research, and chain-of-thought reasonin
 
 ### Quick question (AI answer)
 ```bash
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --ask "What is the latest version of Python?"
 ```
 
 ### Direct web search (ranked results, no AI)
 ```bash
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --search "SQLite graph database patterns" \
     --max-results 5 \
     --recency week
 ```
 
 ### AI-synthesized research
 ```bash
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --research "compare FastAPI vs Django for microservices"
 ```
 
 ### Chain-of-thought reasoning
 ```bash
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --reason "should I use Neo4j or SQLite for small graph under 10k nodes?"
 ```
 
 ### Deep comprehensive research
 ```bash
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --deep "state of AI agent observability 2025"
 ```
 
@@ -89,20 +89,20 @@ uv run python scripts/perplexity_search.py \
 
 ```bash
 # Find recent sources on a topic
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --search "OpenTelemetry AI agent tracing" \
     --recency month --max-results 5
 
 # Get AI synthesis
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --research "best practices for AI agent logging 2025"
 
 # Make a decision
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --reason "microservices vs monolith for startup MVP"
 
 # Deep dive
-uv run python scripts/perplexity_search.py \
+uv run python scripts/mcp/perplexity_search.py \
     --deep "comprehensive guide to building feedback loops for autonomous agents"
 ```
 
diff --git a/.claude/skills/recall-reasoning/SKILL.md b/.claude/skills/recall-reasoning/SKILL.md
@@ -24,7 +24,7 @@ Search through previous sessions to find relevant decisions, approaches that wor
 ### Primary: Artifact Index (rich context)
 
 ```bash
-uv run python scripts/artifact_query.py "<query>" [--outcome SUCCEEDED|FAILED] [--limit N]
+uv run python scripts/core/artifact_query.py "<query>" [--outcome SUCCEEDED|FAILED] [--limit N]
 ```
 
 This searches handoffs with post-mortems (what worked, what failed, key decisions).
@@ -41,13 +41,13 @@ This searches `.git/claude/commits/*/reasoning.md` for build failures and fixes.
 
 ```bash
 # Search for authentication-related work
-uv run python scripts/artifact_query.py "authentication OAuth JWT"
+uv run python scripts/core/artifact_query.py "authentication OAuth JWT"
 
 # Find only successful approaches
-uv run python scripts/artifact_query.py "implement agent" --outcome SUCCEEDED
+uv run python scripts/core/artifact_query.py "implement agent" --outcome SUCCEEDED
 
 # Find what failed (to avoid repeating mistakes)
-uv run python scripts/artifact_query.py "hook implementation" --outcome FAILED
+uv run python scripts/core/artifact_query.py "hook implementation" --outcome FAILED
 
 # Search build/test reasoning
 bash "$CLAUDE_PROJECT_DIR/.claude/scripts/search-reasoning.sh" "TypeError"
@@ -90,7 +90,7 @@ bash "$CLAUDE_PROJECT_DIR/.claude/scripts/search-reasoning.sh" "TypeError"
 ## No Results?
 
 **Artifact Index empty:**
-- Run `uv run python scripts/artifact_index.py --all` to index existing handoffs
+- Run `uv run python scripts/core/artifact_index.py --all` to index existing handoffs
 - Create handoffs with post-mortem sections for future recall
 
 **Reasoning files empty:**
diff --git a/.claude/skills/recall/SKILL.md b/.claude/skills/recall/SKILL.md
@@ -27,7 +27,7 @@ Query the memory system for relevant learnings from past sessions.
 When this skill is invoked, run:
 
 ```bash
-cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/recall_learnings.py --query "<ARGS>" --k 5
+cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/recall_learnings.py --query "<ARGS>" --k 5
 ```
 
 Where `<ARGS>` is the query provided by the user.
diff --git a/.claude/skills/remember/SKILL.md b/.claude/skills/remember/SKILL.md
@@ -44,7 +44,7 @@ Or with explicit type:
 When this skill is invoked, run:
 
 ```bash
-cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/store_learning.py \
+cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/store_learning.py \
   --session-id "manual-$(date +%Y%m%d-%H%M)" \
   --type <TYPE or WORKING_SOLUTION> \
   --content "<ARGS>" \
diff --git a/.claude/skills/research-agent/SKILL.md b/.claude/skills/research-agent/SKILL.md
@@ -32,21 +32,21 @@ Use the MCP scripts via Bash:
 
 **For library documentation (Nia):**
 ```bash
-uv run python -m runtime.harness scripts/nia_docs.py \
+uv run python -m runtime.harness scripts/mcp/nia_docs.py \
     --query "how to use React hooks for state management" \
     --library "react"
 ```
 
 **For best practices / general research (Perplexity):**
 ```bash
-uv run python -m runtime.harness scripts/perplexity_search.py \
+uv run python -m runtime.harness scripts/mcp/perplexity_search.py \
     --query "best practices for implementing OAuth2 in Node.js 2024" \
     --mode "research"
 ```
 
 **For scraping specific documentation pages (Firecrawl):**
 ```bash
-uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
     --url "https://docs.example.com/api/authentication"
 ```
 
diff --git a/.claude/skills/research-external/SKILL.md b/.claude/skills/research-external/SKILL.md
@@ -164,19 +164,19 @@ Primary tool: **nia-docs** - Find API documentation, usage patterns, code exampl
 
 ```bash
 # Semantic search in package
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/nia_docs.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package "$LIBRARY" \
   --registry "$REGISTRY" \
   --query "$TOPIC" \
   --limit 10)
 
 # If thorough depth, also grep for specific patterns
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/nia_docs.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --package "$LIBRARY" \
   --grep "$TOPIC")
 
 # Supplement with official docs if URL known
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
   --url "https://docs.example.com/api/$TOPIC" \
   --format markdown)
 ```
@@ -192,26 +192,26 @@ Primary tool: **perplexity-search** - Find recommended approaches, patterns, ant
 
 ```bash
 # AI-synthesized research (sonar-pro)
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --research "$TOPIC best practices 2024 2025")
 
 # If comparing alternatives
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --reason "$TOPIC vs alternatives - which to choose?")
 ```
 
 **Thorough depth additions:**
 ```bash
 # Chain-of-thought for complex decisions
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --reason "$TOPIC tradeoffs and considerations 2025")
 
 # Deep comprehensive research
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --deep "$TOPIC comprehensive guide 2025")
 
 # Recent developments
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --search "$TOPIC latest developments" \
   --recency month --max-results 5)
 ```
@@ -222,20 +222,20 @@ Use ALL available MCP tools - comprehensive multi-source research.
 
 **Step 2a: Library documentation (nia-docs)**
 ```bash
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/nia_docs.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/nia_docs.py \
   --search "$TOPIC")
 ```
 
 **Step 2b: Web research (perplexity)**
 ```bash
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/perplexity_search.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \
   --research "$TOPIC")
 ```
 
 **Step 2c: Specific documentation (firecrawl)**
 ```bash
 # Scrape relevant documentation pages found in perplexity results
-(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/firecrawl_scrape.py \
+(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \
   --url "$FOUND_DOC_URL" \
   --format markdown)
 ```
diff --git a/.claude/skills/system_overview/SKILL.md b/.claude/skills/system_overview/SKILL.md
@@ -71,7 +71,7 @@ Options:
 | Skills | `.claude/skills/*/SKILL.md` |
 | Setup wizard | `opc/scripts/setup/wizard.py` |
 | Recall script | `opc/scripts/recall_temporal_facts.py` |
-| Store learning | `opc/scripts/store_learning.py` |
+| Store learning | `opc/scripts/core/store_learning.py` |
 | Symbol index builder | `opc/scripts/build_symbol_index.py` |
 
 ## Environment Variables
PATCH

echo "Gold patch applied."
