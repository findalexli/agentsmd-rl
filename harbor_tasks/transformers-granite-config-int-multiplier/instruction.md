# Bug: GraniteConfig rejects integer values for multiplier fields

## Problem

Loading certain Granite model configurations fails with a `StrictDataclassFieldValidationError`. The issue occurs when a model's `config.json` stores multiplier-related fields (such as embedding multiplier, logits scaling, residual multiplier, and attention multiplier) as integers instead of floats.

For example, a config like:
```json
{
  "embedding_multiplier": 12,
  "logits_scaling": 8
}
```
causes the config loader to reject these values because the dataclass fields only accept `float`, not `int`.

## Affected Files

- `src/transformers/models/granite/configuration_granite.py` — `GraniteConfig` class
- `src/transformers/models/granitemoe/configuration_granitemoe.py` — `GraniteMoeConfig` class
- `src/transformers/models/granitemoeshared/configuration_granitemoeshared.py` — `GraniteMoeSharedConfig` class

## Reproduction

```python
from transformers import GraniteConfig
# This should work but raises StrictDataclassFieldValidationError:
config = GraniteConfig(embedding_multiplier=12, logits_scaling=8)
```

## Hints

- Look at how `attention_dropout` is typed in the same class — it already handles a similar situation.
- The fix needs to be applied consistently across all three Granite config variants.
