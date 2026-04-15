# Fix flaky test_load_weights_from_remote_instance in CI

## Problem

The `test_load_weights_from_remote_instance` test in CI is flaky due to nondeterministic configuration selection. The test uses `random.choice()` to select between different modes and backends:

```python
if is_in_ci():
    mode = random.choice(["Engine", "Server"])
    remote_instance_loader_backend = random.choice(["nccl", "transfer_engine"])
```

When the random selection picks certain combinations, the test hangs during initialization on 2-GPU H100 runners. Investigation shows the hangs are tied to a configuration flag that gets set conditionally based on the randomly-selected backend.

## Expected Behavior

The test should be more deterministic. The flaky combination causes a hang during initialization that manifests as a timeout. Making the configuration stable (rather than conditional on the random backend selection) resolves the hangs.

## Files to Look At

- `test/registered/distributed/test_load_weights_from_remote_instance.py` — The distributed test that loads weights from a remote instance

Look at the `init_process_dst` function (where `sgl.Engine` is initialized) and the `test_load_weights_from_remote_instance` method (where `random.choice` is called).

## Notes

- This is a GPU-dependent integration test.
- The fix should stabilize the configuration that causes the hang by making it unconditional rather than dependent on random selection.
