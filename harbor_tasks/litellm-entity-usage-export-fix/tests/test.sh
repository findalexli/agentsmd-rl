#!/bin/bash

# Run test_outputs.py and capture result (don't exit on failure yet)
python3 -m pytest /tests/test_outputs.py -v --tb=short
result=$?

# Write reward (0=fail, 1=pass)
if [ $result -eq 0 ]; then
  echo -n 1 > /logs/verifier/reward.txt
else
  echo -n 0 > /logs/verifier/reward.txt
fi

# Exit with the pytest result
exit $result
