Importing Fast Image Processors via their full module path raises `ModuleNotFoundError`. For example:

```python
from transformers.models.llama4.image_processing_llama4_fast import Llama4ImageProcessorFast
```

This fails because the module `image_processing_llama4_fast` does not exist as a real file — the fast image processors were consolidated into a single backend module, but backward-compatible module aliases were never created for the per-model `image_processing_*_fast` paths.

## What needs to work

1. **Module alias resolution**: For each model that has an `image_processing_<model>.py` file, importing `transformers.models.<model>.image_processing_<model>_fast` must succeed without `ModuleNotFoundError`. This must work for at least these models: `llama4`, `clip`, `vit`, `blip`, `detr`. The solution should dynamically discover eligible models by scanning for `image_processing_*.py` files (excluding any already ending in `_fast`), rather than hardcoding a list. At least 3 dynamically discovered models must resolve successfully.

2. **Class-level redirect**: When `XImageProcessorFast` is accessed from a `_fast` module alias, it must resolve to the exact same class object (identity via `is`) as `XImageProcessor` from the real module. For example, `Llama4ImageProcessorFast` from the alias must be the same object as `Llama4ImageProcessor`. The class name follows CamelCase derived from the model directory name (e.g., `clip` → `Clip`, `llama4` → `Llama4`). At least 1 such redirect must be verifiable.

3. **Existing aliases and exports preserved**: The pre-existing `transformers.image_processing_utils_fast` and `transformers.tokenization_utils` module aliases must continue to work. `transformers.__version__` must remain accessible, and `AutoImageProcessor` must remain in `dir(transformers)`.

4. **Undocumented-name checker compatibility**: The repository has a utility function that determines which names to ignore when checking for undocumented public objects. It must return `True` for names matching the pattern `image_processing_<model>_fast` (e.g., `image_processing_llama4_fast`, `image_processing_clip_fast`, `image_processing_vit_fast`, `image_processing_blip_fast`, `image_processing_detr_fast`). It must NOT return `True` for non-fast image processing names like `image_processing_clip`, nor for unrelated names like `SomeRandomClass`.

5. **`# Copied from` blocks**: Changes must not add, remove, or modify any lines containing `# Copied from` in any modified file — these are managed by `make fix-repo`.

6. **No modular-generated file edits**: Do not modify any `modeling_*.py` files that have a corresponding `modular_*.py` in the same directory — these are auto-generated from the modular source.

7. **Repository consistency checks**: All standard repository checks must continue to pass, including linting and formatting (ruff), init file consistency, dummy objects, copies, modeling structure, documentation TOC, init isort ordering, auto mappings sorting, and doctest list checks.
