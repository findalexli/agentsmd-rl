#!/bin/bash
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short
pytest_exit=$?
if [ $pytest_exit -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi