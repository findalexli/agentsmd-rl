"""Behavioral tests for apache/airflow PR #65272: Polish translation completeness.

Tests verify:
- 17 missing PL translation keys are present (f2p)
- 3 unused dagWarnings.error_* keys are removed (f2p)
- Bulk delete strings now use "grupowy" terminology (f2p)
- Deactivated status uses "Deaktywowany" (not "Dezaktywowany") (f2p)
- pl.md contains the new "Terminology Glossary" section (f2p)
- All 4 PL locale files remain valid JSON (p2p)
- Existing PL translations preserved (p2p)
- Polish-required plural suffixes (`_few`, `_many`) preserved (p2p)
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/airflow")
LOCALES = REPO / "airflow-core/src/airflow/ui/public/i18n/locales"
PL = LOCALES / "pl"
EN = LOCALES / "en"
PL_MD = REPO / ".github/skills/airflow-translations/locales/pl.md"


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _path_get(d: dict, dotted: str):
    cur = d
    for part in dotted.split("."):
        assert isinstance(cur, dict), f"expected dict at {part!r} for {dotted!r}, got {type(cur).__name__}"
        assert part in cur, f"missing key {part!r} (path {dotted!r})"
        cur = cur[part]
    return cur


# ---------- f2p: missing keys added ----------

def test_admin_slotsHelperText_present():
    """admin.json must have pools.form.slotsHelperText with non-empty Polish translation."""
    d = _load(PL / "admin.json")
    val = _path_get(d, "pools.form.slotsHelperText")
    assert isinstance(val, str) and val.strip(), "slotsHelperText must be non-empty string"
    assert not val.startswith("TODO"), f"slotsHelperText must be translated, not a TODO stub: {val!r}"


def test_common_errors_forbidden_present():
    """common.json must have errors.forbidden.{title, description} with non-empty translations."""
    d = _load(PL / "common.json")
    title = _path_get(d, "errors.forbidden.title")
    desc = _path_get(d, "errors.forbidden.description")
    for label, val in [("title", title), ("description", desc)]:
        assert isinstance(val, str) and val.strip(), f"errors.forbidden.{label} must be non-empty string"
        assert not val.startswith("TODO"), f"errors.forbidden.{label} not translated: {val!r}"


def test_common_generateToken_present():
    """common.json must have generateToken with non-empty Polish translation."""
    d = _load(PL / "common.json")
    val = _path_get(d, "generateToken")
    assert isinstance(val, str) and val.strip()
    assert not val.startswith("TODO"), f"generateToken not translated: {val!r}"


def test_common_asset_materialization_present():
    """common.json must have runTypes.asset_materialization with non-empty translation."""
    d = _load(PL / "common.json")
    val = _path_get(d, "runTypes.asset_materialization")
    assert isinstance(val, str) and val.strip()
    assert not val.startswith("TODO"), f"asset_materialization not translated: {val!r}"


def test_common_tokenGeneration_subtree_present():
    """common.json must have all 10 tokenGeneration.* keys, each translated."""
    d = _load(PL / "common.json")
    expected_keys = [
        "apiToken", "cliToken", "errorDescription", "errorTitle",
        "generate", "selectType", "title",
        "tokenExpiresIn", "tokenGenerated", "tokenShownOnce",
    ]
    tg = _path_get(d, "tokenGeneration")
    assert isinstance(tg, dict), "tokenGeneration must be an object"
    missing = [k for k in expected_keys if k not in tg]
    assert not missing, f"tokenGeneration missing subkeys: {missing}"
    for k in expected_keys:
        v = tg[k]
        assert isinstance(v, str) and v.strip(), f"tokenGeneration.{k} must be non-empty"
        assert not v.startswith("TODO"), f"tokenGeneration.{k} not translated: {v!r}"


def test_common_tokenGeneration_preserves_placeholder():
    """tokenGeneration.tokenExpiresIn must preserve the {{duration}} placeholder."""
    d = _load(PL / "common.json")
    val = _path_get(d, "tokenGeneration.tokenExpiresIn")
    assert "{{duration}}" in val, f"placeholder lost: {val!r}"


def test_dag_runTypeLegend_present():
    """dag.json must have grid.runTypeLegend with non-empty translation."""
    d = _load(PL / "dag.json")
    val = _path_get(d, "grid.runTypeLegend")
    assert isinstance(val, str) and val.strip()
    assert not val.startswith("TODO"), f"runTypeLegend not translated: {val!r}"


def test_dag_header_status_deactivated_present():
    """dag.json must have header.status.deactivated with non-empty translation."""
    d = _load(PL / "dag.json")
    val = _path_get(d, "header.status.deactivated")
    assert isinstance(val, str) and val.strip()
    assert not val.startswith("TODO"), f"deactivated not translated: {val!r}"


# ---------- f2p: unused keys removed ----------

def test_components_dagWarnings_unused_keys_removed():
    """pl/components.json must NOT contain dagWarnings.error_few / error_many / error_other.

    The English source only has `dagWarnings.error_one`, so these PL plural variants
    are unused. The pre-existing _few/_many/_other PL entries must be removed.
    """
    d = _load(PL / "components.json")
    dw = d.get("dagWarnings", {})
    forbidden = ["error_few", "error_many", "error_other"]
    present = [k for k in forbidden if k in dw]
    assert not present, f"dagWarnings still has unused plural keys: {present}"
    # error_one must remain
    assert "error_one" in dw, "dagWarnings.error_one must still be present"


# ---------- f2p: glossary terminology applied ----------

def test_bulkDelete_uses_grupowy_terminology():
    """toaster.bulkDelete.error and toaster.bulkDelete.success.title must use
    'grupowego' (not 'masowego') per the new terminology glossary."""
    d = _load(PL / "common.json")
    err = _path_get(d, "toaster.bulkDelete.error")
    title = _path_get(d, "toaster.bulkDelete.success.title")
    assert "grupowego" in err, f"bulkDelete.error must contain 'grupowego': {err!r}"
    assert "masowego" not in err, f"bulkDelete.error must NOT contain 'masowego': {err!r}"
    assert "grupowego" in title, f"bulkDelete.success.title must contain 'grupowego': {title!r}"
    assert "masowego" not in title, f"bulkDelete.success.title must NOT contain 'masowego': {title!r}"


def test_dag_deactivated_uses_deaktywowany():
    """header.status.deactivated must use 'Deaktywowany' (not 'Dezaktywowany')."""
    d = _load(PL / "dag.json")
    val = _path_get(d, "header.status.deactivated")
    # Accept Deaktywowany / Deaktywowana / Deaktywowane (gender variants)
    assert "Deaktywowan" in val, f"expected Deaktywowan* form, got {val!r}"
    assert "Dezaktywowan" not in val, f"must not use Dezaktywowan* form: {val!r}"


# ---------- f2p: pl.md glossary section added ----------

def test_pl_md_has_terminology_glossary_heading():
    """pl.md must contain a 'Terminology Glossary' section heading."""
    text = PL_MD.read_text(encoding="utf-8")
    assert "## Terminology Glossary" in text, "pl.md missing '## Terminology Glossary' heading"


def test_pl_md_glossary_lists_required_terms():
    """The Terminology Glossary in pl.md must mention the three required terms:
    Zabierający (consuming asset), grupowy (bulk), and Deaktywowany (deactivated)."""
    text = PL_MD.read_text(encoding="utf-8")
    # Limit search to the new section for precision
    if "## Terminology Glossary" in text:
        glossary = text.split("## Terminology Glossary", 1)[1]
        # Cut at next ## heading if any
        if "\n## " in glossary:
            glossary = glossary.split("\n## ", 1)[0]
    else:
        glossary = text
    for required in ["Zabieraj", "grupow", "Deaktywowan"]:
        assert required in glossary, f"glossary missing required term stem: {required!r}"
    for avoided in ["Konsumuj", "masow", "Dezaktywowan"]:
        assert avoided in glossary, f"glossary should also reference avoided term {avoided!r} (in 'Avoid' column)"


# ---------- p2p: regression / validity ----------

def test_all_pl_locale_files_valid_json():
    """All 4 PL locale files must remain valid JSON."""
    for name in ["admin.json", "common.json", "components.json", "dag.json"]:
        p = PL / name
        assert p.exists(), f"missing {p}"
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise AssertionError(f"{name} is not valid JSON: {e}")


def test_existing_translations_preserved():
    """Pre-existing translations must remain unchanged after the fix."""
    common = _load(PL / "common.json")
    # Sample of pre-existing keys with their established values
    assert _path_get(common, "logout") == "Wyloguj"
    assert _path_get(common, "reset") == "Resetuj"
    assert _path_get(common, "logicalDate") == "Data logiczna"
    admin = _load(PL / "admin.json")
    assert _path_get(admin, "pools.form.slots") == "Miejsca"


def test_polish_plural_suffixes_preserved():
    """Polish requires _few and _many plural forms; existing pluralized entries
    must keep them (only the unused dagWarnings.error_* set is removed)."""
    components = _load(PL / "components.json")
    # Pre-existing dagWarnings.warning_* plurals must still be present
    dw = components.get("dagWarnings", {})
    for k in ["warning_few", "warning_many", "warning_one"]:
        assert k in dw, f"dagWarnings.{k} should remain"


def test_python_can_parse_all_pl_files():
    """Sanity: python -m json.tool succeeds on each PL locale file (subprocess execution)."""
    for name in ["admin.json", "common.json", "components.json", "dag.json"]:
        path = PL / name
        r = subprocess.run(
            ["python3", "-c", f"import json; json.load(open({str(path)!r}, encoding='utf-8'))"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"python json parse failed for {name}: {r.stderr}"


def test_git_diff_touches_expected_files():
    """git diff (subprocess) shows the 5 expected files modified, ensuring a
    meaningful change set rather than a no-op."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    changed = {line.strip() for line in r.stdout.splitlines() if line.strip()}
    required = {
        ".github/skills/airflow-translations/locales/pl.md",
        "airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json",
        "airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json",
        "airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json",
        "airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json",
    }
    missing = required - changed
    assert not missing, f"expected file modifications missing from git diff: {missing}"
