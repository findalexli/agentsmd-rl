# Bug: `get_size_dict` crashes when receiving a `SizeDict` input

## Context

In the `transformers` image processing pipeline, `SizeDict` is a typed dictionary class used to represent image sizes (e.g., `{"height": 224, "width": 224}`). During initialization of image processors, the `size` parameter is converted to a `SizeDict` instance via `_standardize_kwargs`.

Some remote code models (custom model code loaded from the Hub) call `get_size_dict()` directly, bypassing the standard initialization path. When these models pass a `SizeDict` instance as the `size` argument, the function breaks because it doesn't recognize `SizeDict` as a dict-like type.

## Where to look

- `src/transformers/image_processing_utils.py` — the `get_size_dict()` function
- `src/transformers/image_utils.py` — the `SizeDict` class definition

## How to reproduce

```python
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(height=224, width=224)
result = get_size_dict(sd)  # This should return {"height": 224, "width": 224}
```

Instead of returning the dict, the function attempts to convert the `SizeDict` through `convert_to_size_dict`, which doesn't know how to handle it, resulting in incorrect behavior or an error.

## Expected behavior

`get_size_dict()` should accept `SizeDict` inputs and correctly convert them to a plain dictionary for downstream use.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
