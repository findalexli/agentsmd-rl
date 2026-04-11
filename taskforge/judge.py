#!/usr/bin/env python3
"""LLM judge for agent config rule compliance.

Two modes:
1. Legacy: reads rubric.yaml with simple rule strings
2. Manifest: reads eval_manifest.yaml rubric rules with optional gold references

For rubric rules with `reference` (extracted from solve.sh gold patch),
the judge compares the agent's actual file content against the gold
reference semantically — not exact string match.

Usage:
    # From eval_manifest.yaml (preferred)
    python3 judge.py --manifest /path/to/eval_manifest.yaml --repo /workspace/repo

    # Legacy rubric.yaml
    python3 judge.py /path/to/rubric.yaml /workspace/repo

Output: float score to stdout (0.0–1.0), details to stderr.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from taskforge.config import CONFIG_RE, extract_config_hunks, extract_added_lines

try:
    import yaml
except ImportError:
    yaml = None


# ── Rubric loading ────────────────────────────────────────────────────────

def load_manifest_rubric(manifest_path: str) -> list[dict]:
    """Load rubric rules (Track 3) from eval_manifest.yaml."""
    if not yaml:
        return []
    data = yaml.safe_load(Path(manifest_path).read_text())
    rules = []
    for r in (data.get("rubric") or []):
        if isinstance(r, dict):
            rules.append({
                "rule": r.get("rule", ""),
                "source": r.get("source"),
                "reference": r.get("reference"),
            })
        elif isinstance(r, str):
            rules.append({"rule": r, "source": None, "reference": None})
    return rules


def load_manifest_config_edits(manifest_path: str) -> list[dict]:
    """Load config_edits (Track 2) from eval_manifest.yaml.

    Returns list of {path, tier, gold_added, gold_removed}.
    These are deterministic gold references extracted from solve.sh.
    """
    if not yaml:
        return []
    data = yaml.safe_load(Path(manifest_path).read_text())
    edits = []
    for ce in (data.get("config_edits") or []):
        if isinstance(ce, dict):
            edits.append({
                "path": ce.get("path", ""),
                "tier": ce.get("tier", 2),
                "gold_added": ce.get("gold_added", ""),
                "gold_removed": ce.get("gold_removed", ""),
            })
    return edits


def parse_rubric(path: str) -> list[dict]:
    """Parse legacy rubric.yaml into a list of {rule, from, reference} dicts."""
    text = Path(path).read_text()
    if yaml:
        data = yaml.safe_load(text)
    else:
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
            rules.append({"rule": r, "source": None, "reference": None})
        elif isinstance(r, dict):
            rule_text = r.get("rule") or r.get("text") or r.get("id", "")
            source = r.get("from") or r.get("source")
            reference = r.get("reference")
            rules.append({"rule": rule_text, "source": source, "reference": reference})
    return rules


# ── Agent file reading ────────────────────────────────────────────────────

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


# ── Track 2: Config edit comparison ──────────────────────────────────────

def judge_config_edits(config_edits: list[dict], diff: str, api_key: str) -> tuple[float, list[dict]]:
    """Evaluate whether agent made the correct config file edits (Track 2).

    Compares agent's actual config changes against deterministic gold references
    extracted from solve.sh. Uses Gemini for semantic comparison (not exact match).

    Returns (score, per_edit_results).
    Score is fraction of gold config edits the agent correctly made.
    """
    if not config_edits:
        return 1.0, []  # No config edits expected

    agent_config_hunks = extract_config_hunks(diff)

    # Build per-file comparison
    comparisons = []
    for ce in config_edits:
        gold_path = ce["path"]
        gold_added = ce.get("gold_added", "")

        # Find agent's edit to this file
        agent_edit = ""
        for agent_path, agent_hunk in agent_config_hunks.items():
            if gold_path in agent_path or agent_path in gold_path:
                agent_edit = extract_added_lines(agent_hunk)
                break
        # Broader match: same filename
        if not agent_edit:
            fname = gold_path.rsplit("/", 1)[-1] if "/" in gold_path else gold_path
            for agent_path, agent_hunk in agent_config_hunks.items():
                if fname in agent_path:
                    agent_edit = extract_added_lines(agent_hunk)
                    break

        comparisons.append({
            "path": gold_path,
            "tier": ce.get("tier", 2),
            "gold_added": gold_added[:500],
            "agent_added": agent_edit[:500],
            "file_modified": bool(agent_edit),
        })

    # If no gold edits have content, skip LLM call
    if all(not c["gold_added"] for c in comparisons):
        # Just check file modification
        modified = sum(1 for c in comparisons if c["file_modified"])
        return modified / len(comparisons) if comparisons else 1.0, comparisons

    # Call Gemini for semantic comparison
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        # Fallback: simple file-modified check
        modified = sum(1 for c in comparisons if c["file_modified"])
        return modified / len(comparisons) if comparisons else 1.0, comparisons

    eval_text = ""
    for i, c in enumerate(comparisons):
        eval_text += f"\nFile {i+1}: {c['path']} (tier {c['tier']})\n"
        eval_text += f"  Gold added:\n    {c['gold_added'][:400]}\n"
        if c["file_modified"]:
            eval_text += f"  Agent added:\n    {c['agent_added'][:400]}\n"
        else:
            eval_text += f"  Agent: (did not modify this file)\n"

    prompt = f"""You are evaluating whether a coding agent made the correct config/documentation file edits.

