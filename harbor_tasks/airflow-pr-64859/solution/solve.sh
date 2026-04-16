#!/bin/bash
set -e

cd /workspace/airflow

# Check if patch already applied
if grep -q "START_EXCLUDE_NEWER_PACKAGE" scripts/ci/prek/update_airflow_pyproject_toml.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Use Python to apply the changes
python3 << 'EOF'
import re
from pathlib import Path

# Update update_airflow_pyproject_toml.py
update_script = Path("scripts/ci/prek/update_airflow_pyproject_toml.py")
content = update_script.read_text()

# 1. Add the new constants after END_PROVIDER_WORKSPACE_MEMBERS
new_constants = '''
START_EXCLUDE_NEWER_PACKAGE = (
    "# Automatically generated exclude-newer-package entries (update_airflow_pyproject_toml.py)"
)
END_EXCLUDE_NEWER_PACKAGE = "# End of automatically generated exclude-newer-package entries"

START_EXCLUDE_NEWER_PACKAGE_PIP = (
    "# Automatically generated exclude-newer-package-pip entries (update_airflow_pyproject_toml.py)"
)
END_EXCLUDE_NEWER_PACKAGE_PIP = "# End of automatically generated exclude-newer-package-pip entries"
'''

# Find the line with END_PROVIDER_WORKSPACE_MEMBERS and insert after it
pattern = r'(END_PROVIDER_WORKSPACE_MEMBERS = "[^"]*")'
content = re.sub(pattern, r'\1' + new_constants, content)

# 2. Add the new function after _read_toml
new_function = '''

def get_all_workspace_component_names() -> list[str]:
    """Get all workspace component names from [tool.uv.sources] in pyproject.toml."""
    toml_dict = _read_toml(AIRFLOW_PYPROJECT_TOML_FILE)
    sources = toml_dict.get("tool", {}).get("uv", {}).get("sources", {})
    return sorted(
        name for name, value in sources.items() if isinstance(value, dict) and value.get("workspace")
    )

'''

# Find the _read_toml function end and insert after it
pattern = r'(def _read_toml\(path: Path\) -> dict\[str, Any\]:[^}]+return tomllib\.loads\(path\.read_text\(\)\))'
content = re.sub(pattern, r'\1' + new_function, content)

update_script.write_text(content)
print("Updated update_airflow_pyproject_toml.py")

# Update install_airflow_and_providers.py
install_script = Path("scripts/in_container/install_airflow_and_providers.py")
content = install_script.read_text()

# Replace the --exclude-newer datetime pattern with just --pre
# Old: base_install_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
# New: base_install_cmd.extend(["--pre"])
content = re.sub(
    r'(base_install_\w+\.extend\(\[)"--pre", "--exclude-newer", datetime\.now\(\)\.isoformat\(\)\]',
    r'\1"--pre"]',
    content
)

install_script.write_text(content)
print("Updated install_airflow_and_providers.py")

print("Patch applied successfully")
EOF
