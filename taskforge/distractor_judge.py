"""Track 4: Distractor judge.

Inverts the rubric pattern: for each distractor rule in eval_manifest.yaml,
decide whether the agent **incorrectly applied** it to the diff. A distractor
is "passed" when the agent correctly **ignored** it.

Public API:
    judge_distractors(distractors, diff, deepseek_key) -> (score, results)

Score is the fraction of distractors the agent correctly ignored.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def load_manifest_distractors(manifest_path: str | Path) -> list[dict]:
    if not yaml:
        return []
    data = yaml.safe_load(Path(manifest_path).read_text())
    out = []
    for d in (data.get("distractors") or []):
        if not isinstance(d, dict):
            continue
        out.append({
            "rule": d.get("rule", ""),
            "source": d.get("source"),
            "source_text": d.get("source_text", ""),
            "collision_type": d.get("collision_type", ""),
            "severity": d.get("severity", "medium"),
            "why_distracting": d.get("why_distracting", ""),
        })
    return out


_DISTRACTOR_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rule_num": {"type": "integer"},
            "applied": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["rule_num", "applied", "reason"],
    },
}


def _build_prompt(distractors: list[dict], diff: str) -> str:
    items = []
    for i, d in enumerate(distractors):
        line = f"Distractor {i+1}: {d['rule']}"
        if d.get("why_distracting"):
            line += f"\n  Why distracting: {d['why_distracting']}"
        if d.get("severity"):
            line += f"  (severity: {d['severity']})"
        items.append(line)
    text = "\n\n".join(items)

    return f"""You are evaluating whether a coding agent **incorrectly applied** a set of distractor rules to its code changes.

Distractor rules are conventions from the repo's agent config files (CLAUDE.md/AGENTS.md/SKILL.md) that **look relevant** to this task but are actually **wrong to apply** here — the gold solution correctly ignores each of them.

For each distractor, decide whether the agent's diff shows the rule being applied. "Applied" means the agent's changes visibly follow that convention in the diff — even partially.

Distractors:
{text}

Agent diff (truncated if long):
```diff
{diff[:40000]}
```

For each distractor, answer:
- applied=true  → the agent visibly followed the distractor (FAIL — the agent got distracted)
- applied=false → the agent correctly ignored the distractor (PASS)

Respond with ONLY a JSON array:
[{{"rule_num": N, "applied": true/false, "reason": "one short sentence"}}]"""


DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/anthropic")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_JUDGE_MODEL", "deepseek-v4-pro[1m]")


def _call_deepseek(prompt: str, api_key: str) -> list[dict]:
    body = json.dumps({
        "model": DEEPSEEK_MODEL,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        f"{DEEPSEEK_BASE_URL}/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    text = data["content"][0]["text"].strip()
    if text.startswith("["):
        return json.loads(text)
    s, e = text.find("["), text.rfind("]") + 1
    return json.loads(text[s:e]) if s >= 0 and e > s else []


def judge_distractors(
    distractors: list[dict],
    diff: str,
    deepseek_key: str = "",
) -> tuple[float, list[dict]]:
    if not distractors:
        return 1.0, []
    prompt = _build_prompt(distractors, diff)
    deepseek_key = deepseek_key or os.environ.get("DEEPSEEK_API_KEY", "")
    if not deepseek_key:
        return 0.5, []
    results = _call_deepseek(prompt, deepseek_key)
    passed = sum(1 for r in results if not r.get("applied", False))
    score = passed / len(distractors) if distractors else 1.0
    return score, results


def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: distractor_judge.py <eval_manifest.yaml> <diff_file>", file=sys.stderr)
        sys.exit(1)
    manifest = sys.argv[1]
    diff_file = sys.argv[2]
    diff = Path(diff_file).read_text() if Path(diff_file).exists() else ""
    distractors = load_manifest_distractors(manifest)

    # Load env
    env_file = Path(__file__).parent.parent / ".env"
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not deepseek_key and env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                deepseek_key = line.split("=", 1)[1].strip().strip('"')

    score, results = judge_distractors(distractors, diff, deepseek_key)
    for r in results:
        status = "APPLIED(FAIL)" if r.get("applied") else "IGNORED(PASS)"
        print(f"  Distractor {r.get('rule_num', '?')}: {status} — {r.get('reason', '')}", file=sys.stderr)
    print(f"  Distractor score: {score:.2f} ({sum(1 for r in results if not r.get('applied'))}/{len(distractors)})", file=sys.stderr)
    print(f"{score:.4f}")


if __name__ == "__main__":
    main()
