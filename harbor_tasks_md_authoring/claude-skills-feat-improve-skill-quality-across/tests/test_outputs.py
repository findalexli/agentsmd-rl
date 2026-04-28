"""Behavioral checks for claude-skills-feat-improve-skill-quality-across (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/angular-architect/SKILL.md')
    assert 'description: Generates Angular 17+ standalone components, configures advanced routing with lazy loading and guards, implements NgRx state management, applies RxJS patterns, and optimizes bundle perfor' in text, "expected to find: " + 'description: Generates Angular 17+ standalone components, configures advanced routing with lazy loading and guards, implements NgRx state management, applies RxJS patterns, and optimizes bundle perfor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/angular-architect/SKILL.md')
    assert '5. **Optimize** - Apply performance best practices and bundle optimization; run `ng build --configuration production` to verify bundle size and flag regressions' in text, "expected to find: " + '5. **Optimize** - Apply performance best practices and bundle optimization; run `ng build --configuration production` to verify bundle size and flag regressions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/angular-architect/SKILL.md')
    assert '4. **Manage state** - Setup NgRx store, effects, selectors as needed; verify store hydration and action flow with Redux DevTools before proceeding' in text, "expected to find: " + '4. **Manage state** - Setup NgRx store, effects, selectors as needed; verify store hydration and action flow with Redux DevTools before proceeding'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/api-designer/SKILL.md')
    assert '2. **Model resources** — Identify resources, relationships, and operations; sketch entity diagram before writing any spec' in text, "expected to find: " + '2. **Model resources** — Identify resources, relationships, and operations; sketch entity diagram before writing any spec'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/api-designer/SKILL.md')
    assert '4. **Specify contract** — Create OpenAPI 3.1 spec; validate before proceeding: `npx @redocly/cli lint openapi.yaml`' in text, "expected to find: " + '4. **Specify contract** — Create OpenAPI 3.1 spec; validate before proceeding: `npx @redocly/cli lint openapi.yaml`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/api-designer/SKILL.md')
    assert '5. **Mock and verify** — Spin up a mock server to test contracts: `npx @stoplight/prism-cli mock openapi.yaml`' in text, "expected to find: " + '5. **Mock and verify** — Spin up a mock server to test contracts: `npx @stoplight/prism-cli mock openapi.yaml`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-designer/SKILL.md')
    assert 'description: Use when designing new high-level system architecture, reviewing existing designs, or making architectural decisions. Invoke to create architecture diagrams, write Architecture Decision R' in text, "expected to find: " + 'description: Use when designing new high-level system architecture, reviewing existing designs, or making architectural decisions. Invoke to create architecture diagrams, write Architecture Decision R'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-designer/SKILL.md')
    assert 'You are a principal architect with 15+ years of experience designing scalable, distributed systems. You make pragmatic trade-offs, document decisions with ADRs, and prioritize long-term maintainabilit' in text, "expected to find: " + 'You are a principal architect with 15+ years of experience designing scalable, distributed systems. You make pragmatic trade-offs, document decisions with ADRs, and prioritize long-term maintainabilit'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-designer/SKILL.md')
    assert '1. **Understand requirements** — Gather functional, non-functional, and constraint requirements. _Verify full requirements coverage before proceeding._' in text, "expected to find: " + '1. **Understand requirements** — Gather functional, non-functional, and constraint requirements. _Verify full requirements coverage before proceeding._'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/atlassian-mcp/SKILL.md')
    assert 'description: Integrates with Atlassian products to manage project tracking and documentation via MCP protocol. Use when querying Jira issues with JQL filters, creating and updating tickets with custom' in text, "expected to find: " + 'description: Integrates with Atlassian products to manage project tracking and documentation via MCP protocol. Use when querying Jira issues with JQL filters, creating and updating tickets with custom'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/atlassian-mcp/SKILL.md')
    assert '> **Note:** Always load `JIRA_API_TOKEN` and `CONFLUENCE_API_TOKEN` from environment variables or a secrets manager — never hardcode credentials.' in text, "expected to find: " + '> **Note:** Always load `JIRA_API_TOKEN` and `CONFLUENCE_API_TOKEN` from environment variables or a secrets manager — never hardcode credentials.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/atlassian-mcp/SKILL.md')
    assert '3. **Design queries** - Write JQL for Jira, CQL for Confluence; validate with `maxResults=1` before full execution' in text, "expected to find: " + '3. **Design queries** - Write JQL for Jira, CQL for Confluence; validate with `maxResults=1` before full execution'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chaos-engineer/SKILL.md')
    assert 'description: Designs chaos experiments, creates failure injection frameworks, and facilitates game day exercises for distributed systems — producing runbooks, experiment manifests, rollback procedures' in text, "expected to find: " + 'description: Designs chaos experiments, creates failure injection frameworks, and facilitates game day exercises for distributed systems — producing runbooks, experiment manifests, rollback procedures'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chaos-engineer/SKILL.md')
    assert '- **No production without safety nets** — customer-facing environments require circuit breakers, feature flags, or canary isolation' in text, "expected to find: " + '- **No production without safety nets** — customer-facing environments require circuit breakers, feature flags, or canary isolation'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chaos-engineer/SKILL.md')
    assert '- **Close the loop** — every experiment must produce a written learning summary and at least one tracked improvement' in text, "expected to find: " + '- **Close the loop** — every experiment must produce a written learning summary and at least one tracked improvement'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-developer/SKILL.md')
    assert 'description: Use when building CLI tools, implementing argument parsing, or adding interactive prompts. Invoke for parsing flags and subcommands, displaying progress bars and spinners, generating bash' in text, "expected to find: " + 'description: Use when building CLI tools, implementing argument parsing, or adding interactive prompts. Invoke for parsing flags and subcommands, displaying progress bars and spinners, generating bash'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-developer/SKILL.md')
    assert '3. **Implement** — Build with the appropriate CLI framework for the language (see Reference Guide below). After wiring up commands, run `<cli> --help` to verify help text renders correctly and `<cli> ' in text, "expected to find: " + '3. **Implement** — Build with the appropriate CLI framework for the language (see Reference Guide below). After wiring up commands, run `<cli> --help` to verify help text renders correctly and `<cli> '[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-developer/SKILL.md')
    assert '1. **Analyze UX** — Identify user workflows, command hierarchy, common tasks. Validate by listing all commands and their expected `--help` output before writing code.' in text, "expected to find: " + '1. **Analyze UX** — Identify user workflows, command hierarchy, common tasks. Validate by listing all commands and their expected `--help` output before writing code.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cloud-architect/SKILL.md')
    assert 'description: Designs cloud architectures, creates migration plans, generates cost optimization recommendations, and produces disaster recovery strategies across AWS, Azure, and GCP. Use when designing' in text, "expected to find: " + 'description: Designs cloud architectures, creates migration plans, generates cost optimization recommendations, and produces disaster recovery strategies across AWS, Azure, and GCP. Use when designing'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cloud-architect/SKILL.md')
    assert '**After Design:** Confirm every component has a redundancy strategy and no single points of failure exist in the topology.' in text, "expected to find: " + '**After Design:** Confirm every component has a redundancy strategy and no single points of failure exist in the topology.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cloud-architect/SKILL.md')
    assert '5. **Migration** — Apply 6Rs framework, define waves, validate connectivity before cutover' in text, "expected to find: " + '5. **Migration** — Apply 6Rs framework, define waves, validate connectivity before cutover'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-documenter/SKILL.md')
    assert 'description: Generates, formats, and validates technical documentation — including docstrings, OpenAPI/Swagger specs, JSDoc annotations, doc portals, and user guides. Use when adding docstrings to fun' in text, "expected to find: " + 'description: Generates, formats, and validates technical documentation — including docstrings, OpenAPI/Swagger specs, JSDoc annotations, doc portals, and user guides. Use when adding docstrings to fun'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-documenter/SKILL.md')
    assert 'Applies to any task involving code documentation, API specs, or developer-facing guides. See the reference table below for specific sub-topics.' in text, "expected to find: " + 'Applies to any task involving code documentation, API specs, or developer-facing guides. See the reference table below for specific sub-topics.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-documenter/SKILL.md')
    assert '- Python: `python -m doctest file.py` for doctest blocks; `pytest --doctest-modules` for module-wide checks' in text, "expected to find: " + '- Python: `python -m doctest file.py` for doctest blocks; `pytest --doctest-modules` for module-wide checks'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-reviewer/SKILL.md')
    assert 'description: Analyzes code diffs and files to identify bugs, security vulnerabilities (SQL injection, XSS, insecure deserialization), code smells, N+1 queries, naming issues, and architectural concern' in text, "expected to find: " + 'description: Analyzes code diffs and files to identify bugs, security vulnerabilities (SQL injection, XSS, insecure deserialization), code smells, N+1 queries, naming issues, and architectural concern'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-reviewer/SKILL.md')
    assert '> **Disagreement handling:** If the author has left comments explaining a non-obvious choice, acknowledge their reasoning before suggesting an alternative. Never block on style preferences when a lint' in text, "expected to find: " + '> **Disagreement handling:** If the author has left comments explaining a non-obvious choice, acknowledge their reasoning before suggesting an alternative. Never block on style preferences when a lint'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-reviewer/SKILL.md')
    assert "1. **Context** — Read PR description, understand the problem being solved. **Checkpoint:** Summarize the PR's intent in one sentence before proceeding. If you cannot, ask the author to clarify." in text, "expected to find: " + "1. **Context** — Read PR description, understand the problem being solved. **Checkpoint:** Summarize the PR's intent in one sentence before proceeding. If you cannot, ask the author to clarify."[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cpp-pro/SKILL.md')
    assert 'description: Writes, optimizes, and debugs C++ applications using modern C++20/23 features, template metaprogramming, and high-performance systems techniques. Use when building or refactoring C++ code' in text, "expected to find: " + 'description: Writes, optimizes, and debugs C++ applications using modern C++20/23 features, template metaprogramming, and high-performance systems techniques. Use when building or refactoring C++ code'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cpp-pro/SKILL.md')
    assert '4. **Verify quality** — Run sanitizers and static analysis; if AddressSanitizer or UndefinedBehaviorSanitizer report issues, fix all memory and UB errors before proceeding' in text, "expected to find: " + '4. **Verify quality** — Run sanitizers and static analysis; if AddressSanitizer or UndefinedBehaviorSanitizer report issues, fix all memory and UB errors before proceeding'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cpp-pro/SKILL.md')
    assert '5. **Benchmark** — Profile with real workloads; if performance targets are not met, apply targeted optimizations (SIMD, cache layout, move semantics) and re-measure' in text, "expected to find: " + '5. **Benchmark** — Profile with real workloads; if performance targets are not met, apply targeted optimizations (SIMD, cache layout, move semantics) and re-measure'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-developer/SKILL.md')
    assert 'description: "Use when building C# applications with .NET 8+, ASP.NET Core APIs, or Blazor web apps. Builds REST APIs using minimal or controller-based routing, configures database access with Entity ' in text, "expected to find: " + 'description: "Use when building C# applications with .NET 8+, ASP.NET Core APIs, or Blazor web apps. Builds REST APIs using minimal or controller-based routing, configures database access with Entity '[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-developer/SKILL.md')
    assert '> **EF Core checkpoint (after step 3):** Run `dotnet ef migrations add <Name>` and review the generated migration file before applying. Confirm no unintended table/column drops. Roll back with `dotnet' in text, "expected to find: " + '> **EF Core checkpoint (after step 3):** Run `dotnet ef migrations add <Name>` and review the generated migration file before applying. Confirm no unintended table/column drops. Roll back with `dotnet'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-developer/SKILL.md')
    assert '- Apply async/await for all I/O operations — always accept and forward `CancellationToken`:' in text, "expected to find: " + '- Apply async/await for all I/O operations — always accept and forward `CancellationToken`:'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-optimizer/SKILL.md')
    assert 'description: Optimizes database queries and improves performance across PostgreSQL and MySQL systems. Use when investigating slow queries, analyzing execution plans, or optimizing database performance' in text, "expected to find: " + 'description: Optimizes database queries and improves performance across PostgreSQL and MySQL systems. Use when investigating slow queries, analyzing execution plans, or optimizing database performance'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-optimizer/SKILL.md')
    assert '4. **Implement Changes** — Apply optimizations incrementally with monitoring; validate each change before proceeding to the next' in text, "expected to find: " + '4. **Implement Changes** — Apply optimizations incrementally with monitoring; validate each change before proceeding to the next'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-optimizer/SKILL.md')
    assert '> ⚠️ Always test changes in non-production first. Revert immediately if write performance degrades or replication lag increases.' in text, "expected to find: " + '> ⚠️ Always test changes in non-production first. Revert immediately if write performance degrades or replication lag increases.'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-wizard/SKILL.md')
    assert 'description: Parses error messages, traces execution flow through stack traces, correlates log entries to identify failure points, and applies systematic hypothesis-driven methodology to isolate and r' in text, "expected to find: " + 'description: Parses error messages, traces execution flow through stack traces, correlates log entries to identify failure points, and applies systematic hypothesis-driven methodology to isolate and r'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-wizard/SKILL.md')
    assert 'node --inspect-brk script.js     # pause at first line, attach Chrome DevTools' in text, "expected to find: " + 'node --inspect-brk script.js     # pause at first line, attach Chrome DevTools'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-wizard/SKILL.md')
    assert '# Sources panel: add breakpoints, watch expressions, step through' in text, "expected to find: " + '# Sources panel: add breakpoints, watch expressions, step through'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/devops-engineer/SKILL.md')
    assert 'description: Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes manifests, and generates Terraform/Pulumi infrastructure templates. Handles deployment automation, GitOps configuration,' in text, "expected to find: " + 'description: Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes manifests, and generates Terraform/Pulumi infrastructure templates. Handles deployment automation, GitOps configuration,'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/devops-engineer/SKILL.md')
    assert '4. **Validate** - Run `terraform plan`, lint configs, execute unit/integration tests; confirm no destructive changes before proceeding' in text, "expected to find: " + '4. **Validate** - Run `terraform plan`, lint configs, execute unit/integration tests; confirm no destructive changes before proceeding'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/devops-engineer/SKILL.md')
    assert 'Always document the rollback command and verification step in the PR or change ticket before deploying.' in text, "expected to find: " + 'Always document the rollback command and verification step in the PR or change ticket before deploying.'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/django-expert/SKILL.md')
    assert 'description: "Use when building Django web applications or REST APIs with Django REST Framework. Invoke when working with settings.py, models.py, manage.py, or any Django project file. Creates Django ' in text, "expected to find: " + 'description: "Use when building Django web applications or REST APIs with Django REST Framework. Invoke when working with settings.py, models.py, manage.py, or any Django project file. Creates Django '[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/django-expert/SKILL.md')
    assert '2. **Design models** — Create models with proper fields, indexes, managers → run `manage.py makemigrations` and `manage.py migrate`; verify schema before proceeding' in text, "expected to find: " + '2. **Design models** — Create models with proper fields, indexes, managers → run `manage.py makemigrations` and `manage.py migrate`; verify schema before proceeding'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/django-expert/SKILL.md')
    assert 'The snippet below demonstrates the core MUST DO constraints: indexed fields, `select_related`, serializer validation, and endpoint permissions.' in text, "expected to find: " + 'The snippet below demonstrates the core MUST DO constraints: indexed fields, `select_related`, serializer validation, and endpoint permissions.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-core-expert/SKILL.md')
    assert '5. **Test** — Write comprehensive tests with xUnit and integration testing; run `dotnet test` to confirm all tests pass — if tests fail, diagnose failures, fix the implementation, and re-run before co' in text, "expected to find: " + '5. **Test** — Write comprehensive tests with xUnit and integration testing; run `dotnet test` to confirm all tests pass — if tests fail, diagnose failures, fix the implementation, and re-run before co'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-core-expert/SKILL.md')
    assert '3. **Implement** — Write high-performance code with modern C# features; run `dotnet build` to verify compilation — if build fails, review errors, fix issues, and rebuild before proceeding' in text, "expected to find: " + '3. **Implement** — Write high-performance code with modern C# features; run `dotnet build` to verify compilation — if build fails, review errors, fix issues, and rebuild before proceeding'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-core-expert/SKILL.md')
    assert 'builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));' in text, "expected to find: " + 'builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/embedded-systems/SKILL.md')
    assert 'description: Use when developing firmware for microcontrollers, implementing RTOS applications, or optimizing power consumption. Invoke for STM32, ESP32, FreeRTOS, bare-metal, power optimization, real' in text, "expected to find: " + 'description: Use when developing firmware for microcontrollers, implementing RTOS applications, or optimizing power consumption. Invoke for STM32, ESP32, FreeRTOS, bare-metal, power optimization, real'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/embedded-systems/SKILL.md')
    assert '6. **Test and verify** - Validate timing with logic analyzer or oscilloscope; check stack usage with `uxTaskGetStackHighWaterMark()`; measure ISR latency; confirm no missed deadlines under worst-case ' in text, "expected to find: " + '6. **Test and verify** - Validate timing with logic analyzer or oscilloscope; check stack usage with `uxTaskGetStackHighWaterMark()`; measure ISR latency; confirm no missed deadlines under worst-case '[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/embedded-systems/SKILL.md')
    assert '4. **Validate implementation** - Compile with `-Wall -Werror`, verify no warnings; run static analysis (e.g. `cppcheck`); confirm correct register bit-field usage against datasheet' in text, "expected to find: " + '4. **Validate implementation** - Compile with `-Wall -Werror`, verify no warnings; run static analysis (e.g. `cppcheck`); confirm correct register bit-field usage against datasheet'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fastapi-expert/SKILL.md')
    assert 'description: "Use when building high-performance async Python APIs with FastAPI and Pydantic V2. Invoke to create REST endpoints, define Pydantic models, implement authentication flows, set up async S' in text, "expected to find: " + 'description: "Use when building high-performance async Python APIs with FastAPI and Pydantic V2. Invoke to create REST endpoints, define Pydantic models, implement authentication flows, set up async S'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fastapi-expert/SKILL.md')
    assert '> **Checkpoint after each step:** confirm schemas validate correctly, endpoints return expected HTTP status codes, and `/docs` reflects the intended API surface before proceeding.' in text, "expected to find: " + '> **Checkpoint after each step:** confirm schemas validate correctly, endpoints return expected HTTP status codes, and `/docs` reflects the intended API surface before proceeding.'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fastapi-expert/SKILL.md')
    assert '5. **Test** — Write async tests with pytest and httpx; run `pytest` after each endpoint group and verify OpenAPI docs at `/docs`' in text, "expected to find: " + '5. **Test** — Write async tests with pytest and httpx; run `pytest` after each endpoint group and verify OpenAPI docs at `/docs`'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/feature-forge/SKILL.md')
    assert 'description: Conducts structured requirements workshops to produce feature specifications, user stories, EARS-format functional requirements, acceptance criteria, and implementation checklists. Use wh' in text, "expected to find: " + 'description: Conducts structured requirements workshops to produce feature specifications, user stories, EARS-format functional requirements, acceptance criteria, and implementation checklists. Use wh'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/feature-forge/SKILL.md')
    assert '**Inline acceptance criteria example** (load `references/acceptance-criteria.md` for full format):' in text, "expected to find: " + '**Inline acceptance criteria example** (load `references/acceptance-criteria.md` for full format):'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/feature-forge/SKILL.md')
    assert '**Inline EARS format examples** (load `references/ears-syntax.md` for full syntax):' in text, "expected to find: " + '**Inline EARS format examples** (load `references/ears-syntax.md` for full syntax):'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fine-tuning-expert/SKILL.md')
    assert 'description: "Use when fine-tuning LLMs, training custom models, or adapting foundation models for specific tasks. Invoke for configuring LoRA/QLoRA adapters, preparing JSONL training datasets, settin' in text, "expected to find: " + 'description: "Use when fine-tuning LLMs, training custom models, or adapting foundation models for specific tasks. Invoke for configuring LoRA/QLoRA adapters, preparing JSONL training datasets, settin'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fine-tuning-expert/SKILL.md')
    assert 'triggers: fine-tuning, fine tuning, finetuning, LoRA, QLoRA, PEFT, adapter tuning, transfer learning, model training, custom model, LLM training, instruction tuning, RLHF, model optimization, quantiza' in text, "expected to find: " + 'triggers: fine-tuning, fine tuning, finetuning, LoRA, QLoRA, PEFT, adapter tuning, transfer learning, model training, custom model, LLM training, instruction tuning, RLHF, model optimization, quantiza'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fine-tuning-expert/SKILL.md')
    assert '1. **Dataset preparation script** with validation logic (schema checks, token-length histogram, deduplication)' in text, "expected to find: " + '1. **Dataset preparation script** with validation logic (schema checks, token-length histogram, deduplication)'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flutter-expert/SKILL.md')
    assert '| Jank / dropped frames | Expensive `build()` calls, uncached widgets, heavy main-thread work | Use `RepaintBoundary`, move heavy work to `compute()`, add `const` |' in text, "expected to find: " + '| Jank / dropped frames | Expensive `build()` calls, uncached widgets, heavy main-thread work | Use `RepaintBoundary`, move heavy work to `compute()`, add `const` |'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flutter-expert/SKILL.md')
    assert '| Widget test assertion failures | Widget tree mismatch or async state not settled | Use `tester.pumpAndSettle()` after state changes; verify finder selectors |' in text, "expected to find: " + '| Widget test assertion failures | Widget tree mismatch or async state not settled | Use `tester.pumpAndSettle()` after state changes; verify finder selectors |'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flutter-expert/SKILL.md')
    assert '- If jank persists: check rebuild counts in the Performance overlay, isolate expensive `build()` calls, apply `const` or move state closer to consumers' in text, "expected to find: " + '- If jank persists: check rebuild counts in the Performance overlay, isolate expensive `build()` calls, apply `const` or move state closer to consumers'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fullstack-guardian/SKILL.md')
    assert 'description: Builds security-focused full-stack web applications by implementing integrated frontend and backend components with layered security at every level. Covers the complete stack from databas' in text, "expected to find: " + 'description: Builds security-focused full-stack web applications by implementing integrated frontend and backend components with layered security at every level. Covers the complete stack from databas'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fullstack-guardian/SKILL.md')
    assert '4. **Security checkpoint** - Run through `references/security-checklist.md` before writing any code; confirm auth, authz, validation, and output encoding are addressed' in text, "expected to find: " + '4. **Security checkpoint** - Run through `references/security-checklist.md` before writing any code; confirm auth, authz, validation, and output encoding are addressed'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/fullstack-guardian/SKILL.md')
    assert '- Auth enforced server-side via `require_auth` dependency; client header is a convenience, not the gate.' in text, "expected to find: " + '- Auth enforced server-side via `require_auth` dependency; client header is a convenience, not the gate.'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/game-developer/SKILL.md')
    assert 'description: "Use when building game systems, implementing Unity/Unreal Engine features, or optimizing game performance. Invoke to implement ECS architecture, configure physics systems and colliders, ' in text, "expected to find: " + 'description: "Use when building game systems, implementing Unity/Unreal Engine features, or optimizing game performance. Invoke to implement ECS architecture, configure physics systems and colliders, '[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/game-developer/SKILL.md')
    assert '- ✅ **Validation checkpoint:** Run Unity Profiler or Unreal Insights; verify frame time ≤16 ms (60 FPS) before proceeding. Identify and resolve CPU/GPU bottlenecks iteratively.' in text, "expected to find: " + '- ✅ **Validation checkpoint:** Run Unity Profiler or Unreal Insights; verify frame time ≤16 ms (60 FPS) before proceeding. Identify and resolve CPU/GPU bottlenecks iteratively.'[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/game-developer/SKILL.md')
    assert '- ✅ **Validation checkpoint:** Confirm stable frame rate under stress load; run multiplayer latency/desync tests before shipping.' in text, "expected to find: " + '- ✅ **Validation checkpoint:** Confirm stable frame rate under stress load; run multiplayer latency/desync tests before shipping.'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/golang-pro/SKILL.md')
    assert 'description: Implements concurrent Go patterns using goroutines and channels, designs and builds microservices with gRPC or REST, optimizes Go application performance with pprof, and enforces idiomati' in text, "expected to find: " + 'description: Implements concurrent Go patterns using goroutines and channels, designs and builds microservices with gRPC or REST, optimizes Go application performance with pprof, and enforces idiomati'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/golang-pro/SKILL.md')
    assert 'Key properties demonstrated: bounded goroutine lifetime via `ctx`, error propagation with `%w`, no goroutine leak on cancellation.' in text, "expected to find: " + 'Key properties demonstrated: bounded goroutine lifetime via `ctx`, error propagation with `%w`, no goroutine leak on cancellation.'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/golang-pro/SKILL.md')
    assert '3. **Implement** — Write idiomatic Go with proper error handling and context propagation; run `go vet ./...` before proceeding' in text, "expected to find: " + '3. **Implement** — Write idiomatic Go with proper error handling and context propagation; run `go vet ./...` before proceeding'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/graphql-architect/SKILL.md')
    assert '- _If composition fails:_ review entity `@key` directives, check for missing or mismatched type definitions across subgraphs, resolve any `@external` field inconsistencies, then re-run composition' in text, "expected to find: " + '- _If composition fails:_ review entity `@key` directives, check for missing or mismatched type definitions across subgraphs, resolve any `@external` field inconsistencies, then re-run composition'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/graphql-architect/SKILL.md')
    assert '- _If complexity threshold is exceeded:_ identify the highest-cost fields, add pagination limits, restructure nested queries, or raise the threshold with documented justification' in text, "expected to find: " + '- _If complexity threshold is exceeded:_ identify the highest-cost fields, add pagination limits, restructure nested queries, or raise the threshold with documented justification'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/graphql-architect/SKILL.md')
    assert '5. **Secure** - Add query complexity limits, depth limiting, field-level auth; validate complexity thresholds before deployment' in text, "expected to find: " + '5. **Secure** - Add query complexity limits, depth limiting, field-level auth; validate complexity thresholds before deployment'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/java-architect/SKILL.md')
    assert 'description: Use when building, configuring, or debugging enterprise Java applications with Spring Boot 3.x, microservices, or reactive programming. Invoke to implement WebFlux endpoints, optimize JPA' in text, "expected to find: " + 'description: Use when building, configuring, or debugging enterprise Java applications with Spring Boot 3.x, microservices, or reactive programming. Invoke to implement WebFlux endpoints, optimize JPA'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/java-architect/SKILL.md')
    assert '6. **Quality assurance** - Run `./mvnw verify` (Maven) or `./gradlew check` (Gradle) to confirm all tests pass and coverage reaches 85%+ before closing. If coverage is below threshold: identify untest' in text, "expected to find: " + '6. **Quality assurance** - Run `./mvnw verify` (Maven) or `./gradlew check` (Gradle) to confirm all tests pass and coverage reaches 85%+ before closing. If coverage is below threshold: identify untest'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/java-architect/SKILL.md')
    assert '5. **Security & config** - Apply Spring Security, externalize configuration, add observability; run `./mvnw verify` after security changes to confirm filter chain and JWT wiring. If tests fail: check ' in text, "expected to find: " + '5. **Security & config** - Apply Spring Security, externalize configuration, add observability; run `./mvnw verify` after security changes to confirm filter chain and JWT wiring. If tests fail: check '[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/javascript-pro/SKILL.md')
    assert 'description: Writes, debugs, and refactors JavaScript code using modern ES2023+ features, async/await patterns, ESM module systems, and Node.js APIs. Use when building vanilla JavaScript applications,' in text, "expected to find: " + 'description: Writes, debugs, and refactors JavaScript code using modern ES2023+ features, async/await patterns, ESM module systems, and Node.js APIs. Use when building vanilla JavaScript applications,'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/javascript-pro/SKILL.md')
    assert '4. **Validate** — Run linter (`eslint --fix`); if linter fails, fix all reported issues and re-run before proceeding. Check for memory leaks with DevTools or `--inspect`, verify bundle size; if leaks ' in text, "expected to find: " + '4. **Validate** — Run linter (`eslint --fix`); if linter fails, fix all reported issues and re-run before proceeding. Check for memory leaks with DevTools or `--inspect`, verify bundle size; if leaks '[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/javascript-pro/SKILL.md')
    assert '5. **Test** — Write comprehensive tests with Jest achieving 85%+ coverage; if coverage falls short, add missing cases and re-run. Confirm no unhandled Promise rejections' in text, "expected to find: " + '5. **Test** — Write comprehensive tests with Jest achieving 85%+ coverage; if coverage falls short, add missing cases and re-run. Confirm no unhandled Promise rejections'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-specialist/SKILL.md')
    assert 'description: Provides idiomatic Kotlin implementation patterns including coroutine concurrency, Flow stream handling, multiplatform architecture, Compose UI construction, Ktor server setup, and type-s' in text, "expected to find: " + 'description: Provides idiomatic Kotlin implementation patterns including coroutine concurrency, Flow stream handling, multiplatform architecture, Compose UI construction, Ktor server setup, and type-s'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-specialist/SKILL.md')
    assert '- *Checkpoint:* Verify coroutine cancellation is handled (parent scope cancelled on teardown) and null safety is enforced before proceeding' in text, "expected to find: " + '- *Checkpoint:* Verify coroutine cancellation is handled (parent scope cancelled on teardown) and null safety is enforced before proceeding'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-specialist/SKILL.md')
    assert '- *If detekt/ktlint fails:* Fix all reported issues and re-run both tools before proceeding to step 5' in text, "expected to find: " + '- *If detekt/ktlint fails:* Fix all reported issues and re-run both tools before proceeding to step 5'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-specialist/SKILL.md')
    assert 'description: Use when deploying or managing Kubernetes workloads. Invoke to create deployment manifests, configure pod security policies, set up service accounts, define network isolation rules, debug' in text, "expected to find: " + 'description: Use when deploying or managing Kubernetes workloads. Invoke to create deployment manifests, configure pod security policies, set up service accounts, define network isolation rules, debug'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-specialist/SKILL.md')
    assert '5. **Validate** — Run `kubectl rollout status`, `kubectl get pods -w`, and `kubectl describe pod <name>` to confirm health; roll back with `kubectl rollout undo` if needed' in text, "expected to find: " + '5. **Validate** — Run `kubectl rollout status`, `kubectl get pods -w`, and `kubectl describe pod <name>` to confirm health; roll back with `kubectl rollout undo` if needed'[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-specialist/SKILL.md')
    assert '1. **Analyze requirements** — Understand workload characteristics, scaling needs, security requirements' in text, "expected to find: " + '1. **Analyze requirements** — Understand workload characteristics, scaling needs, security requirements'[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-specialist/SKILL.md')
    assert 'description: Build and configure Laravel 10+ applications, including creating Eloquent models and relationships, implementing Sanctum authentication, configuring Horizon queues, designing RESTful APIs' in text, "expected to find: " + 'description: Build and configure Laravel 10+ applications, including creating Eloquent models and relationships, implementing Sanctum authentication, configuring Horizon queues, designing RESTful APIs'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-specialist/SKILL.md')
    assert '3. **Implement models** — Create Eloquent models with relationships, scopes, and casts; run `php artisan make:model` and verify with `php artisan migrate:status`' in text, "expected to find: " + '3. **Implement models** — Create Eloquent models with relationships, scopes, and casts; run `php artisan make:model` and verify with `php artisan migrate:status`'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-specialist/SKILL.md')
    assert '5. **Test thoroughly** — Write feature and unit tests; run `php artisan test` before considering any step complete (target >85% coverage)' in text, "expected to find: " + '5. **Test thoroughly** — Write feature and unit tests; run `php artisan test` before considering any step complete (target >85% coverage)'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/legacy-modernizer/SKILL.md')
    assert 'description: Designs incremental migration strategies, identifies service boundaries, produces dependency maps and migration roadmaps, and generates API facade designs for aging codebases. Use when mo' in text, "expected to find: " + 'description: Designs incremental migration strategies, identifies service boundaries, produces dependency maps and migration roadmaps, and generates API facade designs for aging codebases. Use when mo'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/legacy-modernizer/SKILL.md')
    assert '2. **Plan migration** — Design an incremental roadmap with explicit rollback strategies per phase. Reference `references/system-assessment.md` for code analysis templates.' in text, "expected to find: " + '2. **Plan migration** — Design an incremental roadmap with explicit rollback strategies per phase. Reference `references/system-assessment.md` for code analysis templates.'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/legacy-modernizer/SKILL.md')
    assert '- *Validation checkpoint:* Verify error rates and latency metrics remain within baseline thresholds after each traffic increment (e.g., 5% → 25% → 50% → 100%).' in text, "expected to find: " + '- *Validation checkpoint:* Verify error rates and latency metrics remain within baseline thresholds after each traffic increment (e.g., 5% → 25% → 50% → 100%).'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-developer/SKILL.md')
    assert '5. **Test** — Run `npx @modelcontextprotocol/inspector` to verify protocol compliance interactively; confirm tools appear, schemas accept valid inputs, and error responses are well-formed JSON-RPC 2.0' in text, "expected to find: " + '5. **Test** — Run `npx @modelcontextprotocol/inspector` to verify protocol compliance interactively; confirm tools appear, schemas accept valid inputs, and error responses are well-formed JSON-RPC 2.0'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-developer/SKILL.md')
    assert 'description: Use when building, debugging, or extending MCP servers or clients that connect AI systems with external tools and data sources. Invoke to implement tool handlers, configure resource provi' in text, "expected to find: " + 'description: Use when building, debugging, or extending MCP servers or clients that connect AI systems with external tools and data sources. Invoke to implement tool handlers, configure resource provi'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-developer/SKILL.md')
    assert '2. **Initialize project** — `npx @modelcontextprotocol/create-server my-server` (TypeScript) or `pip install mcp` + scaffold (Python)' in text, "expected to find: " + '2. **Initialize project** — `npx @modelcontextprotocol/create-server my-server` (TypeScript) or `pip install mcp` + scaffold (Python)'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/microservices-architect/SKILL.md')
    assert 'description: Designs distributed system architectures, decomposes monoliths into bounded-context services, recommends communication patterns, and produces service boundary diagrams and resilience stra' in text, "expected to find: " + 'description: Designs distributed system architectures, decomposes monoliths into bounded-context services, recommends communication patterns, and produces service boundary diagrams and resilience stra'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/microservices-architect/SKILL.md')
    assert '- *Validation checkpoint:* Long-running or cross-aggregate operations use async messaging; only query/command pairs with sub-100 ms SLA use synchronous calls.' in text, "expected to find: " + '- *Validation checkpoint:* Long-running or cross-aggregate operations use async messaging; only query/command pairs with sub-100 ms SLA use synchronous calls.'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/microservices-architect/SKILL.md')
    assert '- *Validation checkpoint:* Each candidate service owns its data exclusively, has a clear public API contract, and can be deployed independently.' in text, "expected to find: " + '- *Validation checkpoint:* Each candidate service owns its data exclusively, has a clear public API contract, and can be deployed independently.'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ml-pipeline/SKILL.md')
    assert 'description: "Designs and implements production-grade ML pipeline infrastructure: configures experiment tracking with MLflow or Weights & Biases, creates Kubeflow or Airflow DAGs for training orchestr' in text, "expected to find: " + 'description: "Designs and implements production-grade ML pipeline infrastructure: configures experiment tracking with MLflow or Weights & Biases, creates Kubeflow or Airflow DAGs for training orchestr'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ml-pipeline/SKILL.md')
    assert '2. **Validate data schema** — Run schema checks and distribution validation before any training begins; halt and report on failures' in text, "expected to find: " + '2. **Validate data schema** — Run schema checks and distribution validation before any training begins; halt and report on failures'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ml-pipeline/SKILL.md')
    assert '1. Complete pipeline definition (Kubeflow DAG, Airflow DAG, or equivalent) — use the templates above as starting structure' in text, "expected to find: " + '1. Complete pipeline definition (Kubeflow DAG, Airflow DAG, or equivalent) — use the templates above as starting structure'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitoring-expert/SKILL.md')
    assert 'description: Configures monitoring systems, implements structured logging pipelines, creates Prometheus/Grafana dashboards, defines alerting rules, and instruments distributed tracing. Implements Prom' in text, "expected to find: " + 'description: Configures monitoring systems, implements structured logging pipelines, creates Prometheus/Grafana dashboards, defines alerting rules, and instruments distributed tracing. Implements Prom'[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitoring-expert/SKILL.md')
    assert '3. **Collect** — Configure aggregation and storage (Prometheus scrape, log shipper, OTLP endpoint); verify data arrives before proceeding' in text, "expected to find: " + '3. **Collect** — Configure aggregation and storage (Prometheus scrape, log shipper, OTLP endpoint); verify data arrives before proceeding'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitoring-expert/SKILL.md')
    assert '5. **Alert** — Define threshold and anomaly alerts on critical paths; validate no false-positive flood before shipping' in text, "expected to find: " + '5. **Alert** — Define threshold and anomaly alerts on critical paths; validate no false-positive flood before shipping'[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nestjs-expert/SKILL.md')
    assert 'description: Creates and configures NestJS modules, controllers, services, DTOs, guards, and interceptors for enterprise-grade TypeScript backend applications. Use when building NestJS REST APIs or Gr' in text, "expected to find: " + 'description: Creates and configures NestJS modules, controllers, services, DTOs, guards, and interceptors for enterprise-grade TypeScript backend applications. Use when building NestJS REST APIs or Gr'[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nestjs-expert/SKILL.md')
    assert '- Use `@Injectable()` and constructor injection for all services — never instantiate services with `new`' in text, "expected to find: " + '- Use `@Injectable()` and constructor injection for all services — never instantiate services with `new`'[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nestjs-expert/SKILL.md')
    assert '- Validate all inputs with `class-validator` decorators on DTOs and enable `ValidationPipe` globally' in text, "expected to find: " + '- Validate all inputs with `class-validator` decorators on DTOs and enable `ValidationPipe` globally'[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nextjs-developer/SKILL.md')
    assert 'description: "Use when building Next.js 14+ applications with App Router, server components, or server actions. Invoke to configure route handlers, implement middleware, set up API routes, add streami' in text, "expected to find: " + 'description: "Use when building Next.js 14+ applications with App Router, server components, or server actions. Invoke to configure route handlers, implement middleware, set up API routes, add streami'[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nextjs-developer/SKILL.md')
    assert '- Validate: run `next build` locally, confirm zero type errors, check `NEXT_PUBLIC_*` and server-only env vars are set, run Lighthouse/PageSpeed to confirm Core Web Vitals > 90' in text, "expected to find: " + '- Validate: run `next build` locally, confirm zero type errors, check `NEXT_PUBLIC_*` and server-only env vars are set, run Lighthouse/PageSpeed to confirm Core Web Vitals > 90'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nextjs-developer/SKILL.md')
    assert "- Keep components as Server Components by default; add `'use client'` only at the leaf boundary where interactivity is required" in text, "expected to find: " + "- Keep components as Server Components by default; add `'use client'` only at the leaf boundary where interactivity is required"[:80]


def test_signal_111():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pandas-pro/SKILL.md')
    assert 'description: Performs pandas DataFrame operations for data analysis, manipulation, and transformation. Use when working with pandas DataFrames, data cleaning, aggregation, merging, or time series anal' in text, "expected to find: " + 'description: Performs pandas DataFrame operations for data analysis, manipulation, and transformation. Use when working with pandas DataFrames, data cleaning, aggregation, merging, or time series anal'[:80]


def test_signal_112():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pandas-pro/SKILL.md')
    assert '2. **Design transformation** — Plan vectorized operations, avoid loops, identify indexing strategy' in text, "expected to find: " + '2. **Design transformation** — Plan vectorized operations, avoid loops, identify indexing strategy'[:80]


def test_signal_113():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pandas-pro/SKILL.md')
    assert '1. **Assess data structure** — Examine dtypes, memory usage, missing values, data quality:' in text, "expected to find: " + '1. **Assess data structure** — Examine dtypes, memory usage, missing values, data quality:'[:80]


def test_signal_114():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/SKILL.md')
    assert 'description: Use when building PHP applications with modern PHP 8.3+ features, Laravel, or Symfony frameworks. Invokes strict typing, PHPStan level 9, async patterns with Swoole, and PSR standards. Cr' in text, "expected to find: " + 'description: Use when building PHP applications with modern PHP 8.3+ features, Laravel, or Symfony frameworks. Invokes strict typing, PHPStan level 9, async patterns with Swoole, and PSR standards. Cr'[:80]


def test_signal_115():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/SKILL.md')
    assert '5. **Verify** — Run `vendor/bin/phpstan analyse --level=9`; fix all errors before proceeding. Run `vendor/bin/phpunit` or `vendor/bin/pest`; enforce 80%+ coverage. Only deliver when both pass clean.' in text, "expected to find: " + '5. **Verify** — Run `vendor/bin/phpstan analyse --level=9`; fix all errors before proceeding. Run `vendor/bin/phpunit` or `vendor/bin/pest`; enforce 80%+ coverage. Only deliver when both pass clean.'[:80]


def test_signal_116():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/SKILL.md')
    assert 'Every complete implementation delivers: a typed entity/DTO, a service class, and a test. Use these as the baseline structure.' in text, "expected to find: " + 'Every complete implementation delivers: a typed entity/DTO, a service class, and a test. Use these as the baseline structure.'[:80]


def test_signal_117():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/playwright-expert/SKILL.md')
    assert 'description: "Use when writing E2E tests with Playwright, setting up test infrastructure, or debugging flaky browser tests. Invoke to write test scripts, create page objects, configure test fixtures, ' in text, "expected to find: " + 'description: "Use when writing E2E tests with Playwright, setting up test infrastructure, or debugging flaky browser tests. Invoke to write test scripts, create page objects, configure test fixtures, '[:80]


def test_signal_118():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/playwright-expert/SKILL.md')
    assert 'E2E testing specialist with deep expertise in Playwright for robust, maintainable browser automation.' in text, "expected to find: " + 'E2E testing specialist with deep expertise in Playwright for robust, maintainable browser automation.'[:80]


def test_signal_119():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/playwright-expert/SKILL.md')
    assert "await page.getByRole('button', { name: 'Save' }).waitFor({ state: 'visible' });" in text, "expected to find: " + "await page.getByRole('button', { name: 'Save' }).waitFor({ state: 'visible' });"[:80]


def test_signal_120():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-pro/SKILL.md')
    assert '5. **Monitor and maintain** — Track VACUUM, bloat, and autovacuum via `pg_stat` views; verify improvements after each change' in text, "expected to find: " + '5. **Monitor and maintain** — Track VACUUM, bloat, and autovacuum via `pg_stat` views; verify improvements after each change'[:80]


def test_signal_121():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-pro/SKILL.md')
    assert '2. **Design indexes** — Choose B-tree, GIN, GiST, or BRIN based on workload; verify with `EXPLAIN` before deploying' in text, "expected to find: " + '2. **Design indexes** — Choose B-tree, GIN, GiST, or BRIN based on workload; verify with `EXPLAIN` before deploying'[:80]


def test_signal_122():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-pro/SKILL.md')
    assert '4. **Setup replication** — Streaming or logical based on requirements; monitor lag continuously' in text, "expected to find: " + '4. **Setup replication** — Streaming or logical based on requirements; monitor lag continuously'[:80]


def test_signal_123():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prompt-engineer/SKILL.md')
    assert 'description: Writes, refactors, and evaluates prompts for LLMs — generating optimized prompt templates, structured output schemas, evaluation rubrics, and test suites. Use when designing prompts for n' in text, "expected to find: " + 'description: Writes, refactors, and evaluates prompts for LLMs — generating optimized prompt templates, structured output schemas, evaluation rubrics, and test suites. Use when designing prompts for n'[:80]


def test_signal_124():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prompt-engineer/SKILL.md')
    assert 'Reference files cover major prompting techniques (zero-shot, few-shot, CoT, ReAct, tree-of-thoughts), structured output patterns (JSON mode, function calling), and model-specific guidance for GPT-4, C' in text, "expected to find: " + 'Reference files cover major prompting techniques (zero-shot, few-shot, CoT, ReAct, tree-of-thoughts), structured output patterns (JSON mode, function calling), and model-specific guidance for GPT-4, C'[:80]


def test_signal_125():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prompt-engineer/SKILL.md')
    assert 'Summarize the document below in exactly 3 bullet points. Each bullet must be one sentence and start with an action verb. Do not include opinions or information not present in the document.' in text, "expected to find: " + 'Summarize the document below in exactly 3 bullet points. Each bullet must be one sentence and start with an action verb. Do not include opinions or information not present in the document.'[:80]


def test_signal_126():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/python-pro/SKILL.md')
    assert 'description: Use when building Python 3.11+ applications requiring type safety, async programming, or robust error handling. Generates type-annotated Python code, configures mypy in strict mode, write' in text, "expected to find: " + 'description: Use when building Python 3.11+ applications requiring type safety, async programming, or robust error handling. Generates type-annotated Python code, configures mypy in strict mode, write'[:80]


def test_signal_127():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/python-pro/SKILL.md')
    assert 'Any reported error (e.g., `error: Function is missing a return type annotation`) must be resolved before the implementation is considered complete.' in text, "expected to find: " + 'Any reported error (e.g., `error: Function is missing a return type annotation`) must be resolved before the implementation is considered complete.'[:80]


def test_signal_128():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/python-pro/SKILL.md')
    assert 'Modern Python 3.11+ specialist focused on type-safe, async-first, production-ready code.' in text, "expected to find: " + 'Modern Python 3.11+ specialist focused on type-safe, async-first, production-ready code.'[:80]


def test_signal_129():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rag-architect/SKILL.md')
    assert 'description: Designs and implements production-grade RAG systems by chunking documents, generating embeddings, configuring vector stores, building hybrid search pipelines, applying reranking, and eval' in text, "expected to find: " + 'description: Designs and implements production-grade RAG systems by chunking documents, generating embeddings, configuring vector stores, building hybrid search pipelines, applying reranking, and eval'[:80]


def test_signal_130():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rag-architect/SKILL.md')
    assert '**Checkpoint:** `assert qdrant.count("knowledge_base").count == len(set(p.id for p in points)), "Deduplication failed"`' in text, "expected to find: " + '**Checkpoint:** `assert qdrant.count("knowledge_base").count == len(set(p.id for p in points)), "Deduplication failed"`'[:80]


def test_signal_131():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rag-architect/SKILL.md')
    assert '**Checkpoint:** `assert len(hybrid_search("test query", tenant_id="demo")) > 0, "Hybrid search returned no results"`' in text, "expected to find: " + '**Checkpoint:** `assert len(hybrid_search("test query", tenant_id="demo")) > 0, "Hybrid search returned no results"`'[:80]


def test_signal_132():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rails-expert/SKILL.md')
    assert 'description: Rails 7+ specialist that optimizes Active Record queries with includes/eager_load, implements Turbo Frames and Turbo Streams for partial page updates, configures Action Cable for WebSocke' in text, "expected to find: " + 'description: Rails 7+ specialist that optimizes Active Record queries with includes/eager_load, implements Turbo Frames and Turbo Streams for partial page updates, configures Action Cable for WebSocke'[:80]


def test_signal_133():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rails-expert/SKILL.md')
    assert '2. **Scaffold resources** — `rails generate model User name:string email:string`, `rails generate controller Users`' in text, "expected to find: " + '2. **Scaffold resources** — `rails generate model User name:string email:string`, `rails generate controller Users`'[:80]


def test_signal_134():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rails-expert/SKILL.md')
    assert '- If migration fails: inspect `db/schema.rb` for conflicts, rollback with `rails db:rollback`, fix and retry' in text, "expected to find: " + '- If migration fails: inspect `db/schema.rb` for conflicts, rollback with `rails db:rollback`, fix and retry'[:80]


def test_signal_135():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-expert/SKILL.md')
    assert 'description: Use when building React 18+ applications in .jsx or .tsx files, Next.js App Router projects, or create-react-app setups. Creates components, implements custom hooks, debugs rendering issu' in text, "expected to find: " + 'description: Use when building React 18+ applications in .jsx or .tsx files, Next.js App Router projects, or create-react-app setups. Creates components, implements custom hooks, debugs rendering issu'[:80]


def test_signal_136():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-expert/SKILL.md')
    assert '4. **Validate** - Run `tsc --noEmit`; if it fails, review reported errors, fix all type issues, and re-run until clean before proceeding' in text, "expected to find: " + '4. **Validate** - Run `tsc --noEmit`; if it fails, review reported errors, fix all type issues, and re-run until clean before proceeding'[:80]


def test_signal_137():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-expert/SKILL.md')
    assert '5. **Optimize** - Apply memoization where needed, ensure accessibility; if new type errors are introduced, return to step 4' in text, "expected to find: " + '5. **Optimize** - Apply memoization where needed, ensure accessibility; if new type errors are introduced, return to step 4'[:80]


def test_signal_138():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-native-expert/SKILL.md')
    assert 'description: Builds, optimizes, and debugs cross-platform mobile applications with React Native and Expo. Implements navigation hierarchies (tabs, stacks, drawers), configures native modules, optimize' in text, "expected to find: " + 'description: Builds, optimizes, and debugs cross-platform mobile applications with React Native and Expo. Implements navigation hierarchies (tabs, stacks, drawers), configures native modules, optimize'[:80]


def test_signal_139():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-native-expert/SKILL.md')
    assert '1. **Setup** — Expo Router or React Navigation, TypeScript config → _run `npx expo doctor` to verify environment and SDK compatibility; fix any reported issues before proceeding_' in text, "expected to find: " + '1. **Setup** — Expo Router or React Navigation, TypeScript config → _run `npx expo doctor` to verify environment and SDK compatibility; fix any reported issues before proceeding_'[:80]


def test_signal_140():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-native-expert/SKILL.md')
    assert '3. **Implement** — Components with platform handling → _verify on iOS simulator and Android emulator; check Metro bundler output for errors before moving on_' in text, "expected to find: " + '3. **Implement** — Components with platform handling → _verify on iOS simulator and Android emulator; check Metro bundler output for errors before moving on_'[:80]


def test_signal_141():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rust-engineer/SKILL.md')
    assert 'description: Writes, reviews, and debugs idiomatic Rust code with memory safety and zero-cost abstractions. Implements ownership patterns, manages lifetimes, designs trait hierarchies, builds async ap' in text, "expected to find: " + 'description: Writes, reviews, and debugs idiomatic Rust code with memory safety and zero-cost abstractions. Implements ownership patterns, manages lifetimes, designs trait hierarchies, builds async ap'[:80]


def test_signal_142():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rust-engineer/SKILL.md')
    assert '1. **Analyze ownership** — Design lifetime relationships and borrowing patterns; annotate lifetimes explicitly where inference is insufficient' in text, "expected to find: " + '1. **Analyze ownership** — Design lifetime relationships and borrowing patterns; annotate lifetimes explicitly where inference is insufficient'[:80]


def test_signal_143():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rust-engineer/SKILL.md')
    assert '5. **Validate** — Run `cargo clippy --all-targets --all-features`, `cargo fmt --check`, and `cargo test`; fix all warnings before finalising' in text, "expected to find: " + '5. **Validate** — Run `cargo clippy --all-targets --all-features`, `cargo fmt --check`, and `cargo test`; fix all warnings before finalising'[:80]


def test_signal_144():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/salesforce-developer/SKILL.md')
    assert 'description: Writes and debugs Apex code, builds Lightning Web Components, optimizes SOQL queries, implements triggers, batch jobs, platform events, and integrations on the Salesforce platform. Use wh' in text, "expected to find: " + 'description: Writes and debugs Apex code, builds Lightning Web Components, optimizes SOQL queries, implements triggers, batch jobs, platform events, and integrations on the Salesforce platform. Use wh'[:80]


def test_signal_145():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/salesforce-developer/SKILL.md')
    assert '4. **Validate governor limits** - Verify SOQL/DML counts, heap size, and CPU time stay within platform limits before proceeding' in text, "expected to find: " + '4. **Validate governor limits** - Verify SOQL/DML counts, heap size, and CPU time stay within platform limits before proceeding'[:80]


def test_signal_146():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/salesforce-developer/SKILL.md')
    assert '5. **Test thoroughly** - Write test classes with 90%+ coverage, test bulk scenarios (200-record batches)' in text, "expected to find: " + '5. **Test thoroughly** - Write test classes with 90%+ coverage, test bulk scenarios (200-record batches)'[:80]


def test_signal_147():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/secure-code-guardian/SKILL.md')
    assert 'description: Use when implementing authentication/authorization, securing user input, or preventing OWASP Top 10 vulnerabilities — including custom security implementations such as hashing passwords w' in text, "expected to find: " + 'description: Use when implementing authentication/authorization, securing user input, or preventing OWASP Top 10 vulnerabilities — including custom security implementations such as hashing passwords w'[:80]


def test_signal_148():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/secure-code-guardian/SKILL.md')
    assert '- **Authentication**: Test brute-force protection (lockout/rate limit triggers), session fixation resistance, token expiration, and invalid-credential error messages (must not leak user existence).' in text, "expected to find: " + '- **Authentication**: Test brute-force protection (lockout/rate limit triggers), session fixation resistance, token expiration, and invalid-credential error messages (must not leak user existence).'[:80]


def test_signal_149():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/secure-code-guardian/SKILL.md')
    assert '- **Headers/CORS**: Validate with a security scanner (e.g., `curl -I`, Mozilla Observatory) that security headers are present and CORS origin allowlist is correct.' in text, "expected to find: " + '- **Headers/CORS**: Validate with a security scanner (e.g., `curl -I`, Mozilla Observatory) that security headers are present and CORS origin allowlist is correct.'[:80]


def test_signal_150():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/security-reviewer/SKILL.md')
    assert 'description: Identifies security vulnerabilities, generates structured audit reports with severity ratings, and provides actionable remediation guidance. Use when conducting security audits, reviewing' in text, "expected to find: " + 'description: Identifies security vulnerabilities, generates structured audit reports with severity ratings, and provides actionable remediation guidance. Use when conducting security audits, reviewing'[:80]


def test_signal_151():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/security-reviewer/SKILL.md')
    assert '4. **Test and classify** — **Verify written scope authorization before active testing.** Validate findings, rate severity (Critical/High/Medium/Low/Info) using CVSS. Confirm exploitability with proof-' in text, "expected to find: " + '4. **Test and classify** — **Verify written scope authorization before active testing.** Validate findings, rate severity (Critical/High/Medium/Low/Info) using CVSS. Confirm exploitability with proof-'[:80]


def test_signal_152():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/security-reviewer/SKILL.md')
    assert '5. **Report** — Confirm findings with stakeholder before finalizing. Document with location, impact, and remediation. Report critical findings immediately.' in text, "expected to find: " + '5. **Report** — Confirm findings with stakeholder before finalizing. Document with location, impact, and remediation. Report critical findings immediately.'[:80]


def test_signal_153():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shopify-expert/SKILL.md')
    assert 'description: Builds and debugs Shopify themes (.liquid files, theme.json, sections), develops custom Shopify apps (shopify.app.toml, OAuth, webhooks), and implements Storefront API integrations for he' in text, "expected to find: " + 'description: Builds and debugs Shopify themes (.liquid files, theme.json, sections), develops custom Shopify apps (shopify.app.toml, OAuth, webhooks), and implements Storefront API integrations for he'[:80]


def test_signal_154():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shopify-expert/SKILL.md')
    assert '4. **Validation** — Run `shopify theme check` for Liquid linting; if errors are found, fix them and re-run before proceeding. Run `shopify app dev` to verify app locally; test checkout extensions in s' in text, "expected to find: " + '4. **Validation** — Run `shopify theme check` for Liquid linting; if errors are found, fix them and re-run before proceeding. Run `shopify app dev` to verify app locally; test checkout extensions in s'[:80]


def test_signal_155():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shopify-expert/SKILL.md')
    assert '5. **Deploy and monitor** — `shopify theme push` for themes; `shopify app deploy` for apps; watch Shopify error logs and performance metrics post-deploy' in text, "expected to find: " + '5. **Deploy and monitor** — `shopify theme push` for themes; `shopify app deploy` for apps; watch Shopify error logs and performance metrics post-deploy'[:80]


def test_signal_156():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spark-engineer/SKILL.md')
    assert 'description: Use when writing Spark jobs, debugging performance issues, or configuring cluster settings for Apache Spark applications, distributed data processing pipelines, or big data workloads. Inv' in text, "expected to find: " + 'description: Use when writing Spark jobs, debugging performance issues, or configuring cluster settings for Apache Spark applications, distributed data processing pipelines, or big data workloads. Inv'[:80]


def test_signal_157():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spark-engineer/SKILL.md')
    assert '5. **Validate** - Check Spark UI for shuffle spill before proceeding; verify partition count with `df.rdd.getNumPartitions()`; if spill or skew detected, return to step 4; test with production-scale d' in text, "expected to find: " + '5. **Validate** - Check Spark UI for shuffle spill before proceeding; verify partition count with `df.rdd.getNumPartitions()`; if spill or skew detected, return to step 4; test with production-scale d'[:80]


def test_signal_158():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spark-engineer/SKILL.md')
    assert 'other_df = other_df.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_BUCKETS)]))) \\' in text, "expected to find: " + 'other_df = other_df.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_BUCKETS)]))) \\'[:80]


def test_signal_159():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spec-miner/SKILL.md')
    assert 'description: "Reverse-engineering specialist that extracts specifications from existing codebases. Use when working with legacy or undocumented systems, inherited projects, or old codebases with no do' in text, "expected to find: " + 'description: "Reverse-engineering specialist that extracts specifications from existing codebases. Use when working with legacy or undocumented systems, inherited projects, or old codebases with no do'[:80]


def test_signal_160():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spec-miner/SKILL.md')
    assert '- _Validation checkpoint:_ Confirm sufficient file coverage before proceeding. If key entry points, configuration files, or core modules remain unread, continue exploration before writing documentatio' in text, "expected to find: " + '- _Validation checkpoint:_ Confirm sufficient file coverage before proceeding. If key entry points, configuration files, or core modules remain unread, continue exploration before writing documentatio'[:80]


def test_signal_161():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spec-miner/SKILL.md')
    assert '| Optional | Where `<feature>` is supported, the `<system>` shall `<action>`. | Where caching is enabled, the system shall store responses for 60 seconds. |' in text, "expected to find: " + '| Optional | Where `<feature>` is supported, the `<system>` shall `<action>`. | Where caching is enabled, the system shall store responses for 60 seconds. |'[:80]


def test_signal_162():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spring-boot-engineer/SKILL.md')
    assert 'description: Generates Spring Boot 3.x configurations, creates REST controllers, implements Spring Security 6 authentication flows, sets up Spring Data JPA repositories, and configures reactive WebFlu' in text, "expected to find: " + 'description: Generates Spring Boot 3.x configurations, creates REST controllers, implements Spring Security 6 authentication flows, sets up Spring Data JPA repositories, and configures reactive WebFlu'[:80]


def test_signal_163():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spring-boot-engineer/SKILL.md')
    assert '5. **Test** — Write unit, integration, and slice tests; run `./mvnw test` (or `./gradlew test`) and confirm all pass before proceeding. If tests fail: review the stack trace, isolate the failing asser' in text, "expected to find: " + '5. **Test** — Write unit, integration, and slice tests; run `./mvnw test` (or `./gradlew test`) and confirm all pass before proceeding. If tests fail: review the stack trace, isolate the failing asser'[:80]


def test_signal_164():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/spring-boot-engineer/SKILL.md')
    assert '6. **Deploy** — Configure health checks and observability via Actuator; validate `/actuator/health` returns `UP`. If health is `DOWN`: check the `components` detail in the response, resolve the failin' in text, "expected to find: " + '6. **Deploy** — Configure health checks and observability via Actuator; validate `/actuator/health` returns `UP`. If health is `DOWN`: check the `components` detail in the response, resolve the failin'[:80]


def test_signal_165():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sql-pro/SKILL.md')
    assert 'description: Optimizes SQL queries, designs database schemas, and troubleshoots performance issues. Use when a user asks why their query is slow, needs help writing complex joins or aggregations, ment' in text, "expected to find: " + 'description: Optimizes SQL queries, designs database schemas, and troubleshoots performance issues. Use when a user asks why their query is slow, needs help writing complex joins or aggregations, ment'[:80]


def test_signal_166():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sql-pro/SKILL.md')
    assert '4. **Verify** - Run `EXPLAIN ANALYZE` and confirm no sequential scans on large tables; if query does not meet sub-100ms target, iterate on index selection or query rewrite before proceeding' in text, "expected to find: " + '4. **Verify** - Run `EXPLAIN ANALYZE` and confirm no sequential scans on large tables; if query does not meet sub-100ms target, iterate on index selection or query rewrite before proceeding'[:80]


def test_signal_167():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sql-pro/SKILL.md')
    assert '- **Buffers: shared hit** vs **read** → high `read` count signals missing cache / index' in text, "expected to find: " + '- **Buffers: shared hit** vs **read** → high `read` count signals missing cache / index'[:80]


def test_signal_168():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sre-engineer/SKILL.md')
    assert 'description: Defines service level objectives, creates error budget policies, designs incident response procedures, develops capacity models, and produces monitoring configurations and automation scri' in text, "expected to find: " + 'description: Defines service level objectives, creates error budget policies, designs incident response procedures, develops capacity models, and produces monitoring configurations and automation scri'[:80]


def test_signal_169():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sre-engineer/SKILL.md')
    assert '6. **Test resilience** - Design and execute chaos experiments; verify recovery meets RTO/RPO targets before marking the experiment complete; validate recovery behavior end-to-end' in text, "expected to find: " + '6. **Test resilience** - Design and execute chaos experiments; verify recovery meets RTO/RPO targets before marking the experiment complete; validate recovery behavior end-to-end'[:80]


def test_signal_170():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sre-engineer/SKILL.md')
    assert 'query = f\'sum(rate(http_requests_total{{status=~"5..",service="{service}"}}[5m])) / sum(rate(http_requests_total{{service="{service}"}}[5m]))\'' in text, "expected to find: " + 'query = f\'sum(rate(http_requests_total{{status=~"5..",service="{service}"}}[5m])) / sum(rate(http_requests_total{{service="{service}"}}[5m]))\''[:80]


def test_signal_171():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-expert/SKILL.md')
    assert 'description: Builds iOS/macOS/watchOS/tvOS applications, implements SwiftUI views and state management, designs protocol-oriented architectures, handles async/await concurrency, implements actors for ' in text, "expected to find: " + 'description: Builds iOS/macOS/watchOS/tvOS applications, implements SwiftUI views and state management, designs protocol-oriented architectures, handles async/await concurrency, implements actors for '[:80]


def test_signal_172():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-expert/SKILL.md')
    assert '> **Validation checkpoints:** After step 3, run `swift build` to verify compilation. After step 4, run `swift build -warnings-as-errors` to surface actor isolation and Sendable warnings. After step 5,' in text, "expected to find: " + '> **Validation checkpoints:** After step 3, run `swift build` to verify compilation. After step 4, run `swift build -warnings-as-errors` to surface actor isolation and Sendable warnings. After step 5,'[:80]


def test_signal_173():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-expert/SKILL.md')
    assert '// Avoid wrapping existing async APIs this way when a native async version exists' in text, "expected to find: " + '// Avoid wrapping existing async APIs this way when a native async version exists'[:80]


def test_signal_174():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/terraform-engineer/SKILL.md')
    assert 'description: Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development (create reusable modules, manage module versioning), state management ' in text, "expected to find: " + 'description: Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development (create reusable modules, manage module versioning), state management '[:80]


def test_signal_175():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/terraform-engineer/SKILL.md')
    assert 'When implementing Terraform solutions, provide: module structure (`main.tf`, `variables.tf`, `outputs.tf`), backend and provider configuration, example usage with tfvars, and a brief explanation of de' in text, "expected to find: " + 'When implementing Terraform solutions, provide: module structure (`main.tf`, `variables.tf`, `outputs.tf`), backend and provider configuration, example usage with tfvars, and a brief explanation of de'[:80]


def test_signal_176():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/terraform-engineer/SKILL.md')
    assert '- *State drift* — Run `terraform refresh` to reconcile state with real resources, or use `terraform state rm` / `terraform import` to realign specific resources, then re-plan.' in text, "expected to find: " + '- *State drift* — Run `terraform refresh` to reconcile state with real resources, or use `terraform state rm` / `terraform import` to realign specific resources, then re-plan.'[:80]


def test_signal_177():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test-master/SKILL.md')
    assert 'description: Generates test files, creates mocking strategies, analyzes code coverage, designs test architectures, and produces test plans and defect reports across functional, performance, and securi' in text, "expected to find: " + 'description: Generates test files, creates mocking strategies, analyzes code coverage, designs test architectures, and produces test plans and defect reports across functional, performance, and securi'[:80]


def test_signal_178():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test-master/SKILL.md')
    assert '- If tests are flaky: isolate ordering dependencies, check async handling, add retry or stabilization logic' in text, "expected to find: " + '- If tests are flaky: isolate ordering dependencies, check async handling, add retry or stabilization logic'[:80]


def test_signal_179():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test-master/SKILL.md')
    assert '2. **Create strategy** — Plan the test approach across functional, performance, and security perspectives' in text, "expected to find: " + '2. **Create strategy** — Plan the test approach across functional, performance, and security perspectives'[:80]


def test_signal_180():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/typescript-pro/SKILL.md')
    assert 'description: Implements advanced TypeScript type systems, creates custom type guards, utility types, and branded types, and configures tRPC for end-to-end type safety. Use when building TypeScript app' in text, "expected to find: " + 'description: Implements advanced TypeScript type systems, creates custom type guards, utility types, and branded types, and configures tRPC for end-to-end type safety. Use when building TypeScript app'[:80]


def test_signal_181():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/typescript-pro/SKILL.md')
    assert '5. **Test types** - Confirm type coverage with a tool like `type-coverage`; validate that all public APIs have explicit return types; iterate on steps 3–4 until all checks pass' in text, "expected to find: " + '5. **Test types** - Confirm type coverage with a tool like `type-coverage`; validate that all public APIs have explicit return types; iterate on steps 3–4 until all checks pass'[:80]


def test_signal_182():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/typescript-pro/SKILL.md')
    assert '3. **Implement with type safety** - Write type guards, discriminated unions, conditional types; run `tsc --noEmit` to catch type errors before proceeding' in text, "expected to find: " + '3. **Implement with type safety** - Write type guards, discriminated unions, conditional types; run `tsc --noEmit` to catch type errors before proceeding'[:80]


def test_signal_183():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert-js/SKILL.md')
    assert 'description: Creates Vue 3 components, builds vanilla JS composables, configures Vite projects, and sets up routing and state management using JavaScript only — no TypeScript. Generates JSDoc-typed co' in text, "expected to find: " + 'description: Creates Vue 3 components, builds vanilla JS composables, configures Vite projects, and sets up routing and state management using JavaScript only — no TypeScript. Generates JSDoc-typed co'[:80]


def test_signal_184():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert-js/SKILL.md')
    assert '3. **Annotate** — Add comprehensive JSDoc comments (`@typedef`, `@param`, `@returns`, `@type`) for full type coverage; then run ESLint with the JSDoc plugin (`eslint-plugin-jsdoc`) to verify coverage ' in text, "expected to find: " + '3. **Annotate** — Add comprehensive JSDoc comments (`@typedef`, `@param`, `@returns`, `@type`) for full type coverage; then run ESLint with the JSDoc plugin (`eslint-plugin-jsdoc`) to verify coverage '[:80]


def test_signal_185():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert-js/SKILL.md')
    assert '4. **Test** — Verify with Vitest using JavaScript files; confirm JSDoc coverage on all public APIs; if tests fail, revisit the relevant composable or component, correct the logic or annotation, and re' in text, "expected to find: " + '4. **Test** — Verify with Vitest using JavaScript files; confirm JSDoc coverage on all public APIs; if tests fail, revisit the relevant composable or component, correct the logic or annotation, and re'[:80]


def test_signal_186():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert/SKILL.md')
    assert 'description: Builds Vue 3 components with Composition API patterns, configures Nuxt 3 SSR/SSG projects, sets up Pinia stores, scaffolds Quasar/Capacitor mobile apps, implements PWA features, and optim' in text, "expected to find: " + 'description: Builds Vue 3 components with Composition API patterns, configures Nuxt 3 SSR/SSG projects, sets up Pinia stores, scaffolds Quasar/Capacitor mobile apps, implements PWA features, and optim'[:80]


def test_signal_187():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert/SKILL.md')
    assert '6. **Test** - Write component tests with Vue Test Utils and Vitest. If tests fail: inspect failure output, identify whether the root cause is a component bug or an incorrect test assertion, fix accord' in text, "expected to find: " + '6. **Test** - Write component tests with Vue Test Utils and Vitest. If tests fail: inspect failure output, identify whether the root cause is a component bug or an incorrect test assertion, fix accord'[:80]


def test_signal_188():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vue-expert/SKILL.md')
    assert '4. **Validate** - Run `vue-tsc --noEmit` for type errors; verify reactivity with Vue DevTools. If type errors are found: fix each issue and re-run `vue-tsc --noEmit` until the output is clean before p' in text, "expected to find: " + '4. **Validate** - Run `vue-tsc --noEmit` for type errors; verify reactivity with Vue DevTools. If type errors are found: fix each issue and re-run `vue-tsc --noEmit` until the output is clean before p'[:80]


def test_signal_189():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/websocket-engineer/SKILL.md')
    assert '4. **Validate locally** — Test connection handling, auth, and room behavior before scaling (e.g., `npx wscat -c ws://localhost:3000`); confirm auth rejection on missing/invalid tokens, room join/leave' in text, "expected to find: " + '4. **Validate locally** — Test connection handling, auth, and room behavior before scaling (e.g., `npx wscat -c ws://localhost:3000`); confirm auth rejection on missing/invalid tokens, room join/leave'[:80]


def test_signal_190():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/websocket-engineer/SKILL.md')
    assert '5. **Scale** — Verify Redis connection and pub/sub round-trip before enabling the adapter; configure sticky sessions and confirm with test connections across multiple instances; set up load balancing' in text, "expected to find: " + '5. **Scale** — Verify Redis connection and pub/sub round-trip before enabling the adapter; configure sticky sessions and confirm with test connections across multiple instances; set up load balancing'[:80]


def test_signal_191():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/websocket-engineer/SKILL.md')
    assert '6. **Monitor** — Track connections, latency, throughput, error rates; add alerts for connection-count spikes and error-rate thresholds' in text, "expected to find: " + '6. **Monitor** — Track connections, latency, throughput, error rates; add alerts for connection-count spikes and error-rate thresholds'[:80]


def test_signal_192():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-pro/SKILL.md')
    assert 'description: Develops custom WordPress themes and plugins, creates and registers Gutenberg blocks and block patterns, configures WooCommerce stores, implements WordPress REST API endpoints, applies se' in text, "expected to find: " + 'description: Develops custom WordPress themes and plugins, creates and registers Gutenberg blocks and block patterns, configures WooCommerce stores, implements WordPress REST API endpoints, applies se'[:80]


def test_signal_193():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-pro/SKILL.md')
    assert '6. **Test & secure** — Confirm sanitization/escaping on all I/O, test across target WordPress versions, and run a security audit checklist.' in text, "expected to find: " + '6. **Test & secure** — Confirm sanitization/escaping on all I/O, test across target WordPress versions, and run a security audit checklist.'[:80]


def test_signal_194():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-pro/SKILL.md')
    assert "if ( ! isset( $_POST['my_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_nonce'] ) ), 'my_action' ) ) {" in text, "expected to find: " + "if ( ! isset( $_POST['my_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_nonce'] ) ), 'my_action' ) ) {"[:80]

