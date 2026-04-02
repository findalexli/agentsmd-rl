# Slow inference service integration tests due to fixture re-creation

## Problem

The inference service integration test suite (`tests/experimental/inference_service/`) is
unnecessarily slow. Three test files — controller, data proxy, and gateway integration
tests — all suffer from the same root issue: expensive test fixtures (local scheduler,
gateway controller) are being torn down and recreated for every single test function,
even though the tests are read-only and don't mutate the fixtures.

Additionally, the test marker strategy is inconsistent. The tests use
`@pytest.mark.slow` on each class, but there is no module-level marker to select all
inference-service integration tests as a group (e.g., for targeted CI runs). The
per-class markers are redundant boilerplate.

Finally, the controller integration tests include coverage for a `should_accept_fn`
filtering feature, but that test coverage is incompatible with sharing the controller
fixture across tests. The `WorkflowExecutor` implementation holds state that prevents
re-entrance when `should_accept_fn` rejects trajectories at module scope. These tests
should be removed.

## Files involved

- `tests/experimental/inference_service/test_controller_integration.py`
  - `local_scheduler` fixture — creates a `LocalScheduler` with temp dirs
  - `gateway_controller` fixture — initializes a `GatewayInferenceController`
  - `gateway_controller_full_init` fixture — full init path controller
  - Test classes: `TestControllerLifecycle`, `TestControllerVersioning`,
    `TestControllerPauseResume`, `TestControllerRolloutBatch`,
    `TestControllerPrepareBatch`, `TestControllerSubmitWait`,
    `TestControllerFullInitialization`
- `tests/experimental/inference_service/test_data_proxy_integration.py`
  - Test classes: `TestChatCompletionsIntegration`, `TestPauseResumeIntegration`,
    `TestConcurrentPauseDuringGeneration`
- `tests/experimental/inference_service/test_gateway_integration.py`
  - Test classes: `TestGatewayStackHealth`, `TestGatewayChatCompletions`,
    `TestGatewaySessionLifecycle`, `TestGatewayAuth`, `TestGatewayPauseContinue`

## Expected behavior

1. Expensive fixtures should be created once per module, not once per test function
2. All three test files should have a single module-level marker for group selection
3. The per-class `@pytest.mark.slow` markers should be removed (the module marker replaces them)
4. Controller settings should be loosened to avoid throttling during setup/rollout
5. Tests that are incompatible with module-scoped fixtures should be removed
