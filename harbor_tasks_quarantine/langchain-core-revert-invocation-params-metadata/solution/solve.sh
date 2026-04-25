#!/bin/bash
set -e

cd /workspace/langchain

# Check if already applied (idempotency check)
if ! grep -q "_get_metadata_invocation_params" libs/core/langchain_core/language_models/chat_models.py; then
    echo "Patch already applied or method already removed"
    exit 0
fi

# Apply the gold patch - revert the invocation params metadata feature
patch -p1 << 'PATCH'
diff --git a/libs/core/langchain_core/language_models/chat_models.py b/libs/core/langchain_core/language_models/chat_models.py
index 4e4e3ab6d24a1..f30b84199641f 100644
--- a/libs/core/langchain_core/language_models/chat_models.py
+++ b/libs/core/langchain_core/language_models/chat_models.py
@@ -556,7 +556,6 @@ def stream(
             params = self._get_invocation_params(stop=stop, **kwargs)
             options = {"stop": stop, **kwargs, **ls_structured_output_format_dict}
             inheritable_metadata = {
-                **self._get_metadata_invocation_params(params),
                 **(config.get("metadata") or {}),
                 **self._get_ls_params_with_defaults(stop=stop, **kwargs),
             }
@@ -685,7 +684,6 @@ async def astream(
         params = self._get_invocation_params(stop=stop, **kwargs)
         options = {"stop": stop, **kwargs, **ls_structured_output_format_dict}
         inheritable_metadata = {
-            **self._get_metadata_invocation_params(params),
             **(config.get("metadata") or {}),
             **self._get_ls_params_with_defaults(stop=stop, **kwargs),
         }
@@ -839,18 +837,6 @@ def _get_invocation_params(
         params["stop"] = stop
         return {**params, **kwargs}

-    def _get_metadata_invocation_params(
-        self,
-        invocation_params: dict[str, Any],
-    ) -> dict[str, Any]:
-        """Filter invocation params for inclusion in run metadata."""
-        secret_keys = set(self.lc_secrets.keys())
-        return {
-            k: v
-            for k, v in invocation_params.items()
-            if v is not None and k not in secret_keys and k != "tools"
-        }
-
     def _get_ls_params(
         self,
         stop: list[str] | None = None,
@@ -974,7 +960,6 @@ def generate(
         params = self._get_invocation_params(stop=stop, **kwargs)
         options = {"stop": stop, **ls_structured_output_format_dict}
         inheritable_metadata = {
-            **self._get_metadata_invocation_params(params),
             **(metadata or {}),
             **self._get_ls_params_with_defaults(stop=stop, **kwargs),
         }
@@ -1098,7 +1083,6 @@ async def agenerate(
         params = self._get_invocation_params(stop=stop, **kwargs)
         options = {"stop": stop, **ls_structured_output_format_dict}
         inheritable_metadata = {
-            **self._get_metadata_invocation_params(params),
             **(metadata or {}),
             **self._get_ls_params_with_defaults(stop=stop, **kwargs),
         }
diff --git a/libs/core/tests/unit_tests/language_models/chat_models/test_base.py b/libs/core/tests/unit_tests/language_models/chat_models/test_base.py
index 90a12671d7ac8..e2475ef3d3a09 100644
--- a/libs/core/tests/unit_tests/language_models/chat_models/test_base.py
+++ b/libs/core/tests/unit_tests/language_models/chat_models/test_base.py
@@ -1390,150 +1390,3 @@ def test_generate_response_from_error_handles_streaming_response_failure() -> None
     assert metadata["body"] is None
     assert metadata["headers"] == {"content-type": "application/json"}
     assert metadata["status_code"] == 400
-
-
-class FakeChatModelWithSecrets(BaseChatModel):
-    """Fake chat model with lc_secrets for testing metadata filtering."""
-
-    api_key: str = "secret-key"
-    model: str = "test-model"
-    thinking: dict[str, Any] | None = None
-
-    @property
-    def lc_secrets(self) -> dict[str, str]:
-        return {"api_key": "API_KEY"}
-
-    @property
-    def _identifying_params(self) -> dict[str, Any]:
-        return {
-            "model": self.model,
-            "thinking": self.thinking,
-        }
-
-    @property
-    def _llm_type(self) -> str:
-        return "fake-chat-model-with-secrets"
-
-    def _generate(
-        self,
-        messages: list[BaseMessage],  # noqa: ARG002
-        stop: list[str] | None = None,  # noqa: ARG002
-        run_manager: CallbackManagerForLLMRun | None = None,  # noqa: ARG002
-        **kwargs: Any,  # noqa: ARG002
-    ) -> ChatResult:
-        return ChatResult(
-            generations=[ChatGeneration(message=AIMessage(content="test response"))]
-        )
-
-
-def test_init_params_in_metadata() -> None:
-    """Test that init params are included in run metadata."""
-    llm = FakeChatModelWithSecrets(thinking={"type": "enabled", "budget_tokens": 10000})
-    with collect_runs() as cb:
-        llm.invoke("hi")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "model" in metadata
-    assert metadata["model"] == "test-model"
-    assert "thinking" in metadata
-    assert metadata["thinking"] == {"type": "enabled", "budget_tokens": 10000}
-
-
-def test_init_params_filter_none_values() -> None:
-    """Test that None values are filtered from init params in metadata."""
-    llm = FakeChatModelWithSecrets(thinking=None)
-    with collect_runs() as cb:
-        llm.invoke("hi")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "thinking" not in metadata
-
-
-def test_init_params_filter_secrets() -> None:
-    """Test that lc_secrets keys are filtered from init params in metadata."""
-    llm = FakeChatModelWithSecrets()
-    with collect_runs() as cb:
-        llm.invoke("hi")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "api_key" not in metadata
-
-
-def test_runtime_params_in_metadata() -> None:
-    """Test that runtime invocation params (kwargs) are included in metadata."""
-    llm = FakeChatModelWithSecrets()
-    with collect_runs() as cb:
-        llm.invoke("hi", effort="low")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "effort" in metadata
-    assert metadata["effort"] == "low"
-
-
-def test_runtime_secrets_filtered_from_metadata() -> None:
-    """Test that runtime secret params (kwargs) are filtered from metadata."""
-    llm = FakeChatModelWithSecrets()
-    with collect_runs() as cb:
-        llm.invoke("hi", api_key="runtime-secret")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "api_key" not in metadata
-
-
-def test_user_metadata_takes_precedence() -> None:
-    """Test that user-provided metadata takes precedence over invocation params."""
-    llm = FakeChatModelWithSecrets(model="init-model")
-    with collect_runs() as cb:
-        llm.invoke("hi", config={"metadata": {"model": "user-override"}})
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert metadata["model"] == "user-override"
-
-
-async def test_invocation_params_in_metadata_ainvoke() -> None:
-    """Test that invocation params are included in run metadata for ainvoke."""
-    llm = FakeChatModelWithSecrets(thinking={"type": "enabled"})
-    with collect_runs() as cb:
-        await llm.ainvoke("hi")
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "thinking" in metadata
-
-
-def test_invocation_params_in_metadata_stream() -> None:
-    """Test that invocation params are included in run metadata for stream."""
-    llm = FakeChatModelWithSecrets(thinking={"type": "enabled"})
-    with collect_runs() as cb:
-        list(llm.stream("hi"))
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "thinking" in metadata
-
-
-async def test_invocation_params_in_metadata_astream() -> None:
-    """Test that invocation params are included in run metadata for astream."""
-    llm = FakeChatModelWithSecrets(thinking={"type": "enabled"})
-    with collect_runs() as cb:
-        async for _ in llm.astream("hi"):
-            pass
-    assert len(cb.traced_runs) == 1
-    run = cb.traced_runs[0]
-    assert run.extra is not None
-    metadata = run.extra.get("metadata", {})
-    assert "thinking" in metadata
PATCH

echo "Patch applied successfully"
