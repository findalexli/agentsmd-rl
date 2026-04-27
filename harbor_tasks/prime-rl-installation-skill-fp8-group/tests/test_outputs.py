"""Tests for prime-rl#1884 — adds fp8-inference dependency group + installation SKILL.md."""

from pathlib import Path
import re
import subprocess
import tomli

REPO = Path("/workspace/prime-rl")
SKILL = REPO / "skills" / "installation" / "SKILL.md"
PYPROJECT = REPO / "pyproject.toml"
WHEEL_URL = (
    "https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/"
    "deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl"
)


def _skill_text() -> str:
    assert SKILL.exists(), f"Expected SKILL doc at {SKILL}"
    return SKILL.read_text()


def test_skill_md_exists_with_frontmatter_name():
    """SKILL.md must exist with `name: installation` in YAML frontmatter."""
    text = _skill_text()
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter (---)"
    end = text.index("\n---\n", 4)
    front = text[4:end]
    assert re.search(r"^name:\s*installation\s*$", front, re.MULTILINE), (
        f"frontmatter must declare `name: installation`; got:\n{front}"
    )


def test_skill_md_frontmatter_has_description():
    """SKILL.md frontmatter must have a non-empty `description:` field."""
    text = _skill_text()
    end = text.index("\n---\n", 4)
    front = text[4:end]
    m = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert m, "frontmatter must declare a non-empty `description`"
    assert len(m.group(1).strip()) >= 20, "description should be a real sentence, not a stub"


def test_skill_md_documents_uv_sync_basic():
    """SKILL.md must document the basic `uv sync` command."""
    text = _skill_text()
    assert re.search(r"```bash\s*\n\s*uv sync\s*\n\s*```", text), (
        "SKILL.md must include a fenced bash block with the bare `uv sync` command"
    )


def test_skill_md_documents_uv_sync_all_extras():
    """SKILL.md must document `uv sync --all-extras`."""
    assert "uv sync --all-extras" in _skill_text(), (
        "SKILL.md must document the `uv sync --all-extras` command"
    )


def test_skill_md_documents_fp8_inference_group():
    """SKILL.md must document the `uv sync --group fp8-inference` command."""
    assert "uv sync --group fp8-inference" in _skill_text(), (
        "SKILL.md must document `uv sync --group fp8-inference` for FP8 inference"
    )


def test_skill_md_mentions_deep_gemm():
    """SKILL.md must explain that the fp8-inference group provides deep-gemm."""
    assert "deep-gemm" in _skill_text(), (
        "SKILL.md must mention the `deep-gemm` package as the fp8-inference content"
    )


def test_pyproject_has_fp8_inference_dependency_group():
    """pyproject.toml must define an `fp8-inference` dependency group."""
    with open(PYPROJECT, "rb") as f:
        data = tomli.load(f)
    groups = data.get("dependency-groups", {})
    assert "fp8-inference" in groups, (
        f"`[dependency-groups]` must contain `fp8-inference`; saw: {sorted(groups.keys())}"
    )
    members = groups["fp8-inference"]
    assert isinstance(members, list) and len(members) >= 1
    assert any("deep-gemm" in m for m in members), (
        f"fp8-inference group must include deep-gemm; got: {members}"
    )


def test_pyproject_fp8_group_uses_prebuilt_wheel_url():
    """The fp8-inference dep must point at the prebuilt deep-gemm wheel URL."""
    with open(PYPROJECT, "rb") as f:
        data = tomli.load(f)
    members = data["dependency-groups"]["fp8-inference"]
    joined = "\n".join(members)
    assert WHEEL_URL in joined, (
        f"fp8-inference group must reference the prebuilt wheel URL\n"
        f"  expected: {WHEEL_URL}\n  got: {members}"
    )


def test_pyproject_still_parses_as_valid_toml():
    """pyproject.toml must remain a syntactically valid TOML file."""
    r = subprocess.run(
        ["python3", "-c", "import tomli; tomli.load(open('pyproject.toml','rb'))"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"pyproject.toml is not valid TOML:\n{r.stderr}"


def test_existing_skills_still_present():
    """Existing skills must not be removed by the change (regression guard)."""
    for name in ("inference-server", "toml-config"):
        p = REPO / "skills" / name / "SKILL.md"
        assert p.exists(), f"existing skill {name} disappeared at {p}"
