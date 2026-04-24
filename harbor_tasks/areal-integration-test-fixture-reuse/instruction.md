# Slow inference service integration tests due to fixture re-creation

## Problem

The inference service integration test suite (`tests/experimental/inference_service/`) is
unnecessarily slow. Test files under this directory all suffer from the same root issue:
expensive fixtures are being torn down and recreated for every single test function,
even though the tests are read-only and don't mutate the fixtures.

Additionally, the test marker strategy is inconsistent. Classes use `@pytest.mark.slow`,
but there is no module-level marker to select all inference-service integration tests
as a group for targeted CI runs.

Some tests in the controller test file use a stateful trajectory filter that prevents
re-entrance when shared across module-scoped fixtures. These tests are incompatible
with fixture reuse and must be removed.

## Files involved

- `tests/experimental/inference_service/test_controller_integration.py`
- `tests/experimental/inference_service/test_data_proxy_integration.py`
- `tests/experimental/inference_service/test_gateway_integration.py`

## Expected behavior

1. Fixtures that are expensive to create should be scoped to the module level
   (`scope="module"` or `scope="session"`), so they are created once per file
   rather than once per test. The fixtures to update are:
   - `local_scheduler` (in `test_controller_integration.py`)
   - `gateway_controller` (in `test_controller_integration.py`)
   - `gateway_controller_full_init` (in `test_controller_integration.py`)

   When changing fixture scope to module or session, the function parameters must
   be compatible with module scope. Specifically:
   - `local_scheduler` must accept `tmp_path_factory` instead of `tmp_path`
   - `gateway_controller` and `gateway_controller_full_init` must NOT have
     `tmp_path` as a parameter (function-scoped fixtures cannot be used with
     module-scoped fixtures)

2. Each of the three test files should have a module-level `pytestmark` variable
   assigned to `pytest.mark.sglang`. When the assignment `pytestmark = pytest.mark.sglang`
   is evaluated at runtime, it must resolve to `pytest.mark.sglang`.

3. Per-class `@pytest.mark.slow` decorators should be removed from all test classes,
   as the module-level marker replaces them.

4. Controller fixture settings need sufficient values to avoid throttling when fixtures
   are shared across multiple tests. The following parameters must meet minimum values:
   - `max_head_offpolicyness` must be >= 100 (in both `gateway_controller` and
     `gateway_controller_full_init`)
   - `consumer_batch_size` must be >= 3 (in `gateway_controller`)

5. Tests that cannot be shared across module-scoped fixtures due to stateful
   trajectory filtering must be removed from the controller integration tests.
   Any test method whose name contains the string `should_accept_fn` must be removed.