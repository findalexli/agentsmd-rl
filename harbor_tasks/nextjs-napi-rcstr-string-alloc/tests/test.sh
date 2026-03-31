#!/usr/bin/env bash
# Verifier for nextjs-napi-rcstr-string-alloc
#
# Bug: #[napi(object)] structs use String fields despite source data being RcStr,
# causing unnecessary heap allocations at the NAPI boundary.
#
# All checks are structural because this is Rust code in the turbopack workspace
# (~200+ crates); cargo check would exceed the test timeout.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

ENDPOINT="/workspace/next.js/crates/next-napi-bindings/src/next_api/endpoint.rs"
PROJECT="/workspace/next.js/crates/next-napi-bindings/src/next_api/project.rs"
UTILS="/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$ENDPOINT" ] || [ ! -f "$PROJECT" ] || [ ! -f "$UTILS" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]    (0.25): NapiAssetPath fields are RcStr, From impl avoids alloc
#   TEST 2 [pr_diff]    (0.20): NapiIssue/NapiAdditionalIssueSource fields are RcStr
#   TEST 3 [pr_diff]    (0.15): NapiSource/NapiDiagnostic fields are RcStr
#   TEST 4 [pr_diff]    (0.10): NapiRoute.pathname is RcStr, from_route accepts RcStr
#   TEST 5 [pr_diff]    (0.10): From impls avoid allocating conversions on RcStr data
#   TEST 6 [pr_diff]    (0.10): P2P — severity/stage stay String, helper structs intact
#   TEST 7 [structural] (0.10): Anti-stub — imports, #[napi] attrs, impl blocks present
#   TOTAL               = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# TEST 1 [pr_diff] (0.25): NapiAssetPath fields use RcStr (positive check)
# WHY structural: Rust code requiring full turbopack workspace to compile
###############################################################################
echo ""
echo "TEST 1: [pr_diff] NapiAssetPath fields are RcStr, From impl avoids allocation"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/endpoint.rs") as f:
    src = f.read()

# turbo_rcstr::RcStr must be imported
if not re.search(r'use\s+turbo_rcstr::RcStr', src):
    print("FAIL: turbo_rcstr::RcStr not imported in endpoint.rs")
    sys.exit(1)

# Find NapiAssetPath struct
struct_match = re.search(r'pub struct NapiAssetPath\s*\{([^}]+)\}', src)
if not struct_match:
    print("FAIL: NapiAssetPath struct not found")
    sys.exit(1)

body = struct_match.group(1)

# Positive check: path field IS RcStr
if not re.search(r'pub\s+path\s*:\s*RcStr', body):
    print("FAIL: NapiAssetPath.path is not RcStr")
    sys.exit(1)

# Positive check: content_hash field IS RcStr
if not re.search(r'pub\s+content_hash\s*:\s*RcStr', body):
    print("FAIL: NapiAssetPath.content_hash is not RcStr")
    sys.exit(1)

# From<AssetPath> impl must not use allocating conversions
from_match = re.search(r'impl\s+From<AssetPath>\s+for\s+NapiAssetPath\s*\{([\s\S]*?)\n\}', src)
if not from_match:
    print("FAIL: From<AssetPath> impl not found")
    sys.exit(1)

from_body = from_match.group(1)
if '.into_owned()' in from_body or '.to_string()' in from_body or 'String::from' in from_body:
    print("FAIL: From<AssetPath> still uses allocating conversion")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 2 [pr_diff] (0.20): NapiIssue and NapiAdditionalIssueSource use RcStr
###############################################################################
echo ""
echo "TEST 2: [pr_diff] NapiIssue/NapiAdditionalIssueSource RcStr-sourced fields are RcStr"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs") as f:
    src = f.read()

# turbo_rcstr::RcStr must be imported
if not re.search(r'use\s+turbo_rcstr::RcStr', src):
    print("FAIL: turbo_rcstr::RcStr not imported in utils.rs")
    sys.exit(1)

# NapiIssue struct — file_path and documentation_link should be RcStr
issue_match = re.search(r'pub struct NapiIssue\s*\{([\s\S]*?)\n\}', src)
if not issue_match:
    print("FAIL: NapiIssue struct not found")
    sys.exit(1)

issue_body = issue_match.group(1)

if not re.search(r'pub\s+file_path\s*:\s*RcStr', issue_body):
    print("FAIL: NapiIssue.file_path is not RcStr")
    sys.exit(1)

if not re.search(r'pub\s+documentation_link\s*:\s*RcStr', issue_body):
    print("FAIL: NapiIssue.documentation_link is not RcStr")
    sys.exit(1)

# severity and stage should remain String (sourced from non-RcStr)
if not re.search(r'pub\s+severity\s*:\s*String', issue_body):
    print("FAIL: NapiIssue.severity should remain String")
    sys.exit(1)
