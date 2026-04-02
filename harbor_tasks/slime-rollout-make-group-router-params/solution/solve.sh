#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency: skip if already patched
if grep -q 'def _make_group(group_cfg, router_ip, router_port' slime/ray/rollout.py 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index 3df73c41da..7ea0d12b56 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -1007,7 +1007,7 @@ def start_rollout_servers(args, pg) -> dict[str, RolloutServer]:

         has_epd = model_cfg.has_encoder_disaggregation

-        def _make_group(group_cfg, overrides_extra=None):
+        def _make_group(group_cfg, router_ip, router_port, overrides_extra=None):
             nonlocal engine_offset, gpu_offset
             gpus_per_engine = group_cfg.num_gpus_per_engine
             num_gpu_per_engine_local = min(gpus_per_engine, args.num_gpus_per_node)
@@ -1051,7 +1051,7 @@ def _make_group(group_cfg, overrides_extra=None):
             for group_cfg in model_cfg.server_groups:
                 if group_cfg.worker_type != "encoder":
                     continue
-                group = _make_group(group_cfg)
+                group = _make_group(group_cfg, router_ip, router_port)
                 handles, port_cursors = group.start_engines(port_cursors)
                 if handles:
                     ray.get(handles)
@@ -1070,7 +1070,7 @@ def _make_group(group_cfg, overrides_extra=None):
                 if encoder_urls and group_cfg.worker_type == "prefill":
                     overrides_extra["language_only"] = True
                     overrides_extra["encoder_urls"] = encoder_urls
-                group = _make_group(group_cfg, overrides_extra=overrides_extra)
+                group = _make_group(group_cfg, router_ip, router_port, overrides_extra=overrides_extra)
                 handles, port_cursors = group.start_engines(port_cursors)
                 non_encoder_handles.extend(handles)
                 server_groups.append(group)
@@ -1081,7 +1081,7 @@ def _make_group(group_cfg, overrides_extra=None):
             # No EPD — start all groups in one pass (original path).
             all_init_handles: list = []
             for group_cfg in model_cfg.server_groups:
-                group = _make_group(group_cfg)
+                group = _make_group(group_cfg, router_ip, router_port)
                 handles, port_cursors = group.start_engines(port_cursors)
                 all_init_handles.extend(handles)
                 server_groups.append(group)

PATCH

echo "Patch applied successfully."
