#!/usr/bin/env python3
"""
LLM Rubric Judge for evaluating code changes against style guidelines.
"""

import json
import os
import sys
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("anthropic not installed, skipping LLM judge")
    sys.exit(0)


def load_rubric(rubric_path: Path) -> dict:
    """Load rubric.yaml rules."""
    import yaml
    with open(rubric_path) as f:
        return yaml.safe_load(f)


def load_diff() -> str:
    """Load git diff from environment or file."""
    diff_path = os.environ.get("DIFF_FILE", "/workspace/diff.patch")
    if Path(diff_path).exists():
        with open(diff_path) as f:
            return f.read()
    # Try to get diff from git
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "--no-color"],
            capture_output=True,
            text=True,
            cwd="/workspace/react"
        )
        return result.stdout
    except:
        return ""


def evaluate_rules(diff: str, rules: list) -> dict:
    """Evaluate diff against rubric rules using LLM."""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    rules_text = "\n".join([
        f"{i+1}. {rule['rule']} (from: {rule.get('from', 'unknown')})"
        for i, rule in enumerate(rules)
    ])

    prompt = f"""As a code reviewer, evaluate the following code diff against these style rules:

RULES:
{rules_text}

CODE DIFF:
```diff
{diff[:4000]}
```

For each rule, determine if the code complies (COMPLIANT), violates (VIOLATION), or if not applicable (N/A).

Respond in JSON format:
{{
  "evaluations": [
    {{
      "rule": "rule text",
      "compliance": "COMPLIANT|VIOLATION|N/A",
      "reason": "brief explanation"
    }}
  ],
  "overall_score": 0.0 to 1.0,
  "summary": "brief summary"
}}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Extract JSON from response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        return json.loads(json_str)
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0.5,
            "summary": "Evaluation failed"
        }


def main():
    task_dir = Path(os.environ.get("TASK_DIR", "/task"))
    rubric_path = task_dir / "rubric.yaml"

    if not rubric_path.exists():
        print("No rubric.yaml found, skipping")
        sys.exit(0)

    rubric = load_rubric(rubric_path)
    rules = rubric.get("rules", [])

    if not rules:
        print("No rules in rubric, skipping")
        sys.exit(0)

    diff = load_diff()
    if not diff:
        print("No diff found, skipping")
        sys.exit(0)

    result = evaluate_rules(diff, rules)

    # Write result
    output_path = Path(os.environ.get("REWARD_JSON", "/logs/verifier/reward.json"))
    if output_path.exists():
        with open(output_path) as f:
            data = json.load(f)
    else:
        data = {}

    data["llm_rubric"] = result
    data["llm_rubric_score"] = result.get("overall_score", 0.5)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"LLM Rubric Score: {result.get('overall_score', 0.5)}")


if __name__ == "__main__":
    main()
