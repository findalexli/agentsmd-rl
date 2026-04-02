#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

TARGET="slime/backends/megatron_utils/arguments.py"

if grep -q "rope_parameters" "$TARGET" 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

python3 <<'PYEOF'
import pathlib

target = pathlib.Path("slime/backends/megatron_utils/arguments.py")
src = target.read_text()

# 1. Insert rope_parameters dict extraction before the for loop
old_for = '    for hf_config_name, megatron_config_name, compare_fn in ['
new_block = '''\
    # Some models store rope_theta inside rope_parameters dict rather than
    # as a top-level attribute.  Prefer the dict value when available so
    # the validation doesn't compare against a stale class default.
    rope_params = getattr(hf_config, "rope_parameters", None)
    if isinstance(rope_params, dict) and "rope_theta" in rope_params:
        _hf_rope_theta = rope_params["rope_theta"]
    else:
        _hf_rope_theta = getattr(hf_config, "rope_theta", None)

    for hf_config_name, megatron_config_name, compare_fn in ['''
src = src.replace(old_for, new_block, 1)

# 2. Remove rope_theta from the generic validation loop
src = src.replace('        ("rope_theta", "rotary_base", equal),\n', '', 1)

# 3. Insert separate rope_theta validation before the error raise
old_raise = '    if len(errors) > 0:'
new_validation = '''\
    # Validate rope_theta separately using the resolved value
    if _hf_rope_theta is not None:
        if not equal(_hf_rope_theta, getattr(args, "rotary_base", None)):
            errors.append(
                f"rope_theta in hf config {_hf_rope_theta} is not equal to "
                f"rotary_base {getattr(args, \'rotary_base\', None)}, please check the config."
            )

    if len(errors) > 0:'''
src = src.replace(old_raise, new_validation, 1)

target.write_text(src)
print("Patch applied successfully.")
PYEOF
