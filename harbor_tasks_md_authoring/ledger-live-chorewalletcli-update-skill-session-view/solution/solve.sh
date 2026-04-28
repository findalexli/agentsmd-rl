#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "> **Session first:** When invoked without a specific task, **immediately run `se" ".agents/skills/ledger-wallet-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/ledger-wallet-cli/SKILL.md b/.agents/skills/ledger-wallet-cli/SKILL.md
@@ -3,196 +3,101 @@ name: ledger-wallet-cli
 description: Official Ledger wallet-cli — USB-based CLI for Ledger hardware wallet flows (account discover, receive, balances, operations, send) built on the Device Management Kit (DMK)
 ---
 
-# wallet-cli usage guide
+# wallet-cli
 
-`wallet-cli` is an experimental USB-based CLI for Ledger wallet flows, built on the Device Management Kit (DMK). Supported networks: **bitcoin**, **ethereum**, **base**, **solana** (mainnet and testnets). On Ledger devices, **Base uses the Ethereum app**.
+USB-based CLI for Ledger wallet flows. Networks: **bitcoin**, **ethereum**, **base**, **solana** (mainnet + testnets). Base uses the Ethereum app.
 
-> **Device contention:** Only one command can use the device at a time. Never run two device-required commands in parallel — they will conflict and fail with `[object Object]` or a garbled APDU error. Run device commands sequentially.
+Run from repo root: `pnpm --silent wallet-cli start <command> [flags]`
 
-**Prerequisites:** Ledger device connected via USB, with the relevant coin app open on device for commands that require it (**Base requires opening the Ethereum app**).
+> **Session first:** When invoked without a specific task, **immediately run `session view`** — do not ask the user what to do first. Show the result, then ask what to do next. If labels exist, skip `account discover`.
 
-**Run from repo root:**
+> **Sandbox:** `account discover`, `receive`, `send` **must** use `dangerouslyDisableSandbox: true` — sandbox blocks USB (causes `Timeout has occurred`). Other commands are fine in sandbox.
 
-```bash
-pnpm --silent wallet-cli start <command> [flags]
-```
-
-> **Sandbox:** Commands that open the USB device (`account discover`, `receive`, `send`) **must** be run with `dangerouslyDisableSandbox: true` in the Bash tool — the sandbox blocks USB access and causes a `Timeout has occurred` error. Commands that don't need the device (`balances`, `operations`, `send --dry-run`) work fine in the sandbox.
-
----
-
-## Commands at a glance
-
-| Command            | Device required                   | Disable sandbox              |
-| ------------------ | --------------------------------- | ---------------------------- |
-| `account discover` | Yes                               | **Yes**                      |
-| `receive`          | Yes (optional with `--no-verify`) | **Yes**                      |
-| `send`             | Yes (unless `--dry-run`)          | **Yes** (unless `--dry-run`) |
-| `balances`         | No                                | No                           |
-| `operations`       | No                                | No                           |
+> **Device contention:** Never run two device commands in parallel — they fail with `[object Object]` or garbled APDU. Run sequentially.
 
 ---
 
-## Account descriptor format (V1)
+## Commands
 
-`account discover` outputs **V1 descriptors**:
+| Command            | Device | Sandbox      |
+| ------------------ | ------ | ------------ |
+| `session view`     | No     | No           |
+| `session reset`    | No     | No           |
+| `account discover` | Yes    | **Required** |
+| `receive`          | Yes    | **Required** |
+| `send`             | Yes*   | **Required** |
+| `balances`         | No     | No           |
+| `operations`       | No     | No           |
 
-```
-account:1:<type>:<network>:<env>:<xpub_or_address>:<path>
-```
+*`send --dry-run` needs no device and no sandbox bypass.
 
-Hardened segments use `h` (shell-safe). `'` is also accepted for backward compatibility.
+---
 
-Examples:
+## Session & labels
 
-```
-account:1:utxo:bitcoin:main:xpub6BosfCn...:m/84h/0h/0h
-account:1:address:ethereum:main:0x71C7656EC7ab88b098defB751B7401B5f6d8976F:m/44h/60h/0h/0/0
-account:1:address:solana:main:7xCU4XQfL...:m/44h/501h/0h/0h
-account:1:utxo:bitcoin:testnet:tpubD8Lg2g...:m/84h/1h/0h
-```
+`account discover` persists accounts. Each gets a label: `<network>[-derivation][-env]-<n>` (e.g. `ethereum-1`, `bitcoin-native-1`, `ethereum-goerli-2`).
 
