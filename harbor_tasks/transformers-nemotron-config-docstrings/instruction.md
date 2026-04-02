# NemotronH Config Docstring Mismatch

## Bug Description

The `NemotronHConfig` class in `src/transformers/models/nemotron_h/configuration_nemotron_h.py` has a docstring that documents parameters which don't match the actual class attributes.

Several of the documented parameter names in the docstring correspond to old/deprecated names that are only accepted through backward-compatibility handling in `__post_init__`. The actual class attributes have different names, but the docstring still lists the old names instead.

This causes `check_docstrings` (run by `make check-repo`) to fail, reporting that documented parameters don't match the class signature.

## What to Fix

Update the docstring of `NemotronHConfig` so that the documented parameter names match the actual class attributes. Look at the class body to see what attributes are actually declared, and compare them against what's documented in the docstring. Several parameters in the mamba-related section of the docstring need to be corrected.

## Relevant Files

- `src/transformers/models/nemotron_h/configuration_nemotron_h.py`
