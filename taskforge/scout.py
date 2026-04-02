"""Stage 1: PR scouting — filter candidates and split patches.

Adapted from:
- SWE-bench (princeton-nlp/SWE-bench) — patch splitting, License: MIT
- R2E-Gym — size thresholds
"""

from __future__ import annotations

import re
from typing import Sequence

from unidiff import PatchSet

from taskforge.models import PRCandidate

# ---------------------------------------------------------------------------
# Patch splitting
# ---------------------------------------------------------------------------

TEST_PATH_KEYWORDS: Sequence[str] = ("test", "tests", "e2e", "testing", "spec", "__tests__")


def split_patch(diff_text: str) -> tuple[str, str]:
    """Split a unified diff into (code_patch, test_patch)."""
    if not diff_text or not diff_text.strip():
        return "", ""
    try:
        patch_set = PatchSet(diff_text)
    except Exception:
        return diff_text, ""

    code_hunks: list[str] = []
    test_hunks: list[str] = []
    for patched_file in patch_set:
        path_lower = patched_file.path.lower()
        if any(kw in path_lower for kw in TEST_PATH_KEYWORDS):
            test_hunks.append(str(patched_file))
        else:
            code_hunks.append(str(patched_file))
    return "\n".join(code_hunks), "\n".join(test_hunks)


def extract_new_identifiers(diff_text: str) -> set[str]:
    """Extract identifiers that appear only in added lines (leakage detection)."""
    if not diff_text:
        return set()
    added: set[str] = set()
    removed: set[str] = set()
    ident_re = re.compile(r"\b([a-zA-Z_]\w{2,})\b")
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.update(ident_re.findall(line))
        elif line.startswith("-") and not line.startswith("---"):
            removed.update(ident_re.findall(line))
    return added - removed


# ---------------------------------------------------------------------------
# PR filtering
# ---------------------------------------------------------------------------

MAX_FILES = 100
MAX_LINES_CHANGED = 5000
MIN_LINES_CHANGED = 5

_DOC_EXTENSIONS = frozenset({".md", ".rst", ".adoc"})
_DOC_PREFIXES = ("docs/", "doc/", ".github/", "website/")
_LOCKFILE_KEYWORDS = frozenset({
    "lock", "requirements", "package.json", "Cargo.toml",
    "pyproject.toml", "go.sum", "yarn.lock", "pnpm-lock",
})
_SHA1_RE = re.compile(r"(?<!/)\b[0-9a-f]{40}\b")


def is_good_candidate(pr: PRCandidate, diff: str = "") -> tuple[bool, str]:
    """Run all heuristic filters. Returns (passed, reason)."""
    if pr.changed_files < 1 or pr.changed_files > MAX_FILES:
        return False, f"file count {pr.changed_files} outside [1, {MAX_FILES}]"
    if pr.total_changes > MAX_LINES_CHANGED:
        return False, f"too large ({pr.total_changes} lines > {MAX_LINES_CHANGED})"
    if pr.total_changes < MIN_LINES_CHANGED:
        return False, f"too small ({pr.total_changes} < {MIN_LINES_CHANGED} lines)"
    if _is_docs_only(pr.file_paths):
        return False, "docs-only PR"
    if _is_deps_only(pr.file_paths):
        return False, "deps-only PR"
    if diff:
        code_patch, _ = split_patch(diff)
        if not code_patch.strip():
            return False, "test-only PR (no code changes)"
    if _SHA1_RE.search(pr.title or ""):
        return False, "title contains commit hash"
    return True, "passed"


def _is_docs_only(paths: Sequence[str]) -> bool:
    if not paths:
        return False
    for p in paths:
        ext = "." + p.rsplit(".", 1)[-1] if "." in p else ""
        if ext not in _DOC_EXTENSIONS and ext not in {".toml", ".cfg", ".ini", ".yml", ".yaml", ".json"}:
            if not any(p.startswith(pfx) for pfx in _DOC_PREFIXES):
                return False
    return True


def _is_deps_only(paths: Sequence[str]) -> bool:
    if not paths:
        return False
    return all(any(kw in p for kw in _LOCKFILE_KEYWORDS) for p in paths)
