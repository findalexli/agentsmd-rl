Importing Fast Image Processors via their full module path raises `ModuleNotFoundError`. For example:

```python
from transformers.models.llama4.image_processing_llama4_fast import Llama4ImageProcessorFast
```

This fails because the module `image_processing_llama4_fast` does not exist as a real file -- the fast image processors were consolidated, but backward-compatible module aliases were never created for the per-model `image_processing_*_fast` paths.

The library already has a pattern for creating module aliases (used for `tokenization_utils_fast`, `tokenization_utils`, and `image_processing_utils_fast`). The same approach needs to be extended to dynamically create aliases for all per-model `image_processing_*_fast` module paths, mapping them back to the corresponding `image_processing_*` module. Additionally, class-level `__getattr__` should handle the case where someone imports `XImageProcessorFast` from the aliased module and redirect to `XImageProcessor`.

The `utils/check_repo.py` file also needs updating so that these alias modules are excluded from documentation completeness checks.

## Files to Modify

- `src/transformers/__init__.py`
- `utils/check_repo.py`
