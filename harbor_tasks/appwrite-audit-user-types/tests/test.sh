#!/bin/bash
cd /workspace/appwrite
python3 -m pytest /tests/test_new.py -v --tb=short
PY_EXIT=$?
mkdir -p /logs/verifier
if [ $PY_EXIT -eq 0 ]; then echo "1" > /logs/verifier/reward.txt; else echo "0" > /logs/verifier/reward.txt; fi
