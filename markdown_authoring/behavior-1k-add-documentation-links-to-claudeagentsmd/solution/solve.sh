#!/usr/bin/env bash
set -euo pipefail

cd /workspace/behavior-1k

# Idempotency guard
if grep -qF "OmniGibson currently uses [Isaac Sim 5.1](https://docs.isaacsim.omniverse.nvidia" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -79,6 +79,8 @@ under the `isaacsim` package. Everything from isaacsim needs to be imported usin
 (e.g. through simulator.py's launch_app). You can follow most of these imports to the source code by finding the appropriate extension inside the isaacsim directory. Especially
 relevant extensions' names start with isaacsim.core.
 
+OmniGibson currently uses [Isaac Sim 5.1](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/) and [Omniverse Kit 107.3.1](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/107.3.1/). This [documentation for USDRT](https://docs.omniverse.nvidia.com/kit/docs/usdrt.scenegraph/7.6.1/index.html#usdrt-scenegraph-module) may also be especially useful for understanding Fabric and USD syncing. When following the links, make sure not to add an extra "docs/" to the href.
+
 ### BDDL3 (`bddl3/bddl/`)
 - **`activity_definitions/`** — One file per activity with symbolic pre/post conditions.
 - **`object_taxonomy.py`** — Hierarchical object ontology.
PATCH

echo "Gold patch applied."
