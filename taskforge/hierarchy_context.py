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


def _parse_skill_frontmatter(content: str) -> tuple[str, str, dict]:
    """Parse SKILL.md frontmatter. Returns (name, description, all_fields).

    Frontmatter fields: name, description, allowed-tools,
    disable-model-invocation, user-invocable, argument-hint.
    """
    name = ""
    description = ""
    fields: dict = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            fm_text = content[3:end]
            for line in fm_text.splitlines():
                line = line.strip()
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    fields[key] = val
                    if key == "description":
                        description = val
                    elif key == "name":
                        name = val
    return name, description, fields


def _skill_body(content: str) -> str:
    """Extract the body (post-frontmatter) from a SKILL.md file."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            return content[end + 3:].strip()
    return content.strip()


def find_relevant_skills(repo_dir: Path, edited_paths: list[str]) -> list[dict]:
    """Find ALL skills in the repo and classify as relevant/irrelevant.

    Returns full skill content (body) for relevant skills so rubric constructor
    can extract rules from them. Irrelevant skills get description-only.

    Relevance is determined by:
    - Path proximity: skill is in a parent directory of an edited file
    - Language match: skill mentions the same language/framework as edited files
    - Domain match: skill name/description overlaps with edited directories
    - NOT pr_review or workflow-only skills (these are agent-internal, not code rules)

    Progressive context disclosure (matching Claude Code's model):
    - All skills: name + description (cheap, for distractor selection)
    - Relevant skills: full body content (for rubric rule extraction)
    """
    skills = []

    # Standard skill directories at repo root
    skill_roots = [".claude/skills", ".agents/skills", ".github/skills",
                   "skills", ".opencode/skill", ".agent/skills"]

    # Also scan for package-scoped skills: packages/*/skills/, packages/*/.claude/skills/
    # These are common in monorepos (TanStack/router, trpc, reduxjs)
    for pattern in ["packages/*/skills", "packages/*/.claude/skills",
                    "packages/*/skills/*/skills"]:
        import glob
        for match in glob.glob(str(repo_dir / pattern)):
            rel = str(Path(match).relative_to(repo_dir))
            if rel not in skill_roots:
                skill_roots.append(rel)

    edited_extensions = {PurePosixPath(p).suffix for p in edited_paths}
    edited_dirs = {str(PurePosixPath(p).parent) for p in edited_paths}
    edited_dirs_lower = {d.lower() for d in edited_dirs}

    for sd in skill_roots:
        skill_root = repo_dir / sd
        if not skill_root.exists():
            continue

        # Walk recursively — skills can be nested (skills/lifecycle/migrate-from-nextjs/)
        for skill_md in skill_root.rglob(SKILL_FILENAME):
            skill_dir = skill_md.parent
            try:
                content = skill_md.read_text(errors="replace")
            except Exception:
                continue

            fm_name, description, fm_fields = _parse_skill_frontmatter(content)
            name = fm_name or skill_dir.name
            body = _skill_body(content)
            rel_path = str(skill_md.relative_to(repo_dir))

            # ── Relevance scoring (weighted, not boolean) ──
            # SkillRouter finding: full body text is critical, but we need to be
            # selective about WHICH skills get full body treatment.
            # SkillsBench finding: focused skills > broad docs; wrong skills hurt.
            #
            # Scoring: domain_match=3, path_proximity=2, language_match=1, testing=1
            # Threshold: score >= 2 = relevant (gets full body sent to Gemini)
            relevance_signals = []
            relevance_score = 0
            desc_lower = (description + " " + name).lower()
            body_lower = body[:800].lower()

            # Domain match: skill name keywords match edited directory keywords (STRONG)
            name_words = set(re.split(r'[-_/]', name.lower())) - {"skill", "dev", "development", "guide"}
            for ed in edited_dirs_lower:
                ed_words = set(re.split(r'[-_/.]', ed)) - {"src", "lib", "test", "tests", "index", "crates", "packages"}
                overlap = name_words & ed_words
                if overlap:
                    relevance_signals.append(f"domain_match:{','.join(overlap)}")
                    relevance_score += 3
                    break

            # Path proximity: skill and edited file share a PACKAGE prefix
            # (NOT just .claude/skills/ — that's the skill container, not a real package)
            skill_parent = str(skill_dir.relative_to(repo_dir)).lower()
            skill_parts = skill_parent.split("/")
            # Skip root-level skill dirs (e.g., .claude/skills/foo — no package proximity)
            if skill_parts[0] not in {".claude", ".agents", ".github", "skills", ".opencode", ".agent"}:
                for ed in edited_dirs_lower:
                    ed_parts = ed.split("/")
                    if len(skill_parts) >= 2 and len(ed_parts) >= 2:
                        if skill_parts[0] == ed_parts[0] and skill_parts[1] == ed_parts[1]:
                            relevance_signals.append("path_proximity")
                            relevance_score += 2
                            break

            # Description mentions specific edited file paths or modules
            for ep in edited_paths:
                ep_stem = PurePosixPath(ep).stem.lower().replace("_", " ").replace("-", " ")
                if len(ep_stem) > 3 and ep_stem in desc_lower:
                    relevance_signals.append(f"description_mentions:{ep_stem}")
                    relevance_score += 3
                    break

            # Language match (WEAK — too broad for monorepos, only a tiebreaker)
            lang_pairs = [
                ([".ts", "typescript", "javascript", ".js", "react", "jsx", "tsx"],
                 {".ts", ".tsx", ".js", ".jsx"}),
                ([".py", "python", "django", "flask", "pytest"],
                 {".py"}),
                ([".rs", "rust", "cargo", "clippy"],
                 {".rs"}),
                ([".go", "golang"],
                 {".go"}),
                ([".java", "kotlin", ".kt"],
                 {".java", ".kt", ".kts"}),
            ]
            for keywords, extensions in lang_pairs:
                if any(kw in desc_lower for kw in keywords):
                    if edited_extensions & extensions:
                        relevance_signals.append("language_match")
                        relevance_score += 1
                        break

            # Testing skill + test files edited (WEAK — almost everything mentions tests)
            if any(kw in desc_lower for kw in ["test", "testing", "spec", "snapshot"]):
                if any("test" in p.lower() for p in edited_paths):
                    relevance_signals.append("testing_match")
                    relevance_score += 1

            # Filter: workflow-only skills (PR creation, commit, changelog, CI, triage)
            # These govern agent behavior, not code conventions
            workflow_keywords = {
                "pull request", "pr review", "create pr", "commit msg",
                "changelog", "cherry-pick", "release note", "triage",
                "changeset", "pr description", "pr template",
                "opening a pr", "ci debug", "backport",
            }
            code_convention_keywords = {
                "code style", "naming", "import", "type annotation", "error handling",
                "must", "never", "always", "prefer", "avoid", "pattern",
            }
            is_workflow_only = (
                any(kw in desc_lower for kw in workflow_keywords)
                and not any(kw in body_lower for kw in code_convention_keywords)
            )

            # Threshold: score >= 2 = relevant (domain_match alone, or path+language)
            is_relevant = relevance_score >= 2 and not is_workflow_only

            skills.append({
                "name": name,
                "path": rel_path,
                "description": description[:300],
                "frontmatter": fm_fields,
                "relevance_signals": relevance_signals,
                "relevance_score": relevance_score,
                "is_relevant": is_relevant,
                "is_workflow_only": is_workflow_only,
                # Full body for relevant skills (rubric extraction)
                # Description-only for irrelevant (distractor selection)
                "body": body[:6000] if is_relevant else "",
                "body_length": len(body),
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
            "is_workflow_only": s.get("is_workflow_only", False),
            "relevance_signals": s["relevance_signals"],
            "body": s.get("body", ""),
            "body_length": s.get("body_length", 0),
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
