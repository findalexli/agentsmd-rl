"""Behavioral checks for opentrons-chorecursor-convert-rules-to-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentrons")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ai-server.mdc')
    assert '.cursor/rules/ai-server.mdc' in text, "expected to find: " + '.cursor/rules/ai-server.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/ai-server/SKILL.md')
    assert '`opentrons-ai-server` is a standalone FastAPI service for Opentrons AI — protocol generation, chat completions, and related AI features. It is **not** part of the monorepo build system; it has its own' in text, "expected to find: " + '`opentrons-ai-server` is a standalone FastAPI service for Opentrons AI — protocol generation, chat completions, and related AI features. It is **not** part of the monorepo build system; it has its own'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/ai-server/SKILL.md')
    assert 'description: Conventions for the opentrons-ai-server FastAPI service — project structure, uv dependency management, settings, testing, Docker, and deployment. Use when working with files in opentrons-' in text, "expected to find: " + 'description: Conventions for the opentrons-ai-server FastAPI service — project structure, uv dependency management, settings, testing, Docker, and deployment. Use when working with files in opentrons-'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/ai-server/SKILL.md')
    assert 'Auth0 JWT verification via `api/integration/auth.py`. Config: `auth0_domain`, `auth0_api_audience`, `auth0_issuer`, `auth0_algorithms` in Settings.' in text, "expected to find: " + 'Auth0 JWT verification via `api/integration/auth.py`. Config: `auth0_domain`, `auth0_api_audience`, `auth0_issuer`, `auth0_algorithms` in Settings.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/analyses-snapshot-testing/SKILL.md')
    assert 'description: Conventions for the analyses snapshot testing framework in analyses-snapshot-testing/. Use when working with protocol analysis snapshots, adding protocols, updating snapshots, or running ' in text, "expected to find: " + 'description: Conventions for the analyses snapshot testing framework in analyses-snapshot-testing/. Use when working with protocol analysis snapshots, adding protocols, updating snapshots, or running '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/analyses-snapshot-testing/SKILL.md')
    assert '{Robot}_{Status}_{Version}_{Source}_{Pipettes}_{Modules}_{Overrides}\\_{Description}' in text, "expected to find: " + '{Robot}_{Status}_{Version}_{Source}_{Pipettes}_{Modules}_{Overrides}\\_{Description}'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/analyses-snapshot-testing/SKILL.md')
    assert 'name: analyses-snapshot-testing' in text, "expected to find: " + 'name: analyses-snapshot-testing'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/components-testing/SKILL.md')
    assert 'description: ProtocolDeck component testing environment using built packages with Playwright visual snapshots in components-testing/. Use when working with component integration tests, package linking' in text, "expected to find: " + 'description: ProtocolDeck component testing environment using built packages with Playwright visual snapshots in components-testing/. Use when working with component integration tests, package linking'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/components-testing/SKILL.md')
    assert '| Target                        | Description                                             |' in text, "expected to find: " + '| Target                        | Description                                             |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/components-testing/SKILL.md')
    assert '| `make setup`                  | Complete setup: pnpm install, build packages, link them |' in text, "expected to find: " + '| `make setup`                  | Complete setup: pnpm install, build packages, link them |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/css-modules/SKILL.md')
    assert 'description: CSS Modules conventions, Stylelint rules, design tokens (spacing, colors, typography, border-radius), and patterns for the Opentrons monorepo. Use when working with .module.css files or s' in text, "expected to find: " + 'description: CSS Modules conventions, Stylelint rules, design tokens (spacing, colors, typography, border-radius), and patterns for the Opentrons monorepo. Use when working with .module.css files or s'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/css-modules/SKILL.md')
    assert '| Property                                     | Use token?                  | Example                        |' in text, "expected to find: " + '| Property                                     | Use token?                  | Example                        |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/css-modules/SKILL.md')
    assert '| `color`, `background-color`, `border-color`  | **Yes**                     | `var(--blue-50)`               |' in text, "expected to find: " + '| `color`, `background-color`, `border-color`  | **Yes**                     | `var(--blue-50)`               |'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/e2e-testing/SKILL.md')
    assert 'description: E2E testing conventions for Protocol Designer and Labware Library using Playwright + pytest in e2e-testing/. Use when writing, running, or modifying end-to-end tests, page objects, or Pla' in text, "expected to find: " + 'description: E2E testing conventions for Protocol Designer and Labware Library using Playwright + pytest in e2e-testing/. Use when writing, running, or modifying end-to-end tests, page objects, or Pla'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/e2e-testing/SKILL.md')
    assert '| Fixture                    | Scope    | Purpose                                                                                        |' in text, "expected to find: " + '| Fixture                    | Scope    | Purpose                                                                                        |'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/e2e-testing/SKILL.md')
    assert '| `pd_base_url`              | session  | Resolves PD URL; starts local preview server when `TEST_ENV=local`                             |' in text, "expected to find: " + '| `pd_base_url`              | session  | Resolves PD URL; starts local preview server when `TEST_ENV=local`                             |'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/locize-sync/SKILL.md')
    assert 'description: Locize i18n synchronization workflow for pushing and downloading translations in the Opentrons monorepo. Use when working with locize_sync.py, localization files in app/src/assets/localiz' in text, "expected to find: " + 'description: Locize i18n synchronization workflow for pushing and downloading translations in the Opentrons monorepo. Use when working with locize_sync.py, localization files in app/src/assets/localiz'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/locize-sync/SKILL.md')
    assert 'name: locize-sync' in text, "expected to find: " + 'name: locize-sync'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/opentrons-typescript/SKILL.md')
    assert 'description: TypeScript conventions, React patterns, testing, styling, and import rules for the Opentrons monorepo JS/TS packages. Use when working with TypeScript or React files in app/, components/,' in text, "expected to find: " + 'description: TypeScript conventions, React patterns, testing, styling, and import rules for the Opentrons monorepo JS/TS packages. Use when working with TypeScript or React files in app/, components/,'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/opentrons-typescript/SKILL.md')
    assert '| Target                            | Description                                                        |' in text, "expected to find: " + '| Target                            | Description                                                        |'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/opentrons-typescript/SKILL.md')
    assert '| `make setup-js`                   | Install all JS deps (`yarn`)                                       |' in text, "expected to find: " + '| `make setup-js`                   | Install all JS deps (`yarn`)                                       |'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/protocol-designer/SKILL.md')
    assert 'Protocol Designer (PD) is a React + Redux + React Router + TypeScript web app for designing Opentrons liquid-handling protocols. It depends on `@opentrons/components`, `@opentrons/shared-data`, and `@' in text, "expected to find: " + 'Protocol Designer (PD) is a React + Redux + React Router + TypeScript web app for designing Opentrons liquid-handling protocols. It depends on `@opentrons/components`, `@opentrons/shared-data`, and `@'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/protocol-designer/SKILL.md')
    assert 'description: Protocol Designer (PD) application architecture, Redux slices, step/timeline system, domain concepts, and dev workflow. Use when working with files in protocol-designer/ or discussing PD ' in text, "expected to find: " + 'description: Protocol Designer (PD) application architecture, Redux slices, step/timeline system, domain concepts, and dev workflow. Use when working with files in protocol-designer/ or discussing PD '[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/protocol-designer/SKILL.md')
    assert 'General TypeScript, React, styling, testing, import, and tooling conventions are in the `opentrons-typescript` skill. This file covers only what is unique to the `protocol-designer` package.' in text, "expected to find: " + 'General TypeScript, React, styling, testing, import, and tooling conventions are in the `opentrons-typescript` skill. This file covers only what is unique to the `protocol-designer` package.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/react-component-creation/SKILL.md')
    assert 'General TypeScript, React, styling, testing, and import conventions are in the `opentrons-typescript` skill. PD-specific architecture is in the `protocol-designer` skill. CSS Modules details are in th' in text, "expected to find: " + 'General TypeScript, React, styling, testing, and import conventions are in the `opentrons-typescript` skill. PD-specific architecture is in the `protocol-designer` skill. CSS Modules details are in th'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/react-component-creation/SKILL.md')
    assert 'description: Component creation checklist and ai-client-specific patterns for React .tsx files in opentrons-ai-client/ and protocol-designer/. Use when creating new React components in these packages.' in text, "expected to find: " + 'description: Component creation checklist and ai-client-specific patterns for React .tsx files in opentrons-ai-client/ and protocol-designer/. Use when creating new React components in these packages.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/react-component-creation/SKILL.md')
    assert "import type { ChatData } from '/ai-client/resources/types'" in text, "expected to find: " + "import type { ChatData } from '/ai-client/resources/types'"[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/robot-python-projects/SKILL.md')
    assert 'description: Guidelines for robot Python projects — api/, robot-server/, hardware/, auth-server/, shared-data/, server-utils/, system-server/, update-server/, usb-bridge/, g-code-testing/. Use when wo' in text, "expected to find: " + 'description: Guidelines for robot Python projects — api/, robot-server/, hardware/, auth-server/, shared-data/, server-utils/, system-server/, update-server/, usb-bridge/, g-code-testing/. Use when wo'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/robot-python-projects/SKILL.md')
    assert '| Project                 | Directory         | Description                                          |' in text, "expected to find: " + '| Project                 | Directory         | Description                                          |'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/robot-python-projects/SKILL.md')
    assert '| `opentrons`             | `api/`            | Core Opentrons Python API for protocol execution     |' in text, "expected to find: " + '| `opentrons`             | `api/`            | Core Opentrons Python API for protocol execution     |'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/static-deploy/SKILL.md')
    assert 'description: Conventions for static deploy automation Python CLIs in scripts/static-deploy/. Use when working with deployment scripts, AWS S3/CloudFront automation, or Python CLIs in the static-deploy' in text, "expected to find: " + 'description: Conventions for static deploy automation Python CLIs in scripts/static-deploy/. Use when working with deployment scripts, AWS S3/CloudFront automation, or Python CLIs in the static-deploy'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/static-deploy/SKILL.md')
    assert 'name: static-deploy' in text, "expected to find: " + 'name: static-deploy'[:80]

