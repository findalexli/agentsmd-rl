# Redundant tokenizer.json parsing in `convert_to_native_format`

## Bug

In `src/transformers/tokenization_utils_tokenizers.py`, the classmethod `TokenizersBackend.convert_to_native_format()` has a performance bug in the code path for tokenizers with a custom `__init__` (the `elif` branch starting around line 120).

When a fast tokenizer file (`tokenizer.json`) is present and the tokenizer class defines its own `__init__`, the method parses the file **twice**:

1. A full Rust-level parse via `TokenizerFast.from_file()` — which builds the entire tokenizer including vocabulary (expensive for large vocabularies like 256K entries). This is done only to extract `post_processor`, `padding`, and `truncation`.
2. A Python `json.load()` parse of the **same file** — to extract `vocab`, `merges`, and normalizer configuration.

For tokenizers with large vocabularies (e.g., CohereTokenizer with 256K entries), the redundant Rust parse adds ~0.4 seconds per load.

## Expected behavior

The file should only be parsed once. The `post_processor`, `padding`, and `truncation` objects can be obtained without parsing the full vocabulary.

## Relevant files

- `src/transformers/tokenization_utils_tokenizers.py` — the `convert_to_native_format` classmethod in the `TokenizersBackend` class

## Hints

- The `post_processor`, `padding`, and `truncation` fields don't depend on the vocabulary — they can be extracted from a much lighter representation of the tokenizer.
- Not all tokenizer model types (BPE, WordPiece, WordLevel, Unigram) behave the same when constructed with minimal data — some require a real vocabulary.
- Some older `tokenizer.json` formats omit the `"type"` field in the `"model"` section, so a fallback path is needed.
