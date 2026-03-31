#!/usr/bin/env bash
set -uo pipefail

SCRIPT="/repo/sgl-kernel/rename_wheels.sh"
TOTAL=0.0
REWARD=0.0

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

# ── GATE (0.00): syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): Script must be valid bash
if ! bash -n "$SCRIPT" 2>/dev/null; then
    echo "GATE FAILED: bash syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED: syntax ok"

# ── Helper: create a minimal valid wheel ────────────────────────────────────
create_mock_wheel() {
    local pkg_name="$1"
    local version="$2"
    local platform="$3"
    local dest_dir="$4"

    local tag="cp312-cp312-${platform}"
    local dist_info="${pkg_name}-${version}.dist-info"
    local tmpdir
    tmpdir=$(mktemp -d)

    mkdir -p "${tmpdir}/${pkg_name}" "${tmpdir}/${dist_info}"

    cat > "${tmpdir}/${pkg_name}/__init__.py" <<'PYEOF'
# placeholder
PYEOF

    cat > "${tmpdir}/${dist_info}/METADATA" <<METAEOF
Metadata-Version: 2.1
Name: ${pkg_name}
Version: ${version}
METAEOF

    cat > "${tmpdir}/${dist_info}/WHEEL" <<WHEELEOF
Wheel-Version: 1.0
Generator: test
Root-Is-Purelib: false
Tag: ${tag}
WHEELEOF

    # Generate proper SHA256 hashes (base64url, no padding) so `wheel unpack` works
    python3 -c "
import hashlib, base64, os, sys
def record_hash(path):
    data = open(path, 'rb').read()
    digest = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return f'sha256={b64},{len(data)}'
tmpdir = sys.argv[1]
di = sys.argv[2]
pkg = sys.argv[3]
lines = []
for rel in [f'{pkg}/__init__.py', f'{di}/METADATA', f'{di}/WHEEL']:
    lines.append(f'{rel},{record_hash(os.path.join(tmpdir, rel))}')
lines.append(f'{di}/RECORD,,')
open(os.path.join(tmpdir, di, 'RECORD'), 'w').write('\n'.join(lines) + '\n')
" "${tmpdir}" "${dist_info}" "${pkg_name}"

    local whl_name="${pkg_name}-${version}-${tag}.whl"
    (cd "$tmpdir" && zip -q -r "${dest_dir}/${whl_name}" .)
    rm -rf "$tmpdir"
    echo "${dest_dir}/${whl_name}"
}

# ── Helper: read metadata field from inside a wheel ─────────────────────────
read_wheel_metadata() {
    local whl="$1"
    local field="$2"
    python3 -c "
import zipfile, sys
with zipfile.ZipFile('$whl') as z:
    for name in z.namelist():
        if name.endswith('.dist-info/METADATA'):
            data = z.read(name).decode()
            for line in data.splitlines():
                if line.startswith('$field:'):
                    print(line.split(':', 1)[1].strip())
                    sys.exit(0)
sys.exit(1)
"
}

read_wheel_tag() {
    local whl="$1"
    python3 -c "
import zipfile, sys
with zipfile.ZipFile('$whl') as z:
    for name in z.namelist():
        if name.endswith('.dist-info/WHEEL'):
            data = z.read(name).decode()
            for line in data.splitlines():
                if line.startswith('Tag:'):
                    print(line.split(':', 1)[1].strip())
                    sys.exit(0)
sys.exit(1)
"
}

check_distinfo_name() {
    local whl="$1"
    local expected_substr="$2"
    python3 -c "
import zipfile, sys
with zipfile.ZipFile('$whl') as z:
    for name in z.namelist():
        if '.dist-info/' in name:
            dirname = name.split('/')[0]
            if '$expected_substr' in dirname:
                sys.exit(0)
sys.exit(1)
"
}

