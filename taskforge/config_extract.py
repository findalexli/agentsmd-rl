#!/usr/bin/env python3
"""Extract gold config changes from solve.sh at scaffold time.

For agentmd-edit tasks, the gold solution modifies both code files AND
config/doc files (AGENTS.md, CLAUDE.md, etc.). This module extracts
the config changes as structured data for deterministic comparison
at eval time — no LLM needed for the gold reference.

Usage:
    # At scaffold time: extract gold config changes
    python -m taskforge.config_extract --task harbor_tasks_agentmd_edits/taskname

    # At eval time: compare agent's changes against gold
    python -m taskforge.config_extract --compare \
        --task ... --agent-diff /path/to/agent.diff

Output: gold_config.json in the task directory:
    {
        "files": {
            "AGENTS.md": {
                "added": "## Writing Standards\\nSee style guide...",
                "removed": "",
                "context_before": "...lines before the change...",
                "context_after": "...lines after the change..."
            }
        },
        "summary": "Modified AGENTS.md and CONTRIBUTING.md"
    }
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from taskforge.config import (
    CONFIG_RE, AGENT_INSTRUCTION_RE, DOC_RE,
    extract_config_hunks, extract_added_lines,
    is_config_file, is_agent_instruction_file,
)


def extract_gold_config(task_dir: Path) -> dict:
    """Extract config file changes from solve.sh by diffing before/after.

    Runs solve.sh inside Docker (if Dockerfile exists) or parses the patch
    commands directly. Returns structured config changes.
    """
    solve_sh = task_dir / "solution" / "solve.sh"
    if not solve_sh.exists():
        return {"files": {}, "error": "no solve.sh"}

    solve_text = solve_sh.read_text()

    # Strategy 1: Parse git apply / git diff patches directly from solve.sh
    config_changes = _parse_patches_from_solve(solve_text)

    # Strategy 2: Parse sed commands that modify config/doc files
    sed_changes = _parse_sed_commands(solve_text)
    for path, change in sed_changes.items():
        if path not in config_changes:
            config_changes[path] = change
        else:
            config_changes[path]["added"] += "\n" + change.get("added", "")

    # Strategy 3: Parse heredoc writes (cat > file << EOF) and echo >> redirects
    heredoc_changes = _parse_heredoc_writes(solve_text)
    for path, change in heredoc_changes.items():
        if path not in config_changes:
            config_changes[path] = change
        else:
            config_changes[path]["added"] += "\n" + change.get("added", "")

    if not config_changes:
        return {"files": {}, "summary": "no config file changes in solve.sh"}

    summary_files = sorted(config_changes.keys())
    tier1 = [f for f in summary_files if is_agent_instruction_file(f)]
    tier2 = [f for f in summary_files if not is_agent_instruction_file(f)]

    summary_parts = []
    if tier1:
        summary_parts.append(f"Tier 1 (agent config): {', '.join(tier1)}")
    if tier2:
        summary_parts.append(f"Tier 2 (docs): {', '.join(tier2)}")

    return {
        "files": config_changes,
        "summary": "; ".join(summary_parts),
        "tier1_count": len(tier1),
        "tier2_count": len(tier2),
    }


def _parse_patches_from_solve(solve_text: str) -> dict[str, dict]:
    """Extract config file changes from git apply/diff patches in solve.sh."""
    changes: dict[str, dict] = {}

    # Find all inline patches (heredoc or echo'd)
    # Pattern: git apply ... <<'PATCH' ... PATCH
    patch_blocks = re.findall(
        r"git apply[^\n]*<<['\"]?(\w+)['\"]?\n(.*?)^\1",
        solve_text,
        re.MULTILINE | re.DOTALL,
    )

    for _delimiter, patch_text in patch_blocks:
        hunks = extract_config_hunks(patch_text)
        for filepath, hunk in hunks.items():
            added = extract_added_lines(hunk)
            removed = _extract_removed_lines(hunk)
            if added or removed:
                changes[filepath] = {
                    "added": added,
                    "removed": removed,
                    "hunk": hunk[:2000],
                }

    return changes


def _extract_removed_lines(hunk: str) -> str:
    """Get removed lines from a diff hunk."""
    return "\n".join(
        line[1:] for line in hunk.split("\n")
        if line.startswith("-") and not line.startswith("---")
    ).strip()


def _parse_sed_commands(solve_text: str) -> dict[str, dict]:
    """Extract ALL non-code file changes from sed commands in solve.sh.

    For agentmd-edit tasks, config files may have non-standard names
    (e.g., .opencode/agent/translator.md). We capture ALL .md file edits
    and anything matching config patterns, not just standard names.
    """
    changes: dict[str, dict] = {}

    # Match sed -i 'expr' filepath  (handles both single-quoted and double-quoted)
    # The key: match from the LAST unquoted token as the filepath
    for line in solve_text.splitlines():
        line = line.strip()
        if not line.startswith("sed ") or "-i" not in line:
            continue

        # Extract the target file (last non-option argument)
        # Strategy: find all tokens, last one that looks like a path is the target
        tokens = line.split()
        target = ""
        for tok in reversed(tokens):
            tok = tok.strip("'\"")
            if "/" in tok or tok.endswith(".md") or tok.endswith(".txt") or tok.endswith(".yml"):
                target = tok
                break

        if not target:
            continue

        # For agentmd tasks: capture ALL .md files + anything matching config patterns
        is_md = target.endswith(".md") or target.endswith(".mdc")
        if not is_md and not is_config_file(target):
            continue

        # Extract what's being added
        added_text = ""
        # Append after pattern: /pattern/a\text
        append_match = re.search(r"/[^/]*/a\\(.+)", line)
        if append_match:
            added_text = append_match.group(1).strip()

        # Substitution: s/old/new/
        if not added_text:
            subst_match = re.search(r"s[/|](.*?)[/|](.*?)[/|]", line)
            if subst_match:
                added_text = subst_match.group(2)

        # Insert after: /pattern/i\text
        if not added_text:
            insert_match = re.search(r"/[^/]*/i\\(.+)", line)
            if insert_match:
                added_text = insert_match.group(1).strip()

        if added_text or is_config_file(target):
            # Clean path: remove /workspace/<repo>/ prefix
            clean = re.sub(r"^/workspace/[^/]+/", "", target)
            changes[clean] = {
                "added": added_text[:1000],
                "removed": "",
                "sed_command": line[:300],
            }

    return changes


def _parse_heredoc_writes(solve_text: str) -> dict[str, dict]:
    """Extract config file changes from cat/tee heredocs and echo redirects."""
    changes: dict[str, dict] = {}

    # cat > file << 'EOF' ... EOF
    heredoc_pattern = re.compile(
        r"(?:cat|tee)\s+(?:>>?)\s+([^\s<]+)\s*<<\s*['\"]?(\w+)['\"]?\n(.*?)^\2",
        re.MULTILINE | re.DOTALL,
    )
    for match in heredoc_pattern.finditer(solve_text):
        target = match.group(1).strip("'\"")
        content = match.group(3).strip()
        is_md = target.endswith(".md") or target.endswith(".mdc")
        if is_md or is_config_file(target):
            clean = re.sub(r"^/workspace/[^/]+/", "", target)
            changes[clean] = {"added": content[:2000], "removed": ""}

    # echo "text" >> file
    echo_pattern = re.compile(r"echo\s+['\"](.+?)['\"]\s*>>\s*(\S+)")
    for match in echo_pattern.finditer(solve_text):
        content = match.group(1)
        target = match.group(2).strip("'\"")
        is_md = target.endswith(".md") or target.endswith(".mdc")
        if is_md or is_config_file(target):
            clean = re.sub(r"^/workspace/[^/]+/", "", target)
            if clean in changes:
                changes[clean]["added"] += "\n" + content
            else:
                changes[clean] = {"added": content[:1000], "removed": ""}

    return changes


def compare_config_changes(
    gold: dict,
    agent_diff: str,
) -> dict:
    """Compare agent's config changes against gold config changes.

    Returns per-file comparison results suitable for Gemini judge.
    """
    gold_files = gold.get("files", {})
    agent_hunks = extract_config_hunks(agent_diff)

    comparisons = []
    for gold_path, gold_change in gold_files.items():
        # Find matching agent hunk
        agent_edit = ""
        matched_path = ""
        for agent_path, agent_hunk in agent_hunks.items():
            if gold_path in agent_path or agent_path in gold_path:
                agent_edit = extract_added_lines(agent_hunk)
                matched_path = agent_path
                break
        # Broader match: same filename
        if not agent_edit:
            fname = gold_path.rsplit("/", 1)[-1] if "/" in gold_path else gold_path
            for agent_path, agent_hunk in agent_hunks.items():
                if fname in agent_path:
                    agent_edit = extract_added_lines(agent_hunk)
                    matched_path = agent_path
                    break

        comparisons.append({
            "gold_path": gold_path,
            "agent_path": matched_path or "(not modified)",
            "gold_added": gold_change.get("added", "")[:500],
            "agent_added": agent_edit[:500],
            "file_modified": bool(agent_edit),
            "tier": "tier1" if is_agent_instruction_file(gold_path) else "tier2",
        })

    # Check for extra config files the agent modified but gold didn't
    gold_names = {p.rsplit("/", 1)[-1] if "/" in p else p for p in gold_files}
    for agent_path in agent_hunks:
        agent_name = agent_path.rsplit("/", 1)[-1] if "/" in agent_path else agent_path
        already_matched = any(c["agent_path"] == agent_path for c in comparisons)
        if not already_matched and agent_name not in gold_names:
            comparisons.append({
                "gold_path": "(not in gold)",
                "agent_path": agent_path,
                "gold_added": "",
                "agent_added": extract_added_lines(agent_hunks[agent_path])[:500],
                "file_modified": True,
                "tier": "extra",
            })

    return {
        "comparisons": comparisons,
        "gold_files": list(gold_files.keys()),
        "agent_files": list(agent_hunks.keys()),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract/compare config changes")
    parser.add_argument("--task", required=True, help="Task directory")
    parser.add_argument("--compare", action="store_true", help="Compare mode")
    parser.add_argument("--agent-diff", help="Path to agent's diff file")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    task_dir = Path(args.task)

    if args.compare:
        # Load gold config
        gold_path = task_dir / "gold_config.json"
        if not gold_path.exists():
            gold = extract_gold_config(task_dir)
        else:
            gold = json.loads(gold_path.read_text())

        if args.agent_diff:
            agent_diff = Path(args.agent_diff).read_text()
        else:
            agent_diff = sys.stdin.read()

        result = compare_config_changes(gold, agent_diff)
    else:
        result = extract_gold_config(task_dir)
        # Save to task dir
        out_path = task_dir / "gold_config.json"
        out_path.write_text(json.dumps(result, indent=2))
        print(f"Extracted to {out_path}", file=sys.stderr)

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
