"""Behavioral tests for the reconcileColumnState fix in plugin-chart-ag-grid-table.

The PR adds `reconcileColumnState` and routes AgGridTable's column-state
restoration through it. We exercise the utility directly (its types are
erased at runtime so it imports cleanly under tsx) and check that
AgGridTable wires the helper into its `onGridReady` path.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")
PLUGIN = REPO / "superset-frontend/plugins/plugin-chart-ag-grid-table"
SRC = PLUGIN / "src/utils/reconcileColumnState.ts"
TEST_FILE = PLUGIN / "src/utils/reconcileColumnState.test.ts"
INDEX_TSX = PLUGIN / "src/AgGridTable/index.tsx"

HARNESS_JS = r"""
import { promises as fs } from 'node:fs';
import path from 'node:path';

const REPO = process.env.REPO || '/workspace/superset';
const SRC = path.join(
  REPO,
  'superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.ts',
);

const out = { ok: false, error: null, results: {} };

try {
  await fs.access(SRC);
} catch {
  out.error = `MISSING_SOURCE:${SRC}`;
  console.log(JSON.stringify(out));
  process.exit(0);
}

let mod;
try {
  mod = await import(SRC);
} catch (e) {
  out.error = `IMPORT_FAIL:${e && e.message ? e.message : String(e)}`;
  console.log(JSON.stringify(out));
  process.exit(0);
}

const reconcile = mod.default;
const { getLeafColumnIds } = mod;

if (typeof reconcile !== 'function') {
  out.error = 'NO_DEFAULT_EXPORT';
  console.log(JSON.stringify(out));
  process.exit(0);
}
if (typeof getLeafColumnIds !== 'function') {
  out.error = 'NO_GET_LEAF_COLUMN_IDS_NAMED_EXPORT';
  console.log(JSON.stringify(out));
  process.exit(0);
}

function safe(name, fn) {
  try {
    out.results[name] = { value: fn(), error: null };
  } catch (e) {
    out.results[name] = { value: null, error: String((e && e.message) || e) };
  }
}

safe('flatten_grouped', () =>
  getLeafColumnIds([
    { field: 'A' },
    { headerName: 'Metrics', children: [{ field: 'B' }, { field: 'C' }] },
    { field: 'D' },
  ]),
);

safe('flatten_nested', () =>
  getLeafColumnIds([
    {
      headerName: 'Group1',
      children: [
        { field: 'X' },
        { headerName: 'inner', children: [{ field: 'Y' }, { field: 'Z' }] },
      ],
    },
    { field: 'W' },
  ]),
);

safe('flatten_skips_invalid', () =>
  getLeafColumnIds([
    { field: 'a' },
    { headerName: 'g', children: [] },
    { headerName: 'g2' },
    { field: 123 },
    { field: 'b' },
  ]),
);

safe('reconcile_undefined_saved', () => reconcile(undefined, [{ field: 'a' }]));
safe('reconcile_empty_saved', () => reconcile([], [{ field: 'a' }]));

safe('reconcile_same_set_different_order', () =>
  reconcile(
    [{ colId: 'M2' }, { colId: 'D' }, { colId: 'M1' }],
    [{ field: 'D' }, { field: 'M1' }, { field: 'M2' }],
  ),
);

safe('reconcile_dimension_swap', () =>
  reconcile(
    [{ colId: 'OldDim' }, { colId: 'M1' }, { colId: 'M2' }, { colId: 'M3' }],
    [{ field: 'NewDim' }, { field: 'M1' }, { field: 'M2' }, { field: 'M3' }],
  ),
);

safe('reconcile_all_stale', () =>
  reconcile([{ colId: 'X' }, { colId: 'Y' }], [{ field: 'A' }, { field: 'B' }]),
);

safe('reconcile_subset_added_col', () =>
  reconcile(
    [{ colId: 'A' }, { colId: 'B' }],
    [{ field: 'A' }, { field: 'B' }, { field: 'C' }],
  ),
);

safe('reconcile_preserves_fields', () =>
  reconcile(
    [{ colId: 'A', width: 100, sort: 'asc' }, { colId: 'B', width: 200 }],
    [{ field: 'A' }, { field: 'B' }],
  ),
);

safe('reconcile_with_grouped_coldefs', () =>
  reconcile(
    [{ colId: 'A' }, { colId: 'B' }, { colId: 'C' }],
    [
      { field: 'A' },
      { headerName: 'g', children: [{ field: 'B' }, { field: 'C' }] },
    ],
  ),
);

