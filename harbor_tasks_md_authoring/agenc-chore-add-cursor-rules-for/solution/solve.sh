#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agenc

# Idempotency guard
if grep -qF "- `SlashReason`: ProofFailed, ProofTimeout, InvalidResult" ".cursor/rules/anchor.mdc" && grep -qF "const deferral = new ProofDeferralManager(config, graph, ledger);" ".cursor/rules/runtime.mdc" && grep -qF "When modifying speculation code, always verify this invariant is maintained." ".cursor/rules/speculation.mdc" && grep -qF "AgenC is a privacy-preserving AI agent coordination protocol built on Solana. It" ".cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/anchor.mdc b/.cursor/rules/anchor.mdc
@@ -0,0 +1,85 @@
+---
+description: Rules for Anchor/Solana program development
+globs: ["**/programs/**/*.rs"]
+---
+
+# Anchor Program Rules
+
+## Account Structs
+
+When adding new account types:
+
+```rust
+#[account]
+pub struct MyAccount {
+    pub field1: Pubkey,
+    pub field2: u64,
+    pub bump: u8,
+}
+
+impl MyAccount {
+    // Calculate exact size: 8 (discriminator) + field sizes
+    pub const SIZE: usize = 8 + 32 + 8 + 1;
+}
+```
+
+## Instructions
+
+Follow existing patterns in `instructions/`:
+
+```rust
+#[derive(Accounts)]
+pub struct MyInstruction<'info> {
+    #[account(mut)]
+    pub signer: Signer<'info>,
+    
+    #[account(
+        init,
+        payer = signer,
+        space = MyAccount::SIZE,
+        seeds = [b"seed", key.as_ref()],
+        bump
+    )]
+    pub account: Account<'info, MyAccount>,
+    
+    pub system_program: Program<'info, System>,
+}
+```
+
+## Events
+
+Always emit events for state changes:
+
+```rust
+emit!(MyEvent {
+    field: value,
+    timestamp: Clock::get()?.unix_timestamp,
+});
+```
+
+## Error Codes
+
+Add to `errors.rs` with descriptive messages:
+
+```rust
+#[error_code]
+pub enum CoordinationError {
+    #[msg("Description of error")]
+    MyError,
+}
+```
+
+## Build Verification
+
+After changes:
+```bash
+anchor build
+anchor test
+```
+
+## Speculation-Specific Types
+
+- `DependencyType`: None, Data, Ordering, Proof
+- `SpeculativeCommitment`: On-chain commitment tracking
+- `SpeculationBond`: Stake bonding for agents
+- `SlashReason`: ProofFailed, ProofTimeout, InvalidResult
diff --git a/.cursor/rules/runtime.mdc b/.cursor/rules/runtime.mdc
@@ -0,0 +1,96 @@
+---
+description: Rules for TypeScript runtime development
+globs: ["**/runtime/**/*.ts", "**/sdk/**/*.ts"]
+---
+
+# Runtime Development Rules
+
+## File Structure
+
+```
+packages/runtime/src/task/
+├── index.ts              # Exports all modules
+├── dependency-graph.ts   # DAG for task relationships
+├── proof-pipeline.ts     # Async proof generation
+├── commitment-ledger.ts  # Speculative state tracking
+├── proof-deferral.ts     # Ancestor-aware proof ordering
+├── rollback-controller.ts # Cascade rollback handling
+├── speculative-executor.ts # Single-level speculation
+├── speculative-scheduler.ts # Main orchestrator
+├── speculation-metrics.ts # Observability
+└── __tests__/            # Test files
+```
+
+## Adding New Components
+
+1. Create the file with interfaces and class
+2. Export from `index.ts`
+3. Add tests alongside or in `__tests__/`
+
+## Interface Patterns
+
+```typescript
+// Config interface
+export interface MyComponentConfig {
+  optionA: number;
+  optionB: boolean;
+}
+
+// Events interface
+export interface MyComponentEvents {
+  onSomething?: (data: SomeType) => void;
+  onError?: (error: Error) => void;
+}
+
+// Main class
+export class MyComponent {
+  constructor(
+    private config: MyComponentConfig,
+    private events: MyComponentEvents = {}
+  ) {}
+  
+  // Always include stats
+  getStats(): object { return {}; }
+}
+```
+
+## Testing
+
+```typescript
+import { describe, it, expect, beforeEach } from 'vitest';
+
+describe('MyComponent', () => {
+  let component: MyComponent;
+  
+  beforeEach(() => {
+    component = new MyComponent({ optionA: 1, optionB: true });
+  });
+  
+  it('should do something', () => {
+    expect(component.getStats()).toBeDefined();
+  });
+});
+```
+
+## Build Commands
+
+```bash
+cd packages/runtime
+yarn build    # Compile TypeScript
+yarn test     # Run tests
+yarn test -- --grep "pattern"  # Run specific tests
+```
+
+## Speculation Components Integration
+
+```typescript
+// Creating the full speculation stack
+const graph = new DependencyGraph();
+const ledger = new CommitmentLedger({ maxCommitments: 1000 });
+const pipeline = new ProofPipeline({ maxConcurrentProofs: 5 });
+const deferral = new ProofDeferralManager(config, graph, ledger);
+const rollback = new RollbackController(config, graph, ledger);
+const scheduler = new SpeculativeTaskScheduler(
+  config, graph, ledger, deferral, rollback
+);
+```
diff --git a/.cursor/rules/speculation.mdc b/.cursor/rules/speculation.mdc
@@ -0,0 +1,57 @@
+---
+description: Rules for working with the speculative execution system
+globs: ["**/runtime/src/task/**", "**/speculation*"]
+---
+
+# Speculative Execution Rules
+
+## Critical Invariant
+
+**NEVER submit a proof until all ancestor proofs are confirmed on-chain.**
+
+When modifying speculation code, always verify this invariant is maintained.
+
+## Component Hierarchy
+
+```
+SpeculativeTaskScheduler (orchestrator)
+├── DependencyGraph (task relationships)
+├── CommitmentLedger (speculative state)
+├── ProofDeferralManager (proof ordering)
+│   └── ProofPipeline (async generation)
+├── RollbackController (failure handling)
+└── SpeculativeExecutor (execution)
+```
+
+## Adding New Speculation Features
+
+1. Check if it affects the critical invariant
+2. Add config option if behavior should be configurable
+3. Add event callback for observability
+4. Add metrics for monitoring
+5. Add tests covering edge cases
+
+## Speculation Decision Policy
+
+When deciding whether to speculate, check in order:
+1. Is speculation enabled?
+2. Is dependency type speculatable? (Data/Ordering yes, Proof no)
+3. Is depth within limit?
+4. Is stake within limit?
+5. Is claim window sufficient?
+
+## Rollback Handling
+
+When a proof fails:
+1. RollbackController traverses DependencyGraph (BFS)
+2. All downstream tasks are rolled back
+3. CommitmentLedger marks commitments as rolled_back
+4. Active tasks are aborted via AbortController
+5. Pending proofs are cancelled
+
+## Testing Requirements
+
+- Unit tests for each component
+- Integration tests for component interactions
+- Chaos tests for failure scenarios
+- Test the critical invariant explicitly
diff --git a/.cursorrules b/.cursorrules
@@ -0,0 +1,137 @@
+# AgenC Cursor Rules
+
+## Project Overview
+
+AgenC is a privacy-preserving AI agent coordination protocol built on Solana. It enables decentralized task coordination with zero-knowledge proofs for private task completions.
+
+## Critical Rules
+
+### Git Workflow
+- **NEVER push directly to main** - always create a branch and PR
+- **NEVER add Co-authored-by trailers** to commits
+- Every change needs a GitHub issue and PR
+
+### Code Style
+- **Never use em dashes (—)** - use commas, colons, or separate sentences
+- Follow existing patterns in the codebase
+- Use TypeScript for runtime code
+- Use Rust/Anchor for on-chain code
+
+## Architecture
+
+### Modules
+- **programs/agenc-coordination/** - Solana Anchor program
+- **packages/sdk/** - TypeScript SDK (@agenc/sdk)
+- **packages/runtime/** - Agent runtime (@agenc/runtime)
+- **circuits/** - ZK circuits (Circom/snarkjs)
+
+### Speculative Execution System
+
+The runtime includes a complete speculative execution system for overlapping task execution with proof generation.
+
+#### Core Components (packages/runtime/src/task/)
+
+| Component | File | Purpose |
+|-----------|------|---------|
+| DependencyGraph | dependency-graph.ts | DAG for task relationships |
+| ProofPipeline | proof-pipeline.ts | Async proof generation queue |
+| CommitmentLedger | commitment-ledger.ts | Tracks speculative state |
+| ProofDeferralManager | proof-deferral.ts | Ancestor-aware proof ordering |
+| RollbackController | rollback-controller.ts | Cascade rollback handling |
+| SpeculativeExecutor | speculative-executor.ts | Single-level speculation |
+| SpeculativeTaskScheduler | speculative-scheduler.ts | Main orchestrator |
+| ProofTimeEstimator | proof-time-estimator.ts | Claim expiry estimation |
+| SpeculationMetricsCollector | speculation-metrics.ts | Observability metrics |
+
+#### Critical Invariant
+
+**Proofs are NEVER submitted until all ancestor proofs are confirmed on-chain.**
+
+This is enforced in:
+- `ProofDeferralManager.canSubmit()`
+- `SpeculativeTaskScheduler.shouldSpeculate()`
+
+#### On-Chain Components (programs/agenc-coordination/src/)
+
+| Component | File | Purpose |
+|-----------|------|---------|
+| Task.depends_on | state.rs | Parent task dependency |
+| DependencyType | state.rs | Data/Ordering/Proof dependency types |
+| SpeculativeCommitment | state.rs | On-chain commitment tracking |
+| SpeculationBond | state.rs | Stake bonding for speculation |
+| SlashReason | state.rs | Proof failure slash reasons |
+| create_dependent_task | instructions/ | Create task with dependency |
+
+## Build Commands
+
+```bash
+# Anchor program
+anchor build
+anchor test
+
+# Runtime
+cd packages/runtime && yarn build && yarn test
+
+# SDK
+cd packages/sdk && yarn build && yarn test
+```
+
+## Design Documentation
+
+Comprehensive design docs at `docs/design/speculative-execution/`:
+- DESIGN-DOCUMENT.md - Full software design document
+- API-SPECIFICATION.md - TypeScript API reference
+- ON-CHAIN-SPECIFICATION.md - Anchor program spec
+- RISK-ASSESSMENT.md - FMEA with 43 failure modes
+- diagrams/ - UML, sequence, state machine diagrams
+- test-plans/ - Unit, integration, chaos test plans
+- runbooks/ - Deployment, operations, troubleshooting
+
+## Testing
+
+```bash
+# All runtime tests (~1300 tests)
+cd packages/runtime && yarn test
+
+# Speculation-specific tests
+yarn test -- --grep "speculation"
+yarn test -- --grep "DependencyGraph"
+yarn test -- --grep "CommitmentLedger"
+yarn test -- --grep "RollbackController"
+
+# Chaos tests
+yarn test -- --grep "chaos"
+```
+
+## Common Patterns
+
+### Adding a new speculation component
+
+1. Create file in `packages/runtime/src/task/`
+2. Export from `packages/runtime/src/task/index.ts`
+3. Add tests in `__tests__/` or alongside the file
+4. Follow existing patterns (events, config, stats)
+
+### Modifying on-chain state
+
+1. Update struct in `programs/agenc-coordination/src/state.rs`
+2. Update SIZE constant
+3. Run `anchor build` to regenerate IDL
+4. Update SDK types if needed
+
+### Creating dependent tasks
+
+```typescript
+// On-chain
+await program.methods.createDependentTask(
+  taskId,
+  { data: {} }, // DependencyType
+  // ... other params
+).accounts({
+  parentTask: parentTaskPda,
+  // ...
+}).rpc();
+
+// Runtime - query dependents
+const dependents = await getTasksByDependency(connection, programId, parentPda);
+```
PATCH

echo "Gold patch applied."
