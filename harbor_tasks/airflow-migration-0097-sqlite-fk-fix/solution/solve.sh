#!/bin/bash
set -e

cd /workspace/task

MIGRATION_FILE="airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py"

# Check if already patched
if grep -A2 "with disable_sqlite_fkeys(op):" "$MIGRATION_FILE" | grep -q "UPDATE log SET"; then
    echo "Already patched"
    # Still run ruff to ensure formatting is correct
    pip install ruff -q 2>/dev/null || true
    ruff format "$MIGRATION_FILE" 2>/dev/null || true
    exit 0
fi

# Apply the fix using Python
python3 << 'PYTHON_EOF'
file_path = "airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py"

with open(file_path, "r") as f:
    content = f.read()

# Remove the UPDATE statements and their comments from before the with block
# This removes lines with the comments and UPDATE statements
lines = content.split('\n')
new_lines = []
in_upgrade = False
found_disable = False
skip_lines = set()

# First pass: identify lines to skip
for i, line in enumerate(lines):
    if line.strip().startswith("def upgrade():"):
        in_upgrade = True
    elif in_upgrade and line.strip().startswith("def "):
        in_upgrade = False
    
    if in_upgrade and not found_disable:
        # Skip comments about log.event and dag.is_stale
        if "log.event can safely" in line or "Make sure DAG rows" in line:
            skip_lines.add(i)
        # Skip the UPDATE statements
        if "UPDATE log SET" in line and "op.execute" in line:
            skip_lines.add(i)
        if "UPDATE dag SET" in line and "op.execute" in line:
            skip_lines.add(i)
    
    if "with disable_sqlite_fkeys(op):" in line:
        found_disable = True

# Second pass: build new content
in_upgrade = False
found_disable = False
for i, line in enumerate(lines):
    if i in skip_lines:
        continue
    
    new_lines.append(line)
    
    if line.strip().startswith("def upgrade():"):
        in_upgrade = True
    elif in_upgrade and line.strip().startswith("def "):
        in_upgrade = False
    
    if in_upgrade and "with disable_sqlite_fkeys(op):" in line and not found_disable:
        # Insert UPDATE statements after the with disable_sqlite_fkeys line
        indent = "        "
        new_lines.append(f"{indent}op.execute(\"UPDATE log SET event = '' WHERE event IS NULL\")")
        new_lines.append(f"{indent}op.execute(\"UPDATE dag SET is_stale = false WHERE is_stale IS NULL\")")
        new_lines.append("")
        found_disable = True

content = "\n".join(new_lines)

with open(file_path, "w") as f:
    f.write(content)

print("Migration file updated successfully")
PYTHON_EOF

# Run ruff format to ensure proper formatting
pip install ruff -q 2>/dev/null || true
ruff format "$MIGRATION_FILE" 2>/dev/null || true

echo "Patch applied successfully"
