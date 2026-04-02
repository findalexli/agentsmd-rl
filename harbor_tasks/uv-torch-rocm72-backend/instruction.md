# Missing ROCm 7.2 Backend Support in uv-torch

## Problem

The `uv-torch` crate handles PyTorch backend selection for various CUDA and ROCm versions. AMD recently released ROCm 7.2, which introduces support for several new GPU architectures (including RDNA 4 GPUs). However, `uv` currently has no way for users to select `rocm7.2` as a torch backend.

This means users with AMD GPUs that require ROCm 7.2 cannot use `uv` to install PyTorch targeting this platform. Attempting to specify `rocm7.2` as a torch mode or backend value will fail with an unknown variant error.

## Relevant Files

- `crates/uv-torch/src/backend.rs` — defines `TorchMode`, `TorchBackend`, index URLs, and the `FromStr` implementations. Look at how existing ROCm versions (e.g., ROCm 7.1, 7.0) are defined for the pattern to follow.
- `crates/uv-torch/src/accelerator.rs` — defines `AmdGpuArchitecture` enum and its `FromStr`/`Display` impls. ROCm 7.2 introduces two new GPU architectures that need to be added here.
- `uv.schema.json` — the JSON schema for `uv` configuration, which lists valid torch mode values.

## What Needs to Happen

1. Add the new ROCm 7.2 torch mode and backend, following the pattern of existing ROCm versions.
2. Add the new AMD GPU architectures introduced by ROCm 7.2 to the architecture enum.
3. Add the ROCm 7.2 GPU driver mappings (which architectures are supported by this backend). You can determine the supported architecture list from AMD's ROCm 7.2 documentation or by examining `torch.cuda.get_arch_list()` from a ROCm 7.2 PyTorch build.
4. Define the PyTorch and Pyx index URLs for the new backend.
5. Update the JSON schema to accept the new backend value.

## Hints

- Study how `Rocm71` is implemented end-to-end across all three files. The new version follows the exact same pattern.
- The ROCm version accessor should return `Some(Version::new([7, 2]))` and the CUDA version accessor should return `None` (since this is an AMD backend, not NVIDIA).
- ROCm 7.2 supports these GPU architectures: gfx900, gfx906, gfx908, gfx90a, gfx942, gfx950, gfx1030, gfx1100, gfx1101, gfx1102, gfx1150, gfx1151, gfx1200, gfx1201. Note that gfx1150 and gfx1151 are new architectures not present in earlier ROCm versions.
