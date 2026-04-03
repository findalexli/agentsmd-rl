"""
Task: wasp-add-script-to-install-playwright
Repo: wasp-lang/wasp @ 02e17a0faa6c5297d0f22fc89a84be5ffa6c6665
PR:   3292

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/wasp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / validation checks
# ---------------------------------------------------------------------------

def test_package_json_valid():
    """All modified package.json files must be valid JSON."""
    pkg_paths = [
        "examples/kitchen-sink/package.json",
        "examples/ask-the-documents/package.json",
        "examples/tutorials/TodoApp/package.json",
        "examples/tutorials/TodoAppTs/package.json",
        "examples/waspello/package.json",
        "examples/waspleau/package.json",
        "examples/websockets-realtime-voting/package.json",
        "waspc/starters-e2e-tests/package.json",
        "waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json",
    ]
    for rel in pkg_paths:
        p = Path(REPO) / rel
        data = json.loads(p.read_text())
        assert "scripts" in data, f"{rel} missing scripts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_kitchen_sink_auto_installs_playwright_deps():
    """kitchen-sink test script must auto-install playwright deps."""
    pkg = json.loads((Path(REPO) / "examples/kitchen-sink/package.json").read_text())
    scripts = pkg["scripts"]

    # Either a dedicated install-deps script chained by test, or a pretest hook
    has_install_script = any(
        "playwright install" in v
        for k, v in scripts.items()
        if "install" in k.lower() or k == "pretest"
    )
    test_chains = (
        "install-deps" in scripts.get("test", "")
        or "pretest" in scripts
    )

    assert has_install_script, (
        "package.json must have a script that runs 'playwright install'"
    )
    assert test_chains, (
        "test script must chain the install-deps script (or use pretest hook)"
    )


def test_starters_auto_installs_playwright_deps():
    """starters-e2e-tests test scripts must auto-install playwright deps."""
    pkg = json.loads(
        (Path(REPO) / "waspc/starters-e2e-tests/package.json").read_text()
    )
    scripts = pkg["scripts"]

    has_install_script = any(
        "playwright install" in v
        for k, v in scripts.items()
        if "install" in k.lower() or k == "pretest"
    )
    # Both test and test:dev should chain the install
    test_chains = (
        "install-deps" in scripts.get("test", "")
        or "pretest" in scripts
    )
    test_dev_chains = (
        "install-deps" in scripts.get("test:dev", "")
        or "pretest" in scripts
    )

    assert has_install_script, (
        "starters package.json must have a script that runs 'playwright install'"
    )
    assert test_chains, "test script must chain install-deps"
    assert test_dev_chains, "test:dev script must chain install-deps"


def test_multiple_examples_auto_install():
    """At least 5 example package.json files must auto-install playwright deps."""
    example_pkgs = [
        "examples/ask-the-documents/package.json",
        "examples/tutorials/TodoApp/package.json",
        "examples/tutorials/TodoAppTs/package.json",
        "examples/waspello/package.json",
        "examples/waspleau/package.json",
        "examples/websockets-realtime-voting/package.json",
    ]
    count = 0
    for rel in example_pkgs:
        pkg = json.loads((Path(REPO) / rel).read_text())
        scripts = pkg.get("scripts", {})
        has_auto = (
            any("playwright install" in v for k, v in scripts.items()
                if "install" in k.lower() or k == "pretest")
            and ("install-deps" in scripts.get("test", "") or "pretest" in scripts)
        )
        if has_auto:
            count += 1

    assert count >= 5, (
        f"Only {count}/6 example package.json files auto-install playwright deps, "
        "expected at least 5"
    )


def test_run_script_no_manual_playwright_install():
    """waspc/run must not manually run 'npx playwright install --with-deps'."""
    run_script = (Path(REPO) / "waspc/run").read_text()
    assert "npx playwright install" not in run_script, (
        "waspc/run should not have manual 'npx playwright install' — "
        "it should be handled by the npm test script"
    )


def test_ci_no_explicit_playwright_install_step():
    """CI workflow files must not have a separate playwright install step."""
    ci_examples = (
        Path(REPO) / ".github/workflows/ci-examples-test.yaml"
    ).read_text()
    ci_starters = (
        Path(REPO) / ".github/workflows/ci-starters-test.yaml"
    ).read_text()

    for name, content in [
        ("ci-examples-test.yaml", ci_examples),
        ("ci-starters-test.yaml", ci_starters),
    ]:
        assert "npx playwright install" not in content, (
            f"{name} should not have explicit 'npx playwright install' step — "
            "it should be handled by npm test script"
        )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------


    # The old README had a numbered step telling users to run
    # 'npx playwright install --with-deps' manually before tests.
    # After the fix, this manual step should be gone since it's automated.
    assert "npx playwright install" not in readme, (
        "README should not tell users to manually run 'npx playwright install' — "
        "this is now automated by the test script"
    )



    # Golden snapshot should also not have the manual install step
    assert "npx playwright install" not in golden, (
        "Golden snapshot README should not have manual 'npx playwright install' step"
    )
    # Should still mention playwright for e2e tests
    assert "playwright" in golden.lower(), (
        "Golden snapshot README should still mention playwright"
    )


def test_golden_snapshot_package_json_updated():
    """Golden snapshot package.json must also have the auto-install script."""
    pkg = json.loads(
        (
            Path(REPO)
            / "waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json"
        ).read_text()
    )
    scripts = pkg["scripts"]
    has_install_script = any(
        "playwright install" in v
        for k, v in scripts.items()
        if "install" in k.lower() or k == "pretest"
    )
    assert has_install_script, (
        "Golden snapshot package.json must have auto-install playwright script"
    )
