# Task: Add Test for Denied Address Withdrawal

## Problem

The Sui blockchain has a coin deny list feature that allows blocking specific addresses from receiving certain coin types. However, there's a gap in test coverage: we need to verify that **withdrawals from denied addresses are also properly blocked**.

## What You Need to Do

Add a test case to verify that when an address is on the deny list for a regulated coin, that address cannot withdraw funds from a balance of that coin type.

## Relevant Files

- `crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move` - The main test file
- `crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap` - The expected output snapshot

## Context

The existing test already:
1. Creates a regulated coin type
2. Mints some coins to address A
3. Denies address B from receiving the coin
4. Verifies that sending to denied address B fails after epoch change
5. Removes the deny entry for address B
6. Verifies transactions work after undeny and epoch change

You need to add a test case between the epoch advance and the undeny operation that attempts to **withdraw funds from the denied account B** and verifies it fails with an appropriate error.

## Hints

1. Look at the existing test patterns in the file - they use transactional test directives like `//# programmable`, `//# run`, etc.
2. The test uses `sui::balance::send_funds` to transfer - you may need to use a similar balance operation for withdrawal
3. The snapshot file will need to be updated to reflect the new expected output (task count, error messages)
4. The test should be added as a new task block between the existing "advance-epoch" and "deny_list_v2_remove" tasks

## Expected Behavior

When address B tries to withdraw funds from a balance of the regulated coin type after being denied:
- The transaction should be rejected
- An error message should indicate that address B is denied for the coin type

## What to Modify

1. **Move test file** (`coin_deny_and_undeny_address_balance_receiver.move`):
   - Add `//# create-checkpoint` directive after the first successful transfer to B
   - Add a new programmable transaction block with `--sender B` that attempts to withdraw funds from the denied account
   - Use `sui::balance::redeem_funds` and `sui::balance::send_funds` in the withdrawal test

2. **Snapshot file** (`coin_deny_and_undeny_address_balance_receiver.snap`):
   - Update task count from "processed 11 tasks" to "processed 13 tasks"
   - Remove the `assertion_line:` entry
   - Add expected error output for the withdrawal test showing address B is denied
   - Update task numbering for all subsequent tasks
