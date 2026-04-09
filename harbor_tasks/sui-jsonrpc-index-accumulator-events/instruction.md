# Fix JSON-RPC Index to Include Address Balance Recipients

## Problem

The `transactions_to_addr` index in the JSON-RPC index store is incomplete. It currently only tracks addresses that receive objects through `mutated_objects`, but it doesn't account for addresses that receive funds via **accumulator events**.

With the address balances feature, a recipient can receive funds through accumulator events without any object ownership changes. As a result, transactions that transfer funds via accumulator events are not being indexed for the recipient's address, causing `queryTransactionBlocks` with the `ToAddress` filter to miss these transactions.

## What You Need to Do

Modify the `IndexStore` implementation in `crates/sui-core/src/jsonrpc_index.rs` to include addresses from accumulator events in the `transactions_to_addr` index.

### Key Details

1. **Location**: Look for the code that populates `transactions_to_addr` in the `index_transaction` method (around line 1112)

2. **Current behavior**: The index only captures addresses from `mutated_objects`:
   ```rust
   batch.insert_batch(
       &self.tables.transactions_to_addr,
       mutated_objects.filter_map(|(_, owner)| {
           owner.get_address_owner_address().ok().map(|addr| ((addr, sequence), digest))
       }),
   )?;
   ```

3. **Required change**: Also include addresses from `accumulator_events`. Each accumulator event has an address accessible via `event.write.address.address`.

4. **Approach**: Create a combined iterator (`affected_addresses`) that:
   - Starts with the existing `mutated_objects.filter_map(...)` iterator
   - Chains in the addresses from `accumulator_events.iter().map(...)`
   - Passes this combined iterator to `batch.insert_batch`

5. **Add a descriptive comment**: Explain that the index now includes both objects sent to addresses AND accumulator event addresses.

## Testing

After your changes:
- The code should compile (`cargo check -p sui-core`)
- The affected_addresses iterator should chain both mutated_objects and accumulator_events
- The batch.insert_batch call should use this combined iterator

## Constraints

- Do NOT modify any other files
- Keep the existing logic for `mutated_objects` intact - just extend it
- The change should be minimal and focused on the indexing fix
