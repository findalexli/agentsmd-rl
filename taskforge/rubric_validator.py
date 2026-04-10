#!/usr/bin/env python3
"""Rubric precision/recall validator.

Runs inside E2B sandbox (or locally) to validate rubric rules against actual
repo state. Calls Gemini to detect hallucinated rules and suggest missing ones.

Two phases:
  Phase 1 (programmatic): file existence, ±50 line extraction, context build
  Phase 2 (Gemini judge): semantic evaluation with explanations

The Gemini feedback is structured so it can be fed back to a Kimi agent
for iterative rubric improvement.

Usage (inside sandbox):
    python3 /workspace/rubric_validator.py \
        --task /workspace/task \
        --repo /workspace/repo \
        --output /workspace/rubric_feedback.json

    # Context-only (no Gemini call, just check file existence)
    python3 /workspace/rubric_validator.py \
        --task /workspace/task --repo /workspace/repo --context-only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


# ── Config file discovery ────────────────────────────────────────────────────

CONFIG_NAMES = {
    "CLAUDE.md", "AGENTS.md", "CONVENTIONS.md", "SKILL.md",
    ".cursorrules", "copilot-instructions.md",
}


def find_config_files(repo_dir: Path) -> list[dict]:
    """Find all agent config files in repo. Returns list of {path, size, preview}."""
    configs = []
    seen = set()

    for root, dirs, files in os.walk(repo_dir):
        # Skip noise
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "__pycache__", "vendor"}]
        rel_root = Path(root).relative_to(repo_dir)
        # Limit depth
        if len(rel_root.parts) > 5:
            dirs.clear()
            continue

        for fname in files:
            if fname in CONFIG_NAMES:
                full = Path(root) / fname
                rel = str(full.relative_to(repo_dir))
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    text = full.read_text(errors="replace")
                    preview = "\n".join(text.splitlines()[:5])
                    configs.append({"path": rel, "size": len(text), "preview": preview[:300]})
                except Exception:
                    configs.append({"path": rel, "size": 0, "preview": ""})

    # Also scan .claude/ directory
    claude_dir = repo_dir / ".claude"
    if claude_dir.exists():
        for md in claude_dir.rglob("*.md"):
            rel = str(md.relative_to(repo_dir))
            if rel in seen:
                continue
            seen.add(rel)
            try:
                text = md.read_text(errors="replace")
                preview = "\n".join(text.splitlines()[:5])
                configs.append({"path": rel, "size": len(text), "preview": preview[:300]})
            except Exception:
                pass

    # Also scan .cursor/rules/
    cursor_dir = repo_dir / ".cursor" / "rules"
    if cursor_dir.exists():
        for f in cursor_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(repo_dir))
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    text = f.read_text(errors="replace")
                    preview = "\n".join(text.splitlines()[:5])
                    configs.append({"path": rel, "size": len(text), "preview": preview[:300]})
                except Exception:
                    pass

    configs.sort(key=lambda c: c["path"])
    return configs


# ── Line context extraction ──────────────────────────────────────────────────

def extract_context(repo_dir: Path, file_path: str, lines_spec: str, padding: int = 50) -> dict:
    """Extract ±padding lines around cited location.

    Returns {exists, snippet, cited_text, total_lines}.
    """
    full = repo_dir / file_path
    if not full.exists():
        return {"exists": False, "snippet": "", "cited_text": "", "total_lines": 0}

    try:
        text = full.read_text(errors="replace")
    except Exception:
        return {"exists": True, "snippet": "(unreadable)", "cited_text": "", "total_lines": 0}

    all_lines = text.splitlines()
    total = len(all_lines)

    if not lines_spec:
        # No lines cited — return first 100 lines
        snippet = "\n".join(f"    {i+1}: {l}" for i, l in enumerate(all_lines[:100]))
        return {"exists": True, "snippet": snippet, "cited_text": "", "total_lines": total}

    # Parse "45" or "30-35"
    try:
        if "-" in lines_spec:
            parts = lines_spec.split("-")
            cite_start = int(parts[0])
            cite_end = int(parts[1])
        else:
            cite_start = cite_end = int(lines_spec)
    except ValueError:
        return {"exists": True, "snippet": "(invalid line spec)", "cited_text": "", "total_lines": total}

    # Bounds check
    if cite_start < 1 or cite_start > total:
        return {
            "exists": True,
            "snippet": f"(line {cite_start} out of range — file has {total} lines)",
            "cited_text": "",
            "total_lines": total,
        }

    # 0-indexed
    s_idx = max(0, cite_start - 1)
    e_idx = min(total, cite_end)
    cited_text = "\n".join(all_lines[s_idx:e_idx])

    # ±padding context
    ctx_s = max(0, s_idx - padding)
    ctx_e = min(total, e_idx + padding)
    lines_out = []
    for i in range(ctx_s, ctx_e):
        marker = ">>>" if s_idx <= i < e_idx else "   "
        lines_out.append(f"{marker} {i+1}: {all_lines[i]}")

    return {
        "exists": True,
        "snippet": "\n".join(lines_out),
        "cited_text": cited_text,
        "total_lines": total,
    }


# ── Rubric loading ───────────────────────────────────────────────────────────

def load_rubric(task_dir: Path) -> list[dict]:
    """Load rubric rules from eval_manifest.yaml."""
    manifest = task_dir / "eval_manifest.yaml"
    if not manifest.exists() or not yaml:
        return []

    data = yaml.safe_load(manifest.read_text())
    rules = []
    for r in (data.get("rubric") or []):
        if isinstance(r, dict):
            source = r.get("source") or {}
            rules.append({
                "rule": r.get("rule", ""),
                "path": source.get("path", "") if isinstance(source, dict) else "",
                "lines": str(source.get("lines", "")) if isinstance(source, dict) else "",
                "commit": source.get("commit", "") if isinstance(source, dict) else "",
                "reference": r.get("reference", ""),
            })
        elif isinstance(r, str):
            rules.append({"rule": r, "path": "", "lines": "", "commit": "", "reference": ""})
    return rules


# ── Phase 1: Programmatic checks ────────────────────────────────────────────

def phase1_check(task_dir: Path, repo_dir: Path) -> dict:
    """Build context: config inventory + per-rule file checks.

    Returns dict with all context needed for Gemini judge.
    """
    configs = find_config_files(repo_dir)
    rules = load_rubric(task_dir)

    # Read solve.sh for judge context
    solve_path = task_dir / "solution" / "solve.sh"
    solve_text = solve_path.read_text()[:3000] if solve_path.exists() else ""

    # Read instruction.md
    instr_path = task_dir / "instruction.md"
    instruction = instr_path.read_text()[:2000] if instr_path.exists() else ""

    rule_checks = []
    for i, r in enumerate(rules):
        check = {
            "idx": i + 1,
            "rule": r["rule"],
            "source_path": r["path"],
            "source_lines": r["lines"],
            "reference": r.get("reference", ""),
        }

        if r["path"]:
            ctx = extract_context(repo_dir, r["path"], r["lines"], padding=50)
            check["file_exists"] = ctx["exists"]
            check["file_total_lines"] = ctx["total_lines"]
            check["context_snippet"] = ctx["snippet"][:4000]
            check["cited_text"] = ctx["cited_text"][:1000]

            # Quick programmatic verdict
            if not ctx["exists"]:
                check["p1_verdict"] = "file_missing"
            elif r["lines"] and not ctx["cited_text"]:
                check["p1_verdict"] = "lines_out_of_range"
            else:
                check["p1_verdict"] = "needs_semantic_check"
        else:
            check["file_exists"] = False
            check["p1_verdict"] = "no_source_cited"
            check["context_snippet"] = ""
            check["cited_text"] = ""

        rule_checks.append(check)

    return {
        "config_inventory": configs,
        "rule_checks": rule_checks,
        "solve_sh": solve_text,
        "instruction": instruction,
        "num_rules": len(rules),
    }


# ── Phase 2: Gemini judge ───────────────────────────────────────────────────

def phase2_gemini_judge(context: dict, gemini_key: str) -> dict:
    """Call Gemini 3.1 Pro to evaluate rubric precision + recall.

    Returns structured feedback with per-rule verdicts and explanations
    suitable for feeding back to a Kimi agent.
    """
    import urllib.request

    # Build [1]: config file inventory
    inventory = "## Config Files in Repo (post-gold-patch)\n\n"
    for c in context["config_inventory"]:
        inventory += f"- **{c['path']}** ({c['size']}b)\n"
        if c["preview"]:
            inventory += f"  ```\n  {c['preview'][:200]}\n  ```\n"
    if not context["config_inventory"]:
        inventory += "(none found)\n"

    # Build [2]: per-rule context with ±50 lines
    rules_section = ""
    for rc in context["rule_checks"]:
        rules_section += f"\n### Rule {rc['idx']}: {rc['rule']}\n"
        rules_section += f"- Source: `{rc['source_path']}` lines `{rc['source_lines']}`\n"
        rules_section += f"- File exists: {rc.get('file_exists', False)}\n"
        rules_section += f"- Phase 1 check: {rc['p1_verdict']}\n"

        if rc.get("reference"):
            rules_section += f"- Gold reference:\n```\n{rc['reference'][:500]}\n```\n"

        if rc.get("file_exists") and rc.get("context_snippet"):
            rules_section += f"- Context (±50 lines, `>>>` = cited lines):\n```\n{rc['context_snippet'][:3000]}\n```\n"
        elif not rc.get("file_exists") and rc["source_path"]:
            rules_section += f"- **FILE DOES NOT EXIST**: `{rc['source_path']}`\n"

        if rc.get("cited_text"):
            rules_section += f"- Exact cited text:\n```\n{rc['cited_text'][:500]}\n```\n"
        rules_section += "\n"

    prompt = f"""You are a rubric quality auditor for a software engineering benchmark.

