# Bug: `video_processing_utils` crashes on import when PIL is not installed

## Summary

The `src/transformers/video_processing_utils.py` module fails to import in environments where Pillow (PIL) is not installed. This breaks downstream tooling that needs to introspect the `processing_auto` module — for example, the `utils/update_metadata.py` CI job crashes with:

```
ImportError: cannot import name 'PILImageResampling' from 'transformers.image_utils'
```

The issue is that the module unconditionally imports a symbol that is only available when the `vision` optional dependency (Pillow) is present, even though that symbol is only needed at runtime when vision processing is actually performed.

## Reproduction

In a Python environment with `transformers` installed but **without** Pillow:

```python
from transformers.video_processing_utils import BaseVideoProcessor
# ImportError: cannot import name 'PILImageResampling' from 'transformers.image_utils'
```

## Relevant Files

- `src/transformers/video_processing_utils.py` — the top-level imports section where the unconditional PIL import occurs
- `src/transformers/image_utils.py` — defines the symbol that fails to import when PIL is absent
- `src/transformers/utils/import_utils.py` — utility functions for checking optional dependency availability

## Expected Behavior

The module should be importable regardless of whether Pillow is installed. Symbols that depend on PIL should only be imported when the dependency is actually available, consistent with how other optional dependencies (torch, torchvision) are already handled elsewhere in this file.

## Required Class Attributes

When imported without PIL present, the `BaseVideoProcessor` class must still have all of the following correct attributes:

- `rescale_factor` must equal `1/255`
- `model_input_names` must equal `['pixel_values_videos']`
- `default_to_square` must be `True`
- `return_metadata` must be `False`

## Required Methods

`BaseVideoProcessor` must have all of these methods: `preprocess`, `_preprocess`, `sample_frames`, `to_dict`, `from_dict`, `from_pretrained`, `save_pretrained`, `to_json_string`. The `__call__` method must delegate to `preprocess`.

## Required Constants

- `BASE_VIDEO_PROCESSOR_DOCSTRING` must be a string containing `do_resize`, `do_normalize`, and `resample`, with length greater than 500 characters.

## PIL Availability

When Pillow **is** installed, `PILImageResampling` must be accessible as an attribute of the `video_processing_utils` module (i.e., `from transformers import video_processing_utils; assert hasattr(video_processing_utils, 'PILImageResampling')`).

## File Content

The file must retain substantial content (more than 8000 characters), including the `class BaseVideoProcessor` definition, `def preprocess`, `def _preprocess`, `def sample_frames`, and `BASE_VIDEO_PROCESSOR_DOCSTRING`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
