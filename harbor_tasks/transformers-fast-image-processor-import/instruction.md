Importing Fast Image Processors via their full module path raises `ModuleNotFoundError`. For example:

```python
from transformers.models.llama4.image_processing_llama4_fast import Llama4ImageProcessorFast
```

This fails because the module `image_processing_llama4_fast` does not exist as a real file -- the fast image processors were consolidated into a single `image_processing_backends` module, but backward-compatible module aliases were never created for the per-model `image_processing_*_fast` paths.

## What needs to work

1. **Module alias resolution**: For each model that has `image_processing_<model>.py`, importing `transformers.models.<model>.image_processing_<model>_fast` must succeed without `ModuleNotFoundError`. This applies to models including but not limited to: `llama4`, `clip`, `vit`, `blip`, `detr`.

2. **Class-level redirect**: When `XImageProcessorFast` is imported from a `_fast` module alias, it must resolve to the same class object as `XImageProcessor` from the real module.

3. **Existing aliases preserved**: The pre-existing `transformers.image_processing_utils_fast` and `transformers.tokenization_utils` aliases must continue to work.

4. **`ignore_undocumented` function**: In `utils/check_repo.py`, the `ignore_undocumented` function must return `True` for names matching `image_processing_*_fast` pattern. Non-fast image processing names must NOT be ignored.

5. **`# Copied from` blocks**: Changes to `__init__.py` must not modify or remove any `# Copied from` blocks.

## Relevant patterns

The codebase already has a module aliasing mechanism: `_create_module_alias`. It is used for `tokenization_utils_fast`, `tokenization_utils`, and `image_processing_utils_fast`. Any solution should integrate with this existing pattern rather than bypassing it.

The `__init__.py` file is large (500+ lines) and contains `# Copied from` blocks that must not be touched. Modifications should be surgically targeted to the relevant section.

Files to examine (do not list as "modify" -- the correct files will be determined from code exploration):
- `src/transformers/__init__.py` -- contains the module aliasing pattern
- `utils/check_repo.py` -- contains the `ignore_undocumented` function
