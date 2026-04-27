#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-cursorrules

# Idempotency guard
if grep -qF "- When writing tests, ONLY use pytest or pytest plugins (not unittest). All test" "rules/python-cursorrules-prompt-file-best-practices/.cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/rules/python-cursorrules-prompt-file-best-practices/.cursorrules b/rules/python-cursorrules-prompt-file-best-practices/.cursorrules
@@ -1,37 +1,25 @@
 You are an AI assistant specialized in Python development. Your approach emphasizes:
 
-Clear project structure with separate directories for source code, tests, docs, and config.
-
-Modular design with distinct files for models, services, controllers, and utilities.
-
-Configuration management using environment variables.
-
-Robust error handling and logging, including context capture.
-
-Comprehensive testing with pytest.
-
-Detailed documentation using docstrings and README files.
-
-Dependency management via https://github.com/astral-sh/uv and virtual environments.
-
-Code style consistency using Ruff.
-
-CI/CD implementation with GitHub Actions or GitLab CI.
+- Clear project structure with separate directories for source code, tests, docs, and config.
+- Modular design with distinct files for models, services, controllers, and utilities.
+- Configuration management using environment variables.
+- Robust error handling and logging, including context capture.
+- Comprehensive testing with pytest.
+- Detailed documentation using docstrings and README files.
+- Dependency management via https://github.com/astral-sh/uv and virtual environments.
+- Code style consistency using Ruff.
+- CI/CD implementation with GitHub Actions or GitLab CI.
 
 AI-friendly coding practices:
-
-You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.
+- You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.
 
 Follow the following rules:
-
-For any python file, be sure to ALWAYS add typing annotations to each function or class. Be sure to include return types when necessary. Add descriptive docstrings to all python functions and classes as well. Please use pep257 convention. Update existing docstrings if need be.
-
-Make sure you keep any comments that exist in a file.
-
-When writing tests, make sure that you ONLY use pytest or pytest plugins, do NOT use the unittest module. All tests should have typing annotations as well. All tests should be in ./tests. Be sure to create all necessary files and folders. If you are creating files inside of ./tests or ./src/goob_ai, be sure to make a init.py file if one does not exist.
+- For any Python file, ALWAYS add typing annotations to each function or class. Include explicit return types (including None where appropriate). Add descriptive docstrings to all Python functions and classes.
+- Please follow PEP 257 docstring conventions. Update existing docstrings as needed.
+- Make sure you keep any comments that exist in a file.
+- When writing tests, ONLY use pytest or pytest plugins (not unittest). All tests should have typing annotations. Place all tests under ./tests. Create any necessary directories. If you create packages under ./tests or ./src/<package_name>, be sure to add an __init__.py if one does not exist.
 
 All tests should be fully annotated and should contain docstrings. Be sure to import the following if TYPE_CHECKING:
-
 from _pytest.capture import CaptureFixture
 from _pytest.fixtures import FixtureRequest
 from _pytest.logging import LogCaptureFixture
PATCH

echo "Gold patch applied."
