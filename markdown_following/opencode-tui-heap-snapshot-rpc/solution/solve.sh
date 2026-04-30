#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for onSnapshot prop in app.tsx)
if grep -q 'onSnapshot' packages/opencode/src/cli/cmd/tui/app.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Update changelog.md
cat > .opencode/command/changelog.md <<'EOF'
create UPCOMING_CHANGELOG.md

it should have sections

```
# TUI

# Desktop

# Core

# Misc
```

go through each PR merged since the last tag

for each PR spawn a subagent to summarize what the PR was about. focus on user facing changes. if it was entirely internal or code related you can ignore it. also skip docs updates. each subagent should append its summary to UPCOMING_CHANGELOG.md into the appropriate section.

once that is done, read UPCOMING_CHANGELOG.md and group it into sections for better readability. make sure all PR references are preserved
EOF

# Update worker.ts - add writeHeapSnapshot import and snapshot method
sed -i 's|import { setTimeout as sleep } from "node:timers/promises"|import { setTimeout as sleep } from "node:timers/promises"\nimport { writeHeapSnapshot } from "node:v8"|' packages/opencode/src/cli/cmd/tui/worker.ts

# Add snapshot() method to rpc object in worker.ts
sed -i '/^  },$/,/^  async server(input: { port: number; hostname: string; mdns?: boolean; cors?: string\[\] }) {$/{
  /^  async server/i\  snapshot() {\n    const result = writeHeapSnapshot("server.heapsnapshot")\n    return result\n  },
}' packages/opencode/src/cli/cmd/tui/worker.ts

# Update thread.ts - add writeHeapSnapshot import
sed -i 's|import { Instance } from "@/project/instance"|import { Instance } from "@/project/instance"\nimport { writeHeapSnapshot } from "v8"|' packages/opencode/src/cli/cmd/tui/thread.ts

# Update thread.ts - add onSnapshot callback to tui() call
# This is tricky with sed - let's use a different approach
python3 << 'PYEOF'
import re

# Read thread.ts
with open('packages/opencode/src/cli/cmd/tui/thread.ts', 'r') as f:
    content = f.read()

# Add onSnapshot callback to tui() call
old_pattern = r'await tui\({\s*url: transport\.url,'
new_code = '''await tui({
          url: transport.url,
          async onSnapshot() {
            const tui = writeHeapSnapshot("tui.heapsnapshot")
            const server = await client.call("snapshot", undefined)
            return [tui, server]
          },'''

content = re.sub(old_pattern, new_code, content)

with open('packages/opencode/src/cli/cmd/tui/thread.ts', 'w') as f:
    f.write(content)
PYEOF

# Update app.tsx - add onSnapshot prop to tui input
sed -i 's|config: TuiConfig.Info|config: TuiConfig.Info\n  onSnapshot?: () => Promise<string[]>|' packages/opencode/src/cli/cmd/tui/app.tsx

# Update app.tsx - change <App /> to <App onSnapshot={input.onSnapshot} />
sed -i 's|<App />|<App onSnapshot={input.onSnapshot} />|' packages/opencode/src/cli/cmd/tui/app.tsx

# Update app.tsx - change function App() to function App(props: ...)
sed -i 's|function App() {|function App(props: { onSnapshot?: () => Promise<string[]> }) {|' packages/opencode/src/cli/cmd/tui/app.tsx

# Update app.tsx - change heap snapshot onSelect to async and use props.onSnapshot
python3 << 'PYEOF'
import re

with open('packages/opencode/src/cli/cmd/tui/app.tsx', 'r') as f:
    content = f.read()

# Update the heap snapshot onSelect
old_code = '''onSelect: (dialog) => {
        const path = writeHeapSnapshot()
        toast.show({
          variant: "info",
          message: `Heap snapshot written to ${path}`,'''

new_code = '''onSelect: async (dialog) => {
        const files = await props.onSnapshot?.()
        toast.show({
          variant: "info",
          message: `Heap snapshot written to ${files?.join(", ")}`,'''

content = content.replace(old_code, new_code)

with open('packages/opencode/src/cli/cmd/tui/app.tsx', 'w') as f:
    f.write(content)
PYEOF

echo "Patch applied successfully."
