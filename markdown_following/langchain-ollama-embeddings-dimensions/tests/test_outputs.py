"""Tests for langchain-ollama dimensions feature.

This test file verifies that the OllamaEmbeddings class properly supports
the `dimensions` parameter for controlling output embedding size.
"""

import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from langchain_ollama import OllamaEmbeddings

REPO = Path("/workspace/langchain/libs/partners/ollama")


def test_dimensions_field_exists():
    """OllamaEmbeddings has a `dimensions` field that accepts int or None."""
    # Should be able to create with dimensions=None (default)
    emb = OllamaEmbeddings(model="llama3")
    assert emb.dimensions is None

    # Should be able to create with explicit dimensions
    emb = OllamaEmbeddings(model="llama3", dimensions=512)
    assert emb.dimensions == 512


def test_dimensions_validation_positive():
    """Dimensions must be a positive integer - valid cases."""
    # Valid positive integers should work
    for dim in [1, 10, 512, 768, 1024, 4096]:
        emb = OllamaEmbeddings(model="llama3", dimensions=dim)
        assert emb.dimensions == dim


def test_dimensions_validation_zero():
    """Dimensions=0 should raise ValueError."""
    with pytest.raises(ValueError, match="positive integer"):
        OllamaEmbeddings(model="llama3", dimensions=0)


def test_dimensions_validation_negative():
    """Dimensions negative values should raise ValueError."""
    for dim in [-1, -10, -100, -512]:
        with pytest.raises(ValueError, match="positive integer"):
            OllamaEmbeddings(model="llama3", dimensions=dim)


@patch("langchain_ollama.embeddings.Client")
def test_embed_documents_passes_dimensions(mock_client_class):
    """embed_documents passes dimensions to the Ollama client embed call."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    embeddings = OllamaEmbeddings(model="llama3", dimensions=512)
    embeddings.embed_documents(["test text"])

    call_args = mock_client.embed.call_args
    assert call_args.kwargs["dimensions"] == 512


@patch("langchain_ollama.embeddings.Client")
def test_embed_documents_dimensions_none_by_default(mock_client_class):
    """When dimensions not specified, None is passed to the client."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    embeddings = OllamaEmbeddings(model="llama3")
    embeddings.embed_documents(["test text"])

    call_args = mock_client.embed.call_args
    assert call_args.kwargs["dimensions"] is None


@patch("langchain_ollama.embeddings.AsyncClient")
@patch("langchain_ollama.embeddings.Client")
def test_aembed_documents_passes_dimensions(mock_client_class, mock_async_client_class):
    """aembed_documents passes dimensions to the async Ollama client embed call."""
    mock_async_client = AsyncMock()
    mock_async_client_class.return_value = mock_async_client
    mock_async_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    embeddings = OllamaEmbeddings(model="llama3", dimensions=512)

    import asyncio
    asyncio.run(embeddings.aembed_documents(["test text"]))

    call_args = mock_async_client.embed.call_args
    assert call_args.kwargs["dimensions"] == 512


@patch("langchain_ollama.embeddings.AsyncClient")
@patch("langchain_ollama.embeddings.Client")
def test_aembed_documents_dimensions_none_by_default(mock_client_class, mock_async_client_class):
    """When dimensions not specified, None is passed to async client."""
    mock_async_client = AsyncMock()
    mock_async_client_class.return_value = mock_async_client
    mock_async_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    embeddings = OllamaEmbeddings(model="llama3")

    import asyncio
    asyncio.run(embeddings.aembed_documents(["test text"]))

    call_args = mock_async_client.embed.call_args
    assert call_args.kwargs["dimensions"] is None


def test_dimensions_various_values():
    """Test that various valid dimension values work correctly."""
    test_values = [256, 512, 768, 1024, 2048, 4096]
    for dim in test_values:
        emb = OllamaEmbeddings(model="llama3", dimensions=dim)
        assert emb.dimensions == dim, f"Failed for dimensions={dim}"


@patch("langchain_ollama.embeddings.Client")
def test_embed_query_uses_dimensions(mock_client_class):
    """embed_query should also use the dimensions parameter via embed_documents."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    embeddings = OllamaEmbeddings(model="llama3", dimensions=768)
    embeddings.embed_query("test query")

    call_args = mock_client.embed.call_args
    assert call_args.kwargs["dimensions"] == 768


def test_repo_unit_tests_pass():
    """Repo's own unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/test_embeddings.py", "-v", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_repo_ruff_check():
    """Repo's linter passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "ruff", "check", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # If ruff is not installed, skip this test
    if "No module named" in result.stderr:
        pytest.skip("ruff not installed")
    assert result.returncode == 0, f"Ruff check failed:\n{result.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's code formatting passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "ruff", "format", "--diff", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    if "No module named" in result.stderr:
        pytest.skip("ruff not installed")
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout[-500:]}"


def test_repo_imports_check():
    """Repo's imports check script passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "scripts/lint_imports.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Import lint check failed:\n{result.stderr[-500:]}"


def test_repo_package_imports():
    """Repo package imports work correctly (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from langchain_ollama import __all__; print('Imports OK')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Package import failed:\n{result.stderr[-500:]}"


def test_repo_embeddings_import():
    """Embeddings module imports work correctly (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from langchain_ollama.embeddings import OllamaEmbeddings; print('Embeddings OK')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Embeddings import failed:\n{result.stderr[-500:]}"


def test_repo_py_compile():
    """Python files compile without errors (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "py_compile", "langchain_ollama/embeddings.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Python compilation failed:\n{result.stderr[-500:]}"


def test_repo_imports_test():
    """Repo's own imports test passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/test_imports.py", "-x", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Imports test failed:\n{result.stderr[-500:]}"


def test_repo_llms_unit_tests():
    """Repo's LLM unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/test_llms.py", "-x", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"LLM tests failed:\n{result.stderr[-500:]}"


def test_repo_auth_unit_tests():
    """Repo's auth unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/test_auth.py", "-x", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Auth tests failed:\n{result.stderr[-500:]}"
