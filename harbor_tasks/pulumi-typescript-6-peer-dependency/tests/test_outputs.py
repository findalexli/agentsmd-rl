import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/pulumi")
SDK = REPO / "sdk/nodejs"
SXS = SDK / "tests/sxs_ts_test"


def _run(cmd, cwd=None, timeout=600, env=None):
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
        timeout=timeout, env=env,
    )


def test_peerdep_allows_typescript_6():
    """Several TypeScript 6.x releases must satisfy peerDependencies.typescript;
    older majors (3.8.3, 4, 5) must keep working; TypeScript 7 must NOT
    satisfy. Evaluates the semver range with the installed `semver` module —
    no string matching.
    """
    pkg = json.loads((SDK / "package.json").read_text())
    rng = pkg["peerDependencies"]["typescript"]

    def _semver_check(version, expected):
        script = (
            "const semver = require('semver');"
            f"const ok = semver.satisfies({json.dumps(version)}, {json.dumps(rng)});"
            "process.exit(ok ? 0 : 1);"
        )
        r = _run(["node", "-e", script], cwd=SDK, timeout=60)
        got = r.returncode == 0
        assert got is expected, (
            f"semver.satisfies({version!r}, {rng!r}) returned {got}, expected {expected}.\n"
            f"stdout={r.stdout}\nstderr={r.stderr}"
        )

    # Must NOW be allowed — every 6.x version we expect to support.
    for v in ["6.0.0", "6.0.1", "6.5.4", "6.99.99"]:
        _semver_check(v, True)
    # Must STILL be allowed — older majors that the SDK has always supported.
    for v in ["3.8.3", "4.9.5", "5.7.2"]:
        _semver_check(v, True)
    # Must NOT be allowed — the upper bound has not been opened to TS 7+.
    for v in ["7.0.0", "8.0.0"]:
        _semver_check(v, False)


def test_makefile_sxs_tests_includes_ts6():
    """`make -n sxs_tests` should expand TSC_SUPPORTED_VERSIONS so that the
    TypeScript-6 per-version package file (`package^6.json`) is referenced
    in the recipe output.

    Make expands $(TSC_SUPPORTED_VERSIONS:%=sxs_test_%) and the per-version
    cp command in the rule substitutes $(version) into `package<version>.json`;
    the dry-run output is therefore the source of truth for which versions
    are exercised.
    """
    r = _run(["make", "-n", "sxs_tests"], cwd=SDK, timeout=60)
    assert r.returncode == 0, f"make -n sxs_tests failed:\n{r.stdout}\n{r.stderr}"
    out = r.stdout + r.stderr
    assert "package^6.json" in out, (
        "make -n sxs_tests does not reference package^6.json — "
        "TSC_SUPPORTED_VERSIONS appears not to cover TypeScript 6.\n"
        f"Output:\n{out}"
    )


