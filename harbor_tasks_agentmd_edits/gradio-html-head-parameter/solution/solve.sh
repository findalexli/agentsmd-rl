#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q '"head": self.head' gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply changes using Python
python3 << 'PYEOF'
import re

# 1. Modify html.py - add head parameter to __init__
with open("gradio/components/html.py", "r") as f:
    html_content = f.read()

# Add head parameter after server_functions parameter
html_content = html_content.replace(
    "server_functions: list[Callable] | None = None,",
    "server_functions: list[Callable] | None = None,\n        head: str | None = None,"
)

# Add head docstring after apply_default_css docstring  
html_content = html_content.replace(
    "apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.",
    "apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.\n            head: A raw HTML string to inject into the document before js_on_load runs."
)

# Add self.head = head after self.apply_default_css
html_content = html_content.replace(
    "self.apply_default_css = apply_default_css",
    "self.apply_default_css = apply_default_css\n        self.head = head"
)

# Add head to api_info return value
html_content = html_content.replace(
    'def api_info(self) -> dict[str, Any]:\n        return {"type": "string"}',
    'def api_info(self) -> dict[str, Any]:\n        return {"type": "string", "head": self.head}'
)

# Modify get_config to exclude head from the result
# The original code does: config = super().get_config() and returns it
# We need to pop head from the config before returning
old_get_config = '''def get_config(self) -> dict[str, Any]:  # type: ignore[override]
        if type(self) is not HTML:
            config = {
                **super().get_config(),
                **super().get_config(HTML),
            }
        else:
            config = super().get_config()
        # For custom HTML components, we use the component_class_name
        # to identify the component in the frontend when reporting errors.
        config["component_class_name"] = self.component_class_name
        return config'''

new_get_config = '''def get_config(self) -> dict[str, Any]:  # type: ignore[override]
        if type(self) is not HTML:
            config = {
                **super().get_config(),
                **super().get_config(HTML),
            }
        else:
            config = super().get_config()
        # For custom HTML components, we use the component_class_name
        # to identify the component in the frontend when reporting errors.
        config["component_class_name"] = self.component_class_name
        # Remove head from config as it is handled separately via api_info
        config.pop("head", None)
        return config'''

html_content = html_content.replace(old_get_config, new_get_config)

with open("gradio/components/html.py", "w") as f:
    f.write(html_content)

# 2. Modify SKILL.md if it exists
import os
if os.path.exists(".agents/skills/gradio/SKILL.md"):
    with open(".agents/skills/gradio/SKILL.md", "r") as f:
        skill_content = f.read()
    
    # Update HTML signature to include head parameter
    skill_content = skill_content.replace(
        "server_functions: list[Callable] | None = None, props: Any)`",
        "server_functions: list[Callable] | None = None, head: str | None = None, props: Any)`"
    )
    
    with open(".agents/skills/gradio/SKILL.md", "w") as f:
        f.write(skill_content)

print("Changes applied successfully.")
PYEOF

echo "Done."