# ── Test 1 (0.30): METADATA Version includes +cu suffix after script run ────
# [pr_diff] (0.30): Internal METADATA Version must include CUDA suffix
echo "--- Test 1: METADATA Version includes CUDA suffix ---"
TEST1=0
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST" "${WORKDIR}/usr_local/cuda-12.4"

    create_mock_wheel "sgl_kernel" "0.4.5" "linux_x86_64" "$DIST" > /dev/null

    cd "$WORKDIR"
    # Override /usr/local detection by placing a symlink
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    # Run the script from a directory where WHEEL_DIR=dist resolves
    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    # Find output wheel
    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    if [[ -z "$OUT_WHL" ]]; then
        echo "FAIL: no output wheel found"
        exit 1
    fi

    VERSION=$(read_wheel_metadata "$OUT_WHL" "Version")
    echo "Output METADATA Version: $VERSION"
    if [[ "$VERSION" == *"+cu"* ]]; then
        echo "PASS: Version contains +cu suffix"
        exit 0
    else
        echo "FAIL: Version does not contain +cu suffix (got: $VERSION)"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.30
    echo "Test 1: PASS (+0.30)"
else
    echo "Test 1: FAIL"
fi

# ── Test 2 (0.15): .dist-info directory renamed to include +cu suffix ───────
# [pr_diff] (0.15): dist-info dir must match suffixed version
echo "--- Test 2: dist-info directory includes CUDA suffix ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    create_mock_wheel "sgl_kernel" "0.4.5" "linux_x86_64" "$DIST" > /dev/null

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    if check_distinfo_name "$OUT_WHL" "+cu"; then
        echo "PASS: dist-info contains +cu"
        exit 0
    else
        echo "FAIL: dist-info does not contain +cu"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.15
    echo "Test 2: PASS (+0.15)"
else
    echo "Test 2: FAIL"
fi

# ── Test 3 (0.15): WHEEL platform tags use manylinux2014 ───────────────────
# [pr_diff] (0.15): WHEEL tags must say manylinux2014, not linux
echo "--- Test 3: WHEEL platform tags updated to manylinux2014 ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    create_mock_wheel "sgl_kernel" "0.4.5" "linux_x86_64" "$DIST" > /dev/null

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    TAG=$(read_wheel_tag "$OUT_WHL")
    echo "Output WHEEL Tag: $TAG"
    if [[ "$TAG" == *"manylinux2014"* ]]; then
        echo "PASS: platform tag is manylinux2014"
        exit 0
    else
        echo "FAIL: platform tag is not manylinux2014 (got: $TAG)"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.15
    echo "Test 3: PASS (+0.15)"
else
    echo "Test 3: FAIL"
fi

# ── Test 4 (0.10): Idempotency — running twice doesn't double-suffix ───────
# [pr_diff] (0.10): Script must be idempotent (skip already-suffixed wheels)
echo "--- Test 4: Idempotency (second run is a no-op) ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    create_mock_wheel "sgl_kernel" "0.4.5" "linux_x86_64" "$DIST" > /dev/null

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    # Run a second time
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    VERSION=$(read_wheel_metadata "$OUT_WHL" "Version")
    echo "After 2nd run, Version: $VERSION"

    # Should have exactly one +cu, not +cu124+cu124
    COUNT=$(echo "$VERSION" | grep -o '+cu' | wc -l)
    if [[ "$COUNT" -eq 1 ]]; then
        echo "PASS: idempotent (one +cu suffix)"
        exit 0
    else
        echo "FAIL: not idempotent (found $COUNT +cu occurrences in $VERSION)"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.10
    echo "Test 4: PASS (+0.10)"
else
    echo "Test 4: FAIL"
fi

# ── Test 5 (0.10): No CUDA → wheel unchanged ──────────────────────────────
# [pr_diff] (0.10): Without CUDA, wheel should pass through unmodified
echo "--- Test 5: No CUDA detected → wheel unchanged ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"

    # Remove any fake CUDA dirs we created
    rm -rf /usr/local/cuda-12.4 /usr/local/cuda-12.8 /usr/local/cuda-13.0 2>/dev/null || true

    WHL=$(create_mock_wheel "sgl_kernel" "0.4.5" "manylinux2014_x86_64" "$DIST")

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    VERSION=$(read_wheel_metadata "$OUT_WHL" "Version")
    echo "No-CUDA Version: $VERSION"
    if [[ "$VERSION" == "0.4.5" ]]; then
        echo "PASS: version unchanged without CUDA"
        exit 0
    else
        echo "FAIL: version changed without CUDA (got: $VERSION)"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.10
    echo "Test 5: PASS (+0.10)"
