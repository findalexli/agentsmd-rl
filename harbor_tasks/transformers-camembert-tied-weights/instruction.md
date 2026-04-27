# Fix: CamembertForCausalLM crashes on instantiation due to weight tying error

## Problem

Instantiating `CamembertForCausalLM` crashes with a `ValueError` during `post_init()`. The error message says:

```
ValueError: There is an issue with your definition of `tie_weights_keys` for
^camembert.embeddings.word_embeddings.weight:^lm_head.decoder.weight.
We found [] to tie into ['lm_head.decoder.weight']
```

The model fails to load at all. The error indicates that the path `camembert.embeddings.word_embeddings.weight` referenced in `_tied_weights_keys` does not match any actual parameter in the model, so the weight tying mechanism cannot find the tensor it is supposed to tie. You will need to investigate what the actual parameter names are in the model and ensure `_tied_weights_keys` maps them correctly.

## Relevant files

The two files that define `CamembertForCausalLM` are:

- `src/transformers/models/camembert/modeling_camembert.py` — the generated modeling file
- `src/transformers/models/camembert/modular_camembert.py` — the modular source-of-truth file (where `CamembertForCausalLM` extends `RobertaForCausalLM`)

## Requirements

1. `CamembertForCausalLM` must instantiate without raising a `ValueError`. The resulting model must have both a `lm_head` attribute and a `roberta` attribute.
2. The `lm_head.decoder.weight` tensor must share memory with `roberta.embeddings.word_embeddings.weight` (verified by `data_ptr()` equality).
3. Mutating one weight must propagate to the other (bidirectional): writing to `model.lm_head.decoder.weight` must be reflected in `model.roberta.embeddings.word_embeddings.weight`, and vice versa.
4. The `_tied_weights_keys` attribute must be correctly defined for `CamembertForCausalLM` in both `modeling_camembert.py` and `modular_camembert.py`, with weight paths that match the actual parameter names in the model. The modular file is the source-of-truth and must also contain the fix.
5. All other Camembert model variants (`CamembertModel`, `CamembertForMaskedLM`, `CamembertForSequenceClassification`) must continue to work correctly.
6. Both files must remain syntactically valid, pass `ruff` linting/formatting, and pass the repository's `utils/check_copies.py` and `utils/checkers.py` validation utilities.
