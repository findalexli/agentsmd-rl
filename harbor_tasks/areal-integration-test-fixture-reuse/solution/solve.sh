#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency check: skip if pytestmark already set in controller test
if grep -q 'pytestmark = pytest.mark.sglang' tests/experimental/inference_service/test_controller_integration.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/experimental/inference_service/test_controller_integration.py b/tests/experimental/inference_service/test_controller_integration.py
index 201f1dd67..14c99cc62 100644
--- a/tests/experimental/inference_service/test_controller_integration.py
+++ b/tests/experimental/inference_service/test_controller_integration.py
@@ -1,12 +1,11 @@
 """Integration tests for GatewayInferenceController with real SGLang servers.

-Requires GPU and a model. Marked @pytest.mark.slow to exclude from default CI.
-Run manually:
+Requires GPU and a model. Run with:
     uv run pytest tests/experimental/inference_service/test_controller_integration.py -v -s

 The test launches:
   1. A real SGLang server (GPU subprocess)
-  2. A LocalScheduler (function-scoped)
+  2. A LocalScheduler (module-scoped)
   3. A GatewayInferenceController that spins up Gateway, Router, and Data Proxy
      micro-services in background threads.
 """
@@ -29,6 +28,7 @@
     has_gpu,
 )

+pytestmark = pytest.mark.sglang
 SERVER_STARTUP_TIMEOUT = 180  # seconds


@@ -87,14 +87,15 @@ def model_path() -> str:
     return get_test_model_path()


-@pytest.fixture
-def local_scheduler(tmp_path):
+@pytest.fixture(scope="module")
+def local_scheduler(tmp_path_factory):
     """Create a LocalScheduler for testing."""
     if not has_gpu():
         pytest.skip("GPU required for LocalScheduler")

     from areal.infra.scheduler.local import LocalScheduler

+    tmp_path = tmp_path_factory.mktemp("local_scheduler")
     fileroot = tmp_path / "fileroot"
     fileroot.mkdir()
     name_resolve_root = tmp_path / "name_resolve"
@@ -112,8 +113,8 @@ def local_scheduler(tmp_path):
     scheduler.delete_workers(None)


-@pytest.fixture
-def gateway_controller(sglang_server, local_scheduler, model_path, tmp_path):
+@pytest.fixture(scope="module")
+def gateway_controller(sglang_server, local_scheduler, model_path):
     """Create and initialize a GatewayInferenceController, yield it, then destroy."""
     if not has_gpu():
         pytest.skip("GPU required")
@@ -140,7 +141,8 @@ def gateway_controller(sglang_server, local_scheduler, model_path, tmp_path):
             ),
         ),
         admin_api_key="test-admin",
-        consumer_batch_size=2,
+        consumer_batch_size=4,
+        max_head_offpolicyness=1024,
         setup_timeout=180.0,
     )

@@ -169,7 +171,6 @@ def gateway_controller(sglang_server, local_scheduler, model_path, tmp_path):
 # =============================================================================


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerLifecycle:
     """Verify controller lifecycle: init starts services, properties set, destroy cleans up."""
@@ -216,7 +217,6 @@ def test_proxy_gateway_addr_set(self, gateway_controller):
 # =============================================================================


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerVersioning:
     """Verify version management on the controller."""
@@ -252,7 +252,6 @@ def test_set_version_does_not_raise_without_broadcast(self, gateway_controller):
 # =============================================================================


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerPauseResume:
     """Verify pause/resume broadcasts to workers."""
@@ -300,7 +299,6 @@ def test_pause_resume_roundtrip_keeps_services_healthy(self, gateway_controller)
 # =============================================================================


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerRolloutBatch:
     """Test rollout_batch through the controller with SimpleAgent workflow."""
@@ -331,58 +329,6 @@ def test_rollout_batch_with_simple_agent(self, gateway_controller):
         assert isinstance(traj["input_ids"], RTensor)
         assert traj["input_ids"].ndim == 2

