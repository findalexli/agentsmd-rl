# Enable FIFO Compaction for All Consensus Networks

## Problem

The Sui consensus layer currently uses RocksDB for persistent storage. The `RocksDBStore` supports FIFO compaction as an optimization, but this feature is currently disabled on Mainnet due to a network-specific guard in the initialization code.

In `consensus/core/src/authority_node.rs`, when initializing the `RocksDBStore`, the code has a conditional that disables FIFO compaction for Mainnet. This guard needs to be removed so that FIFO compaction can be enabled for all networks (devnet, testnet, and mainnet).

## Your Task

Modify `consensus/core/src/authority_node.rs` to:

1. Remove the Mainnet-specific guard that prevents FIFO compaction from being enabled on Mainnet
2. Clean up any imports that are no longer needed after removing the guard
3. Ensure the code compiles successfully

The fix should simplify the code that initializes `RocksDBStore::new()` so that it only passes the `use_fifo_compaction` parameter directly, without any network-specific exclusions.

## Hints

- Look for the `RocksDBStore::new()` call in the `AuthorityNode::start()` method
- The guard involves checking `context.protocol_config.chain()` against `ChainType::Mainnet`
- After removing the guard, you may need to adjust imports since `ChainType` may no longer be needed
- Run `cargo check -p consensus-core` to verify your changes compile
