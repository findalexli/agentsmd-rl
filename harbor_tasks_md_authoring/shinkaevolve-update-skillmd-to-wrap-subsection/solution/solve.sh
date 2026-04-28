#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shinkaevolve

# Idempotency guard
if grep -qF "## Template: `evaluate.py` (non-Python `initial.<ext>` path)" "skills/shinka-setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/shinka-setup/SKILL.md b/skills/shinka-setup/SKILL.md
@@ -100,7 +100,7 @@ Rules:
 - Non-Python candidates: evaluate via `subprocess` and write `metrics.json` + `correct.json`.
 - Always set both `evo_config.language` and matching `evo_config.init_program_path`.
 
-## Template: initial.<ext> (Python example)
+## Template: `initial.<ext>` (Python example)
 ```py
 import random
 
@@ -124,7 +124,7 @@ def run_experiment(random_seed: int | None = None, **kwargs):
 
 For non-Python `initial.<ext>`, keep the same idea: small evolve region + deterministic program interface consumed by `evaluate.py`.
 
-## Template: evaluate.py (Python `run_shinka_eval` path)
+## Template: `evaluate.py` (Python `run_shinka_eval` path)
 ```py
 import argparse
 import numpy as np
@@ -178,7 +178,7 @@ if __name__ == "__main__":
     main(program_path=args.program_path, results_dir=args.results_dir)
 ```
 
-## Template: evaluate.py (non-Python `initial.<ext>` path)
+## Template: `evaluate.py` (non-Python `initial.<ext>` path)
 ```py
 import argparse
 import json
@@ -217,11 +217,11 @@ if __name__ == "__main__":
     main(program_path=args.program_path, results_dir=args.results_dir)
 ```
 
-## (Optional) Template: run_evo.py (async)
+## (Optional) Template: `run_evo.py` (async)
 
 See `skills/shinka-setup/scripts/run_evo.py` for an example to edit.
 
-## (Optional) Template: shinka.yaml
+## (Optional) Template: `shinka.yaml`
 
 See `skills/shinka-setup/scripts/shinka.yaml` for an example to edit.
 
PATCH

echo "Gold patch applied."
