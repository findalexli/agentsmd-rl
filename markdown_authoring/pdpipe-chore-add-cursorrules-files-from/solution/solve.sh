#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pdpipe

# Idempotency guard
if grep -qF "You are a both **Python expert** and a **Data Science expert**, with deep knowle" ".cursor/rules/always.mdc" && grep -qF "- In this machine, uv is installed on pyenv's Python 3.12.10, and pyenv is not i" ".cursor/rules/dev_test_and_build.mdc" && grep -qF "*   **src layout:** Consider using a `src` directory to separate application cod" ".cursor/rules/python.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/always.mdc b/.cursor/rules/always.mdc
@@ -0,0 +1,153 @@
+---
+description: This defines your general behavior when helping me code for the pdpipe package
+globs:
+alwaysApply: true
+---
+
+# Your Role
+You are a both **Python expert** and a **Data Science expert**, with deep knowledge of modern Python practices, machine learning tools and practices. Prioritize clean, maintainable code that follows Python idioms and best practices.
+
+## Do's
+- Prefer using MCP over CLIs for git when possible
+- Use linked files (via imports) generously to get the full context
+- Use **context7 MCP** when inserting new major depdencies in order to use their most recent version
+- The project uses **GitHub Issues** for issue tracking; review it when creating new PRs and create a relevant issue for linking
+- Use the terminal generously
+
+## Dont's
+- Never use non ascii characters
+- Never use the *em dash* character
+- When appear stuck - tell me and suggest to open a new chat with latest context
+- Don't use single-line docstrings for space-saving - they look ugly
+
+## Project-Specific Context
+- **Repository**: pdpipe/pdpipe
+- **Workflow**: Either:
+  1. Issue → Feature branch → GitHub PR
+  2. I ask for a feature branch → Issue → GitHub PR
+
+# More on the pdpipe package:
+
+
+- pdpipe is a Python package for building serializable, chainable, and verbose data processing pipelines for pandas DataFrames, with a focus on data science and machine learning workflows.
+- Always follow the fit-transform design pattern compatible with scikit-learn transformers when discussing pipeline stages or API design.
+- Code must adhere to flake8 and black formatting standards (see pyproject.toml for details). Linting is enforced in CI.
+- Use numpy docstring conventions for all public functions, classes, and methods. Include clear parameter and return type documentation and examples where possible.
+- Do not mutate input DataFrames in place; all transformations should return new DataFrames.
+- When adding new pipeline stages, use informative, explicit naming (e.g., ColDrop, ValDrop) to maximize pipeline readability.
+- Tests must be added for all new code. Place tests in the appropriate module subdirectory under tests/, and use one test function per use case. Aim to maintain 100% test coverage.
+- Doctests and code examples are encouraged in docstrings for new stages and functions.
+- Some features are optional and require scikit-learn or nltk; code should gracefully degrade if these are not installed, issuing a warning but not failing.
+- Pipelines and stages should be highly configurable and support serialization/deserialization for production use.
+- Default behaviors should help users avoid common data science pitfalls (e.g., one-hot encoding drops one column by default to avoid the dummy variable trap).
+- pdpipe supports Python 3.9 and up. Ensure compatibility with all supported versions.
+- For configuration, support both config files and environment variables as described in the README.
+- For help, reference the official documentation at https://pdpipe.readthedocs.io/en/latest/ and the Gitter community.
+
+
+## Overview
+
+`pdpipe` is a Python package for building robust, readable, and highly configurable pipelines for processing pandas DataFrames. It emphasizes:
+- **Preconditions and postconditions** for pipeline stages.
+- **Verbose, informative errors and prints**.
+- **Fit/transform API compatibility** with scikit-learn.
+- **Pipeline arithmetics** (addition, chaining, slicing).
+- **High serializability and productization-readiness**.
+- **Support for mixed-type data and supervised learning (X/y)**.
+
+## Key Design Patterns and Decisions
+
+### 1. **Pipeline and Stage Architecture**
+- **Base Classes:**
+  - `PdPipelineStage` (abstract): All stages inherit from this. Defines precondition (`_prec`), postcondition (`_post`), and transformation logic.
+  - `ColumnsBasedPipelineStage`: For stages operating on columns, handles `columns`, `exclude_columns`, and dynamic column selection.
+  - `PdPipeline`: A sequence of `PdPipelineStage` objects, itself a stage, supporting slicing, addition, and chaining.
+- **Stage Construction:**
+  - Stages are constructed with clear, explicit parameters (e.g., `columns`, `drop`, `errors`).
+  - Stages should be highly configurable, with sensible defaults.
+  - Stages support preconditions (`prec`), postconditions (`post`), and skip conditions (`skip`), all of which can be callables or condition objects from `pdpipe.cond`.
+
+### 2. **Usage Patterns**
+- **Pipeline Construction:**
+  - Pipelines can be built by passing a list of stages to `PdPipeline`, or using `make_pdpipeline(*stages)`.
+  - Stages and pipelines can be added together (`+`), or chained via method calls for one-liners.
+  - Slicing and indexing pipelines returns sub-pipelines or stages.
+- **Application:**
+  - Pipelines and stages are callable (`pipeline(df)`), or can use `.apply()`, `.fit()`, `.transform()`, `.fit_transform()`.
+  - Verbose and exception-raising behavior is controlled via `verbose` and `exraise` parameters, both at construction and per-call.
+  - Pipelines and stages support both X-only and X/y (supervised) transformations, maintaining index alignment.
+
+### 3. **Extensibility**
+- **Custom Stages:**
+  - New stages should inherit from `PdPipelineStage` or `ColumnsBasedPipelineStage`.
+  - Implement `_transform()` and `_prec()` for simple stateless stages.
+  - For fit-dependent stages, implement `_fit_transform()` and `_transform()`.
+  - For stages that affect both X and y, implement `_transform_Xy()` and/or `_fit_transform_Xy()`.
+  - Use `pdpipe.cond` for reusable, composable condition logic.
+- **Column Qualifiers:**
+  - Stages with a `columns` parameter accept single labels, lists, or callables (column qualifiers).
+  - Use `pdpipe.cq` for advanced column selection logic (by dtype, name, missingness, etc.), supporting fit-time determination.
+
+### 4. **Integration**
+- **scikit-learn:**
+  - `PdPipelineAndSklearnEstimator` allows chaining a `PdPipeline` with a scikit-learn estimator for use in `GridSearchCV`, etc.
+  - Use `.values` when passing DataFrames to scikit-learn estimators.
+  - Use `pdpipe_scorer_from_sklearn_scorer` to adapt sklearn scorers for use with `PdPipelineAndSklearnEstimator`.
+
+### 5. **Special Features**
+- **Fly Handles:**
+  - The `df` handle allows creation of stages from DataFrame methods and column assignments using operator overloading.
+  - `drop_rows_where` and `keep_rows_where` provide intuitive row filtering.
+- **Dynamic Parameters:**
+  - Use `pdp.dynamic` to set parameters at runtime based on input data.
+- **Stage Wrappers:**
+  - `FitOnly` applies a stage only during fitting, not during transform.
+
+### 6. **Testing and Documentation**
+- **Tests:**
+  - All new features and bug fixes must be accompanied by tests.
+  - Use `tests/requirements.txt` for test dependencies.
+- **Docs:**
+  - All public classes, methods, and parameters must be documented with clear docstrings and usage examples.
+  - Update Markdown docs in `docs/` for new features or changes.
+
+### 7. **Code Style and Quality**
+- **Formatting:** Use Black for code formatting.
+- **Linting:** Fix all Flake8 errors and warnings.
+- **Warnings:** Suppress known deprecation warnings as per project conventions.
+- **Readability:** Favor explicit, readable code and descriptive variable names.
+
+## Key Modules and Classes
+
+- `src/pdpipe/core.py`: Core pipeline and stage classes.
+- `src/pdpipe/basic_stages.py`: Basic built-in stages (e.g., `ColDrop`, `ValDrop`, `RowDrop`, `Schematize`).
+- `src/pdpipe/col_generation.py`: Column generation stages (e.g., `Bin`, `OneHotEncode`, `MapColVals`, `ApplyToRows`, `TransformByCols`).
+- `src/pdpipe/sklearn_stages.py`: Stages for sklearn integration (e.g., `Encode`, `Scale`, `Decompose`).
+- `src/pdpipe/skintegrate.py`: Integration with scikit-learn estimators.
+- `src/pdpipe/cond.py`, `src/pdpipe/cq.py`: Condition and column qualifier utilities.
+- `src/pdpipe/wrappers.py`: Stage wrappers (e.g., `FitOnly`).
+- `src/pdpipe/df/`: Fly handle and DataFrame method wrappers.
+
+## Contribution and Review Checklist
+
+**For Contributors:**
+- [ ] Follow the fit/transform API and ensure all new stages are serializable.
+- [ ] Use and document preconditions, postconditions, and skip conditions.
+- [ ] Prefer extending `ColumnsBasedPipelineStage` for column-based logic.
+- [ ] Support column qualifiers and dynamic parameters where appropriate.
+- [ ] Add tests and documentation for all new features.
+- [ ] Ensure code is Black-formatted and Flake8-clean.
+
+**For Reviewers:**
+- [ ] Check for adherence to API and design patterns.
+- [ ] Ensure new code is well-documented and tested.
+- [ ] Verify that new stages and pipelines are serializable and composable.
+- [ ] Confirm that all warnings and errors are handled as per conventions.
+- [ ] Review for code readability, maintainability, and extensibility.
+
+---
+
+**References:**
+- [pdpipe documentation](https://pdpipe.readthedocs.io/)
+- [pdpipe GitHub Discussions](https://github.com/pdpipe/pdpipe/discussions)
+- [Recent PRs and code style changes](https://github.com/pdpipe/pdpipe/pulls)
diff --git a/.cursor/rules/dev_test_and_build.mdc b/.cursor/rules/dev_test_and_build.mdc
@@ -0,0 +1,14 @@
+---
+description: When asked to build virtualenvs, run commands in them, run tests, setup or build the package, handle dependencies, integrate tools into the package or the CI, and anytime handling pyproject.tom
+globs:
+alwaysApply: false
+---
+
+# Build and dependency system in cachier
+
+- We use pyproject.toml with the modern PEP 621 format.
+- I prefer working with uv for virtualenv management, depdency isnallation, etc.
+- Tests should be run inside the uv venv, and using the dev/scripts/run_pytest.sh, so using the command `uv run sh dev/scripts/run_pytest.sh`.
+- In this machine, uv is installed on pyenv's Python 3.12.10, and pyenv is not initialized on every terminal session *on purpose*, so you'll have to run `pyenv init - bash`, then `pyenv shell 3.12.10` and only then the above command for running pytest inside the uv venv.
+- Before every commit, run the pre-commit hooks defined by pre-commit-config.yaml by running `uv run pre-commit run --all-files` in the project's root, and fix every raised error.
+- Black formatting errors raised by the above pre-commit command should be handled by running `uv run black src` and `uv run black tests`
diff --git a/.cursor/rules/python.mdc b/.cursor/rules/python.mdc
@@ -0,0 +1,348 @@
+---
+description: Comprehensive guidelines for Python development, covering code organization, performance, security, testing, and more.  These rules promote maintainable, efficient, and secure Python codebases.
+globs: *.py
+---
+# Python Best Practices and Coding Standards
+
+This document outlines comprehensive best practices and coding standards for Python development, aiming to promote clean, efficient, maintainable, and secure code.
+
+## 1. Code Organization and Structure
+
+### 1.1. Directory Structure Best Practices
+
+*   **Flat is better than nested (but not always).**  Start with a simple structure and refactor as needed.
+*   **Packages vs. Modules:** Use packages (directories with `__init__.py`) for logical grouping of modules.
+*   **src layout:** Consider using a `src` directory to separate application code from project-level files (setup.py, requirements.txt, etc.). This helps avoid import conflicts and clarifies the project's boundaries.
+*   **Typical Project Structure:**
+
+
+    project_name/
+    ├── src/
+    │   ├── package_name/
+    │   │   ├── __init__.py
+    │   │   ├── module1.py
+    │   │   ├── module2.py
+    │   ├── main.py  # Entry point
+    ├── tests/
+    │   ├── requirements.txt
+    │   ├── __init__.py
+    │   ├── test_module1.py
+    │   ├── test_module2.py
+    ├── docs/
+    │   ├── conf.py
+    │   ├── index.rst
+    ├── .gitignore
+    ├── pyproject.toml or setup.py
+    ├── README.md
+    ├── requirements.txt or requirements-dev.txt
+
+
+### 1.2. File Naming Conventions
+
+*   **Modules:**  Lowercase, with underscores for readability (e.g., `my_module.py`).
+*   **Packages:** Lowercase (e.g., `my_package`). Avoid underscores unless necessary.
+*   **Tests:** Start with `test_` (e.g., `test_my_module.py`).
+
+### 1.3. Module Organization Best Practices
+
+*   **Single Responsibility Principle:** Each module should have a well-defined purpose.
+*   **Imports:**
+    *   Order: standard library, third-party, local.
+    *   Absolute imports are generally preferred (e.g., `from my_package.module1 import function1`).
+    *   Use explicit relative imports (`from . import sibling_module`) when dealing with complex package layouts where absolute imports are overly verbose or impractical.
+*   **Constants:**  Define module-level constants in uppercase (e.g., `MAX_ITERATIONS = 100`).
+*   **Dunder names:** `__all__`, `__version__`, etc. should be after the module docstring but before any imports (except `from __future__`).  Use `__all__` to explicitly define the public API.
+
+### 1.4. Component Architecture Recommendations
+
+*   **Layered Architecture:** Suitable for larger applications, separating concerns into presentation, business logic, and data access layers.
+*   **Microservices:**  For very large applications, consider breaking the system into smaller, independent services.
+*   **Hexagonal/Clean Architecture:** Emphasizes decoupling business logic from external dependencies like databases and frameworks.
+*   **Dependency Injection:** Use dependency injection to improve testability and reduce coupling.
+
+### 1.5. Code Splitting Strategies
+
+*   **By Functionality:**  Split code into modules based on distinct functionalities (e.g., user management, data processing).
+*   **By Layer:** Separate presentation, business logic, and data access code.
+*   **Lazy Loading:** Use `importlib.import_module()` to load modules on demand, improving startup time.
+*   **Conditional Imports:** Import modules only when needed, based on certain conditions.
+
+## 2. Common Patterns and Anti-patterns
+
+### 2.1. Design Patterns
+
+*   **Singleton:**  Restrict instantiation of a class to one object.
+*   **Factory:**  Create objects without specifying the exact class to be created.
+*   **Observer:**  Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified.
+*   **Strategy:**  Define a family of algorithms, encapsulate each one, and make them interchangeable.
+*   **Decorator:**  Add responsibilities to objects dynamically.
+*   **Context Manager:** Guarantees resources are properly cleaned up (e.g., files are closed).
+
+### 2.2. Recommended Approaches for Common Tasks
+
+*   **Data Validation:** Use libraries like `pydantic` or `marshmallow` for data validation and serialization.
+*   **Configuration Management:** Use libraries like `python-decouple`, `dynaconf` or standard library's `configparser` to manage environment-specific settings.
+*   **Logging:** Use the `logging` module for structured logging. Configure log levels and handlers appropriately.
+*   **Command-Line Interfaces:** Use `argparse`, `click` or `typer` for creating command-line interfaces.
+*   **Asynchronous Programming:** Use `asyncio` for I/O-bound and concurrency problems.
+
+### 2.3. Anti-patterns and Code Smells
+
+*   **God Class:** A class that does too much.  Break it down into smaller, more focused classes.
+*   **Shotgun Surgery:**  Making small changes to many different classes at once. Indicates poor cohesion.
+*   **Spaghetti Code:**  Unstructured and difficult-to-follow code.  Refactor using well-defined functions and classes.
+*   **Duplicate Code:**  Extract common code into reusable functions or classes (DRY - Don't Repeat Yourself).
+*   **Magic Numbers/Strings:**  Use named constants instead of hardcoded values.
+*   **Nested Callbacks:**  Avoid excessive nesting of callbacks. Use `async/await` or promises for better readability.
+*   **Premature Optimization:** Don't optimize code before identifying bottlenecks.
+
+### 2.4. State Management Best Practices
+
+*   **Stateless Functions:** Prefer stateless functions where possible.
+*   **Immutable Data:** Use immutable data structures to prevent accidental modification.
+*   **Explicit State:**  Manage state explicitly using classes or data structures.  Avoid relying on global variables.
+*   **Context Variables:** Use `contextvars` (Python 3.7+) for managing request-scoped state in asynchronous applications.
+*   **Redux-like patterns:** Consider redux-like patterns for managing client-side and complex application state.
+
+### 2.5. Error Handling Patterns
+
+*   **Specific Exceptions:** Catch specific exceptions rather than broad `Exception` or `BaseException`.
+*   **`try...except...finally`:** Use `finally` to ensure cleanup code is always executed.
+*   **Context Managers:**  Use context managers (`with open(...) as f:`) for resource management.
+*   **Logging Errors:** Log exceptions with complete traceback information.
+*   **Raising Exceptions:** Raise exceptions with informative error messages.
+*   **Custom Exceptions:** Create custom exception classes for specific error conditions.
+*   **Avoid using exceptions for control flow.** Exceptions should represent exceptional circumstances.
+
+## 3. Performance Considerations
+
+### 3.1. Optimization Techniques
+
+*   **Profiling:**  Use `cProfile` to identify performance bottlenecks.
+*   **Efficient Data Structures:**  Choose the right data structure for the task (e.g., `set` for membership testing, `dict` for lookups).
+*   **List Comprehensions and Generators:**  Use list comprehensions and generator expressions for concise and efficient code.
+*   **Vectorization with NumPy:**  Use NumPy for numerical computations, leveraging vectorized operations.
+*   **Just-In-Time Compilation (JIT):**  Consider using JIT compilers like Numba for performance-critical code.
+*   **Caching:** Implement caching mechanisms using `functools.lru_cache` or external caching libraries like Redis or Memcached.
+*   **String Concatenation:** Use `''.join(iterable)` for efficient string concatenation.
+*   **Avoid Global Variables:** Accessing local variables is faster than accessing global variables.
+*   **Cython:** Use Cython to write C extensions for Python, improving performance.
+
+### 3.2. Memory Management Considerations
+
+*   **Garbage Collection:**  Understand Python's garbage collection mechanism.
+*   **Object References:**  Be mindful of object references and circular dependencies, which can prevent garbage collection.
+*   **Memory Profiling:** Use `memory_profiler` to identify memory leaks.
+*   **Slots:** Use `__slots__` in classes to reduce memory footprint (disables `__dict__`).
+*   **Generators:** Use generators for processing large datasets without loading them into memory.
+*   **Data type sizing:** Use the most efficient data types possible to reduce memory use.
+
+### 3.3. Rendering Optimization
+
+*   N/A for core Python libraries. Relevant for GUI frameworks (e.g., Tkinter, PyQt, Kivy).
+*   For web development with frameworks such as Django, Flask, or Pyramid, use efficient templating, caching and database query optimizations.
+
+### 3.4. Bundle Size Optimization
+
+*   N/A for core Python libraries. Relevant for web applications or when creating executable bundles.
+*   Use tools like `PyInstaller` or `cx_Freeze` to create executable bundles.
+*   Minimize dependencies to reduce bundle size.
+*   Use code minification techniques.
+
+### 3.5. Lazy Loading Strategies
+
+*   **Module Loading:**  Use `importlib.import_module()` to load modules on demand.
+*   **Data Loading:** Load large datasets only when needed.
+*   **Deferred Execution:**  Use generators or coroutines to defer execution of code.
+
+## 4. Security Best Practices
+
+### 4.1. Common Vulnerabilities and Prevention
+
+*   **SQL Injection:**  Use parameterized queries or ORMs to prevent SQL injection attacks.
+*   **Cross-Site Scripting (XSS):** Sanitize user input and escape output to prevent XSS attacks.
+*   **Cross-Site Request Forgery (CSRF):**  Use CSRF tokens to protect against CSRF attacks.
+*   **Command Injection:**  Avoid executing arbitrary commands based on user input. If necessary, sanitize input carefully.
+*   **Path Traversal:**  Validate file paths to prevent path traversal attacks.
+*   **Denial of Service (DoS):** Implement rate limiting and input validation to protect against DoS attacks.
+*   **Pickle Deserialization:**  Avoid using `pickle` to deserialize untrusted data, as it can lead to arbitrary code execution. Use safer alternatives like JSON or Protocol Buffers.
+*   **Dependency Vulnerabilities:** Regularly audit and update dependencies to address security vulnerabilities.
+*   **Hardcoded Secrets:** Never hardcode secrets (passwords, API keys) in code. Use environment variables or secure configuration files.
+
+### 4.2. Input Validation Best Practices
+
+*   **Whitelisting:**  Validate input against a whitelist of allowed values.
+*   **Regular Expressions:** Use regular expressions to validate input formats.
+*   **Data Type Validation:**  Ensure input data types are correct.
+*   **Length Validation:**  Limit the length of input strings.
+*   **Sanitization:**  Remove or escape potentially harmful characters from input.
+*   **Use libraries:** Use libraries like `cerberus` and `schematics` to assist with validating the input.
+
+### 4.3. Authentication and Authorization Patterns
+
+*   **Authentication:**
+    *   Use strong password hashing algorithms (e.g., bcrypt, Argon2).
+    *   Implement multi-factor authentication (MFA).
+    *   Use secure session management techniques.
+    *   Consider using a dedicated authentication service (e.g., Auth0, Okta).
+*   **Authorization:**
+    *   Implement role-based access control (RBAC) or attribute-based access control (ABAC).
+    *   Use a permissions system to control access to resources.
+    *   Enforce the principle of least privilege.
+    *   Use access tokens (JWTs).
+
+### 4.4. Data Protection Strategies
+
+*   **Encryption:** Encrypt sensitive data at rest and in transit.
+*   **Data Masking:** Mask sensitive data when displaying it to users.
+*   **Tokenization:** Replace sensitive data with non-sensitive tokens.
+*   **Data Loss Prevention (DLP):** Implement DLP measures to prevent sensitive data from leaving the organization.
+*   **Regular backups and disaster recovery plans.**
+
+### 4.5. Secure API Communication
+
+*   **HTTPS:**  Always use HTTPS for API communication.
+*   **API Keys:**  Use API keys for authentication.
+*   **OAuth 2.0:**  Use OAuth 2.0 for delegated authorization.
+*   **Input validation**: Validate all API requests before processing.
+*   **Rate Limiting:** Implement rate limiting to prevent abuse.
+*   **Web Application Firewall (WAF)** Implement WAF to provide centralized security layer.
+
+## 5. Testing Approaches
+
+### 5.1. Unit Testing Strategies
+
+*   **Test Individual Units:** Test individual functions, classes, or modules in isolation.
+*   **Test-Driven Development (TDD):** Write tests before writing code.
+*   **Coverage:**  Aim for high test coverage.
+*   **Assertion Styles:** Use appropriate assertion methods (e.g., `assertEqual`, `assertTrue`, `assertRaises`).
+*   **Boundary conditions:** Test boundary conditions and edge cases.
+*   **Error conditions:** Test that exceptions are raised when appropriate.
+
+### 5.2. Integration Testing Approaches
+
+*   **Test Interactions:** Test the interactions between different modules or components.
+*   **Database Testing:** Test database interactions.
+*   **API Testing:** Test API endpoints.
+*   **Mock External Services:** Use mocks to simulate external services during integration tests.
+*   **Focus on key workflows.** Integration tests should exercise the most important user workflows.
+
+### 5.3. End-to-End Testing Recommendations
+
+*   **Test Entire System:** Test the entire system from end to end.
+*   **User Perspective:** Write tests from the perspective of the user.
+*   **Browser Automation:** Use browser automation tools like Selenium or Playwright.
+*   **Real-World Scenarios:** Simulate real-world scenarios in end-to-end tests.
+*   **Focus on critical paths.** End-to-end tests are expensive to write and maintain, so focus on the most critical paths.
+
+### 5.4. Test Organization Best Practices
+
+*   **Separate Test Directory:**  Keep tests in a separate `tests` directory.
+*   **Mirror Source Structure:**  Mirror the source code structure in the test directory.
+*   **Test Modules:** Create test modules for each source module.
+*   **Test Classes:**  Use test classes to group related tests.
+*   **Use a test runner:** Use `pytest` or `unittest` test runners.
+*   **Use fixtures:** Utilize fixtures to setup and tear down resources for tests.
+
+### 5.5. Mocking and Stubbing Techniques
+
+*   **`unittest.mock`:** Use the `unittest.mock` module for mocking and stubbing.
+*   **Patching:**  Use `patch` to replace objects with mocks during tests.
+*   **Side Effects:**  Define side effects for mocks to simulate different scenarios.
+*   **Mocking External Dependencies:** Mock external dependencies like databases, APIs, and file systems.
+*   **Use dependency injection for testability.** Dependency injection makes it easier to mock dependencies.
+
+## 6. Common Pitfalls and Gotchas
+
+### 6.1. Frequent Mistakes
+
+*   **Mutable Default Arguments:**  Avoid using mutable default arguments in function definitions.
+*   **Scope of Variables:**  Be aware of variable scope in nested functions.
+*   **`==` vs. `is`:**  Use `==` for value comparison and `is` for object identity comparison.
+*   **`try...except` Blocks:** Placing too much code inside try blocks. Keep try blocks as small as possible.
+*   **Ignoring Exceptions:** Swallowing exceptions without handling or logging them.
+*   **Incorrect indentation.**  Indentation errors are a common source of bugs.
+*   **Not using virtual environments.** Not using virtual environments can lead to dependency conflicts.
+
+### 6.2. Edge Cases
+
+*   **Floating-Point Arithmetic:** Be aware of the limitations of floating-point arithmetic.
+*   **Unicode Handling:** Handle Unicode strings carefully.
+*   **File Encoding:**  Specify file encoding when reading and writing files.
+*   **Time Zones:**  Handle time zones correctly.
+*   **Resource limits:** Be aware of and handle system resource limits (e.g., file handles, memory).
+
+### 6.3. Version-Specific Issues
+
+*   **Python 2 vs. Python 3:** Be aware of the differences between Python 2 and Python 3.
+*   **Syntax Changes:**  Be aware of syntax changes in different Python versions.
+*   **Library Compatibility:**  Ensure that libraries are compatible with the Python version being used.
+*   **Deprecated features.** Avoid using deprecated features.
+
+### 6.4. Compatibility Concerns
+
+*   **Operating Systems:** Test code on different operating systems (Windows, macOS, Linux).
+*   **Python Implementations:**  Consider compatibility with different Python implementations (CPython, PyPy, Jython).
+*   **Database Versions:** Ensure compatibility with different database versions.
+*   **External Libraries:**  Be aware of compatibility issues with external libraries.
+
+### 6.5. Debugging Strategies
+
+*   **`pdb`:**  Use the `pdb` debugger for interactive debugging.
+*   **Logging:**  Use logging to track program execution.
+*   **Print Statements:** Use print statements for simple debugging.
+*   **Assertions:**  Use assertions to check for expected conditions.
+*   **Profiling:** Use profilers to identify performance bottlenecks.
+*   **Code Analysis Tools:** Use code analysis tools like pylint or flake8 to detect potential problems.
+*   **Remote debugging:** Use remote debugging tools when debugging code running on remote servers.
+
+## 7. Tooling and Environment
+
+### 7.1. Recommended Development Tools
+
+*   **IDEs:** PyCharm, VS Code (with Python extension), Sublime Text.
+*   **Virtual Environment Managers:** `venv` (built-in), `virtualenv`, `conda`, `pipenv`.
+*   **Package Managers:** `pip` (default), `conda`, `poetry`.
+*   **Debuggers:** `pdb`, IDE debuggers.
+*   **Profilers:** `cProfile`, `memory_profiler`.
+*   **Linters:** `pylint`, `flake8`.
+*   **Formatters:** `black`, `autopep8`, `YAPF`.
+*   **Static Analyzers:** `mypy`, `pytype`.
+*    **Notebook environments**: Jupyter Notebook, Jupyter Lab, Google Colab.
+
+### 7.2. Build Configuration Best Practices
+
+*   **`pyproject.toml`:**  Use `pyproject.toml` for build configuration (PEP 518, PEP 621).
+*   **`setup.py`:**  Use `setup.py` for legacy projects (but prefer `pyproject.toml` for new projects).
+*   **Dependency Management:**  Specify dependencies in `requirements.txt` or `pyproject.toml`.
+*   **Virtual Environments:**  Use virtual environments to isolate project dependencies.
+*   **Reproducible builds:** Ensure reproducible builds by pinning dependencies.
+
+### 7.3. Linting and Formatting Recommendations
+
+*   **PEP 8:** Adhere to PEP 8 style guidelines.
+*   **Linters:** Use linters to enforce code style and detect potential problems.
+*   **Formatters:** Use formatters to automatically format code according to PEP 8.
+*   **Pre-commit Hooks:** Use pre-commit hooks to run linters and formatters before committing code.
+*   **Consistent Style:** Maintain a consistent code style throughout the project.
+
+### 7.4. Deployment Best Practices
+
+*   **Virtual Environments:** Deploy applications in virtual environments.
+*   **Dependency Management:**  Install dependencies using `pip install -r requirements.txt` or `poetry install`.
+*   **Process Managers:** Use process managers like `systemd`, `Supervisor`, or `Docker` to manage application processes.
+*   **Web Servers:**  Use web servers like Gunicorn or uWSGI to serve web applications.
+*   **Load Balancing:** Use load balancers to distribute traffic across multiple servers.
+*   **Containerization:** Use containerization technologies like Docker to package and deploy applications.
+*   **Infrastructure as Code (IaC)** Manage infrastructure using IaC tools like Terraform or CloudFormation.
+
+### 7.5. CI/CD Integration Strategies
+
+*   **Continuous Integration (CI):** Automatically build and test code on every commit.
+*   **Continuous Delivery (CD):** Automatically deploy code to staging or production environments.
+*   **CI/CD Tools:** Use CI/CD tools like Jenkins, GitLab CI, GitHub Actions, CircleCI, or Travis CI.
+*   **Automated Testing:**  Include automated tests in the CI/CD pipeline.
+*   **Code Analysis:** Integrate code analysis tools into the CI/CD pipeline.
+*   **Automated deployments.** Automate the deployment process to reduce manual effort and errors.
+
+By adhering to these best practices and coding standards, developers can create Python code that is more robust, maintainable, and secure.
PATCH

echo "Gold patch applied."
