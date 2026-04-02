#!/usr/bin/env python3
"""LLM judge for agent config rule compliance.

Reads rubric.yaml (list of rules from agent config files),
diffs the agent's changes, asks the LLM to evaluate each rule.
Returns a float score to stdout for test.sh to consume.

Usage in test.sh:
    ICR=$(python3 /judge.py /path/to/rubric.yaml /workspace/repo 2>/dev/null || echo "0.0")
    SCORE=$(python3 -c "print($SCORE + 0.15 * float('$ICR'))")

Rubric format (dead simple, LLM-writable):
    rules:
      - "Functions parsing external input must handle malformed lines gracefully"
      - "New code must match surrounding style"
      - "No wildcard imports"

Or with source attribution:
    rules:
      - rule: "Functions parsing external input must handle malformed lines gracefully"
        from: ".claude/skills/write-sglang-test/SKILL.md:8"
      - rule: "New code must match surrounding style"
        from: "AGENTS.md:45"
"""

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # Inline YAML parser for the simple format we use
    yaml = None


def parse_rubric(path: str) -> list[dict]:
    """Parse rubric.yaml into a list of {rule, from} dicts."""
    text = Path(path).read_text()

    if yaml:
        data = yaml.safe_load(text)
    else:
        # Minimal parser: extract lines starting with "- " under "rules:"
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
                    # Complex form: - rule: "..." \n   from: "..."
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
            # Handle both new simple format and old complex format
            rule_text = r.get("rule") or r.get("text") or r.get("id", "")
            source = r.get("from")
            if not source and "source" in r:
                # Old format: source: {file: "...", lines: [N, M]}
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
        # Maybe changes are staged
        result = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=repo_dir, capture_output=True, text=True
        )
        diff = result.stdout
    if not diff:
        # Maybe committed — diff against original checkout
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
    return diff[:50000]  # Cap at 50k chars


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
    # Extract JSON from response
    if text.startswith("["):
        return json.loads(text)
    # Try to find JSON array in the response
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return []


def main():
    if len(sys.argv) < 3:
        print("Usage: judge.py <rubric.yaml> <repo_dir>", file=sys.stderr)
        print("0.0")
        sys.exit(0)

    rubric_path = sys.argv[1]
    repo_dir = sys.argv[2]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try .env file
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"')
        if not api_key:
            print("0.5", file=sys.stderr)  # No API key = neutral score
            print("0.5")
            sys.exit(0)

    rules = parse_rubric(rubric_path)
    if not rules:
        print("1.0")  # No rules = perfect compliance
        sys.exit(0)

    diff = get_diff(repo_dir)
    if not diff:
        print("0.5")  # No diff = can't evaluate
        sys.exit(0)

    try:
        results = call_judge(rules, diff, api_key)
    except Exception as e:
        print(f"Judge error: {e}", file=sys.stderr)
        print("0.5")  # API failure = neutral
        sys.exit(0)

    # Compute ICR: fraction of rules that pass
    if not results:
        print("0.5")
        sys.exit(0)

    passed = sum(1 for r in results if r.get("pass", False))
    total = len(results)
    icr = passed / total if total > 0 else 0.5

    # Print details to stderr, score to stdout
    for r in results:
        status = "PASS" if r.get("pass") else "FAIL"
        print(f"  Rule {r.get('rule_num', '?')}: {status} — {r.get('reason', '')}", file=sys.stderr)
    print(f"  ICR: {passed}/{total} = {icr:.2f}", file=sys.stderr)

    print(f"{icr:.4f}")


if __name__ == "__main__":
    main()
