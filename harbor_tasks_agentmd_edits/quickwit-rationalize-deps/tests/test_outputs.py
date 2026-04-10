"""
Task: quickwit-rationalize-deps
Repo: quickwit-oss/quickwit @ eca4f763214604006262fc6a29dcf59c754813e3
PR:   6125

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

REPO = "/workspace/quickwit"
CARGO_TOML = Path(REPO) / "quickwit" / "Cargo.toml"
SKILL_PATH = Path(REPO) / ".claude" / "skills" / "rationalize-deps" / "SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_cargo_toml_valid():
    """Cargo.toml must be valid TOML after modifications."""
    content = CARGO_TOML.read_text()
    data = tomllib.loads(content)
    assert "workspace" in data, "Missing [workspace] section"
    assert "dependencies" in data["workspace"], "Missing [workspace.dependencies]"


def test_essential_deps_unchanged():
    """Critical dependencies must still be present in workspace."""
    content = CARGO_TOML.read_text()
    data = tomllib.loads(content)
    deps = data["workspace"]["dependencies"]
    for crate in ["tokio", "serde", "hyper", "hyper-util", "tokio-util",
                   "prometheus", "dialoguer", "zstd", "env_logger"]:
        assert crate in deps, f"Dependency '{crate}' must still be present in workspace deps"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_deps_rationalized():
    """All 6 deps must have default-features=false and no 'full' feature."""
    cargo_path = str(CARGO_TOML)
    r = subprocess.run(
        [sys.executable, "-c", DEPS_SCRIPT, cargo_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Dep validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


DEPS_SCRIPT = """\
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

cargo_path = sys.argv[1]
data = tomllib.loads(open(cargo_path).read())
deps = data["workspace"]["dependencies"]

errors = []
must_disable = ["hyper-util", "tokio-util", "prometheus", "dialoguer", "zstd", "env_logger"]
for name in must_disable:
    dep = deps.get(name)
    if dep is None:
        errors.append(f"{name} not found")
        continue
    if isinstance(dep, str):
        errors.append(f"{name} is a plain version string, needs default-features = false")
        continue
    if dep.get("default-features") is not False:
        errors.append(f"{name} missing default-features = false")
    features = dep.get("features", [])
    if "full" in features:
        errors.append(f"{name} still has 'full' feature")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
print("PASS: all 6 deps properly rationalized")
"""


def test_hyper_util_essential_features():
    """hyper-util must retain essential features (tokio, service) after removing 'full'."""
    cargo_path = str(CARGO_TOML)
    r = subprocess.run(
        [sys.executable, "-c", HYPER_UTIL_SCRIPT, cargo_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Feature check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


HYPER_UTIL_SCRIPT = """\
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

cargo_path = sys.argv[1]
data = tomllib.loads(open(cargo_path).read())
hu = data["workspace"]["dependencies"]["hyper-util"]

if isinstance(hu, str):
    print("FAIL: hyper-util is a plain string, no explicit features", file=sys.stderr)
    sys.exit(1)

features = hu.get("features", [])
if "full" in features:
    print("FAIL: hyper-util still uses 'full'", file=sys.stderr)
    sys.exit(1)

required = ["tokio", "service"]
missing = [f for f in required if f not in features]
if missing:
    print(f"FAIL: hyper-util missing required features: {missing}", file=sys.stderr)
    sys.exit(1)

print("PASS: hyper-util has essential features")
"""


def test_skill_file_exists():
    """rationalize-deps SKILL.md must exist with YAML frontmatter."""
    skill_path = str(SKILL_PATH)
    r = subprocess.run(
        [sys.executable, "-c", SKILL_EXISTS_SCRIPT, skill_path],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"SKILL.md check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


SKILL_EXISTS_SCRIPT = """\
import sys
from pathlib import Path

skill_path = Path(sys.argv[1])
if not skill_path.is_file():
    print(f"FAIL: {skill_path} does not exist", file=sys.stderr)
    sys.exit(1)

content = skill_path.read_text()
if not content.startswith("---"):
    print("FAIL: missing YAML frontmatter", file=sys.stderr)
    sys.exit(1)

parts = content.split("---", 2)
if len(parts) < 3:
    print("FAIL: frontmatter not properly closed", file=sys.stderr)
    sys.exit(1)

fm = parts[1]
if "name:" not in fm:
    print("FAIL: frontmatter missing 'name' field", file=sys.stderr)
    sys.exit(1)
if "description:" not in fm:
    print("FAIL: frontmatter missing 'description' field", file=sys.stderr)
    sys.exit(1)

print("PASS: SKILL.md exists with valid frontmatter")
"""


def test_skill_documents_workflow():
    """SKILL.md must document the dependency rationalization workflow."""
    skill_path = str(SKILL_PATH)
    r = subprocess.run(
        [sys.executable, "-c", SKILL_WORKFLOW_SCRIPT, skill_path],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Workflow check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


SKILL_WORKFLOW_SCRIPT = """\
import sys
from pathlib import Path

skill_path = Path(sys.argv[1])
if not skill_path.is_file():
    print(f"FAIL: {skill_path} does not exist", file=sys.stderr)
    sys.exit(1)

content = skill_path.read_text().lower()
required_keywords = ["cargo", "default-features", "cargo check"]
missing = [kw for kw in required_keywords if kw not in content]
if missing:
    print(f"FAIL: SKILL.md missing expected keywords: {missing}", file=sys.stderr)
    sys.exit(1)

print("PASS: SKILL.md documents rationalization workflow")
"""



# ---------------------------------------------------------------------------
# Additional pass_to_pass tests (enriched from CI exploration)
# These document CI commands that should pass on base commit.
# ---------------------------------------------------------------------------

def test_cargo_toml_members_exist():
    """All workspace members must have valid paths (pass_to_pass)."""
    content = CARGO_TOML.read_text()
    data = tomllib.loads(content)

    members = data.get("workspace", {}).get("members", [])
    workspace_root = Path(REPO) / "quickwit"

    missing = []
    for member in members:
        if member.strip().startswith("#"):
            continue  # Skip commented-out members
        member_path = workspace_root / member / "Cargo.toml"
        if not member_path.exists():
            missing.append(member)

    assert not missing, f"Missing workspace member directories: {missing}"


def test_cargo_toml_no_duplicate_deps():
    """No duplicate entries in workspace dependencies (pass_to_pass)."""
    content = CARGO_TOML.read_text()
    data = tomllib.loads(content)

    deps = data.get("workspace", {}).get("dependencies", {})
    dep_names = list(deps.keys())

    seen = set()
    duplicates = []
    for name in dep_names:
        if name in seen:
            duplicates.append(name)
        seen.add(name)

    assert not duplicates, f"Duplicate dependencies found: {duplicates}"


def test_cargo_toml_no_merge_conflicts():
    """Cargo.toml must not contain Git merge conflict markers (pass_to_pass)."""
    content = CARGO_TOML.read_text()
    assert "<<<<<<" not in content, "Git merge conflict markers found"
    assert ">>>>>>" not in content, "Git merge conflict markers found"
    assert "======" not in content, "Git merge conflict markers found"


def test_repo_scripts_exist():
    """CI scripts referenced by workflows must exist (pass_to_pass)."""
    scripts_dir = Path(REPO) / "quickwit" / "scripts"
    assert scripts_dir.exists(), "Scripts directory missing"

    # Key scripts referenced in CI
    key_scripts = ["check_license_headers.sh", "dep-tree.py"]
    for script in key_scripts:
        script_path = scripts_dir / script
        assert script_path.exists(), f"CI script missing: {script}"
