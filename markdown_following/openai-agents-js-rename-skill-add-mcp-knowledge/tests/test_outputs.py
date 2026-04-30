"""Structural checks for openai-agents-js PR #836 task."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/openai-agents-js")
SKILL_NEW = REPO / ".codex/skills/code-change-verification/SKILL.md"
SKILL_OLD_DIR = REPO / ".codex/skills/verify-changes"
KNOWLEDGE_SKILL = REPO / ".codex/skills/openai-knowledge/SKILL.md"
AGENTS_MD = REPO / "AGENTS.md"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _frontmatter(p: Path) -> dict:
    text = _read(p)
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError(f"{p} has no YAML frontmatter delimited by ---")
    return yaml.safe_load(parts[1]) or {}


# ---------------------------------------------------------------------------
# fail_to_pass — these fail at base, pass on gold.
# ---------------------------------------------------------------------------

def test_renamed_skill_file_exists():
    assert SKILL_NEW.exists(), (
        f"Expected the renamed Codex skill file at {SKILL_NEW}; not found."
    )


def test_renamed_skill_frontmatter_name():
    fm = _frontmatter(SKILL_NEW)
    assert fm.get("name") == "code-change-verification", (
        f"SKILL.md frontmatter must declare name: code-change-verification; "
        f"got {fm.get('name')!r}."
    )


def test_openai_knowledge_skill_file_exists():
    assert KNOWLEDGE_SKILL.exists(), (
        f"Expected new Codex skill file at {KNOWLEDGE_SKILL}; not found."
    )


def test_openai_knowledge_skill_frontmatter_name():
    fm = _frontmatter(KNOWLEDGE_SKILL)
    assert fm.get("name") == "openai-knowledge", (
        f"openai-knowledge SKILL.md frontmatter must declare "
        f"name: openai-knowledge; got {fm.get('name')!r}."
    )


def test_agents_md_references_code_change_verification_skill():
    """AGENTS.md must mention the renamed skill via $code-change-verification."""
    r = subprocess.run(
        ["grep", "-Fq", "$code-change-verification", str(AGENTS_MD)],
        capture_output=True,
    )
    assert r.returncode == 0, (
        "AGENTS.md must reference the renamed skill as $code-change-verification."
    )


def test_agents_md_references_openai_knowledge_skill():
    """AGENTS.md must mention the new $openai-knowledge skill."""
    r = subprocess.run(
        ["grep", "-Fq", "$openai-knowledge", str(AGENTS_MD)],
        capture_output=True,
    )
    assert r.returncode == 0, (
        "AGENTS.md must reference the new $openai-knowledge skill."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — these pass at base AND on gold.
# ---------------------------------------------------------------------------

def test_agents_md_conventional_commits_section_intact():
    """AGENTS.md still documents Conventional Commits — should not be removed."""
    text = _read(AGENTS_MD)
    assert "Conventional Commits" in text, (
        "AGENTS.md should retain the Conventional Commits guidelines."
    )


def test_agents_md_top_header_intact():
    """AGENTS.md still opens with its Contributor Guide top-level header."""
    text = _read(AGENTS_MD)
    assert text.lstrip().startswith("# Contributor Guide"), (
        "AGENTS.md should keep its `# Contributor Guide` top-level heading."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")