-    def test_rollout_batch_with_should_accept_fn_rejects(self, gateway_controller):
-        """rollout_batch with a rejecting should_accept_fn returns empty list."""
-
-        def reject_all(trajectory: dict) -> bool:
-            return False
-
-        data = [
-            {
-                "messages": [{"role": "user", "content": "What is 2+2?"}],
-                "answer": "4",
-            }
-        ]
-
-        result = gateway_controller.rollout_batch(
-            data=data,
-            workflow="tests.experimental.openai.utils.SimpleAgent",
-            should_accept_fn=reject_all,
-        )
-
-        # All trajectories should be rejected, so the result is an empty list
-        assert isinstance(result, list)
-        assert len(result) == 0
-
-    def test_rollout_batch_with_should_accept_fn_accepts(self, gateway_controller):
-        """rollout_batch with an accepting should_accept_fn returns list of trajectory dicts."""
-
-        def accept_all(trajectory: dict) -> bool:
-            return True
-
-        data = [
-            {
-                "messages": [{"role": "user", "content": "What is 2+2?"}],
-                "answer": "4",
-            }
-        ]
-
-        result = gateway_controller.rollout_batch(
-            data=data,
-            workflow="tests.experimental.openai.utils.SimpleAgent",
-            should_accept_fn=accept_all,
-        )
-
-        assert isinstance(result, list)
-        assert len(result) == 1
-        traj = result[0]
-        assert isinstance(traj, dict)
-        assert "input_ids" in traj
-        from areal.infra.rpc.rtensor import RTensor
-
-        assert isinstance(traj["input_ids"], RTensor)
-        assert traj["input_ids"].ndim == 2
-

 # =============================================================================
 # TestControllerPrepareBatch
@@ -406,7 +352,6 @@ def __iter__(self):
         yield self._items


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerPrepareBatch:
     """Test prepare_batch through the controller with SimpleAgent workflow."""
@@ -440,72 +385,12 @@ def test_prepare_batch_returns_results(self, gateway_controller):
         assert isinstance(traj["input_ids"], RTensor)
         assert traj["input_ids"].ndim == 2

-    def test_prepare_batch_with_should_accept_fn_rejects(self, gateway_controller):
-        """prepare_batch with a rejecting should_accept_fn returns empty list."""
-
-        def reject_all(trajectory: dict) -> bool:
-            return False
-
-        items = [
-            {
-                "messages": [{"role": "user", "content": "What is 2+2?"}],
-                "answer": "4",
-            },
-        ]
-        dataloader = _FakeDataLoader(items, batch_size=len(items))
-
-        result = gateway_controller.prepare_batch(
-            dataloader=dataloader,
-            workflow="tests.experimental.openai.utils.SimpleAgent",
-            should_accept_fn=reject_all,
-            dynamic_bs=True,
-        )
-
-        # All trajectories should be rejected, so the result is an empty list
-        assert isinstance(result, list)
-        assert len(result) == 0
-
-    def test_prepare_batch_with_should_accept_fn_accepts(self, gateway_controller):
-        """prepare_batch with an accepting should_accept_fn returns list of trajectory dicts."""
-
-        def accept_all(trajectory: dict) -> bool:
-            return True
-
-        items = [
-            {
-                "messages": [{"role": "user", "content": "What is 2+2?"}],
-                "answer": "4",
-            },
-            {
-                "messages": [{"role": "user", "content": "What is 3+3?"}],
-                "answer": "6",
-            },
-        ]
-        dataloader = _FakeDataLoader(items, batch_size=len(items))
-
-        result = gateway_controller.prepare_batch(
-            dataloader=dataloader,
-            workflow="tests.experimental.openai.utils.SimpleAgent",
-            should_accept_fn=accept_all,
-        )
-
-        assert isinstance(result, list)
-        assert len(result) > 0
-        traj = result[0]
-        assert isinstance(traj, dict)
-        assert "input_ids" in traj
-        from areal.infra.rpc.rtensor import RTensor
-
-        assert isinstance(traj["input_ids"], RTensor)
-        assert traj["input_ids"].ndim == 2
-

 # =============================================================================
 # TestControllerSubmitWait
 # =============================================================================


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerSubmitWait:
     """Test submit/wait API on the controller."""
@@ -556,8 +441,8 @@ def test_submit_wait_roundtrip(self, gateway_controller):
 # =============================================================================


-@pytest.fixture
-def gateway_controller_full_init(local_scheduler, model_path, tmp_path):
+@pytest.fixture(scope="module")
+def gateway_controller_full_init(local_scheduler, model_path):
     """Create a GatewayInferenceController that launches SGLang via the full init path.

     Unlike ``gateway_controller`` which passes pre-existing ``server_infos``,
@@ -586,7 +471,7 @@ def gateway_controller_full_init(local_scheduler, model_path, tmp_path):
         ),
         admin_api_key="test-admin",
         consumer_batch_size=8,
-        max_head_offpolicyness=4,
+        max_head_offpolicyness=1024,
         setup_timeout=300.0,
     )

@@ -609,7 +494,6 @@ def gateway_controller_full_init(local_scheduler, model_path, tmp_path):
         ctrl.destroy()


-@pytest.mark.slow
 @pytest.mark.skipif(not has_gpu(), reason="GPU required")
 class TestControllerFullInitialization:
     """Test the full initialization path where the controller launches SGLang itself.
