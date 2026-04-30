# Bug: Configuration validation happens too late

## Summary

Several configuration dataclasses in the AReaL codebase lack validation at
construction time, meaning invalid config values are only caught much later —
during training initialization or at runtime — wasting resources and making
debugging harder. The affected files are `areal/api/cli_args.py` and
`areal/utils/data.py`.

## Style Requirements

All Python files must pass formatting and linting checks using **ruff version
0.14.9**. Run `ruff format` and `ruff check` on `areal/api/cli_args.py` and
`areal/utils/data.py` before submitting.

## Affected Areas

### 1. `NormConfig` (areal/api/cli_args.py)

The `NormConfig` dataclass has fields `mean_level`, `std_level`, and `group_size`, but
no validation at construction time. Invalid values like `mean_level="invalid"` are only
caught when a `Normalization` object is created later, meaning a bad config can survive
through the entire setup phase before failing.

**Valid values:**
- `mean_level`: `"batch"`, `"group"`, or `None` (default is `"batch"`)
- `std_level`: `"batch"`, `"group"`, or `None` (default is `"batch"`)
- `group_size`: default is `1`; must be a positive integer when using group
  normalization (i.e., when `mean_level="group"` or `std_level="group"`)

**Invalid values that should be rejected with `ValueError` or `TypeError`:**
- `mean_level`: `"invalid"`, `"per_sample"`, or any integer like `42`
- `std_level`: `"invalid"`, `"per_sample"`, or any integer like `99`
- `group_size`: `0`, `-1`, or any non-positive value when using group normalization

**Eliminate duplicate validation:** The `Normalization` class in `areal/utils/data.py`
independently validates `mean_level` and `std_level` in its `__init__` method. This
creates duplicate validation — both `NormConfig.__post_init__` (once added) and
`Normalization.__init__` would check these values against the same allowed set.
Remove the `mean_level` and `std_level` validation from `Normalization.__init__`
entirely; it should exist only in `NormConfig.__post_init__`.

### 2. `PPOActorConfig` (areal/api/cli_args.py)

The `PPOActorConfig` class has SAPO-related fields (`use_sapo_loss`, `sapo_tau_pos`,
`sapo_tau_neg`), behavioral importance weight fields (`behave_imp_weight_mode`,
`behave_imp_weight_cap`), and a `use_decoupled_loss` field. The existing
validation already covers some of these but does not validate the SAPO fields:

- When `use_sapo_loss=True`, both `sapo_tau_pos` and `sapo_tau_neg` must be positive
  (values of `0.0` or negative should be rejected with `ValueError`)
- SAPO mode (`use_sapo_loss=True`) is incompatible with `use_decoupled_loss=True`, but
  this constraint is not enforced

The `behave_imp_weight_mode` field defaults to `"disabled"` and
`behave_imp_weight_cap` defaults to `None`. The existing validation for these fields
must be preserved — when `use_sapo_loss=True` and these are at their defaults
(`"disabled"` and `None`), the SAPO validation should still function correctly.

Note: the `PPOActorConfig` validation should continue to call its parent's
validation method.

### 3. `BaseExperimentConfig` (areal/api/cli_args.py)

The `total_train_epochs` field has no validation — a value of `0` or negative is
silently accepted, leading to confusing behavior downstream. Values of `0`, `-1`, or
`-100` should be rejected with `ValueError`.

## Expected Behavior

All config validation should happen at dataclass construction time,
raising `ValueError` with clear messages. Each new validation method should include a
docstring describing its purpose. The duplicate validation of `mean_level` and
`std_level` should be eliminated — it should exist in only one place. Valid
configurations should continue to construct without error.