Each rubric rule claims to come from an agent config file (CLAUDE.md, AGENTS.md, etc.) in the repository. You must check each rule for precision (is it real?) and assess recall (are important rules missing?).

**KEY DISTINCTION**: Rules must cite PRE-EXISTING conventions from config files. Rules that merely describe what the gold solution (solve.sh) does are REDUNDANT — they belong as hard test checks, not rubric rules. The gold patch may also ADD new content to config files (for agentmd-edit tasks) — rules about those additions need a `reference` field.

{inventory}

## Gold Solution
```bash
{context['solve_sh'][:2000]}
```

## Task Description
{context['instruction'][:1000]}

{rules_section}

## Your Job

For each rule, determine:
1. **SOURCE CHECK**: Does the file exist? Do cited lines contain related content?
2. **PRE-EXISTING vs REDUNDANT**: Is this a standing convention from BEFORE the PR, or does it just describe what solve.sh does?
3. **HALLUCINATION CHECK**: Did the agent fabricate a rule not actually in any config file?
4. **EVALUABILITY**: Could a judge reading the agent's diff + this rule give PASS/FAIL?

For each rule, provide:
- `verdict`: "accurate", "partial", "hallucinated", or "redundant"
- `explanation`: 2-3 sentences explaining WHY this verdict. Be specific: quote the actual cited lines vs what the rule claims. This explanation will be shown to another agent to fix the rule.
- `fix_suggestion`: If hallucinated/redundant, what should be done (remove, rewrite with correct source, convert to hard check)

