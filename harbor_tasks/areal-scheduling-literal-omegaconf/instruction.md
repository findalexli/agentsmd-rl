# Bug: SchedulingSpec crashes on config loading with omegaconf

## Summary

The `SchedulingSpec` dataclass in `areal/api/cli_args.py` causes a `ValidationError`
whenever any code path loads a config that includes scheduling configuration.

## Reproduction

```python
from omegaconf import OmegaConf
from areal.api.cli_args import SchedulingSpec

OmegaConf.structured(SchedulingSpec())  # Raises ValidationError
```

## Expected Behavior

1. `OmegaConf.structured(SchedulingSpec())` must succeed without raising `ValidationError`
2. The valid values for `ray_placement_strategy` are: `"shared"`, `"separate"`, `"deferred"`
3. Invalid values must be rejected at runtime with a `ValueError` that includes the field name `"ray_placement_strategy"` in the error message
4. The default value when `SchedulingSpec()` is instantiated with no arguments must be `"shared"`

## Code Standards (per AGENTS.md)

The file `areal/api/cli_args.py` must comply with these rules:

- **No wildcard imports** — do not use `from X import *`
- **Unused imports must be removed** — if a `Literal` import from `typing` is no longer needed in type annotations, it must be deleted
- **No bare print() calls** — use `areal.utils.logging` instead
- **Ruff formatting must pass** — code must conform to the project's ruff configuration

## What to Fix

The `SchedulingSpec` dataclass currently uses a `Literal` type annotation for the `ray_placement_strategy` field. This is incompatible with the version of omegaconf pinned in the project (`omegaconf 2.4.0.dev2`). You must change the field's type annotation while preserving runtime validation of allowed values.