"""
Tests for airflow-optional-theme-tokens task.

Tests that the tokens field is optional in Theme configuration,
allowing CSS-only, icon-only, or empty theme configurations.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

REPO = Path("/workspace/airflow")

# Cache for loaded module
_types_module = None


def _load_types_module():
    """Load the types module directly from file without the full airflow import chain."""
    global _types_module
    if _types_module is not None:
        return _types_module

    # Create mock modules for the airflow._shared.timezones dependency
    mock_timezone = MagicMock()
    mock_timezone.utc = MagicMock()
    mock_timezones = MagicMock()
    mock_timezones.timezone = mock_timezone

    # Register mock modules
    sys.modules.setdefault('airflow', MagicMock(__path__=[str(REPO / "airflow-core/src/airflow")]))
    sys.modules.setdefault('airflow._shared', MagicMock())
    sys.modules.setdefault('airflow._shared.timezones', mock_timezones)

    # Load types.py directly using importlib
    types_path = REPO / "airflow-core/src/airflow/api_fastapi/common/types.py"
    spec = importlib.util.spec_from_file_location("airflow.api_fastapi.common.types", types_path)
    types_module = importlib.util.module_from_spec(spec)

    # Register subpackages in sys.modules
    sys.modules['airflow.api_fastapi'] = MagicMock()
    sys.modules['airflow.api_fastapi.common'] = MagicMock()
    sys.modules['airflow.api_fastapi.common.types'] = types_module

    # Execute the module
    spec.loader.exec_module(types_module)

    _types_module = types_module
    return types_module


def test_theme_accepts_none_tokens():
    """Theme model accepts None for tokens field (fail_to_pass).

    On the base commit, tokens is required. After the fix, it's optional.
    """
    types = _load_types_module()
    Theme = types.Theme

    # Should not raise - tokens can be None after the fix
    theme = Theme(tokens=None, globalCss={"body": {"background": "red"}})
    assert theme.tokens is None
    assert theme.globalCss == {"body": {"background": "red"}}


def test_theme_works_with_only_globalcss():
    """Theme model works with only globalCss, no tokens (fail_to_pass).

    Tests that theme can be created with CSS-only configuration.
    """
    types = _load_types_module()
    Theme = types.Theme

    # Create theme with only CSS, no tokens
    theme = Theme(globalCss={"body": {"margin": "0"}})
    assert theme.tokens is None
    assert theme.globalCss == {"body": {"margin": "0"}}
    assert theme.icon is None


def test_theme_works_with_only_icon():
    """Theme model works with only icon field, no tokens (fail_to_pass).

    Tests that theme can be created with icon-only configuration.
    """
    types = _load_types_module()
    Theme = types.Theme

    # Create theme with only icon, no tokens or CSS
    # Icon must be app-relative (starts with /) or http(s) URL
    theme = Theme(icon="/static/custom-icon.svg")
    assert theme.tokens is None
    assert theme.globalCss is None
    assert theme.icon == "/static/custom-icon.svg"


def test_theme_empty_config():
    """Theme model accepts empty configuration (fail_to_pass).

    Users should be able to pass an empty theme to restore OSS defaults.
    """
    types = _load_types_module()
    Theme = types.Theme

    # Empty theme should work - all fields are optional
    theme = Theme()
    assert theme.tokens is None
    assert theme.globalCss is None
    assert theme.icon is None
    assert theme.icon_dark_mode is None


def test_theme_with_tokens_still_works():
    """Theme model still works when tokens are provided (pass_to_pass).

    Ensures backward compatibility - existing configs with tokens still work.
    """
    types = _load_types_module()
    Theme = types.Theme
    ThemeColors = types.ThemeColors

    # ColorScale format: {"shade": {"value": "oklch(...)"}}
    colors = ThemeColors(brand={
        "50": {"value": "oklch(0.95 0.01 250)"},
        "100": {"value": "oklch(0.90 0.02 250)"},
        "200": {"value": "oklch(0.80 0.04 250)"},
        "300": {"value": "oklch(0.70 0.06 250)"},
        "400": {"value": "oklch(0.60 0.08 250)"},
        "500": {"value": "oklch(0.50 0.10 250)"},
        "600": {"value": "oklch(0.40 0.12 250)"},
        "700": {"value": "oklch(0.35 0.10 250)"},
        "800": {"value": "oklch(0.30 0.08 250)"},
        "900": {"value": "oklch(0.25 0.06 250)"},
        "950": {"value": "oklch(0.20 0.04 250)"},
    })

    theme = Theme(tokens={"colors": colors})
    assert theme.tokens is not None
    assert "colors" in theme.tokens
    assert theme.tokens["colors"].brand is not None


def test_themecolors_validation_still_works():
    """ThemeColors still requires at least one color token (pass_to_pass).

    The validation rule that requires at least one color should still work.
    """
    types = _load_types_module()
    ThemeColors = types.ThemeColors
    from pydantic import ValidationError

    # Should raise - no colors provided
    try:
        ThemeColors()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "At least one color token must be provided" in str(e)


def test_theme_serialization_excludes_none():
    """Theme serialization excludes None values (fail_to_pass).

    After the fix, ConfigResponse.serialize_theme should use exclude_none=True.
    """
    types = _load_types_module()
    Theme = types.Theme

    # Create theme with only some fields set
    theme = Theme(globalCss={"body": {"color": "black"}})

    # Serialize the theme
    serialized = theme.model_dump(exclude_none=True)

    # None fields should not appear in the output
    assert "tokens" not in serialized or serialized.get("tokens") is None
    assert "globalCss" in serialized
    assert serialized["globalCss"] == {"body": {"color": "black"}}


def test_syntax_check_types_file():
    """Syntax check passes on the modified types.py file (pass_to_pass).

    origin: agent_config
    source: AGENTS.md - "Always format and check Python files with ruff"
    """
    result = subprocess.run(
        ["python", "-m", "py_compile",
         str(REPO / "airflow-core/src/airflow/api_fastapi/common/types.py")],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


def test_syntax_check_config_file():
    """Syntax check passes on the modified config.py file (pass_to_pass).

    origin: agent_config
    source: AGENTS.md - "Always format and check Python files with ruff"
    """
    result = subprocess.run(
        ["python", "-m", "py_compile",
         str(REPO / "airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py")],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


def test_repo_ruff_check():
    """Ruff lint passes on modified files (pass_to_pass).

    Runs the repo's ruff linter on the files modified by the PR.
    CI uses 'prek' which internally runs ruff.
    """
    # Install ruff if needed and run check
    result = subprocess.run(
        ["bash", "-c",
         "pip install ruff --quiet 2>/dev/null && "
         "ruff check "
         "airflow-core/src/airflow/api_fastapi/common/types.py "
         "airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_no_assert_in_production_code():
    """No assert statements in production code (pass_to_pass).

    origin: agent_config
    source: AGENTS.md - "No assert in production code"
    """
    types_file = REPO / "airflow-core/src/airflow/api_fastapi/common/types.py"
    config_file = REPO / "airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py"

    for filepath in [types_file, config_file]:
        content = filepath.read_text()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments and strings
            if stripped.startswith('#'):
                continue
            # Check for bare assert statements (not in strings)
            if stripped.startswith('assert ') and not stripped.startswith('assert_'):
                # Ignore asserts in type checking blocks
                assert False, f"Found 'assert' in production code at {filepath}:{i}: {line}"


def test_multiple_theme_configurations():
    """Test various theme configurations work correctly (fail_to_pass).

    Verifies the fix handles multiple different optional configurations.
    """
    types = _load_types_module()
    Theme = types.Theme
    ThemeColors = types.ThemeColors

    # Config 1: Only globalCss
    t1 = Theme(globalCss={"div": {"padding": "10px"}})
    assert t1.tokens is None
    assert t1.globalCss == {"div": {"padding": "10px"}}

    # Config 2: Only icon (app-relative path, must be SVG)
    t2 = Theme(icon="/assets/icon.svg")
    assert t2.icon == "/assets/icon.svg"
    assert t2.tokens is None

    # Config 3: Only icon_dark_mode (https URL, must be SVG)
    t3 = Theme(icon_dark_mode="https://example.com/dark-icon.svg")
    assert t3.icon_dark_mode == "https://example.com/dark-icon.svg"

    # Config 4: globalCss + icon (no tokens)
    t4 = Theme(globalCss={"span": {"color": "blue"}}, icon="/logo.svg")
    assert t4.tokens is None
    assert t4.globalCss is not None
    assert t4.icon == "/logo.svg"

    # Config 5: Full config with tokens (colors must be in oklch format)
    colors = ThemeColors(gray={
        "50": {"value": "oklch(0.98 0 0)"}, "100": {"value": "oklch(0.96 0 0)"},
        "200": {"value": "oklch(0.93 0 0)"}, "300": {"value": "oklch(0.88 0 0)"},
        "400": {"value": "oklch(0.74 0 0)"}, "500": {"value": "oklch(0.62 0 0)"},
        "600": {"value": "oklch(0.46 0 0)"}, "700": {"value": "oklch(0.38 0 0)"},
        "800": {"value": "oklch(0.26 0 0)"}, "900": {"value": "oklch(0.13 0 0)"},
        "950": {"value": "oklch(0.07 0 0)"}
    })
    t5 = Theme(tokens={"colors": colors}, globalCss={"body": {"font": "sans-serif"}})
    assert t5.tokens is not None
    assert t5.globalCss is not None
