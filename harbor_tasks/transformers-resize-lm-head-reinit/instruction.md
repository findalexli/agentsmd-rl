# Fix resized LM head weights being overwritten by post_init

## Problem

When `tie_word_embeddings=False`, calling `resize_token_embeddings()` followed by `post_init()` overwrites the LM head weights with random values.

This happens because `_get_resized_lm_head()` returns a new `nn.Linear` module without setting `_is_hf_initialized = True`. When `post_init()` runs, it sees the LM head as uninitialized and re-initializes all weights.

### Symptoms

1. Create a model with `tie_word_embeddings=False`
2. Call `resize_token_embeddings()` to expand vocabulary
3. Call `post_init()` (e.g., after loading or during model preparation)
4. The LM head weights will be replaced with random values — any previously learned weights are lost

### Example scenario

```python
from transformers import AutoConfig, AutoModelForCausalLM

config = AutoConfig.from_pretrained("gpt2")
config.tie_word_embeddings = False

model = AutoModelForCausalLM.from_config(config)

# User resizes embeddings for new tokens
model.resize_token_embeddings(config.vocab_size + 100)

# Later, post_init is called (e.g., by training framework)
model.post_init()
# BUG: LM head weights are now random!
```

## Files to Look At

- `src/transformers/modeling_utils.py` — Contains `_get_resized_lm_head()` and `_get_resized_embeddings()` methods

## Expected Fix

The fix should set `new_lm_head._is_hf_initialized = True` after all weight copying is done in `_get_resized_lm_head()`, similar to how `_get_resized_embeddings()` already preserves the original module object (which already has the flag set).

The fix should be minimal — likely a single line addition.
