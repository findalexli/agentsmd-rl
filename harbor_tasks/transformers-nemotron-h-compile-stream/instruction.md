# NemotronH segfaults under torch.compile

## Bug

When running `torch.compile` on a `NemotronHForCausalLM` model, certain tests crash with a segmentation fault:

```
Fatal Python error: Segmentation fault
```

The crash is intermittent (flaky) and occurs during `torch.compile` tracing.

## Root Cause Area

The `NemotronHBlock.forward` method in `src/transformers/models/nemotron_h/modeling_nemotron_h.py` (and its modular counterpart `modular_nemotron_h.py`) creates a temporary `torch.cuda.Stream` on every forward pass. During `torch.compile`, TorchDynamo stores a weakref to this stream object. Since the stream is a local variable with no other references, CUDA frees the underlying C++ object before Dynamo's cleanup runs, leaving a dangling pointer that causes a SIGSEGV.

## Relevant Files

- `src/transformers/models/nemotron_h/modeling_nemotron_h.py` — the generated modeling file; contains `NemotronHBlock` and `NemotronHMamba2Mixer`
- `src/transformers/models/nemotron_h/modular_nemotron_h.py` — the modular source file (edits here regenerate the modeling file)

## Hints

- Look at how `NemotronHMamba2Mixer.forward` already guards its CUDA fast path with `is_torchdynamo_compiling()` — the stream management should follow a similar pattern.
- The stream context is only needed for the CUDA kernel path, not for the general `NemotronHBlock.forward` flow.
- `contextlib.nullcontext()` is a code smell here — the stream should be managed closer to where it's actually needed.
- Both the modular and the generated modeling file need to be updated consistently.
