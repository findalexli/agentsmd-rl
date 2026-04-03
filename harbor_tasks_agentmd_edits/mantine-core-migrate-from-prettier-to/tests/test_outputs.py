"""
Task: mantine-core-migrate-from-prettier-to
Repo: mantinedev/mantine @ 2281c3859b4f26227d2f1f371aaa9258d3a8dbd8
PR:   8786

Migrate from prettier to oxfmt as the code formatter. All agent config
files (CLAUDE.md, SKILL.md, llms/testing.md) must be updated too.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/mantine"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_package_json_valid():
    """package.json must be valid JSON after modifications."""
    pkg_path = Path(REPO) / "package.json"
    data = json.loads(pkg_path.read_text())
    assert "scripts" in data, "package.json must have a scripts section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code/config migration tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_format_scripts_in_package_json():
    """package.json must have format:test, format:write, format:write:files scripts using oxfmt."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg["scripts"]

    # New format scripts must exist
    assert "format:test" in scripts, "Missing format:test script"
    assert "format:write" in scripts, "Missing format:write script"
    assert "format:write:files" in scripts, "Missing format:write:files script"

    # They must invoke oxfmt, not prettier
    assert "oxfmt" in scripts["format:test"], "format:test should use oxfmt"
    assert "oxfmt" in scripts["format:write"], "format:write should use oxfmt"
    assert "oxfmt" in scripts["format:write:files"], "format:write:files should use oxfmt"

    # Old prettier scripts must be gone
    assert "prettier:test" not in scripts, "prettier:test should be removed"
    assert "prettier:write" not in scripts, "prettier:write should be removed"
    assert "prettier:write:files" not in scripts, "prettier:write:files should be removed"


# [pr_diff] fail_to_pass
def test_test_all_uses_format():
    """test:all script must reference format:test, not prettier:test."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    test_all = pkg["scripts"]["test:all"]
    assert "format:test" in test_all, "test:all should use format:test"
    assert "prettier:test" not in test_all, "test:all should not reference prettier:test"


# [pr_diff] fail_to_pass
def test_oxfmt_config_created():
    """.oxfmtrc.json must exist with valid formatting config."""
    cfg_path = Path(REPO) / ".oxfmtrc.json"
    assert cfg_path.exists(), ".oxfmtrc.json must be created"
    data = json.loads(cfg_path.read_text())
    assert "printWidth" in data, "oxfmt config should have printWidth"
    assert "singleQuote" in data, "oxfmt config should have singleQuote"
    assert "importOrder" in data, "oxfmt config should have importOrder"
    assert isinstance(data["importOrder"], list), "importOrder should be a list"
    assert len(data["importOrder"]) >= 5, "importOrder should have import sorting rules"


# [pr_diff] fail_to_pass
def test_prettier_config_removed():
    """.prettierrc.mjs and .prettierignore must be removed."""
    assert not (Path(REPO) / ".prettierrc.mjs").exists(), \
        ".prettierrc.mjs should be deleted"
    assert not (Path(REPO) / ".prettierignore").exists(), \
        ".prettierignore should be deleted"


# [pr_diff] fail_to_pass
def test_prettier_dep_removed_oxfmt_added():
    """prettier and its plugin removed from deps; oxfmt added."""
    pkg_text = (Path(REPO) / "package.json").read_text()
    pkg = json.loads(pkg_text)

    # Check all dependency sections
    all_deps = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        all_deps.update(pkg.get(key, {}))

    assert "prettier" not in all_deps, "prettier should be removed from dependencies"
    assert "@ianvs/prettier-plugin-sort-imports" not in all_deps, \
        "prettier sort-imports plugin should be removed"

    # oxfmt must be present somewhere in deps
    assert "oxfmt" in all_deps or "oxfmt" in pkg_text, \
        "oxfmt should be added as a dependency"


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — agent config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # Must mention oxfmt (not prettier) in the test:all description
    assert "oxfmt" in content, \
        "SKILL.md should mention oxfmt as the formatter"
    assert "format:write" in content, \
        "SKILL.md should reference format:write command"

    # Old prettier references should be gone
    assert "prettier:write" not in content, \
        "SKILL.md should not reference prettier:write"
    # The word "prettier" in "This runs prettier," should be replaced
    lines = content.split("\n")
    for line in lines:
        if "This runs" in line and "syncpack" in line:
            assert "prettier" not in line, \
                "SKILL.md 'This runs ...' line should not mention prettier"


# [config_edit] fail_to_pass