out.ok = true;
console.log(JSON.stringify(out));
"""


# ---- helpers ----------------------------------------------------------------


_HARNESS_CACHE: dict | None = None


def _run_harness() -> dict:
    global _HARNESS_CACHE
    if _HARNESS_CACHE is not None:
        return _HARNESS_CACHE
    env = {**os.environ, "REPO": str(REPO)}
    with tempfile.NamedTemporaryFile(
        "w", suffix=".mjs", delete=False, encoding="utf-8"
    ) as f:
        f.write(HARNESS_JS)
        harness_path = f.name
    try:
        r = subprocess.run(
            ["tsx", harness_path],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    finally:
        try:
            os.unlink(harness_path)
        except OSError:
            pass
    assert r.returncode == 0, (
        f"harness exited {r.returncode}\nstderr:\n{r.stderr[-2000:]}\n"
        f"stdout:\n{r.stdout[-2000:]}"
    )
    last = r.stdout.strip().splitlines()[-1]
    _HARNESS_CACHE = json.loads(last)
    return _HARNESS_CACHE


def _strip_license(src: str) -> str:
    return re.sub(r"^/\*[\s\S]*?\*/\s*", "", src, count=1)


# ---- f2p: behavior of the new utility --------------------------------------


def test_utility_source_file_exists():
    assert SRC.exists(), f"missing {SRC}"


def test_harness_imports_and_runs():
    data = _run_harness()
    assert data.get("ok") is True, f"harness failed: {data.get('error')!r}"


def test_get_leaf_column_ids_flattens_groups_in_visual_order():
    data = _run_harness()
    res = data["results"]["flatten_grouped"]
    assert res["error"] is None, res
    assert res["value"] == ["A", "B", "C", "D"]


def test_get_leaf_column_ids_flattens_nested_groups():
    data = _run_harness()
    res = data["results"]["flatten_nested"]
    assert res["error"] is None, res
    assert res["value"] == ["X", "Y", "Z", "W"]


def test_get_leaf_column_ids_skips_invalid_entries():
    data = _run_harness()
    res = data["results"]["flatten_skips_invalid"]
    assert res["error"] is None, res
    assert res["value"] == ["a", "b"]


def test_reconcile_returns_null_for_undefined_saved_state():
    data = _run_harness()
    res = data["results"]["reconcile_undefined_saved"]
    assert res["error"] is None, res
    assert res["value"] is None


def test_reconcile_returns_null_for_empty_saved_state():
    data = _run_harness()
    res = data["results"]["reconcile_empty_saved"]
    assert res["error"] is None, res
    assert res["value"] is None


def test_reconcile_keeps_saved_order_when_set_unchanged():
    data = _run_harness()
    res = data["results"]["reconcile_same_set_different_order"]
    assert res["error"] is None, res
    assert res["value"] == {
        "applyOrder": True,
        "columnState": [
            {"colId": "M2"},
            {"colId": "D"},
            {"colId": "M1"},
        ],
    }


def test_reconcile_drops_stale_dim_and_disables_applyorder():
    data = _run_harness()
    res = data["results"]["reconcile_dimension_swap"]
    assert res["error"] is None, res
    assert res["value"] == {
        "applyOrder": False,
        "columnState": [
            {"colId": "M1"},
            {"colId": "M2"},
            {"colId": "M3"},
        ],
    }


def test_reconcile_returns_null_when_all_saved_stale():
    data = _run_harness()
    res = data["results"]["reconcile_all_stale"]
    assert res["error"] is None, res
    assert res["value"] is None


def test_reconcile_disables_applyorder_when_column_added():
    data = _run_harness()
    res = data["results"]["reconcile_subset_added_col"]
    assert res["error"] is None, res
    val = res["value"]
    assert val is not None
    assert val["applyOrder"] is False
    assert val["columnState"] == [{"colId": "A"}, {"colId": "B"}]


def test_reconcile_preserves_extra_columnstate_fields():
    data = _run_harness()
    res = data["results"]["reconcile_preserves_fields"]
    assert res["error"] is None, res
    assert res["value"] == {
        "applyOrder": True,
        "columnState": [
            {"colId": "A", "width": 100, "sort": "asc"},
            {"colId": "B", "width": 200},
        ],
    }


def test_reconcile_handles_grouped_column_defs():
    data = _run_harness()
    res = data["results"]["reconcile_with_grouped_coldefs"]
    assert res["error"] is None, res
    val = res["value"]
    assert val is not None
    assert val["applyOrder"] is True
    assert val["columnState"] == [
        {"colId": "A"},
        {"colId": "B"},
        {"colId": "C"},
    ]


# ---- f2p: AgGridTable wiring ------------------------------------------------


def test_aggridtable_routes_through_reconcile():
    text = INDEX_TSX.read_text(encoding="utf-8")
    assert re.search(
        r"import\s+\w+\s+from\s+['\"](?:\.\./)+utils/reconcileColumnState['\"]",
        text,
    ), "AgGridTable does not import the reconcileColumnState helper"
    assert re.search(r"reconcileColumnState\s*\(", text), (
        "AgGridTable imports reconcileColumnState but never calls it"
    )
    bug_pattern = re.compile(
        r"applyColumnState\?\s*\(\s*\{\s*"
        r"state\s*:\s*chartState\.columnState[^}]*"
        r"applyOrder\s*:\s*true",
        re.S,
    )
    assert not bug_pattern.search(text), (
        "AgGridTable still applies chartState.columnState directly "
        "with applyOrder: true; reconcile is not in the path"
    )


# ---- agent_config: programmatic checks of repo-wide rules ------------------


def test_no_any_types_in_new_utility():
    text = SRC.read_text(encoding="utf-8")
    body = _strip_license(text)
    assert not re.search(r":\s*any\b", body), "found `: any` annotation in new utility"
    assert not re.search(r"\bas\s+any\b", body), "found `as any` cast in new utility"
    assert not re.search(r"<any\b", body), "found generic <any> in new utility"


def test_new_utility_has_apache_license_header():
    text = SRC.read_text(encoding="utf-8")
    assert "Licensed to the Apache Software Foundation" in text, (
        "new utility file is missing the ASF license header"
    )
    assert "Apache License, Version 2.0" in text


def test_test_file_has_apache_license_header():
    if not TEST_FILE.exists():
        pytest.skip("no test file added by this PR")
    text = TEST_FILE.read_text(encoding="utf-8")
    assert "Licensed to the Apache Software Foundation" in text, (
        "new test file is missing the ASF license header"
    )


def test_test_file_uses_test_not_describe():
    if not TEST_FILE.exists():
        pytest.skip("no test file added by this PR")
    body = _strip_license(TEST_FILE.read_text(encoding="utf-8"))
    assert not re.search(r"\bdescribe\s*\(", body), (
        "new test file uses describe() blocks; AGENTS.md says use test()"
    )
    assert re.search(r"\btest\s*\(", body), (
        "new test file has no test() calls"
    )


def test_no_time_specific_words_in_new_code_comments():
    text = _strip_license(SRC.read_text(encoding="utf-8"))
    comments = []
    for m in re.finditer(r"//[^\n]*", text):
        comments.append(m.group(0))
    for m in re.finditer(r"/\*[\s\S]*?\*/", text):
        comments.append(m.group(0))
    joined = "\n".join(comments)
    for word in ("now", "currently", "today"):
        assert not re.search(rf"\b{word}\b", joined, re.I), (
            f"comment in new utility uses time-specific word {word!r}"
        )


# ---- p2p: repo build sanity --------------------------------------------------


def test_node_and_tsx_available():
    r = subprocess.run(
        ["tsx", "--version"], capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, r.stderr


def test_repo_layout_intact():
    assert PLUGIN.is_dir(), f"missing plugin dir {PLUGIN}"
    assert INDEX_TSX.exists(), f"missing {INDEX_TSX}"


# === PR-added f2p tests ===
# At the base commit the test file does not exist -> each test fails.
# After the gold patch the file is present with the expected content -> each passes.


def test_pr_added_getLeafColumnIds_flattens_grouped_column_defs_in():
    """fail_to_pass | PR added test 'getLeafColumnIds flattens grouped column defs in visual order' in reconcileColumnState.test.ts"""
    assert TEST_FILE.exists(), f"missing {TEST_FILE}"
    text = TEST_FILE.read_text(encoding="utf-8")
    assert "getLeafColumnIds flattens grouped column defs in visual order" in text, (
        "test file missing required test case")


def test_pr_added_preserves_saved_order_when_the_current_column_se():
    """fail_to_pass | PR added test 'preserves saved order when the current column set is unchanged' in reconcileColumnState.test.ts"""
    assert TEST_FILE.exists(), f"missing {TEST_FILE}"
    text = TEST_FILE.read_text(encoding="utf-8")
    assert "preserves saved order when the current column set is unchanged" in text, (
        "test file missing required test case")


def test_pr_added_drops_stale_order_when_a_dynamic_group_by_swaps_():
    """fail_to_pass | PR added test 'drops stale order when a dynamic group by swaps the dimension column' in reconcileColumnState.test.ts"""
    assert TEST_FILE.exists(), f"missing {TEST_FILE}"
    text = TEST_FILE.read_text(encoding="utf-8")
    assert "drops stale order when a dynamic group by swaps the dimension column" in text, (
        "test file missing required test case")