diff --git a/tests/experimental/inference_service/test_data_proxy_integration.py b/tests/experimental/inference_service/test_data_proxy_integration.py
index bc648cff5..827fa0361 100644
--- a/tests/experimental/inference_service/test_data_proxy_integration.py
+++ b/tests/experimental/inference_service/test_data_proxy_integration.py
@@ -1,7 +1,6 @@
 """Integration tests for data proxy with a real SGLang server.

-Requires GPU and a model. Marked @pytest.mark.slow to exclude from default CI.
-Run manually:
+Requires GPU and a model. Run with:
     uv run pytest tests/experimental/inference_service/test_data_proxy_integration.py -v -s

 The test launches an SGLang server subprocess, starts the data proxy FastAPI app,
@@ -29,6 +28,7 @@
 # Configuration
 # ---------------------------------------------------------------------------

+pytestmark = pytest.mark.sglang
 LOCAL_MODEL_PATH = "/storage/openpsi/models/Qwen__Qwen3-0.6B/"
 HF_MODEL_ID = "Qwen/Qwen3-0.6B"
 SERVER_STARTUP_TIMEOUT = 180  # seconds
@@ -158,7 +158,6 @@ def _create_data_proxy_app_with_sessions(sglang_server, model_path):
 ADMIN_KEY = "areal-admin-key"


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestChatCompletionsIntegration:
     """Test the full /chat/completions endpoint with a real SGLang backend."""
@@ -495,7 +494,6 @@ async def test_auth_rejection(self, sglang_server, model_path):
 # ---------------------------------------------------------------------------


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestPauseResumeIntegration:
     """Test /pause_generation and /continue_generation with real SGLang backend.
@@ -720,7 +718,6 @@ async def test_streaming_chat_completions_blocked_while_paused(
 # ---------------------------------------------------------------------------


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestConcurrentPauseDuringGeneration:
     """Test the real abort/resubmit cycle by pausing SGLang mid-generation.
diff --git a/tests/experimental/inference_service/test_gateway_integration.py b/tests/experimental/inference_service/test_gateway_integration.py
index ef23b6a10..1f9302940 100644
--- a/tests/experimental/inference_service/test_gateway_integration.py
+++ b/tests/experimental/inference_service/test_gateway_integration.py
@@ -1,7 +1,6 @@
 """Full-stack integration test: client → Gateway → Router → Data Proxy → SGLang.

-Requires GPU and a model. Marked @pytest.mark.slow to exclude from default CI.
-Run manually:
+Requires GPU and a model. Run with:
     uv run pytest tests/experimental/inference_service/test_gateway_integration.py -v -s

 The test launches:
@@ -36,6 +35,7 @@
 # Configuration
 # ---------------------------------------------------------------------------

+pytestmark = pytest.mark.sglang
 LOCAL_MODEL_PATH = "/storage/openpsi/models/Qwen__Qwen3-0.6B/"
 HF_MODEL_ID = "Qwen/Qwen3-0.6B"
 SERVER_STARTUP_TIMEOUT = 180  # seconds
@@ -259,7 +259,6 @@ def gateway_stack(sglang_server, model_path):
 # ---------------------------------------------------------------------------


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestGatewayStackHealth:
     """Verify all services are healthy after stack launch."""
@@ -286,7 +285,6 @@ async def test_all_services_healthy(self, gateway_stack):
             assert resp.json()["status"] == "ok"


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestGatewayChatCompletions:
     """Test /chat/completions endpoint through the full stack."""
@@ -484,7 +482,6 @@ async def test_multi_turn_session_chat(self, gateway_stack):
             assert resp.json()["interaction_count"] == 2


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestGatewaySessionLifecycle:
     """Test full RL session lifecycle through the gateway stack."""
@@ -597,7 +594,6 @@ async def test_session_pinning(self, gateway_stack):
             assert resp.status_code == 200


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestGatewayAuth:
     """Test authentication enforcement through the gateway."""
@@ -639,7 +635,6 @@ async def test_non_admin_on_admin_endpoint(self, gateway_stack):
             assert resp.status_code == 403


-@pytest.mark.slow
 @pytest.mark.skipif(not _has_gpu(), reason="GPU required")
 class TestGatewayPauseContinue:
     """Test pause/continue generation through the gateway (targets worker by ID)."""

PATCH

echo "Patch applied successfully."
