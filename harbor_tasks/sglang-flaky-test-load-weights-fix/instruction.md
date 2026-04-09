# Fix flaky test_load_weights_from_remote_instance in CI

## Problem

The `test_load_weights_from_remote_instance` test in CI is flaky. It uses `random.choice()` to select between different modes and backends:

```python
if is_in_ci():
    mode = random.choice(["Engine", "Server"])
    remote_instance_loader_backend = random.choice(["nccl", "transfer_engine"])
```

This randomness causes the test to fail intermittently when the "transfer_engine" backend is selected with "Engine" mode. The root cause appears to be that when using the `transfer_engine` backend, the `remote_instance_weight_loader_start_seed_via_transfer_engine` parameter is set to `True` (because it's conditionally set based on `remote_instance_loader_backend == "transfer_engine"`), but this configuration is unreliable.

The `Engine` + `transfer_engine` combination hangs during initialization on 2-GPU H100 runners. The original CI flakiness is because `random.choice` picks `transfer_engine` ~50% of the time.

## Expected Behavior

The test should be more deterministic and avoid the problematic configuration. The fix should:

1. Hardcode `remote_instance_weight_loader_start_seed_via_transfer_engine=False` instead of conditionally setting it based on the backend type
2. Add a FIXME comment acknowledging that the test needs refactoring to have less random behavior

## Files to Look At

- `test/registered/distributed/test_load_weights_from_remote_instance.py` — The flaky distributed test that loads weights from a remote instance

Look specifically at:
1. The `init_process_dst` function where `sgl.Engine` is initialized
2. The `test_load_weights_from_remote_instance` method where `random.choice` is called

Note: This is a GPU-dependent integration test. The fix should make the configuration more stable by disabling the transfer_engine seed path that causes hangs.
