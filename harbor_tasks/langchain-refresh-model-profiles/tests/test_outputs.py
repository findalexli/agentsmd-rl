"""Tests for model profile data updates in langchain PR #36368."""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/langchain")


def test_mistralai_model_small_2603_exists():
    """Fail-to-pass: mistral-small-2603 model should exist in profiles."""
    profiles_path = REPO / "libs/partners/mistralai/langchain_mistralai/data/_profiles.py"
    content = profiles_path.read_text()

    # Check that the new model exists
    assert '"mistral-small-2603":' in content, "mistral-small-2603 model not found in profiles"

    # Parse to verify structure
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and key.value == "mistral-small-2603":
                    return
    raise AssertionError("mistral-small-2603 not found as a dict key in _PROFILES")


def test_mistralai_model_small_2603_specs():
    """Fail-to-pass: mistral-small-2603 should have correct specs."""
    profiles_path = REPO / "libs/partners/mistralai/langchain_mistralai/data/_profiles.py"
    content = profiles_path.read_text()

    # Extract the dict using ast
    tree = ast.parse(content)

    # Find the _PROFILES dict
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id') and node.target.id == "_PROFILES":
            if isinstance(node.value, ast.Dict):
                for i, key in enumerate(node.value.keys):
                    if isinstance(key, ast.Constant) and key.value == "mistral-small-2603":
                        model_data = node.value.values[i]
                        if isinstance(model_data, ast.Dict):
                            # Extract key-value pairs
                            specs = {}
                            for k, v in zip(model_data.keys, model_data.values):
                                if isinstance(k, ast.Constant):
                                    if isinstance(v, ast.Constant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.NameConstant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.Name):
                                        specs[k.value] = v.id == "True"

                            # Verify key specs
                            assert specs.get("name") == "Mistral Small 4", f"Wrong name: {specs.get('name')}"
                            assert specs.get("max_input_tokens") == 256000, f"Wrong max_input_tokens: {specs.get('max_input_tokens')}"
                            assert specs.get("max_output_tokens") == 256000, f"Wrong max_output_tokens: {specs.get('max_output_tokens')}"
                            assert specs.get("reasoning_output") == True, f"Wrong reasoning_output: {specs.get('reasoning_output')}"
                            assert specs.get("tool_calling") == True, f"Wrong tool_calling: {specs.get('tool_calling')}"
                            return

    raise AssertionError("Could not verify mistral-small-2603 specs")


def test_mistralai_small_latest_updated():
    """Fail-to-pass: mistral-small-latest should have updated specs (256k tokens, reasoning=True)."""
    profiles_path = REPO / "libs/partners/mistralai/langchain_mistralai/data/_profiles.py"
    content = profiles_path.read_text()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id') and node.target.id == "_PROFILES":
            if isinstance(node.value, ast.Dict):
                for i, key in enumerate(node.value.keys):
                    if isinstance(key, ast.Constant) and key.value == "mistral-small-latest":
                        model_data = node.value.values[i]
                        if isinstance(model_data, ast.Dict):
                            specs = {}
                            for k, v in zip(model_data.keys, model_data.values):
                                if isinstance(k, ast.Constant):
                                    if isinstance(v, ast.Constant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.NameConstant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.Name):
                                        specs[k.value] = v.id == "True"

                            # Verify updated specs (the old values were 128000/16384/reasoning=False)
                            assert specs.get("max_input_tokens") == 256000, \
                                f"mistral-small-latest max_input_tokens should be 256000, got {specs.get('max_input_tokens')}"
                            assert specs.get("max_output_tokens") == 256000, \
                                f"mistral-small-latest max_output_tokens should be 256000, got {specs.get('max_output_tokens')}"
                            assert specs.get("reasoning_output") == True, \
                                f"mistral-small-latest reasoning_output should be True, got {specs.get('reasoning_output')}"
                            assert specs.get("attachment") == True, \
                                f"mistral-small-latest attachment should be True, got {specs.get('attachment')}"
                            return

    raise AssertionError("Could not verify mistral-small-latest updated specs")


