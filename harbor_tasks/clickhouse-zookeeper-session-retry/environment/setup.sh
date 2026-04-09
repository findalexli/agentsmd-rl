#!/bin/bash
set -e

cd /workspace/ClickHouse

# Ensure the repository is at the base commit
git checkout 6f01023e78a9e84c588068560fda778a7c11a665

# Create logs directory
mkdir -p /logs/verifier

echo "Environment setup complete. Repository is at base commit."
