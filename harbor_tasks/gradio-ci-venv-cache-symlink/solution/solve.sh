#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if setup-python step already has id field, skip
if grep -q 'id: setup-python' .github/actions/install-all-deps/action.yml; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/actions/install-all-deps/action.yml b/.github/actions/install-all-deps/action.yml
index 702142243b..0d58771814 100644
--- a/.github/actions/install-all-deps/action.yml
+++ b/.github/actions/install-all-deps/action.yml
@@ -41,6 +41,7 @@ runs:
       run: |
         echo "venv_activate=$VENV_ACTIVATE" >> $GITHUB_OUTPUT
     - name: Install Python
+      id: setup-python
       uses: actions/setup-python@v5
       with:
         python-version: ${{ inputs.python_version }}
@@ -61,10 +62,6 @@ runs:
       run: |
         powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.9.2/install.ps1 | iex"
         echo "$HOME/.cargo/bin" >> $GITHUB_PATH
-    - name: Create env
-      shell: bash
-      run: |
-        uv venv venv --python=${{ inputs.python_version }}
     - uses: actions/cache@v4
       id: cache
       with:
@@ -72,8 +69,12 @@ runs:
           venv/**
           client/python/venv
         restore-keys: |
-          gradio-lib-main-${{inputs.python_version}}-${{inputs.os}}-latest-pip-
-        key: "gradio-lib-main-${{inputs.python_version}}-${{inputs.os}}-latest-pip-${{ hashFiles('client/python/requirements.txt') }}-${{ hashFiles('requirements.txt') }}-${{ hashFiles('test/requirements.txt') }}-${{ hashFiles('client/python/test/requirements.txt') }}${{ inputs.test == 'true' && '-test' || ''}}"
+          gradio-lib-main-${{inputs.python_version}}-${{ steps.setup-python.outputs.python-version }}-${{inputs.os}}-latest-pip-
+        key: "gradio-lib-main-${{inputs.python_version}}-${{ steps.setup-python.outputs.python-version }}-${{inputs.os}}-latest-pip-${{ hashFiles('client/python/requirements.txt') }}-${{ hashFiles('requirements.txt') }}-${{ hashFiles('test/requirements.txt') }}-${{ hashFiles('client/python/test/requirements.txt') }}${{ inputs.test == 'true' && '-test' || ''}}"
+    - name: Create env
+      shell: bash
+      run: |
+        uv venv venv --python=${{ inputs.python_version }}
     - name: Install ffmpeg
       uses: FedericoCarboni/setup-ffmpeg@583042d32dd1cabb8bd09df03bde06080da5c87c # @v2
     - name: Install test dependencies
diff --git a/js/textbox/Textbox.test.ts b/js/textbox/Textbox.test.ts
index b7371e9ba3..d4d5340cb5 100644
--- a/js/textbox/Textbox.test.ts
+++ b/js/textbox/Textbox.test.ts
@@ -171,7 +171,7 @@ describe("Events", () => {
 		btn.focus();

 		await fireEvent.click(btn);
-		// await tick();
+		await tick();

 		expect(copy).toHaveBeenCalledTimes(1);
 		expect(copy).toHaveBeenCalledWith({ value: "copy me" });

PATCH

echo "Patch applied successfully."
