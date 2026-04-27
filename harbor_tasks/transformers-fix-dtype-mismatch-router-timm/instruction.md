# Fix dtype mismatch in SwitchTransformers router and TimmWrapperModel

The `huggingface/transformers` source tree is checked out at
`/workspace/transformers`. Two reduced-precision use cases currently raise
`RuntimeError` instead of producing valid output. Make them work.

## Bug 1 — `SwitchTransformersTop1Router`

Reproduce:

```python
import torch
from transformers.models.switch_transformers.configuration_switch_transformers \
    import SwitchTransformersConfig
from transformers.models.switch_transformers.modeling_switch_transformers \
    import SwitchTransformersTop1Router

config = SwitchTransformersConfig(
    num_experts=4, expert_capacity=4, d_model=8,
    router_bias=False, router_jitter_noise=0.0,
    router_ignore_padding_tokens=False, router_dtype="float32",
)
router = SwitchTransformersTop1Router(config).to(torch.bfloat16).eval()
hidden = torch.randn(2, 4, 8, dtype=torch.float32)
router(hidden)        # raises RuntimeError: expected m1 and m2 to have the same dtype
```

What is happening: `SwitchTransformersTop1Router.__init__` stores
`self.dtype = getattr(torch, config.router_dtype)` (typically
`torch.float32`). When the user calls `router.to(torch.bfloat16)` the
underlying `nn.Linear` classifier weights are converted, but the
`self.dtype` attribute is not — it still says `float32`. Inside
`forward`, `hidden_states` is cast to `self.dtype` (float32) and then
passed through the bfloat16 classifier, producing a dtype mismatch.

Expected behavior: `router(hidden)` must run to completion for any input
dtype regardless of how the module was cast (`bfloat16`, `float16`,
default). Output `router_probs` must be cast back to the input's dtype
(the existing "selective precision" contract — see the comment in
`forward`).

## Bug 2 — `TimmWrapperModel`

Reproduce:

```python
import torch
from transformers import TimmWrapperConfig, TimmWrapperModel

config = TimmWrapperConfig(architecture="resnet18", model_args={})
model = TimmWrapperModel(config=config).to(torch.bfloat16).eval()
pixel_values = torch.randn(1, 3, 64, 64, dtype=torch.float32)
model(pixel_values)   # raises RuntimeError: Input type ... and weight type ... should be the same
```

What is happening: in `TimmWrapperModel.forward`, the line that prepares
`pixel_values` only moves the tensor to the model's device, leaving its
dtype untouched. When the wrapper has been cast to a non-default dtype,
the underlying `timm` model receives mismatched inputs.

Expected behavior: `pixel_values` must arrive at the inner `timm` model
in the model's parameter dtype, not just on the right device. After the
fix, `model(pixel_values).last_hidden_state.dtype` must equal
`model.dtype` (e.g. `torch.bfloat16`) and contain no NaNs.

## Repository conventions you must follow

The `switch_transformers` directory contains both
`modular_switch_transformers.py` and the generated
`modeling_switch_transformers.py`. Per the project's `CLAUDE.md` and
`AGENTS.md`:

- The modular file is the source of truth.
- The modeling file is **generated** — its first lines say "Do NOT edit
  this file manually" — but our build/CI guarantees both stay in sync.
- Any code change must therefore be reflected in **both** files (either
  by editing modular and regenerating, or by editing both directly).
  Tests will fail if `SwitchTransformersTop1Router.forward` diverges
  between the two files.

## Code Style Requirements

`CLAUDE.md` mandates `make style` (which runs `ruff format` and
`ruff check`) before opening a PR. Tests run `python -m ruff format
--check` against the three files you modify; your edits must remain
ruff-format-clean.

## Files in scope

You should only need to modify code in:
- `src/transformers/models/switch_transformers/` (modular and modeling)
- `src/transformers/models/timm_wrapper/modeling_timm_wrapper.py`

No new files, no public API changes. Keep the diff minimal — the project
explicitly asks bugfix PRs to be one or two lines per file.
