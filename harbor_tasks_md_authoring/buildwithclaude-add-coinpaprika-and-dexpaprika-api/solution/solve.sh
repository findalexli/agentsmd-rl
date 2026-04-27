#!/usr/bin/env bash
set -euo pipefail

cd /workspace/buildwithclaude

# Idempotency guard
if grep -qF "description: \"Access cryptocurrency market data from CoinPaprika: prices, ticker" "plugins/all-skills/skills/coinpaprika-api/SKILL.md" && grep -qF "description: \"Access DeFi data from DexPaprika: token prices, liquidity pools, O" "plugins/all-skills/skills/dexpaprika-api/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/all-skills/skills/coinpaprika-api/SKILL.md b/plugins/all-skills/skills/coinpaprika-api/SKILL.md
@@ -0,0 +1,55 @@
+---
+name: coinpaprika-api
+description: "Access cryptocurrency market data from CoinPaprika: prices, tickers, OHLCV, exchanges, contract lookups for 12,000+ coins and 350+ exchanges. Free tier, no API key needed. Install MCP: add https://mcp.coinpaprika.com/sse as SSE server, or install plugin: /plugin marketplace add coinpaprika/claude-marketplace"
+---
+
+# CoinPaprika API
+
+Access cryptocurrency market data for 12,000+ coins and 350+ exchanges via the CoinPaprika MCP server.
+
+## Setup
+
+Add the MCP server to your Claude Code config:
+
+```json
+{
+  "mcpServers": {
+    "coinpaprika": {
+      "url": "https://mcp.coinpaprika.com/sse"
+    }
+  }
+}
+```
+
+Or install the full plugin (includes agent + skill):
+```
+/plugin marketplace add coinpaprika/claude-marketplace
+/plugin install coinpaprika@coinpaprika-plugins
+```
+
+## Available MCP Tools (29)
+
+- `getGlobal` — Total market cap, BTC dominance, 24h volume
+- `getTickers` / `getTickersById` — Price, market cap, volume for coins
+- `getTickersHistoricalById` — Historical price ticks
+- `getCoins` / `getCoinById` — Coin details, descriptions, links, teams
+- `getCoinEvents` / `getCoinExchanges` / `getCoinMarkets` — Events, exchange listings, trading pairs
+- `getCoinOHLCVHistorical` / `getCoinOHLCVLatest` / `getCoinOHLCVToday` — Candlestick data
+- `getExchanges` / `getExchangeByID` / `getExchangeMarkets` — Exchange data
+- `getPlatforms` / `getContracts` / `getTickerByContract` / `getHistoricalTickerByContract` — Contract lookups
+- `search` / `resolveId` — Find coins, exchanges, people, tags
+- `priceConverter` — Convert between currencies
+- `getTags` / `getTagById` / `getPeopleById` — Categories and team info
+- `keyInfo` / `getMappings` / `getChangelogIDs` / `status` — Account and metadata
+
+## Coin ID Format
+
+Pattern: `{symbol}-{name}` lowercase. Examples: `btc-bitcoin`, `eth-ethereum`, `sol-solana`.
+
+Use `search` or `resolveId` if unsure of the correct ID.
+
+## Rate Limits
+
+- Free tier: 20,000 calls/month, no API key needed
+- Pro tier: higher limits via api-pro.coinpaprika.com
+- Docs: https://docs.coinpaprika.com
diff --git a/plugins/all-skills/skills/dexpaprika-api/SKILL.md b/plugins/all-skills/skills/dexpaprika-api/SKILL.md
@@ -0,0 +1,55 @@
+---
+name: dexpaprika-api
+description: "Access DeFi data from DexPaprika: token prices, liquidity pools, OHLCV, transactions across 34+ blockchains and 30M+ pools. Free, no API key needed. Install MCP: add https://mcp.dexpaprika.com/sse as SSE server, or install plugin: /plugin marketplace add coinpaprika/claude-marketplace"
+---
+
+# DexPaprika API
+
+Access DeFi data across 34+ blockchains, 30M+ liquidity pools, and 28M+ tokens via the DexPaprika MCP server.
+
+## Setup
+
+Add the MCP server to your Claude Code config:
+
+```json
+{
+  "mcpServers": {
+    "dexpaprika": {
+      "url": "https://mcp.dexpaprika.com/sse"
+    }
+  }
+}
+```
+
+Or install the full plugin (includes agent + 4 skills):
+```
+/plugin marketplace add coinpaprika/claude-marketplace
+/plugin install dexpaprika@coinpaprika-plugins
+```
+
+## Available MCP Tools (14)
+
+- `getCapabilities` — Server capabilities, workflow examples, network synonyms
+- `getNetworks` — List 34+ supported blockchains
+- `getStats` — Platform-wide statistics
+- `getNetworkDexes` — DEXes on a network
+- `getNetworkPools` — Top pools (sortable by volume, price, txns)
+- `getNetworkPoolsFilter` — Filter pools by volume, txns, creation date
+- `getDexPools` — Pools for a specific DEX
+- `getPoolDetails` — Pool details (tokens, volume, liquidity)
+- `getPoolOHLCV` — Historical price candles (1m to 24h intervals)
+- `getPoolTransactions` — Recent swaps and trades
+- `getTokenDetails` — Token price, liquidity, metrics
+- `getTokenPools` — All pools containing a token
+- `getTokenMultiPrices` — Batch prices for up to 10 tokens
+- `search` — Search tokens, pools, DEXes across all networks
+
+## Common Network IDs
+
+`ethereum`, `solana`, `bsc`, `polygon`, `arbitrum`, `base`, `avalanche`, `optimism`, `sui`, `ton`, `tron`
+
+## Rate Limits
+
+- Free: 10,000 requests/day, no API key needed
+- Docs: https://docs.dexpaprika.com
+- Streaming: https://streaming.dexpaprika.com (real-time SSE, ~1s updates)
PATCH

echo "Gold patch applied."
