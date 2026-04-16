# Add Server Functions Support to gr.HTML

## Problem

The `gr.HTML` component supports a `js_on_load` parameter for running JavaScript when the component loads, but there is currently no way to call Python backend functions from within that JavaScript code. Users need a mechanism to define Python functions and invoke them asynchronously from `js_on_load` scripts.

## Expected Behavior

### Python Component Changes (gradio/components/html.py)

1. **Import the server decorator**: Add `server` to the import from `gradio.components.base`. The import line should contain:
   ```
   from gradio.components.base import Component, server
   ```

2. **New `server_functions` parameter**: Add a `server_functions` parameter to the HTML component's `__init__` method with type `list[Callable] | None` defaulting to `None`, placed between the `buttons` and `props` parameters.

3. **Function registration implementation**: When `server_functions` is provided, implement the registration logic with these exact patterns:
   - Check `if server_functions:` to handle the non-empty case
   - Loop with `for fn in server_functions:` to iterate over functions
   - Decorate each function with `decorated = server(fn)` (assignment to `decorated` variable)
   - Attach the decorated function to the instance using `setattr(self, fn_name, decorated)` where `fn_name` is the function's `__name__`
   - Append the decorated function to `self.server_fns`

4. **`js_on_load` docstring update**: The docstring for `js_on_load` must be updated to document that a `server` object is available when `server_functions` is provided. The updated docstring must contain the word "server" and the term "server_functions".

5. **`server_functions` parameter docstring**: Add a docstring entry for the `server_functions` parameter that:
   - Begins with the exact text `server_functions:` (as the parameter label)
   - Contains the phrase "async method" to describe how functions are called from JavaScript
   - Explains that each function becomes an async method that sends calls to the backend and returns results

### Frontend Changes

6. **Server object in `js_on_load`**: The `server` object must be propagated through the Svelte component hierarchy and made available as a parameter in the `js_on_load` function execution. The JavaScript function that runs `js_on_load` must receive `server` alongside the existing `element`, `trigger`, and `props` parameters so that code like `server.my_func(arg).then(result => ...)` or `const result = await server.my_func(arg)` works.

### Agent Skill Documentation

7. **Update SKILL.md HTML signature**: The HTML component signature in `.agents/skills/gradio/SKILL.md` must include the new `server_functions` parameter with type `list[Callable] | None = None`, placed between the `buttons` and `props` parameters in the function signature.

8. **Add Server Functions section**: Add a new `## Server Functions` section to the same SKILL.md file that includes:
   - An explanation of how `server_functions` integrates with `js_on_load`
   - A complete working example showing `server_functions=[function_name]` syntax
   - Documentation of the `server` object's async interface, with example code containing both `server.` (method calls with dot notation) and `await` (async/await syntax) usage
