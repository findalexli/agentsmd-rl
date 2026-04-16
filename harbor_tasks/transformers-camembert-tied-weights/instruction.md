# Fix: Incorrect _tied_weights_keys in CamembertForCausalLM

## Problem

Instantiating `CamembertForCausalLM` crashes with a `ValueError` during `post_init()`. The error message says:

```
ValueError: There is an issue with your definition of `tie_weights_keys` for
^camembert.embeddings.word_embeddings.weight:^lm_head.decoder.weight.
We found [] to tie into ['lm_head.decoder.weight']
```

The model fails to load at all due to a mismatch in the weight tying key definitions. Note that `CamembertForCausalLM` inherits from the RoBERTa architecture, so internally the model backbone is accessed via the `roberta` attribute (i.e., `model.roberta`), not `camembert`. The embedding weights live at `model.roberta.embeddings.word_embeddings.weight`.

## Relevant files

The two files that define `CamembertForCausalLM` are:

- `src/transformers/models/camembert/modeling_camembert.py` — the generated modeling file
- `src/transformers/models/camembert/modular_camembert.py` — the modular source-of-truth file (where `CamembertForCausalLM` extends `RobertaForCausalLM`)

## Requirements

1. `CamembertForCausalLM` must instantiate without raising a `ValueError`. The resulting model must have both a `lm_head` attribute and a `roberta` attribute.
2. The `lm_head.decoder.weight` tensor must share memory with `roberta.embeddings.word_embeddings.weight` (verified by `data_ptr()` equality).
3. Mutating one weight must propagate to the other (bidirectional): writing to `model.lm_head.decoder.weight` must be reflected in `model.roberta.embeddings.word_embeddings.weight`, and vice versa.
4. The `_tied_weights_keys` attribute must be defined for `CamembertForCausalLM` in both `modeling_camembert.py` and `modular_camembert.py`. In the modular file, the class must explicitly override `_tied_weights_keys` with the correct `roberta.embeddings.word_embeddings.weight` path.
5. All other Camembert model variants (`CamembertModel`, `CamembertForMaskedLM`, `CamembertForSequenceClassification`) must continue to work correctly.
6. Both files must remain syntactically valid, pass `ruff` linting/formatting, and pass the repository's `utils/check_copies.py` and `utils/checkers.py` validation utilities.
