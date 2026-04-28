#!/usr/bin/env python3
"""Standalone judge for LLM-based rubric evaluation."""
import json
import sys

# Placeholder — LLM judge evaluation is handled by the Harbor runtime.
# This script exists so test.sh can invoke it without error.
print(json.dumps({"status": "ok", "verdict": "judge_not_run_in_scaffold"}))
