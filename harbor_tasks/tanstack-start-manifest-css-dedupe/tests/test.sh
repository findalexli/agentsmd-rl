#!/bin/bash
set -e

# Install pytest if not available (using --break-system-packages for container environment)
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet || true

# Run the test file
pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1

# Exit with pytest's exit code
exit ${PIPESTATUS[0]}