def test_openai_gpt_5_3_chat_latest_exists():
    """Fail-to-pass: gpt-5.3-chat-latest model should exist in profiles."""
    profiles_path = REPO / "libs/partners/openai/langchain_openai/data/_profiles.py"
    content = profiles_path.read_text()

    assert '"gpt-5.3-chat-latest":' in content, "gpt-5.3-chat-latest model not found in profiles"

    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id') and node.target.id == "_PROFILES":
            if isinstance(node.value, ast.Dict):
                for i, key in enumerate(node.value.keys):
                    if isinstance(key, ast.Constant) and key.value == "gpt-5.3-chat-latest":
                        return

    raise AssertionError("gpt-5.3-chat-latest not found as a dict key in _PROFILES")


def test_openai_gpt_5_3_chat_latest_specs():
    """Fail-to-pass: gpt-5.3-chat-latest should have correct specs."""
    profiles_path = REPO / "libs/partners/openai/langchain_openai/data/_profiles.py"
    content = profiles_path.read_text()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id') and node.target.id == "_PROFILES":
            if isinstance(node.value, ast.Dict):
                for i, key in enumerate(node.value.keys):
                    if isinstance(key, ast.Constant) and key.value == "gpt-5.3-chat-latest":
                        model_data = node.value.values[i]
                        if isinstance(model_data, ast.Dict):
                            specs = {}
                            for k, v in zip(model_data.keys, model_data.values):
                                if isinstance(k, ast.Constant):
                                    if isinstance(v, ast.Constant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.NameConstant):
                                        specs[k.value] = v.value
                                    elif isinstance(v, ast.Name):
                                        specs[k.value] = v.id == "True"

                            # Verify key specs
                            assert specs.get("name") == "GPT-5.3 Chat (latest)", f"Wrong name: {specs.get('name')}"
                            assert specs.get("max_input_tokens") == 128000, f"Wrong max_input_tokens: {specs.get('max_input_tokens')}"
                            assert specs.get("max_output_tokens") == 16384, f"Wrong max_output_tokens: {specs.get('max_output_tokens')}"
                            assert specs.get("tool_calling") == True, f"Wrong tool_calling: {specs.get('tool_calling')}"
                            assert specs.get("structured_output") == True, f"Wrong structured_output: {specs.get('structured_output')}"
                            return

    raise AssertionError("Could not verify gpt-5.3-chat-latest specs")


def test_openrouter_nemotron_model_id_fixed():
    """Fail-to-pass: OpenRouter nemotron model ID should use colon separator."""
    profiles_path = REPO / "libs/partners/openrouter/langchain_openrouter/data/_profiles.py"
    content = profiles_path.read_text()

    # The fix changes from "nvidia/nemotron-3-super-120b-a12b-free" to "nvidia/nemotron-3-super-120b-a12b:free"
    assert '"nvidia/nemotron-3-super-120b-a12b:free":' in content, \
        "Fixed model ID 'nvidia/nemotron-3-super-120b-a12b:free' not found"

    # Ensure the old buggy ID doesn't exist
    assert '"nvidia/nemotron-3-super-120b-a12b-free":' not in content, \
        "Old buggy model ID 'nvidia/nemotron-3-super-120b-a12b-free' still exists"


def test_mistralai_profiles_syntax():
    """Pass-to-pass: MistralAI profiles file should be valid Python."""
    profiles_path = REPO / "libs/partners/mistralai/langchain_mistralai/data/_profiles.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(profiles_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"MistralAI profiles has syntax errors: {result.stderr}"


def test_openai_profiles_syntax():
    """Pass-to-pass: OpenAI profiles file should be valid Python."""
    profiles_path = REPO / "libs/partners/openai/langchain_openai/data/_profiles.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(profiles_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"OpenAI profiles has syntax errors: {result.stderr}"


