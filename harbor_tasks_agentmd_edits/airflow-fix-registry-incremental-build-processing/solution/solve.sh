#!/usr/bin/env bash
set -euo pipefail

cd /workspace/airflow

# Idempotent: skip if already applied
if grep -q 'extract_parameters\.py{provider_flag}' dev/breeze/src/airflow_breeze/commands/registry_commands.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
from pathlib import Path

# ── Fix 1: Forward --provider flag to all extraction scripts ──
p = Path("dev/breeze/src/airflow_breeze/commands/registry_commands.py")
src = p.read_text()
src = src.replace(
    '        "python dev/registry/extract_parameters.py && "\n'
    '        "python dev/registry/extract_connections.py"',
    '        f"python dev/registry/extract_parameters.py{provider_flag} && "\n'
    '        f"python dev/registry/extract_connections.py{provider_flag}"',
)
p.write_text(src)
print("Fixed registry_commands.py")

# ── Fix 2: Handle missing new_modules file in merge_registry_data.py ──
p = Path("dev/registry/merge_registry_data.py")
src = p.read_text()
src = src.replace(
    '    new_modules = json.loads(new_modules_path.read_text())["modules"]',
    '    new_modules: list[dict] = []\n'
    '    if new_modules_path.exists():\n'
    '        new_modules = json.loads(new_modules_path.read_text())["modules"]',
)
p.write_text(src)
print("Fixed merge_registry_data.py")

# ── Fix 3: Multi-provider filter in extract_connections.py ──
p = Path("dev/registry/extract_connections.py")
src = p.read_text()

# Update help text
src = src.replace(
    "help=\"Only output connections for this provider ID (e.g. 'amazon').\",",
    "help=\"Only output connections for these provider ID(s) (space-separated, e.g. 'amazon common-io').\",",
)

# Add early filter parsing before the main loop
src = src.replace(
    '    total_with_ui = 0\n\n    for conn_type, hook_info in sorted(hooks.items()):',
    '    total_with_ui = 0\n\n'
    '    # Parse space-separated provider filter (matches extract_metadata.py behaviour)\n'
    '    provider_filter: set[str] | None = None\n'
    '    if args.provider:\n'
    '        provider_filter = {pid.strip() for pid in args.provider.split() if pid.strip()}\n'
    '        print(f"Filtering to provider(s): {\', \'.join(sorted(provider_filter))}")\n\n'
    '    for conn_type, hook_info in sorted(hooks.items()):',
)

# Add early continue after provider_id lookup
src = src.replace(
    '        provider_id = package_name_to_provider_id(hook_info.package_name)\n\n        standard_fields',
    '        provider_id = package_name_to_provider_id(hook_info.package_name)\n\n'
    '        if provider_filter and provider_id not in provider_filter:\n'
    '            continue\n\n'
    '        standard_fields',
)

# Remove old post-filter block
src = src.replace(
    '    # Filter to single provider if requested\n'
    '    if args.provider:\n'
    '        provider_connections = {\n'
    '            pid: conns for pid, conns in provider_connections.items() if pid == args.provider\n'
    '        }\n'
    '        print(f"Filtering output to provider: {args.provider}")\n\n'
    '    # Write per-provider',
    '    # Write per-provider',
)

p.write_text(src)
print("Fixed extract_connections.py")

# ── Fix 4: Update registry/AGENTS.md — document selective S3 sync ──
p = Path("registry/AGENTS.md")
src = p.read_text()
src = src.replace(
    '     with existing data from S3 via `merge_registry_data.py`, then builds the full site\n'
    '2. **S3 buckets**',
    '     with existing data from S3 via `merge_registry_data.py`, then builds the full site.\n'
    '     The S3 sync step excludes the entire `api/providers/` subtree for non-target\n'
    '     providers to avoid overwriting real data with Eleventy\'s incomplete/empty\n'
    '     stubs (Eleventy 3.x `permalink: false` does not work with pagination).\n'
    '2. **S3 buckets**',
)
p.write_text(src)
print("Fixed registry/AGENTS.md")

# ── Fix 5: Update registry/README.md — selective sync + known limitation ──
p = Path("registry/README.md")
src = p.read_text()

# Update merge step description
src = src.replace(
    '   the downloaded JSON while keeping all other providers intact.\n'
    '4. **Build site**',
    '   the downloaded JSON while keeping all other providers intact. Only global files\n'
    '   (`providers.json`, `modules.json`) are merged \u2014 per-version files like\n'
    '   `connections.json` and `parameters.json` are not downloaded from S3.\n'
    '4. **Build site**',
)

# Update build + S3 sync steps
src = src.replace(
    '   all records.\n'
    '5. **S3 sync** \u2014 only changed pages are uploaded (S3 sync diffs).',
    '   all records. Because per-version data only exists for the target provider, Eleventy\n'
    '   emits empty fallback JSON for other providers\' `connections.json` and\n'
    '   `parameters.json` API endpoints (see **Known limitation** below).\n'
    '5. **S3 sync (selective)** \u2014 the main sync excludes the entire `api/providers/`\n'
    '   subtree to avoid overwriting real data with incomplete/empty stubs. A second\n'
    '   sync uploads only the target provider\'s API files.',
)

# Add known limitation section
src = src.replace(
    '- Missing modules file: treated as empty.\n\nTo run an incremental build locally:',
    '- Missing modules file: treated as empty.\n\n'
    '**Known limitation**: Eleventy\'s pagination templates generate API files for every\n'
    'provider in `providers.json`, even when per-version data (connections, parameters) only\n'
    'exists for the target provider. The templates emit empty fallback JSON\n'
    '(`{"connection_types":[]}`) for providers without data. The S3 sync step works around\n'
    'this with `--exclude` patterns during incremental builds. A proper template-level fix\n'
    '(skipping file generation) is tracked as a follow-up \u2014 `permalink: false` does not work\n'
    'with Eleventy 3.x pagination templates.\n\n'
    'To run an incremental build locally:',
)

p.write_text(src)
print("Fixed registry/README.md")

print("\nAll patches applied successfully.")
PYEOF
