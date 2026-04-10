#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied (check for server_functions parameter)
if grep -q 'server_functions: list\[Callable\]' gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
import re

# Patch 1: html.py
with open('gradio/components/html.py', 'r') as f:
    content = f.read()

# 1. Update import line
content = content.replace(
    'from gradio.components.base import Component',
    'from gradio.components.base import Component, server'
)

# 2. Add server_functions parameter
content = content.replace(
    'buttons: list[Button] | None = None,',
    'buttons: list[Button] | None = None,\n        server_functions: list[Callable] | None = None,'
)

# 3. Update js_on_load docstring
content = content.replace(
    "trigger('click'). The value and other props can be edited through `props`, e.g. `props.value = \"new value\"` which will re-render the HTML template.",
    "trigger('click'). The value and other props can be edited through `props`, e.g. `props.value = \"new value\"` which will re-render the HTML template. If `server_functions` is provided, a `server` object is also available in `js_on_load`, where each function is accessible as an async method, e.g. `server.list_files(path).then(files => ...)` or `const files = await server.list_files(path)`."
)

# 4. Add server_functions docstring
content = content.replace(
    'clicking them will trigger any .click() events registered on the button.',
    '''clicking them will trigger any .click() events registered on the button.
            server_functions: A list of Python functions that can be called from `js_on_load` via the `server` object. For example, if you pass `server_functions=[my_func]`, you can call `server.my_func(arg1, arg2)` in your `js_on_load` code. Each function becomes an async method that sends the call to the Python backend and returns the result.'''
)

# 5. Add server_functions logic
old_line = '        self.buttons = set_default_buttons(buttons, None)'
new_code = '''        self.buttons = set_default_buttons(buttons, None)
        if server_functions:
            for fn in server_functions:
                decorated = server(fn)
                fn_name = getattr(fn, "__name__", str(fn))
                setattr(self, fn_name, decorated)
                self.server_fns.append(decorated)'''
content = content.replace(old_line, new_code)

with open('gradio/components/html.py', 'w') as f:
    f.write(content)
print('html.py done')

# Patch 2: Index.svelte
with open('js/html/Index.svelte', 'r') as f:
    content = f.read()

content = content.replace(
    'component_class_name={gradio.props.component_class_name}',
    'component_class_name={gradio.props.component_class_name}\n\t\t\tserver={gradio.shared.server}'
)

with open('js/html/Index.svelte', 'w') as f:
    f.write(content)
print('Index.svelte done')

# Patch 3: HTML.svelte
with open('js/html/shared/HTML.svelte', 'r') as f:
    content = f.read()

# Add server prop
content = content.replace(
    'component_class_name = "HTML",\n\t\tchildren',
    'component_class_name = "HTML",\n\t\tserver = {},\n\t\tchildren'
)

# Add server type
content = content.replace(
    'component_class_name: string;\n\t\tchildren?: Snippet;',
    'component_class_name: string;\n\t\tserver: Record<string, (...args: any[]) => Promise<any>>;\n\t\tchildren?: Snippet;'
)

# Update js_on_load function
old_func = '''const func = new Function("element", "trigger", "props", js_on_load);
\t\t\t\tfunc(element, trigger, reactiveProps);'''
new_func = '''const func = new Function(
\t\t\t\t\t"element",
\t\t\t\t\t"trigger",
\t\t\t\t\t"props",
\t\t\t\t\t"server",
\t\t\t\t\tjs_on_load
\t\t\t\t);
\t\t\t\tfunc(element, trigger, reactiveProps, server);'''
content = content.replace(old_func, new_func)

with open('js/html/shared/HTML.svelte', 'w') as f:
    f.write(content)
print('HTML.svelte done')

# Patch 4: SKILL.md
with open('.agents/skills/gradio/SKILL.md', 'r') as f:
    content = f.read()

content = content.replace(
    'buttons: list[Button] | None = None, props: Any)',
    'buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)'
)

server_section = '''

## Server Functions

You can call Python functions directly from your `js_on_load` code using the `server_functions` parameter. Pass a list of Python functions to `server_functions`, and they become available as async methods on a `server` object inside `js_on_load`.

Example:
```python
import os
import gradio as gr

def list_files(path):
    try:
        return os.listdir(path)
    except (FileNotFoundError, PermissionError) as e:
        return [f"Error: {e}"]

with gr.Blocks() as demo:
    gr.Markdown("# Server Functions Demo")
    filetree = gr.HTML(
        value=os.path.abspath(''),
        html_template="""
            <div>
                <p>Directory: <strong>${value}</strong></p>
                <div class='tree'></div>
                <button class='load-btn'>Load Files</button>
            </div>
        """,
        js_on_load="""
            const loadBtn = element.querySelector('.load-btn');
            const tree = element.querySelector('.tree');
            loadBtn.addEventListener('click', async () => {
                const files = await server.list_files(props.value);
                tree.innerHTML = '';
                files.forEach(file => {
                    const fileEl = document.createElement('div');
                    fileEl.textContent = file;
                    tree.appendChild(fileEl);
                });
            });
        """,
        server_functions=[list_files],
    )

if __name__ == "__main__":
    demo.launch()
```

Each function in `server_functions` becomes an async method on the `server` object:
- Function name becomes the method name
- Arguments are passed to the Python function
- Returns a Promise that resolves with the function's return value
- Use `await server.func_name(args)` or `server.func_name(args).then(result => ...)`
'''

content = content + server_section

with open('.agents/skills/gradio/SKILL.md', 'w') as f:
    f.write(content)
print('SKILL.md done')
print('All patches applied!')
PYEOF
