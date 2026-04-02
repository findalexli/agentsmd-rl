# Bug: `check_models_have_kwargs` flags nested helper classes as missing `**kwargs`

## Description

The repository consistency checker in `utils/check_repo.py` has a function `check_models_have_kwargs()` that verifies all model classes inheriting from `PreTrainedModel` accept `**kwargs` in their `forward()` method. However, it incorrectly flags **nested classes** — classes defined inside other classes or inside functions — that happen to inherit from `PreTrainedModel`.

These nested classes are internal helpers, not public model APIs, and should not be subject to the `**kwargs` requirement. The current implementation walks the entire AST tree of each modeling file, picking up class definitions at every nesting level. It should only inspect top-level class definitions.

## Affected files

- `utils/check_repo.py` — the `check_models_have_kwargs()` function (around line 1325)

## Additional performance concern

The `get_model_modules()` function in the same file is called multiple times during consistency checks but recomputes its result on every call by traversing all model modules. This is wasteful and should be cached.

## Expected behavior

1. `check_models_have_kwargs()` should only check **top-level** class definitions in modeling files, ignoring classes nested inside other classes or functions.
2. `get_model_modules()` should cache its result so repeated calls don't re-traverse the module tree.

## Reproduction

Create a modeling file with a nested class inheriting from `PreTrainedModel` whose `forward()` method lacks `**kwargs`. Running `python utils/check_repo.py` will incorrectly report this nested class as failing the check.
