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

- `src/transformers/video_processing_utils.py` — the top-level imports section (around lines 28–34)
- `src/transformers/image_utils.py` — defines the symbol that fails to import when PIL is absent
- `src/transformers/utils/import_utils.py` — utility functions for checking optional dependency availability

## Expected Behavior

The module should be importable regardless of whether Pillow is installed. Symbols that depend on PIL should only be imported when the dependency is actually available, consistent with how other optional dependencies (torch, torchvision) are already handled elsewhere in this file.
