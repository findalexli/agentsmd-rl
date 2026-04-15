# Add Server Functions Support to gr.HTML

## Problem

The `gr.HTML` component supports a `js_on_load` parameter for running JavaScript when the component loads, but there is currently no way to call Python backend functions from within that JavaScript code. Users need a mechanism to define Python functions and invoke them asynchronously from `js_on_load` scripts.

The Gradio codebase already has a `server` decorator in the base component module that is used by other components (e.g., `FileExplorer`, `ImageEditor`) to register server-callable functions. This same mechanism should be made available for `gr.HTML`.

## Expected Behavior

### Python Component Changes

1. **New `server_functions` parameter**: Add a `server_functions` parameter to the HTML component's constructor with type `list[Callable] | None` defaulting to `None`. This allows users to pass a list of Python callables that can be invoked from JavaScript.

2. **Function registration**: When `server_functions` is provided, each function must be:
   - Decorated with the `server` decorator from the base component module (the same one used by `FileExplorer` and `ImageEditor`)
   - Set as a named attribute on the component instance (using the function's `__name__`)
   - Added to the component's existing `server_fns` list

3. **`js_on_load` docstring update**: The docstring for `js_on_load` must be updated to document that a `server` object is available when `server_functions` is provided. The updated docstring must contain the word "server" and the term "server_functions".

4. **`server_functions` parameter docstring**: Add a docstring entry for `server_functions` that:
   - Begins with `server_functions:` (as a parameter label)
   - Explains that each function becomes an async method that sends calls to the Python backend and returns results (the docstring must contain either the phrase "async method" or the word "backend")

### Frontend Changes

5. **Server object in `js_on_load`**: The `server` object must be propagated through the Svelte component hierarchy and made available as a parameter in the `js_on_load` function execution. The JavaScript function that runs `js_on_load` must receive `server` alongside the existing `element`, `trigger`, and `props` parameters so that code like `server.my_func(arg).then(result => ...)` or `const result = await server.my_func(arg)` works.

### Agent Skill Documentation

6. **Update SKILL.md HTML signature**: The HTML component signature in `.agents/skills/gradio/SKILL.md` must include the new `server_functions` parameter, placed between the `buttons` and `props` parameters.

7. **Add Server Functions section**: Add a new `## Server Functions` section to the same SKILL.md file that includes:
   - An explanation of how `server_functions` integrates with `js_on_load`
   - A complete working example showing `server_functions=[list_files]` syntax
   - Documentation of the `server` object's async interface, with example code containing both `server.` (method calls) and `await` usage
