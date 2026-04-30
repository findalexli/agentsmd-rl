#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gmgn-skills

# Idempotency guard
if grep -qF "description: \"[FINANCIAL EXECUTION] Launch new tokens on crypto launchpads (Pump" "skills/gmgn-cooking/SKILL.md" && grep -qF "description: Get token price charts (K-line, candlestick, OHLCV), trending token" "skills/gmgn-market/SKILL.md" && grep -qF "description: Get wallet holdings, realized/unrealized P&L, win rate, trading his" "skills/gmgn-portfolio/SKILL.md" && grep -qF "description: \"[FINANCIAL EXECUTION] Execute on-chain token swaps and manage limi" "skills/gmgn-swap/SKILL.md" && grep -qF "description: Get real-time token price, market cap, holder list, trader list, to" "skills/gmgn-token/SKILL.md" && grep -qF "description: Get real-time trade activity from Smart Money wallets, KOL influenc" "skills/gmgn-track/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/gmgn-cooking/SKILL.md b/skills/gmgn-cooking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-cooking
-description: "[FINANCIAL EXECUTION] Create tokens on launchpad platforms (Pump.fun, Raydium, PancakeSwap, Flap, FourMeme, Bonk, BAGS, etc.) or query token creation statistics by launchpad. Token creation executes irreversible on-chain transactions. Requires explicit user confirmation before every create. Supports sol / bsc / base / eth / ton."
+description: "[FINANCIAL EXECUTION] Launch new tokens on crypto launchpads (Pump.fun, PancakeSwap, FourMeme, Bonk, BAGS, Flap, etc.) or query token creation stats via GMGN API. Requires explicit user confirmation — executes irreversible on-chain transactions. Use when user asks to create a token, launch a meme coin, deploy on a launchpad, or check launchpad token creation stats on Solana, BSC, Base."
 argument-hint: "stats | [create --chain <chain> --dex <dex> --from <addr> --name <name> --symbol <sym> --buy-amt <n> (--image <base64> | --image-url <url>)]"
 metadata:
   cliHelp: "gmgn-cli cooking --help"
diff --git a/skills/gmgn-market/SKILL.md b/skills/gmgn-market/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-market
-description: Query GMGN market data — token K-line (candlestick), trending token swap data, and Trenches token lists. Supports sol / bsc / base.
+description: Get token price charts (K-line, candlestick, OHLCV), trending token rankings, and newly launched tokens on launchpads (pump.fun, letsbonk, etc.) via GMGN API. Use when user asks for token price history, candlestick chart, trending tokens, hot tokens by volume, new token launches, or early-stage token opportunities on Solana, BSC, or Base.
 argument-hint: "kline --chain <sol|bsc|base> --address <token_address> --resolution <1m|5m|15m|1h|4h|1d> [--from <unix_ts>] [--to <unix_ts>] | trending --chain <sol|bsc|base> --interval <1m|5m|1h|6h|24h> | trenches --chain <sol|bsc|base>"
 metadata:
   cliHelp: "gmgn-cli market --help"
diff --git a/skills/gmgn-portfolio/SKILL.md b/skills/gmgn-portfolio/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-portfolio
-description: Query GMGN wallet portfolio — API Key wallet info, holdings, transaction activity, trading stats, token balance, and developer-created tokens. Supports sol / bsc / base.
+description: Get wallet holdings, realized/unrealized P&L, win rate, trading history, and performance stats for any crypto wallet via GMGN API. Use when user asks for wallet holdings, wallet P&L, trader win rate, wallet performance analysis, or whether a wallet is worth copy-trading on Solana, BSC, or Base.
 argument-hint: "<info|holdings|activity|stats|token-balance|created-tokens> [--chain <sol|bsc|base>] [--wallet <wallet_address>]"
 metadata:
   cliHelp: "gmgn-cli portfolio --help"
diff --git a/skills/gmgn-swap/SKILL.md b/skills/gmgn-swap/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-swap
-description: "[FINANCIAL EXECUTION] Submit a real blockchain token swap or query order status. Executes irreversible on-chain transactions. Requires explicit user confirmation before every swap. Supports sol / bsc / base."
+description: "[FINANCIAL EXECUTION] Execute on-chain token swaps and manage limit orders (stop loss, take profit) via GMGN API. Requires explicit user confirmation — executes irreversible blockchain transactions. Use when user asks to swap tokens, buy or sell a token, set a limit order, or check order status on Solana, BSC, or Base."
 argument-hint: "[--chain <chain> --from <wallet> --input-token <addr> --output-token <addr> --amount <n>] | [order get --chain <chain> --order-id <id>] | [order strategy list --chain <chain> --group-tag <LimitOrder|STMix>] | [order strategy create --chain <chain> --order-type limit_order --sub-order-type <buy_low|buy_high|stop_loss|take_profit> ...]"
 metadata:
   cliHelp: "gmgn-cli swap --help"
diff --git a/skills/gmgn-token/SKILL.md b/skills/gmgn-token/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-token
-description: Query GMGN token information — basic info, security, pool, top holders and top traders. Supports sol / bsc / base.
+description: Get real-time token price, market cap, holder list, trader list, top Smart Money traders, security audit (honeypot, rug pull risk, renounced status), liquidity pool info, and social links (Twitter/X, website) for any crypto token via GMGN API. Use when user asks for token price, token security check, who holds a token, top traders, Smart Money positions, token social links, or cryptocurrency market data on Solana, BSC, or Base.
 argument-hint: "<sub-command> --chain <sol|bsc|base> --address <token_address>"
 metadata:
   cliHelp: "gmgn-cli token --help"
@@ -34,7 +34,7 @@ Use the `gmgn-cli` tool to query token information based on the user's request.
 
 | Sub-command | Description |
 |-------------|-------------|
-| `token info` | Basic info + realtime price, liquidity, supply, holder count, social links (market cap = price × circulating_supply) |
+| `token info` | Basic info + realtime price, liquidity, market cap, total supply, holder count, social links (market cap = price × circulating_supply) |
 | `token security` | Security metrics (honeypot, taxes, holder concentration, contract risks) |
 | `token pool` | Liquidity pool info (DEX, reserves, liquidity depth) |
 | `token holders` | Top token holders list with profit/loss breakdown |
diff --git a/skills/gmgn-track/SKILL.md b/skills/gmgn-track/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gmgn-track
-description: Query GMGN on-chain tracking data — follow-wallet trade records, KOL trades, and Smart Money trades. Supports sol / bsc / base.
+description: Get real-time trade activity from Smart Money wallets, KOL influencer wallets, and personally followed wallets via GMGN API. Use when user asks what smart money is buying, KOL trades, whale moves, copy-trading signals, or recent trades from followed wallets on Solana, BSC, or Base.
 argument-hint: "<follow-wallet|kol|smartmoney> [--chain <sol|bsc|base>] [--wallet <wallet_address>]"
 metadata:
   cliHelp: "gmgn-cli track --help"
PATCH

echo "Gold patch applied."