The gold solution modifies certain config files (CLAUDE.md, AGENTS.md, README.md, etc.). Below is a comparison of what the gold solution added vs what the agent added to each file.

{eval_text}

For each file, decide: did the agent make a SEMANTICALLY EQUIVALENT edit?
- Same meaning in different words = PASS
- Right file, right information, different structure = PASS
- Agent didn't modify the file at all = FAIL
- Agent modified the file but with wrong/unrelated content = FAIL
- Agent added partial information (some key points missing) = PARTIAL

Respond with ONLY a JSON array:
[{{"file_num": N, "verdict": "pass|partial|fail", "reason": "one sentence"}}]"""

    try:
        results = _call_gemini(prompt, gemini_key)
    except Exception:
        # Fallback
        modified = sum(1 for c in comparisons if c["file_modified"])
        return modified / len(comparisons) if comparisons else 1.0, comparisons

    # Calculate score
    score_map = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
    total_score = 0.0
    for r in results:
        idx = r.get("file_num", 0) - 1
        verdict = r.get("verdict", "fail").lower()
        total_score += score_map.get(verdict, 0.0)
        if 0 <= idx < len(comparisons):
            comparisons[idx]["verdict"] = verdict
            comparisons[idx]["reason"] = r.get("reason", "")

    config_score = total_score / len(comparisons) if comparisons else 1.0
    return config_score, comparisons


# ── Track 3: Rubric LLM judge ───────────────────────────────────────────

def call_judge(rules: list[dict], diff: str, api_key: str) -> list[dict]:
    """Evaluate whether the agent made the right config file edits.

    Core question: "As a result of these code changes, did the agent also
    make the appropriate edits to the agent config / documentation files?
    Here's the reference edit from the gold solution."
    """
    import urllib.request

    # Extract the agent's config file changes using the same parser as gold
    agent_config_hunks = extract_config_hunks(diff)

    # Build per-file comparison: gold reference vs agent's actual diff
    eval_items = []
    for i, r in enumerate(rules):
        source_path = "unknown"
        if isinstance(r.get("source"), dict):
            source_path = r["source"].get("path", "unknown")

        # Gold reference: what the correct solution adds
        gold_ref = r.get("reference", "")

        # Agent's actual edit to this file (find best match)
        agent_edit = ""
        for agent_path, agent_hunk in agent_config_hunks.items():
            if source_path in agent_path or agent_path in source_path:
                agent_edit = extract_added_lines(agent_hunk)
                break
        # Broader match: same filename anywhere in path
        if not agent_edit:
            fname = source_path.rsplit("/", 1)[-1] if "/" in source_path else source_path
            for agent_path, agent_hunk in agent_config_hunks.items():
                if fname in agent_path:
                    agent_edit = extract_added_lines(agent_hunk)
                    break

        item = f"Check {i+1}: {r['rule']}\n  Target file: {source_path}"
        if gold_ref:
            item += f"\n  Gold solution added:\n    {gold_ref[:500]}"
        if agent_edit:
            item += f"\n  Agent added:\n    {agent_edit[:500]}"
        else:
            item += f"\n  Agent added: (nothing — file not modified)"
        eval_items.append(item)

    eval_text = "\n\n".join(eval_items)

    # Summary of which files the agent touched
    if agent_config_hunks:
        touched = ", ".join(sorted(agent_config_hunks.keys()))
    else:
        touched = "(none)"

    prompt = f"""You are evaluating whether a coding agent made the right documentation/config file edits alongside a code change.

The agent was given a task that requires both CODE changes and DOCUMENTATION updates (to files like CLAUDE.md, AGENTS.md, README.md, SKILL.md, etc.). Below is a side-by-side comparison of what the gold solution added vs what the agent actually added to each config file.

Config files the agent modified: {touched}

{eval_text}

