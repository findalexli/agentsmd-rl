#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest and dependencies
pip install pytest pyarrow numpy lancedb ruff --quiet 2>/dev/null || true

# Set up the lancedb package properly for testing:
# 1. Clear PYTHONPATH to use pip-installed lancedb (which has compiled extensions)
# 2. Copy the repo's query.py to the pip-installed lancedb location
unset PYTHONPATH

# Copy the repo's query.py to the site-packages lancedb for testing
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
REPO_QUERY="/workspace/lancedb/python/python/lancedb/query.py"
INSTALLED_QUERY="$SITE_PACKAGES/lancedb/query.py"

if [ -f "$REPO_QUERY" ]; then
    cp "$REPO_QUERY" "$INSTALLED_QUERY"
    echo "Copied repo query.py to site-packages for testing"
fi

# Run the test suite and capture output
echo "Running tests..."
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "Tests passed - writing reward 1"
    echo "1" > /logs/verifier/reward.txt
else
    echo "Tests failed - writing reward 0"
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test execution complete. Reward written to /logs/verifier/reward.txt"
