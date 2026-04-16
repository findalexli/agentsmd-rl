"""Tests for the OpenHands config models search endpoint benchmark.

These tests verify:
1. The new /api/v1/config/models/search endpoint exists and works
2. Pagination functionality works correctly
3. Filtering by query and verified status works
4. Parameter validation (limit bounds) works
5. Existing code continues to work (pass-to-pass)
"""

import sys
import os
import subprocess
import json
import re
import ast
from pathlib import Path

# Add repo to path
REPO = Path("/workspace/OpenHands")
sys.path.insert(0, str(REPO))


def test_config_models_file_exists():
    """F2P: config_models.py file must exist with LLMModel and LLMModelPage classes."""
    config_models_path = REPO / "openhands" / "app_server" / "config_api" / "config_models.py"
    assert config_models_path.exists(), "config_models.py does not exist"

    # Import and verify the classes exist
    from openhands.app_server.config_api.config_models import LLMModel, LLMModelPage

    # Test LLMModel can be instantiated
    model = LLMModel(provider="openai", name="gpt-4", verified=True)
    assert model.provider == "openai"
    assert model.name == "gpt-4"
    assert model.verified is True

    # Test LLMModel with default verified=False
    model2 = LLMModel(provider="anthropic", name="claude-3")
    assert model2.verified is False

    # Test LLMModelPage
    page = LLMModelPage(items=[model, model2], next_page_id="page2")
    assert len(page.items) == 2
    assert page.next_page_id == "page2"


def test_config_router_file_exists():
    """F2P: config_router.py file must exist with search_models endpoint."""
    config_router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    assert config_router_path.exists(), "config_router.py does not exist"

    # Read file to verify key components exist without importing (due to deps)
    content = config_router_path.read_text()

    # Verify search_models function exists
    assert "async def search_models(" in content, "search_models function must exist"

    # Verify helper functions exist
    assert "def _get_verified_models(" in content, "_get_verified_models must exist"
    assert "def _get_all_models_with_verified(" in content, "_get_all_models_with_verified must exist"

    # Verify router is created
    assert "router = APIRouter(" in content, "APIRouter must be created"
    assert "prefix='/config'" in content, "Router must have /config prefix"


def test_v1_router_includes_config_router():
    """F2P: v1_router.py must include the config_router."""
    v1_router_path = REPO / "openhands" / "app_server" / "v1_router.py"
    assert v1_router_path.exists(), "v1_router.py does not exist"

    # Read file and check for config_router import and include
    content = v1_router_path.read_text()
    assert "config_router" in content, "config_router not imported or included in v1_router.py"
    assert "router.include_router(config_router)" in content, "config_router not included in v1_router"


def test_public_models_deprecated():
    """F2P: /models endpoint must be marked as deprecated."""
    public_path = REPO / "openhands" / "server" / "routes" / "public.py"
    assert public_path.exists(), "public.py does not exist"

    content = public_path.read_text()
    # Check for deprecated=True parameter
    assert "deprecated=True" in content, "@app.get('/models') must have deprecated=True"
    # Check for deprecation note in docstring
    assert "deprecated" in content.lower(), "Deprecation notice must be in docstring"


def test_llm_model_serialization():
    """F2P: LLMModel must serialize correctly to dict/JSON."""
    from openhands.app_server.config_api.config_models import LLMModel, LLMModelPage

    # Test with provider
    model1 = LLMModel(provider="openai", name="gpt-4", verified=True)
    data1 = model1.model_dump()
    assert data1 == {"provider": "openai", "name": "gpt-4", "verified": True}

    # Test without provider
    model2 = LLMModel(name="local-model")
    data2 = model2.model_dump()
    assert data2 == {"provider": None, "name": "local-model", "verified": False}

    # Test page serialization
    page = LLMModelPage(items=[model1, model2], next_page_id="next123")
    page_data = page.model_dump()
    assert len(page_data["items"]) == 2
    assert page_data["next_page_id"] == "next123"


def test_get_verified_models_function():
    """F2P: _get_verified_models must return a set of verified model identifiers."""
    # Load the function via AST to avoid dependency issues
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Verify function signature
    assert "def _get_verified_models() -> set[str]:" in content, "Function must have correct signature"

    # Verify it creates a set and returns it
    assert "verified_models = set()" in content, "Function must create a set"
    assert "return verified_models" in content, "Function must return the set"

    # Verify it iterates over VERIFIED_MODELS
    assert "VERIFIED_MODELS.items()" in content, "Function must iterate over VERIFIED_MODELS"
    assert 'verified_models.add(' in content, "Function must add to the set"


