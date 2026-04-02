# ty emits false-positive TypedDict diagnostics for `TypedDict | dict` unions

## Bug

When a dict literal is assigned to (or passed as) a type annotated as a union of a `TypedDict` and a plain `dict` (e.g. `FormatterConfig | dict[str, Any]`), `ty` incorrectly emits `missing-typed-dict-key` and `invalid-key` diagnostics. It validates the dict literal eagerly against the `TypedDict` arm of the union, even though the non-`TypedDict` arm (`dict[str, Any]`) would accept the literal just fine.

## Reproduction

```python
from typing import TypedDict, Any

class FormatterConfig(TypedDict, total=False):
    format: str

def takes_formatter(config: FormatterConfig | dict[str, Any]) -> None: ...

# ty incorrectly flags these:
takes_formatter({"format": "%(message)s"})       # OK — matches FormatterConfig
takes_formatter({"factory": object(), "facility": "local0"})  # should be OK — matches dict[str, Any]
```

Running `ty check` on this file produces spurious `missing-typed-dict-key` / `invalid-key` errors for the second call, even though `dict[str, Any]` accepts any string-keyed dict.

## Expected behavior

When a union contains both a `TypedDict` and a non-`TypedDict` dict type (like `dict[str, Any]`), `ty` should suppress eager `TypedDict` diagnostics for dict literals that don't match the `TypedDict` arm, since the dict arm can still accept them.

Importantly, unions like `TypedDict | None` (where there is **no** dict-compatible fallback) should continue to validate eagerly against the `TypedDict` arm and emit diagnostics as before.

## Relevant code

The dict-literal inference logic lives in `crates/ty_python_semantic/src/types/infer/builder.rs`, in the section that handles `TypedDict` dictionary literal assignments. The code currently filters the union to only `TypedDict` elements and validates against all of them, without considering whether a non-`TypedDict` dict arm exists that could accept the literal.