-All commands (`balances`, `operations`, `receive`, `send`) accept V1 descriptors as `--account` or first positional arg. Legacy V0 (`js:2:bitcoin:xpub...:native_segwit:0`) still accepted.
+All `--account` flags accept a label or a full descriptor.
 
 ---
 
-## Typical flow
+## Commands
 
-### 1. Discover accounts — requires device
+### session view / reset
+```bash
+pnpm --silent wallet-cli start session view
+pnpm --silent wallet-cli start session reset
+```
 
+### account discover
 ```bash
-pnpm --silent wallet-cli start account discover bitcoin
 pnpm --silent wallet-cli start account discover ethereum
-pnpm --silent wallet-cli start account discover base
+pnpm --silent wallet-cli start account discover bitcoin
 pnpm --silent wallet-cli start account discover ethereum:sepolia
-pnpm --silent wallet-cli start account discover bitcoin --output json
 ```
+Networks: `bitcoin` (mainnet), `base`, `ethereum:sepolia`, `bitcoin:testnet`, `solana:devnet`.
 
-Network forms: `bitcoin` (= mainnet), `ethereum:mainnet` (alias → `main`), `base`, `ethereum:sepolia`, `bitcoin:testnet` (env → `testnet`), `solana:devnet` (env → `devnet`).
-
-Human output: one account per line with fresh address and V1 descriptor to copy.
-JSON output: `{ "accounts": ["account:1:utxo:bitcoin:main:xpub...:m/84h/0h/0h", ...] }`
-
-### 2. Receive address — requires device
-
+### receive
 ```bash
-pnpm --silent wallet-cli start receive account:1:utxo:bitcoin:main:xpub...:m/84h/0h/0h
-pnpm --silent wallet-cli start receive account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0 --no-verify
+pnpm --silent wallet-cli start receive ethereum-1
+pnpm --silent wallet-cli start receive ethereum-1 --no-verify  # skip device confirmation
 ```
 
-Use `--no-verify` to skip device confirmation.
-
-### 3. Balances — no device required
-
+### balances
 ```bash
-pnpm --silent wallet-cli start balances account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0
-pnpm --silent wallet-cli start balances account:1:utxo:bitcoin:main:xpub...:m/84h/0h/0h --output json
+pnpm --silent wallet-cli start balances ethereum-1
+pnpm --silent wallet-cli start balances ethereum-1 --output json
 ```
 
-Fetches native balance and token balances (ERC-20). JSON amounts are human-readable strings (`"1.5 ETH"`, `"100 USDT"`).
-
-### 4. Operations — no device required
-
+### operations
 ```bash
-pnpm --silent wallet-cli start operations account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0
-pnpm --silent wallet-cli start operations <descriptor> --limit 20 --cursor <cursor>
-pnpm --silent wallet-cli start operations <descriptor> --output json
+pnpm --silent wallet-cli start operations ethereum-1
+pnpm --silent wallet-cli start operations ethereum-1 --limit 20 --cursor <cursor>
 ```
+Pagination: next cursor on stderr (human) or `nextCursor` in JSON.
 
-Lists transactions including internal operations (ETH contract call traces). Pagination: `--limit <n>` and `--cursor <cursor>`. Next cursor on stderr (human) or `nextCursor` in JSON.
-
-JSON: `value`/`fee` are human-readable ticker strings. `accountId` is the V1 descriptor string.
-
-### 5. Send — requires device (unless `--dry-run`)
-
+### send
 ```bash
-# Native ETH
-pnpm --silent wallet-cli start send account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0 \
-  --to 0xDEF... --amount '0.5 ETH'
-
-# ERC-20 token — ticker resolves the token automatically
-pnpm --silent wallet-cli start send account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0 \
-  --to 0xDEF... --amount '100 USDT'
-
-# Bitcoin with custom fee
-pnpm --silent wallet-cli start send account:1:utxo:bitcoin:main:xpub...:m/84h/0h/0h \
-  --to bc1q... --amount '0.001 BTC' --fee-per-byte 15 --rbf
-
-# Dry run — no device needed
-pnpm --silent wallet-cli start send account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0 \
-  --to 0xDEF... --amount '0.5 ETH' --dry-run
-```
-
-Ticker is **mandatory** in `--amount` (e.g. `'0.5 ETH'`, `'0.001 BTC'`). It drives asset resolution — no `--token` flag.
-
-`--dry-run`: prepares and validates without signing or broadcasting. No device opened.
-
----
-
-## Send flags
-
-### All families
-
-| Flag                          | Description                                                |
-| ----------------------------- | ---------------------------------------------------------- |
-| `--amount '<value> <TICKER>'` | Required. e.g. `'0.001 BTC'`, `'0.01 ETH'`, `'0.4 USDT'`   |
-| `--to <address>`              | Required. Recipient address                                |
-| `--dry-run`                   | Prepare and validate without signing or opening the device |
-| `--output json`               | Machine-readable JSON output                               |
-
-### Bitcoin only
-
-| Flag                        | Description                     |
-| --------------------------- | ------------------------------- |
-| `--fee-per-byte <satoshis>` | Custom fee per byte in satoshis |
-| `--rbf`                     | Enable Replace-By-Fee           |
-
-### Solana only
-
-| Flag                        | Description                                                                                             |
-| --------------------------- | ------------------------------------------------------------------------------------------------------- |
-| `--mode <mode>`             | `send`, `stake.createAccount`, `stake.delegate`, `stake.undelegate`, `stake.withdraw` (default: `send`) |
-| `--validator <address>`     | Validator address (staking flows)                                                                       |
-| `--stake-account <address>` | Stake account address (staking flows)                                                                   |
-| `--memo <text>`             | Memo/tag                                                                                                |
-
----
-
-## Output format
-
-All commands: `--output human` (default) or `--output json`.
-
-JSON envelope shape:
-
-```json
-{
-  "status": "success",
-  "command": "balances",
-  "network": "ethereum:main",
-  "account": "account:1:address:ethereum:main:0xABC...:m/44h/60h/0h/0/0",
-  "timestamp": "2026-04-03T12:00:00.000Z",
-  "...": "command-specific fields"
-}
+pnpm --silent wallet-cli start send ethereum-1 --to 0xDEF... --amount '0.5 ETH'
+pnpm --silent wallet-cli start send ethereum-1 --to 0xDEF... --amount '100 USDT'  # ERC-20
+pnpm --silent wallet-cli start send bitcoin-native-1 --to bc1q... --amount '0.001 BTC' --fee-per-byte 15 --rbf
+pnpm --silent wallet-cli start send ethereum-1 --to 0xDEF... --amount '0.5 ETH' --dry-run
 ```
 
-Command-specific payloads:
+Ticker is **mandatory** in `--amount`. No `--token` flag — ticker drives asset resolution.
 
-- `account discover`: `{ "accounts": ["account:1:...", ...] }`
-- `balances`: `{ "balances": [{ "asset": "ethereum", "amount": "1.5 ETH" }, ...] }`
-- `operations`: `{ "operations": [{ "accountId": "account:1:...", "value": "0.1 ETH", "fee": "...", ... }], "nextCursor": "..." }`
-- `send`: `{ "tx_hash": "0x...", "amount": "0.5 ETH", "fee": "0.0003 ETH" }`
-- `send --dry-run`: `{ "dry_run": true, "recipient": "0x...", "amount": "0.5 ETH", "fee": "0.0003 ETH" }`
+**Bitcoin flags:** `--fee-per-byte <sats>`, `--rbf`
 
-Error envelope: `{ "status": "error", "message": "...", ... }` — exit code non-zero.
+**Solana flags:** `--mode send|stake.createAccount|stake.delegate|stake.undelegate|stake.withdraw`, `--validator <addr>`, `--stake-account <addr>`, `--memo <text>`
 
 ---
 
 ## Common errors
 
-| Error                                                            | Cause                                     |
-| ---------------------------------------------------------------- | ----------------------------------------- |
-| `Amount must include a ticker, e.g. '0.5 ETH' or '0.001 BTC'`    | `--amount` given a bare number            |
-| `Ticker UNKN not found in account. Available: ETH, USDT, ...`    | Ticker not in account balances            |
-| `No currencyId mapping for network "x:y"`                        | Unsupported network/env combination       |
-| `UnknownDeviceExchangeError`                                     | Device not connected or coin app not open |
-| `[x] Transaction Cancelled: Rejected on device. No funds moved.` | User rejected on device                   |
+| Error | Cause |
+| ----- | ----- |
+| `Amount must include a ticker` | `--amount` missing ticker |
+| `Ticker UNKN not found in account` | ticker not in account balances |
+| `UnknownDeviceExchangeError` | device not connected or wrong app |
+| `Transaction Cancelled: Rejected on device` | user rejected on device |
+| `Timeout has occurred` | sandbox blocking USB — use `dangerouslyDisableSandbox: true` |
PATCH

echo "Gold patch applied."