def test_openrouter_profiles_syntax():
    """Pass-to-pass: OpenRouter profiles file should be valid Python."""
    profiles_path = REPO / "libs/partners/openrouter/langchain_openrouter/data/_profiles.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(profiles_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"OpenRouter profiles has syntax errors: {result.stderr}"


def test_mistralai_profiles_importable():
    """Pass-to-pass: MistralAI profiles _PROFILES dict should be directly importable."""
    profiles_path = REPO / "libs/partners/mistralai/langchain_mistralai/data/_profiles.py"
    # Import just the _profiles module directly without the parent package
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, '{profiles_path.parent}'); "
         "from _profiles import _PROFILES; print('OK')"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"MistralAI profiles not importable: {result.stderr}"


def test_openai_profiles_importable():
    """Pass-to-pass: OpenAI profiles _PROFILES dict should be directly importable."""
    profiles_path = REPO / "libs/partners/openai/langchain_openai/data/_profiles.py"
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, '{profiles_path.parent}'); "
         "from _profiles import _PROFILES; print('OK')"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"OpenAI profiles not importable: {result.stderr}"


def test_openrouter_profiles_importable():
    """Pass-to-pass: OpenRouter profiles _PROFILES dict should be directly importable."""
    profiles_path = REPO / "libs/partners/openrouter/langchain_openrouter/data/_profiles.py"
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, '{profiles_path.parent}'); "
         "from _profiles import _PROFILES; print('OK')"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"OpenRouter profiles not importable: {result.stderr}"


def test_repo_mistralai_ruff():
    """Repo CI: MistralAI package passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "langchain_mistralai"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/mistralai",
    )
    assert r.returncode == 0, f"MistralAI ruff check failed:\n{r.stderr[-500:]}"


def test_repo_openai_ruff():
    """Repo CI: OpenAI package passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "langchain_openai"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openai",
    )
    assert r.returncode == 0, f"OpenAI ruff check failed:\n{r.stderr[-500:]}"


def test_repo_openrouter_ruff():
    """Repo CI: OpenRouter package passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "langchain_openrouter"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openrouter",
    )
    assert r.returncode == 0, f"OpenRouter ruff check failed:\n{r.stderr[-500:]}"


def test_repo_mistralai_mypy():
    """Repo CI: MistralAI package passes mypy type checking (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--all-groups", "mypy", "langchain_mistralai", "--cache-dir", ".mypy_cache"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/mistralai",
    )
    assert r.returncode == 0, f"MistralAI mypy check failed:\n{r.stderr[-500:]}"


def test_repo_openai_mypy():
    """Repo CI: OpenAI package passes mypy type checking (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--all-groups", "mypy", "langchain_openai", "--cache-dir", ".mypy_cache"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openai",
    )
    assert r.returncode == 0, f"OpenAI mypy check failed:\n{r.stderr[-500:]}"


def test_repo_openrouter_mypy():
    """Repo CI: OpenRouter package passes mypy type checking (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--all-groups", "mypy", "langchain_openrouter", "--cache-dir", ".mypy_cache"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openrouter",
    )
    assert r.returncode == 0, f"OpenRouter mypy check failed:\n{r.stderr[-500:]}"


def test_repo_mistralai_unit_imports():
    """Repo CI: MistralAI unit import tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "test", "pytest", "tests/unit_tests/test_imports.py", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/mistralai",
    )
    assert r.returncode == 0, f"MistralAI unit import tests failed:\n{r.stderr[-500:]}"


def test_repo_openai_unit_imports():
    """Repo CI: OpenAI unit import tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "test", "pytest", "tests/unit_tests/test_imports.py", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openai",
    )
    assert r.returncode == 0, f"OpenAI unit import tests failed:\n{r.stderr[-500:]}"


def test_repo_openrouter_unit_imports():
    """Repo CI: OpenRouter unit import tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "test", "pytest", "tests/unit_tests/test_imports.py", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO / "libs/partners/openrouter",
    )
    assert r.returncode == 0, f"OpenRouter unit import tests failed:\n{r.stderr[-500:]}"
