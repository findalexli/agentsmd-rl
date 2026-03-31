#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0
DETAILS=""

add() {
    local weight="$1" score="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    local pts
    pts=$(python3 -c "print(round($weight * $score, 4))")
    EARNED=$(python3 -c "print(round($EARNED + $pts, 4))")
    DETAILS+="$tag ($weight): $desc -> $score\n"
}

SCRIPT="/repo/scripts/patch-dist-manifest-checksums.py"

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (GATE): Script must be valid Python
if [ -f "$SCRIPT" ] && python3 -c "import ast; ast.parse(open('$SCRIPT').read())"; then
    echo "GATE PASS: syntax ok"
else
    echo "GATE FAIL: script missing or syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    printf '{"reward": 0.0, "details": "GATE FAIL: script missing or has syntax errors"}\n' > /logs/verifier/reward.json
    exit 0
fi

# ── Setup test fixtures ─────────────────────────────────────────────
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

ARTIFACTS_DIR="$TMPDIR/artifacts"
mkdir -p "$ARTIFACTS_DIR"

# Create a sample manifest with two artifacts
cat > "$TMPDIR/manifest.json" <<'EOF'
{
  "artifacts": {
    "uv-x86_64-unknown-linux-gnu.tar.gz": {
      "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
      "kind": "executable-zip"
    },
    "uv-aarch64-apple-darwin.tar.gz": {
      "name": "uv-aarch64-apple-darwin.tar.gz",
      "kind": "executable-zip"
    }
  }
}
EOF

# Create matching .sha256 sidecar files
echo "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2  uv-x86_64-unknown-linux-gnu.tar.gz" \
    > "$ARTIFACTS_DIR/uv-x86_64-unknown-linux-gnu.tar.gz.sha256"
echo "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5  uv-aarch64-apple-darwin.tar.gz" \
    > "$ARTIFACTS_DIR/uv-aarch64-apple-darwin.tar.gz.sha256"

