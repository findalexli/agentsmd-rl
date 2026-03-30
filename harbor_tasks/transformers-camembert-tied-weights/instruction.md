# Fix: Incorrect _tied_weights_keys in CamembertForCausalLM

## Problem

Loading `CamembertForCausalLM` (e.g., via `AutoModelForCausalLM.from_pretrained("hf-internal-testing/tiny-random-camembert")`) crashes with a `ValueError` during `post_init()`. The error message says:

```
ValueError: There is an issue with your definition of `tie_weights_keys` for
^camembert.embeddings.word_embeddings.weight:^lm_head.decoder.weight.
We found [] to tie into ['lm_head.decoder.weight']
```

The model fails to load at all due to this mismatch in the weight tying key definitions.

## Root Cause

`CamembertForCausalLM` defines `_tied_weights_keys` with an incorrect embedding path. The dict maps `"lm_head.decoder.weight"` to `"camembert.embeddings.word_embeddings.weight"`, but the model's actual embedding layer is stored under `self.roberta`, not `self.camembert`. The correct path is `"roberta.embeddings.word_embeddings.weight"`.

This bug exists in both `modeling_camembert.py` (the generated file) and `modular_camembert.py` (the source-of-truth modular file). The modular file inherits from `RobertaForCausalLM` but has the wrong tied weights key that was incorrectly set to use "camembert" instead of "roberta" as the prefix.

## Files to Modify

- `src/transformers/models/camembert/modeling_camembert.py` -- fix `_tied_weights_keys` in `CamembertForCausalLM`
- `src/transformers/models/camembert/modular_camembert.py` -- add correct `_tied_weights_keys` override in `CamembertForCausalLM`
