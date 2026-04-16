#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch to implement the new /api/v1/config/models/search endpoint
patch -p1 <<'PATCH'
diff --git a/openhands/app_server/config_api/config_models.py b/openhands/app_server/config_api/config_models.py
new file mode 100644
index 000000000000..bccd6549897c
--- /dev/null
+++ b/openhands/app_server/config_api/config_models.py
@@ -0,0 +1,32 @@
+"""Config-related models for OpenHands App Server V1 API."""
+
+from pydantic import BaseModel, Field
+
+
+class LLMModel(BaseModel):
+    """LLM Model object for API responses.
+
+    Attributes:
+        name: The model name.
+        verified: Whether the model is verified by OpenHands.
+    """
+
+    provider: str | None = Field(
+        default=None, description='The name of the provider for this model'
+    )
+    name: str = Field(description='The name of this model')
+    verified: bool = Field(
+        default=False, description='Whether the model is verified by OpenHands'
+    )
+
+
+class LLMModelPage(BaseModel):
+    """Paginated response for LLM models.
+
+    Attributes:
+        items: List of LLM models in the current page.
+        next_page_id: ID for the next page, or None if there are no more pages.
+    """
+
+    items: list[LLMModel]
+    next_page_id: str | None = None
diff --git a/openhands/app_server/config_api/config_router.py b/openhands/app_server/config_api/config_router.py
new file mode 100644
index 000000000000..29df9e870c6d
--- /dev/null
+++ b/openhands/app_server/config_api/config_router.py
@@ -0,0 +1,94 @@
+"""Config router for OpenHands App Server V1 API.
+
+This module provides V1 API endpoints for configuration, including model search
+with pagination support.
+"""
+
+from typing import Annotated
+
+from fastapi import APIRouter, Depends, Query
+
+from openhands.app_server.config_api.config_models import LLMModel, LLMModelPage
+from openhands.app_server.utils.dependencies import get_dependencies
+from openhands.app_server.utils.paging_utils import (
+    paginate_results,
+)
+from openhands.sdk.llm.utils.verified_models import VERIFIED_MODELS
+from openhands.server.routes.public import get_llm_models_dependency
+from openhands.utils.llm import ModelsResponse
+
+# We use the get_dependencies method here to signal to the OpenAPI docs that this endpoint
+# is protected. The actual protection is provided by SetAuthCookieMiddleware
+router = APIRouter(
+    prefix='/config',
+    tags=['Config'],
+    dependencies=get_dependencies(),
+)
+
+
+@router.get('/models/search')
+async def search_models(
+    page_id: Annotated[
+        str | None,
+        Query(title='Optional next_page_id from the previously returned page'),
+    ] = None,
+    limit: Annotated[
+        int,
+        Query(title='The max number of results in the page', gt=0, le=100),
+    ] = 50,
+    query: Annotated[
+        str | None,
+        Query(title='Filter models by name (case-insensitive substring match)'),
+    ] = None,
+    verified__eq: Annotated[
+        bool | None,
+        Query(title='Filter by verified status (true/false, omit for all)'),
+    ] = None,
+    models: ModelsResponse = Depends(get_llm_models_dependency),
+) -> LLMModelPage:
+    """Search for LLM models with pagination and filtering.
+
+    Returns a paginated list of models that can be filtered by name
+    (contains) and verified status.
+    """
+    filtered_models = _get_all_models_with_verified(models)
+
+    if query is not None:
+        query_lower = query.lower()
+        filtered_models = [m for m in filtered_models if query_lower in m.name.lower()]
+
+    if verified__eq is not None:
+        filtered_models = [m for m in filtered_models if m.verified == verified__eq]
+
+    # Apply pagination
+    items, next_page_id = paginate_results(filtered_models, page_id, limit)
+
+    return LLMModelPage(items=items, next_page_id=next_page_id)
+
+
+def _get_verified_models() -> set[str]:
+    verified_models = set()
+    for provider, models in VERIFIED_MODELS.items():
+        for name in models:
+            verified_models.add(f'{provider}/{name}')
+    return verified_models
+
+
+def _get_all_models_with_verified(models: ModelsResponse) -> list[LLMModel]:
+    verified_models = _get_verified_models()
+    results = []
+    for model_name in models.models:
+        verified = model_name in verified_models
+        parts = model_name.split('/', 1)
+        if len(parts) == 2:
+            provider, name = parts
+        else:
+            provider = None
+            name = parts[0]
+        result = LLMModel(
+            provider=provider,
+            name=name,
+            verified=verified,
+        )
+        results.append(result)
+    return results
diff --git a/openhands/app_server/v1_router.py b/openhands/app_server/v1_router.py
index 292b77b2e100..eae32aa933bd 100644
--- a/openhands/app_server/v1_router.py
+++ b/openhands/app_server/v1_router.py
@@ -1,6 +1,7 @@
 from fastapi import APIRouter

 from openhands.app_server.app_conversation import app_conversation_router
+from openhands.app_server.config_api.config_router import router as config_router
 from openhands.app_server.event import event_router
 from openhands.app_server.event_callback import (
     webhook_router,
@@ -33,3 +34,4 @@
 router.include_router(webhook_router.router)
 router.include_router(web_client_router.router)
 router.include_router(git_router)
+router.include_router(config_router)
diff --git a/openhands/server/routes/public.py b/openhands/server/routes/public.py
index 6c8067f87c7a..3ceb3f0bbd78 100644
--- a/openhands/server/routes/public.py
+++ b/openhands/server/routes/public.py
@@ -29,10 +29,18 @@ async def get_llm_models_dependency(request: Request) -> ModelsResponse:
     return get_supported_llm_models(config)


-@app.get('/models')
+@app.get('/models', deprecated=True)
 async def get_litellm_models(
     models: ModelsResponse = Depends(get_llm_models_dependency),
 ) -> ModelsResponse:
+    """Get all supported LLM models.
+
+    .. deprecated::
+        This endpoint is deprecated. Use `/api/v1/config/models/search` instead.
+
+    Returns:
+        ModelsResponse: Response containing models, verified_models, verified_providers, and default_model.
+    """
     return models


PATCH

# Idempotency check: verify distinctive line from patch exists
if grep -q "Filter by verified status (true/false, omit for all)" openhands/app_server/config_api/config_router.py; then
    echo "Patch applied successfully"
else
    echo "Patch may have already been applied or failed"
    exit 0
fi
