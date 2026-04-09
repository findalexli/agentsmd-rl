#!/bin/bash
set -e

cd /workspace/task

# Install pytest if not already installed
pip install pytest --quiet

# Run tests and capture output
pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Exit with pytest's exit code
exit ${PIPESTATUS[0]}
