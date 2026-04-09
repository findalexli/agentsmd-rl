#!/bin/bash
set -e
cd /workspace/vscode
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/verifier_output.log
exit_code=${PIPESTATUS[0]}
exit $exit_code
