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


# [repo_tests] pass_to_pass — repo CI checks (ruff linting)
def test_client_lint():
    """gradio_client module passes ruff linting (pass_to_pass)."""
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/gradio_client/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo CI checks (ruff formatting)
def test_client_format():
    """gradio_client module passes ruff format check (pass_to_pass)."""
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/gradio_client/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo unit tests for utils module
def test_repo_utils_unit_tests():
    """gradio_client utils unit tests pass (pass_to_pass)."""
    # Run specific unit tests from test_utils.py that don't require gradio fixtures
    test_code = '''
import sys
sys.path.insert(0, "/workspace/gradio/client/python")
sys.path.insert(0, "/workspace/gradio/client/python/test")

# Import test functions directly
from gradio_client import utils

# Test: test_strip_invalid_filename_characters
assert utils.strip_invalid_filename_characters("abc") == "abc"
assert utils.strip_invalid_filename_characters("$$AAabc&3") == "AAabc3"

# Test: test_get_mimetype
assert utils.get_mimetype("photo.webp") == "image/webp"
assert utils.get_mimetype("image.png") == "image/png"

# Test: test_is_valid_file
assert utils.is_valid_file("/home/user/example.pdf", [".pdf"]) is True
assert utils.is_valid_file("/home/user/example.png", [".jpg"]) is False

print("All unit tests passed!")
'''
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout}\n{r.stderr}"


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
"""
Additional Pass-to-Pass tests for gradio-filepath-api-display task.
These are supplementary tests covering more of the repo's CI checks.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"


# [repo_tests] pass_to_pass — more comprehensive utils unit tests
def test_repo_utils_extended_tests():
    """gradio_client utils extended unit tests pass (pass_to_pass)."""
    # Extended tests covering more edge cases from test_utils.py
    test_code = '''
import sys
sys.path.insert(0, "/workspace/gradio/client/python")

from gradio_client import utils

# Extended strip_invalid_filename_characters tests
assert utils.strip_invalid_filename_characters("$$AAa&..b-c3_") == "AAa..b-c3_"
assert utils.strip_invalid_filename_characters("#.txt") == "file.txt"
assert utils.strip_invalid_filename_characters("###.pdf") == "file.pdf"
assert utils.strip_invalid_filename_characters("@!$.csv") == "file.csv"

# Extended get_mimetype tests
assert utils.get_mimetype("photo.WEBP") == "image/webp"  # case insensitive
assert utils.get_mimetype("photo.WebP") == "image/webp"
assert utils.get_mimetype("video.vtt") == "text/vtt"
assert utils.get_mimetype("video.VTT") == "text/vtt"

# Extended is_valid_file tests
assert utils.is_valid_file("C:/Users/user/documents/example.png", [".png"]) is True
assert utils.is_valid_file("C:/Users/user/documents/example.png", ["image"]) is True
assert utils.is_valid_file("C:/Users/user/documents/example.png", ["file"]) is True
assert utils.is_valid_file("https://example.com/avatar/xxxx.mp4", ["audio", ".png", ".jpg"]) is False

# Test: encode_url_or_file_to_base64 on real file
import tempfile
import os
with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
    f.write(b"test content")
    tmp_path = f.name
try:
    result = utils.encode_file_to_base64(tmp_path)
    assert result.startswith("data:text/plain;base64,"), f"Expected base64 data URI, got: {result[:50]}"
    assert "dGVzdCBjb250ZW50" in result  # base64 encoded "test content"
finally:
    os.unlink(tmp_path)

# Test: get_extension - check function works (actual values depend on system mimetypes db)
ext_result = utils.get_extension("audio/wav")
assert ext_result is None or ext_result == "wav", f"Expected None or 'wav', got: {ext_result}"
ext_result = utils.get_extension("audio/flac")
assert ext_result == "flac" or ext_result is None, f"Expected 'flac' or None, got: {ext_result}"

# Test: is_http_url_like
assert utils.is_http_url_like("https://example.com/file.txt") is True
assert utils.is_http_url_like("http://example.com/file.txt") is True
assert utils.is_http_url_like("/home/user/file.txt") is False

print("All extended unit tests passed!")
'''
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Extended unit tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo CI checks (ruff linting on whole client/python)
def test_client_python_lint():
    """Full client/python module passes ruff linting (pass_to_pass)."""
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo CI checks (ruff format on whole client/python)
def test_client_python_format():
    """Full client/python module passes ruff format check (pass_to_pass)."""
    subprocess.run(["pip", "install", "-q", "ruff"], check=False, capture_output=True)
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — test specific utils functions modified in PR
def test_utils_json_schema_functions():
    """gradio_client utils JSON schema functions work correctly (pass_to_pass)."""
    test_code = '''
import sys
sys.path.insert(0, "/workspace/gradio/client/python")

from gradio_client import utils
import json

# Test: json_schema_to_python_type with basic types
schema_str = {"type": "string"}
result = utils.json_schema_to_python_type(schema_str)
assert result == "str", f"Expected 'str', got: {result}"

schema_int = {"type": "integer"}
result = utils.json_schema_to_python_type(schema_int)
assert result == "int", f"Expected 'int', got: {result}"

schema_num = {"type": "number"}
result = utils.json_schema_to_python_type(schema_num)
assert result == "float", f"Expected 'float', got: {result}"

schema_bool = {"type": "boolean"}
result = utils.json_schema_to_python_type(schema_bool)
assert result == "bool", f"Expected 'bool', got: {result}"

# Test: json_schema_to_python_type with array
schema_array = {"type": "array", "items": {"type": "string"}}
result = utils.json_schema_to_python_type(schema_array)
assert result == "list[str]", f"Expected 'list[str]', got: {result}"

# Test: json_schema_to_python_type with object (non-file)
schema_obj = {"type": "object", "properties": {"name": {"type": "string"}, "count": {"type": "integer"}}}
result = utils.json_schema_to_python_type(schema_obj)
assert "dict(" in result, f"Expected 'dict(...)', got: {result}"
assert "name" in result, f"Expected 'name' field, got: {result}"
assert "count" in result, f"Expected 'count' field, got: {result}"

# Test: value_is_file with non-file schema (before fix, this checks it doesn't crash)
non_file_schema = {"type": "object", "properties": {"text": {"type": "string"}}}
# This shouldn't crash - we're checking the function exists and works
result = utils.value_is_file(non_file_schema)
assert result is False, f"Expected False for non-file schema, got: {result}"

print("All JSON schema function tests passed!")
'''
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"JSON schema function tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — test python_type_to_json_schema function
def test_utils_python_type_to_schema():
    """gradio_client utils python_type_to_json_schema works correctly (pass_to_pass)."""
    test_code = '''
import sys
sys.path.insert(0, "/workspace/gradio/client/python")

from gradio_client import utils
from typing import Any, Union, Optional

# Test: python_type_to_json_schema with basic types
assert utils.python_type_to_json_schema(str) == {"type": "string"}
assert utils.python_type_to_json_schema(int) == {"type": "integer"}
assert utils.python_type_to_json_schema(float) == {"type": "number"}
assert utils.python_type_to_json_schema(bool) == {"type": "boolean"}
assert utils.python_type_to_json_schema(type(None)) == {"type": "null"}

# Test: with complex types
result = utils.python_type_to_json_schema(Union[str, int])
assert "anyOf" in result, f"Expected 'anyOf' in result, got: {result}"

result = utils.python_type_to_json_schema(Optional[str])
assert "oneOf" in result or "anyOf" in result, f"Expected union type, got: {result}"

result = utils.python_type_to_json_schema(dict)
assert result == {"type": "object", "additionalProperties": {}}, f"Expected dict schema, got: {result}"

result = utils.python_type_to_json_schema(list)
assert result == {"type": "array", "items": {}}, f"Expected list schema, got: {result}"

print("All python_type_to_json_schema tests passed!")
'''
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"python_type_to_json_schema tests failed:\n{r.stdout}\n{r.stderr}"