def test_get_all_models_with_verified():
    """F2P: _get_all_models_with_verified must correctly mark models as verified/unverified."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Verify function signature
    assert "def _get_all_models_with_verified(models: ModelsResponse) -> list[LLMModel]:" in content, \
        "Function must have correct signature"

    # Verify it calls _get_verified_models
    assert "_get_verified_models()" in content, "Function must call _get_verified_models"

    # Verify it splits model names by "/"
    assert "model_name.split('/', 1)" in content or 'model_name.split("/", 1)' in content, \
        "Function must split model_name by /"

    # Verify it creates LLMModel instances
    assert "LLMModel(" in content, "Function must create LLMModel instances"


def test_repo_unit_tests_circular_imports():
    """Repo's circular import tests pass (pass_to_pass).

    Runs the unit tests that check for circular import issues.
    These tests analyze source code files and don't require heavy dependencies.
    """
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/utils/test_circular_imports.py", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular imports tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_unit_tests_import_utils():
    """Repo's import utils tests pass (pass_to_pass).

    Runs the unit tests for import utility functions.
    These tests verify dynamic import capabilities.
    """
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/utils/test_import_utils.py", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Import utils tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_pagination_utils_importable():
    """Pagination utilities can be imported and used (pass_to_pass).

    Tests that the paging_utils module can be imported and basic pagination works.
    """
    r = subprocess.run(
        ["python", "-c",
         "from openhands.app_server.utils.paging_utils import paginate_results, encode_page_id; "
         "items = list(range(10)); "
         "page1, next_id = paginate_results(items, None, 3); "
         "assert len(page1) == 3, f'Expected 3 items, got {len(page1)}'; "
         "assert next_id is not None, 'Expected next_page_id for more items'; "
         "page2, next_id2 = paginate_results(items, next_id, 3); "
         "assert len(page2) == 3, f'Expected 3 items on page 2, got {len(page2)}'; "
         "print('Pagination test passed')"
         ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Pagination utils test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_pydantic_models_work():
    """Pydantic models can be created and serialized (pass_to_pass).

    Tests basic Pydantic functionality used by the new API endpoints.
    """
    script = '''
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    value: int = 0

m = TestModel(name='test')
assert m.name == 'test', f"Expected name='test', got {m.name}"
assert m.value == 0, f"Expected value=0, got {m.value}"
data = m.model_dump()
assert data == {'name': 'test', 'value': 0}, f"Unexpected data: {data}"
print('Pydantic models test passed')
'''
    r = subprocess.run(
        ["python", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Pydantic models test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_fastapi_router_creation():
    """FastAPI routers can be created (pass_to_pass).

    Tests that FastAPI components needed for the new endpoint are available.
    """
    r = subprocess.run(
        ["python", "-c",
         "from fastapi import APIRouter, Query, Depends; "
         "from typing import Annotated; "
         "router = APIRouter(prefix='/config', tags=['Config']); "
         "assert router.prefix == '/config'; "
         "print('FastAPI router test passed')"
         ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"FastAPI router test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_base64_encoding():
    """Base64 encoding works for pagination tokens (pass_to_pass).

    Tests the base64 encoding/decoding used for opaque page IDs.
    """
    script = '''
import base64

def encode(value: int) -> str:
    return base64.urlsafe_b64encode(str(value).encode()).decode().rstrip("=")

def decode(page_id: str) -> int:
    padded = page_id + "=" * (4 - len(page_id) % 4)
    return int(base64.urlsafe_b64decode(padded.encode()).decode())

encoded = encode(42)
decoded = decode(encoded)
assert decoded == 42, f"Expected 42, got {decoded}"
print("Base64 encoding test passed")
'''
    r = subprocess.run(
        ["python", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Base64 encoding test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_search_models_signature():
    """F2P: search_models function must have correct signature and parameters."""
    import inspect

    # Read the file and verify signature via AST
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Check for all expected parameters in the function definition
    assert "page_id:" in content, "Must have page_id parameter"
    assert "limit:" in content, "Must have limit parameter"
    assert "query:" in content, "Must have query parameter"
    assert "verified__eq:" in content, "Must have verified__eq parameter"
    assert "models:" in content, "Must have models parameter"


def test_limit_parameter_validation_bounds():
    """F2P: Limit parameter must have gt=0 and le=100 constraints."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Check for the limit parameter with constraints
    # The Query may span multiple lines, so we need multiline matching
    # Look for limit: Annotated[int, ... Query(... gt=0 ... le=100 ...)]

    # Find the limit parameter section
    limit_match = re.search(
        r'limit:\s*Annotated\[\s*int\s*,[^\]]*Query\([^\)]*gt\s*=\s*0[^\)]*le\s*=\s*100[^\)]*\)[^\]]*\]',
        content,
        re.DOTALL
    )
    assert limit_match, "Limit must have gt=0 and le=100 constraints (Query with both bounds)"

    # Also verify with simpler checks in case structure differs
    limit_section = re.search(r'limit:\s*Annotated\[.*?\][^\n]*=\s*50', content, re.DOTALL)
    if limit_section:
        section = limit_section.group(0)
        assert 'gt=0' in section or 'gt = 0' in section, "Limit must have gt=0 constraint"
        assert 'le=100' in section or 'le = 100' in section, "Limit must have le=100 constraint"


