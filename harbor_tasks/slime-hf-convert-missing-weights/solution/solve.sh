#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'converted_names = set()' tools/convert_torch_dist_to_hf.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tools/convert_torch_dist_to_hf.py b/tools/convert_torch_dist_to_hf.py
index 2ddd1b7b1..dbb144b5f 100644
--- a/tools/convert_torch_dist_to_hf.py
+++ b/tools/convert_torch_dist_to_hf.py
@@ -103,18 +103,20 @@ def get_named_params(args, state_dict):
         yield from get_layer_param(args, name, param)


-def save_tensors(args, model_name, state_dict, output_dir, chunk_size, vocab_size=None):
+def save_tensors(args, model_name, state_dict, output_dir, chunk_size, vocab_size=None, origin_hf_dir=None):
     print(f"start saving to {output_dir}")
     os.makedirs(output_dir, exist_ok=True)
     # 2GB
     current_size = 0
     total_size = 0
     modeltensors = [{}]
+    converted_names = set()
     for name, param in get_named_params(args, state_dict):
         if vocab_size:
             param = remove_padding(name, param, vocab_size)
         converted_named_tensors = convert_to_hf(args, model_name, name, param)
         for converted_name, converted_param in converted_named_tensors:
+            converted_names.add(converted_name)
             tensor_size = converted_param.numel() * converted_param.element_size()
             if tensor_size + current_size > chunk_size:
                 modeltensors.append({})
@@ -123,6 +125,24 @@ def save_tensors(args, model_name, state_dict, output_dir, chunk_size, vocab_siz
             current_size += tensor_size
             total_size += tensor_size

+    if origin_hf_dir is not None:
+        safetensors_files = [f for f in os.listdir(origin_hf_dir) if f.endswith(".safetensors")]
+        for filename in safetensors_files:
+            with safetensors.safe_open(os.path.join(origin_hf_dir, filename), framework="pt", device="cuda") as f:
+                for k in f.keys():
+                    if k not in converted_names:
+                        converted_name = k
+                        print(f"add {k} from origin hf checkpoint")
+                        converted_param = f.get_tensor(k)
+                        converted_names.add(k)
+                        tensor_size = converted_param.numel() * converted_param.element_size()
+                        if tensor_size + current_size > chunk_size:
+                            modeltensors.append({})
+                            current_size = 0
+                        modeltensors[-1][converted_name] = converted_param
+                        current_size += tensor_size
+                    total_size += tensor_size
+
     metadata = {"metadata": {"total_size": total_size}, "weight_map": {}}

     num_files = len(modeltensors)
@@ -169,6 +189,9 @@ def copy_assets(origin_hf_dir, output_dir):
     parser.add_argument(
         "-f", "--force", action="store_true", help="Force overwrite the output directory if it exists."
     )
+    parser.add_argument(
+        "-a", "--add-missing-from-origin-hf", action="store_true", help="Add missing weights from origin hf checkpoint"
+    )
     parser.add_argument(
         "--chunk-size",
         type=int,
@@ -207,7 +230,15 @@ def copy_assets(origin_hf_dir, output_dir):
     )
     print(f"model loaded in {time.time()-t:.2f} sec.")

-    save_tensors(megatron_args, args.model_name, state_dict, args.output_dir, args.chunk_size, args.vocab_size)
+    save_tensors(
+        megatron_args,
+        args.model_name,
+        state_dict,
+        args.output_dir,
+        args.chunk_size,
+        args.vocab_size,
+        args.origin_hf_dir if args.add_missing_from_origin_hf else None,
+    )

     if args.origin_hf_dir:
         copy_assets(args.origin_hf_dir, args.output_dir)

PATCH

echo "Patch applied successfully."
