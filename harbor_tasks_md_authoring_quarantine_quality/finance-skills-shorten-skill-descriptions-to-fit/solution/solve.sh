#!/usr/bin/env bash
set -euo pipefail

cd /workspace/finance-skills

# Idempotency guard
if grep -qF "analyst targets, DCF, options chain/flow/unusual activity, GEX, IV rank, max pai" "skills/funda-data/SKILL.md" && grep -qF "Use when the user asks about correlated stocks, related companies, sector peers," "skills/stock-correlation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/funda-data/SKILL.md b/skills/funda-data/SKILL.md
@@ -1,25 +1,19 @@
 ---
 name: funda-data
 description: >
-  Fetch comprehensive financial data from the Funda AI API (https://api.funda.ai).
-  Covers real-time quotes, historical prices, financial statements, SEC filings, earnings transcripts,
-  analyst estimates, options flow/greeks/GEX, supply chain knowledge graph, social sentiment
-  (Twitter KOL posts, Reddit finance posts), prediction markets (Polymarket), congressional trades,
-  economic indicators, ESG ratings, news, insider/institutional ownership, and more.
-  Use this skill whenever the user asks for financial data that could come from the Funda API,
-  including: stock quotes, company fundamentals, balance sheet, income statement, cash flow,
-  analyst price targets, DCF valuation, options chain, options flow, unusual options activity,
-  GEX/gamma exposure, IV rank, max pain, earnings calendar, dividend calendar, IPO calendar,
-  SEC filings (10-K, 10-Q, 8-K), earnings call transcripts, podcast transcripts,
-  supply chain relationships, suppliers, customers, competitors, bottleneck stocks,
-  congressional/government trading, insider trades, institutional holdings (13F),
-  Reddit sentiment (wallstreetbets, stocks), financial Twitter/KOL tweets,
-  Polymarket prediction markets, treasury rates, GDP, CPI, unemployment, FRED data,
-  ESG scores, commodity prices, forex rates, crypto prices, stock screener,
-  market performance (sector/industry gainers/losers), ETF/fund holdings,
-  news and press releases, COT reports, or crowdfunding data.
-  Also triggers when the user mentions "funda", "funda.ai", or "funda API".
-  Always use this skill even if the user only provides a ticker — if Funda API can answer it, use it.
+  Fetch financial data from the Funda AI API (https://api.funda.ai).
+  Covers quotes, historical prices, financials, SEC filings, earnings transcripts,
+  analyst estimates, options flow/greeks/GEX, supply chain graph, social sentiment,
+  prediction markets, congressional trades, economic indicators, ESG, and news.
+  Triggers: stock quotes, fundamentals, balance sheet, income statement, cash flow,
+  analyst targets, DCF, options chain/flow/unusual activity, GEX, IV rank, max pain,
+  earnings/dividend/IPO calendar, SEC filings (10-K/10-Q/8-K), transcripts,
+  supply chain (suppliers/customers/competitors), congressional trading,
+  insider trades, institutional holdings (13F), Reddit/Twitter sentiment,
+  Polymarket, treasury rates, GDP, CPI, FRED data, ESG scores,
+  commodity/forex/crypto prices, stock screener, sector performance,
+  ETF holdings, news, COT reports. Also triggers for "funda" or "funda.ai".
+  If only a ticker is provided and Funda API can answer, use this skill.
 ---
 
 # Funda Data API Skill
diff --git a/skills/stock-correlation/SKILL.md b/skills/stock-correlation/SKILL.md
@@ -2,21 +2,18 @@
 name: stock-correlation
 description: >
   Analyze stock correlations to find related companies and trading pairs.
-  Use this skill whenever the user asks about correlated stocks, related companies,
-  sector peers, trading pairs, or how two or more stocks move together.
-  Triggers include: "what correlates with NVDA", "find stocks related to AMD",
+  Use when the user asks about correlated stocks, related companies, sector peers,
+  trading pairs, or how two or more stocks move together.
+  Triggers: "what correlates with NVDA", "find stocks related to AMD",
   "correlation between AAPL and MSFT", "what moves with", "sector peers",
   "pair trading", "correlated stocks", "when NVDA drops what else drops",
-  "find me a pair for", "stocks that move together", "beta to", "relative performance",
-  "which stocks follow AMD", "supply chain partners", "correlation matrix",
-  "co-movement", "related tickers", "sympathy plays", "if GOOGL moves what else moves",
-  "semiconductor peers", "compare correlation", "hedging pair",
-  "sector clustering", "realized correlation", "rolling correlation",
-  or any request about finding stocks that move in tandem or inversely.
-  Also triggers when the user mentions well-known pairs like AMD/NVDA, GOOGL/AVGO, LITE/COHR
-  and wants to understand or find similar relationships.
-  Always use this skill even if the user only provides one ticker — infer that they want
-  to find correlated peers.
+  "stocks that move together", "beta to", "relative performance",
+  "supply chain partners", "correlation matrix", "co-movement",
+  "related tickers", "sympathy plays", "semiconductor peers",
+  "hedging pair", "realized correlation", "rolling correlation",
+  or any request about stocks that move in tandem or inversely.
+  Also triggers for well-known pairs like AMD/NVDA, GOOGL/AVGO, LITE/COHR.
+  If only one ticker is provided, infer the user wants correlated peers.
 ---
 
 # Stock Correlation Analysis Skill
PATCH

echo "Gold patch applied."
