#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check: if "encoder" is already a valid worker_type, patch is applied
if grep -q '"encoder"' slime/backends/sglang_utils/sglang_config.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/sglang_utils/sglang_config.py b/slime/backends/sglang_utils/sglang_config.py
index e3e566f43a..827b47a1bd 100644
--- a/slime/backends/sglang_utils/sglang_config.py
+++ b/slime/backends/sglang_utils/sglang_config.py
@@ -13,8 +13,13 @@ class ServerGroupConfig:
     """Configuration for a single server group.

     Attributes:
-        worker_type: One of "regular", "prefill", "decode", or "placeholder".
+        worker_type: One of "regular", "prefill", "decode", "placeholder",
+                     or "encoder".
                      "placeholder" reserves GPU slots without creating engines.
+                     "encoder" creates encoder-only engines for EPD
+                     (Encoder-Prefill-Decode) disaggregation; encoder engines
+                     are started first and their URLs are automatically
+                     injected into prefill groups as ``encoder_urls``.
         num_gpus: Total number of GPUs for this group.
         num_gpus_per_engine: GPUs per engine for this group.  Overrides the
                              model-level or global ``--rollout-num-gpus-per-engine``.
@@ -29,7 +34,7 @@ class ServerGroupConfig:
     overrides: dict = dataclasses.field(default_factory=dict)

     def __post_init__(self):
-        valid_types = {"regular", "prefill", "decode", "placeholder"}
+        valid_types = {"regular", "prefill", "decode", "placeholder", "encoder"}
         assert (
             self.worker_type in valid_types
         ), f"Invalid worker_type '{self.worker_type}', must be one of {valid_types}"
@@ -98,6 +103,10 @@ def resolve(self, args) -> None:
     def has_pd_disaggregation(self) -> bool:
         return any(g.worker_type in ("prefill", "decode") for g in self.server_groups)

+    @property
+    def has_encoder_disaggregation(self) -> bool:
+        return any(g.worker_type == "encoder" for g in self.server_groups)
+
     @property
     def total_num_gpus(self) -> int:
         return sum(g.num_gpus for g in self.server_groups)
diff --git a/slime/backends/sglang_utils/sglang_engine.py b/slime/backends/sglang_utils/sglang_engine.py
index bed0cf0b2c..b03a7a5982 100644
--- a/slime/backends/sglang_utils/sglang_engine.py
+++ b/slime/backends/sglang_utils/sglang_engine.py
@@ -51,7 +51,10 @@ def _to_local_gpu_id(physical_gpu_id: int) -> int:


 def launch_server_process(server_args: ServerArgs) -> multiprocessing.Process:
-    from sglang.srt.entrypoints.http_server import launch_server
+    if server_args.encoder_only:
+        from sglang.srt.disaggregation.encode_server import launch_server
+    else:
+        from sglang.srt.entrypoints.http_server import launch_server

     multiprocessing.set_start_method("spawn", force=True)
     server_args.host = server_args.host.strip("[]")
@@ -188,6 +191,9 @@ def _init_normal(self, server_args_dict):
         logger.info(f"Launch HttpServerEngineAdapter at: {self.server_host}:{self.server_port}")
         self.process = launch_server_process(ServerArgs(**server_args_dict))

+        if self.worker_type == "encoder":
+            return
+
         if self.node_rank == 0 and self.router_ip and self.router_port:
             if parse(sglang_router.__version__) <= parse("0.2.1") or self.args.use_slime_router:
                 assert (
@@ -246,12 +252,13 @@ def health_generate(self, timeout: float = 5.0) -> bool:
         if self.node_rank != 0:
             return True

-        response = requests.get(
-            f"http://{self.server_host}:{self.server_port}/health_generate",
-            timeout=timeout,
-        )
-        response.raise_for_status()
-        return True
+        url = f"http://{self.server_host}:{self.server_port}/health_generate"
+        try:
+            response = requests.get(url, timeout=timeout)
+            response.raise_for_status()
+            return True
+        except requests.RequestException:
+            raise

     def update_weights_from_tensor(
         self,
@@ -297,12 +304,17 @@ def flush_cache(self):
         else:
             raise TimeoutError("Timeout while flushing cache.")

+    def get_url(self):
+        if self.node_rank != 0:
+            return None
+        return f"http://{self.server_host}:{self.server_port}"
+
     def shutdown(self):
         if self.args.rollout_external:
             return

         logger.info(f"Shutdown engine {self.server_host}:{self.server_port}...")
-        if self.node_rank == 0:
+        if self.worker_type != "encoder" and self.node_rank == 0:
             worker_url = f"http://{self.server_host}:{self.server_port}"
             response = None
             if parse(sglang_router.__version__) <= parse("0.2.1") or self.args.use_slime_router:
@@ -537,6 +549,8 @@ def _compute_server_args(
     elif worker_type == "decode":
         kwargs["disaggregation_mode"] = "decode"
         kwargs["prefill_round_robin_balance"] = True
+    elif worker_type == "encoder":
+        kwargs["encoder_only"] = True

     if args.use_rollout_routing_replay:
         kwargs["enable_return_routed_experts"] = True
@@ -544,8 +558,10 @@ def _compute_server_args(
         kwargs["dtype"] = "float16"
     external_engine_need_check_fields = [k for k in kwargs.keys() if k not in _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS]

+    server_arg_fields = dataclasses.fields(ServerArgs)
+    server_arg_field_names = {attr.name for attr in server_arg_fields}
     unused_keys = set(kwargs.keys())
-    for attr in dataclasses.fields(ServerArgs):
+    for attr in server_arg_fields:
         if worker_type == "decode" and attr.name == "enable_hierarchical_cache":
             continue
         if hasattr(args, f"sglang_{attr.name}") and attr.name not in kwargs:
@@ -556,10 +572,21 @@ def _compute_server_args(
     # Applied after base args so they take highest priority.
     if sglang_overrides:
         for key, value in sglang_overrides.items():
-            if key in kwargs:
-                logger.info(f"sglang_overrides: overriding {key}={kwargs[key]} -> {value} (rank={rank})")
-            kwargs[key] = value
-            unused_keys.discard(key)
+            normalized_key = key.replace("-", "_")
+            if normalized_key != key:
+                logger.warning(
+                    f"sglang_overrides key '{key}' normalized to '{normalized_key}' (rank={rank}). "
+                    "Please use underscore style in YAML overrides."
+                )
+            if normalized_key in kwargs:
+                logger.info(
+                    f"sglang_overrides: overriding {normalized_key}={kwargs[normalized_key]} -> {value} (rank={rank})"
+                )
+            kwargs[normalized_key] = value
+            if normalized_key in server_arg_field_names:
+                unused_keys.discard(normalized_key)
+            else:
+                unused_keys.add(normalized_key)

     # for compatibility with old args
     if len(unused_keys) > 0:
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index cd501bd10d..3df73c41da 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -1003,18 +1003,22 @@ def start_rollout_servers(args, pg) -> dict[str, RolloutServer]:
             args.sglang_router_port = router_port

         server_groups: list[ServerGroup] = []
-        all_init_handles: list = []
         port_cursors: dict[int, int] = {}

-        for group_cfg in model_cfg.server_groups:
+        has_epd = model_cfg.has_encoder_disaggregation
+
+        def _make_group(group_cfg, overrides_extra=None):
+            nonlocal engine_offset, gpu_offset
             gpus_per_engine = group_cfg.num_gpus_per_engine
             num_gpu_per_engine_local = min(gpus_per_engine, args.num_gpus_per_node)
             num_engines = group_cfg.num_gpus // num_gpu_per_engine_local

-            # Only offload groups whose GPUs overlap with megatron.
             group_abs_start = rollout_pg_offset + gpu_offset
             needs_offload = args.offload_rollout and group_abs_start < megatron_num_gpus
             overrides = dict(group_cfg.overrides)
+            if overrides_extra:
+                for k, v in overrides_extra.items():
+                    overrides.setdefault(k, v)
             if args.offload_rollout and not needs_offload:
                 overrides.setdefault("enable_memory_saver", False)
             logger.info(
@@ -1037,15 +1041,53 @@ def start_rollout_servers(args, pg) -> dict[str, RolloutServer]:
                 router_ip=router_ip,
                 router_port=router_port,
             )
-            handles, port_cursors = group.start_engines(port_cursors)
-            all_init_handles.extend(handles)
-            server_groups.append(group)
-
             engine_offset += num_engines
             gpu_offset += group_cfg.num_gpus
+            return group

-        if all_init_handles:
-            ray.get(all_init_handles)
+        if has_epd:
+            # --- Phase 1: start encoder groups, wait, collect URLs ---
+            encoder_urls: list[str] = []
+            for group_cfg in model_cfg.server_groups:
+                if group_cfg.worker_type != "encoder":
+                    continue
+                group = _make_group(group_cfg)
+                handles, port_cursors = group.start_engines(port_cursors)
+                if handles:
+                    ray.get(handles)
+                urls = ray.get([e.get_url.remote() for e in group.engines])
+                encoder_urls.extend(u for u in urls if u is not None)
+                server_groups.append(group)
+
+            logger.info(f"EPD phase 1 done: collected {len(encoder_urls)} encoder URLs: {encoder_urls}")
+
+            # --- Phase 2: start non-encoder groups, injecting encoder URLs into prefill ---
+            non_encoder_handles: list = []
+            for group_cfg in model_cfg.server_groups:
+                if group_cfg.worker_type == "encoder":
+                    continue
+                overrides_extra = {}
+                if encoder_urls and group_cfg.worker_type == "prefill":
+                    overrides_extra["language_only"] = True
+                    overrides_extra["encoder_urls"] = encoder_urls
+                group = _make_group(group_cfg, overrides_extra=overrides_extra)
+                handles, port_cursors = group.start_engines(port_cursors)
+                non_encoder_handles.extend(handles)
+                server_groups.append(group)
+
+            if non_encoder_handles:
+                ray.get(non_encoder_handles)
+        else:
+            # No EPD — start all groups in one pass (original path).
+            all_init_handles: list = []
+            for group_cfg in model_cfg.server_groups:
+                group = _make_group(group_cfg)
+                handles, port_cursors = group.start_engines(port_cursors)
+                all_init_handles.extend(handles)
+                server_groups.append(group)
+
+            if all_init_handles:
+                ray.get(all_init_handles)

         servers[model_cfg.name] = RolloutServer(
             server_groups=server_groups,

PATCH

echo "Patch applied successfully."
