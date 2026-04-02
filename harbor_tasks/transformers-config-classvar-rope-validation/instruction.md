# Bug: Config ClassVar type hints prevent per-instance serialization, and RoPE validation crashes on empty dict

## Problem 1: `transformers_version` and `architectures` are ClassVar but shouldn't be

In `src/transformers/configuration_utils.py`, the `PreTrainedConfig` dataclass declares
`transformers_version` and `architectures` as `ClassVar`. This is incorrect — these fields
are set per-instance (each config gets its own version and architecture list when saved/loaded),
not shared across all instances of the class. Because they are `ClassVar`, they are excluded from
`dataclasses.fields()` and from serialization. They also don't appear in the config's `__dict__`
in the expected way.

Additionally, `utils/check_config_attributes.py` has an allowlist of attributes
(`ATTRIBUTES_TO_ALLOW`) that is missing these two fields, causing false positives
in config attribute validation checks.

## Problem 2: RoPE validation fails on empty `rope_parameters` dict

In `src/transformers/modeling_rope_utils.py`, the `validate_rope()` function checks
`if rope_parameters_dict is None: return` to skip validation for non-RoPE configs.
However, some configs set `rope_parameters` to an empty dict `{}` instead of `None`.
The empty dict passes the `is None` check and then validation proceeds, hitting errors
because the dict has no entries to validate against.

The fix should also handle the empty dict case, not just `None`.

## Problem 3: Auto-docstring shows inherited parameters for config classes

In `src/transformers/utils/auto_docstring.py`, when generating docstrings for config
classes (which are dataclasses), the `auto_class_docstring` function documents ALL
parameters from the full class hierarchy. This means every config subclass's docstring
includes parameters from `PreTrainedConfig` and all parent classes, producing very long
and confusing docstrings.

Config classes should only document their own parameters (fields defined directly on
the class), not inherited ones. The docstring generation pipeline needs a way to filter
which parameters get documented.

## Files to investigate

- `src/transformers/configuration_utils.py` — ClassVar declarations
- `src/transformers/modeling_rope_utils.py` — `validate_rope()` function
- `src/transformers/utils/auto_docstring.py` — `auto_class_docstring()` and parameter processing
- `utils/check_config_attributes.py` — `ATTRIBUTES_TO_ALLOW` tuple
- `tests/utils/test_configuration_utils.py` — config test expectations
