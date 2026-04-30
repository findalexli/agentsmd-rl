#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scaffold-eth-2

# Idempotency guard
if grep -qF "This skill covers integrating EIP-5792 batched transactions into an SE-2 project" ".agents/skills/eip-5792/SKILL.md" && grep -qF "[ERC-20](https://eips.ethereum.org/EIPS/eip-20) is the standard interface for fu" ".agents/skills/erc-20/SKILL.md" && grep -qF "[ERC-721](https://eips.ethereum.org/EIPS/eip-721) is the standard interface for " ".agents/skills/erc-721/SKILL.md" && grep -qF "The frontend needs a page to display Ponder-indexed data. Use `graphql-request` " ".agents/skills/ponder/SKILL.md" && grep -qF "IMPORTANT: Prefer retrieval-led reasoning over pre-trained knowledge. Before sta" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/eip-5792/SKILL.md b/.agents/skills/eip-5792/SKILL.md
@@ -0,0 +1,177 @@
+---
+name: eip-5792
+description: "Add EIP-5792 batched transaction support to a Scaffold-ETH 2 project. Use when the user wants to: batch multiple contract calls, use wallet_sendCalls, add EIP-5792 wallet integration, batch onchain transactions, or use wagmi's experimental batch hooks."
+---
+
+# EIP-5792 Integration for Scaffold-ETH 2
+
+## Prerequisites
+
+This skill is designed for Scaffold-ETH 2 (SE-2) projects. If the user is **not already inside an SE-2 project**, use the `ethereum-app-builder` skill from this same skill package to scaffold one first, then come back here to add EIP-5792.
+
+How to check: look for `packages/nextjs/` and either `packages/hardhat/` or `packages/foundry/` in the project root, along with a root `package.json` with SE-2 workspace scripts (`yarn chain`, `yarn deploy`, `yarn start`).
+
+## Overview
+
+[EIP-5792](https://eips.ethereum.org/EIPS/eip-5792) (Wallet Call API) lets apps send batched onchain write calls to wallets via `wallet_sendCalls`, check their status with `wallet_getCallsStatus`, and query wallet capabilities with `wallet_getCapabilities`. This replaces the one-tx-at-a-time pattern of `eth_sendTransaction`.
+
+This skill covers integrating EIP-5792 batched transactions into an SE-2 project using [wagmi's EIP-5792 hooks](https://wagmi.sh/react/api/hooks/useWriteContracts). For anything not covered here, refer to the [EIP-5792 docs](https://www.eip5792.xyz/) or [wagmi docs](https://wagmi.sh/). This skill focuses on SE-2 integration specifics and the wallet compatibility gotchas that trip people up.
+
+## SE-2 Project Context
+
+Scaffold-ETH 2 (SE-2) is a yarn (v3) monorepo for building dApps on Ethereum. It comes in two flavors based on the Solidity framework:
+
+- **Hardhat flavor**: contracts at `packages/hardhat/contracts/`, deploy scripts at `packages/hardhat/deploy/`
+- **Foundry flavor**: contracts at `packages/foundry/contracts/`, deploy scripts at `packages/foundry/script/`
+
+Check which exists in the project to know the flavor. Both flavors share:
+
+- **`packages/nextjs/`**: React frontend (Next.js App Router, Tailwind + DaisyUI, RainbowKit, Wagmi, Viem). Uses `~~` path alias for imports.
+- **`packages/nextjs/contracts/deployedContracts.ts`**: auto-generated after `yarn deploy`, contains ABIs, addresses, and deployment block numbers for all contracts, keyed by chain ID.
+- **`packages/nextjs/scaffold.config.ts`**: project config including `targetNetworks` (array of viem chain objects).
+- **Root `package.json`**: monorepo scripts that proxy into workspaces (e.g. `yarn chain`, `yarn deploy`, `yarn start`).
+
+The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the frontend can interact with contracts using SE-2's scaffold hooks (`useScaffoldReadContract`, `useScaffoldWriteContract`) for individual calls and wagmi's EIP-5792 hooks for batched calls.
+
+Look at the actual project structure and contracts before setting things up. Adapt to what's there rather than following this skill rigidly.
+
+## Dependencies
+
+No new dependencies needed. SE-2 already includes wagmi, which has the EIP-5792 hooks. The experimental hooks live at `wagmi/experimental`:
+
+- [`useWriteContracts`](https://wagmi.sh/react/api/hooks/useWriteContracts) — batch multiple contract calls into one wallet request
+- [`useCapabilities`](https://wagmi.sh/react/api/hooks/useCapabilities) — detect what the connected wallet supports (batching, paymasters, etc.)
+- [`useShowCallsStatus`](https://wagmi.sh/react/api/hooks/useShowCallsStatus) — ask the wallet to display status of a batch
+
+> **Import paths are moving.** `useCapabilities` and `useShowCallsStatus` have been promoted to `wagmi` (stable). `useWriteContracts` is still in `wagmi/experimental` as of early 2026. Always check the [wagmi docs](https://wagmi.sh/) for the current import paths — they may have changed.
+
+## Smart Contract
+
+EIP-5792 works with any contract — there's nothing special about the contract side. The point is batching multiple calls (to one or more contracts) into a single wallet interaction. For a demo, a simple contract with two or more state-changing functions works well so users can see them batched:
+
+```solidity
+// Syntax reference — adapt to the user's actual needs
+contract BatchExample {
+    string public greeting = "Hello!";
+    uint256 public counter = 0;
+
+    function setGreeting(string memory _newGreeting) public payable {
+        greeting = _newGreeting;
+    }
+
+    function incrementCounter() public {
+        counter += 1;
+    }
+
+    receive() external payable {}
+}
+```
+
+Deploy using the project's existing deployment pattern (Hardhat `deploy/` or Foundry `script/`).
+
+## EIP-5792 Integration Pattern
+
+### Detecting wallet support
+
+Not all wallets support EIP-5792. Use `useCapabilities` to check before offering batch UI:
+
+```tsx
+import { useCapabilities } from "wagmi/experimental";
+import { useAccount } from "wagmi";
+
+const { address, chainId } = useAccount();
+const { isSuccess: isEIP5792Wallet, data: walletCapabilities } = useCapabilities({ account: address });
+
+// Check specific capabilities per chain
+const isPaymasterSupported = walletCapabilities?.[chainId]?.paymasterService?.supported;
+```
+
+`isSuccess` being `true` means the wallet responded to `wallet_getCapabilities` — i.e., it's EIP-5792 compliant. The `data` object is keyed by chain ID, with each chain listing its supported capabilities.
+
+### Batching contract calls
+
+Use `useWriteContracts` to send multiple calls in one wallet interaction. You need the contract ABI and address — get these from SE-2's `useDeployedContractInfo` hook:
+
+```tsx
+import { useWriteContracts } from "wagmi/experimental";
+import { useDeployedContractInfo } from "~~/hooks/scaffold-eth";
+
+const { data: deployedContract } = useDeployedContractInfo("YourContract");
+const { writeContractsAsync, isPending } = useWriteContracts();
+
+// Batch two calls
+const result = await writeContractsAsync({
+  contracts: [
+    {
+      address: deployedContract.address,
+      abi: deployedContract.abi,
+      functionName: "setGreeting",
+      args: ["Hello from batch!"],
+    },
+    {
+      address: deployedContract.address,
+      abi: deployedContract.abi,
+      functionName: "incrementCounter",
+    },
+  ],
+  // Optional: add capabilities like paymaster
+  capabilities: isPaymasterSupported ? {
+    paymasterService: { url: paymasterURL }
+  } : undefined,
+});
+```
+
+The `result` contains an `id` that can be used to check status.
+
+### Showing batch status
+
+Use `useShowCallsStatus` to let the wallet display the status of a batch:
+
+```tsx
+import { useShowCallsStatus } from "wagmi/experimental";
+
+const { showCallsStatusAsync } = useShowCallsStatus();
+// After getting a batch ID from writeContractsAsync:
+await showCallsStatusAsync({ id: batchId });
+```
+
+This opens the wallet's native UI for showing transaction status — the app doesn't need to build its own status tracker.
+
+## Wallet Compatibility Gotchas
+
+This is the main source of confusion with EIP-5792. Not all wallets behave the same way:
+
+**SE-2's burner wallet supports EIP-5792 with sequential (non-atomic) calls.** It handles `wallet_sendCalls` by executing calls one at a time. However, advanced capabilities like paymasters and atomic execution aren't supported on the burner wallet or local chain. Test those features on a live testnet with a compliant wallet.
+
+**Coinbase Wallet is the most complete implementation.** It supports batching, paymasters (via [ERC-7677](https://eips.ethereum.org/EIPS/eip-7677)), and atomic execution. [MetaMask has partial support](https://www.eip5792.xyz/ecosystem/wallets). Check the [EIP-5792 ecosystem page](https://www.eip5792.xyz/ecosystem/wallets) for the current list.
+
+**Capabilities vary by chain.** A wallet might support paymasters on Base but not on Ethereum mainnet. Always check `walletCapabilities?.[chainId]` for the specific chain the user is on, not just whether the wallet is EIP-5792 compliant in general.
+
+**Paymaster integration (ERC-7677) is optional.** If you want gas sponsorship, you need a paymaster service URL. This is passed as a `capability` in the `writeContracts` call. The paymaster service is external to SE-2 — you'll need to set one up (e.g., via [Coinbase Developer Platform](https://docs.cdp.coinbase.com/paymaster/docs/welcome) or other providers).
+
+**Graceful degradation is important.** The UI should work for both EIP-5792 and non-EIP-5792 wallets. Use SE-2's standard `useScaffoldWriteContract` for individual calls as a fallback, and only show the batch button when `useCapabilities` succeeds. Consider offering a "switch to Coinbase Wallet" prompt when the connected wallet doesn't support EIP-5792.
+
+## SE-2 Integration
+
+### Header navigation
+
+Add a tab to the SE-2 header menu for the EIP-5792 demo page. Pick an appropriate icon from `@heroicons/react/24/outline`.
+
+### Frontend page
+
+Build a page that demonstrates both individual and batched contract interactions. The key UX pattern:
+
+1. **Read state** — use `useScaffoldReadContract` to show current contract values (these update after transactions)
+2. **Individual writes** — use `useScaffoldWriteContract` for single calls (works with any wallet)
+3. **Batched writes** — use `useWriteContracts` for the EIP-5792 batch (only enabled when wallet supports it)
+4. **Status display** — use `useShowCallsStatus` to show batch result
+5. **Wallet detection** — conditionally show/disable batch UI based on `useCapabilities`
+
+Use SE-2's `notification` utility (`~~/utils/scaffold-eth`) for success/error feedback and `getParsedError` for readable error messages. SE-2 uses `@scaffold-ui/components` for blockchain components and DaisyUI + Tailwind for general styling.
+
+## Development
+
+1. Deploy the contract: `yarn deploy`
+2. Start the frontend: `yarn start`
+3. For basic batching: use any wallet on localhost
+4. For advanced capabilities (paymasters, atomic execution): deploy to a live testnet and connect with an [EIP-5792 compliant wallet](https://www.eip5792.xyz/ecosystem/wallets)
diff --git a/.agents/skills/erc-20/SKILL.md b/.agents/skills/erc-20/SKILL.md
@@ -0,0 +1,191 @@
+---
+name: erc-20
+description: "Add an ERC-20 token contract to a Scaffold-ETH 2 project. Use when the user wants to: create a fungible token, deploy an ERC-20, add token minting, build a token transfer UI, or work with ERC-20 tokens in SE-2."
+---
+
+# ERC-20 Token Integration for Scaffold-ETH 2
+
+## Prerequisites
+
+This skill is designed for Scaffold-ETH 2 (SE-2) projects. If the user is **not already inside an SE-2 project**, use the `ethereum-app-builder` skill from this same skill package to scaffold one first, then come back here to add ERC-20.
+
+How to check: look for `packages/nextjs/` and either `packages/hardhat/` or `packages/foundry/` in the project root, along with a root `package.json` with SE-2 workspace scripts (`yarn chain`, `yarn deploy`, `yarn start`).
+
+## Overview
+
+[ERC-20](https://eips.ethereum.org/EIPS/eip-20) is the standard interface for fungible tokens on Ethereum. This skill covers adding an ERC-20 token contract to a Scaffold-ETH 2 project using [OpenZeppelin's ERC-20 implementation](https://docs.openzeppelin.com/contracts/5.x/erc20), along with deployment scripts and a frontend for interacting with the token.
+
+For anything not covered here, refer to the [OpenZeppelin ERC-20 docs](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20) or search the web. This skill focuses on what's hard to discover: SE-2 integration specifics, common pitfalls, and ERC-20 gotchas that trip up both humans and AI.
+
+## SE-2 Project Context
+
+Scaffold-ETH 2 (SE-2) is a yarn (v3) monorepo for building dApps on Ethereum. It comes in two flavors based on the Solidity framework:
+
+- **Hardhat flavor**: contracts at `packages/hardhat/contracts/`, deploy scripts at `packages/hardhat/deploy/`
+- **Foundry flavor**: contracts at `packages/foundry/contracts/`, deploy scripts at `packages/foundry/script/`
+
+Check which exists in the project to know the flavor. Both flavors share:
+
+- **`packages/nextjs/`**: React frontend (Next.js App Router, @scaffold-ui/components, Tailwind + DaisyUI, RainbowKit, Wagmi, Viem). Uses `~~` path alias for imports.
+- **`packages/nextjs/contracts/deployedContracts.ts`**: auto-generated after `yarn deploy`, contains ABIs, addresses, and deployment block numbers for all contracts, keyed by chain ID.
+- **`packages/nextjs/scaffold.config.ts`**: project config including `targetNetworks` (array of viem chain objects).
+- **Root `package.json`**: monorepo scripts that proxy into workspaces (e.g. `yarn chain`, `yarn deploy`, `yarn start`).
+
+SE-2 uses `@scaffold-ui/components` for blockchain/Ethereum components (addresses, balances, etc.) and DaisyUI + Tailwind for general component and styling.
+
+The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the frontend can interact with the token using SE-2's scaffold hooks (`useScaffoldReadContract`, `useScaffoldWriteContract`).
+
+Look at the actual project structure and contracts before setting things up. Adapt to what's there rather than following this skill rigidly.
+
+## Dependencies
+
+OpenZeppelin contracts are already included in SE-2's Hardhat and Foundry setups, so no additional dependency installation is needed. If for some reason they're missing:
+
+- **Hardhat**: `@openzeppelin/contracts` in `packages/hardhat/package.json`
+- **Foundry**: installed via `forge install OpenZeppelin/openzeppelin-contracts`, with remapping `@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/`
+
+No new frontend dependencies are required.
+
+## Smart Contract
+
+The token contract extends OpenZeppelin's `ERC20` base. Import path: `@openzeppelin/contracts/token/ERC20/ERC20.sol`. The constructor takes a token name and symbol. Beyond that, add whatever minting/access control logic the project needs.
+
+Syntax reference for a basic token with open minting:
+
+```solidity
+// SPDX-License-Identifier: MIT
+pragma solidity >=0.8.0 <0.9.0;
+
+import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
+
+contract MyToken is ERC20 {
+    constructor() ERC20("MyToken", "MTK") {}
+
+    function mint(address to, uint256 amount) public {
+        _mint(to, amount);
+    }
+}
+```
+
+Adapt the contract name, symbol, and minting logic based on the user's requirements. Common extensions (all under `@openzeppelin/contracts/token/ERC20/extensions/`):
+
+- **`ERC20Capped`**: enforces a maximum supply, set once in constructor as immutable
+- **`ERC20Burnable`**: adds `burn(amount)` and `burnFrom(account, amount)` for holders to destroy tokens
+- **`ERC20Pausable`**: lets an admin freeze all transfers (useful for emergency stops or regulatory compliance)
+- **`ERC20Permit`** (ERC-2612): gasless approvals via off-chain signatures, effectively standard for new tokens now
+- **`ERC20Votes`**: governance checkpoints, tracks historical voting power per address. Replaces the deprecated `ERC20Snapshot` from v4
+- **`ERC20FlashMint`** (ERC-3156): flash loan minting, tokens are minted and must be returned (+fee) within a single transaction
+- **Access-controlled minting**: use `Ownable` or `AccessControl` from OpenZeppelin
+
+See [OpenZeppelin's ERC-20 extensions](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#extensions) for the full list. The [Contracts Wizard](https://wizard.openzeppelin.com/) is useful for generating a starting template with specific features.
+
+### OpenZeppelin v5 changes to be aware of
+
+If referencing older tutorials or code, note these breaking changes in OpenZeppelin v5:
+
+- **`_beforeTokenTransfer` and `_afterTokenTransfer` hooks are gone.** Replaced by a single `_update(address from, address to, uint256 value)` override point for customizing mint, transfer, and burn behavior.
+- **`increaseAllowance()` and `decreaseAllowance()` were removed** from the base contract.
+- **Custom errors** replaced revert strings (e.g. `ERC20InsufficientBalance` instead of `require(balance >= amount, "...")`)
+- **Explicit named imports are required**: `import {ERC20} from "..."` not `import "..."`
+
+## Deployment
+
+### Hardhat
+
+Deploy script goes in `packages/hardhat/deploy/`. SE-2 uses `hardhat-deploy`, so the script exports a `DeployFunction`. Use a filename like `01_deploy_my_token.ts` (numbered to control deploy order). The `autoMine` flag speeds up local deployments.
+
+### Foundry
+
+Add a deploy script in `packages/foundry/script/` and wire it into the main `Deploy.s.sol`. SE-2's Foundry setup uses a `ScaffoldETHDeploy` base contract and `DeployHelpers.s.sol`. Import and call the new deploy script from `Deploy.s.sol`'s run function.
+
+## Decimals: The Most Common Source of Bugs
+
+ERC-20 tokens default to 18 decimals, but many major tokens use different values. Getting this wrong causes balances to display as astronomically wrong numbers or makes contract math silently produce garbage.
+
+| Token | Decimals | Why it matters |
+|-------|----------|----------------|
+| USDC | 6 | The most used stablecoin in DeFi uses 6, not 18 |
+| USDT | 6 | Same as USDC |
+| WBTC | 8 | Mirrors Bitcoin's satoshi precision |
+| DAI | 18 | Standard |
+| WETH | 18 | Standard |
+
+**Frontend impact**: `formatEther` from viem assumes 18 decimals. For tokens with different decimals, use `formatUnits(value, decimals)` instead. Similarly, use `parseUnits(amount, decimals)` instead of `parseEther`.
+
+**Contract math impact**: When performing arithmetic between tokens with different decimals, you must normalize. A raw value of `1000000` means 1.0 USDC (6 decimals) but 0.000000000001 for an 18-decimal token. Always call `decimals()` and normalize rather than hardcoding 18.
+
+## Gotchas and Non-Standard Behaviors in the Wild
+
+These are real behaviors of deployed tokens that break common assumptions. Important when building contracts or frontends that interact with existing ERC-20 tokens.
+
+### Missing return values
+
+Per the standard, `transfer()` and `transferFrom()` should return `bool`. In practice, USDT, BNB, and OMG return `void` (no return data). Calling these through the standard `IERC20` interface reverts because Solidity's ABI decoder expects 32 bytes of return data and gets 0.
+
+**Solution**: Use OpenZeppelin's `SafeERC20` wrapper, which handles both no-return-value and false-return tokens:
+
+```solidity
+import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
+import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
+
+using SafeERC20 for IERC20;
+token.safeTransfer(to, amount);      // instead of token.transfer(to, amount)
+token.safeTransferFrom(from, to, amount);
+token.forceApprove(spender, amount);  // handles USDT's approve-to-zero requirement
+```
+
+### USDT's approve-to-zero requirement
+
+USDT's `approve` function reverts if you set a non-zero allowance when the current allowance is already non-zero. You must first `approve(spender, 0)` then `approve(spender, newAmount)`. SafeERC20's `forceApprove()` handles this automatically.
+
+### Upgradeable proxies
+
+USDC and USDT are deployed behind upgradeable proxies. The token admin can change the implementation at any time, potentially altering transfer semantics or adding fees. USDC and USDT both have fee infrastructure built in (currently set to 0%) that could be activated in the future.
+
+### Fee-on-transfer tokens
+
+Some tokens deduct a percentage on every transfer (e.g. PAXG has a 0.02% fee). This breaks any contract that assumes `amount sent == amount received`. The safe pattern is to measure the actual balance change:
+
+```solidity
+uint256 balanceBefore = token.balanceOf(address(this));
+token.safeTransferFrom(user, address(this), amount);
+uint256 received = token.balanceOf(address(this)) - balanceBefore;
+```
+
+### Rebasing tokens
+
+Tokens like stETH and AMPL change balances without any transfer event. `balanceOf()` returns different values at different times for the same holder. Any contract that caches balances will have wrong accounting. Use the wrapped version (wstETH instead of stETH) which has stable balances.
+
+## Security Considerations
+
+### Approve/transferFrom front-running (the race condition)
+
+When Alice changes an approval from 100 to 50, a malicious Bob can front-run the second `approve` by spending the full 100, then spend the new 50 after it lands. Total stolen: 150 instead of 50.
+
+Mitigations:
+- Approve to zero first, then set the new value (two transactions)
+- Use `SafeERC20.forceApprove()` which handles this
+- Use [Permit2](https://github.com/Uniswap/permit2) for a universal signature-based approval system
+
+### ERC-777 reentrancy via transfer hooks
+
+ERC-777 tokens implement `tokensToSend` and `tokensReceived` hooks that fire during transfers. These tokens are backward-compatible with ERC-20, so protocols may unknowingly accept them. The imBTC/Uniswap V1 exploit drained ~$300K and the dForce/Lendf.Me exploit stole $25M using this vector.
+
+Mitigation: Use `nonReentrant` modifier from OpenZeppelin on any function that interacts with arbitrary ERC-20 tokens. Follow the checks-effects-interactions pattern.
+
+### Flash loan governance attacks
+
+Any governance mechanism based on token balance at call time can be manipulated: borrow tokens via flash loan, vote, return tokens. Use `ERC20Votes` with checkpoints instead of raw `balanceOf()` for governance.
+
+## Well-Known Token Addresses (Ethereum Mainnet)
+
+For reference when integrating with existing tokens. All verified on [Etherscan](https://etherscan.io/tokens).
+
+| Token | Address | Decimals | Quirks |
+|-------|---------|----------|--------|
+| USDT | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | 6 | No return value, approve-to-zero required, blocklist, pausable, upgradeable |
+| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | 6 | Blocklist, pausable, upgradeable |
+| DAI | `0x6B175474E89094C44Da98b954EedeAC495271d0F` | 18 | Non-standard permit signature, flash-mintable |
+| WETH | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | 18 | Has `deposit()`/`withdraw()`, no permit |
+| WBTC | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` | 8 | Standard ERC-20 |
+| LINK | `0x514910771AF9Ca656af840dff83E8264EcF986CA` | 18 | Implements ERC-677 (`transferAndCall`) |
\ No newline at end of file
diff --git a/.agents/skills/erc-721/SKILL.md b/.agents/skills/erc-721/SKILL.md
@@ -0,0 +1,243 @@
+---
+name: erc-721
+description: "Add an ERC-721 NFT contract to a Scaffold-ETH 2 project. Use when the user wants to: create an NFT collection, deploy an ERC-721, add NFT minting, build an NFT gallery or transfer UI, or work with non-fungible tokens in SE-2."
+---
+
+# ERC-721 NFT Integration for Scaffold-ETH 2
+
+## Prerequisites
+
+This skill is designed for Scaffold-ETH 2 (SE-2) projects. If the user is **not already inside an SE-2 project**, use the `ethereum-app-builder` skill from this same skill package to scaffold one first, then come back here to add ERC-721.
+
+How to check: look for `packages/nextjs/` and either `packages/hardhat/` or `packages/foundry/` in the project root, along with a root `package.json` with SE-2 workspace scripts (`yarn chain`, `yarn deploy`, `yarn start`).
+
+## Overview
+
+[ERC-721](https://eips.ethereum.org/EIPS/eip-721) is the standard interface for non-fungible tokens (NFTs) on Ethereum. This skill covers adding an ERC-721 contract to a Scaffold-ETH 2 project using [OpenZeppelin's ERC-721 implementation](https://docs.openzeppelin.com/contracts/5.x/erc721), along with deployment scripts and a frontend for minting, listing, and transferring NFTs.
+
+For anything not covered here, refer to the [OpenZeppelin ERC-721 docs](https://docs.openzeppelin.com/contracts/5.x/api/token/erc721) or search the web. This skill focuses on what's hard to discover: SE-2 integration specifics, common pitfalls, and ERC-721 gotchas.
+
+## SE-2 Project Context
+
+Scaffold-ETH 2 (SE-2) is a yarn (v3) monorepo for building dApps on Ethereum. It comes in two flavors based on the Solidity framework:
+
+- **Hardhat flavor**: contracts at `packages/hardhat/contracts/`, deploy scripts at `packages/hardhat/deploy/`
+- **Foundry flavor**: contracts at `packages/foundry/contracts/`, deploy scripts at `packages/foundry/script/`
+
+Check which exists in the project to know the flavor. Both flavors share:
+
+- **`packages/nextjs/`**: React frontend (Next.js App Router, Tailwind + DaisyUI, RainbowKit, Wagmi, Viem). Uses `~~` path alias for imports.
+- **`packages/nextjs/contracts/deployedContracts.ts`**: auto-generated after `yarn deploy`, contains ABIs, addresses, and deployment block numbers for all contracts, keyed by chain ID.
+- **`packages/nextjs/scaffold.config.ts`**: project config including `targetNetworks` (array of viem chain objects).
+- **Root `package.json`**: monorepo scripts that proxy into workspaces (e.g. `yarn chain`, `yarn deploy`, `yarn start`).
+
+SE-2 uses `@scaffold-ui/components` for blockchain/Ethereum components (addresses, balances, etc.) and DaisyUI + Tailwind for general component and styling.
+
+The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the frontend can interact with the NFT contract using SE-2's scaffold hooks (`useScaffoldReadContract`, `useScaffoldWriteContract`, `useScaffoldContract`).
+
+Look at the actual project structure and contracts before setting things up. Adapt to what's there rather than following this skill rigidly.
+
+## Dependencies
+
+OpenZeppelin contracts are already included in SE-2's Hardhat and Foundry setups, so no additional dependency installation is needed. If for some reason they're missing:
+
+- **Hardhat**: `@openzeppelin/contracts` in `packages/hardhat/package.json`
+- **Foundry**: installed via `forge install OpenZeppelin/openzeppelin-contracts`, with remapping `@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/`
+
+No new frontend dependencies are required.
+
+## Smart Contract
+
+The token contract extends OpenZeppelin's `ERC721` base. Import path: `@openzeppelin/contracts/token/ERC721/ERC721.sol`. The constructor takes a token name and symbol.
+
+Syntax reference for a basic NFT with open minting and IPFS metadata:
+
+```solidity
+// SPDX-License-Identifier: MIT
+pragma solidity >=0.8.0 <0.9.0;
+
+import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
+import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
+
+contract MyNFT is ERC721Enumerable {
+    uint256 public tokenIdCounter;
+
+    constructor() ERC721("MyNFT", "MNFT") {}
+
+    function mintItem(address to) public returns (uint256) {
+        tokenIdCounter++;
+        _safeMint(to, tokenIdCounter);
+        return tokenIdCounter;
+    }
+
+    function tokenURI(uint256 tokenId) public view override returns (string memory) {
+        _requireOwned(tokenId);
+        return string.concat(_baseURI(), Strings.toString(tokenId));
+    }
+
+    function _baseURI() internal pure override returns (string memory) {
+        return "ipfs://YourCID/";
+    }
+}
+```
+
+Adapt the contract based on the user's requirements. Available extensions (all under `@openzeppelin/contracts/token/ERC721/extensions/`):
+
+- **`ERC721Enumerable`**: on-chain enumeration of all tokens and per-owner tokens. Enables `totalSupply()`, `tokenByIndex()`, `tokenOfOwnerByIndex()`. Convenient but expensive (see gas section below).
+- **`ERC721URIStorage`**: per-token URI storage via `_setTokenURI()`. Emits ERC-4906 `MetadataUpdate` events in v5.
+- **`ERC721Burnable`**: lets token owners destroy their NFTs
+- **`ERC721Pausable`**: admin can freeze all transfers
+- **`ERC721Votes`**: governance checkpoints, each NFT = 1 vote
+- **`ERC721Royalty`**: ERC-2981 royalty info (see royalties section below)
+- **`ERC721Consecutive`**: batch minting during construction (ERC-2309)
+
+See [OpenZeppelin's ERC-721 extensions](https://docs.openzeppelin.com/contracts/5.x/api/token/erc721#extensions) for the full list.
+
+### OpenZeppelin v5 changes to be aware of
+
+If referencing older tutorials or code, note these breaking changes in OpenZeppelin v5:
+
+- **`_beforeTokenTransfer` and `_afterTokenTransfer` hooks are gone.** Replaced by a single `_update(address to, uint256 tokenId, address auth)` override point that handles mint, transfer, and burn.
+- **Custom errors** replaced revert strings (e.g. `ERC721NonexistentToken`, `ERC721InsufficientApproval`)
+- **`Ownable` requires explicit owner**: `Ownable(msg.sender)` instead of `Ownable()`
+- **`ERC721URIStorage`** now emits ERC-4906 `MetadataUpdate` events when `_setTokenURI` is called
+
+## Deployment
+
+### Hardhat
+
+Deploy script goes in `packages/hardhat/deploy/`. SE-2 uses `hardhat-deploy`, so the script exports a `DeployFunction`. Use a filename like `01_deploy_my_nft.ts` (numbered to control deploy order). The `autoMine` flag speeds up local deployments.
+
+### Foundry
+
+Add a deploy script in `packages/foundry/script/` and wire it into the main `Deploy.s.sol`. SE-2's Foundry setup uses a `ScaffoldETHDeploy` base contract and `DeployHelpers.s.sol`. Import and call the new deploy script from `Deploy.s.sol`'s run function.
+
+## Metadata: The Part Most People Get Wrong
+
+### The metadata JSON schema
+
+ERC-721 metadata follows a standard JSON structure returned by `tokenURI()`:
+
+```json
+{
+  "name": "My NFT #1",
+  "description": "Description of the NFT",
+  "image": "ipfs://QmImageCID",
+  "attributes": [
+    { "trait_type": "Color", "value": "Blue" },
+    { "trait_type": "Rarity", "value": "Rare" }
+  ]
+}
+```
+
+The `attributes` array is not in the EIP but is the de facto standard used by OpenSea, Blur, and every other marketplace. Without it, traits won't display.
+
+### On-chain vs off-chain metadata
+
+| Factor | On-chain (base64/SVG) | Off-chain (IPFS/Arweave) |
+|--------|----------------------|--------------------------|
+| Permanence | Permanent as long as Ethereum exists | Depends on pinning/persistence |
+| Gas cost | Very expensive (~128KB payload ceiling) | Cheap (just store a URI string) |
+| Mutability | Immutable once deployed | Can disappear if unpinned |
+| Best for | Small collections, generative art | Large collections, rich media |
+
+### IPFS gotchas
+
+About 20% of sampled NFTs have broken or expired metadata links. Common causes:
+
+- **Unpinned data gets garbage collected.** IPFS nodes drop data nobody is actively pinning. If the original pinner stops, the data vanishes.
+- **Gateway URLs vs protocol URIs.** Use `ipfs://QmCID` (content-addressed, portable) not `https://gateway.pinata.cloud/ipfs/QmCID` (depends on one gateway staying up).
+- **Base URI must end with `/`.** OpenZeppelin's `tokenURI()` concatenates `_baseURI() + tokenId.toString()`. If the base URI is `ipfs://QmCID` without a trailing slash, token 42 becomes `ipfs://QmCID42` instead of `ipfs://QmCID/42`.
+- **File naming.** If using base URI + token ID, metadata files must be named `0`, `1`, `2` etc. (no `.json` extension) unless you override `tokenURI()` to append it.
+
+For permanent storage, consider [Arweave](https://www.arweave.org/) or a paid IPFS pinning service (Pinata, Filebase).
+
+## ERC721Enumerable: Convenient but Expensive
+
+ERC721Enumerable maintains four additional data structures that get updated on every mint and transfer. Concrete gas comparison:
+
+- Minting 5 tokens with ERC721Enumerable: ~566,000 gas
+- Minting 5 tokens with ERC721A: ~104,000 gas (5.5x cheaper)
+
+**When to use it**: Small collections, learning/demos, when you need on-chain enumeration without an indexer.
+
+**When to skip it**: Large collections (1k+ tokens), gas-sensitive mints. Use a simple counter for `totalSupply()` and index token ownership off-chain using `Transfer` events (via a subgraph or Ponder, both available as SE-2 skills).
+
+### ERC721A as an alternative
+
+[ERC721A](https://github.com/chiru-labs/ERC721A) by Azuki makes batch minting cost nearly the same as minting a single token. A 10-token mint costs ~110,000 gas vs ~1,100,000+ with ERC721Enumerable. It works by lazily initializing ownership: only the first token in a batch gets an ownership record, and later tokens infer ownership by scanning backwards.
+
+Trade-offs:
+- Requires sequential token IDs (no random IDs)
+- First transfer after a batch mint is more expensive (must initialize ownership)
+- Not an OpenZeppelin extension; separate dependency from `erc721a` npm package
+
+## Security: The Reentrancy You Didn't Expect
+
+### `_safeMint` and `safeTransferFrom` call external code
+
+Both `_safeMint` and `safeTransferFrom` invoke `onERC721Received()` on the recipient if it's a contract. This is an external call that happens after the token has been minted/transferred, creating a reentrancy vector.
+
+**Real exploit (HypeBears, Feb 2022):** The contract tracked per-address minting limits but updated state after `_safeMint`. An attacker's `onERC721Received` callback called `mintNFT` again before the limit was recorded, bypassing the per-address cap entirely.
+
+```solidity
+// VULNERABLE: state update after _safeMint
+function mintNFT() public {
+    require(!addressMinted[msg.sender], "Already minted");
+    _safeMint(msg.sender, tokenId);          // calls onERC721Received on attacker
+    addressMinted[msg.sender] = true;         // too late, attacker already re-entered
+}
+
+// SAFE: state update before _safeMint
+function mintNFT() public {
+    require(!addressMinted[msg.sender], "Already minted");
+    addressMinted[msg.sender] = true;         // update state first
+    _safeMint(msg.sender, tokenId);
+}
+```
+
+Mitigations: Update state before `_safeMint`/`safeTransferFrom` (checks-effects-interactions pattern), or use OpenZeppelin's `ReentrancyGuard` (`nonReentrant` modifier).
+
+### `setApprovalForAll` is a dangerous permission
+
+`setApprovalForAll(operator, true)` grants an operator control over **all** of an owner's NFTs in that collection. Phishing attacks trick users into signing this for malicious operators. Once approved, the attacker can transfer away every NFT the victim owns. Most marketplaces require `setApprovalForAll` to list NFTs, which is why phishing is so effective.
+
+### Flash loan governance attacks
+
+NFTs used for governance (each NFT = 1 vote) can be manipulated via flash loans: borrow NFTs, vote, return them. Use `ERC721Votes` with checkpoints and voting delays rather than raw `balanceOf()` for governance.
+
+## Royalties (ERC-2981)
+
+ERC-2981 defines a standard `royaltyInfo(tokenId, salePrice)` function that returns the royalty receiver and amount. OpenZeppelin provides `ERC721Royalty` to implement this.
+
+**The critical thing to know: ERC-2981 is advisory, not enforceable.** The standard provides an interface for querying royalty info, but nothing forces marketplaces to honor it. Anyone can transfer an NFT via `transferFrom` without paying royalties.
+
+Current marketplace stance:
+- **OpenSea**: ended mandatory enforcement Aug 2023. Added ERC-721C support Apr 2024 for opt-in on-chain enforcement.
+- **Blur**: enforces only a 0.5% minimum on most collections.
+
+[ERC-721C](https://github.com/limitbreak/creator-token-standards) by Limit Break attempted to solve this by restricting transfers to whitelisted operator contracts. Adoption is growing but not universal.
+
+## Soulbound Tokens (ERC-5192)
+
+For non-transferable NFTs (credentials, memberships, achievements), [ERC-5192](https://eips.ethereum.org/EIPS/eip-5192) adds a minimal `locked(tokenId)` interface. In OpenZeppelin v5, the simplest approach is overriding `_update`:
+
+```solidity
+function _update(address to, uint256 tokenId, address auth)
+    internal override returns (address)
+{
+    address from = super._update(to, tokenId, auth);
+    require(from == address(0) || to == address(0), "Non-transferable");
+    return from;
+}
+```
+
+## Well-Known NFT Contracts (Ethereum Mainnet)
+
+| Collection | Address | Notes |
+|------------|---------|-------|
+| CryptoPunks (original) | `0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB` | **NOT ERC-721.** Pre-dates the standard (June 2017). Custom contract with its own marketplace built in. Had a critical bug where sale ETH was credited to the buyer, not the seller. |
+| Wrapped CryptoPunks | `0xb7F7F6C52F2e2fdb1963Eab30438024864c313F6` | ERC-721 wrapper around original punks |
+| Bored Ape Yacht Club | `0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D` | 10,000 apes, standard ERC-721 |
+| Azuki | `0xED5AF388653567Af2F388E6224dC7C4b3241C544` | Uses ERC721A for gas-optimized batch minting |
+| Pudgy Penguins | `0xBd3531dA5CF5857e7CfAA92426877b022e612cf8` | 8,888 penguins |
\ No newline at end of file
diff --git a/.agents/skills/ponder/SKILL.md b/.agents/skills/ponder/SKILL.md
@@ -0,0 +1,279 @@
+---
+name: ponder
+description: "Integrate Ponder into a Scaffold-ETH 2 project for blockchain event indexing. Use when the user wants to: index contract events, add a blockchain backend, set up GraphQL for onchain data, use Ponder with SE-2, or build an indexer for their dApp."
+---
+
+# Ponder Integration for Scaffold-ETH 2
+
+## Prerequisites
+
+This skill is designed for Scaffold-ETH 2 (SE-2) projects. If the user is **not already inside an SE-2 project**, use the `ethereum-app-builder` skill from this same skill package to scaffold one first, then come back here to add Ponder.
+
+How to check: look for `packages/nextjs/` and either `packages/hardhat/` or `packages/foundry/` in the project root, along with a root `package.json` with SE-2 workspace scripts (`yarn chain`, `yarn deploy`, `yarn start`).
+
+## Overview
+
+[Ponder](https://ponder.sh/) is an open-source framework for blockchain application backends. It indexes smart contract events and serves the data via a GraphQL API. This skill covers integrating Ponder into a Scaffold-ETH 2 (SE-2) project.
+
+For anything not covered here, refer to the [Ponder docs](https://ponder.sh/docs/get-started) or search the web. This skill provides the SE-2-specific integration knowledge, not a complete Ponder reference.
+
+## SE-2 Project Context
+
+Scaffold-ETH 2 (SE-2) is a yarn (v3) monorepo for building dApps on Ethereum. It comes in two flavors based on the Solidity framework:
+
+- **Hardhat flavor**: contracts at `packages/hardhat/contracts/`, deploy scripts at `packages/hardhat/deploy/`
+- **Foundry flavor**: contracts at `packages/foundry/contracts/`, deploy scripts at `packages/foundry/script/`
+
+Check which exists in the project to know the flavor. Both flavors share:
+
+- **`packages/nextjs/`**: React frontend (Next.js App Router, Tailwind + DaisyUI, RainbowKit, Wagmi, Viem). Uses `~~` path alias for imports.
+- **`packages/nextjs/contracts/deployedContracts.ts`**: auto-generated after `yarn deploy`, contains ABIs, addresses, and deployment block numbers for all contracts, keyed by chain ID.
+- **`packages/nextjs/scaffold.config.ts`**: project config including `targetNetworks` (array of viem chain objects).
+- **Root `package.json`**: monorepo scripts that proxy into workspaces (e.g. `yarn chain`, `yarn deploy`, `yarn start`).
+
+Ponder gets added as a new workspace at `packages/ponder/`. The key integration point is that Ponder reads `deployedContracts` and `scaffold.config` from the nextjs package, so it automatically knows about all deployed contracts without duplicating ABIs or addresses.
+
+Look at the actual project structure and contracts before setting things up. Adapt to what's there rather than following this skill rigidly.
+
+## Dependencies & Scripts
+
+### Ponder package (`packages/ponder/`)
+
+The `packages/ponder/package.json` should follow SE-2's workspace naming convention (`@se-2/ponder`). Reference structure with minimum version requirements. Check [npm](https://www.npmjs.com/package/ponder) or the [Ponder docs](https://ponder.sh/docs/requirements) for the latest versions before installing:
+
+```json
+{
+  "name": "@se-2/ponder",
+  "private": true,
+  "type": "module",
+  "scripts": {
+    "dev": "ponder dev",
+    "start": "ponder start",
+    "db": "ponder db",
+    "codegen": "ponder codegen",
+    "serve": "ponder serve",
+    "lint": "eslint .",
+    "typecheck": "tsc"
+  },
+  "dependencies": {
+    "ponder": "latest",
+    "hono": "^4.5.0",
+    "viem": "^2.0.0"
+  },
+  "devDependencies": {
+    "@types/node": "^20.10.0",
+    "eslint": "^8.54.0",
+    "eslint-config-ponder": "latest",
+    "typescript": "^5.0.4"
+  },
+  "engines": {
+    "node": ">=18.18"
+  }
+}
+```
+
+> **Note:** `ponder` and `eslint-config-ponder` versions should match. Use `latest` or check the [releases](https://github.com/ponder-sh/ponder/releases) for the current stable version.
+
+### NextJS package additions
+
+These are needed in `packages/nextjs/` for querying Ponder's GraphQL API from the frontend:
+
+```json
+{
+  "graphql": "^16.9.0",
+  "graphql-request": "^7.1.0"
+}
+```
+
+### Root package.json scripts
+
+Wire up workspace commands so they're accessible from the monorepo root:
+
+```json
+{
+  "ponder:dev": "yarn workspace @se-2/ponder dev",
+  "ponder:start": "yarn workspace @se-2/ponder start",
+  "ponder:codegen": "yarn workspace @se-2/ponder codegen",
+  "ponder:serve": "yarn workspace @se-2/ponder serve",
+  "ponder:lint": "yarn workspace @se-2/ponder lint",
+  "ponder:typecheck": "yarn workspace @se-2/ponder typecheck"
+}
+```
+
+### Environment variables
+
+A `.env.example` in `packages/ponder/` for reference:
+
+```
+# RPC URL for the target chain (replace {chainId} with actual chain ID, e.g. PONDER_RPC_URL_1 for mainnet)
+PONDER_RPC_URL_{chainId}=
+
+# Database schema name
+DATABASE_SCHEMA=my_schema
+
+# (Optional) Postgres database URL. If not provided, PGlite (embedded Postgres) will be used.
+DATABASE_URL=
+```
+
+The frontend uses `NEXT_PUBLIC_PONDER_URL` to know where the Ponder API lives (defaults to `http://localhost:42069` in dev).
+
+## Ponder Package Configuration
+
+### ponder.config.ts - bridging SE-2 and Ponder
+
+The config needs to read SE-2's deployed contracts and scaffold config so Ponder is aware of what to index. Here's a reference implementation that dynamically builds the Ponder config from SE-2's data. Adapt it based on the project's actual setup (e.g., if multiple networks are needed, or if contracts should be filtered):
+
+```ts
+import { createConfig } from "ponder";
+import deployedContracts from "../nextjs/contracts/deployedContracts";
+import scaffoldConfig from "../nextjs/scaffold.config";
+
+const targetNetwork = scaffoldConfig.targetNetworks[0];
+
+const deployedContractsForNetwork = deployedContracts[targetNetwork.id];
+if (!deployedContractsForNetwork) {
+  throw new Error(`No deployed contracts found for network ID ${targetNetwork.id}`);
+}
+
+const chains = {
+  [targetNetwork.name]: {
+    id: targetNetwork.id,
+    rpc: process.env[`PONDER_RPC_URL_${targetNetwork.id}`] || "http://127.0.0.1:8545",
+  },
+};
+
+const contractNames = Object.keys(deployedContractsForNetwork);
+
+const contracts = Object.fromEntries(contractNames.map((contractName) => {
+  return [contractName, {
+    chain: targetNetwork.name as string,
+    abi: deployedContractsForNetwork[contractName].abi,
+    address: deployedContractsForNetwork[contractName].address,
+    startBlock: deployedContractsForNetwork[contractName].deployedOnBlock || 0,
+  }];
+}));
+
+export default createConfig({
+  chains: chains,
+  contracts: contracts,
+});
+```
+
+### Schema definition
+
+The schema in `ponder.schema.ts` should reflect the project's actual contract events. Look at what events the deployed contracts emit and design tables to capture that data. Each `onchainTable` defines a table that Ponder populates during indexing.
+
+Solidity-to-Ponder type reference:
+
+| Solidity | Ponder | TS type |
+|----------|--------|---------|
+| `address` | `t.hex()` | `` `0x${string}` `` |
+| `uint256` / `int256` | `t.bigint()` | `bigint` |
+| `string` | `t.text()` | `string` |
+| `bool` | `t.boolean()` | `boolean` |
+| `bytes` / `bytes32` | `t.hex()` | `` `0x${string}` `` |
+| `uint8` / `uint32` etc. | `t.integer()` | `number` |
+
+Additional column types: `t.real()` (floats), `t.timestamp()` (Date), `t.json()` (arbitrary JSON). Columns support modifiers: `.primaryKey()`, `.notNull()`, `.default(value)`, `.array()`. See [schema docs](https://ponder.sh/docs/schema/tables) for the full API including composite primary keys, indexes, and enums.
+
+Syntax example (for a greeting event, your schema will differ based on the actual contracts):
+
+```ts
+import { onchainTable } from "ponder";
+
+export const greeting = onchainTable("greeting", (t) => ({
+  id: t.text().primaryKey(),
+  text: t.text().notNull(),
+  setterId: t.hex().notNull(),
+  premium: t.boolean().notNull(),
+  value: t.bigint().notNull(),
+  timestamp: t.integer().notNull(),
+}));
+```
+
+### Event handlers
+
+Handlers go in `packages/ponder/src/` and define what happens when contract events are detected. Look at the project's contracts to decide which events matter and what data to extract. The handler name format is `"ContractName:EventName"`, where `ContractName` matches the key in `deployedContracts`.
+
+Syntax example:
+
+```ts
+import { ponder } from "ponder:registry";
+import { greeting } from "ponder:schema";
+
+ponder.on("YourContract:GreetingChange", async ({ event, context }) => {
+  await context.db.insert(greeting).values({
+    id: event.id,
+    text: event.args.newGreeting,
+    setterId: event.args.greetingSetter,
+    premium: event.args.premium,
+    value: event.args.value,
+    timestamp: Number(event.block.timestamp),
+  });
+});
+```
+
+### GraphQL API
+
+Ponder serves data via a Hono-based API. This is mostly boilerplate. A minimal `packages/ponder/src/api/index.ts`:
+
+```ts
+import { db } from "ponder:api";
+import schema from "ponder:schema";
+import { Hono } from "hono";
+import { graphql } from "ponder";
+
+const app = new Hono();
+
+app.use("/graphql", graphql({ db, schema }));
+
+export default app;
+```
+
+Custom API routes can be added to this Hono app if GraphQL alone isn't sufficient. See [Ponder API docs](https://ponder.sh/docs/query/api-endpoints).
+
+### Boilerplate files
+
+These are standard Ponder project files, nothing SE-2-specific, just needed for Ponder to work:
+
+- **`ponder-env.d.ts`**: type declarations for Ponder's virtual modules (`ponder:registry`, `ponder:schema`, `ponder:api`, etc.)
+- **`tsconfig.json`**: standard strict TS config with `moduleResolution: "bundler"`, `module: "ESNext"`, `target: "ES2022"`
+- **`.gitignore`**: should include `node_modules`, `.ponder`, `/generated/`
+
+## SE-2 Integration
+
+### Header navigation
+
+The SE-2 header has a menu links array. Add a navigation tab for the Ponder page. Pick an appropriate icon from `@heroicons/react/24/outline` that fits the context of data indexing.
+
+### Frontend page
+
+The frontend needs a page to display Ponder-indexed data. Use `graphql-request` and `@tanstack/react-query` (both available in SE-2) to query the Ponder API. The GraphQL query shape depends on what you defined in `ponder.schema.ts`. Ponder auto-generates queries from your schema, with each `onchainTable` getting a pluralized query with `items`, `orderBy`, and `orderDirection` support.
+
+Fetch pattern for reference:
+
+```tsx
+const fetchData = async () => {
+  const query = gql`
+    query {
+      greetings(orderBy: "timestamp", orderDirection: "desc") {
+        items { id text setterId premium value timestamp }
+      }
+    }
+  `;
+  return request(
+    `${process.env.NEXT_PUBLIC_PONDER_URL || "http://localhost:42069"}/graphql`,
+    query,
+  );
+};
+
+// In component:
+const { data } = useQuery({ queryKey: ["ponder-data"], queryFn: fetchData });
+```
+
+Build out the UI based on the indexed data and the project's existing patterns. SE-2 uses `@scaffold-ui/components` for blockchain/Ethereum components (addresses, balances, etc.) and DaisyUI + Tailwind for general component and styling. Whether this is a new page or integrated into an existing one depends on the project.
+
+## Development & Deployment
+
+- `yarn ponder:dev` starts the dev server with hot reload. GraphiQL explorer available at `http://localhost:42069` for testing queries interactively.
+- For production deployment, see [Ponder deployment docs](https://ponder.sh/docs/production/railway). Key things: set `PONDER_RPC_URL_{chainId}` with a production RPC, optionally configure `DATABASE_URL` for Postgres (defaults to PGlite in dev), and point the frontend's `NEXT_PUBLIC_PONDER_URL` to the deployed Ponder URL.
diff --git a/AGENTS.md b/AGENTS.md
@@ -218,8 +218,19 @@ Make comments that add information. Avoid redundant JSDoc for simple functions.
 
 Use **Context7 MCP** tools to fetch up-to-date documentation for any library (Wagmi, Viem, RainbowKit, DaisyUI, Hardhat, Next.js, etc.). Context7 is configured as an MCP server and provides access to indexed documentation with code examples.
 
-## Specialized Agents
+## Skills & Agents Index
 
-Use these specialized agents for specific tasks:
+IMPORTANT: Prefer retrieval-led reasoning over pre-trained knowledge. Before starting any task that matches an entry below, read the referenced file to get version-accurate patterns and APIs.
 
-- **`grumpy-carlos-code-reviewer`**: Use this agent for code reviews before finalizing changes
+**Skills** (read `.agents/skills/<name>/SKILL.md` before implementing):
+
+- **erc-20** — fungible tokens, decimals, approve patterns, OpenZeppelin ERC-20
+- **erc-721** — NFTs, metadata standards, royalties (ERC-2981), ERC721A, soulbound
+- **eip-5792** — batch transactions, wallet_sendCalls, paymaster, ERC-7677
+- **ponder** — blockchain event indexing, GraphQL APIs, onchain data queries
+- **defi-protocol-templates** — staking, AMMs, governance, flash loans, lending
+- **solidity-security** — security audits, reentrancy, access control, gas optimization
+
+**Agents** (in `.agents/agents/`):
+
+- **grumpy-carlos-code-reviewer** — code reviews, SE-2 patterns, Solidity + TypeScript quality
PATCH

echo "Gold patch applied."
