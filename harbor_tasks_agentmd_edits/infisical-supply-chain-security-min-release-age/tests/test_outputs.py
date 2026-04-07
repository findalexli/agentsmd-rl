import subprocess
import json
import pytest
from pathlib import Path

REPO = Path("/workspace/infisical")


# --- Fail-to-pass: behavioral tests (npm executes and reads .npmrc) ---


def test_npm_reads_backend_config():
    """npm must read min-release-age=7 from backend/.npmrc."""
    result = subprocess.run(
        ["npm", "config", "get", "min-release-age"],
        cwd=str(REPO / "backend"),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"npm config get failed: {result.stderr}"
    assert result.stdout.strip() == "7", (
        f"Expected '7', got: {result.stdout.strip()!r}"
    )


def test_npm_reads_frontend_config():
    """npm must read min-release-age=7 from frontend/.npmrc."""
    result = subprocess.run(
        ["npm", "config", "get", "min-release-age"],
        cwd=str(REPO / "frontend"),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"npm config get failed: {result.stderr}"
    assert result.stdout.strip() == "7", (
        f"Expected '7', got: {result.stdout.strip()!r}"
    )


# --- Fail-to-pass: structural tests ---


def test_backend_npmrc_exists():
    """backend/.npmrc must exist with min-release-age=7."""
    npmrc = REPO / "backend" / ".npmrc"
    assert npmrc.exists(), "backend/.npmrc does not exist"
    content = npmrc.read_text().strip()
    assert "min-release-age=7" in content, f"Expected 'min-release-age=7', got: {content}"


def test_frontend_npmrc_exists():
    """frontend/.npmrc must exist with min-release-age=7."""
    npmrc = REPO / "frontend" / ".npmrc"
    assert npmrc.exists(), "frontend/.npmrc does not exist"
    content = npmrc.read_text().strip()
    assert "min-release-age=7" in content, f"Expected 'min-release-age=7', got: {content}"


def test_backend_package_json_engine():
    """backend/package.json must require npm >= 11.10.0."""
    pkg = json.loads((REPO / "backend" / "package.json").read_text())
    assert "engines" in pkg, "package.json missing 'engines' field"
    assert "npm" in pkg["engines"], "engines missing 'npm' requirement"
    npm_ver = pkg["engines"]["npm"]
    assert "11.10" in npm_ver, f"Expected npm >= 11.10.0, got: {npm_ver}"


def test_frontend_package_json_engine():
    """frontend/package.json must require npm >= 11.10.0."""
    pkg = json.loads((REPO / "frontend" / "package.json").read_text())
    assert "engines" in pkg, "package.json missing 'engines' field"
    assert "npm" in pkg["engines"], "engines missing 'npm' requirement"
    npm_ver = pkg["engines"]["npm"]
    assert "11.10" in npm_ver, f"Expected npm >= 11.10.0, got: {npm_ver}"


# --- Fail-to-pass: config/documentation update ---


def test_claude_md_dependency_policy():
    """CLAUDE.md must document the dependency policy with supply-chain context."""
    claude_md = (REPO / "CLAUDE.md").read_text()
    assert "Dependency Policy" in claude_md, (
        "CLAUDE.md missing 'Dependency Policy' section"
    )
    assert "min-release-age" in claude_md or "minimum release age" in claude_md.lower(), (
        "CLAUDE.md should mention the minimum release age setting"
    )
    assert "supply-chain" in claude_md.lower() or "supply chain" in claude_md.lower(), (
        "CLAUDE.md should describe this as a supply-chain security measure"
    )


# --- Pass-to-pass: existing functionality preserved ---


def test_claude_md_existing_sections_intact():
    """Existing CLAUDE.md sections (Essential Commands, Cross-Cutting Patterns) must remain."""
    claude_md = (REPO / "CLAUDE.md").read_text()
    assert "## Essential Commands" in claude_md, (
        "Essential Commands section missing from CLAUDE.md"
    )
    assert "## Cross-Cutting Patterns" in claude_md, (
        "Cross-Cutting Patterns section missing from CLAUDE.md"
    )


def test_backend_package_json_scripts_intact():
    """backend/package.json core fields (name, main, scripts) must remain unchanged."""
    pkg = json.loads((REPO / "backend" / "package.json").read_text())
    assert pkg.get("name") == "infisical", f"Unexpected name: {pkg.get('name')}"
    assert "scripts" in pkg, "package.json missing scripts"
    assert "dev" in pkg["scripts"], "dev script missing"
