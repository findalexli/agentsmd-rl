#!/usr/bin/env bash
# Standardized test harness — runs pytest, writes binary reward to
# /logs/verifier/reward.txt based purely on pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# Run pytest. CTRF JSON report is written for downstream analysis.
# -p no:cacheprovider avoids cache-write warnings on the read-only /tests mount.
python -m pytest \
    -v \
    --tb=short \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional judge step; markdown_authoring uses Track 2 via Gemini in
# the harness, configured from eval_manifest.yaml's config_edits section.)

exit 0
