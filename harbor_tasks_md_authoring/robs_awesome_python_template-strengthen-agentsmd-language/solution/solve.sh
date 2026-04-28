#!/usr/bin/env bash
set -euo pipefail

cd /workspace/robs-awesome-python-template

# Idempotency guard
if grep -qF "Before beginning any task, make sure you review the documentation (`docs/dev/` a" "{{cookiecutter.__package_slug}}/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/{{cookiecutter.__package_slug}}/AGENTS.md b/{{cookiecutter.__package_slug}}/AGENTS.md
@@ -1,8 +1,8 @@
 # Agent Instructions
 
-You should always follow the best practices outlined in this document. If there is a valid reason why you cannot follow one of these practices, you should inform the user and document the reasons.
+You must always follow the best practices outlined in this document. If there is a valid reason why you cannot follow one of these practices, you must inform the user and document the reasons.
 
-Before beginning any task, make sure you review the documentation (`docs/dev/` and `README.md`), the existing tests to understand the project, and the task runner (Makefile) to understand what dev tools are available and how to use them. You should review code related to your request to understand preferred style: for example, you should review other tests before writing a new test suite, or review existing routers before creating a new one.
+Before beginning any task, make sure you review the documentation (`docs/dev/` and `README.md`), the existing tests to understand the project, and the task runner (Makefile) to understand what dev tools are available and how to use them. You must review code related to your request to understand preferred style: for example, you must review other tests before writing a new test suite, or review existing routers before creating a new one.
 
 ## Important Commands
 
@@ -111,29 +111,29 @@ docker compose exec service_name bash # Open a bash shell in a running service c
 * Prefer existing dependencies over adding new ones when possible.
 * For complex code, always consider using third-party libraries instead of writing new code that has to be maintained.
 * Use keyword arguments instead of positional arguments when calling functions and methods.
-* Do not put `import` statements inside functions unless necessary to prevent circular imports. Imports should be at the top of the file.
+* Do not put `import` statements inside functions unless necessary to prevent circular imports. Imports must be at the top of the file.
 
 ### Security
 
 * Always write secure code.
 * Never hardcode sensitive data.
 * Do not log sensitive data.
-* All user input should be validated.
+* All user input must be validated.
 * Never roll your own cryptography system.
 
 ### Production Ready
 
-* All generated code should be production ready.
-* There should be no stubs "for production".
-* There should not be any non-production logic branches in the main code package itself.
-* Any code or package differences between Development and Production should be avoided unless absolutely necessary.
+* All generated code must be production ready.
+* There must be no stubs "for production".
+* There must not be any non-production logic branches in the main code package itself.
+* Any code or package differences between Development and Production must be avoided unless absolutely necessary.
 
 ### Logging
 
 * Do not use `print` for logging or debugging: use the `getLogger` logger instead.
-* Each file should get its own logger using the `__name__` variable for a name.
+* Each file must get its own logger using the `__name__` variable for a name.
 * Use logging levels to allow developers to enable richer logging while testing than in production.
-* Most caught exceptions should be logged with `logger.exception`.
+* Most caught exceptions must be logged with `logger.exception`.
 
 ```python
 from logging import getLogger
@@ -153,10 +153,10 @@ def process_data(data: Dict[str, str]) -> None:
 
 ### Commenting
 
-* Comments should improve code readability and understandability.
-* Comments should not simply exist for the sake of existing.
+* Comments must improve code readability and understandability.
+* Comments must not simply exist for the sake of existing.
 * Examples of good comments include unclear function names/parameters, decisions about settings or function choices, logic descriptions, variable definitions, security risks, edge cases, and advice for developers refactoring or expanding code.
-* Comments should be concise, accurate, and add value to the codebase.
+* Comments must be concise, accurate, and add value to the codebase.
 
 ### Error Handling
 
@@ -183,7 +183,7 @@ except FileNotFoundError:
 
 ### Typing
 
-* Everything should be typed: function signatures (including return values), variables, and anything else.
+* Everything must be typed: function signatures (including return values), variables, and anything else.
 * Use the union operator for multiple allowed types.
 * Do not use `Optional`: use a union with `None` (i.e., `str | None`).
 * Use typing library metaclasses instead of native types for objects and lists (i.e., `Dict[str, str]` and `List[str]` instead of `dict` or `list`).
@@ -216,8 +216,8 @@ def process_users_bad(users: list[dict], config: dict) -> list:
 
 * Manage application settings with the `pydantic-settings` library.
 * The main Settings class is located in `PACKAGE_NAME/conf/settings.py` - update this existing class rather than creating new ones.
-* Sensitive configuration data should always use Pydantic `SecretStr` or `SecretBytes` types.
-* Settings that are allowed to be unset should default to `None` instead of empty strings.
+* Sensitive configuration data must always use Pydantic `SecretStr` or `SecretBytes` types.
+* Settings that are allowed to be unset must default to `None` instead of empty strings.
 * Define settings with the Pydantic `Field` function and include descriptions for users.
 
 ```python
@@ -256,10 +256,10 @@ class Settings(BaseSettings):
 
 ### FastAPI
 
