"""
Task: gradio-filepath-api-display
Repo: gradio-app/gradio @ 1bd5fa898de569bd14ac069d338eb4bd82b72716
PR:   13045

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"

# Ensure the client source is importable
sys.path.insert(0, f"{REPO}/client/python")


# ---------------------------------------------------------------------------
# Helpers: hand-crafted JSON schemas that mimic Gradio's FileData / ImageData
# ---------------------------------------------------------------------------

# FileData-like schema: path + meta with $ref to a definition containing const
FILE_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "url": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "orig_name": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "mime_type": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "is_stream": {"type": "boolean", "default": False},
        "meta": {"$ref": "#/$defs/Meta", "default": {"_type": "gradio.FileData"}},
    },
    "$defs": {
        "Meta": {
            "type": "object",
            "properties": {"_type": {"const": "gradio.FileData", "title": " Type"}},
            "required": ["_type"],
            "title": "Meta",
        }
    },
    "title": "FileData",
}

# ImageData-like schema: meta resolved via default dict (no properties._type.const)
IMAGE_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "url": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "meta": {"type": "object", "default": {"_type": "gradio.FileData"}},
    },
    "title": "ImageData",
}

# Nested: an object containing a file-type field
GALLERY_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "image": {"$ref": "#/$defs/FileData"},
        "caption": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
    },
    "$defs": {
        "FileData": {
            "type": "object",
            "properties": {
                "path": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "meta": {
                    "$ref": "#/$defs/Meta",
                    "default": {"_type": "gradio.FileData"},
                },
            },
        },
        "Meta": {
            "type": "object",
            "properties": {"_type": {"const": "gradio.FileData"}},
            "required": ["_type"],
        },
    },
}

# Plain object (no file data at all)
PLAIN_OBJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "number"},
    },
}


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    targets = [
        Path(REPO) / "client" / "python" / "gradio_client" / "utils.py",
    ]
    for p in targets:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(p)],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"{p.name} has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_file_schema_returns_filepath():
    """FileData-like JSON schema must produce 'filepath', not a verbose dict."""
    from gradio_client.utils import _json_schema_to_python_type

    result = _json_schema_to_python_type(
        FILE_DATA_SCHEMA, FILE_DATA_SCHEMA.get("$defs")
    )
    assert result == "filepath", (
        f"Expected 'filepath' for FileData schema, got: {result!r}"
    )


# [pr_diff] fail_to_pass
def test_image_like_schema_returns_filepath():
    """ImageData-like schema (meta via default) must also produce 'filepath'."""
    from gradio_client.utils import _json_schema_to_python_type

    result = _json_schema_to_python_type(
        IMAGE_DATA_SCHEMA, IMAGE_DATA_SCHEMA.get("$defs")
    )
    assert result == "filepath", (
        f"Expected 'filepath' for ImageData schema, got: {result!r}"
    )


# [pr_diff] fail_to_pass
def test_nested_file_shows_filepath_in_dict():
    """Object containing a file field should show 'filepath' in dict repr."""
    from gradio_client.utils import _json_schema_to_python_type

    result = _json_schema_to_python_type(
        GALLERY_ITEM_SCHEMA, GALLERY_ITEM_SCHEMA.get("$defs")
    )
    assert "filepath" in result, (
        f"Nested file field should render as 'filepath', got: {result!r}"
    )
    # The outer structure should still be dict(...)
    assert result.startswith("dict("), (
        f"Outer type should be dict(...), got: {result!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass — repo CI checks (ruff linting and formatting)
def test_client_lint():
    """gradio_client module passes ruff linting (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/gradio_client/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass — repo CI checks (ruff formatting)
def test_client_format():
    """gradio_client module passes ruff format check (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/gradio_client/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_non_file_object_still_dict():
    """Plain object schema (no file data) must still render as dict(...)."""
    from gradio_client.utils import _json_schema_to_python_type

    result = _json_schema_to_python_type(
        PLAIN_OBJECT_SCHEMA, PLAIN_OBJECT_SCHEMA.get("$defs")
    )
    assert result.startswith("dict("), f"Expected dict(...), got: {result!r}"
    assert "name" in result, f"Expected 'name' field in dict, got: {result!r}"
    assert "filepath" not in result, (
        f"Non-file schema must not contain 'filepath', got: {result!r}"
    )
