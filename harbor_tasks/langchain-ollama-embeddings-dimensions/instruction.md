# Task: Add `dimensions` parameter to `OllamaEmbeddings`

## Problem

The `OllamaEmbeddings` class in `libs/partners/ollama/langchain_ollama/embeddings.py` does not support specifying the output embedding dimensionality. Users need to be able to control the size of embedding vectors returned by the Ollama API, as some models support variable dimensions.

When attempting to pass `dimensions=768` (or any value) to `OllamaEmbeddings`, the current implementation does not accept this parameter.

## Requirements

Add a `dimensions` parameter to the `OllamaEmbeddings` class that:

1. Is defined as an optional field accepting `int | None` (defaults to `None`)
2. Validates that when set, the value is a positive integer (≥ 1), raising `ValueError` with message containing "positive integer" for zero or negative values
3. The validated value is passed to the Ollama client's `embed()` method for both synchronous (`embed_documents`) and asynchronous (`aembed_documents`) calls, using the expression `dimensions=self.dimensions`
4. The validation is implemented via a function named `_validate_dimensions` decorated with `@field_validator`

## Files to Modify

- `libs/partners/ollama/langchain_ollama/embeddings.py` - Add the `dimensions` field and validation

## Testing

The repository has unit tests in `tests/unit_tests/test_embeddings.py` that you can reference for testing patterns. The repository uses:
- `uv` for dependency management
- `pytest` for testing
- `ruff` for linting

Run tests with: `uv run --group test pytest tests/unit_tests/test_embeddings.py -v`
