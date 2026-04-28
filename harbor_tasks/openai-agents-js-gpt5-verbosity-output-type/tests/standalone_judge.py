"""Standalone judge stub for tasks that don't need LLM config-diff evaluation."""
import json, os

# This is a code_fix task — no markdown config edits to judge.
# Write a no-op pass so the test.sh judge block doesn't crash.
os.makedirs("/logs/verifier", exist_ok=True)
judge_out = {"score": 1.0, "notes": "code_fix task — no config-diff evaluation"}
with open("/logs/verifier/judge.json", "w") as f:
    json.dump(judge_out, f)
print("Judge: no-op (code_fix task)")
