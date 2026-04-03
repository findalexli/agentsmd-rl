#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dagger

# Idempotent: skip if already applied
if grep -q 'RecordType' core/engine.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
# 1. Add RecordType field to EngineCacheEntry struct in core/engine.go
p = "core/engine.go"
t = open(p).read()
anchor = '\tActivelyUsed              bool   `field:"true" doc:"Whether the cache entry is actively being used."`'
replacement = anchor + '\n\tRecordType                string `field:"true" doc:"The type of the cache record (e.g. regular, internal, frontend, source.local, source.git.checkout, exec.cachemount)."`'
assert anchor in t, "Cannot find ActivelyUsed field in core/engine.go"
t = t.replace(anchor, replacement)
open(p, "w").write(t)

# 2. Populate RecordType in engine/server/gc.go
p = "engine/server/gc.go"
t = open(p).read()
anchor = "\t\t\tCreatedTimeUnixNano: int(r.CreatedAt.UnixNano()),"
replacement = anchor + "\n\t\t\tRecordType:          string(r.RecordType),"
assert anchor in t, "Cannot find CreatedTimeUnixNano in engine/server/gc.go"
t = t.replace(anchor, replacement)
open(p, "w").write(t)

# 3. Add recordType to GraphQL schema
p = "docs/docs-graphql/schema.graphqls"
t = open(p).read()
anchor = '  """The most recent time the cache entry was used, in Unix nanoseconds."""\n  mostRecentUseTimeUnixNano: Int!'
replacement = anchor + '\n\n  """\n  The type of the cache record (e.g. regular, internal, frontend, source.local, source.git.checkout, exec.cachemount).\n  """\n  recordType: String!'
assert anchor in t, "Cannot find mostRecentUseTimeUnixNano in schema.graphqls"
t = t.replace(anchor, replacement)
open(p, "w").write(t)

# 4. Update outdated CLI commands in CONTRIBUTING.md
p = "CONTRIBUTING.md"
t = open(p).read()

replacements = [
    ("Click on the *Fork* button", "Click on the _Fork_ button"),
    ("dagger call playground terminal", "dagger call engine-dev playground terminal"),
    ("- Run all core tests: `dagger call test all`",
     "- Run all core tests: `dagger checks test-split:*`"),
    ("- Run available core tests: `dagger call test list`",
     "- Run available core tests: `dagger call engine-dev tests`"),
    ('- Run a specific core test (eg.  `TestNamespacing` in the `TestModule` suite): `dagger call test specific --pkg="./core/integration" --run="^TestModule/TestNamespacing$"`',
     '- Run a specific core test (eg. `TestNamespacing` in the `TestModule` suite): `dagger call engine-dev test --pkg="./core/integration" --run="^TestModule/TestNamespacing$"`'),
    ("- Run SDK tests: `dagger call test-sdks`",
     "- Run SDK tests: `dagger check *sdk:*test*`"),
    ("To run all linters: `dagger call lint`",
     "To run all linters: `dagger checks *:lint`"),
    ("To run a local docs server: `dagger -m docs call server up`",
     "To run a local docs server: `dagger call docs server up`"),
    ("- Generate API docs, client bindings, and other generated files with `dagger call generate`, and include the output in your git commit.",
     "- Generate API docs, client bindings, and other generated files with `dagger generate`, and include the output in your git commit."),
    ("- Call all linters: `dagger call lint`",
     "- Call all linters: `dagger checks *:lint`"),
]

for old, new in replacements:
    t = t.replace(old, new)

# Remove extra blank line between docs server section and next section
t = t.replace("To run a local docs server: `dagger call docs server up`\n\n\n",
              "To run a local docs server: `dagger call docs server up`\n\n")

open(p, "w").write(t)
PYEOF

echo "Patch applied successfully."