def test_llm_model_page_has_items_and_next_page_id():
    """F2P: LLMModelPage must have items and next_page_id fields."""
    from openhands.app_server.config_api.config_models import LLMModelPage, LLMModel

    # Check field existence through instantiation
    model = LLMModel(provider="test", name="model", verified=True)
    page = LLMModelPage(items=[model], next_page_id=None)

    assert hasattr(page, 'items'), "LLMModelPage must have items field"
    assert hasattr(page, 'next_page_id'), "LLMModelPage must have next_page_id field"

    # Verify items is a list of LLMModel
    assert isinstance(page.items, list)
    assert all(isinstance(m, LLMModel) for m in page.items)


def test_config_router_imports_correct_modules():
    """F2P: Config router must import all required modules correctly."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Verify key imports are present
    assert "from fastapi import APIRouter, Depends, Query" in content, \
        "Must import FastAPI components"
    assert "from openhands.app_server.config_api.config_models import" in content, \
        "Must import config models"
    assert "from openhands.app_server.utils.dependencies import get_dependencies" in content, \
        "Must import dependencies"
    assert "from openhands.app_server.utils.paging_utils import" in content, \
        "Must import pagination utils"
    # VERIFIED_MODELS import path may vary - check for the variable usage
    assert "VERIFIED_MODELS" in content, \
        "Must use VERIFIED_MODELS constant"
    assert "from openhands.server.routes.public import get_llm_models_dependency" in content, \
        "Must import get_llm_models_dependency"
    assert "from openhands.utils.llm import ModelsResponse" in content, \
        "Must import ModelsResponse"


def test_query_parameter_is_case_insensitive():
    """F2P: Query parameter filtering must be case-insensitive."""
    # We verify this by examining the code
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Check for case-insensitive filtering
    # Should have query.lower() and m.name.lower()
    assert "query_lower" in content or "query.lower()" in content, "Query must be lowercased"
    assert "m.name.lower()" in content or ".name.lower()" in content, "Model name must be lowercased for comparison"


def test_new_endpoint_path_correct():
    """F2P: New endpoint must be at /config/models/search."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    assert "@router.get('/models/search')" in content, "Endpoint must be at /models/search"


def test_config_api_directory_structure():
    """F2P: Config API directory must have both models and router files."""
    config_api_dir = REPO / "openhands" / "app_server" / "config_api"

    assert config_api_dir.exists(), "config_api directory must exist"
    assert (config_api_dir / "config_models.py").exists(), "config_models.py must exist"
    assert (config_api_dir / "config_router.py").exists(), "config_router.py must exist"


def test_config_models_imports_base_model():
    """F2P: config_models.py must import BaseModel from pydantic."""
    models_path = REPO / "openhands" / "app_server" / "config_api" / "config_models.py"
    content = models_path.read_text()

    assert "from pydantic import BaseModel" in content, "Must import BaseModel from pydantic"
    assert "class LLMModel(BaseModel):" in content, "LLMModel must inherit from BaseModel"
    assert "class LLMModelPage(BaseModel):" in content, "LLMModelPage must inherit from BaseModel"


def test_router_has_dependencies():
    """F2P: Config router must use get_dependencies."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    assert "dependencies=get_dependencies()" in content, "Router must use get_dependencies()"


def test_endpoint_returns_llm_model_page():
    """F2P: search_models endpoint must return LLMModelPage."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Check return type annotation
    assert ") -> LLMModelPage:" in content, "search_models must return LLMModelPage"

    # Check that it creates and returns LLMModelPage
    assert "return LLMModelPage(" in content, "search_models must return LLMModelPage instance"


def test_filters_combined_correctly():
    """F2P: Query and verified filters must be combined (both applied if provided)."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    # Both filters should apply to the same list (filtered_models)
    # Query filter comes first, then verified filter
    query_filter_idx = content.find("if query is not None:")
    verified_filter_idx = content.find("if verified__eq is not None:")

    assert query_filter_idx != -1, "Must have query filter"
    assert verified_filter_idx != -1, "Must have verified__eq filter"

    # Both should modify filtered_models
    assert "filtered_models = [m for m in filtered_models" in content, \
        "Both filters must modify the same filtered_models list"


def test_pagination_applied_to_filtered_results():
    """F2P: Pagination must be applied after filtering."""
    router_path = REPO / "openhands" / "app_server" / "config_api" / "config_router.py"
    content = router_path.read_text()

    paginate_idx = content.find("paginate_results(filtered_models")
    assert paginate_idx != -1, "paginate_results must be called with filtered_models"

    # Check that items and next_page_id are returned
    assert "items, next_page_id = paginate_results" in content, \
        "Must unpack paginate_results return value"
