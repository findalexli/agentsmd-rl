import os
import re
import subprocess

REPO = "/workspace/civitai"


# === Fail-to-pass tests (f2p) ===
# These fail on the base commit and pass after the gold fix is applied.


def test_max_notification_window_constant_exists():
    """fail_to_pass | MAX_NOTIFICATION_WINDOW_MS constant defined as 10 * 60 * 1000 (10 minutes in ms)"""
    filepath = os.path.join(REPO, "src/server/jobs/send-notifications.ts")
    with open(filepath) as f:
        content = f.read()
    assert "MAX_NOTIFICATION_WINDOW_MS" in content, (
        "MAX_NOTIFICATION_WINDOW_MS constant not found in send-notifications.ts"
    )
    match = re.search(r"MAX_NOTIFICATION_WINDOW_MS\s*=\s*10\s*\*\s*60\s*\*\s*1000", content)
    assert match is not None, (
        "MAX_NOTIFICATION_WINDOW_MS must equal '10 * 60 * 1000' (10 minutes in ms). "
        f"Found context: {content[max(0, content.find('MAX_NOTIFICATION_WINDOW_MS')-20):content.find('MAX_NOTIFICATION_WINDOW_MS')+80]}"
    )


def test_effective_now_field_in_notification_input_type():
    """fail_to_pass | effectiveNow string field present in NotificationProcessorRunInput type"""
    filepath = os.path.join(REPO, "src/server/notifications/base.notifications.ts")
    with open(filepath) as f:
        content = f.read()
    # Find the actual TYPE DEFINITION (export type NotificationProcessorRunInput), not the first reference
    type_start = content.find("export type NotificationProcessorRunInput")
    assert type_start != -1, "export type NotificationProcessorRunInput not found"
    type_section = content[type_start : type_start + 300]
    assert "effectiveNow" in type_section, (
        f"effectiveNow field not found in NotificationProcessorRunInput type. "
        f"Type section:\n{type_section}"
    )
    assert re.search(r"effectiveNow\s*:\s*string", type_section), (
        f"effectiveNow must be typed as 'string'. Type section:\n{type_section}"
    )


def test_effective_now_replaces_now_in_model_version_query():
    """fail_to_pass | new-model-version SQL query uses effectiveNow instead of bare now()"""
    filepath = os.path.join(REPO, "src/server/notifications/model.notifications.ts")
    with open(filepath) as f:
        content = f.read()
    # Find the new-model-version query section
    nv_start = content.find("new_model_version AS")
    assert nv_start != -1, "new_model_version query not found"
    nv_section = content[nv_start : nv_start + 1200]
    # Must use effectiveNow in the publishedAt BETWEEN clause, not bare now()
    assert "effectiveNow" in nv_section, (
        f"effectiveNow not referenced in new-model-version query. Section:\n{nv_section}"
    )
    # Specifically: the BETWEEN clause should use '${effectiveNow}' not now()
    assert "'${effectiveNow}'" in nv_section or "${effectiveNow}" in nv_section, (
        f"effectiveNow not interpolated in SQL string in new-model-version query. Section:\n{nv_section}"
    )
    # Should NOT have bare now() in the model_version SQL (only effectiveNow)
    bare_now_in_sql = re.search(r"BETWEEN.*AND\s+now\(\)", nv_section)
    assert bare_now_in_sql is None, (
        f"Bare now() still present in new-model-version query; should use effectiveNow instead. "
        f"Match: {bare_now_in_sql.group() if bare_now_in_sql else 'none'}"
    )


def test_effective_now_replaces_now_in_following_query():
    """fail_to_pass | new-model-from-following SQL query uses effectiveNow with 59s lookback"""
    filepath = os.path.join(REPO, "src/server/notifications/model.notifications.ts")
    with open(filepath) as f:
        content = f.read()
    # Find the new-model-from-following query section
    nf_start = content.find("new_model_from_following AS")
    assert nf_start != -1, "new_model_from_following query not found"
    nf_section = content[nf_start : nf_start + 1200]
    assert "effectiveNow" in nf_section, (
        f"effectiveNow not referenced in new-model-from-following query. Section:\n{nf_section}"
    )
    assert "'${effectiveNow}'" in nf_section or "${effectiveNow}" in nf_section, (
        f"effectiveNow not interpolated in SQL string in new-model-from-following query. Section:\n{nf_section}"
    )
    # Must have the 59-second lookback buffer
    assert "59 second" in nf_section or "59 second" in nf_section, (
        f"59-second lookback buffer not found in new-model-from-following query. Section:\n{nf_section}"
    )
    # Should NOT have bare now() in the following SQL
    bare_now_match = re.search(r"BETWEEN.*AND\s+now\(\)", nf_section)
    assert bare_now_match is None, (
        f"Bare now() still present in new-model-from-following query. "
        f"Match: {bare_now_match.group() if bare_now_match else 'none'}"
    )


