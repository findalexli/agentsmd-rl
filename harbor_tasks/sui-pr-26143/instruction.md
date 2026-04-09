# Task: Remove Certified Blocks Sender Channel

## Problem

The `certified_blocks_sender` channel in `TransactionCertifier` is dead code that should be removed. This channel was used to send certified blocks out of consensus for processing, but is no longer needed.

## Files to Modify

The changes span the following files in `consensus/core/src/`:

1. **transaction_certifier.rs** - Primary file to modify:
   - Remove `certified_blocks_sender` field from `TransactionCertifier` struct
   - Remove `certified_blocks_sender` parameter from `TransactionCertifier::new()`
   - Remove `send_certified_blocks()` method
   - Update `add_voted_blocks()` to not send to the channel
   - Update `add_proposed_block()` to not send to the channel
   - Remove import of `UnboundedSender` and `CertifiedBlocksOutput`

2. **block.rs**:
   - Remove `CertifiedBlocksOutput` struct definition

3. **lib.rs**:
   - Remove `CertifiedBlocksOutput` from public exports

4. **commit_consumer.rs**:
   - Remove `block_sender` field from `CommitConsumerArgs`
   - Remove creation of block_sender channel

5. **authority_node.rs**:
   - Update `TransactionCertifier::new()` call to remove `block_sender` argument

6. **authority_service.rs**:
   - Update test code - remove blocks_sender channel creation and remove it from `TransactionCertifier::new()` calls (multiple test functions)

7. **commit_observer.rs**:
   - Update test code - remove blocks_sender channel creation and argument

8. **commit_syncer.rs**:
   - Update test code similarly

9. **commit_test_fixture.rs**:
   - Update test fixture similarly

10. **core.rs**:
    - Update test code similarly (many test functions)

11. **core_thread.rs**:
    - Update test code similarly

12. **synchronizer.rs**:
    - Update test code similarly

13. **benches/commit_finalizer_bench.rs**:
    - Update benchmark code similarly

## What to Do

1. The `TransactionCertifier` struct should only keep 3 fields after the removal
2. The `TransactionCertifier::new()` function should take only 3 parameters
3. Remove the `send_certified_blocks()` helper method entirely
4. Update `add_voted_blocks()` and `add_proposed_block()` to simply call the state methods without sending to any channel
5. Remove the `CertifiedBlocksOutput` type from the codebase
6. Update all call sites in test files to not pass the `blocks_sender` argument

## Agent Config Rules

From CLAUDE.md:
- **ALWAYS run `cargo xclippy` after finishing development** to ensure code passes all linting checks
- **NEVER disable or ignore tests** - all tests must pass and be enabled
- **All unit tests must work properly** - use `#[tokio::test]` for async tests
- When compiling, set timeout limits to at least 10 minutes
- Use `cargo nextest --lib` to run only library tests for faster feedback
- Use `-p consensus-core` to run only the consensus core crate
