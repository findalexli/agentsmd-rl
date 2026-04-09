# Task: Add Probe-Before-Fetch to Consensus Commit Sync

## Problem

When fetching commits and blocks from peers in the consensus layer, the system currently commits to full fetches without checking if the peer is reachable first. This causes unnecessary delays when peers are unavailable or slow.

Additionally, the timeout values for commit sync operations are hardcoded, making it difficult to tune them for different network conditions.

## What You Need to Do

1. **Add configurable timeout parameters** to the consensus config:
   - `commit_sync_request_timeout`: Base per-request timeout for commit sync fetches (default: 10s)
   - `commit_sync_probe_timeout`: Short timeout for connectivity probes before fetching (default: 2s)

2. **Implement a connectivity probe mechanism** in the network client that can quickly check if a peer is reachable before committing to a full fetch.

3. **Update the commit syncer** to:
   - Use the configurable `commit_sync_request_timeout` instead of the hardcoded constant
   - Call the connectivity probe before fetching commits from a peer
   - Use `commit_sync_probe_timeout` for the probe operation

4. **Implement the `ObserverNetworkService` trait** for `AuthorityService` with stub methods for:
   - `handle_stream_blocks`
   - `handle_fetch_blocks`
   - `handle_fetch_commits`

## Relevant Files

- `consensus/config/src/parameters.rs` - Add the new timeout parameters with defaults
- `consensus/config/tests/snapshots/parameters_test__parameters.snap` - Update snapshot test
- `consensus/core/src/network/clients.rs` - Add `probe_connectivity` method to `NetworkClient`
- `consensus/core/src/commit_syncer.rs` - Use configurable timeout and call probe before fetch
- `consensus/core/src/authority_service.rs` - Implement `ObserverNetworkService` trait

## Hints

- The probe should use a short timeout (2 seconds) to quickly skip unreachable peers
- The full fetch timeout should be configurable and grow progressively with a multiplier
- Look at existing network client methods to understand the pattern for adding new functionality
- The `ObserverNetworkService` trait methods can return `Not yet implemented` errors for now

## Testing

Run the following to verify your changes:

```bash
# Check compilation
cargo check -p consensus-core -p consensus-config

# Run the parameter tests
cargo test -p consensus-config --lib parameters_test
```

All tests must pass before submitting.
