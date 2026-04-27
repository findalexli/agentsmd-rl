"""Behavioral tests for the LightGlue trust_remote_code removal + TRF014 linter rule."""

import ast
import importlib
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path("/workspace/transformers")
LIGHTGLUE_DIR = REPO / "src/transformers/models/lightglue"
MLINTER_DIR = REPO / "utils/mlinter"


def _ensure_repo_on_path():
    p = str(REPO)
    if p not in sys.path:
        sys.path.insert(0, p)


def _import_trf014():
    _ensure_repo_on_path()
    # Reload in case rule discovery imported a stub earlier; we want the user-authored module.
    if "utils.mlinter.trf014" in sys.modules:
        return importlib.reload(sys.modules["utils.mlinter.trf014"])
    return importlib.import_module("utils.mlinter.trf014")


def _run_trf014(source: str):
    mod = _import_trf014()
    # The mlinter discovery sets RULE_ID at runtime; emulate it for direct calls.
    mod.RULE_ID = "TRF014"
    tree = ast.parse(source)
    return mod.check(tree, Path("synthetic.py"), source.splitlines())


# ---------------------------------------------------------------------------
# F2P — TRF014 rule must exist and be wired into the linter spec
# ---------------------------------------------------------------------------

def test_trf014_module_file_exists():
    """A new linter rule module trf014.py must exist in utils/mlinter/."""
    assert (MLINTER_DIR / "trf014.py").is_file(), \
        "utils/mlinter/trf014.py is missing"


def test_trf014_in_rules_toml():
    """rules.toml must declare a [rules.TRF014] block with required spec fields."""
    text = (MLINTER_DIR / "rules.toml").read_text(encoding="utf-8")
    assert "[rules.TRF014]" in text, "rules.toml is missing the TRF014 spec block"
    assert "[rules.TRF014.explanation]" in text, \
        "TRF014 spec block must include an [rules.TRF014.explanation] section"
    # Required spec fields per mlinter._load_rule_specs
    for required in ("description", "default_enabled", "allowlist_models"):
        assert required in text.split("[rules.TRF014]", 1)[1].split("[rules.", 1)[0], \
            f"TRF014 spec is missing the {required!r} field"
    # Required explanation fields
    explanation_block = text.split("[rules.TRF014.explanation]", 1)[1]
    for required in ("what_it_does", "why_bad", "bad_example", "good_example"):
        assert required in explanation_block, \
            f"TRF014 explanation block is missing {required!r}"


def test_trf014_default_enabled_true():
    """TRF014 must be on by default — security rules should not require opt-in."""
    import tomllib
    text = (MLINTER_DIR / "rules.toml").read_text(encoding="utf-8")
    parsed = tomllib.loads(text)
    assert parsed["rules"]["TRF014"]["default_enabled"] is True, \
        "TRF014 must have default_enabled = true"


# ---------------------------------------------------------------------------
# F2P — TRF014 visitor flags the three documented patterns
# ---------------------------------------------------------------------------

def test_trf014_detects_keyword_argument():
    """Pattern 1: foo(..., trust_remote_code=...)"""
    src = "AutoModel.from_pretrained('m', trust_remote_code=True)\n"
    violations = _run_trf014(src)
    assert len(violations) == 1, f"Expected exactly 1 violation, got {len(violations)}: {violations}"
    assert "trust_remote_code" in violations[0].message


def test_trf014_detects_dict_kwargs():
    """Pattern 2: foo(**{'trust_remote_code': ...})"""
    src = "foo(x=1, **{'trust_remote_code': True})\n"
    violations = _run_trf014(src)
    assert len(violations) == 1, f"Expected exactly 1 violation, got {violations}"
    assert "trust_remote_code" in violations[0].message


def test_trf014_detects_dict_constructor_kwargs():
    """Pattern 3: foo(**dict(trust_remote_code=...)) — at least one violation must mention the dict-constructor splat."""
    src = "foo(**dict(trust_remote_code=False, other=1))\n"
    violations = _run_trf014(src)
    assert len(violations) >= 1, f"Expected violations, got {violations}"
    assert any("dict constructor" in v.message for v in violations), (
        f"No dict-constructor violation among: {violations}"
    )
    # Every violation must mention trust_remote_code
    for v in violations:
        assert "trust_remote_code" in v.message


def test_trf014_clean_code_no_violation():
    """Code without trust_remote_code must not be flagged."""
    src = (
        "AutoModel.from_pretrained('m')\n"
        "foo(x=1, y=2)\n"
        "bar(**{'something_else': True})\n"
        "baz(**dict(other=1))\n"
    )
    violations = _run_trf014(src)
    assert violations == [], f"Unexpected violations: {violations}"


def test_trf014_does_not_flag_pre_bound_kwargs():
    """Per the rule's docstring, pre-bound kwargs (kw = {...}; foo(**kw)) are out of scope."""
    src = "kw = {'trust_remote_code': True}\nfoo(**kw)\n"
    violations = _run_trf014(src)
    assert violations == [], f"Pre-bound kwargs must not be flagged: {violations}"


# ---------------------------------------------------------------------------
# F2P — LightGlue source files must no longer use trust_remote_code
# ---------------------------------------------------------------------------

def _trf014_check_file(path: Path):
    """Run the TRF014 visitor against a real source file."""
    src = path.read_text(encoding="utf-8")
    return _run_trf014(src)


