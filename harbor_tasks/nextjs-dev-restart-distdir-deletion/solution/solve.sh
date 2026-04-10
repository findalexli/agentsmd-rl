#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q "wp.on('remove'" packages/next/src/server/lib/start-server.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'ENDPYTHON'
import re

src_file = "/workspace/next.js/packages/next/src/server/lib/start-server.ts"

with open(src_file, 'r') as f:
    content = f.read()

# Check if already patched
if "wp.on('remove'" in content:
    print("Patch already applied.")
    exit(0)

# The new isDev block
new_block = '''  // Watch config files for changes and distDir ancestors for deletion.
  if (isDev) {
    // Note: dir is absolute and normalized (.. segments removed), absDistDir
    // is also normalized because path.join() performs normalization. distDir
    // does not have to be inside of dir!
    const absDistDir = path.join(dir, distDir)
    // always watch dir and absDistDir
    const dirWatchPaths: string[] = [dir, absDistDir]
    // also watch ancestors of absDistDir that are inside of dir.
    let prevAncestor = absDistDir
    while (true) {
      const nextAncestor = path.dirname(prevAncestor)
      // note: dirname('/') === '/' if we happen to reach the FS root
      if (
        !nextAncestor.startsWith(dir + path.sep) ||
        nextAncestor === prevAncestor
      ) {
        break
      }
      dirWatchPaths.push(nextAncestor)
      prevAncestor = nextAncestor
    }

    const configFiles = CONFIG_FILES.map((file) => path.join(dir, file))

    const wp = new Watchpack()
    wp.watch({
      files: configFiles,
      missing: dirWatchPaths,
    })
    wp.on('change', async (filename) => {
      if (!configFiles.includes(filename)) {
        return
      }
      Log.warn(
        \`Found a change in \${path.basename(
          filename
        )}. Restarting the server to apply the changes...
      \`)
      process.exit(RESTART_EXIT_CODE)
    })
    wp.on('remove', (removedPath: string) => {
      if (dirWatchPaths.includes(removedPath)) {
        Log.error(
          \`The directory at \\${removedPath}\ was deleted.\\n\\n\` +
            'Deleting this directory while Next.js is running can lead to ' +
            'undefined behavior. Restarting the server to recover...'
        )
        process.exit(RESTART_EXIT_CODE)
      }
    })
  }'''

# Find all occurrences of if (isDev) and pick the one with watchConfigFiles
start_marker = "  if (isDev) {"
start_idx = -1
search_pos = 0

while True:
    idx = content.find(start_marker, search_pos)
    if idx == -1:
        break
    block_check = content[idx:idx+500]
    if "watchConfigFiles" in block_check:
        start_idx = idx
        break
    search_pos = idx + len(start_marker)

if start_idx == -1:
    print("ERROR: Could not find 'if (isDev)' block with watchConfigFiles")
    exit(1)

end_marker = "  }\n\n  return { distDir }"
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("ERROR: Could not find end of 'if (isDev)' block")
    exit(1)

new_content = content[:start_idx] + new_block + content[end_idx+len("  }"):]

with open(src_file, 'w') as f:
    f.write(new_content)

print("Patch applied successfully.")
ENDPYTHON
