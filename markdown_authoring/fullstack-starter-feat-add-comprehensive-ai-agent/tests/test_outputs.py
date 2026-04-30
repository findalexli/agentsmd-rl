"""Behavioral checks for fullstack-starter-feat-add-comprehensive-ai-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fullstack-starter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/backend-development/SKILL.md')
    assert 'description: Comprehensive backend development skill for building scalable backend systems using Python (FastAPI), Postgres, Redis, and more. Includes API design, database optimization, security imple' in text, "expected to find: " + 'description: Comprehensive backend development skill for building scalable backend systems using Python (FastAPI), Postgres, Redis, and more. Includes API design, database optimization, security imple'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/backend-development/SKILL.md')
    assert 'This skill provides expert guidance for building robust, scalable, and secure backend systems, primarily focusing on the Python/FastAPI ecosystem used in this project.' in text, "expected to find: " + 'This skill provides expert guidance for building robust, scalable, and secure backend systems, primarily focusing on the Python/FastAPI ecosystem used in this project.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/backend-development/SKILL.md')
    assert '- **Schema Design**: Normalized relationships, indexing strategies, and migration management (Alembic).' in text, "expected to find: " + '- **Schema Design**: Normalized relationships, indexing strategies, and migration management (Alembic).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/cache-components/SKILL.md')
    assert "**DETECTION**: At the start of a session in a Next.js project, check for `cacheComponents: true` in `next.config`. If enabled, this skill's patterns should guide all component authoring, data fetching" in text, "expected to find: " + "**DETECTION**: At the start of a session in a Next.js project, check for `cacheComponents: true` in `next.config`. If enabled, this skill's patterns should guide all component authoring, data fetching"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/cache-components/SKILL.md')
    assert '**PROACTIVE ACTIVATION**: Use this skill automatically when working in Next.js projects that have `cacheComponents: true` in their `next.config.ts` or `next.config.js`.' in text, "expected to find: " + '**PROACTIVE ACTIVATION**: Use this skill automatically when working in Next.js projects that have `cacheComponents: true` in their `next.config.ts` or `next.config.js`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/cache-components/SKILL.md')
    assert 'description: Expert guidance for Next.js Cache Components and Partial Prerendering (PPR). PROACTIVE ACTIVATION when cacheComponents config is detected.' in text, "expected to find: " + 'description: Expert guidance for Next.js Cache Components and Partial Prerendering (PPR). PROACTIVE ACTIVATION when cacheComponents config is detected.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/component-refactoring/SKILL.md')
    assert '**Complexity Threshold**: Components with **cyclomatic complexity > 50** or **line count > 300** should be candidates for refactoring.' in text, "expected to find: " + '**Complexity Threshold**: Components with **cyclomatic complexity > 50** or **line count > 300** should be candidates for refactoring.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/component-refactoring/SKILL.md')
    assert 'description: Refactor high-complexity React components. Use when complexity metrics are high or to split monolithic UI.' in text, "expected to find: " + 'description: Refactor high-complexity React components. Use when complexity metrics are high or to split monolithic UI.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/component-refactoring/SKILL.md')
    assert '- Keep the `isOpen` state locally if specific to a single component, but extract the Modal content to a separate file.' in text, "expected to find: " + '- Keep the `isOpen` state locally if specific to a single component, but extract the Modal content to a separate file.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/create-pr/SKILL.md')
    assert 'description: Automates the creation of detailed, well-formatted Pull Requests using the GitHub CLI. Parses conventional commits to generate titles and descriptions.' in text, "expected to find: " + 'description: Automates the creation of detailed, well-formatted Pull Requests using the GitHub CLI. Parses conventional commits to generate titles and descriptions.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/create-pr/SKILL.md')
    assert '- The current branch must have commits that are not yet on the remote (or a corresponding remote branch).' in text, "expected to find: " + '- The current branch must have commits that are not yet on the remote (or a corresponding remote branch).'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/create-pr/SKILL.md')
    assert 'This skill streamlines the Pull Request process, ensuring consistent and high-quality PR descriptions.' in text, "expected to find: " + 'This skill streamlines the Pull Request process, ensuring consistent and high-quality PR descriptions.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/devops-iac-engineer/SKILL.md')
    assert 'description: Expert guidance for designing, implementing, and maintaining cloud infrastructure using Experience in Infrastructure as Code (IaC) principles. Use this skill for architecting cloud soluti' in text, "expected to find: " + 'description: Expert guidance for designing, implementing, and maintaining cloud infrastructure using Experience in Infrastructure as Code (IaC) principles. Use this skill for architecting cloud soluti'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/devops-iac-engineer/SKILL.md')
    assert 'This skill provides expertise in designing and managing cloud infrastructure using Infrastructure as Code (IaC) and DevOps/SRE best practices.' in text, "expected to find: " + 'This skill provides expertise in designing and managing cloud infrastructure using Infrastructure as Code (IaC) and DevOps/SRE best practices.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/devops-iac-engineer/SKILL.md')
    assert '- **GitOps**: Code repository is the single source of truth. Changes are applied via PRs and automated pipelines.' in text, "expected to find: " + '- **GitOps**: Code repository is the single source of truth. Changes are applied via PRs and automated pipelines.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-router-creator/SKILL.md')
    assert 'description: Guide for creating and organizing FastAPI routes using a file-based routing system or modular router pattern. Helps organize complex API structures.' in text, "expected to find: " + 'description: Guide for creating and organizing FastAPI routes using a file-based routing system or modular router pattern. Helps organize complex API structures.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-router-creator/SKILL.md')
    assert 'For a Next.js-like experience where file structure dictates URLs. (Requires `fastapi-router` library or custom walker).' in text, "expected to find: " + 'For a Next.js-like experience where file structure dictates URLs. (Requires `fastapi-router` library or custom walker).'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-router-creator/SKILL.md')
    assert '3.  **Dependencies**: Apply dependencies (like auth) at the router level if they apply to all endpoints in that router.' in text, "expected to find: " + '3.  **Dependencies**: Apply dependencies (like auth) at the router level if they apply to all endpoints in that router.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-templates/SKILL.md')
    assert 'description: Production-ready FastAPI project templates and patterns. Use when starting new FastAPI projects, services, or adding standard components like auth, DB connection, or middleware.' in text, "expected to find: " + 'description: Production-ready FastAPI project templates and patterns. Use when starting new FastAPI projects, services, or adding standard components like auth, DB connection, or middleware.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-templates/SKILL.md')
    assert 'This skill provides production-ready templates and scaffolding patterns for FastAPI applications.' in text, "expected to find: " + 'This skill provides production-ready templates and scaffolding patterns for FastAPI applications.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/fastapi-templates/SKILL.md')
    assert 'return await item_service.create(db, obj_in=item_in, owner_id=current_user.id)' in text, "expected to find: " + 'return await item_service.create(db, obj_in=item_in, owner_id=current_user.id)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/frontend-code-review/SKILL.md')
    assert '1. **Scan**: Read the code to identify architectural patterns, hooks usage, and component structure.' in text, "expected to find: " + '1. **Scan**: Read the code to identify architectural patterns, hooks usage, and component structure.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/frontend-code-review/SKILL.md')
    assert 'description: Standardized checklist and process for reviewing frontend code (.tsx, .ts, .js).' in text, "expected to find: " + 'description: Standardized checklist and process for reviewing frontend code (.tsx, .ts, .js).'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/frontend-code-review/SKILL.md')
    assert '- [ ] **Naming**: Are variables/functions named descriptively? (e.g., `isLoading` vs `flag`)' in text, "expected to find: " + '- [ ] **Naming**: Are variables/functions named descriptively? (e.g., `isLoading` vs `flag`)'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/senior-architect/SKILL.md')
    assert 'description: Comprehensive software architecture skill for designing scalable, maintainable systems using ReactJS, NextJS, NodeJS, FastAPI, Flutter, etc. Includes system design patterns, tech stack de' in text, "expected to find: " + 'description: Comprehensive software architecture skill for designing scalable, maintainable systems using ReactJS, NextJS, NodeJS, FastAPI, Flutter, etc. Includes system design patterns, tech stack de'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/senior-architect/SKILL.md')
    assert 'This skill provides high-level architectural guidance, ensuring the system is scalable, maintainable, and aligned with business goals.' in text, "expected to find: " + 'This skill provides high-level architectural guidance, ensuring the system is scalable, maintainable, and aligned with business goals.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/senior-architect/SKILL.md')
    assert '- **Data Modeling**: Design schemas for relational (Postgres) and NoSQL (Firestore/Redis) databases.' in text, "expected to find: " + '- **Data Modeling**: Design schemas for relational (Postgres) and NoSQL (Firestore/Redis) databases.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/skill-lookup/SKILL.md')
    assert 'description: Discover, retrieve, and learn about available Agent Skills. key capability for finding tools to solve specific problems.' in text, "expected to find: " + 'description: Discover, retrieve, and learn about available Agent Skills. key capability for finding tools to solve specific problems.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/skill-lookup/SKILL.md')
    assert 'This skill allows the Agent to introspect its own capabilities and find the right tool for the job.' in text, "expected to find: " + 'This skill allows the Agent to introspect its own capabilities and find the right tool for the job.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/skill-lookup/SKILL.md')
    assert '- Agent is unsure how to perform a specialized task and wants to check if a skill exists.' in text, "expected to find: " + '- Agent is unsure how to perform a specialized task and wants to check if a skill exists.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-creator/SKILL.md')
    assert 'description: Helper for scaffolding new Terraform modules. Complements terraform-module-library by providing structure generation.' in text, "expected to find: " + 'description: Helper for scaffolding new Terraform modules. Complements terraform-module-library by providing structure generation.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-creator/SKILL.md')
    assert 'This skill assists in scaffolding new Terraform modules following the standards defined in `terraform-module-library`.' in text, "expected to find: " + 'This skill assists in scaffolding new Terraform modules following the standards defined in `terraform-module-library`.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-creator/SKILL.md')
    assert '- Use **terraform-module-library** for design patterns, best practices, and internal code logic.' in text, "expected to find: " + '- Use **terraform-module-library** for design patterns, best practices, and internal code logic.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-library/SKILL.md')
    assert 'description: Expert guidance for creating, managing, and using Terraform modules. Use this skill when the user wants to create reusable infrastructure components, standardize Terraform patterns, or ne' in text, "expected to find: " + 'description: Expert guidance for creating, managing, and using Terraform modules. Use this skill when the user wants to create reusable infrastructure components, standardize Terraform patterns, or ne'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-library/SKILL.md')
    assert '- **Variables**: Include `description` and `type` for all variables. Use `validation` blocks for constraints.' in text, "expected to find: " + '- **Variables**: Include `description` and `type` for all variables. Use `validation` blocks for constraints.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-module-library/SKILL.md')
    assert '- **State**: Do not include backend configuration in modules; state is managed by the root configuration.' in text, "expected to find: " + '- **State**: Do not include backend configuration in modules; state is managed by the root configuration.'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-state-manager/SKILL.md')
    assert 'description: Manages Terraform state operations such as importing, moving, and removing resources. Use this skill when the user needs to refactor Terraform state, import existing infrastructure, fixin' in text, "expected to find: " + 'description: Manages Terraform state operations such as importing, moving, and removing resources. Use this skill when the user needs to refactor Terraform state, import existing infrastructure, fixin'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-state-manager/SKILL.md')
    assert '2.  **Plan After**: Run `terraform plan` immediately after any state change to verify the result is a "no-op" (no changes detected) or matches expectation.' in text, "expected to find: " + '2.  **Plan After**: Run `terraform plan` immediately after any state change to verify the result is a "no-op" (no changes detected) or matches expectation.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/terraform-state-manager/SKILL.md')
    assert '# Example: terraform state mv google_storage_bucket.old_name module.storage.google_storage_bucket.new_name' in text, "expected to find: " + '# Example: terraform state mv google_storage_bucket.old_name module.storage.google_storage_bucket.new_name'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ui-ux-pro-max/SKILL.md')
    assert 'description: Advanced design intelligence for professional UI/UX. Use for implementing modern design patterns (Glassmorphism, Bento Grid), ensuring accessibility, and generating tailored design system' in text, "expected to find: " + 'description: Advanced design intelligence for professional UI/UX. Use for implementing modern design patterns (Glassmorphism, Bento Grid), ensuring accessibility, and generating tailored design system'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ui-ux-pro-max/SKILL.md')
    assert 'This skill provides professional-grade UI/UX design guidance, focusing on modern aesthetics, accessibility, and consistency.' in text, "expected to find: " + 'This skill provides professional-grade UI/UX design guidance, focusing on modern aesthetics, accessibility, and consistency.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ui-ux-pro-max/SKILL.md')
    assert '- **Motion**: Use subtle micro-animations (200-300ms) to make the UI feel alive.' in text, "expected to find: " + '- **Motion**: Use subtle micro-animations (200-300ms) to make the UI feel alive.'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/webf-native-ui-dev/SKILL.md')
    assert 'description: Develop custom native UI libraries based on Flutter widgets for WebF. Create reusable component libraries that wrap Flutter widgets as web-accessible custom elements.' in text, "expected to find: " + 'description: Develop custom native UI libraries based on Flutter widgets for WebF. Create reusable component libraries that wrap Flutter widgets as web-accessible custom elements.'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/webf-native-ui-dev/SKILL.md')
    assert "WebF allows you to render HTML/CSS using Flutter's rendering engine. This skill helps you expose complex Flutter widgets as `<custom-element>` tags usable in HTML." in text, "expected to find: " + "WebF allows you to render HTML/CSS using Flutter's rendering engine. This skill helps you expose complex Flutter widgets as `<custom-element>` tags usable in HTML."[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/webf-native-ui-dev/SKILL.md')
    assert 'This skill guides the development of custom native UI components for **WebF** (Web on Flutter). It bridges Flutter widgets to standard HTML custom elements.' in text, "expected to find: " + 'This skill guides the development of custom native UI components for **WebF** (Web on Flutter). It bridges Flutter widgets to standard HTML custom elements.'[:80]