Also assess RECALL: are there specific, evaluable conventions in the config files that apply to this PR's changes but are NOT in the rubric?

Respond with ONLY a JSON object:
{{
  "rules": [
    {{
      "rule_num": 1,
      "verdict": "accurate|partial|hallucinated|redundant",
      "explanation": "Detailed explanation of why. Quote actual file content vs rule claim.",
      "fix_suggestion": "remove|rewrite: ...|keep|convert_to_check"
    }}
  ],
  "recall": {{
    "missing_rules": [
      {{"rule": "specific rule text", "source_path": "file.md", "source_lines": "N-M", "rationale": "why this applies"}}
    ],
    "notes": "overall recall assessment"
  }},
  "precision_score": 0.75,
  "summary": "one-sentence overall quality assessment"
}}"""

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
        },
    }).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview-customtools:generateContent?key={gemini_key}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Parse JSON (Gemini may wrap in markdown)
    if "```" in text:
        start = text.find("```json")
        if start >= 0:
            start = text.find("\n", start) + 1
        else:
            start = text.find("```") + 3
            start = text.find("\n", start) + 1
        end = text.find("```", start)
        text = text[start:end].strip()

    if text.startswith("{"):
        return json.loads(text)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"error": "failed to parse Gemini response", "raw": text[:500]}


# ── Full validation ──────────────────────────────────────────────────────────

def validate(task_dir: Path, repo_dir: Path, gemini_key: str = "",
             context_only: bool = False) -> dict:
    """Full validation: phase 1 + phase 2.

    Returns structured feedback dict ready for Kimi agent or human review.
    """
    context = phase1_check(task_dir, repo_dir)

    if not context["rule_checks"]:
        return {"status": "no_rules", "num_rules": 0}

    # Phase 1 summary
    p1_results = []
    for rc in context["rule_checks"]:
        p1_results.append({
            "rule_num": rc["idx"],
            "rule": rc["rule"],
            "source_path": rc["source_path"],
            "file_exists": rc.get("file_exists", False),
            "p1_verdict": rc["p1_verdict"],
        })

    if context_only:
        return {
            "status": "context_only",
            "num_rules": context["num_rules"],
            "config_files": [c["path"] for c in context["config_inventory"]],
            "phase1": p1_results,
        }

    if not gemini_key:
        return {
            "status": "no_gemini_key",
            "phase1": p1_results,
        }

    # Phase 2: Gemini judge
    try:
        gemini_result = phase2_gemini_judge(context, gemini_key)
    except Exception as e:
        return {
            "status": "gemini_error",
            "error": str(e)[:300],
            "phase1": p1_results,
        }

    # Merge results
    output = {
        "status": "complete",
        "num_rules": context["num_rules"],
        "config_files": [c["path"] for c in context["config_inventory"]],
        "precision_score": gemini_result.get("precision_score", 0),
        "summary": gemini_result.get("summary", ""),
        "rules": gemini_result.get("rules", []),
        "recall": gemini_result.get("recall", {}),
        "phase1": p1_results,
    }

    return output


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rubric precision/recall validator")
    parser.add_argument("--task", required=True, help="Task directory path")
    parser.add_argument("--repo", required=True, help="Repo directory path (at base or post-gold commit)")
    parser.add_argument("--output", help="Write JSON result to this file")
    parser.add_argument("--context-only", action="store_true", help="Skip Gemini, just check files")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    result = validate(
        Path(args.task),
        Path(args.repo),
        gemini_key=gemini_key,
        context_only=args.context_only,
    )

    output = json.dumps(result, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        # Also print summary to stdout
        print(f"Status: {result.get('status')}")
        print(f"Precision: {result.get('precision_score', 'n/a')}")
        print(f"Summary: {result.get('summary', 'n/a')}")
        for rv in result.get("rules", []):
            v = rv.get("verdict", "?").upper()
            print(f"  Rule {rv.get('rule_num')}: [{v}] {rv.get('explanation', '')[:100]}")
    else:
        print(output)


if __name__ == "__main__":
    main()
