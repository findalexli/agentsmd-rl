import os
import re
import subprocess

import yaml

REPO = "/workspace/openai-agents-js"
WORKFLOWS_DIR = os.path.join(REPO, ".github", "workflows")


def _workflow_files():
    return sorted(
        os.path.join(WORKFLOWS_DIR, f)
        for f in os.listdir(WORKFLOWS_DIR)
        if f.endswith((".yml", ".yaml"))
    )


def _find_action_setup_steps(doc):
    """Walk a parsed YAML doc and yield (step_name, uses, with_block) tuples."""
    if isinstance(doc, dict):
        if "uses" in doc and "pnpm/action-setup" in str(doc.get("uses", "")):
            yield doc.get("name"), doc["uses"], doc.get("with", {})
        for v in doc.values():
            yield from _find_action_setup_steps(v)
    elif isinstance(doc, list):
        for item in doc:
            yield from _find_action_setup_steps(item)


# ---------- fail_to_pass ----------

def test_action_setup_pinned():
    """No workflow uses pnpm/action-setup with a floating major-only tag like @v4."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            content = fh.read()
        for m in re.finditer(r"pnpm/action-setup@(\S+)", content):
            tag = m.group(1)
            assert re.search(r"\d+\.\d+", tag), (
                f"{fname}: pnpm/action-setup tag '{tag}' is a floating major; "
                f"must be pinned to a specific minor/patch version"
            )


def test_version_field_in_with():
    """Every pnpm/action-setup step specifies a version number in its with block."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            doc = yaml.safe_load(fh)
        for step_name, uses, with_block in _find_action_setup_steps(doc):
            assert isinstance(with_block, dict), (
                f"{fname}: pnpm/action-setup step '{step_name}' is missing its 'with' block"
            )
            assert "version" in with_block, (
                f"{fname}: pnpm/action-setup step '{step_name}' has no 'version' in 'with'"
            )


def test_docs_step_name():
    """The workflow step that installs pnpm in docs.yml is named 'Install pnpm'."""
    docs_yml = os.path.join(WORKFLOWS_DIR, "docs.yml")
    with open(docs_yml) as fh:
        doc = yaml.safe_load(fh)
    steps = doc.get("jobs", {}).get("build", {}).get("steps", [])
    for step in steps:
        if "pnpm/action-setup" in str(step.get("uses", "")):
            assert step.get("name") == "Install pnpm", (
                f"docs.yml pnpm/action-setup step should be named 'Install pnpm', "
                f"got '{step.get('name')}'"
            )
            return
    raise AssertionError("No pnpm/action-setup step found in docs.yml")


def test_pnpm_upgrade_skill_exists():
    """The pnpm-upgrade SKILL.md file exists."""
    skill_path = os.path.join(REPO, ".codex", "skills", "pnpm-upgrade", "SKILL.md")
    assert os.path.exists(skill_path), f"{skill_path} does not exist"


def test_skill_frontmatter():
    """SKILL.md has correct frontmatter fields."""
    skill_path = os.path.join(REPO, ".codex", "skills", "pnpm-upgrade", "SKILL.md")
    with open(skill_path) as fh:
        content = fh.read()
    assert "name: pnpm-upgrade" in content, "SKILL.md missing 'name: pnpm-upgrade' in frontmatter"
    assert "pnpm self-update" in content, "SKILL.md must reference pnpm self-update"
    assert "packageManager" in content, "SKILL.md must reference packageManager alignment"
    assert "pnpm/action-setup" in content, "SKILL.md must reference pnpm/action-setup"


# ---------- pass_to_pass ----------

def test_workflow_yaml_valid():
    """Every workflow YAML file remains valid YAML (p2p)."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            try:
                yaml.safe_load(fh)
            except yaml.YAMLError as e:
                raise AssertionError(f"{fname} is not valid YAML: {e}")


def test_repo_checkout_ok():
    """The repo is checked out at the expected base commit (p2p)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    # HEAD should be the base commit (before fix applied)
    # This is informational; pass_to_pass just verifies the repo is usable

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'build' → step 'Run build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run build' failed (returncode={r.returncode}):\n"
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