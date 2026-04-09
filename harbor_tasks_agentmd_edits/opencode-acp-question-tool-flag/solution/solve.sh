#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'OPENCODE_ENABLE_QUESTION_TOOL' packages/opencode/src/flag/flag.ts 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

echo 'Applying OPENCODE_ENABLE_QUESTION_TOOL changes...'

# 1. Update flag.ts - add OPENCODE_ENABLE_QUESTION_TOOL constant after OPENCODE_SERVER_USERNAME
sed -i '/export const OPENCODE_SERVER_USERNAME = process.env\["OPENCODE_SERVER_USERNAME"\]/a\  export const OPENCODE_ENABLE_QUESTION_TOOL = truthy("OPENCODE_ENABLE_QUESTION_TOOL")' packages/opencode/src/flag/flag.ts

# 2. Update registry.ts - add question variable after config line
sed -i '/const config = await Config.get()/a\    const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL' packages/opencode/src/tool/registry.ts

# 3. Update registry.ts - replace the QuestionTool conditional to use question variable  
sed -i 's/(\["app", "cli", "desktop"\].includes(Flag.OPENCODE_CLIENT) ? \[QuestionTool\] : \[\])/(question ? [QuestionTool] : [])/' packages/opencode/src/tool/registry.ts

# 4. Update translator.md - add the env var after OPENCODE_EXPERIMENTAL_PLAN_MODE
sed -i '/^OPENCODE_EXPERIMENTAL_PLAN_MODE$/a\OPENCODE_ENABLE_QUESTION_TOOL' .opencode/agent/translator.md

# 5. Update acp/README.md - add the Question Tool Opt-In section before '### Programmatic'
LINE=$(grep -n '### Programmatic' packages/opencode/src/acp/README.md | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    head -n $((LINE-1)) packages/opencode/src/acp/README.md > /tmp/readme_part1.txt
    tail -n +$LINE packages/opencode/src/acp/README.md > /tmp/readme_part2.txt
    cat > /tmp/readme_new_section.txt << 'SECTIONEOF'
### Question Tool Opt-In

ACP excludes `QuestionTool` by default.

```bash
OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp
```

Enable this only for ACP clients that support interactive question prompts.

SECTIONEOF
    cat /tmp/readme_part1.txt /tmp/readme_new_section.txt /tmp/readme_part2.txt > packages/opencode/src/acp/README.md
fi

echo 'Patch applied successfully.'
