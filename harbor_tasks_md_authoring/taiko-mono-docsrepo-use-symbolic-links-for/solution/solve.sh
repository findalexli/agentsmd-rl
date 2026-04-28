#!/usr/bin/env bash
set -euo pipefail

cd /workspace/taiko-mono

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "Agents.md" "Agents.md" && grep -qF "packages/protocol/AGENTS.md" "packages/protocol/AGENTS.md" && grep -qF "packages/protocol/Agents.md" "packages/protocol/Agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/Agents.md b/Agents.md
@@ -1,58 +0,0 @@
-# agents.md — Root (Monorepo Guide for Coding Agents)
-
-> **Canonical brief for this repository.** Agents should also read `/packages/protocol/agents.md` when editing smart contracts. Keep responses terse, deterministic, and actionable. Always include exact file paths and runnable commands.
-
-## Project Snapshot
-
-- **Domain**: Based rollup on Ethereum (Type‑1 ZK‑EVM)
-- **Key traits**: L1‑sequenced; SGX + ZK multi‑proofs; contestable validity proofs with bonding; Ethereum‑equivalent semantics
-- **Workspace**: `pnpm` monorepo
-
-```
-packages/
-├─ protocol/          # Solidity + Foundry (core contracts)
-├─ taiko-client/      # Go (driver, proposer, prover)
-├─ bridge-ui/         # TS/SvelteKit
-├─ relayer/           # Go bridge relayer
-├─ eventindexer/      # Go indexer
-└─ ...
-```
-
-## Top‑Level Commands (run at repo root)
-
-```bash
-pnpm install                     # install all deps
-pnpm build                       # build all packages
-pnpm --filter @taiko/protocol test
-pnpm --filter @taiko/bridge-ui dev
-pnpm --filter @taiko/taiko-client build
-pnpm clean && pnpm install       # fix dependency state
-```
-
-## Global Policies
-
-- Use **GitHub CLI `gh`** for PR management and checks.
-- Prefer package‑scoped commands for single‑package work; use root for cross‑package.
-- Use real debuggers (Foundry `-vvvv`, Go `dlv`, browser DevTools) rather than print‑only debugging.
-- Never commit secrets. Validate inputs and add DoS/rate‑limit guards for services.
-
-## Agent Decision Flow (Root)
-
-1. **Identify scope**: {protocol | taiko-client | relayer | eventindexer | bridge-ui}.
-2. **Route**: if scope is **protocol**, switch to `/packages/protocol/agents.md` rules and runbooks.
-3. **Plan a minimal diff**: smallest change that solves the problem; respect package conventions.
-4. **Prepare validation**: include exact commands to compile/test/verify for the affected packages.
-5. **For multi‑package edits**: run `pnpm build` and targeted `--filter` tests for each impacted package.
-
-## CI/Test Expectations
-
-- All tests must pass; maintain high coverage (target >95% where measured).
-- Code review focuses on: security, error handling, L1 gas (when applicable), style consistency, concurrency risks (Go/TS), and test quality.
-- Keep READMEs and CHANGELOGs current when adding significant features.
-
-## PR Checklist (Root)
-
-- Clear title + concise summary of intent.
-- Exact commands to reproduce build/test/validation.
-- If smart contracts are touched: link to evidence of **storage layout** checks and **gas snapshots** (see nested file).
-- Security considerations (auth, invariants, failure modes).
diff --git a/packages/protocol/AGENTS.md b/packages/protocol/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/packages/protocol/Agents.md b/packages/protocol/Agents.md
@@ -1,134 +0,0 @@
-> **Scope**: Solidity contracts (L1/L2), Foundry tests, gas, and upgrade safety. Use this file for anything under `/packages/protocol`.
-
-## Quick Rules (enforce strictly)
-
-- **Imports**: `import {Contract} from "./Contract.sol";` (named imports only; no wildcard/side‑effect imports)
-- **Naming**:
-
-  - Private/internal funcs & state: `_prefix`
-  - Function params: start with `_`
-  - Return vars: end with `_`
-  - Events: **past tense** (e.g., `BlockProposed`, `ProofVerified`)
-  - Mappings: use **named parameters**
-
-- **Errors**: prefer custom errors; avoid require strings; define errors at end of implementation (not in interfaces).
-- **Docs**: `/// @notice` on external/public; `/// @dev` on internal/private; include `/// @custom:security-contact security@taiko.xyz` in all non‑test Solidity files; license **MIT** at top of each Solidity file.
-- **Upgradeable safety**: never reorder existing storage; append new vars only; include `uint256[50] __gap` in upgradeables; always verify layout before/after edits.
-
-## Layout & Key Files
-
-- L1 contracts: `contracts/layer1/`
-- L2 contracts: `contracts/layer2/`
-- Shared libs: `contracts/shared/`
-- **Shasta focus**:
-
-  - `contracts/layer1/shasta/impl/Inbox.sol` — propose/prove/finalize core
-  - `contracts/layer1/shasta/iface/` — interfaces & structs
-  - `contracts/layer2/based/ShastaAnchor.sol` — L1→L2 anchor + bond management
-
-- Patterns: UUPS upgradeable (OZ), Resolver for cross‑contract discovery, storage gaps on upgradeables.
-
-## Runbook (copy‑paste)
-
-```bash
-# Compile
-pnpm compile            # all contracts
-pnpm compile:l1         # FOUNDRY_PROFILE=layer1
-pnpm compile:l2         # FOUNDRY_PROFILE=layer2
-
-# Tests
-pnpm test               # all tests
-pnpm test:l1            # L1 only
-pnpm test:l2            # L2 only
-pnpm test:coverage      # coverage report
-forge test --match-test <name>
-forge test --match-path <path>
-forge test -vvvv
-forge test --match-path <path> --summary   # show gas per test
-
-# Shasta‑only inner loop (Inbox)
-forge test --match-path "test/layer1/shasta/inbox/suite2/*" -vvvv
-
-# Gas & storage layout (L1 critical)
-pnpm snapshot:l1                      # writes gas-reports/layer1-contracts.txt
-pnpm layout                           # verify storage layout; run before/after
-forge test --gas-report
-```
-
-## Test Style
-
-- Positive: `test_functionName_Description`
-- Negative: `test_functionName_RevertWhen_Description`
-- Inherit from **`CommonTest`** and use built‑in accounts (Alice, Bob, Carol, David, Emma)
-- Use `vm.expectEmit()` without parameters (treats all topics/data as checked)
-- Prefer real implementations over mocks when feasible to mirror prod deps
-
-## Gas Optimization Workflow
-
-1. **Baseline**: `pnpm snapshot:l1` → save `gas-reports/layer1-contracts.txt` as reference
-2. **Optimize**: minimize storage R/W; pack vars; prefer memory; batch ops; use `calldata`; store hashes of large structs when viable
-3. **Measure**: re‑run snapshot; compare diffs in `gas-reports/` and `snapshots/`; document deltas in PR body
-
-## Storage Layout Verification
-
-```bash
-pnpm layout
-# Attach/record before & after summaries in the PR when touching upgradeables
-```
-
-## PR Checklist (Protocol)
-
-- [ ] Solidity formatted: `pnpm fmt:sol`
-- [ ] Tests pass: `pnpm test` (and targeted suites)
-- [ ] Coverage reviewed: `pnpm test:coverage`
-- [ ] **Storage layout** verified: `pnpm layout` (summaries captured)
-- [ ] **Gas snapshot** updated: `pnpm snapshot:l1` (deltas noted)
-- [ ] Negative tests cover revert reasons; events asserted via `vm.expectEmit()`
-- [ ] Performance notes for critical paths (why trade‑offs are safe)
-
-## Common Pitfalls (auto‑warn)
-
-- Running full Shasta tests unnecessarily → use the specific suite path above.
-- Reordering storage in upgradeables.
-- Using require strings instead of custom errors.
-- Event names not in past tense.
-- Missing `security@taiko.xyz` custom tag.
-- Skipping `pnpm install` before Foundry work in a fresh checkout.
-
-## New Upgradeable Contract: Minimal Header
-
-```solidity
-// SPDX-License-Identifier: MIT
-pragma solidity ^0.8.0;
-
-import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
-import {UUPSUpgradeable} from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
-
-/// @custom:security-contact security@taiko.xyz
-contract MyContract is Initializable, UUPSUpgradeable {
-    uint256 private _x;
-    uint256[50] private __gap;
-
-    function initialize(uint256 _x_) public initializer {
-        _x = _x_;
-    }
-
-    function _authorizeUpgrade(address _newImpl_) internal override {}
-
-    // ---------------------------------------------------------------
-    // External & Public Functions
-    // ---------------------------------------------------------------
-
-    // ---------------------------------------------------------------
-    // Internal Functions
-    // ---------------------------------------------------------------
-
-    // ---------------------------------------------------------------
-    // Private Functions
-    // ---------------------------------------------------------------
-
-    // ---------------------------------------------------------------
-    // Custom Errors
-    // ---------------------------------------------------------------
-}
-```
PATCH

echo "Gold patch applied."
