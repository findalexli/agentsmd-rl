# Bug: Processor `apply_chat_template` drops custom Jinja2 template variables

## Summary

The `ProcessorMixin.apply_chat_template()` method in `src/transformers/processing_utils.py` cannot handle arbitrary user-defined template variables in Jinja2 chat templates. When users define custom variables in their chat template (e.g. `{{ num_frames }}`, `{{ custom_flag }}`), the method fails to correctly distinguish template-level kwargs from processor kwargs because it relies on a hardcoded `AllKwargsForChatTemplate` TypedDict to classify arguments.

## Reproduction

When calling `apply_chat_template` with kwargs that correspond to custom Jinja2 template variables (not listed in the `AllKwargsForChatTemplate` TypedDict), those kwargs are incorrectly routed as processor kwargs rather than being passed to the Jinja2 template renderer. This causes:

1. Custom template variables to be undefined when the template renders
2. Processor kwargs to be polluted with template-level arguments, causing downstream errors

The root issue is in the kwargs-filtering logic:

```python
# Current (broken) approach in processing_utils.py:
template_kwargs = {}
for key in AllKwargsForChatTemplate.__annotations__["template_kwargs"].__annotations__:
    ...
    value = kwargs.pop(key, default_value)
    ...
template_kwargs.update(kwargs)  # remaining kwargs get lumped in
```

This approach uses a static list of known template kwargs. Any variable not in that list gets misclassified.

## Affected files

- `src/transformers/processing_utils.py` — `ProcessorMixin.apply_chat_template()` method
- `src/transformers/utils/chat_template_utils.py` — missing utility to introspect template variables
- `src/transformers/models/smolvlm/processing_smolvlm.py` — SmolVLM processor's `apply_chat_template` override
- `src/transformers/models/voxtral/processing_voxtral.py` — Voxtral processor's `apply_chat_template` override

## Expected behavior

The method should dynamically determine which kwargs are template variables by introspecting the actual Jinja2 chat template, rather than relying on a hardcoded list. Custom template variables should be correctly passed through to the Jinja2 renderer, while processor-specific kwargs (like `padding`, `max_length`, `return_tensors`) should be separated and passed to the processor's `__call__` method.

Additionally, the method signatures should use explicit parameters instead of the opaque `**kwargs: Unpack[AllKwargsForChatTemplate]` pattern, and support a dedicated `processor_kwargs` dict parameter for cleaner separation.
