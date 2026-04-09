#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Run tests
cd /workspace/task/tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Exit with pytest's exit code
exit ${PIPESTATUS[0]}
