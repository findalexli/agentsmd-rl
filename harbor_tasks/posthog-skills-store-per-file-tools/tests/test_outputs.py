"""Behavioural / structural tests for the skills-store SKILL.md update.

The PR teaches the agent-facing `products/llm_analytics/skills/skills-store/SKILL.md`
about the per-file edit primitives (`skill-file-create`, `skill-file-delete`,
`skill-file-rename`, plus the body `edits` and per-file `file_edits` payloads).
These tests verify the documentation surface area: the available-tools table,
the local /phs bridge's allowed-tools list, frontmatter sanity, and that
the writing-skills "<500 lines" convention still holds.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/posthog")
SKILL_PATH = REPO / "products/llm_analytics/skills/skills-store/SKILL.md"


def _read() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_skill_file_present() -> None:
    """The target SKILL.md exists at the expected path."""
    r = subprocess.run(
        ["test", "-f", str(SKILL_PATH)],
        cwd=str(REPO),
        capture_output=True,
    )
    assert r.returncode == 0, f"Expected SKILL.md at {SKILL_PATH}"


def test_tools_table_lists_per_file_create() -> None:
    """Available-tools table must list `posthog:skill-file-create`."""
    text = _read()
    assert "posthog:skill-file-create" in text, (
        "The Available tools table must list the new `posthog:skill-file-create` tool."
    )


def test_tools_table_lists_per_file_delete() -> None:
    """Available-tools table must list `posthog:skill-file-delete`."""
    text = _read()
    assert "posthog:skill-file-delete" in text, (
        "The Available tools table must list the new `posthog:skill-file-delete` tool."
    )


def test_tools_table_lists_per_file_rename() -> None:
    """Available-tools table must list `posthog:skill-file-rename`."""
    text = _read()
    assert "posthog:skill-file-rename" in text, (
        "The Available tools table must list the new `posthog:skill-file-rename` tool."
    )


def _bridge_allowed_tools(text: str) -> str:
    """Return the value of the bridge skill's `allowed-tools:` line."""
    m = re.search(r"^allowed-tools:\s*(.+)$", text, re.M)
    assert m, "Expected an `allowed-tools:` line in the local /phs bridge frontmatter"
    return m.group(1)


def test_bridge_allowed_tools_includes_skill_file_create() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-create."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-create" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-create`."
    )


def test_bridge_allowed_tools_includes_skill_file_delete() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-delete."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-delete" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-delete`."
    )


def test_bridge_allowed_tools_includes_skill_file_rename() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-rename."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-rename" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-rename`."
    )


def test_per_file_edits_payload_documented() -> None:
    """Doc must teach the `file_edits` per-file patch payload by name."""
    text = _read()
    assert "file_edits" in text, (
        "Doc must teach the `file_edits` payload (per-file find/replace) by name."
    )


def test_frontmatter_skill_name_unchanged() -> None:
    """The top-level skill name remains `skills-store` (frontmatter sanity)."""
    text = _read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    assert m, "SKILL.md must start with YAML frontmatter delimited by `---` lines"
    fm = m.group(1)
    assert re.search(r"^name:\s*skills-store\s*$", fm, re.M), (
        "Top-level frontmatter `name:` must remain `skills-store` (this PR is documentation only)."
    )


def test_skill_under_500_lines() -> None:
    """SKILL.md stays under 500 lines (writing-skills convention)."""
    r = subprocess.run(
        ["wc", "-l", str(SKILL_PATH)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    n = int(r.stdout.split()[0])
    assert n < 500, (
        f"SKILL.md is {n} lines — the writing-skills convention requires bodies "
        "to stay under 500 lines (move detailed material into bundled files)."
    )


def test_no_files_array_replace_all_promoted_as_default() -> None:
    """The bulk-replace `files` shape should not be the recommended default any more.

    Before the PR, the only documented update path was a `skill-update` call
    that took `body`/`files` (replacing the whole bundle). The PR demotes that
    path: per-file edits should be the recommended primitive. We check that the
    doc no longer says `files` replace-all is the default carry-forward
    behaviour for updates.
    """
    text = _read()
    legacy_phrase = (
        "If you pass `files`, they replace the previous version's file set; "
        "if you omit `files`, they're carried forward"
    )
    assert legacy_phrase not in text, (
        "The original phrasing that promoted `files` replace-all as the default "
        "update shape should no longer appear — describe per-file edits as the "
        "preferred primitive instead."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_integration_tests_run_migrations():
    """pass_to_pass | CI job 'Integration Tests' → step 'Run migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py migrate --noinput && python manage.py migrate_clickhouse'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_integration_tests_seed_test_data():
    """pass_to_pass | CI job 'Integration Tests' → step 'Seed test data'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py generate_demo_data --n-clusters 10 --days-past 7 --days-future 0 --skip-materialization --skip-flag-sync --skip-user-product-list'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Seed test data' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_integration_tests_create_api_key_and_extract_test_ids():
    """pass_to_pass | CI job 'Integration Tests' → step 'Create API key and extract test IDs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Create API key and extract test IDs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_integration_tests_run_integration_tests():
    """pass_to_pass | CI job 'Integration Tests' → step 'Run integration tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:integration'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run integration tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_wrangler_pre_build_steps():
    """pass_to_pass | CI job 'Unit Tests' → step 'Run wrangler pre-build steps'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build && pnpm exec tsx scripts/copy-instructions.ts'], cwd=os.path.join(REPO, 'services/mcp'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run wrangler pre-build steps' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_unit_tests():
    """pass_to_pass | CI job 'Unit Tests' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/mcp run test -u'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_build_package():
    """pass_to_pass | CI job 'Build Package' → step 'Build package'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build package' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_type_check():
    """pass_to_pass | CI job 'Build Package' → step 'Type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_check_generated_ui_apps_are_up_to_date():
    """pass_to_pass | CI job 'Build Package' → step 'Check generated UI apps are up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run generate:ui-apps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated UI apps are up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_lint_tool_names():
    """pass_to_pass | CI job 'Build Package' → step 'Lint tool names'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint-tool-names'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint tool names' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_rust_services_run_cargo_build():
    """pass_to_pass | CI job 'Build Rust services' → step 'Run cargo build'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build --all --locked --release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cargo build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_rust_set_up_databases():
    """pass_to_pass | CI job 'Test Rust' → step 'Set up databases'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py setup_test_environment'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Set up databases' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")