# Bug: CUDA wheel filenames have `+cu*` suffix but internal metadata does not

## Context

SGLang's `sgl-kernel` package uses a post-build script (`sgl-kernel/rename_wheels.sh`) to rename CUDA wheel files with a `+cu124`, `+cu128`, or `+cu130` local version suffix based on the detected CUDA toolkit version. This suffix appears in the `.whl` filename so that pip can distinguish CUDA-specific builds.

## Problem

The current script only renames the **filename** of the `.whl` archive. It does not update the **internal metadata** inside the wheel zip:

1. The `METADATA` file's `Version:` field still shows the base version (e.g., `0.4.5`) without the `+cu*` suffix.
2. The `.dist-info` directory name inside the wheel still uses the base version.
3. The `WHEEL` file's platform tags may still say `linux_x86_64` instead of `manylinux2014_x86_64` after the filename rename.

This causes pip to report an **inconsistent version** error — the filename says one version (with `+cu124`) but the metadata says another (without it). Depending on pip version, this can cause install failures or silent confusion.

## Relevant Files

- `sgl-kernel/rename_wheels.sh` — the post-build wheel renaming script

## Additional Notes

- The `linux` → `manylinux2014` platform tag substitution in the current script uses a naive global string replacement (`${wheel/linux/manylinux2014}`) which can corrupt tags on repeated runs since `linux` is a substring of `manylinux2014`.
- The fix should ensure that internal wheel metadata (METADATA Version, .dist-info directory name, WHEEL platform tags) all match the filename after renaming.
- The `RECORD` file inside the wheel must also be regenerated to reflect any internal changes.
