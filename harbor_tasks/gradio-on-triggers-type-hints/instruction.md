# Type hints for gr.on and gr.render triggers parameter cause false type-checking errors

## Bug Description

The `triggers` parameter in `gr.on()` (in `gradio/events.py`) and `gr.render()` (in `gradio/renderable.py`) produces false type-checking errors in mypy, pyright, and VS Code Pylance when passed bound component event methods like `button.click`, `tab.select`, or `state.change`.

The current type annotation for `triggers` uses `EventListenerCallable`, which expects a callable with a `block` first-parameter. However, bound component event methods have already consumed the `self`/`block` parameter through binding, so their signature does not match `EventListenerCallable`.

This means valid, working code like this produces type errors:

```python
gr.on(triggers=[tab.select, state.change, button.click])  # type error
gr.on(triggers=button.click)  # type error
gr.render(triggers=[input.change, button.click])  # type error
```

## Required Fix

The `triggers` parameter type should accept:
1. The existing `EventListenerCallable` type (for backward compatibility)
2. Any bound component event method (any callable that returns a `Dependency`)

The new type should be named `Trigger` (a type alias defined in `gradio/events.py` that includes both `EventListenerCallable` and `Callable[..., Dependency]`).

## Affected Files

- `gradio/events.py`: The `gr.on()` function and the location where `Trigger` should be defined
- `gradio/renderable.py`: The `gr.render()` function and its imports from `gradio.events`

## Acceptance Criteria

- A `Trigger` type alias is defined in `gradio/events.py` that includes both `EventListenerCallable` and `Callable[..., Dependency]`
- `gr.on()` in `gradio/events.py` has its `triggers` parameter annotated with a type that references `Trigger` (not `EventListenerCallable` directly)
- `gr.render()` in `gradio/renderable.py` has its `triggers` parameter annotated with a type that references `Trigger` (not `EventListenerCallable` directly)
- `gradio/renderable.py` imports `Trigger` from `gradio.events` (not `EventListenerCallable`)
- Both files remain syntactically valid Python
- `EventListenerCallable` remains importable from `gradio.events` (backward compatibility)
- Runtime behavior is unchanged (this is a type annotation fix only)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
