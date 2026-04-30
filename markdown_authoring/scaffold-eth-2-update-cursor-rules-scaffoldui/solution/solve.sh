#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scaffold-eth-2

# Idempotency guard
if grep -qF "With the `@scaffold-ui/components` library, SE-2 provides a set of pre-built Rea" ".cursor/rules/scaffold-eth.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/scaffold-eth.mdc b/.cursor/rules/scaffold-eth.mdc
@@ -1,8 +1,9 @@
 ---
-description: 
-globs: 
+description:
+globs:
 alwaysApply: true
 ---
+
 This codebase contains Scaffold-ETH 2 (SE-2), everything you need to build dApps on Ethereum. Its tech stack is NextJS, RainbowKit, Wagmi and Typescript. Supports Hardhat and Foundry.
 
 It's a yarn monorepo that contains two main packages:
@@ -31,6 +32,7 @@ The usual dev flow is:
 SE-2 provides a set of hooks that facilitates contract interactions from the UI. It reads the contract data from `deployedContracts.ts` and `externalContracts.ts`, located in `packages/nextjs/contracts`.
 
 ### Reading data from a contract
+
 Use the `useScaffoldReadContract` (`packages/nextjs/hooks/scaffold-eth/useScaffoldReadContract.ts`) hook. Example:
 
 ```typescript
@@ -42,11 +44,13 @@ const { data: someData } = useScaffoldReadContract({
 ```
 
 ### Writing data to a contract
+
 Use the `useScaffoldWriteContract` (`packages/nextjs/hooks/scaffold-eth/useScaffoldWriteContract.ts`) hook.
+
 1. Initilize the hook with just the contract name
 2. Call the `writeContractAsync` function.
 
- Example:
+Example:
 
 ```typescript
 const { writeContractAsync: writeYourContractAsync } = useScaffoldWriteContract(
@@ -100,15 +104,18 @@ The `data` property consists of an array of events and can be displayed as:
 ```
 
 ### Other Hooks
+
 SE-2 also provides other hooks to interact with blockchain data: `useScaffoldWatchContractEvent`, `useScaffoldEventHistory`, `useDeployedContractInfo`, `useScaffoldContract`, `useTransactor`. They live under `packages/nextjs/hooks/scaffold-eth`.
 
 ## Display Components guidelines
-SE-2 provides a set of pre-built React components for common Ethereum use cases: 
+
+With the `@scaffold-ui/components` library, SE-2 provides a set of pre-built React components for common Ethereum use cases:
+
 - `Address`: Always use this when displaying an ETH address
 - `AddressInput`: Always use this when users need to input an ETH address
 - `Balance`: Display the ETH/USDC balance of a given address
 - `EtherInput`: An extended number input with ETH/USD conversion.
 
-They live under `packages/nextjs/components/scaffold-eth`.
+For fully customizable components, you can use the hooks from the `@scaffold-ui/hooks` library to get the data you need.
 
 Find the relevant information from the documentation and the codebase. Think step by step before answering the question.
PATCH

echo "Gold patch applied."