if not re.search(r'pub\s+stage\s*:\s*String', issue_body):
    print("FAIL: NapiIssue.stage should remain String")
    sys.exit(1)

# NapiAdditionalIssueSource — description should be RcStr
addl_match = re.search(r'pub struct NapiAdditionalIssueSource\s*\{([\s\S]*?)\n\}', src)
if not addl_match:
    print("FAIL: NapiAdditionalIssueSource struct not found")
    sys.exit(1)

addl_body = addl_match.group(1)
if not re.search(r'pub\s+description\s*:\s*RcStr', addl_body):
    print("FAIL: NapiAdditionalIssueSource.description is not RcStr")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): NapiSource and NapiDiagnostic fields are RcStr
###############################################################################
echo ""
echo "TEST 3: [pr_diff] NapiSource and NapiDiagnostic fields are RcStr"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs") as f:
    src = f.read()

# NapiSource: ident and file_path should be RcStr
source_match = re.search(r'pub struct NapiSource\s*\{([\s\S]*?)\n\}', src)
if not source_match:
    print("FAIL: NapiSource struct not found")
    sys.exit(1)

source_body = source_match.group(1)
if not re.search(r'pub\s+ident\s*:\s*RcStr', source_body):
    print("FAIL: NapiSource.ident is not RcStr")
    sys.exit(1)
if not re.search(r'pub\s+file_path\s*:\s*RcStr', source_body):
    print("FAIL: NapiSource.file_path is not RcStr")
    sys.exit(1)

# NapiDiagnostic: category, name should be RcStr; payload should use RcStr keys/values
diag_match = re.search(r'pub struct NapiDiagnostic\s*\{([\s\S]*?)\n\}', src)
if not diag_match:
    print("FAIL: NapiDiagnostic struct not found")
    sys.exit(1)

diag_body = diag_match.group(1)
if not re.search(r'pub\s+category\s*:\s*RcStr', diag_body):
    print("FAIL: NapiDiagnostic.category is not RcStr")
    sys.exit(1)
if not re.search(r'pub\s+name\s*:\s*RcStr', diag_body):
    print("FAIL: NapiDiagnostic.name is not RcStr")
    sys.exit(1)

# payload should not use String keys/values
if re.search(r'FxHashMap<String', diag_body):
    print("FAIL: NapiDiagnostic.payload still uses String in FxHashMap")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): NapiRoute.pathname is RcStr, from_route accepts RcStr
###############################################################################
echo ""
echo "TEST 4: [pr_diff] NapiRoute.pathname is RcStr, from_route param updated"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/project.rs") as f:
    src = f.read()

# NapiRoute.pathname should be RcStr
route_match = re.search(r'pub struct NapiRoute\s*\{([\s\S]*?)\n\}', src)
if not route_match:
    print("FAIL: NapiRoute struct not found")
    sys.exit(1)

route_body = route_match.group(1)
if not re.search(r'pub\s+pathname\s*:\s*RcStr', route_body):
    print("FAIL: NapiRoute.pathname is not RcStr")
    sys.exit(1)

# from_route should accept RcStr (not String) for pathname
from_route_match = re.search(r'fn\s+from_route\s*\(([\s\S]*?)\)\s*->', src)
if from_route_match:
    params = from_route_match.group(1)
    if re.search(r'pathname\s*:\s*String', params):
        print("FAIL: from_route still takes pathname: String")
        sys.exit(1)

# Caller should not convert key to String (no k.to_string() in the map call)
# Check the entrypoints routes mapping area
routes_area = re.search(r'\.routes[\s\S]{0,200}\.map\(\|.*?\|.*?from_route\((.*?)\)', src)
if routes_area:
    call_arg = routes_area.group(1)
    if '.to_string()' in call_arg:
        print("FAIL: routes map still converts key via .to_string()")
        sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 5 [pr_diff] (0.10): From impls avoid allocating conversions on RcStr data
###############################################################################
echo ""
echo "TEST 5: [pr_diff] From impls avoid allocating conversions on RcStr-sourced fields"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs") as f:
    src = f.read()

# From<&PlainIssue> for NapiIssue — should not allocate for file_path/documentation_link
from_impl = re.search(r'impl\s+From<&PlainIssue>\s+for\s+NapiIssue\s*\{([\s\S]*?)\n\}', src)
if not from_impl:
    print("FAIL: From<&PlainIssue> for NapiIssue impl not found")
    sys.exit(1)

impl_body = from_impl.group(1)

