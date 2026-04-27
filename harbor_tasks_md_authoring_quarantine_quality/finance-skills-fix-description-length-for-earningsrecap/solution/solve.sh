#!/usr/bin/env bash
set -euo pipefail

cd /workspace/finance-skills

# Idempotency guard
if grep -qF "Triggers: \"AAPL earnings recap\", \"how did TSLA earnings go\", \"MSFT earnings resu" "skills/earnings-recap/SKILL.md" && grep -qF "how EPS or revenue forecasts changed over time, compare estimate distributions," "skills/estimate-analysis/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/earnings-recap/SKILL.md b/skills/earnings-recap/SKILL.md
@@ -2,19 +2,16 @@
 name: earnings-recap
 description: >
   Generate a post-earnings analysis for any stock using Yahoo Finance data.
-  Use this skill whenever the user wants to review what happened after a company reported earnings,
-  understand the beat/miss result, see how the stock reacted, or get a quick recap of recent earnings.
-  Triggers include: "AAPL earnings recap", "how did TSLA earnings go", "MSFT earnings results",
-  "did NVDA beat earnings", "earnings recap", "post-earnings analysis",
-  "earnings surprise", "what happened with GOOGL earnings",
-  "earnings reaction", "stock moved after earnings", "earnings report summary",
-  "EPS beat or miss", "revenue beat or miss", "after earnings",
-  "earnings results", "quarterly results for", "how were earnings",
-  "AMZN reported last night", "earnings call recap",
-  any mention of reviewing or summarizing earnings that already happened,
-  or any request about a company's most recent earnings outcome.
-  Always use this skill when the user references a past earnings event,
-  even if they just say something like "AAPL reported" or "how did they do".
+  Use when the user wants to review what happened after earnings,
+  understand beat/miss results, see stock reaction, or get an earnings recap.
+  Triggers: "AAPL earnings recap", "how did TSLA earnings go", "MSFT earnings results",
+  "did NVDA beat earnings", "post-earnings analysis", "earnings surprise",
+  "what happened with GOOGL earnings", "earnings reaction",
+  "stock moved after earnings", "EPS beat or miss", "revenue beat or miss",
+  "quarterly results for", "how were earnings", "AMZN reported last night",
+  "earnings call recap", or any request about a company's recent earnings outcome.
+  Use this skill when the user references a past earnings event,
+  even if they just say "AAPL reported" or "how did they do".
 ---
 
 # Earnings Recap Skill
diff --git a/skills/estimate-analysis/SKILL.md b/skills/estimate-analysis/SKILL.md
@@ -2,23 +2,19 @@
 name: estimate-analysis
 description: >
   Deep-dive into analyst estimates and revision trends for any stock using Yahoo Finance data.
-  Use this skill whenever the user wants to understand the direction of analyst estimates,
-  how EPS or revenue forecasts have changed over time, compare estimate distributions,
+  Use when the user wants to understand analyst estimate direction,
+  how EPS or revenue forecasts changed over time, compare estimate distributions,
   or analyze growth projections across periods.
-  Triggers include: "estimate analysis for AAPL", "analyst estimate trends for NVDA",
+  Triggers: "estimate analysis for AAPL", "analyst estimate trends for NVDA",
   "EPS revisions for TSLA", "how have estimates changed for MSFT",
   "estimate revisions", "EPS trend", "revenue estimates",
   "consensus changes", "analyst estimates", "estimate distribution",
-  "growth estimates for", "how many analysts cover",
-  "are estimates going up or down", "estimate momentum",
-  "revision trend", "earnings estimate history",
-  "forward estimates", "next quarter estimates",
-  "annual estimates", "FY estimates", "estimate spread",
-  "bull case vs bear case estimates", "estimate range",
-  any mention of analyzing, tracking, or comparing analyst estimates/revisions,
-  or any request about understanding where analyst forecasts are heading.
-  Always use this skill when the user asks about estimates beyond a simple lookup —
-  if they want context, trends, or analysis of the numbers, this is the right skill.
+  "growth estimates for", "estimate momentum", "revision trend",
+  "forward estimates", "next quarter estimates", "annual estimates",
+  "estimate spread", "bull vs bear estimates", "estimate range",
+  or any request about tracking or comparing analyst estimates/revisions.
+  Use this skill when the user asks about estimates beyond a simple lookup —
+  if they want context, trends, or analysis, this is the right skill.
 ---
 
 # Estimate Analysis Skill
PATCH

echo "Gold patch applied."
