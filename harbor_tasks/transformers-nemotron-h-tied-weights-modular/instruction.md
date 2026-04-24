# NemotronH model: incorrect `_tied_weights_keys` placement and modular `__init__` override

## Bug Description

The `NemotronHPreTrainedModel` base class in `src/transformers/models/nemotron_h/modeling_nemotron_h.py` incorrectly defines a class attribute that should only exist on the causal LM subclass, not on the base pretrained model class. This shadows the parent class's attribute and can cause unexpected behavior during weight tying.

Additionally, the modular file (`modular_nemotron_h.py`) has a `NemotronHForCausalLM.__init__` override that exists solely to delete the attribute after construction — a workaround for the base class issue. This override is unnecessary and should be removed. The generated modeling file's `NemotronHForCausalLM.__init__` is also missing a proper type annotation on its `config` parameter.

## Affected Files

- `src/transformers/models/nemotron_h/modeling_nemotron_h.py` — the `NemotronHPreTrainedModel` class and `NemotronHForCausalLM.__init__`
- `src/transformers/models/nemotron_h/modular_nemotron_h.py` — the `NemotronHForCausalLM` class

## Expected Behavior

- The weight-tying keys attribute should only be defined on the causal LM class, not on the base pretrained model class.
- The modular file should not need to override `__init__` just to clean up a misplaced base class attribute.
- The config parameter in the modeling file's `__init__` should have the correct type annotation.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
