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
   (`scope="module"`), so they are created once per file rather than once per test.
   The `local_scheduler` fixture must be changed to use `tmp_path_factory` parameter
   instead of `tmp_path` to be compatible with module scope.

2. Each of the three test files should have a module-level `pytestmark` variable
   assigned to a `pytest.mark.<marker>` expression, where `<marker>` is the identifier
   registered for this test suite. The marker must be accessible as `pytest.mark.<marker>`
   at runtime when the assignment is evaluated.

3. Per-class `@pytest.mark.slow` decorators should be removed from all test classes,
   as the module-level marker replaces them.

4. Controller fixture settings need sufficient values to avoid throttling when fixtures
   are shared across multiple tests:
   - `gateway_controller` fixture: `consumer_batch_size` argument must be >= 3
   - `gateway_controller_full_init` fixture: `max_head_offpolicyness` argument must be >= 100

5. Tests that cannot be shared across module-scoped fixtures due to stateful
   trajectory filtering must be removed from the controller integration tests.
   Specifically, any test method whose name contains `should_accept_fn` must be removed.