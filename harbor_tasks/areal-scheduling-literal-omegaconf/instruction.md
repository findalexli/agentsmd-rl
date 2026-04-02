# Bug: SchedulingSpec crashes on config loading with omegaconf

## Summary

The `SchedulingSpec` dataclass in `areal/api/cli_args.py` causes a `ValidationError`
whenever any code path loads a config that includes scheduling configuration. This
affects **all** scheduler types, not just Ray — including `scheduler.type=local`.

## Reproduction

```python
from omegaconf import OmegaConf
from areal.api.cli_args import SchedulingSpec

OmegaConf.structured(SchedulingSpec())  # Raises ValidationError
```

The error message indicates that the type annotation used for the
`ray_placement_strategy` field is not supported by the version of omegaconf pinned in
the project (`omegaconf 2.4.0.dev2`).

## Where to look

- `areal/api/cli_args.py` — the `SchedulingSpec` dataclass, specifically the
  `ray_placement_strategy` field's type annotation
- The project uses omegaconf structured configs extensively for all configuration
  dataclasses

## Expected behavior

- `OmegaConf.structured(SchedulingSpec())` should succeed without raising
- The field should still enforce that only valid placement strategy values are accepted
- The fix should follow existing patterns used by other enum-like fields in the same
  file (look at how other fields with a fixed set of valid choices handle validation)

## Hints

- Check how other fields in `cli_args.py` that have a fixed set of choices specify
  their type vs. how they validate their values
- The CLI documentation files may need to be updated to reflect the field being available
