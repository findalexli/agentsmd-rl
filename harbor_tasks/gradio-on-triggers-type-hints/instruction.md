# Fix type hints for gr.on and gr.render triggers parameter

## Bug Description

The `triggers` parameter in `gr.on()` and `gr.render()` has incorrect type hints that cause false type-checking errors in mypy, pyright, and VS Code Pylance. The parameter is typed as `Sequence[EventListenerCallable] | EventListenerCallable | None`, but component event methods like `button.click` and `tab.select` are **bound methods** that do not expose the `block` first-parameter present in the `EventListenerCallable` type alias.

This means that valid, working code like this produces type errors:

```python
gr.on(triggers=[tab.select, state.change, button.click])  # type error
gr.on(triggers=button.click)  # type error
```

The `EventListenerCallable` type expects a callable with a specific signature that includes a `block` parameter as the first argument. But bound component event methods (e.g., `button.click`) have already consumed the `self`/`block` parameter through binding, so their signature does not match `EventListenerCallable`.

## What to Fix

1. In `gradio/events.py`, define a `Trigger` type alias that accepts both the full `EventListenerCallable` and bound component event methods (any callable that returns a `Dependency`). Update the `gr.on()` function signature to use `Trigger` instead of `EventListenerCallable` for the `triggers` parameter.

2. In `gradio/renderable.py`, update the import and the `gr.render()` function signature to use the new `Trigger` type instead of `EventListenerCallable`.

## Affected Code

- `gradio/events.py`: Add `Trigger` type alias, update `on()` signature
- `gradio/renderable.py`: Update import and `render()` signature

## Acceptance Criteria

- A `Trigger` type alias (or equivalent) is defined that accepts both `EventListenerCallable` and `Callable[..., Dependency]`
- `gr.on()` triggers parameter uses the new type
- `gr.render()` triggers parameter uses the new type
- Both files remain syntactically valid Python
- Runtime behavior is unchanged
