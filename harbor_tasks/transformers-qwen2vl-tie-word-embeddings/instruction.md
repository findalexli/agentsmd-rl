# Bug: `tie_word_embeddings` incorrectly defined on Qwen2VL text sub-configs

## Summary

The `Qwen2VLTextConfig` and `Qwen2_5_VLTextConfig` classes in `src/transformers/models/qwen2_vl/configuration_qwen2_vl.py` and `src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py` each define `tie_word_embeddings` as a class-level dataclass field. This attribute does not belong on the text sub-config — it is not a valid parameter for these text models. Having it there causes incorrect behavior when the parent composite config tries to control word embedding tying, because the text config's hardcoded value shadows any setting on the parent.

As a consequence, downstream composite configs `ColQwen2Config` (`src/transformers/models/colqwen2/configuration_colqwen2.py`) and `ColModernVBertConfig` (`src/transformers/models/colmodernvbert/configuration_colmodernvbert.py`) had to add a workaround hack in `__post_init__` to propagate the text config's value up to the VLM config. With the root cause fixed, this hack becomes unnecessary dead code and should be removed.

Additionally, `ModernVBertForMaskedLM.__init__` in `src/transformers/models/modernvbert/modeling_modernvbert.py` (and its `modular_modernvbert.py` source) is missing a type annotation on its `config` parameter, which causes type checking failures.

## Files to investigate

- `src/transformers/models/qwen2_vl/configuration_qwen2_vl.py` — `Qwen2VLTextConfig` class
- `src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py` — `Qwen2_5_VLTextConfig` class
- `src/transformers/models/colqwen2/configuration_colqwen2.py` — `ColQwen2Config.__post_init__`
- `src/transformers/models/colmodernvbert/configuration_colmodernvbert.py` — `ColModernVBertConfig.__post_init__`
- `src/transformers/models/modernvbert/modeling_modernvbert.py` — `ModernVBertForMaskedLM.__init__`
- `src/transformers/models/modernvbert/modular_modernvbert.py` — `ModernVBertForMaskedLM.__init__`

## Expected behavior

- Text sub-configs should NOT define `tie_word_embeddings` — it is not a valid field for these models
- Composite configs should not need hacks to propagate embedding tying settings
- `ModernVBertForMaskedLM.__init__` should have a proper type annotation on its `config` parameter
