# Task: Add Config Models Search Endpoint

## Problem Statement

The OpenHands app server needs a new paginated, filterable search endpoint for LLM models. Currently there is no way to search or browse models with pagination. A new endpoint at `/api/v1/config/models/search` should be added that supports model discovery with cursor-based pagination, case-insensitive name filtering, and verified-status filtering. Additionally, the existing `/models` endpoint must be marked as deprecated in favor of the new endpoint.

## Files to Create or Modify

| File | Action |
|------|--------|
| `openhands/app_server/config_api/config_models.py` | Create — Pydantic data models for the response |
| `openhands/app_server/config_api/config_router.py` | Create — FastAPI router with the search endpoint |
| `openhands/app_server/v1_router.py` | Modify — register the new config router |
| `openhands/server/routes/public.py` | Modify — deprecate the `/models` endpoint |

## Response Models (`config_models.py`)

Import `BaseModel` from `pydantic` and define two classes inheriting from `BaseModel`:

**`LLMModel`** — represents a single LLM model with fields:
- `provider`: `str | None` — default `None`
- `name`: `str` — required
- `verified`: `bool` — default `False`

When serialized via `model_dump()`, must produce `{"provider": ..., "name": ..., "verified": ...}`. A model created with only `name="local-model"` should serialize to `{"provider": None, "name": "local-model", "verified": False}`.

**`LLMModelPage`** — represents a page of results with fields:
- `items`: `list[LLMModel]` — the models in this page
- `next_page_id`: `str | None` — default `None`, cursor for the next page

## Router Module (`config_router.py`)

### Required Imports

The module must import the following:
- `APIRouter`, `Depends`, `Query` from `fastapi`
- `LLMModel`, `LLMModelPage` from `openhands.app_server.config_api.config_models`
- `get_dependencies` from `openhands.app_server.utils.dependencies`
- `paginate_results` from `openhands.app_server.utils.paging_utils`
- `get_llm_models_dependency` from `openhands.server.routes.public`
- `ModelsResponse` from `openhands.utils.llm`
- `VERIFIED_MODELS` from `openhands.sdk.llm.utils.verified_models`
- `Annotated` from `typing`

### Router Configuration

Create an `APIRouter` with `prefix='/config'`, `tags=['Config']`, and `dependencies=get_dependencies()`.

### Search Endpoint

Define an `async def search_models` function decorated with `@router.get('/models/search')` that returns `LLMModelPage`. All parameters must use `Annotated` type hints. The function must:

1. Accept these query parameters:
   - `page_id` (`str | None`, default `None`) — pagination cursor
   - `limit` (`int`, default `50`) — page size, constrained with `gt=0` and `le=100` via `Query`
   - `query` (`str | None`, default `None`) — case-insensitive substring filter on model name
   - `verified__eq` (`bool | None`, default `None`) — filter by verified status
   - `models` (`ModelsResponse`) — injected via `Depends(get_llm_models_dependency)`

2. Build a list of all models with their verified status, then apply optional filters:
   - If `query` is not `None`: filter by case-insensitive substring match on the model's name
   - If `verified__eq` is not `None`: filter to models whose verified status matches

3. Apply cursor-based pagination using `paginate_results` from the paging utilities

4. Return an `LLMModelPage` with the paginated items and next page cursor

### Helper Functions

The module must define these helpers:

**`_get_verified_models() -> set[str]`**: Returns a set of verified model identifier strings in `"provider/model"` format. Should iterate over `VERIFIED_MODELS` dictionary entries to build this set.

**`_get_all_models_with_verified(models: ModelsResponse) -> list[LLMModel]`**: Takes the models response and returns a list of `LLMModel` instances. Each model identifier in the response should be split on `"/"` (maxsplit=1) to extract provider and name. Verified status is determined by checking if the full identifier is in the verified set.

## Integration

**`v1_router.py`**: Import the config router from `openhands.app_server.config_api.config_router` and include it via `router.include_router(config_router)`.

**`public.py`**: The existing `@app.get('/models')` decorator must include `deprecated=True`. The endpoint's docstring must mention that it is deprecated (containing the word "deprecated").
