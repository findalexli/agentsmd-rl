#!/usr/bin/env python3
"""Hierarchical agent config context extractor.

For each task, builds the FULL config context an agent would see:
1. Config hierarchy: all AGENTS.md/CLAUDE.md from root → edited file directories
2. Relevant skills: matched by proximity + description to the PR's changed files
3. Positive rubrics: rules the gold solution FOLLOWS
4. Negative rubrics / distractors: rules that SEEM relevant but gold IGNORES

The PR author's choices (what they follow vs ignore) are the ground truth signal.

Usage:
    # Single task
    python -m taskforge.hierarchy_context --task harbor_tasks_agentmd_edits/opencode-acp-question-tool-flag

    # Batch scan
    python -m taskforge.hierarchy_context --task-dir harbor_tasks_agentmd_edits --limit 10
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError:
    yaml = None


# ── Config file discovery with hierarchy ─────────────────────────────────────

CONFIG_FILENAMES = {
    "CLAUDE.md", "AGENTS.md", "CONVENTIONS.md",
    ".cursorrules", "copilot-instructions.md",
}

SKILL_FILENAME = "SKILL.md"


def extract_edited_paths(task_dir: Path) -> list[str]:
    """Extract file paths edited by the gold solution from solve.sh."""
    solve = task_dir / "solution" / "solve.sh"
    if not solve.exists():
        return []

    text = solve.read_text()
    paths = set()

    # From git apply patches
    for m in re.finditer(r'diff --git a/(\S+) b/(\S+)', text):
        paths.add(m.group(2))

    # From sed -i commands (last arg is the file)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("sed ") and "-i" in line:
            tokens = line.split()
            for tok in reversed(tokens):
                tok = tok.strip("'\"")
                if "/" in tok or tok.endswith((".ts", ".py", ".rs", ".go", ".md", ".yml", ".json")):
                    # Clean workspace prefix
                    clean = re.sub(r"^/workspace/[^/]+/", "", tok)
                    paths.add(clean)
                    break

    return sorted(paths)


def build_directory_set(edited_paths: list[str]) -> set[str]:
    """Get all directories in the path from root to each edited file."""
    dirs = {""}  # root
    for p in edited_paths:
        parts = PurePosixPath(p).parent.parts
        for i in range(len(parts)):
            dirs.add("/".join(parts[:i+1]))
    return dirs


def find_config_hierarchy(repo_dir: Path, edited_paths: list[str]) -> list[dict]:
    """Find ALL config files in the hierarchy from root → edited file directories.

    Returns list of {path, level, content, applies_to} sorted by depth.
    Level 0 = root, higher = deeper in the tree.
    """
    target_dirs = build_directory_set(edited_paths)
    configs = []

    # Walk the repo looking for config files in relevant directories
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "__pycache__", "vendor", "dist"}]
        rel_root = str(Path(root).relative_to(repo_dir))
        if rel_root == ".":
            rel_root = ""

        # Check if this directory is in the path to any edited file
        is_relevant = rel_root in target_dirs
        # Also check if it's an ancestor of a relevant directory
        is_ancestor = any(td.startswith(rel_root + "/") or td == rel_root for td in target_dirs)

        if not is_relevant and not is_ancestor and rel_root:
            continue

        for fname in files:
            if fname in CONFIG_FILENAMES:
                full = Path(root) / fname
                rel = str(full.relative_to(repo_dir))
                level = len(PurePosixPath(rel).parent.parts)
                try:
                    content = full.read_text(errors="replace")
                except Exception:
                    content = ""

                # Which edited files does this config apply to?
                applies_to = []
                for ep in edited_paths:
                    ep_dir = str(PurePosixPath(ep).parent)
                    if ep_dir.startswith(rel_root) or rel_root == "":
                        applies_to.append(ep)

                configs.append({
                    "path": rel,
                    "level": level,
                    "content": content,
                    "applies_to": applies_to,
                    "directory": rel_root or "(root)",
                })

    configs.sort(key=lambda c: c["level"])
    return configs


def find_relevant_skills(repo_dir: Path, edited_paths: list[str]) -> list[dict]:
    """Find ALL skills in the repo and classify as relevant/irrelevant.

    A skill is relevant if:
    - Its directory is in the path to an edited file
    - Its description mentions concepts related to the edited files
    - It's in .claude/skills/ or similar skill directories
    """
    skills = []
    skill_dirs = [".claude/skills", ".agents/skills", ".github/skills",
                  "skills", ".opencode/skill"]

    for sd in skill_dirs:
        skill_root = repo_dir / sd
        if not skill_root.exists():
            continue

        for skill_dir in skill_root.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / SKILL_FILENAME
            if not skill_md.exists():
                continue

            try:
                content = skill_md.read_text(errors="replace")
            except Exception:
                continue

            # Parse frontmatter
            name = skill_dir.name
            description = ""
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    fm = content[3:end]
                    for line in fm.splitlines():
                        if line.strip().startswith("description:"):
                            description = line.split(":", 1)[1].strip().strip('"\'')
                        elif line.strip().startswith("name:"):
                            name = line.split(":", 1)[1].strip().strip('"\'')

            rel_path = str(skill_dir.relative_to(repo_dir))

            # Heuristic relevance: does the skill description/name relate to edited file types?
            edited_extensions = {PurePosixPath(p).suffix for p in edited_paths}
            edited_dirs = {str(PurePosixPath(p).parent) for p in edited_paths}

            relevance_signals = []
            desc_lower = (description + " " + name + " " + content[:500]).lower()
            if any(ext in desc_lower for ext in [".ts", "typescript", "javascript", ".js"]):
                if any(e in {".ts", ".tsx", ".js", ".jsx"} for e in edited_extensions):
                    relevance_signals.append("language_match")
            if any(ext in desc_lower for ext in [".py", "python"]):
                if any(e in {".py"} for e in edited_extensions):
                    relevance_signals.append("language_match")
            if any(ext in desc_lower for ext in [".rs", "rust", "cargo"]):
                if any(e in {".rs"} for e in edited_extensions):
                    relevance_signals.append("language_match")
            if any(kw in desc_lower for kw in ["test", "testing", "spec"]):
                if any("test" in p.lower() for p in edited_paths):
                    relevance_signals.append("testing_match")
            if any(kw in desc_lower for kw in ["review", "pr", "pull request"]):
                relevance_signals.append("pr_review")
            if any(kw in desc_lower for kw in ["build", "compile", "deploy"]):
                relevance_signals.append("build_match")

            skills.append({
                "name": name,
                "path": rel_path,
                "description": description[:200],
                "relevance_signals": relevance_signals,
                "is_relevant": len(relevance_signals) > 0,
                "content_preview": content[:500],
            })

    return skills


# ── Positive vs Negative rubric classification ───────────────────────────────

def extract_rules_from_config(config_content: str) -> list[str]:
    """Extract individual rules/instructions from a config file.

    Looks for bullet points, numbered lists, and imperative statements.
    """
    rules = []
    for line in config_content.splitlines():
        line = line.strip()
        # Bullet points
        if line.startswith("- ") and len(line) > 10:
            rules.append(line[2:].strip())
        # Numbered lists
        elif re.match(r'^\d+\.\s', line) and len(line) > 10:
            rules.append(re.sub(r'^\d+\.\s+', '', line).strip())
    return rules


def build_hierarchy_context(task_dir: Path, repo_dir: Path) -> dict:
    """Build complete hierarchical context for a task.

    Returns {
        edited_paths, config_hierarchy, skills,
        total_rules, hierarchy_depth, potential_conflicts
    }
    """
    edited_paths = extract_edited_paths(task_dir)
    config_hierarchy = find_config_hierarchy(repo_dir, edited_paths)
    skills = find_relevant_skills(repo_dir, edited_paths)

    # Count total rules across all config files
    total_rules = 0
    all_rules_by_level = {}
    for cfg in config_hierarchy:
        rules = extract_rules_from_config(cfg["content"])
        total_rules += len(rules)
        all_rules_by_level[cfg["path"]] = rules

    # Identify potential conflicts: same topic at different levels
    # (simplified: look for rules with overlapping keywords)
    potential_conflicts = []
    paths = list(all_rules_by_level.keys())
    for i, p1 in enumerate(paths):
        for p2 in paths[i+1:]:
            for r1 in all_rules_by_level[p1]:
                for r2 in all_rules_by_level[p2]:
                    # Very rough conflict detection: same key terms
                    words1 = set(r1.lower().split())
                    words2 = set(r2.lower().split())
                    overlap = words1 & words2 - {"the", "a", "an", "and", "or", "is", "to", "in", "for", "of", "with"}
                    if len(overlap) >= 3 and r1 != r2:
                        potential_conflicts.append({
                            "file1": p1, "rule1": r1[:100],
                            "file2": p2, "rule2": r2[:100],
                            "shared_terms": list(overlap)[:5],
                        })

    return {
        "edited_paths": edited_paths,
        "config_hierarchy": [{
            "path": c["path"],
            "level": c["level"],
            "directory": c["directory"],
            "applies_to": c["applies_to"],
            "rule_count": len(all_rules_by_level.get(c["path"], [])),
            "content_length": len(c["content"]),
        } for c in config_hierarchy],
        "config_contents": {c["path"]: c["content"][:5000] for c in config_hierarchy},
        "skills": [{
            "name": s["name"],
            "path": s["path"],
            "description": s["description"],
            "is_relevant": s["is_relevant"],
            "relevance_signals": s["relevance_signals"],
        } for s in skills],
        "total_config_rules": total_rules,
        "hierarchy_depth": max((c["level"] for c in config_hierarchy), default=0),
        "potential_conflicts": potential_conflicts[:10],
        "relevant_skills": sum(1 for s in skills if s["is_relevant"]),
        "distractor_skills": sum(1 for s in skills if not s["is_relevant"]),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Hierarchical config context extractor")
    parser.add_argument("--task", help="Single task directory")
    parser.add_argument("--task-dir", help="Parent directory for batch")
    parser.add_argument("--repo", help="Repo directory (overrides auto-clone)")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.task:
        task_dir = Path(args.task)
        if args.repo:
            repo_dir = Path(args.repo)
        else:
            print("--repo required (path to cloned repo at base commit)")
            sys.exit(1)

        result = build_hierarchy_context(task_dir, repo_dir)
        output = json.dumps(result, indent=2)

        if args.output:
            Path(args.output).write_text(output)
        else:
            print(output)

    elif args.task_dir:
        print("Batch mode requires E2B sandbox (repo clone per task). Use single --task mode.")
        sys.exit(1)


if __name__ == "__main__":
    main()
