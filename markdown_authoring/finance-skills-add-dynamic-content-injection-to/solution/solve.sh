#!/usr/bin/env bash
set -euo pipefail

cd /workspace/finance-skills

# Idempotency guard
if grep -qF "Skills can embed shell commands that Claude Code executes at skill invocation ti" "CLAUDE.md" && grep -qF "!`(command -v discord && discord status 2>&1 | head -5 && echo \"AUTH_OK\" || echo" "skills/discord/SKILL.md" && grep -qF "!`python3 -c \"import yfinance as yf; print(f'SPX \u2248 {yf.Ticker(\\\"^GSPC\\\").fast_in" "skills/options-payoff/SKILL.md" && grep -qF "!`python3 -c \"import yfinance, pandas, numpy; print(f'yfinance={yfinance.__versi" "skills/stock-correlation/SKILL.md" && grep -qF "!`(tdl chat ls --limit 1 2>&1 >/dev/null && echo \"AUTH_OK\" || echo \"AUTH_NEEDED\"" "skills/telegram/SKILL.md" && grep -qF "!`(command -v twitter && twitter status --yaml 2>&1 | head -5 && echo \"AUTH_OK\" " "skills/twitter/SKILL.md" && grep -qF "!`python3 -c \"import yfinance; print('yfinance ' + yfinance.__version__ + ' inst" "skills/yfinance-data/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -66,6 +66,22 @@ Skills that require shell access, network calls, or external binaries (e.g., twi
 
 Skills that only use Claude's built-in tools (e.g., `show_widget` for generative-ui) work on **Claude.ai**.
 
