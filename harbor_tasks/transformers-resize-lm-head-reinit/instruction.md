# Fix resized LM head weights being overwritten by post_init

## Problem

When `tie_word_embeddings=False`, calling `resize_token_embeddings()` followed by `post_init()` overwrites the LM head weights with random values.

### Symptoms

1. Create a model with `tie_word_embeddings=False`
2. Call `resize_token_embeddings()` to expand or shrink the vocabulary
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

## Root Cause

The `post_init()` method iterates over a model's modules and checks each module's `_is_hf_initialized` attribute. If this flag is `False` (or missing), `post_init()` treats the module as uninitialized and reinitializes its weights. When `_get_resized_lm_head()` creates a new `nn.Linear` for the resized LM head, the newly created module does not carry the `_is_hf_initialized` flag, so a subsequent `post_init()` call reinitializes its weights — overwriting the values that were carefully copied during the resize.

## Expected Behavior

After `resize_token_embeddings()` is called, subsequent calls to `post_init()` must preserve the LM head weights exactly as they were after the resize operation. The weights should not be reinitialized to random values.

## Files to Look At

- `src/transformers/modeling_utils.py` — Contains `resize_token_embeddings()`, `_get_resized_lm_head()`, `_get_resized_embeddings()`, and `post_init()`
