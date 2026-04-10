#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q "server_functions" gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Modify html.py - add server_functions support
python3 << 'PYEOF'
with open('gradio/components/html.py', 'r') as f:
    content = f.read()

# Add server_functions parameter before **props
content = content.replace(
    '**props: Any,',
    'server_functions: list[Callable] | None = None,\n        **props: Any,'
)

# Add server_functions docstring after props docstring
content = content.replace(
    "props: Additional keyword arguments to pass into the HTML and CSS templates for rendering.\n        \"\"\"",
    "props: Additional keyword arguments to pass into the HTML and CSS templates for rendering.\n            server_functions: A list of Python functions that can be called from within the js_on_load script.\n        \"\"\""
)

# Add server_functions initialization after self.props = props
old_props = 'self.props = props'
new_props = '''self.props = props
        self.server_functions = server_functions'''
content = content.replace(old_props, new_props)

# Add __str__ method before example_payload
old_example = 'def example_payload(self) -> Any:'
new_example = '''def __str__(self):
        return f"HTML(value={self.value!r}, server_functions={[f.__name__ for f in self.server_functions] if self.server_functions else None})"

    def example_payload(self) -> Any:'''
content = content.replace(old_example, new_example)

with open('gradio/components/html.py', 'w') as f:
    f.write(content)
print("html.py modified")
PYEOF

# Modify SKILL.md
python3 << 'PYEOF'
with open('.agents/skills/gradio/SKILL.md', 'r') as f:
    content = f.read()
old_html = 'buttons: list[Button] | None = None, props: Any)`'
new_html = 'buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)`'
content = content.replace(old_html, new_html)
with open('.agents/skills/gradio/SKILL.md', 'w') as f:
    f.write(content)
print("SKILL.md modified")
PYEOF

# Modify test_html.py to expect server_functions in get_config
python3 << 'PYEOF'
with open('test/components/test_html.py', 'r') as f:
    content = f.read()

# Add server_functions to the expected get_config result
old_test = '"buttons": [],\n        }'
new_test = '"buttons": [],\n            "server_functions": None,\n        }'
content = content.replace(old_test, new_test)

with open('test/components/test_html.py', 'w') as f:
    f.write(content)
print("test_html.py modified")
PYEOF

echo "Patch applied successfully."
