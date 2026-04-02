# ASYNC115 autofix generates broken import for `anyio.sleep(0)`

## Bug

The ASYNC115 rule detects `anyio.sleep(0)` and `trio.sleep(0)` calls and suggests replacing them with `lowlevel.checkpoint()`. The autofix generates an import statement to bring `lowlevel` into scope, but for `anyio` it generates `from anyio import lowlevel`. This is incorrect because `anyio.lowlevel` is a submodule, not a re-exported member — using `from anyio import lowlevel` produces code that fails at runtime with an `AttributeError`.

By contrast, `trio.lowlevel` is re-exported as a member, so `from trio import lowlevel` works fine there. The autofix needs to be module-aware: it should use `import anyio.lowlevel` (a submodule import) for anyio, rather than the `from ... import` form.

## Reproduction

Create a Python file:

```python
from anyio import sleep as anyio_sleep

async def func():
    await anyio_sleep(0)
```

Run `ruff check --select ASYNC115 --fix` on it. The autofix produces `from anyio import lowlevel`, which would fail at runtime. It should produce `import anyio.lowlevel` instead.

## Relevant files

- `crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs` — contains the ASYNC115 rule implementation and autofix logic
- `crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py` — test fixtures for the rule
