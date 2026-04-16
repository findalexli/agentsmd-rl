#!/bin/bash
set -e

cd /workspace/airflow

TARGET_FILE="dev/breeze/src/airflow_breeze/utils/constraints_version_check.py"

# Check if patch has already been applied (idempotency)
if grep -q "get_latest_version_with_cooldown" "$TARGET_FILE" 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Use Python to apply the changes
python3 << 'PYTHON_SCRIPT'
import re
from pathlib import Path

file_path = Path("dev/breeze/src/airflow_breeze/utils/constraints_version_check.py")
content = file_path.read_text()

# 1. Fix the import: add timedelta
content = content.replace(
    "from datetime import datetime\n",
    "from datetime import datetime, timedelta\n"
)

# 2. Add the get_latest_version_with_cooldown function after should_show_package
new_function = '''

def get_latest_version_with_cooldown(releases: dict[str, Any], cooldown_days: int) -> str | None:
    """Find the latest non-prerelease version whose release date is outside the cooldown period.

    Returns the version string, or None if no version qualifies.
    """
    from packaging import version

    cutoff = datetime.now() - timedelta(days=cooldown_days)
    candidates: list[tuple[version.Version, str]] = []
    for v, release_files in releases.items():
        if not release_files:
            continue
        try:
            parsed_v = version.parse(v)
        except version.InvalidVersion:
            continue
        if parsed_v.is_prerelease or parsed_v.is_devrelease:
            continue
        try:
            upload_time = datetime.fromisoformat(
                release_files[0]["upload_time_iso_8601"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except (KeyError, IndexError, ValueError):
            continue
        if upload_time <= cutoff:
            candidates.append((parsed_v, v))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

'''

# Find the end of should_show_package function and insert new function
pattern = r'(def should_show_package\(.*?    return True\n)'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.end()] + new_function + content[match.end():]

# 3. Add cooldown_days parameter to constraints_version_check function
# Replace the closing of the function signature
content = content.replace(
    "    github_repository: str | None = None,\n):",
    "    github_repository: str | None = None,\n    cooldown_days: int = 4,\n):"
)

# 4. Add cooldown period console print
content = content.replace(
    'console_print(f"[bold cyan]Constraints mode:[/] [white]{airflow_constraints_mode}[/]\\n")',
    'console_print(f"[bold cyan]Constraints mode:[/] [white]{airflow_constraints_mode}[/]")\n    console_print(f"[bold cyan]Cooldown period:[/] [white]{cooldown_days} days[/]\\n")'
)

# 5. Add cooldown_days parameter to process_packages call
content = content.replace(
    "        github_repository=github_repository,\n    )",
    "        github_repository=github_repository,\n        cooldown_days=cooldown_days,\n    )"
)

# 6. Add cooldown_days parameter to process_packages function definition
content = content.replace(
    "    github_repository: str | None,\n) -> tuple[int, int, list[str], dict[str, int]]:",
    "    github_repository: str | None,\n    cooldown_days: int = 4,\n) -> tuple[int, int, list[str], dict[str, int]]:"
)

# 7. Modify process_packages to use cooldown function
content = content.replace(
    '''data = fetch_pypi_data(pkg)
            latest_version = data["info"]["version"]
            releases = data["releases"]''',
    '''data = fetch_pypi_data(pkg)
            releases = data["releases"]
            latest_version_with_cooldown = get_latest_version_with_cooldown(releases, cooldown_days)
            latest_version = latest_version_with_cooldown or data["info"]["version"]'''
)

file_path.write_text(content)
print("Patch applied successfully")
PYTHON_SCRIPT

echo "Patch applied successfully"
