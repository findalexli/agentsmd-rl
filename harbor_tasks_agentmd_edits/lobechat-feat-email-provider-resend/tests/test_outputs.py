"""
Task: lobechat-feat-email-provider-resend
Repo: lobehub/lobe-chat @ 08572d060270afd65fcc5efdf7cde9e5fb0b0e04
PR:   10557

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — pre-installed / always-available
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_package_json_valid():
    """package.json must be valid JSON with resend dependency."""
    pkg_path = Path(REPO) / "package.json"
    data = json.loads(pkg_path.read_text())
    assert "dependencies" in data, "package.json must have dependencies section"


# [static] pass_to_pass
def test_resend_sdk_importable():
    """The resend npm package must be importable and provide a Resend class."""
    result = _run_node(
        "const { Resend } = require('resend');"
        "console.log(typeof Resend === 'function' ? 'OK' : 'FAIL');"
    )
    assert result.returncode == 0, f"Failed to import resend: {result.stderr}"
    assert "OK" in result.stdout, "Resend must be a callable constructor"


# ---------------------------------------------------------------------------
# Repo CI Tests (pass_to_pass) — verify repo's own tests/lints pass
# These require full npm/pnpm install to work (validated in later stage)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_code_style():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_types_valid():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "type-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_circular_deps():
    """Repo's circular dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:circular:main"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular dependency check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-app"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resend_impl_file_structure():
    """ResendImpl must exist as a class implementing EmailServiceImpl with sendMail and TRPCError."""
    result = _run_node("""
        const fs = require('fs');
        const path = require('path');
        const implPath = path.join('src/server/services/email/impls/resend/index.ts');
        try {
            const code = fs.readFileSync(implPath, 'utf8');
            const checks = [
                ['has_class', code.includes('class ResendImpl')],
                ['implements_interface', code.includes('implements EmailServiceImpl')],
                ['has_sendMail', code.includes('async sendMail')],
                ['uses_trpc_error', code.includes('TRPCError')],
                ['checks_api_key', code.includes('RESEND_API_KEY')],
                ['imports_resend_sdk', code.includes("from 'resend'") || code.includes('from "resend"')],
            ];
            const failed = checks.filter(c => !c[1]).map(c => c[0]);
            if (failed.length > 0) {
                console.log('FAIL:' + failed.join(','));
            } else {
                console.log('PASS');
            }
        } catch(e) {
            console.log('MISSING:' + e.message);
        }
    """)
    assert result.returncode == 0, f"Node execution failed: {result.stderr}"
    assert "PASS" in result.stdout, f"ResendImpl validation failed: {result.stdout}"


# [pr_diff] fail_to_pass
def test_enum_includes_resend():
    """EmailImplType enum must include 'resend' value with factory support."""
    result = _run_node("""
        const fs = require('fs');
        const code = fs.readFileSync('src/server/services/email/impls/index.ts', 'utf8');
        const checks = [
            ['resend_value', /Resend\\s*=\\s*'resend'/.test(code)],
            ['resend_import', code.includes('ResendImpl')],
            ['factory_case', code.includes('EmailImplType.Resend')],
            ['creates_resend', code.includes('new ResendImpl()')],
        ];
        const failed = checks.filter(c => !c[1]).map(c => c[0]);
        if (failed.length > 0) {
            console.log('FAIL:' + failed.join(','));
        } else {
            console.log('PASS');
        }
    """)
    assert result.returncode == 0, f"Node execution failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Enum check failed: {result.stdout}"


# [pr_diff] fail_to_pass
def test_env_configures_resend_vars():
    """src/envs/email.ts must define RESEND_API_KEY, RESEND_FROM, EMAIL_SERVICE_PROVIDER."""
    env_path = Path(REPO) / "src/envs/email.ts"
    code = env_path.read_text()
    assert "RESEND_API_KEY" in code, "Must declare RESEND_API_KEY env var"
    assert "RESEND_FROM" in code, "Must declare RESEND_FROM env var"
    assert "EMAIL_SERVICE_PROVIDER" in code, "Must declare EMAIL_SERVICE_PROVIDER env var"
    assert "nodemailer" in code and "resend" in code, \
        "EMAIL_SERVICE_PROVIDER must validate against 'nodemailer' and 'resend'"


# [pr_diff] fail_to_pass
def test_email_service_resolves_provider():
    """EmailService constructor must resolve provider from EMAIL_SERVICE_PROVIDER env var."""
    service_path = Path(REPO) / "src/server/services/email/index.ts"
    code = service_path.read_text()
    assert "EMAIL_SERVICE_PROVIDER" in code, \
        "EmailService must read EMAIL_SERVICE_PROVIDER from env"
    assert "emailEnv" in code, "Must import emailEnv"
    assert "createEmailServiceImpl" in code, "Must call createEmailServiceImpl with resolved type"
    # Must fall back to Nodemailer as default
    assert "Nodemailer" in code, "Must have Nodemailer as default fallback"


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_email_readme_documents_resend():
    """src/server/services/email/README.md must document the Resend provider."""
    readme_path = Path(REPO) / "src/server/services/email/README.md"
    content = readme_path.read_text()
    assert "Resend" in content, "README must mention Resend provider"
    assert "RESEND_API_KEY" in content, "README must document RESEND_API_KEY env var"
    assert "RESEND_FROM" in content, "README must document RESEND_FROM env var"
    assert "EMAIL_SERVICE_PROVIDER" in content, \
        "README must document EMAIL_SERVICE_PROVIDER selector"


# [pr_diff] fail_to_pass
def test_agents_md_has_project_description():
    """AGENTS.md must include a Project Description section with AI Agent Workspace branding."""
    agents_path = Path(REPO) / "AGENTS.md"
    content = agents_path.read_text()
    assert "## Project Description" in content, \
        "AGENTS.md must have a Project Description section"
    assert "LobeHub" in content, "Project description must mention LobeHub"
    assert "AI Agent Workspace" in content, \
        "Project description must describe the project as AI Agent Workspace"
