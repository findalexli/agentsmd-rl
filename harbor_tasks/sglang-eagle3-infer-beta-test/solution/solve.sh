#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'DEFAULT_TARGET_MODEL_EAGLE3' test/registered/spec/eagle/test_eagle_infer_beta.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply using Python for reliable multi-line edits
python3 << 'PYEOF'
import re

with open('test/registered/spec/eagle/test_eagle_infer_beta.py', 'r') as f:
    content = f.read()

# 1. Update imports: DEFAULT_DRAFT_MODEL_EAGLE -> DEFAULT_DRAFT_MODEL_EAGLE3
content = content.replace('DEFAULT_DRAFT_MODEL_EAGLE,', 'DEFAULT_DRAFT_MODEL_EAGLE3,')
content = content.replace('DEFAULT_TARGET_MODEL_EAGLE,', 'DEFAULT_TARGET_MODEL_EAGLE3,')

# 2. Update class names
content = content.replace('class TestEagleServerBase(CustomTestCase, MatchedStopMixin):',
                         'class TestEagle3ServerBase(CustomTestCase, MatchedStopMixin):')
content = content.replace('class TestEagleServerPage(TestEagleServerBase):',
                         'class TestEagle3ServerPage(TestEagle3ServerBase):')

# 3. Update speculative algorithm
content = content.replace('"EAGLE",', '"EAGLE3",')

# 4. Add --dtype=float16 after --trust-remote-code
content = content.replace(
    '"--trust-remote-code",',
    '"--trust-remote-code",\n            "--dtype=float16",'
)

# 5. Add --chunked-prefill-size and 1024
content = content.replace(
    '"--dtype=float16",',
    '"--dtype=float16",\n            "--chunked-prefill-size",\n            "1024",'
)

# 6. Add SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN env override
# Find the pattern and add after it
old_env = '        ), envs.SGLANG_SPEC_OOB_DETECTION.override(\n            True\n        ):'
new_env = '        ), envs.SGLANG_SPEC_OOB_DETECTION.override(\n            True\n        ), envs.SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN.override(\n            True\n        ):'
content = content.replace(old_env, new_env)

# 7. Update test name in print statement
content = content.replace('print(f"TestEagleLargeBS -- {metrics=}")',
                         'print(f"TestEagle3LargeBS -- {metrics=}")')

# 8. Update score threshold and remove multi-line assert
old_assert = '''        self.assertGreater(
            metrics["score"], 0.22
        )  # ~0.227 for 1000 questions via /v1/completions'''
new_assert = '        self.assertGreater(metrics["score"], 0.7)'
content = content.replace(old_assert, new_assert)

with open('test/registered/spec/eagle/test_eagle_infer_beta.py', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
PYEOF
