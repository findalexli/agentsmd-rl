#!/usr/bin/env python3
"""LLM rubric judge for react-native-event-global-dispatch task."""
import argparse
import json
import os

# Copy of agentsmd_rl/judge.py adapted for this task

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--agent-output", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Read rubric
    rubric_path = os.path.join(args.task, "rubric.yaml")
    # Simplified: just output placeholder since we don't use LLM judge by default
    result = {
        "reward": 0.0,
        "passed": 0,
        "failed": 0,
        "rules": []
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Judge output written to {args.output}")

if __name__ == "__main__":
    main()