def test_typescript_6_compiles_sxs_consumer():
    """End-to-end: typecheck the sxs_test consumer with TypeScript 6.

    Mirrors what `make sxs_test_^6` does, but uses the already-installed
    node_modules (tested at image-build time) so we do not need network at
    test time. This is the core behavioral check: a project depending on
    @pulumi/pulumi with typescript@6 must typecheck cleanly under the
    project-supplied tsconfig override.
    """
    pkg6 = SXS / "package^6.json"
    cfg6 = SXS / "tsconfig^6.json"

    # If the patch is incomplete, the cp / project flag below will surface it.
    pkg_dst = SXS / "package.json"
    if pkg_dst.exists():
        pkg_dst.unlink()

    # Behavioral: actually copy the package file and run tsc.
    shutil.copyfile(pkg6, pkg_dst)
    try:
        # Sanity: the resolved tsc binary is TypeScript 6.x.
        ver = _run(["yarn", "run", "--silent", "tsc", "--version"], cwd=SXS, timeout=120)
        assert ver.returncode == 0, f"tsc --version failed:\n{ver.stdout}\n{ver.stderr}"
        assert "Version 6." in ver.stdout, f"Expected TypeScript 6.x, got: {ver.stdout!r}"

        # Real typecheck: must succeed with the patched tsconfig override.
        r = _run(
            ["yarn", "run", "--silent", "tsc", "--project", str(cfg6.name)],
            cwd=SXS, timeout=300,
        )
        assert r.returncode == 0, (
            "tsc --project tsconfig^6.json failed:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        )
    finally:
        if pkg_dst.exists():
            pkg_dst.unlink()


def test_changelog_entry_added_for_sdk_nodejs():
    """The repo's PR convention is that user-visible SDK changes get a pending
    changelog entry. CLAUDE.md / AGENTS.md state changelog entries are
    required for most PRs. We parse the pending YAML and verify an entry
    of `type: fix` and `scope: sdk/nodejs` exists — this validates schema,
    not just substrings.
    """
    pending = REPO / "changelog/pending"
    assert pending.is_dir(), f"changelog/pending dir missing at {pending}"

    # Use Node's js-yaml (already installed in sdk/nodejs/node_modules) to
    # parse the changelog YAML — keeps us off Python YAML libraries that
    # are not installed in the image.
    matched = []
    for entry in sorted(pending.glob("*.yaml")):
        script = (
            "const fs = require('fs');"
            "const yaml = require('js-yaml');"
            f"const doc = yaml.load(fs.readFileSync({json.dumps(str(entry))}, 'utf8'));"
            "for (const c of (doc && doc.changes) || []) {"
            "  if (c.type === 'fix' && c.scope === 'sdk/nodejs') {"
            "    process.stdout.write('MATCH:' + (c.description||''));"
            "    process.exit(0);"
            "  }"
            "}"
            "process.exit(1);"
        )
        r = _run(["node", "-e", script], cwd=SDK, timeout=60)
        if r.returncode == 0 and r.stdout.startswith("MATCH:"):
            matched.append((entry.name, r.stdout[len("MATCH:"):]))

    assert matched, (
        f"No pending changelog entry parsed as type=fix scope=sdk/nodejs under {pending}. "
        "Per CLAUDE.md/AGENTS.md, most PRs require a changelog entry."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: anchors that already work at the base commit and must keep
# working after the fix. They guard against destructive changes.
# ---------------------------------------------------------------------------


def test_p2p_sdk_nodejs_typechecks():
    """The SDK's TypeScript sources must keep typechecking under the SDK's
    own `tsconfig.json`. The fix should not break the SDK's own build.
    """
    r = _run(["yarn", "run", "--silent", "tsc", "--noEmit"], cwd=SDK, timeout=300)
    assert r.returncode == 0, (
        f"`yarn run tsc --noEmit` (sdk/nodejs build) failed:\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_p2p_sdk_nodejs_package_json_valid():
    """sdk/nodejs/package.json must remain valid JSON with the @pulumi/pulumi name."""
    pkg = json.loads((SDK / "package.json").read_text())
    assert pkg.get("name") == "@pulumi/pulumi"
    assert "peerDependencies" in pkg
    assert "typescript" in pkg["peerDependencies"]
    assert "ts-node" in pkg["peerDependencies"]
    # ts-node range must NOT have been narrowed.
    assert pkg["peerDependencies"]["ts-node"] == ">= 7.0.1 < 12"


def test_p2p_makefile_keeps_existing_versions():
    """The existing TypeScript versions (~3.8.3, ^3, ^4) in TSC_SUPPORTED_VERSIONS
    must still be present after the fix — adding ^6 must not drop the older ones.
    Each per-version cp expands to `package<version>.json` in the recipe.
    """
    r = _run(["make", "-n", "sxs_tests"], cwd=SDK, timeout=60)
    assert r.returncode == 0
    out = r.stdout + r.stderr
    for f in ["package~3.8.3.json", "package^3.json", "package^4.json"]:
        assert f in out, (
            f"Existing TS per-version package file {f!r} dropped from sxs_tests:\n{out}"
        )


def test_p2p_biome_files_section_valid_json():
    """biome.json must remain valid JSON after editing the files.ignore list."""
    text = (SDK / "biome.json").read_text()
    # biome.json contains comments? No, it's plain JSON. Parse it.
    data = json.loads(text)
    assert "files" in data and "ignore" in data["files"]
    # bin/, proto/, dist/, node_modules ignores must remain.
    ignored = data["files"]["ignore"]
    for required in ["bin/", "proto/", "dist/", "node_modules"]:
        assert required in ignored, f"biome.json files.ignore lost {required!r}: {ignored}"