else
    echo "Test 5: FAIL"
fi

# ── Test 6 (0.10): Filename-METADATA consistency ──────────────────────────
# [pr_diff] (0.10): Wheel filename version must match internal METADATA version
echo "--- Test 6: Filename matches METADATA Version ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    create_mock_wheel "sgl_kernel" "0.4.5" "linux_x86_64" "$DIST" > /dev/null

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    FNAME=$(basename "$OUT_WHL")
    VERSION=$(read_wheel_metadata "$OUT_WHL" "Version")

    # The filename should contain the version (with + encoded as %2B or literally)
    # Wheel filenames use the version directly with local separator
    FNAME_VERSION=$(echo "$FNAME" | sed 's/^[^-]*-//' | sed 's/-.*//')
    echo "Filename version part: $FNAME_VERSION"
    echo "METADATA Version: $VERSION"

    # Both should contain +cu
    if [[ "$FNAME_VERSION" == *"+cu"* ]] && [[ "$VERSION" == *"+cu"* ]]; then
        echo "PASS: both filename and metadata have +cu"
        exit 0
    else
        echo "FAIL: mismatch — filename=$FNAME_VERSION metadata=$VERSION"
        exit 1
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.10
    echo "Test 6: PASS (+0.10)"
else
    echo "Test 6: FAIL"
fi

# ── Test 7 (0.10): linux→manylinux substitution is safe (no substring corruption)
# [pr_diff] (0.10): Platform rename must not corrupt manylinux2014 on re-run
echo "--- Test 7: Platform tag substitution is anchored (no double-mangle) ---"
(
    set -e
    WORKDIR=$(mktemp -d)
    DIST="${WORKDIR}/dist"
    mkdir -p "$DIST"
    mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

    # Start with a wheel that already has manylinux2014 in the filename
    create_mock_wheel "sgl_kernel" "0.4.5" "manylinux2014_x86_64" "$DIST" > /dev/null

    cp "$SCRIPT" "${WORKDIR}/rename_wheels.sh"
    chmod +x "${WORKDIR}/rename_wheels.sh"
    cd "$WORKDIR"
    bash rename_wheels.sh

    OUT_WHL=$(ls "$DIST"/*.whl 2>/dev/null | head -1)
    FNAME=$(basename "$OUT_WHL")
    echo "Output filename: $FNAME"

    # Should NOT contain "manylinux20142014" or other corrupted tag
    if echo "$FNAME" | grep -q "manylinux20142014\|manymanylinux"; then
        echo "FAIL: platform tag corrupted by double substitution"
        exit 1
    else
        echo "PASS: platform tag not corrupted"
        exit 0
    fi
)
if [[ $? -eq 0 ]]; then
    add 0.10
    echo "Test 7: PASS (+0.10)"
else
    echo "Test 7: FAIL"
fi

# Restore CUDA dir for consistency
mkdir -p /usr/local/cuda-12.4 2>/dev/null || true

# ── Final score ─────────────────────────────────────────────────────────────
echo ""
echo "========================================="
echo "Total reward: $REWARD"
echo "========================================="
echo "$REWARD" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
reward = $REWARD
# Tests 1-4,6,7 are behavioral (0.90), Test 5 is pass-to-pass (0.10)
behavioral = min(reward, 0.90)
regression = max(0, reward - 0.90) if reward > 0.90 else min(0.10, max(0, reward - 0.80))
# Simplified: just report total
print(json.dumps({'reward': reward, 'behavioral': round(min(reward, 0.90), 4), 'regression': round(max(0, reward - 0.90), 4)}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
