#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if grep -q 'extras\["docs"\]' setup.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 9d9f32c1138c..0bcbca8bcbff 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -394,7 +394,7 @@ You'll need **[Python 3.9](https://github.com/huggingface/transformers/blob/main
    make sure you install the [documentation builder](https://github.com/huggingface/doc-builder).

    ```bash
-   pip install hf-doc-builder
+   pip install ".[docs]"
    ```

    Run the following command from the root of the repository:
@@ -406,6 +406,18 @@ You'll need **[Python 3.9](https://github.com/huggingface/transformers/blob/main
    This will build the documentation in the `~/tmp/test-build` folder where you can inspect the generated
    Markdown files with your favorite editor. You can also preview the docs on GitHub when you open a pull request.

+   If you're adding or editing runnable examples in Markdown docs, mark Python fences with `runnable` or
+   `runnable:<label>` and run them locally with `pytest`:
+
+   ```bash
+   pytest -q docs/source/en/my_page.md
+   pytest -q docs/source/en/
+   ```
+
+   For the full runnable syntax, including continuation blocks, `# pytest-decorator:`, and
+   `# doc-builder: hide`, see the
+   [doc-builder runnable code blocks guide](https://github.com/huggingface/doc-builder/blob/main/docs/runnable-code-blocks.md).
+
    Once you're happy with your changes, add the changed files with `git add` and
    record your changes locally with `git commit`:

diff --git a/docs/source/en/model_doc/glmasr.md b/docs/source/en/model_doc/glmasr.md
index 747d421219f1..5b52af8dce64 100644
--- a/docs/source/en/model_doc/glmasr.md
+++ b/docs/source/en/model_doc/glmasr.md
@@ -49,7 +49,8 @@ you can check the [model card](https://huggingface.co/zai-org/GLM-ASR-Nano-2512)
 <options id="usage">
 <hfoption id="AutoModel">

-```py
+```py runnable:test_basic
+# pytest-decorator: transformers.testing_utils.slow, transformers.testing_utils.require_torch
 from transformers import AutoModelForSeq2SeqLM, AutoProcessor

 processor = AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")
@@ -61,6 +62,7 @@ inputs = inputs.to(model.device, dtype=model.dtype)
 outputs = model.generate(**inputs, do_sample=False, max_new_tokens=500)

 decoded_outputs = processor.batch_decode(outputs[:, inputs.input_ids.shape[1] :], skip_special_tokens=True)
+assert len(decoded_outputs) == 1  # nodoc
 print(decoded_outputs)
 ```

@@ -71,10 +73,12 @@ print(decoded_outputs)

 The processor's `apply_transcription_request` is equivalent to using the chat template in the following manner:

-```py
+```py runnable:test_advanced
+# pytest-decorator: transformers.testing_utils.slow, transformers.testing_utils.require_torch
 from transformers import GlmAsrForConditionalGeneration, AutoProcessor

-processor = GlmAsrForConditionalGeneration.from_pretrained("zai-org/GLM-ASR-Nano-2512")
+processor = AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")
+model = GlmAsrForConditionalGeneration.from_pretrained("zai-org/GLM-ASR-Nano-2512", dtype="auto", device_map="auto")

 inputs = processor.apply_transcription_request("https://huggingface.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/bcn_weather.mp3")

@@ -98,13 +102,20 @@ inputs = processor.apply_chat_template(
     add_generation_prompt=True,
     return_dict=True,
 )
+
+inputs = inputs.to(model.device, dtype=model.dtype)
+outputs = model.generate(**inputs, do_sample=False, max_new_tokens=500)
+
+decoded_outputs = processor.batch_decode(outputs[:, inputs.input_ids.shape[1] :], skip_special_tokens=True)
+print(decoded_outputs)
 ```

 One can also use audio arrays directly:

-```py
+```py runnable:test_audio_array
+# pytest-decorator: transformers.testing_utils.slow, transformers.testing_utils.require_torch
 from transformers import GlmAsrForConditionalGeneration, AutoProcessor
-from datasets import load_dataset
+from datasets import load_dataset, Audio

 processor = AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")
 model = GlmAsrForConditionalGeneration.from_pretrained("zai-org/GLM-ASR-Nano-2512", dtype="auto", device_map="auto")
@@ -127,22 +138,68 @@ print(decoded_outputs)

 You can process multiple audio files at once:

-```py
-from transformers import GlmAsrForConditionalGeneration, AutoProcessor
+```py runnable:test_batched
+# pytest-decorator: transformers.testing_utils.slow, transformers.testing_utils.require_torch
+import torch
+from transformers import AutoProcessor, GlmAsrForConditionalGeneration

-processor = AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")
-model = GlmAsrForConditionalGeneration.from_pretrained("zai-org/GLM-ASR-Nano-2512", dtype="auto", device_map="auto")
+checkpoint_name = "zai-org/GLM-ASR-Nano-2512"
+processor = AutoProcessor.from_pretrained(checkpoint_name)
+
+conversation = [
+    [
+        {
+            "role": "user",
+            "content": [
+                {
+                    "type": "audio",
+                    "url": "https://huggingface.co/datasets/eustlb/audio-samples/resolve/main/bcn_weather.mp3",
+                },
+                {"type": "text", "text": "Please transcribe this audio into text"},
+            ],
+        },
+    ],
+    [
+        {
+            "role": "user",
+            "content": [
+                {
+                    "type": "audio",
+                    "url": "https://huggingface.co/datasets/eustlb/audio-samples/resolve/main/obama2.mp3",
+                },
+                {"type": "text", "text": "Please transcribe this audio into text"},
+            ],
+        },
+    ],
+]

-inputs = processor.apply_transcription_request([
-    "https://huggingface.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/bcn_weather.mp3",
-    "https://huggingface.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/obama.mp3",
-])
+model = GlmAsrForConditionalGeneration.from_pretrained(checkpoint_name, device_map="auto", dtype="auto")
+
+inputs = processor.apply_chat_template(
+    conversation, tokenize=True, add_generation_prompt=True, return_dict=True
+).to(model.device, dtype=model.dtype)
+
+inputs_transcription = processor.apply_transcription_request(
+    [
+        "https://huggingface.co/datasets/eustlb/audio-samples/resolve/main/bcn_weather.mp3",
+        "https://huggingface.co/datasets/eustlb/audio-samples/resolve/main/obama2.mp3",
+    ],
+).to(model.device, dtype=model.dtype)
+
+for key in inputs:  # doc-builder: ignore-bare-assert
+    assert torch.equal(inputs[key], inputs_transcription[key])

-inputs = inputs.to(model.device, dtype=model.dtype)
 outputs = model.generate(**inputs, do_sample=False, max_new_tokens=500)

-decoded_outputs = processor.batch_decode(outputs[:, inputs.input_ids.shape[1] :], skip_special_tokens=True)
-print(decoded_outputs)
+decoded_outputs = processor.batch_decode(
+    outputs[:, inputs.input_ids.shape[1] :], skip_special_tokens=True
+)
+
+EXPECTED_OUTPUT = [
+    "Yesterday it was thirty five degrees in Barcelona, but today the temperature will go down to minus twenty degrees.",
+    "This week, I traveled to Chicago to deliver my final farewell address to the nation, following in the tradition of presidents before me. It was an opportunity to say thank you. Whether we've seen eye to eye or rarely agreed at all, my conversations with you, the American people, in living rooms and schools, at farms and on factory floors, at diners and on distant military outposts, all these conversations are what have kept me honest, kept me inspired, and kept me going. Every day, I learned from you. You made me a better president, and you made me a better man. Over the",
+]
+assert decoded_outputs == EXPECTED_OUTPUT
 ```

 ## GlmAsrEncoderConfig
diff --git a/docs/source/en/testing.md b/docs/source/en/testing.md
index cefc69ee3b54..59f004e5b145 100644
--- a/docs/source/en/testing.md
+++ b/docs/source/en/testing.md
@@ -216,6 +216,21 @@ pytest --doctest-modules <path_to_file_or_dir>

 If the file has a markdown extension, you should add the `--doctest-glob="*.md"` argument.

+#### Run runnable Markdown blocks
+
+Markdown pages can also include runnable Python fences marked with `runnable` or `runnable:<label>`.
+When `hf-doc-builder` is installed, `pytest` can collect and execute those blocks directly from a documentation page
+or from the whole documentation tree:
+
+```bash
+pytest -q docs/source/en/my_page.md
+pytest -q docs/source/en/
+```
+
+For the full authoring syntax, including continuation blocks, `# pytest-decorator:`, and
+`# doc-builder: hide`, see the
+[doc-builder runnable code blocks guide](https://github.com/huggingface/doc-builder/blob/main/docs/runnable-code-blocks.md).
+
 ### Run only modified tests

 You can run the tests related to the unstaged files or the current branch (according to Git) by using [pytest-picked](https://github.com/anapaulagomes/pytest-picked). This is a great way of quickly testing your changes didn't break
diff --git a/setup.py b/setup.py
index 22b4ffc7fbe7..cb93750074bb 100644
--- a/setup.py
+++ b/setup.py
@@ -85,7 +85,7 @@
     "filelock",
     "fugashi>=1.0",
     "GitPython<3.1.19",
-    "hf-doc-builder>=0.3.0",
+    "hf-doc-builder @ git+https://github.com/huggingface/doc-builder.git@main",
     "huggingface-hub>=1.5.0,<2.0",
     "ipadic>=1.0.0,<2.0",
     "jinja2>=3.1.0",
@@ -183,6 +183,7 @@ def deps_list(*pkgs):
 extras["video"] = deps_list("av")
 extras["timm"] = deps_list("timm")
 extras["quality"] = deps_list("datasets", "ruff", "GitPython", "urllib3", "libcst", "rich", "ty", "tomli")
+extras["docs"] = deps_list("hf-doc-builder")
 extras["kernels"] = deps_list("kernels")
 extras["sentencepiece"] = deps_list("sentencepiece", "protobuf")
 extras["tiktoken"] = deps_list("tiktoken", "blobfile")
@@ -233,6 +234,7 @@ def deps_list(*pkgs):
         "sacrebleu",  # needed in trainer tests, see references to `run_translation.py`
         "filelock",  # filesystem locks, e.g., to prevent parallel downloads
     )
+    + extras["docs"]
     + extras["quality"]
     + extras["retrieval"]
     + extras["sentencepiece"]
diff --git a/src/transformers/dependency_versions_table.py b/src/transformers/dependency_versions_table.py
index d37c243c3a4f..e7a69e4c2d43 100644
--- a/src/transformers/dependency_versions_table.py
+++ b/src/transformers/dependency_versions_table.py
@@ -17,7 +17,7 @@
     "filelock": "filelock",
     "fugashi": "fugashi>=1.0",
     "GitPython": "GitPython<3.1.19",
-    "hf-doc-builder": "hf-doc-builder>=0.3.0",
+    "hf-doc-builder": "hf-doc-builder @ git+https://github.com/huggingface/doc-builder.git@main",
     "huggingface-hub": "huggingface-hub>=1.5.0,<2.0",
     "ipadic": "ipadic>=1.0.0,<2.0",
     "jinja2": "jinja2>=3.1.0",

PATCH

echo "Patch applied successfully."
