# ty: dataclass_transform ignores keyword params passed via `**kwargs`

## Bug Description

When a dataclass transformer (function, metaclass, or base class decorated with `@dataclass_transform()`) accepts its configuration parameters through `**kwargs` rather than listing them explicitly in its signature, ty fails to recognize those parameters.

For example, if a transformer function is defined as:

```python
@dataclass_transform()
def create_model[T: type](**kwargs) -> Callable[[T], T]:
    raise NotImplementedError
```

And then used with:

```python
@create_model(frozen=True)
class Frozen:
    name: str
```

ty does not respect the `frozen=True` argument. It should report an `invalid-assignment` error when mutating a field on an instance of `Frozen`, but it currently allows it silently.

The same issue occurs for metaclass-based and base-class-based transformers that use `**kwargs` in their `__new__` or `__init_subclass__` methods.

## Relevant Code

The dataclass transform parameter resolution logic is in:
- `crates/ty_python_semantic/src/types/call/bind.rs`

Look at where `DATACLASS_FLAGS` are iterated and how parameter types are looked up. The current approach only works when the transformer's signature explicitly names each parameter — it doesn't handle the case where parameters arrive through `**kwargs`.

## Expected Behavior

All three transformer patterns (function-based, metaclass-based, base-class-based) should correctly respect dataclass parameters like `frozen`, `eq`, `order`, and `kw_only` even when the transformer uses `**kwargs` in its signature.
