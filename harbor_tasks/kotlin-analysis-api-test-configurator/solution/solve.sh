#!/bin/bash
set -e

cd /workspace/kotlin

# Run the Python script to apply all changes
python3 /solution/solve.py

# Verify the distinctive line is present
grep -q "AnalysisApiTestConfiguratorFactoryData()" plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt
echo "Patch verified successfully"
