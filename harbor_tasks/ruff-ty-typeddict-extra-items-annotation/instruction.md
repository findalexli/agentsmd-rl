# [ty] Infer `extra_items` keyword in class-based TypedDicts as an annotation expression

## Problem

The `ty` type checker does not properly validate the `extra_items` keyword argument in class-based TypedDict definitions. Currently, `extra_items` is inferred as a regular expression rather than as a type annotation, which means:

1. **Invalid type qualifiers are silently accepted.** For example, `class TD(TypedDict, extra_items=Required[int])` does not produce any error, even though `Required` and `NotRequired` are not valid qualifiers for `extra_items` (only `ReadOnly` is). The same applies to `ClassVar`, `Final`, and `InitVar`.

2. **Forward references in `extra_items` are not handled correctly.** Stringified forward references like `extra_items="Foo | None"` are not resolved as type annotations, and self-referential forward references in stub files do not work.

## Expected Behavior

- `extra_items` should be treated as an annotation expression (not a regular expression) when the class is a real `typing.TypedDict`.
- Invalid qualifiers (`Required`, `NotRequired`, `ClassVar`, `Final`, `InitVar`) in `extra_items` should produce an `invalid-type-form` diagnostic.
- `ReadOnly` should remain valid in `extra_items`.
- Forward references (stringified in `.py`, bare in `.pyi`) should be properly resolved.
- For non-`typing.TypedDict` classes that happen to accept an `extra_items` keyword, the value should continue to be treated as a regular expression, not a type annotation.

## Files to Look At

- `crates/ty_python_semantic/src/types/infer/builder/class.rs` — handles class definition inference, including keyword argument processing
- `crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs` — contains TypedDict-specific inference logic including `infer_extra_items_kwarg`
- `crates/ty_python_semantic/resources/mdtest/typed_dict.md` — mdtest cases for TypedDict behavior (update existing `extra_items` section)