# file_path assignment should not use .to_string() or .into_owned() or String::from
for field in ['file_path', 'documentation_link']:
    # Look for pattern: field_name: <expr>.to_string() or .into_owned()
    alloc_pat = re.search(
        rf'{field}\s*:\s*[^,]*?\.(to_string|into_owned)\s*\(\)',
        impl_body
    )
    if alloc_pat:
        print(f"FAIL: {field} in From<&PlainIssue> still uses allocating conversion: .{alloc_pat.group(1)}()")
        sys.exit(1)

# NapiDiagnostic::from — category/name should not use .to_string()
diag_impl = re.search(r'impl\s+NapiDiagnostic\s*\{([\s\S]*?)\n\s*\}', src)
if diag_impl:
    diag_body = diag_impl.group(1)
    for field in ['category', 'name']:
        alloc_pat = re.search(
            rf'{field}\s*:\s*[^,]*?\.(to_string|into_owned)\s*\(\)',
            diag_body
        )
        if alloc_pat:
            print(f"FAIL: NapiDiagnostic.{field} still uses .{alloc_pat.group(1)}()")
            sys.exit(1)

# NapiSource From impl — ident/file_path should not use .to_string()
source_impl = re.search(r'impl\s+From<&PlainSource>\s+for\s+NapiSource\s*\{([\s\S]*?)\n\}', src)
if source_impl:
    source_body = source_impl.group(1)
    for field in ['ident', 'file_path']:
        alloc_pat = re.search(
            rf'{field}\s*:\s*[^,]*?\.(to_string|into_owned)\s*\(\)',
            source_body
        )
        if alloc_pat:
            print(f"FAIL: NapiSource.{field} still uses .{alloc_pat.group(1)}()")
            sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 6 [pr_diff] (0.10): P2P — structs and non-RcStr fields preserved
###############################################################################
echo ""
echo "TEST 6: [pr_diff] P2P — helper structs and non-RcStr String fields intact"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs") as f:
    src = f.read()

# These structs must still exist (not deleted during refactor)
required_structs = ['NapiIssueSource', 'NapiSourcePos', 'NapiIssueSourceRange']
for s in required_structs:
    if f'pub struct {s}' not in src:
        print(f"FAIL: {s} struct missing — must not be deleted")
        sys.exit(1)

# NapiIssue must still have its non-RcStr fields with correct types
issue_match = re.search(r'pub struct NapiIssue\s*\{([\s\S]*?)\n\}', src)
if not issue_match:
    print("FAIL: NapiIssue struct missing")
    sys.exit(1)

issue_body = issue_match.group(1)

# title, description, detail should still be serde_json::Value / Option<...>
if 'title' not in issue_body:
    print("FAIL: NapiIssue.title field missing")
    sys.exit(1)
if 'source' not in issue_body:
    print("FAIL: NapiIssue.source field missing")
    sys.exit(1)
if 'additional_sources' not in issue_body:
    print("FAIL: NapiIssue.additional_sources field missing")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 7 [structural] (0.10): Anti-stub — real code, not hollow replacements
###############################################################################
echo ""
echo "TEST 7: [structural] Anti-stub — files contain real Rust code"
python3 << 'PYEOF'
import re, sys

checks = {
    "/workspace/next.js/crates/next-napi-bindings/src/next_api/endpoint.rs": {
        "min_lines": 100,
        "required_patterns": [
            (r'#\[napi', "#[napi attribute"),
            (r'impl\s+From<AssetPath>', "From<AssetPath> impl"),
            (r'use\s+turbo_rcstr::RcStr', "turbo_rcstr::RcStr import"),
        ],
    },
    "/workspace/next.js/crates/next-napi-bindings/src/next_api/project.rs": {
        "min_lines": 200,
        "required_patterns": [
            (r'#\[napi', "#[napi attribute"),
            (r'fn\s+from_route', "from_route function"),
            (r'pub struct NapiRoute', "NapiRoute struct"),
        ],
    },
    "/workspace/next.js/crates/next-napi-bindings/src/next_api/utils.rs": {
        "min_lines": 200,
        "required_patterns": [
            (r'#\[napi', "#[napi attribute"),
            (r'use\s+turbo_rcstr::RcStr', "turbo_rcstr::RcStr import"),
            (r'impl\s+From<&PlainIssue>', "From<&PlainIssue> impl"),
            (r'impl\s+NapiDiagnostic', "NapiDiagnostic impl block"),
        ],
    },
}

for filepath, spec in checks.items():
    with open(filepath) as f:
        content = f.read()
    lines = content.count('\n') + 1
    if lines < spec["min_lines"]:
        print(f"FAIL: {filepath.split('/')[-1]} has {lines} lines (min {spec['min_lines']})")
        sys.exit(1)
    for pattern, desc in spec["required_patterns"]:
        if not re.search(pattern, content):
            print(f"FAIL: {filepath.split('/')[-1]} missing {desc}")
            sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "========================================="
echo "TOTAL SCORE: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
