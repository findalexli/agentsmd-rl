# NemotronH Config Docstring Mismatch

## Bug Description

The `NemotronHConfig` class in `src/transformers/models/nemotron_h/configuration_nemotron_h.py` has a docstring that is out of sync with the class's actual annotated attributes. Running `make check-repo` (specifically the `check_docstrings` utility) reports that some documented parameter names don't correspond to any class-level annotation, while some actual annotated attributes are missing from the docstring entirely.

## What to Fix

Investigate the `NemotronHConfig` class and compare the parameter names listed in its docstring against the class-level annotated attributes defined in the class body. You will find that some parameters documented in the docstring are not real class annotations — they are only backward-compatibility aliases handled in `__post_init__`. Meanwhile, the actual class annotations those aliases map to are not documented.

Fix the docstring so that:
- Every documented parameter name corresponds to an actual class-level annotated attribute
- Any annotated attributes that are currently missing from the docstring are added with appropriate descriptions
- All existing correctly-documented parameters remain intact
- The backward-compatibility alias handling in `__post_init__` must not be removed — those aliases need to continue working at runtime, they just should not be documented as primary parameters in the docstring
- The file must continue to pass `ruff format` and `ruff check`

## Relevant Files

- `src/transformers/models/nemotron_h/configuration_nemotron_h.py`
