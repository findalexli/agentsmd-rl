#!/bin/bash
set -e

cd /workspace/transformers

# Check if already applied
if grep -q "train_sampling_strategy" src/transformers/training_args.py; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch: Unify train sampler strategy
cat > /tmp/patch.diff << 'PATCH_EOF'
diff --git a/examples/pytorch/speech-recognition/README.md b/examples/pytorch/speech-recognition/README.md
index d43d49fc90..427488b3cc 100644
--- a/examples/pytorch/speech-recognition/README.md
+++ b/examples/pytorch/speech-recognition/README.md
@@ -86,7 +86,7 @@ python run_speech_recognition_ctc.py \
 	--gradient_checkpointing \
 	--chars_to_ignore , ? . ! - \; \: \" " " % ' " \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--push_to_hub \
 	--do_train --do_eval
 ```
@@ -121,7 +121,7 @@ torchrun \
 	--gradient_checkpointing \
 	--chars_to_ignore , ? . ! - \; \: \" " " % ' " \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--push_to_hub \
 	--do_train --do_eval
 ```
@@ -300,7 +300,7 @@ python run_speech_recognition_ctc.py \
 	--gradient_checkpointing \
 	--chars_to_ignore , ? . ! - \; \: \" " " % ' " \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--do_train --do_eval \
   --push_to_hub
 ```
@@ -337,7 +337,7 @@ python run_speech_recognition_ctc.py \
 	--gradient_checkpointing \
 	--chars_to_ignore , ? . ! - \; \: \" " " % ' " \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--do_train --do_eval \
   --push_to_hub
 ```
@@ -547,7 +547,7 @@ python run_speech_recognition_seq2seq.py \
 	--freeze_feature_encoder \
 	--gradient_checkpointing \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--predict_with_generate \
 	--generation_max_length="40" \
 	--generation_num_beams="1" \
@@ -588,7 +588,7 @@ torchrun \
 	--freeze_feature_encoder \
 	--gradient_checkpointing \
 	--fp16 \
-	--group_by_length \
+	--train_sampling_strategy group_by_length \
 	--predict_with_generate \
 	--do_train --do_eval \
 	--do_lower_case

diff --git a/src/transformers/trainer.py b/src/transformers/trainer.py
index 2b48264dbc..70cac6a7f1 100755
--- a/src/transformers/trainer.py
+++ b/src/transformers/trainer.py
@@ -684,12 +684,12 @@ def _validate_args(self):
                 "The train_dataset does not implement __len__, max_steps has to be specified. "
                 "The number of steps needs to be known in advance for the learning rate scheduler."
             )
-        if (
-            self.train_dataset is not None
-            and isinstance(self.train_dataset, torch.utils.data.IterableDataset)
-            and args.group_by_length
-        ):
-            raise ValueError("the `--group_by_length` option is only available for `Dataset`, not `IterableDataset")
+
+        if self.train_dataset is not None and isinstance(self.train_dataset, torch.utils.data.IterableDataset):
+            logger.info(
+                f"The `train_sampling_strategy='{args.train_sampling_strategy}'` option is ignored when using an `IterableDataset`. "
+                "Samplers cannot be used with IterableDataset as they require indexed access to the dataset."
+            )

     def add_callback(self, callback):
         """
@@ -810,7 +810,7 @@ def _get_train_sampler(self, train_dataset: Dataset | None = None) -> torch.util
             return None

         # Build the sampler.
-        if self.args.group_by_length:
+        if self.args.train_sampling_strategy == "group_by_length":
             if is_datasets_available() and isinstance(train_dataset, datasets.Dataset):
                 lengths = (
                     train_dataset[self.args.length_column_name]
@@ -828,7 +828,8 @@ def _get_train_sampler(self, train_dataset: Dataset | None = None) -> torch.util
                 lengths=lengths,
                 model_input_name=model_input_name,
             )
-
+        elif self.args.train_sampling_strategy == "sequential":
+            return SequentialSampler(train_dataset)
         else:
             return RandomSampler(train_dataset)

@@ -906,7 +907,7 @@ def _get_eval_sampler(self, eval_dataset: Dataset) -> torch.utils.data.Sampler |
         if eval_dataset is None or not has_length(eval_dataset):
             return None

-        if self.args.group_by_length:
+        if self.args.train_sampling_strategy == "group_by_length":
             if is_datasets_available() and isinstance(eval_dataset, datasets.Dataset):
                 lengths = (
                     eval_dataset[self.args.length_column_name]
diff --git a/src/transformers/training_args.py b/src/transformers/training_args.py
index e87189dfd1..fa248b2988 100644
--- a/src/transformers/training_args.py
+++ b/src/transformers/training_args.py
@@ -601,13 +601,19 @@ class TrainingArguments:
             except if the model used is one of the `XxxForQuestionAnswering` in which case it will also include the
             `["start_positions", "end_positions"]` keys.
             You should only specify `label_names` if you're using custom label names or if your model's `forward` consumes multiple label tensors (e.g., extractive QA).
-        group_by_length (`bool`, *optional*, defaults to `False`):
-            Whether or not to group together samples of roughly the same length in the training dataset (to minimize
-            padding applied and be more efficient). Only useful if applying dynamic padding.
+        train_sampling_strategy (`str`, *optional*, defaults to `"random"`):
+            The sampler to use for the training dataloader. Possible values are:
+
+                - `"random"`: Uses `RandomSampler` (default).
+                - `"sequential"`: Uses `SequentialSampler`.
+                - `"group_by_length"`: Uses `LengthGroupedSampler` to group samples of roughly the same length
+                  together (to minimize padding and be more efficient).
+
+            Note: When using an `IterableDataset`, this argument is ignored.
         length_column_name (`str`, *optional*, defaults to `"length"`):
             Column name for precomputed lengths. If the column exists, grouping by length will use these values rather
-            than computing them on train startup. Ignored unless `group_by_length` is `True` and the dataset is an
-            instance of `Dataset`.
+            than computing them on train startup. Ignored unless `train_sampling_strategy` is `"group_by_length"` and the dataset
+            is an instance of `Dataset`.

         > DDP (DistributedDataParallel)

@@ -1300,15 +1306,18 @@ class TrainingArguments:
     label_names: list[str] | None = field(
         default=None, metadata={"help": "The list of keys in your dictionary of inputs that correspond to the labels."}
     )
-    group_by_length: bool = field(
-        default=False,
+    train_sampling_strategy: str = field(
+        default="random",
         metadata={
-            "help": "Whether or not to group samples of roughly the same length together when batching. Only useful if applying dynamic padding."
+            "help": "Sampler for training: 'random' (default), 'sequential', or 'group_by_length'.",
+            "choices": ["random", "sequential", "group_by_length"],
         },
     )
     length_column_name: str = field(
         default="length",
-        metadata={"help": "Column name for precomputed lengths. Ignored unless `group_by_length` is True."},
+        metadata={
+            "help": "Column name for precomputed lengths. Ignored unless `train_sampling_strategy` is 'group_by_length'."
+        },
     )

     # --- DDP ---
PATCH_EOF

# Apply the patch
git apply /tmp/patch.diff

echo "Gold patch applied successfully!"
