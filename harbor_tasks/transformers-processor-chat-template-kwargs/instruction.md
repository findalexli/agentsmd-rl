# Bug: Processor `apply_chat_template` drops custom Jinja2 template variables

## Summary

The `ProcessorMixin.apply_chat_template()` method in `src/transformers/processing_utils.py` cannot handle arbitrary user-defined template variables in Jinja2 chat templates. When users define custom variables in their chat template (e.g. `{{ num_frames }}`, `{{ custom_flag }}`), the method fails to correctly distinguish template-level kwargs from processor kwargs.

## Expected Behavior

The method should correctly route:
- Custom Jinja2 template variables (e.g. `num_frames`, `fps`, `custom_var`, `custom_flag`) to the Jinja2 template renderer
- Processor-specific kwargs (e.g. `padding`, `max_length`, `return_tensors`, `truncation`) to the processor's `__call__` method

## Requirements

### 1. New extraction function in `chat_template_utils`

Add a function (discoverable by the tests) that:
- Takes a chat template string as input
- Returns a `set` or `frozenset` of the template's variable names
- Uses caching (via `lru_cache`) for performance — subsequent calls with the same template return cached results
- Correctly identifies Jinja2 variables like `{{ messages }}`, `{{ bos_token }}`, `{% if custom_var %}`
- Excludes loop variables (e.g., the `msg` in `{% for msg in messages %}`)
- Works with nested conditionals like `{% if a %}{% if b %}{{ c }}{% endif %}{% endif %}`
- Handles empty/literal templates (returns empty set)

### 2. Kwarg separation in `apply_chat_template`

The `apply_chat_template` method must:
- Dynamically determine which kwargs are template variables using the extraction function
- Ensure processor kwargs (`padding`, `max_length`, `return_tensors`, `truncation`) are NOT treated as template variables
- Support a `processor_kwargs` dict parameter for clearer separation

### 3. Files to modify (syntax must remain valid)

- `src/transformers/processing_utils.py`
- `src/transformers/utils/chat_template_utils.py`
- `src/transformers/models/smolvlm/processing_smolvlm.py`
- `src/transformers/models/voxtral/processing_voxtral.py`

All modified files must pass Python syntax checks and ruff linting.

### 4. Backward compatibility

- `render_jinja_template`, `get_json_schema`, `_compile_jinja_template` must continue to work
- Existing unit tests in `tests/utils/test_chat_template_utils.py` must pass

## Symptom (not fix description)

When a chat template contains custom variables and those variables are passed via `**kwargs`, they may be incorrectly routed. For example, `{{ num_frames }}` in a template should receive the value passed for `num_frames`, but currently the routing logic doesn't distinguish template variables from processor kwargs.