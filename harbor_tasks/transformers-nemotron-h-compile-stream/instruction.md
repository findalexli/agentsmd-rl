# Fix NemotronH torch.compile Segfault

## Symptom

When running `torch.compile` on a `NemotronHForCausalLM` model, certain tests crash with a segmentation fault:

```
Fatal Python error: Segmentation fault
```

The crash is intermittent (flaky) and occurs during `torch.compile` tracing.

## What the Fix Must Achieve

The solution must satisfy all of the following structural requirements:

1. **Both files must define a module-level sentinel** `is_fast_path_available = False`

2. **`contextlib` must be fully removed** — neither file should import it

3. **`NemotronHBlock.forward` must not use `torch.cuda.stream` or `nullcontext`**

4. **`NemotronHMamba2Mixer` in both files must have CUDA stream management guarded by a compile check** in its `forward` or `cuda_kernels_forward` method

5. **The modular source file** (`modular_nemotron_h.py`) **must also have a `forward` override for `NemotronHMamba2Mixer`** with stream management and compile guard

## Relevant Files

- `modeling_nemotron_h.py` — the generated modeling file in the NemotronH model directory; contains `NemotronHBlock` and `NemotronHMamba2Mixer`
- `modular_nemotron_h.py` — the modular source file in the same directory (edits here regenerate the modeling file)

## Approach Hints

- Look at how `NemotronHMamba2Mixer.forward` already guards its CUDA fast path with a compile check — the stream management should follow a similar pattern
- The stream context is only needed for the CUDA kernel path, not for the general block forward flow
- Removing contextlib means the stream management logic that used `nullcontext` must be reimplemented differently
- Both the modular and the generated modeling file need to be updated consistently

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
