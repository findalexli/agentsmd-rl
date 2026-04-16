# Fix flaky test_load_weights_from_remote_instance in CI

## Problem

The `test_load_weights_from_remote_instance` test in CI is flaky due to nondeterministic configuration selection. The test uses `random.choice()` to select between different modes and backends:

```python
if is_in_ci():
    mode = random.choice(["Engine", "Server"])
    remote_instance_loader_backend = random.choice(["nccl", "transfer_engine"])
```

When the random selection picks certain combinations, the test hangs during initialization on 2-GPU H100 runners.

## Required Changes

1. **Add a FIXME comment** about the random behavior. Add the following comment immediately before the `random.choice()` calls in the CI conditional block:
   ```python
   # FIXME: refactor this test to have less random behavior
   ```

2. **Stabilize the configuration parameter** that causes the hang. The parameter `remote_instance_weight_loader_start_seed_via_transfer_engine` is currently set conditionally based on the randomly-selected backend. Change it to be **hardcoded to `False`** instead of being conditional on the backend type.

   Before:
   ```python
   remote_instance_weight_loader_start_seed_via_transfer_engine=(
       remote_instance_loader_backend == "transfer_engine"
   )
   ```

   After:
   ```python
   remote_instance_weight_loader_start_seed_via_transfer_engine=False
   ```

## Expected Behavior

The test should be more deterministic. Making the configuration stable (by hardcoding `remote_instance_weight_loader_start_seed_via_transfer_engine` to `False` and adding the FIXME comment) resolves the hangs on 2-GPU runners.

## Files to Look At

- `test/registered/distributed/test_load_weights_from_remote_instance.py` — The distributed test that loads weights from a remote instance

## Notes

- This is a GPU-dependent integration test.
- The fix should stabilize the configuration that causes the hang by making `remote_instance_weight_loader_start_seed_via_transfer_engine` unconditional (hardcoded to `False`) rather than dependent on random backend selection.
- The FIXME comment must exactly match: `# FIXME: refactor this test to have less random behavior`
