#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opc-skills

# Idempotency guard
if grep -qF "description: Generate user demand research reports from real user feedback. Scra" "skills/requesthunt/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/requesthunt/SKILL.md b/skills/requesthunt/SKILL.md
@@ -1,11 +1,11 @@
 ---
 name: requesthunt
-description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, GitHub, YouTube, and LinkedIn. Use when user wants to do demand research, find feature requests, analyze user demand, or run RequestHunt queries.
+description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, GitHub, YouTube, LinkedIn, and Amazon. Use when user wants to do demand research, find feature requests, analyze user demand, or run RequestHunt queries.
 ---
 
 # RequestHunt Skill
 
-Generate user demand research reports by collecting and analyzing real user feedback from Reddit, X (Twitter), GitHub, YouTube, and LinkedIn.
+Generate user demand research reports by collecting and analyzing real user feedback from Reddit, X (Twitter), GitHub, YouTube, LinkedIn, and Amazon.
 
 ## Prerequisites
 
@@ -55,28 +55,31 @@ Each platform captures different types of user feedback. Choose platforms based
 | **LinkedIn** | B2B software, healthcare, enterprise tools | Professional/industry opinions, market context | Low volume but high engagement |
 | **X** | Trending topics, quick sentiment signals | Fragmented feedback, emotional reactions | Low-medium (1-6 per topic) |
 | **GitHub** | Open-source tools, developer infrastructure | Concrete bugs and feature requests from issues | High for OSS, zero for non-tech |
+| **Amazon** | Consumer products, electronics, home goods | Product review complaints and feature wishes | High for physical products |
 
 ### Recommended Platforms by Category
 
 | Category | Primary | Secondary | Notes |
 |----------|---------|-----------|-------|
-| **Automotive / Hardware** | YouTube | Reddit | Video review comments are the richest source (dashcams: 29, EVs: 19) |
-| **Gaming / Entertainment** | YouTube | Reddit | Game streams and reviews generate natural feedback |
-| **Travel / Transportation** | YouTube | LinkedIn | Travel vlogs + LinkedIn for business travel needs |
+| **Automotive / Hardware** | YouTube | Amazon, Reddit | Video review comments + Amazon product reviews are richest sources |
+| **Gaming / Entertainment** | YouTube | Amazon, Reddit | Game streams, product reviews, and community feedback |
+| **Travel / Transportation** | YouTube | Amazon, LinkedIn | Travel vlogs + Amazon gear reviews + business travel needs |
 | **Social / Communication** | YouTube | Reddit | App review videos + community discussions |
-| **Food / Dining** | YouTube | Reddit | Recipe and delivery app review comments |
-| **Real Estate / Home** | YouTube | X | Interior design and renovation videos dominate |
-| **Education / Learning** | YouTube | — | Tutorial video comments are the only reliable source |
-| **Health / Medical** | LinkedIn | X | Rare LinkedIn-dominant category (professional healthcare) |
+| **Food / Dining** | YouTube | Amazon, Reddit | Recipe/delivery app reviews + Amazon kitchen product feedback |
+| **Real Estate / Home** | Amazon | YouTube, Reddit | Amazon dominates for home improvement and smart home products |
+| **Education / Learning** | YouTube | Amazon | Tutorial video comments + Amazon course/book reviews |
+| **Health / Medical** | LinkedIn | Amazon, X | Professional healthcare + Amazon health product reviews |
 | **Creator Economy** | Reddit | GitHub | Reddit communities overwhelmingly active (Newsletter: 176 requests) |
 | **Developer Tools** | Reddit | GitHub | Technical communities + open-source issue trackers |
 | **AI / SaaS Products** | Reddit | LinkedIn | Reddit for user complaints, LinkedIn for industry analysis |
+| **Consumer Electronics** | Amazon | YouTube, Reddit | Amazon product reviews are the primary signal source |
 
 ### Quick Selection Rules
 
-- **Consumer / hardware / lifestyle** → YouTube first, Reddit second
+- **Consumer / hardware / lifestyle** → Amazon + YouTube first, Reddit second
 - **Developer / creator tools** → Reddit first, GitHub second
 - **B2B / enterprise / medical** → LinkedIn first, X second
+- **Physical products / electronics** → Amazon first, YouTube second
 - **Has open-source projects** → add GitHub
 - **Everything** → add X as a supplementary source
 
@@ -105,8 +108,11 @@ requesthunt scrape start "code editors" --platforms reddit,github --depth 2
 # B2B / enterprise — LinkedIn-first strategy
 requesthunt scrape start "electronic health records" --platforms linkedin,x --depth 2
 
+# Consumer products — Amazon-first strategy
+requesthunt scrape start "wireless earbuds" --platforms amazon,youtube,reddit --depth 2
+
 # Broad research — all platforms
-requesthunt scrape start "AI coding assistants" --platforms reddit,x,github,youtube,linkedin --depth 2
+requesthunt scrape start "AI coding assistants" --platforms reddit,x,github,youtube,linkedin,amazon --depth 2
 
 # Search with expansion for more data
 requesthunt search "dark mode" --expand --limit 50
@@ -124,7 +130,7 @@ Analyze collected data and generate a structured Markdown report:
 
 ## Overview
 - Scope: ...
-- Data Sources: Reddit (N), X (N), GitHub (N), YouTube (N), LinkedIn (N)
+- Data Sources: Reddit (N), X (N), GitHub (N), YouTube (N), LinkedIn (N), Amazon (N)
 - Platform Strategy: [why these platforms were chosen for this category]
 - Time Range: ...
 
@@ -139,10 +145,10 @@ Analyze collected data and generate a structured Markdown report:
 - Sources: [which platforms surfaced this]
 
 ### 3. Platform Signal Comparison
-| Insight | Reddit | YouTube | LinkedIn | X | GitHub |
-|---------|--------|---------|----------|---|--------|
-| Volume | ... | ... | ... | ... | ... |
-| Signal type | Technical | UX/Feature | Strategic | Sentiment | Bug/FR |
+| Insight | Reddit | YouTube | LinkedIn | X | GitHub | Amazon |
+|---------|--------|---------|----------|---|--------|--------|
+| Volume | ... | ... | ... | ... | ... | ... |
+| Signal type | Technical | UX/Feature | Strategic | Sentiment | Bug/FR | Product |
 
 ### 4. Competitive Comparison (if specified)
 | Feature | Product A | Product B | User Expectations |
@@ -184,7 +190,7 @@ requesthunt list --sort top --limit 20                       # Top voted
 ### Scrape
 ```bash
 requesthunt scrape start "developer-tools" --depth 1         # Default: all platforms
-requesthunt scrape start "ai-assistant" --platforms reddit,x,github,youtube,linkedin --depth 2
+requesthunt scrape start "ai-assistant" --platforms reddit,x,github,youtube,linkedin,amazon --depth 2
 requesthunt scrape status "job_123"                          # Check job status
 ```
 
@@ -203,6 +209,6 @@ requesthunt config show                                      # Check auth status
   - Pro tier: 2,000 credits/month, 60 req/min
 - **Costs**:
   - API call: 1 credit
-  - Scrape: depth x number of platforms credits
+  - Scrape: depth x number of platforms credits (Amazon capped at depth 5)
 - **Docs**: https://requesthunt.com/docs
 - **Agent Setup**: https://requesthunt.com/setup.md
PATCH

echo "Gold patch applied."
