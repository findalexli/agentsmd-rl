# Rename IPO masking to DPPO+KL in default loss function

## Problem

The default loss function in `src/prime_rl/trainer/rl/loss.py` currently uses field names `ipo_mask_low` and `ipo_mask_high` in both the config (`src/prime_rl/configs/trainer.py`) and the implementation. Additionally, the masking logic is unconditional (doesn't consider the sign of advantages).

The loss function also has an outdated docstring that describes an "IPO (INTELLECT Policy Optimization)" loss which doesn't match the current DPPO+KL implementation.

## Expected Behavior

1. **Config fields renamed**: The `DefaultLossConfig` should use `dppo_mask_low` and `dppo_mask_high` instead of `ipo_mask_low` and `ipo_mask_high`.

2. **Masking logic updated**: The loss function should use advantage-conditioned masking:
   - For positive advantages: mask tokens where probability increased too much (upweight trust region violation)
   - For negative advantages: mask tokens where probability decreased too much (downweight trust region violation)

3. **Docstring updated**: The docstring should describe "DPPO+KL loss" and explain the advantage-based masking logic.

4. **Documentation updated**: The `.cursor/BUGBOT.md` file contains guidelines about when to update `CHANGELOG.md`. Since this PR renames config fields (a breaking change), update the BUGBOT documentation to:
   - Clarify that only **breaking** config changes (renamed/removed/moved fields) require changelog updates
   - List the specific breaking change categories: Renamed, Removed, Moved
   - Clarify that additive changes don't require changelog entries
   - Update the config file path reference to `src/prime_rl/configs/`

## Files to Look At

- `src/prime_rl/trainer/rl/loss.py` — Contains the `default_loss_fn` with masking logic and docstring
- `src/prime_rl/configs/trainer.py` — Contains the `DefaultLossConfig` class with field definitions
- `.cursor/BUGBOT.md` — Documentation about when changelog updates are required