For each check, decide: did the agent make a SEMANTICALLY EQUIVALENT edit to the right file?
- Same meaning in different words = PASS
- Right information in the right file but different structure = PASS
- Agent didn't touch the file at all = FAIL
- Agent touched the file but added unrelated/wrong content = FAIL
- Agent added partial information (some but not all key points) = FAIL if major points missing, PASS if minor wording differs

Respond with ONLY a JSON array:
[{{"rule_num": N, "pass": true/false, "reason": "one sentence"}}]"""

    # Try Gemini first (preferred), fall back to Anthropic
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        return _call_gemini(prompt, gemini_key)
    else:
        return _call_anthropic(prompt, api_key)


_JUDGE_RESULT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rule_num": {"type": "integer"},
            "rule": {"type": "string"},
            "reasoning": {"type": "string"},
            "pass": {"type": "boolean"},
        },
        "required": ["rule_num", "reasoning", "pass"],
        "propertyOrdering": ["rule_num", "rule", "reasoning", "pass"],
    },
}


def _call_gemini(prompt: str, api_key: str) -> list[dict]:
    """Call Gemini 3.1 Pro for rubric judging with structured output."""
    import urllib.request

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "responseSchema": _JUDGE_RESULT_SCHEMA,
        },
    }).encode()

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview-customtools:generateContent"
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    })

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    if not parts:
        return []

    text = parts[0].get("text", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []


def _call_anthropic(prompt: str, api_key: str) -> list[dict]:
    """Fallback: call Anthropic Claude Haiku for rubric judging."""
    import urllib.request

    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2048,
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

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())

    text = data["content"][0]["text"].strip()
    if text.startswith("["):
        return json.loads(text)
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return []


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    # Parse args
    manifest_path = None
    rubric_path = None
    repo_dir = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--manifest" and i + 1 < len(args):
            manifest_path = args[i + 1]
            i += 2
        elif args[i] == "--repo" and i + 1 < len(args):
            repo_dir = args[i + 1]
            i += 2
        elif not rubric_path:
            rubric_path = args[i]
            i += 1
        elif not repo_dir:
            repo_dir = args[i]
            i += 1
        else:
            i += 1

    if not repo_dir:
        print("Usage: judge.py --manifest <eval_manifest.yaml> --repo <repo_dir>", file=sys.stderr)
        print("   or: judge.py <rubric.yaml> <repo_dir>", file=sys.stderr)
        print("0.0")
        sys.exit(0)

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not gemini_key and not api_key:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')
                    os.environ["GEMINI_API_KEY"] = gemini_key
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"')
        if not gemini_key and not api_key:
            print("0.5", file=sys.stderr)
            print("0.5")
            sys.exit(0)

    # Get agent's work
    diff = get_diff(repo_dir)

    if not diff:
        print("0.0")  # No changes at all
        sys.exit(0)

    scores = {}

    # ── Track 2: Config edits (deterministic gold comparison) ──
    if manifest_path:
        config_edits = load_manifest_config_edits(manifest_path)
        if config_edits:
            try:
                ce_score, ce_results = judge_config_edits(config_edits, diff, api_key)
                scores["config_edits"] = ce_score
                for cr in ce_results:
                    v = cr.get("verdict", "?")
                    print(f"  Config {cr['path']}: {v} — {cr.get('reason', '')}", file=sys.stderr)
                print(f"  Config edit score: {ce_score:.2f}", file=sys.stderr)
            except Exception as e:
                print(f"  Config edit judge error: {e}", file=sys.stderr)

    # ── Track 3: Rubric rules (convention compliance) ──
    if manifest_path:
        rules = load_manifest_rubric(manifest_path)
    elif rubric_path:
        rules = parse_rubric(rubric_path)
    else:
        rules = []

    if rules:
        try:
            results = call_judge(rules, diff, api_key)
            if results:
                passed = sum(1 for r in results if r.get("pass", False))
                total = len(results)
                icr = passed / total if total > 0 else 0.5
                scores["rubric"] = icr

                for r in results:
                    status = "PASS" if r.get("pass") else "FAIL"
                    print(f"  Rule {r.get('rule_num', '?')}: {status} — {r.get('reason', '')}", file=sys.stderr)
                print(f"  Rubric ICR: {passed}/{total} = {icr:.2f}", file=sys.stderr)
        except Exception as e:
            print(f"  Rubric judge error: {e}", file=sys.stderr)

    # ── Combined score ──
    if not scores:
        print("1.0")  # No tracks to evaluate = perfect
    else:
        # Average across active tracks
        combined = sum(scores.values()) / len(scores)
        print(f"  Combined: {scores} → {combined:.2f}", file=sys.stderr)
        print(f"{combined:.4f}")


if __name__ == "__main__":
    main()
