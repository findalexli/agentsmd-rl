# NemotronH Mamba layer dimension mismatch for non-120B model sizes

## Problem

The `NemotronHConfig` in `src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py` sets up Zamba2-compatible alias attributes that are read by the parent `Zamba2MambaMixer.__init__` when constructing `NemotronHMamba2Mixer`. One of these aliases controls the expansion factor used to compute `intermediate_size` inside the Zamba2 parent: `int(mamba_expand * hidden_size)`.

For the 120B model, the default parameters happen to produce correct dimensions. However, for other model sizes (e.g., Nemotron-3-Nano-30B with `mamba_num_heads=64`, `mamba_head_dim=64`, `hidden_size=2688`), the Zamba2-computed `intermediate_size` does not match `mamba_num_heads * mamba_head_dim`, resulting in wrong conv1d and projection dimensions. This causes checkpoint loading to fail with shape mismatches.

The root cause is that the Zamba2 compat alias for the expansion factor is set using the raw config parameter, which doesn't account for the relationship between head count, head dimension, and hidden size across different model variants.

## Affected files

- `src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py` -- the Zamba2 compat alias section in `__init__`
- `src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py` -- the `NemotronHMambaLayer` construction

## Expected behavior

For any model size, `int(mamba_expand * hidden_size)` should equal `mamba_num_heads * mamba_head_dim`, so that the Zamba2 parent mixer builds conv/projection dimensions that match the actual checkpoint weights.

## Reproduction

Construct a `NemotronHConfig` with Nemotron-3-Nano-30B parameters (`hidden_size=2688`, `mamba_num_heads=64`, `mamba_head_dim=64`, `mamba_expand=2`) and check the Zamba2 compat `mamba_expand` attribute. The computed `int(mamba_expand * hidden_size)` will be `5376` instead of the expected `4096` (`64 * 64`).