-* APIs should adhere as closely as possible to REST principles, including appropriate use of GET/PUT/POST/DELETE HTTP verbs.
-* All routes should use Pydantic models for input and output.
-* Use different Pydantic models for inputs and outputs (i.e., creating a `Post` should require a `PostCreate` and return a `PostRead` model, not reuse the same model).
-* Parameters in Pydantic models for user input should use the Field function with validation and descriptions.
+* APIs must adhere as closely as possible to REST principles, including appropriate use of GET/PUT/POST/DELETE HTTP verbs.
+* All routes must use Pydantic models for input and output.
+* Use different Pydantic models for inputs and outputs (i.e., creating a `Post` must require a `PostCreate` and return a `PostRead` model, not reuse the same model).
+* Parameters in Pydantic models for user input must use the Field function with validation and descriptions.
 
 ```python
 from uuid import UUID
@@ -310,7 +310,7 @@ async def delete_post(post_id: UUID) -> None:
 * Always use async SQLAlchemy APIs with SQLAlchemy 2.0 syntax.
 * Represent database tables with the declarative class system.
 * Use Alembic to define migrations.
-* Migrations should be compatible with both SQLite and PostgreSQL.
+* Migrations must be compatible with both SQLite and PostgreSQL.
 * When creating queries, do not use implicit `and`: instead use the `and_` function (instead of `where(Model.parameter_a == A, Model.parameter_b == B)` do `where(and_(Model.parameter_a == A, Model.parameter_b == B))`).
 
 ```python
@@ -355,8 +355,8 @@ async def get_user_bad(session: AsyncSession, email: str, name: str) -> User | N
 
 ### Typer
 
-* Any CLI command or script that should be accessible to users should be exposed via the Typer library.
-* The main CLI entrypoint should be `PACKAGE_NAME/cli.py`.
+* Any CLI command or script that must be accessible to users must be exposed via the Typer library.
+* The main CLI entrypoint must be `PACKAGE_NAME/cli.py`.
 * For async commands, use the `@syncify` decorator provided in `cli.py` to convert async functions to sync for Typer compatibility.
 
 ```python
@@ -397,29 +397,29 @@ if __name__ == "__main__":
 ### Testing
 
 * Do not wrap test functions in classes unless there is a specific technical reason: instead prefer single functions.
-* All fixtures should be defined or imported in `conftest.py` so they are available to all tests.
+* All fixtures must be defined or imported in `conftest.py` so they are available to all tests.
 * Do not use mocks to replace simple dataclasses or Pydantic models unless absolutely necessary: instead create an instance of the appropriate class with desired parameters.
 * Use the FastAPI Test Client (preferably with a fixture) rather than calling FastAPI router classes directly.
 * Use a test database fixture with memory-backed SQLite for tests requiring a database. Including a dependency override for this test database as part of the FastAPI App fixture is extremely useful.
-* When adding new code, you should also add appropriate tests to cover that new code.
-* The test suite file structure should mirror the main code file structure.
+* When adding new code, you must also add appropriate tests to cover that new code.
+* The test suite file structure must mirror the main code file structure.
 
 ### Files
 
-* Filenames should always be lowercase for better compatibility with case-insensitive filesystems.
+* Filenames must always be lowercase for better compatibility with case-insensitive filesystems.
 * This includes documentation files, except standard files (like `README.md`, `LICENSE`, etc.).
-* Developer documentation should live in `docs/dev`.
-* New developer documents should be added to the table of contents in `docs/dev/README.md`.
-* Files only meant for building containers should live in the `docker/` folder.
-* Database models should live in `PACKAGE_NAME/models/`.
-* The primary settings file should live in `PACKAGE_NAME/conf/settings.py`.
+* Developer documentation must live in `docs/dev`.
+* New developer documents must be added to the table of contents in `docs/dev/README.md`.
+* Files only meant for building containers must live in the `docker/` folder.
+* Database models must live in `PACKAGE_NAME/models/`.
+* The primary settings file must live in `PACKAGE_NAME/conf/settings.py`.
 
 ### Developer Environments
 
-* Common developer tasks should be defined in the `makefile` to easy reuse.
-* Developers should always be able to start a fully functional developer instance with `docker compose up`.
-* Developer environments should be initialized with fake data for easy use.
-* Developer settings should live in the `.env` file, which should be in `.gitignore`.
-* A `.env.example` file should exist as a template for new developers to create their `.env` file and learn what variables to set.
-* Python projects should always use virtual environments at `.venv` in the project root. This should be activated before running tests.
+* Common developer tasks must be defined in the `makefile` to easy reuse.
+* Developers must always be able to start a fully functional developer instance with `docker compose up`.
+* Developer environments must be initialized with fake data for easy use.
+* Developer settings must live in the `.env` file, which must be in `.gitignore`.
+* A `.env.example` file must exist as a template for new developers to create their `.env` file and learn what variables to set.
+* Python projects must always use virtual environments at `.venv` in the project root. This must be activated before running tests.
 * Use `uv` for Python version management and package installation instead of pyenv and pip for significantly faster installations and automatic Python version handling.
PATCH

echo "Gold patch applied."