def test_effective_now_replaces_now_in_early_access_query():
    """fail_to_pass | early-access-complete SQL query uses effectiveNow instead of bare now()"""
    filepath = os.path.join(REPO, "src/server/notifications/model.notifications.ts")
    with open(filepath) as f:
        content = f.read()
    # Find the early-access query section
    ea_start = content.find("early_access_versions AS")
    assert ea_start != -1, "early_access_versions query not found"
    ea_section = content[ea_start : ea_start + 1500]
    assert "effectiveNow" in ea_section, (
        f"effectiveNow not referenced in early-access-complete query. Section:\n{ea_section}"
    )
    assert "'${effectiveNow}'" in ea_section or "${effectiveNow}" in ea_section, (
        f"effectiveNow not interpolated in SQL string in early-access query. Section:\n{ea_section}"
    )
    # Should NOT have bare now() in the early-access SQL
    bare_now_match = re.search(r"AND\s+ev\.updated_published_at\s*<\s*now\(\)", ea_section)
    assert bare_now_match is None, (
        f"Bare now() still present in early-access query; should use effectiveNow. "
        f"Match: {bare_now_match.group() if bare_now_match else 'none'}"
    )


def test_notification_migration_index_exists():
    """fail_to_pass | Model(status, publishedAt) index migration file exists"""
    import glob
    migration_pattern = os.path.join(
        REPO, "prisma/migrations/*add_model_status_published_at*/migration.sql"
    )
    migrations = glob.glob(migration_pattern)
    assert len(migrations) >= 1, (
        f"No migration found matching pattern: {migration_pattern}"
    )
    migration_file = migrations[0]
    with open(migration_file) as f:
        content = f.read()
    assert 'CREATE INDEX' in content, (
        f"Migration file {migration_file} does not contain CREATE INDEX"
    )
    assert 'Model_status_publishedAt_idx' in content, (
        f"Migration file {migration_file} does not contain Model_status_publishedAt_idx index"
    )
    assert '"Model"' in content and 'status' in content and '"publishedAt"' in content, (
        f"Migration file {migration_file} does not reference Model(status, publishedAt) columns"
    )


# === Pass-to-pass tests (p2p) ===
# These pass on both the base commit and the gold fix — they guard against regressions.


def test_eslint_passes():
    """pass_to_pass | ESLint passes on modified notification source files"""
    files = [
        "src/server/jobs/send-notifications.ts",
        "src/server/notifications/base.notifications.ts",
        "src/server/notifications/model.notifications.ts",
    ]
    r = subprocess.run(
        ["bash", "-lc", f"cd {REPO} && npx eslint --quiet --no-cache {' '.join(files)}"],
        cwd=REPO,
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"ESLint failed on notification files (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )


def test_prettier_passes():
    """pass_to_pass | Prettier format check passes on modified files"""
    files = [
        "src/server/jobs/send-notifications.ts",
        "src/server/notifications/base.notifications.ts",
        "src/server/notifications/model.notifications.ts",
    ]
    r = subprocess.run(
        ["bash", "-lc", f"cd {REPO} && pnpm prettier --check {' '.join(files)}"],
        cwd=REPO,
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Prettier check failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )


def test_eslint_modified_files():
    """pass_to_pass | ESLint runs directly on the modified source files (no cache)"""
    files = [
        "src/server/jobs/send-notifications.ts",
        "src/server/notifications/base.notifications.ts",
        "src/server/notifications/model.notifications.ts",
    ]
    r = subprocess.run(
        ["bash", "-lc", f"cd {REPO} && npx eslint {' '.join(files)} --no-cache"],
        cwd=REPO,
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"ESLint (no-cache) failed on notification files (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )
