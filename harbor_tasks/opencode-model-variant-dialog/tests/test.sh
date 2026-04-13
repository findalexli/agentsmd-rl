#!/bin/bash
# Test runner script

cd /tests

# Run ALL tests (both pass_to_pass and fail_to_pass)
python3 -m pytest test_outputs.py -v 2>&1
ALL_EXIT=$?

if [ $ALL_EXIT -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "All tests passed!"
    echo "=========================================="
    # Write reward file
    mkdir -p /logs/verifier
    echo "1" > /logs/verifier/reward.txt
else
    echo ""
    echo "=========================================="
    echo "Some tests failed!"
    echo "=========================================="
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
fi

exit $ALL_EXIT