+### Dynamic content with `!`command``
+
+Skills can embed shell commands that Claude Code executes at skill invocation time, injecting the output inline. Use this for runtime environment checks (tool installation status, auth state, live data). Syntax: wrap in a fenced code block with `` !`command` ``.
+
+Example — checking if a CLI tool is installed and authenticated:
+```
+!`(command -v mytool && mytool status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`
+```
+
+Guidelines:
+- Use for environment/auth checks so the model skips install/auth steps when unnecessary
+- Use for injecting live data (e.g., current stock prices) to replace hardcoded values
+- Keep commands fast (< 2s) — they run synchronously before the skill loads
+- Always include fallback output (e.g., `|| echo "UNAVAILABLE"`) so the skill degrades gracefully
+- Only works on CLI-based agents (Claude Code) — Claude.ai ignores these
+
 ### Instruction style guidelines
 
 - Organize as numbered steps (## Step 1, Step 2, etc.)
diff --git a/skills/discord/SKILL.md b/skills/discord/SKILL.md
@@ -25,17 +25,20 @@ Reads Discord for financial research using [discord-cli](https://github.com/jack
 
 ## Step 1: Ensure discord-cli Is Installed and Authenticated
 
-Before running any command, install and check auth:
+**Current environment status:**
+
+```
+!`(command -v discord && discord status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`
+```
+
+If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:
 
 ```bash
 # Install (requires Python 3.10+)
-command -v discord || uv tool install kabi-discord-cli
-
-# Check authentication
-discord status && echo "AUTH_OK" || echo "AUTH_NEEDED"
+uv tool install kabi-discord-cli
 ```
 
-If `AUTH_OK`, skip to Step 2. If `AUTH_NEEDED`, guide the user:
+If `AUTH_NEEDED`, guide the user:
 
 ### Authentication
 
diff --git a/skills/options-payoff/SKILL.md b/skills/options-payoff/SKILL.md
@@ -38,7 +38,12 @@ When the user provides a screenshot or text, extract:
 | IV | Shown in greeks panel, or estimate from vega | 20% |
 | Risk-free rate | — | 4.3% |
 
-**Critical for screenshots**: The spot price is the CURRENT price of the underlying index/stock, NOT the strikes. For SPX, check market data — as of March 2026 SPX ≈ 5,500. Never default spot to a strike price value.
+**Critical for screenshots**: The spot price is the CURRENT price of the underlying index/stock, NOT the strikes. Never default spot to a strike price value.
+
+**Current SPX reference price:**
+```
+!`python3 -c "import yfinance as yf; print(f'SPX ≈ {yf.Ticker(\"^GSPC\").fast_info[\"lastPrice\"]:.0f}')" 2>/dev/null || echo "SPX price unavailable — check market data"`
+```
 
 ---
 
diff --git a/skills/stock-correlation/SKILL.md b/skills/stock-correlation/SKILL.md
@@ -29,14 +29,20 @@ Finds and analyzes correlated stocks using historical price data from Yahoo Fina
 
 ## Step 1: Ensure Dependencies Are Available
 
-Before running any code, install required packages if needed:
+**Current environment status:**
+
+```
+!`python3 -c "import yfinance, pandas, numpy; print(f'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}')" 2>/dev/null || echo "DEPS_MISSING"`
+```
+
+If `DEPS_MISSING`, install required packages before running any code:
 
 ```python
 import subprocess, sys
 subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance", "pandas", "numpy"])
 ```
 
-Always include this at the top of your script.
+If all dependencies are already installed, skip the install step and proceed directly.
 
 ---
 
diff --git a/skills/telegram/SKILL.md b/skills/telegram/SKILL.md
@@ -22,11 +22,13 @@ Reads Telegram channels and groups for financial news and market research using
 
 ## Step 1: Ensure tdl Is Installed
 
-Before running any command, check if tdl is installed:
+**Current environment status:**
 
-```bash
-command -v tdl && tdl version || echo "TDL_NOT_INSTALLED"
 ```
+!`(command -v tdl && tdl version 2>&1 | head -3 || echo "TDL_NOT_INSTALLED") 2>/dev/null`
+```
+
+If the status above shows a version number, tdl is installed — skip to Step 2.
 
 If `TDL_NOT_INSTALLED`, install tdl based on the user's platform:
 
@@ -45,10 +47,10 @@ Ask the user which installation method they prefer. Default to Homebrew on macOS
 
 ## Step 2: Ensure tdl Is Authenticated
 
-Check if the user is logged in:
+**Current auth status:**
 
-```bash
-tdl chat ls --limit 1 2>&1 && echo "AUTH_OK" || echo "AUTH_NEEDED"
+```
+!`(tdl chat ls --limit 1 2>&1 >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null`
 ```
 
 If `AUTH_OK`, skip to Step 3.
diff --git a/skills/twitter/SKILL.md b/skills/twitter/SKILL.md
@@ -23,17 +23,20 @@ Reads Twitter/X for financial research using [twitter-cli](https://github.com/ja
 
 ## Step 1: Ensure twitter-cli Is Installed and Authenticated
 
-Before running any command, install and check auth:
+**Current environment status:**
+
+```
+!`(command -v twitter && twitter status --yaml 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`
+```
+
+If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:
 
 ```bash
 # Install (requires Python 3.10+)
-command -v twitter || uv tool install twitter-cli
-
-# Check authentication
-twitter status --yaml >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED"
+uv tool install twitter-cli
 ```
 
-If `AUTH_OK`, skip to Step 2. If `AUTH_NEEDED`, guide the user:
+If `AUTH_NEEDED`, guide the user:
 
 ### Authentication methods
 
diff --git a/skills/yfinance-data/SKILL.md b/skills/yfinance-data/SKILL.md
@@ -22,14 +22,20 @@ Fetches financial and market data from Yahoo Finance using the [yfinance](https:
 
 ## Step 1: Ensure yfinance Is Available
 
-Before running any code, install yfinance if needed:
+**Current environment status:**
+
+```
+!`python3 -c "import yfinance; print('yfinance ' + yfinance.__version__ + ' installed')" 2>/dev/null || echo "YFINANCE_NOT_INSTALLED"`
+```
+
+If `YFINANCE_NOT_INSTALLED`, install it before running any code:
 
 ```python
 import subprocess, sys
 subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
 ```
 
-Always include this at the top of your script.
+If yfinance is already installed, skip the install step and proceed directly.
 
 ---
 
PATCH

echo "Gold patch applied."
