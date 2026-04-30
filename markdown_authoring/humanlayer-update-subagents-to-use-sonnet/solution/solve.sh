#!/usr/bin/env bash
set -euo pipefail

cd /workspace/humanlayer

# Idempotency guard
if grep -qF "model: sonnet" ".claude/agents/codebase-analyzer.md" && grep -qF "model: sonnet" ".claude/agents/codebase-locator.md" && grep -qF "model: sonnet" ".claude/agents/codebase-pattern-finder.md" && grep -qF "model: sonnet" ".claude/agents/thoughts-analyzer.md" && grep -qF "model: sonnet" ".claude/agents/thoughts-locator.md" && grep -qF "model: sonnet" ".claude/agents/web-search-researcher.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/codebase-analyzer.md b/.claude/agents/codebase-analyzer.md
@@ -2,7 +2,7 @@
 name: codebase-analyzer
 description: Analyzes codebase implementation details. Call the codebase-analyzer agent when you need to find detailed information about specific components. As always, the more detailed your request prompt, the better! :)
 tools: Read, Grep, Glob, LS
-model: inherit
+model: sonnet
 ---
 
 You are a specialist at understanding HOW code works. Your job is to analyze implementation details, trace data flow, and explain technical workings with precise file:line references.
diff --git a/.claude/agents/codebase-locator.md b/.claude/agents/codebase-locator.md
@@ -2,7 +2,7 @@
 name: codebase-locator
 description: Locates files, directories, and components relevant to a feature or task. Call `codebase-locator` with human language prompt describing what you're looking for. Basically a "Super Grep/Glob/LS tool" — Use it if you find yourself desiring to use one of these tools more than once.
 tools: Grep, Glob, LS
-model: inherit
+model: sonnet
 ---
 
 You are a specialist at finding WHERE code lives in a codebase. Your job is to locate relevant files and organize them by purpose, NOT to analyze their contents.
diff --git a/.claude/agents/codebase-pattern-finder.md b/.claude/agents/codebase-pattern-finder.md
@@ -2,7 +2,7 @@
 name: codebase-pattern-finder
 description: codebase-pattern-finder is a useful subagent_type for finding similar implementations, usage examples, or existing patterns that can be modeled after. It will give you concrete code examples based on what you're looking for! It's sorta like codebase-locator, but it will not only tell you the location of files, it will also give you code details!
 tools: Grep, Glob, Read, LS
-model: inherit
+model: sonnet
 ---
 
 You are a specialist at finding code patterns and examples in the codebase. Your job is to locate similar implementations that can serve as templates or inspiration for new work.
diff --git a/.claude/agents/thoughts-analyzer.md b/.claude/agents/thoughts-analyzer.md
@@ -2,7 +2,7 @@
 name: thoughts-analyzer
 description: The research equivalent of codebase-analyzer. Use this subagent_type when wanting to deep dive on a research topic. Not commonly needed otherwise.
 tools: Read, Grep, Glob, LS
-model: inherit
+model: sonnet
 ---
 
 You are a specialist at extracting HIGH-VALUE insights from thoughts documents. Your job is to deeply analyze documents and return only the most relevant, actionable information while filtering out noise.
diff --git a/.claude/agents/thoughts-locator.md b/.claude/agents/thoughts-locator.md
@@ -2,7 +2,7 @@
 name: thoughts-locator
 description: Discovers relevant documents in thoughts/ directory (We use this for all sorts of metadata storage!). This is really only relevant/needed when you're in a reseaching mood and need to figure out if we have random thoughts written down that are relevant to your current research task. Based on the name, I imagine you can guess this is the `thoughts` equivilent of `codebase-locator`
 tools: Grep, Glob, LS
-model: inherit
+model: sonnet
 ---
 
 You are a specialist at finding documents in the thoughts/ directory. Your job is to locate relevant thought documents and categorize them, NOT to analyze their contents in depth.
diff --git a/.claude/agents/web-search-researcher.md b/.claude/agents/web-search-researcher.md
@@ -3,7 +3,7 @@ name: web-search-researcher
 description: Do you find yourself desiring information that you don't quite feel well-trained (confident) on? Information that is modern and potentially only discoverable on the web? Use the web-search-researcher subagent_type today to find any and all answers to your questions! It will research deeply to figure out and attempt to answer your questions! If you aren't immediately satisfied you can get your money back! (Not really - but you can re-run web-search-researcher with an altered prompt in the event you're not satisfied the first time)
 tools: WebSearch, WebFetch, TodoWrite, Read, Grep, Glob, LS
 color: yellow
-model: inherit
+model: sonnet
 ---
 
 You are an expert web research specialist focused on finding accurate, relevant information from web sources. Your primary tools are WebSearch and WebFetch, which you use to discover and retrieve information based on user queries.
PATCH

echo "Gold patch applied."
