#!/usr/bin/env python3
"""LLM judge for agent config rule compliance."""
import json
import os
import subprocess
import sys
from pathlib import Path


def parse_rubric(path: str) -> list[dict]:
    """Parse rubric.yaml into a list of {rule, from} dicts."""
    text = Path(path).read_text()
    data = {"rules": []}
    in_rules = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "rules:":
            in_rules = True
            continue
        if in_rules and stripped.startswith("- "):
            val = stripped[2:].strip().strip('"').strip("'")
            if val.startswith("rule:"):
                data["rules"].append({"rule": val[5:].strip().strip('"')})
            else:
                data["rules"].append(val)
        elif in_rules and stripped.startswith("from:") and data["rules"]:
            last = data["rules"][-1]
            if isinstance(last, dict):
                last["from"] = stripped[5:].strip().strip('"')

    rules = []
    for r in data.get("rules", []):
        if isinstance(r, str):
            rules.append({"rule": r, "from": None})
        elif isinstance(r, dict):
            rule_text = r.get("rule") or r.get("text") or r.get("id", "")
            source = r.get("from")
            if not source and "source" in r:
                src = r["source"]
                if isinstance(src, dict):
                    f = src.get("file", "")
                    lines = src.get("lines", [0, 0])
                    source = f"{f}:{lines[0]}" if f else None
            rules.append({"rule": rule_text, "from": source})
    return rules


def get_diff(repo_dir: str) -> str:
    """Get the agent's changes as a unified diff."""
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=repo_dir, capture_output=True, text=True
    )
    diff = result.stdout
    if not diff:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=repo_dir, capture_output=True, text=True
        )
        diff = result.stdout
    if not diff:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=repo_dir, capture_output=True, text=True
        )
        if result.stdout.strip():
            result = subprocess.run(
                ["git", "diff", "HEAD~1"],
                cwd=repo_dir, capture_output=True, text=True
            )
            diff = result.stdout
    return diff[:50000]


def call_judge(rules: list[dict], diff: str, api_key: str) -> list[dict]:
    """Call the LLM to evaluate each rule against the diff."""
    import urllib.request

    rules_text = "\n".join(
        f"{i+1}. {r['rule']}" + (f" (from {r['from']})" if r['from'] else "")
        for i, r in enumerate(rules)
    )

    prompt = f"""You are evaluating whether a code patch follows repository guidelines.

RULES (from the repo's agent config files):
{rules_text}

PATCH:
```diff
{diff}
```

For each rule, respond with ONLY a JSON array. Each element:
{{"rule_num": N, "pass": true/false, "reason": "one sentence"}}

If a rule is not applicable to this patch, set "pass": true.
Respond with ONLY the JSON array, no other text."""

    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    text = data["content"][0]["text"].strip()
    if text.startswith("["):
        return json.loads(text)
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return []


def main():
    if len(sys.argv) < 3:
        print("0.0")
        sys.exit(0)

    rubric_path = sys.argv[1]
    repo_dir = sys.argv[2]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"')
        if not api_key:
            print("0.5")
            sys.exit(0)

    rules = parse_rubric(rubric_path)
    if not rules:
        print("1.0")
        sys.exit(0)

    diff = get_diff(repo_dir)
    if not diff:
        print("0.5")
        sys.exit(0)

    try:
        results = call_judge(rules, diff, api_key)
    except Exception:
        print("0.5")
        sys.exit(0)

    if not results:
        print("0.5")
        sys.exit(0)

    passed = sum(1 for r in results if r.get("pass", False))
    total = len(results)
    icr = passed / total if total > 0 else 0.5
    print(f"{icr:.4f}")


if __name__ == "__main__":
    main()
