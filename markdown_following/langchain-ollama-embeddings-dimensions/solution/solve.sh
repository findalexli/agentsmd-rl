#!/bin/bash
set -e

cd /workspace/langchain

# Idempotency check - verify we haven't already applied the patch
if grep -q "dimensions: int | None = None" libs/partners/ollama/langchain_ollama/embeddings.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/libs/partners/ollama/langchain_ollama/embeddings.py b/libs/partners/ollama/langchain_ollama/embeddings.py
index b8fa44ed41e1b..a28f081b57c3a 100644
--- a/libs/partners/ollama/langchain_ollama/embeddings.py
+++ b/libs/partners/ollama/langchain_ollama/embeddings.py
@@ -6,7 +6,13 @@

 from langchain_core.embeddings import Embeddings
 from ollama import AsyncClient, Client
-from pydantic import BaseModel, ConfigDict, PrivateAttr, model_validator
+from pydantic import (
+    BaseModel,
+    ConfigDict,
+    PrivateAttr,
+    field_validator,
+    model_validator,
+)
 from typing_extensions import Self

 from langchain_ollama._utils import (
@@ -124,6 +130,20 @@ class OllamaEmbeddings(BaseModel, Embeddings):
     model: str
     """Model name to use."""

+    dimensions: int | None = None
+    """Number of dimensions for the output embedding vectors.
+
+    If not provided, the model's default embedding dimensionality is used.
+    """
+
+    @field_validator("dimensions")
+    @classmethod
+    def _validate_dimensions(cls, v: int | None) -> int | None:
+        if v is not None and v < 1:
+            msg = "`dimensions` must be a positive integer."
+            raise ValueError(msg)
+        return v
+
     validate_model_on_init: bool = False
     """Whether to validate the model exists in ollama locally on initialization.

@@ -303,7 +323,11 @@ def embed_documents(self, texts: list[str]) -> list[list[float]]:
             )
             raise RuntimeError(msg)
         return self._client.embed(
-            self.model, texts, options=self._default_params, keep_alive=self.keep_alive
+            self.model,
+            texts,
+            dimensions=self.dimensions,
+            options=self._default_params,
+            keep_alive=self.keep_alive,
         )["embeddings"]

     def embed_query(self, text: str) -> list[float]:
@@ -322,6 +346,7 @@ async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
             await self._async_client.embed(
                 self.model,
                 texts,
+                dimensions=self.dimensions,
                 options=self._default_params,
                 keep_alive=self.keep_alive,
             )
diff --git a/libs/partners/ollama/tests/unit_tests/test_embeddings.py b/libs/partners/ollama/tests/unit_tests/test_embeddings.py
index c6b45700110b3..674f1a8bb8921 100644
--- a/libs/partners/ollama/tests/unit_tests/test_embeddings.py
+++ b/libs/partners/ollama/tests/unit_tests/test_embeddings.py
@@ -1,7 +1,7 @@
 """Test embedding model integration."""

 from typing import Any
-from unittest.mock import MagicMock, Mock, patch
+from unittest.mock import AsyncMock, MagicMock, Mock, patch

 import pytest

@@ -54,6 +54,60 @@ def test_embed_documents_passes_options(mock_client_class: Any) -> None:
     assert options["temperature"] == 0.5


+@patch("langchain_ollama.embeddings.Client")
+def test_embed_documents_passes_dimensions(mock_client_class: Any) -> None:
+    """Test that embed_documents passes dimensions to the embed call."""
+    mock_client = Mock()
+    mock_client_class.return_value = mock_client
+    mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
+
+    embeddings = OllamaEmbeddings(model=MODEL_NAME, dimensions=512)
+    embeddings.embed_documents(["test text"])
+
+    call_args = mock_client.embed.call_args
+    assert call_args.kwargs["dimensions"] == 512
+
+
+@patch("langchain_ollama.embeddings.Client")
+def test_embed_documents_dimensions_none_by_default(mock_client_class: Any) -> None:
+    """Test that dimensions defaults to None when not specified."""
+    mock_client = Mock()
+    mock_client_class.return_value = mock_client
+    mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
+
+    embeddings = OllamaEmbeddings(model=MODEL_NAME)
+    embeddings.embed_documents(["test text"])
+
+    call_args = mock_client.embed.call_args
+    assert call_args.kwargs["dimensions"] is None
+
+
+@patch("langchain_ollama.embeddings.AsyncClient")
+@patch("langchain_ollama.embeddings.Client")
+async def test_aembed_documents_passes_dimensions(
+    mock_client_class: Any, mock_async_client_class: Any
+) -> None:
+    """Test that aembed_documents passes dimensions to the async embed call."""
+    mock_async_client = AsyncMock()
+    mock_async_client_class.return_value = mock_async_client
+    mock_async_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
+
+    embeddings = OllamaEmbeddings(model=MODEL_NAME, dimensions=512)
+    await embeddings.aembed_documents(["test text"])
+
+    call_args = mock_async_client.embed.call_args
+    assert call_args.kwargs["dimensions"] == 512
+
+
+def test_dimensions_validation() -> None:
+    """Test that dimensions must be a positive integer."""
+    with pytest.raises(ValueError, match="must be a positive integer"):
+        OllamaEmbeddings(model=MODEL_NAME, dimensions=0)
+
+    with pytest.raises(ValueError, match="must be a positive integer"):
+        OllamaEmbeddings(model=MODEL_NAME, dimensions=-1)
+
+
 def test_embed_documents_raises_when_client_none() -> None:
     """Test that embed_documents raises RuntimeError when client is None."""
     with patch("langchain_ollama.embeddings.Client") as mock_client_class:
PATCH

echo "Patch applied successfully"
