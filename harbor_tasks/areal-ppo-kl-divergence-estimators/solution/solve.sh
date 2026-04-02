#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency check: see if KL divergence estimators are already added
if grep -q 'kl_div_estimator_direct' areal/trainer/ppo/actor.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
target = "areal/trainer/ppo/actor.py"
with open(target) as f:
    content = f.read()

# Insert KL divergence estimators BEFORE the versions early-return,
# so they fire whenever logprobs is available (regardless of versions).
anchor = """\
        # Skip if versions not available
        if versions is None or current_version is None:
            return"""

insertion = """\
        if logprobs is not None:
            # Log KL divergence estimators to check for policy drift between the
            # training-time policy (logprobs) and the inference-time policy (old_logp).
            log_ratio = (logprobs.float() - old_logp.float()).detach()

            # Implementation of different estimators for KL divergence.
            kl_div_estimator_direct = -log_ratio
            kl_div_estimator_taylor = log_ratio**2 / 2.0
            kl_div_estimator_dual = log_ratio.exp() - 1 - log_ratio

            # Register these to TensorBoard
            stats_tracker.stat(
                kl_div_direct=kl_div_estimator_direct,
                kl_div_taylor=kl_div_estimator_taylor,
                kl_div_dual=kl_div_estimator_dual,
                denominator="n_valid_tokens",
            )

"""

if anchor not in content:
    print("ERROR: anchor not found in file")
    exit(1)

content = content.replace(anchor, insertion + anchor)

with open(target, "w") as f:
    f.write(content)

print("Patch applied successfully.")
PYEOF
