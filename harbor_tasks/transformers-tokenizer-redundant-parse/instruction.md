# Redundant tokenizer.json parsing in `convert_to_native_format`

## Bug

In `src/transformers/tokenization_utils_tokenizers.py`, the classmethod `TokenizersBackend.convert_to_native_format()` has a performance bug in the code path for tokenizers with a custom `__init__` (the `elif` branch starting around line 120).

When a fast tokenizer file (`tokenizer.json`) is present and the tokenizer class defines its own `__init__`, the method parses the file **twice**:

1. A full Rust-level parse via `TokenizerFast.from_file()` — which builds the entire tokenizer including vocabulary (expensive for large vocabularies like 256K entries). This is done only to extract `post_processor`, `padding`, and `truncation`.
2. A Python `json.load()` parse of the **same file** — to extract `vocab`, `merges`, and normalizer configuration.

For tokenizers with large vocabularies (e.g., CohereTokenizer with 256K entries), the redundant Rust parse adds ~0.4 seconds per load.

## Expected behavior

The file should be parsed once. The `post_processor`, `padding`, and `truncation` Rust objects can be obtained without parsing the full vocabulary. The result dict returned by `convert_to_native_format` must contain at minimum the following keys:

- `vocab` — a dict mapping tokens to indices (BPE, WordPiece, WordLevel) or a list of token entries (Unigram)
- `merges` — a list of merge strings (BPE only)
- `post_processor` — the post-processor object
- `tokenizer_padding` — the padding configuration object
- `tokenizer_truncation` — the truncation configuration object
- `tokenizer_object` — the full tokenizer object (returned when the base class path is taken, i.e., no custom `__init__`)

The optimized path must avoid calling `TokenizerFast.from_file()` for model types where a lighter-weight alternative suffices. The model type is declared in the `model.type` field of `tokenizer.json`: `BPE`, `WordPiece`, `WordLevel`, and `Unigram` are the recognized types. Older `tokenizer.json` files may omit the `type` field entirely — in that case a fallback to the original (non-optimized) behavior is acceptable.

## Relevant files

- `src/transformers/tokenization_utils_tokenizers.py` — the `convert_to_native_format` classmethod in the `TokenizersBackend` class

## Hints

- The `post_processor`, `padding`, and `truncation` Rust objects don't depend on the vocabulary — they can be extracted from a much lighter representation of the tokenizer.
- Not all tokenizer model types behave the same when constructed with minimal data — some require a real vocabulary to initialize correctly.
- Some older `tokenizer.json` formats omit the `"type"` field in the `"model"` section, so a fallback path is needed for those cases.