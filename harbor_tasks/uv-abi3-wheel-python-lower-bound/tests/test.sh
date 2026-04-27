#!/usr/bin/env bash
# Standard task verifier. Reward = 1 iff all pytest tests pass.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# pytest + ctrf json plugin should already be installed in the image.
python3 -m pytest \
    test_outputs.py \
    -v --tb=short \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "PYTEST_RC=$PYTEST_RC"
echo "REWARD=$(cat /logs/verifier/reward.txt)"

exit 0