# ── Behavioral: patches checksums into manifest (0.30) ──────────────
# [pr_diff] (0.40): Script injects sha256 checksums into artifact entries
HAPPY_PATH=0
cp "$TMPDIR/manifest.json" "$TMPDIR/test1.json"
if python3 "$SCRIPT" --manifest "$TMPDIR/test1.json" --artifacts-dir "$ARTIFACTS_DIR" 2>/dev/null; then
    # Verify both checksums were injected
    INJECT_OK=$(python3 -c "
import json, sys
m = json.load(open('$TMPDIR/test1.json'))
a = m.get('artifacts', {})
c1 = a.get('uv-x86_64-unknown-linux-gnu.tar.gz', {}).get('checksums', {}).get('sha256', '')
c2 = a.get('uv-aarch64-apple-darwin.tar.gz', {}).get('checksums', {}).get('sha256', '')
if c1 == 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2' and \
   c2 == 'f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5':
    # Also verify manifest is still valid JSON and existing fields preserved
    assert a['uv-x86_64-unknown-linux-gnu.tar.gz']['kind'] == 'executable-zip'
    print('OK')
else:
    print('FAIL')
")
    if [ "$INJECT_OK" = "OK" ]; then
        add 0.40 1 "[pr_diff]" "Checksums correctly patched into manifest"
        HAPPY_PATH=1
    else
        add 0.40 0 "[pr_diff]" "Checksums not correctly patched"
    fi
else
    add 0.40 0 "[pr_diff]" "Script failed on valid input"
fi

# ── Behavioral: idempotent re-run (0.10) ─────────────────────────────
# [pr_diff] (0.10): Running script twice yields same result
if [ "$HAPPY_PATH" = "1" ]; then
    cp "$TMPDIR/manifest.json" "$TMPDIR/test_idem.json"
    python3 "$SCRIPT" --manifest "$TMPDIR/test_idem.json" --artifacts-dir "$ARTIFACTS_DIR" 2>/dev/null
    FIRST=$(cat "$TMPDIR/test_idem.json")
    python3 "$SCRIPT" --manifest "$TMPDIR/test_idem.json" --artifacts-dir "$ARTIFACTS_DIR" 2>/dev/null
    SECOND=$(cat "$TMPDIR/test_idem.json")
    if [ "$FIRST" = "$SECOND" ]; then
        add 0.10 1 "[pr_diff]" "Idempotent re-run produces same output"
    else
        add 0.10 0 "[pr_diff]" "Re-run changed manifest contents"
    fi
else
    add 0.10 0 "[pr_diff]" "Skipped (happy path failed)"
fi

# ── Behavioral: exit 1 when no checksums matched (0.10) ──────────────
# [pr_diff] (0.10): Script returns error when no sidecar files match any artifact
# Guard: only counts if the happy path passed (prevents stubs from scoring)
if [ "$HAPPY_PATH" = "1" ]; then
    EMPTY_DIR=$(mktemp -d)
    cp "$TMPDIR/manifest.json" "$TMPDIR/test2.json"
    if python3 "$SCRIPT" --manifest "$TMPDIR/test2.json" --artifacts-dir "$EMPTY_DIR" 2>/dev/null; then
        add 0.10 0 "[pr_diff]" "Should have returned error with no checksums"
    else
        add 0.10 1 "[pr_diff]" "Correctly returns error when no checksums patched"
    fi
    rm -rf "$EMPTY_DIR"
else
    add 0.10 0 "[pr_diff]" "Skipped (happy path failed)"
fi

# ── Behavioral: validates checksum length (0.10) ────────────────────
# [pr_diff] (0.10): Script rejects checksums that aren't 64 hex chars
if [ "$HAPPY_PATH" = "1" ]; then
    BAD_DIR=$(mktemp -d)
    echo "tooshort  uv-x86_64-unknown-linux-gnu.tar.gz" > "$BAD_DIR/uv-x86_64-unknown-linux-gnu.tar.gz.sha256"
    cp "$TMPDIR/manifest.json" "$TMPDIR/test4.json"
    if python3 "$SCRIPT" --manifest "$TMPDIR/test4.json" --artifacts-dir "$BAD_DIR" 2>/dev/null; then
        add 0.10 0 "[pr_diff]" "Should have rejected bad checksum length"
    else
        # Verify it didn't silently inject the bad checksum
        BAD_INJECTED=$(python3 -c "
import json
m = json.load(open('$TMPDIR/test4.json'))
c = m.get('artifacts',{}).get('uv-x86_64-unknown-linux-gnu.tar.gz',{}).get('checksums',{}).get('sha256','')
print('yes' if c == 'tooshort' else 'no')
")
        if [ "$BAD_INJECTED" = "no" ]; then
            add 0.10 1 "[pr_diff]" "Correctly rejects invalid checksum length"
        else
            add 0.10 0 "[pr_diff]" "Injected bad checksum instead of rejecting"
        fi
    fi
    rm -rf "$BAD_DIR"
else
    add 0.10 0 "[pr_diff]" "Skipped (happy path failed)"
fi

# ── Behavioral: rejects empty checksum file (0.10) ──────────────────
# [pr_diff] (0.10): Script rejects empty .sha256 sidecar files
if [ "$HAPPY_PATH" = "1" ]; then
    EMPTY_CKSUM_DIR=$(mktemp -d)
    echo "" > "$EMPTY_CKSUM_DIR/uv-x86_64-unknown-linux-gnu.tar.gz.sha256"
    cp "$TMPDIR/manifest.json" "$TMPDIR/test5.json"
    if python3 "$SCRIPT" --manifest "$TMPDIR/test5.json" --artifacts-dir "$EMPTY_CKSUM_DIR" 2>/dev/null; then
        add 0.10 0 "[pr_diff]" "Should have rejected empty checksum file"
    else
        add 0.10 1 "[pr_diff]" "Correctly rejects empty checksum files"
    fi
    rm -rf "$EMPTY_CKSUM_DIR"
else
    add 0.10 0 "[pr_diff]" "Skipped (happy path failed)"
fi

# ── Pass-to-pass: existing repo scripts still parse (0.10) ──────────
# [repo_tests] (0.10): Existing Python scripts in scripts/ remain valid
P2P_OK=1
for f in /repo/scripts/*.py; do
    [ -f "$f" ] || continue
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        P2P_OK=0
        break
    fi
done
add 0.10 "$P2P_OK" "[repo_tests]" "Existing scripts/ Python files remain valid"

# ── Structural: release workflow references new job (0.05) ──────────
# [pr_diff] (0.05): release.yml adds a job that synthesizes a local dist manifest
if grep -q "synthesize-local-dist-manifest\|synthesize.*dist.*manifest\|local-dist-manifest" /repo/.github/workflows/release.yml 2>/dev/null; then
    add 0.05 1 "[pr_diff]" "release.yml has synthesize-local-dist-manifest job"
else
    add 0.05 0 "[pr_diff]" "release.yml missing new job"
fi

# ── Config-derived: top-level imports (0.05) ─────────────────────────
# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:16 @ d0f2f3babc7c
if [ -f "$SCRIPT" ]; then
    IN_FUNC_IMPORT=$(python3 -c "
import ast, sys
tree = ast.parse(open('$SCRIPT').read())
bad = 0
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                bad += 1
print(bad)
")
    if [ "$IN_FUNC_IMPORT" = "0" ]; then
        add 0.05 1 "[agent_config]" "Top-level imports only"
    else
        add 0.05 0 "[agent_config]" "Found imports inside functions"
    fi
else
    add 0.05 0 "[agent_config]" "Script missing"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($EARNED, 2))")

echo "$REWARD" > /logs/verifier/reward.txt
printf '{"reward": %s, "behavioral": 0.80, "pass_to_pass": 0.10, "structural": 0.05, "config": 0.05}\n' "$REWARD" > /logs/verifier/reward.json

echo "=== Test Results ==="
printf "$DETAILS"
echo "Total: $REWARD / $TOTAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
