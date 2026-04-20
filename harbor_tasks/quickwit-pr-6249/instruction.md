# Quickwit Ingester Status Bug

## Symptom

When performing a rolling deployment of Quickwit, the new control plane nodes start with incomplete information about cluster ingesters. Old ingesters (running the previous version) do not broadcast their `IngesterStatus`, causing the new control plane to see only the new ingesters as `Ready`. This results in all shards being placed exclusively on new ingesters, which breaks cluster operations until the deployment completes and all old ingesters are restarted.

## Expected Behavior

An ingester that has not yet broadcast its status should be treated as `Ready`. The cluster's shard routing should function correctly during rolling deployments, with ingesters that haven't reported their status being assumed ready to receive shards.

## The Problem

The `ingester_status()` method in `quickwit/quickwit-cluster/src/member.rs` retrieves the ingester's status from the node state. When an ingester hasn't broadcast its status yet, the key is absent from the node state. The current implementation returns an incorrect value when the key is missing.

## Verification

After applying the fix:
1. The specific test `test_ingester_status_defaults_to_ready_when_key_absent` should pass
2. The `ingester_status()` function should return `IngesterStatus::Ready` when the `INGESTER_STATUS_KEY` is absent from the node state
3. All existing tests in `quickwit-cluster` should continue to pass

## Context

- Ingester status is stored in node state using `INGESTER_STATUS_KEY`
- The status is broadcast by ingesters during cluster membership exchanges
- During a rolling deployment, old and new versions coexist temporarily
- The control plane relies on accurate ingester status to route shards appropriately