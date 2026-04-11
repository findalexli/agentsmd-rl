#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for distinctive line from the patch)
if grep -q 'THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply AGENTS.md changes first
git apply - <<'AGENTS_PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 758714d10aaa..2158d73af1b4 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -20,6 +20,17 @@

 Prefer single word names for variables and functions. Only use multiple words if necessary.

+### Naming Enforcement (Read This)
+
+THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE.
+
+- Use single word names by default for new locals, params, and helper functions.
+- Multi-word names are allowed only when a single word would be unclear or ambiguous.
+- Do not introduce new camelCase compounds when a short single-word alternative is clear.
+- Before finishing edits, review touched lines and shorten newly introduced identifiers where possible.
+- Good short names to prefer: `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`.
+- Examples to avoid unless truly required: `inputPID`, `existingClient`, `connectTimeout`, `workerPath`.
+
 ```ts
 // Good
 const foo = 1
AGENTS_PATCH

echo "AGENTS.md patch applied successfully."

# Now apply the worker.ts changes - remove Promise.race, just await Instance.disposeAll()
# Create backup first
cp packages/opencode/src/cli/cmd/tui/worker.ts packages/opencode/src/cli/cmd/tui/worker.ts.bak

# Use sed to replace the Promise.race block with just await Instance.disposeAll()
# First, let's check what the current state is
if grep -q "await Promise.race" packages/opencode/src/cli/cmd/tui/worker.ts; then
    # Use a Python script to do the replacement since sed with multiline is tricky
    python3 << 'PYEOF'
import re

with open('packages/opencode/src/cli/cmd/tui/worker.ts', 'r') as f:
    content = f.read()

# Replace Promise.race block with just await Instance.disposeAll()
old_block = '''await Promise.race([
      Instance.disposeAll(),
      new Promise((resolve) => {
        setTimeout(resolve, 5000)
      }),
    ])'''

new_block = 'await Instance.disposeAll()'

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('packages/opencode/src/cli/cmd/tui/worker.ts', 'w') as f:
        f.write(content)
    print("worker.ts updated successfully.")
else:
    print("WARNING: Could not find exact Promise.race block")
    # Try to find partial match
    if 'Promise.race' in content:
        print("Found Promise.race but block doesn't match exactly")
PYEOF
else
    echo "worker.ts already updated (no Promise.race found)"
fi

# Verify worker.ts changes
if grep -q "await Promise.race" packages/opencode/src/cli/cmd/tui/worker.ts; then
    echo "ERROR: worker.ts still has Promise.race"
    exit 1
fi

if ! grep -q "await Instance.disposeAll()" packages/opencode/src/cli/cmd/tui/worker.ts; then
    echo "ERROR: worker.ts missing await Instance.disposeAll()"
    exit 1
fi

echo "worker.ts verified."

# Now apply thread.ts changes - add unref to setTimeout
# Use Python for the complex modifications
python3 << 'PYEOF'
import re

with open('packages/opencode/src/cli/cmd/tui/thread.ts', 'r') as f:
    content = f.read()

# Add .unref?.() to setTimeout for checkUpgrade
old_timeout = '''setTimeout(() => {
        client.call("checkUpgrade", { directory: cwd }).catch(() => {})
      }, 1000)'''

new_timeout = '''setTimeout(() => {
        client.call("checkUpgrade", { directory: cwd }).catch(() => {})
      }, 1000).unref?.()'''

if old_timeout in content:
    content = content.replace(old_timeout, new_timeout)
    print("Added unref to setTimeout")
elif 'unref' not in content:
    print("WARNING: Could not find setTimeout block to add unref")
else:
    print("unref already present")

# Check if stop function exists
if 'const stop = async' not in content:
    print("WARNING: stop() function not found - need to add it")
    # The stop function needs to be added - check current structure
    # Look for process.on handlers and error handler definitions
    if 'const error = (e: unknown)' in content or 'const error = (' in content:
        print("Found error handler, looking for where to insert stop()...")
        # Insert stop() function after the process.on("SIGUSR2"...) line
        # Find pattern: process.on("SIGUSR2", reload)
        pattern = r'(process\.on\("SIGUSR2", reload\))'
        stop_func = '''\1

      let stopped = false
      const stop = async () => {
        if (stopped) return
        stopped = true
        process.off("uncaughtException", error)
        process.off("unhandledRejection", error)
        process.off("SIGUSR2", reload)
        await withTimeout(client.call("shutdown", undefined), 5000).catch((error) => {
          Log.Default.warn("worker shutdown failed", {
            error: error instanceof Error ? error.message : String(error),
          })
        })
        worker.terminate()
      }'''
        content = re.sub(pattern, stop_func, content)
        print("Added stop() function")
else:
    print("stop() function already exists")

with open('packages/opencode/src/cli/cmd/tui/thread.ts', 'w') as f:
    f.write(content)
print("thread.ts updated.")
PYEOF

echo "All patches applied successfully."
