# Gemma3n and Gemma4 attention layers must not register the rotary kernel

The HuggingFace Transformers tree under `/workspace/transformers` (a clone at
a specific commit) contains a bug in two of its model implementations:
**`gemma3n`** and **`gemma4`**. The text-attention classes in both models
(`Gemma3nTextAttention` and `Gemma4TextAttention`) opt-in to a
function-kernel substitution mechanism that is incompatible with how their
`forward` actually applies rotary position embeddings.

## What is broken

The kernelization machinery in `transformers.integrations` exposes a class
decorator that, when applied to an `nn.Module`, wraps the class's
`__init__` so that every instance gets a `_hidden_kernels` dict populated
with the function(s) passed to the decorator. That dict is later read by
the `kernelize` framework to swap the listed function in for a fused-kernel
implementation that operates on **both `q` and `k` simultaneously**.

`Gemma3nTextAttention.forward` and `Gemma4TextAttention.forward` do **not**
follow that contract. Each layer calls `apply_rotary_pos_emb` separately
on the query and on the key (and some sub-paths apply it to the query
only, e.g. shared-KV layers in Gemma3n). Registering
`apply_rotary_pos_emb` for kernel substitution is therefore wrong for
these classes — it marks them as candidates for a kernel that does not
match their actual computation.

The observable symptom on the unfixed code is:

```python
attn = Gemma3nTextAttention(config, layer_idx=0)
attn._hidden_kernels  # -> {'apply_rotary_pos_emb': <function ...>}
```

After the fix, `attn._hidden_kernels` must not contain
`'apply_rotary_pos_emb'` (it should be empty / absent). The same property
must hold for `Gemma4TextAttention`.

Equivalently: `Gemma3nTextAttention.__init__.__qualname__` must not
contain `"use_kernelized_func"` (the decorator wraps `__init__` with a
function whose qualified name lives under
`use_kernelized_func.<locals>.decorator.<locals>.new_init`). Removing the
decorator restores the class's plain `__init__`.

## What to do

Locate the offending decorator on each of the two attention classes and
remove it. Each class is decorated in two places that must stay in sync:
once in the `modeling_*.py` file (the runtime module) and once in the
`modular_*.py` file (the source from which the modeling file is
generated). Both files must end up consistent — the repository ships a
modular-conversion check that verifies the modeling file matches what
would be regenerated from the modular file.

The decorator import (`from ...integrations import use_kernelized_func`)
becomes unused once the decorators are gone. Leave the file lint-clean.

You do not need to add any tests, change any other files, or refactor.
The fix is purely a removal.

## Verification commands you may find useful

```bash
cd /workspace/transformers

# Repository's own modular-conversion consistency check
python utils/check_modular_conversion.py

# Style check on the affected models
ruff check src/transformers/models/gemma3n/ src/transformers/models/gemma4/
```

## Code Style Requirements

The repository enforces `ruff` in CI. After your changes, `ruff check` on
the four affected files must pass — in particular, F401 (unused import)
will fire if the `use_kernelized_func` import is left behind after the
decorator is removed.

## Constraints

- Keep the diff minimal. Do not reformat unrelated code, add docstrings,
  or introduce new helpers — this is a removal-only bugfix.
- Edits to a `modeling_<name>.py` file must be reflected in its
  corresponding `modular_<name>.py` (and vice-versa). The standard
  workflow is to edit the modular file and run `make fix-repo` (or
  `python utils/checkers.py modular_conversion --fix`) to regenerate the
  modeling file; manual edits to both files are equivalent as long as the
  end result is consistent.
- Do not modify any other models, the kernel registration code itself, or
  the test suite.
