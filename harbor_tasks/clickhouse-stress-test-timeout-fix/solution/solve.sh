#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already patched (idempotency)
if grep -q 'start_server 30' tests/docker_scripts/stress_runner.sh; then
    echo "Already patched, exiting"
    exit 0
fi

python3 << 'EOF'
import re

file_path = "tests/docker_scripts/stress_runner.sh"

with open(file_path, 'r') as f:
    content = f.read()

# Fix 1: Replace date-based randomization with $RANDOM
# Change: if [ $(( $(date +%-d) % 2 )) -eq 0 ]; then
# To:     if [ $((RANDOM % 2)) -eq 0 ]; then
content = re.sub(
    r'if \[ \$\(\( \$\(date \+%-d\) % 2 \)\) -eq 0 \]; then',
    'if [ $((RANDOM % 2)) -eq 0 ]; then',
    content
)

# Fix 2: Replace the post-stress start_server call
# The pattern is:
# rm /etc/clickhouse-server/config.d/cannot_allocate_thread_injection.xml
# <blank line>
# start_server || { echo "Failed to start server"; exit 1; }
content = re.sub(
    r'(rm /etc/clickhouse-server/config\.d/cannot_allocate_thread_injection\.xml)\n\n(start_server \|\| \{ echo "Failed to start server"; exit 1; \})',
    r'''\1

# Use a larger timeout for the post-stress restart: under sanitizers with
# async_load_databases=false the server may need minutes to load all tables.
start_server 30 || { echo "Failed to start server"; exit 1; }''',
    content
)

with open(file_path, 'w') as f:
    f.write(content)

print("Changes applied successfully")
EOF

# Verify the changes
if ! grep -q '$((RANDOM % 2))' tests/docker_scripts/stress_runner.sh; then
    echo "ERROR: Failed to replace date-based randomization with RANDOM"
    exit 1
fi

if ! grep -q 'start_server 30' tests/docker_scripts/stress_runner.sh; then
    echo "ERROR: Failed to add timeout to post-stress start_server call"
    exit 1
fi

if ! grep -q 'larger timeout for the post-stress restart' tests/docker_scripts/stress_runner.sh; then
    echo "ERROR: Failed to add explanatory comment"
    exit 1
fi

echo "Patch applied successfully"
