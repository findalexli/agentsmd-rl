#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Standardized test runner - DO NOT MODIFY task-specific logic here

set -euo pipefail

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install --quiet --break-system-packages pytest
fi

# Run tests and capture result
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
