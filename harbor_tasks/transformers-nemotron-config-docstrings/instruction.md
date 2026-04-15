# NemotronH Config Docstring Mismatch

## Bug Description

The `NemotronHConfig` class in `src/transformers/models/nemotron_h/configuration_nemotron_h.py` has a docstring that documents parameters which don't match the actual class attributes.

The docstring currently documents these deprecated parameter names:
- `mamba_dt_min`
- `mamba_dt_max`
- `mamba_dt_limit`
- `mamba_dt_init_floor`

These are backward-compatibility aliases that only exist in `__post_init__` handling. The actual class attributes with annotations are:
- `n_groups` (default: 8)
- `expand` (default: 2)
- `use_conv_bias` (default: True)
- `chunk_size` (default: 128)

This causes `check_docstrings` (run by `make check-repo`) to fail, reporting that documented parameters don't match the class signature.

## What to Fix

Update the docstring of `NemotronHConfig` so that the documented parameter names match the actual class attributes. The four deprecated names (`mamba_dt_min`, `mamba_dt_max`, `mamba_dt_limit`, `mamba_dt_init_floor`) must be removed from the docstring and replaced with documentation for the four actual attributes (`n_groups`, `expand`, `use_conv_bias`, `chunk_size`).

Look at the class body annotations to see the correct parameter names and their default values. Ensure all other existing documented parameters remain intact.

## Relevant Files

- `src/transformers/models/nemotron_h/configuration_nemotron_h.py`
