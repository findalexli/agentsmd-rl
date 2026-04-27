#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-codex-settings

# Idempotency guard
if grep -qF "- **Before exiting the plan mode**: Never assume anything. Always run tests with" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -22,12 +22,34 @@ Guidance for Claude Code and other AI tools working in this repository.
 
 ## MCP Tools
 
-- Use `mcp__tavily__tavily_search` for web discovery, `mcp__tavily__tavily_extract` for specific URLs
+### Tavily (Web Search)
+
+- Use `mcp__tavily__tavily_search` for discovery/broad queries
+- Use `mcp__tavily__tavily_extract` for specific URL content
+- Search first to find URLs, then extract for detailed analysis
+
+### MongoDB
+
 - MongoDB MCP is READ-ONLY (no write/update/delete operations)
-- For GitHub URLs, use `mcp__github__*` tools or `gh` CLI instead of web scraping
+
+### GitHub CLI
+
+Use `gh` CLI for all GitHub interactions. Never clone repositories to read code.
+
+- **Read file from repo**: `gh api repos/{owner}/{repo}/contents/{path} -q .content | base64 -d`
+- **Search code**: `gh search code "query" --repo {owner}/{repo}` or `gh search code "query" --language python`
+- **Search repos**: `gh search repos "query" --language python --sort stars`
+- **Compare commits**: `gh api repos/{owner}/{repo}/compare/{base}...{head}`
+- **View PR**: `gh pr view {number} --repo {owner}/{repo}`
+- **View PR diff**: `gh pr diff {number} --repo {owner}/{repo}`
+- **View PR comments**: `gh api repos/{owner}/{repo}/pulls/{number}/comments`
+- **List commits**: `gh api repos/{owner}/{repo}/commits --jq '.[].sha'`
+- **View issue**: `gh issue view {number} --repo {owner}/{repo}`
 
 ## Python Coding
 
+- **Before exiting the plan mode**: Never assume anything. Always run tests with `python -c "..."` to verify you hypothesis and bugfix candidates about code behavior, package functions, or data structures before suggesting a plan or exiting the plan mode. This prevents wasted effort on incorrect assumptions.
+- **Package Manager**: uv (NOT pip) - defined in pyproject.toml
 - Use Google-style docstrings:
   - **Summary**: Start with clear, concise summary line in imperative mood ("Calculate", not "Calculates")
   - **Args/Attributes**: Document all parameters with types and brief descriptions (no default values)
@@ -91,3 +113,22 @@ Guidance for Claude Code and other AI tools working in this repository.
 
 - `/github-dev:commit-staged` - commit staged changes
 - `/github-dev:create-pr` - create pull request
+
+## Citation Verification Rules
+
+**CRITICAL**: Never use unverified citation information. Before adding or referencing any academic citation:
+
+1. **Author Names**: Verify exact author names from the actual paper PDF or official publication page. Do not guess or hallucinate author names based on similar-sounding names.
+2. **Publication Venue**: Confirm the exact venue (conference/journal) and year. Papers may be submitted to one venue but published at another (e.g., ICLR submission → ICRA publication).
+3. **Paper Title**: Use the exact title from the published version, not preprint titles which may differ.
+4. **Cited Claims**: Every specific claim attributed to a paper (e.g., "9% improvement on Synthia", "4.7% on OpenImages") must be verifiable in the actual paper text. If a number cannot be confirmed, use qualitative language instead (e.g., "significant improvements").
+5. **BibTeX Keys**: When updating citation keys, search for ALL references to the old key and update them consistently.
+
+**Verification Process**:
+
+- Use web search to find the official publication page (not just preprints)
+- Cross-reference author names with the paper's author list
+- DBLP is the authoritative source for CS publication metadata
+- For specific numerical claims, locate the exact quote or table in the paper
+- When uncertain, flag the citation for manual verification rather than guessing
+- After adding citations into md or bibtex entries into biblo.bib, fact check all fields from web. Even if you performed fact check before, always do it again after writing the citation in the document.
\ No newline at end of file
PATCH

echo "Gold patch applied."
