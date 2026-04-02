# Bug: Configuration validation happens too late

## Summary

Several configuration dataclasses in `areal/api/cli_args.py` lack validation in their
`__post_init__` methods, which means invalid config values are only caught much later —
during training initialization or even at runtime — wasting resources and making
debugging harder.

## Affected Areas

### 1. `NormConfig` (areal/api/cli_args.py)

The `NormConfig` dataclass has fields `mean_level`, `std_level`, and `group_size`, but
no validation at construction time. Invalid values like `mean_level="invalid"` are only
caught when a `Normalization` object is created in `areal/utils/data.py`. This means
a bad config can survive through the entire setup phase before failing.

The validation currently lives in `Normalization.__init__` in `areal/utils/data.py`
(around line 1162) — it should be moved into `NormConfig.__post_init__` so errors are
detected at config construction time.

### 2. `PPOActorConfig` (areal/api/cli_args.py)

The `PPOActorConfig` class has SAPO-related fields (`use_sapo_loss`, `sapo_tau_pos`,
`sapo_tau_neg`) but the existing `__post_init__` does not validate them. Specifically:

- When `use_sapo_loss=True`, both temperature parameters must be positive
- SAPO mode is incompatible with `use_decoupled_loss=True`, but this is not enforced

### 3. `BaseExperimentConfig` (areal/api/cli_args.py)

The `total_train_epochs` field has no validation — a value of 0 or negative is silently
accepted, leading to confusing behavior downstream.

## Expected Behavior

All config validation should happen at dataclass construction time (in `__post_init__`),
raising `ValueError` with clear messages. The redundant validation in
`Normalization.__init__` should be removed after moving it to `NormConfig`.
