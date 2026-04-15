# Bug: GraniteConfig rejects integer values for multiplier fields

## Problem

Loading certain Granite model configurations fails with a `StrictDataclassFieldValidationError`. The issue occurs when a model's `config.json` stores multiplier-related fields as integers instead of floats.

For example, a config like:
```json
{
  "embedding_multiplier": 12,
  "logits_scaling": 8
}
```
causes the config loader to reject these values because the dataclass fields only accept `float`, not `int`.

## Affected Fields

The following constructor parameters across all three Granite config classes must accept integer values:

- `GraniteConfig`:
  - `embedding_multiplier`
  - `logits_scaling`
  - `residual_multiplier`
  - `attention_multiplier`

- `GraniteMoeConfig`:
  - `embedding_multiplier`
  - `logits_scaling`
  - `residual_multiplier`
  - `attention_multiplier`
  (also must accept `None` values for these fields)

- `GraniteMoeSharedConfig`:
  - `embedding_multiplier`
  - `logits_scaling`
  (also must accept `None` values for these fields)

## Reproduction

```python
from transformers import GraniteConfig
# This should work but raises StrictDataclassFieldValidationError:
config = GraniteConfig(embedding_multiplier=12, logits_scaling=8)
```

## Required Behavior

1. **Integer values must be accepted** for all multiplier fields (`embedding_multiplier`, `logits_scaling`, `residual_multiplier`, `attention_multiplier`) across all three config classes.

2. **Roundtrip persistence must work**: configs with integer multiplier values must survive `save_pretrained()` / `from_pretrained()` roundtrips without data loss.

3. **Float values must continue to work** — existing float defaults (1.0) and explicit float values must still be accepted.

4. **None values must be accepted** where the config class allows them (`GraniteMoeConfig` and `GraniteMoeSharedConfig`).

5. **Repo CI/CD gates must pass**: after any fix, `ruff check`, `ruff format --check`, and existing Granite model tests must still pass.

## Affected Files

- `src/transformers/models/granite/configuration_granite.py` — `GraniteConfig` class
- `src/transformers/models/granitemoe/configuration_granitemoe.py` — `GraniteMoeConfig` class
- `src/transformers/models/granitemoeshared/configuration_granitemoeshared.py` — `GraniteMoeSharedConfig` class