def test_lightglue_modeling_no_trust_remote_code_calls():
    """modeling_lightglue.py must not pass trust_remote_code to any callable."""
    violations = _trf014_check_file(LIGHTGLUE_DIR / "modeling_lightglue.py")
    assert violations == [], (
        "modeling_lightglue.py still passes trust_remote_code to a callable: "
        + "; ".join(f"L{v.line_number}: {v.message}" for v in violations)
    )


def test_lightglue_modular_no_trust_remote_code_calls():
    """modular_lightglue.py must not pass trust_remote_code to any callable."""
    violations = _trf014_check_file(LIGHTGLUE_DIR / "modular_lightglue.py")
    assert violations == [], (
        "modular_lightglue.py still passes trust_remote_code to a callable: "
        + "; ".join(f"L{v.line_number}: {v.message}" for v in violations)
    )


def test_lightglue_configuration_no_trust_remote_code_calls():
    """configuration_lightglue.py must not pass trust_remote_code to any callable."""
    violations = _trf014_check_file(LIGHTGLUE_DIR / "configuration_lightglue.py")
    assert violations == [], (
        "configuration_lightglue.py still passes trust_remote_code to a callable: "
        + "; ".join(f"L{v.line_number}: {v.message}" for v in violations)
    )


def _lightglue_config_class_attrs(filename: str):
    src = (LIGHTGLUE_DIR / filename).read_text(encoding="utf-8")
    tree = ast.parse(src)
    attrs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LightGlueConfig":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    attrs.append(item.target.id)
                elif isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            attrs.append(t.id)
    return attrs


def test_lightglue_config_no_trust_remote_code_field_in_modular():
    """LightGlueConfig (in modular_lightglue.py) must not declare a trust_remote_code attribute."""
    attrs = _lightglue_config_class_attrs("modular_lightglue.py")
    assert "trust_remote_code" not in attrs, \
        f"modular_lightglue.py LightGlueConfig still declares trust_remote_code (attrs: {attrs})"


def test_lightglue_config_no_trust_remote_code_field_in_configuration():
    """LightGlueConfig (in configuration_lightglue.py) must not declare a trust_remote_code attribute."""
    attrs = _lightglue_config_class_attrs("configuration_lightglue.py")
    assert "trust_remote_code" not in attrs, \
        f"configuration_lightglue.py LightGlueConfig still declares trust_remote_code (attrs: {attrs})"


def test_lightglue_docstring_does_not_document_trust_remote_code():
    """The trust_remote_code argument must be removed from the LightGlueConfig docstring."""
    for fname in ("configuration_lightglue.py", "modular_lightglue.py"):
        src = (LIGHTGLUE_DIR / fname).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "LightGlueConfig":
                doc = ast.get_docstring(node) or ""
                assert "trust_remote_code" not in doc, \
                    f"{fname}: LightGlueConfig docstring still mentions trust_remote_code"


# ---------------------------------------------------------------------------
# P2P — repo-level invariants that hold on both base and gold
# ---------------------------------------------------------------------------

def test_helpers_module_loadable():
    """utils.mlinter._helpers continues to expose Violation."""
    _ensure_repo_on_path()
    if "utils.mlinter._helpers" in sys.modules:
        del sys.modules["utils.mlinter._helpers"]
    helpers = importlib.import_module("utils.mlinter._helpers")
    v = helpers.Violation(file_path=Path("a.py"), line_number=1, message="m")
    assert v.line_number == 1
    assert v.message == "m"


def test_existing_trf013_runs_against_modular_lightglue():
    """An existing rule (TRF013) keeps functioning on the modular_lightglue.py source."""
    _ensure_repo_on_path()
    if "utils.mlinter.trf013" in sys.modules:
        del sys.modules["utils.mlinter.trf013"]
    trf013 = importlib.import_module("utils.mlinter.trf013")
    trf013.RULE_ID = "TRF013"
    src = (LIGHTGLUE_DIR / "modular_lightglue.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    result = trf013.check(tree, LIGHTGLUE_DIR / "modular_lightglue.py", src.splitlines())
    assert isinstance(result, list)


def test_lightglue_modules_parse_as_python():
    """All three LightGlue modules must remain syntactically valid Python."""
    for fname in ("configuration_lightglue.py", "modeling_lightglue.py", "modular_lightglue.py"):
        path = LIGHTGLUE_DIR / fname
        src = path.read_text(encoding="utf-8")
        ast.parse(src)  # must not raise


def test_rules_toml_parses_as_toml():
    """rules.toml must remain valid TOML."""
    import tomllib
    text = (MLINTER_DIR / "rules.toml").read_text(encoding="utf-8")
    parsed = tomllib.loads(text)
    assert "rules" in parsed
    # Every existing rule (TRF001..TRF013) is still present
    for rule_id in [f"TRF{i:03d}" for i in range(1, 14)]:
        assert rule_id in parsed["rules"], f"existing rule {rule_id} missing from rules.toml"


def test_python_compiles_lightglue_files():
    """Use python -m py_compile as an out-of-process syntactic sanity check."""
    files = [
        LIGHTGLUE_DIR / "configuration_lightglue.py",
        LIGHTGLUE_DIR / "modeling_lightglue.py",
        LIGHTGLUE_DIR / "modular_lightglue.py",
    ]
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, files)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"
