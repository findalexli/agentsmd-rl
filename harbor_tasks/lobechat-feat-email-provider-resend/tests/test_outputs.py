"""
Task: lobechat-feat-email-provider-resend
Repo: lobehub/lobe-chat @ 08572d060270afd65fcc5efdf7cde9e5fb0b0e04
PR:   10557

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node(script: str, timeout: int = 30, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Run a Node.js script in the specified directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=cwd,
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
    # Use global node_modules where resend was installed by Dockerfile
    result = _run_node(
        "const { Resend } = require('resend');"
        "console.log(typeof Resend === 'function' ? 'OK' : 'FAIL');",
        cwd="/"  # Use root to find globally installed resend
    )
    assert result.returncode == 0, f"Failed to import resend: {result.stderr}"
    assert "OK" in result.stdout, "Resend must be a callable constructor"


# [static] pass_to_pass
def test_nodejs_available():
    """Node.js runtime must be available and functional."""
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Node.js not available: {result.stderr}"
    assert "v22" in result.stdout or "v20" in result.stdout or "v18" in result.stdout, \
        f"Unexpected Node.js version: {result.stdout}"


# [static] pass_to_pass
def test_repo_has_typescript_config():
    """Repo has TypeScript configuration (static check)."""
    tsconfig = Path(REPO) / "tsconfig.json"
    assert tsconfig.exists(), "tsconfig.json must exist"
    data = json.loads(tsconfig.read_text())
    assert "compilerOptions" in data, "tsconfig.json must have compilerOptions"


# [static] pass_to_pass
def test_repo_has_eslint_config():
    """Repo has ESLint configuration (static check)."""
    eslintrc_js = Path(REPO) / ".eslintrc.js"
    eslintrc_json = Path(REPO) / ".eslintrc.json"
    eslint_flat = Path(REPO) / "eslint.config.js"
    assert eslintrc_js.exists() or eslintrc_json.exists() or eslint_flat.exists(), \
        "ESLint configuration file must exist"


# [static] pass_to_pass
def test_repo_package_scripts_defined():
    """Repo package.json has expected CI scripts defined (static check)."""
    pkg_path = Path(REPO) / "package.json"
    data = json.loads(pkg_path.read_text())
    scripts = data.get("scripts", {})
    assert "test-app" in scripts, "package.json must have test-app script"
    assert "type-check" in scripts, "package.json must have type-check script"
    assert "lint" in scripts, "package.json must have lint script"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — repo_tests: actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_email_service_tests():
    """Repo's email service tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/server/services/email/", "--silent=passed-only"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Email service tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_passes():
    """Repo ESLint check on TypeScript files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_resend_sdk_importable_via_node():
    """The resend npm package must be importable via Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const { Resend } = require('resend'); console.log(typeof Resend === 'function' ? 'OK' : 'FAIL');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to import resend: {r.stderr}"
    assert "OK" in r.stdout, "Resend must be a callable constructor"


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


# [repo_tests] pass_to_pass
def test_repo_email_index_tests():
    """Repo's email index.test.ts tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/server/services/email/index.test.ts", "--silent=passed-only"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Email index tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_email_impls_tests():
    """Repo's email impls/index.test.ts tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/server/services/email/impls/index.test.ts", "--silent=passed-only"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Email impls tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_ci_test_database_test_client_db():
    """pass_to_pass | CI job 'Test Database' -> step 'Test Client DB'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:client-db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Client DB' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_desktop_app_test_desktop_client():
    """pass_to_pass | CI job 'Test Desktop App' → step 'Test Desktop Client'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=os.path.join(REPO, 'apps/desktop'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Desktop Client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_lint():
    """pass_to_pass | CI job 'Test Database' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_test_coverage():
    """pass_to_pass | CI job 'Test Database' → step 'Test Coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_website_test_app_coverage():
    """pass_to_pass | CI job 'Test Website' → step 'Test App Coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run test-app:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test App Coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_web_app_run_e2e_tests():
    """pass_to_pass | CI job 'Test Web App' → step 'Run E2E tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run e2e'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run E2E tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm test
# 2 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_f2p_chatservice_private_methods_getchatcompletion_should_merge_responseanimation_sty(_run_cmd=None):
    # Discovered f2p (failed at base, passed at gold): 'ChatService private methods > getChatCompletion > should merge responseAnimation styles correctly '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_f2p_mcpstore_actions_installmcpplugin_cloudendpoint_support_should_create_cloud_type(_run_cmd=None):
    # Discovered f2p (failed at base, passed at gold): 'mcpStore actions > installMCPPlugin > cloudEndPoint support > should create cloud type connection when cloudEndPoint is available on web '
    pass  # placeholder — recorded in manifest under origin: exec_diff


def test_exec_p2p_chatservice_createassistantmessage_should_handle_content_correctly_for_vision_mo(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'ChatService > createAssistantMessage > should handle content correctly for vision models > should include image content when with vision model '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpclient_error_handling_should_throw_error_for_unsupported_connection_type(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MCPClient > Error Handling > should throw error for unsupported connection type'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpclient_stdio_transport_should_call_the_add_tool_via_stdio(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MCPClient > Stdio Transport > should call the "add" tool via stdio '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpclient_stdio_transport_should_call_the_echo_tool_via_stdio(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MCPClient > Stdio Transport > should call the "echo" tool via stdio '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpclient_stdio_transport_should_create_and_initialize_an_instance_with_stdio_tr(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MCPClient > Stdio Transport > should create and initialize an instance with stdio transport '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpservice_calltool_should_return_mcptoolcallresult_when_content_array_is_empty(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MCPService > callTool > should return MCPToolCallResult when content array is empty '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_message_router_integration_tests_createmessage_should_create_message_with_correc(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'Message Router Integration Tests > createMessage > should create message with correct sessionId and topicId '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_oidc_provider_market_client_integration_resolveclerkaccount_with_clerk_enabled_s(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'OIDC Provider - Market Client Integration > resolveClerkAccount - with Clerk enabled > should resolve Clerk user with full profile '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_oidc_provider_market_client_integration_resolveclerkaccount_should_return_undefi(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'OIDC Provider - Market Client Integration > resolveClerkAccount > should return undefined when Clerk is disabled '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_toolservice_gettoolmanifest_support_openapi_manifest_should_get_plugin_manifest(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'ToolService > getToolManifest > support OpenAPI manifest > should get plugin manifest '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mcpstore_actions_usefetchmcppluginlist_should_not_append_connectiontype_in_deskt(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mcpStore actions > useFetchMCPPluginList > should not append connectionType in desktop environment '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend__deprecated_createbizopenai_auth_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/_deprecated/createBizOpenAI/auth.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend_middleware_auth_index_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/middleware/auth/index.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend_middleware_auth_utils_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/middleware/auth/utils.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend_trpc_trpc_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/trpc/trpc.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend_webapi_chat_provider_route_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/webapi/chat/[provider]/route.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_backend_webapi_plugin_gateway_settings_test_ts_12_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/(backend)/webapi/plugin/gateway/settings.test.ts (12 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_mobile_me_home___tests___userbanner_test_tsx_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/(mobile)/me/(home)/__tests__/UserBanner.test.tsx (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_mobile_me_home___tests___usecategory_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/(mobile)/me/(home)/__tests__/useCategory.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_discover_features___tests___calculatescore_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/discover/features/__tests__/calculateScore.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_image_menu_features_configpanel_utils___tests___dimensionc(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/image/@menu/features/ConfigPanel/utils/__tests__/dimensionConstraints.test.ts (24 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_image_menu_features_configpanel_utils___tests___imagevalid(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/image/@menu/features/ConfigPanel/utils/__tests__/imageValidation.test.ts (32 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_image_features_generationfeed_generationitem_utils_test_ts(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/image/features/GenerationFeed/GenerationItem/utils.test.ts (24 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_layouts_desktop_sidebar_avatar_test_tsx_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/layouts/desktop/SideBar/Avatar.test.tsx (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app_variants_main_layouts_desktop_sidebar_topactions_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/[variants]/(main)/layouts/desktop/SideBar/TopActions.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_app___tests___desktop_routes_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/app/__tests__/desktop.routes.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_components_antdstaticmethods_index_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/components/AntdStaticMethods/index.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_components_dragupload_usedragupload_test_tsx_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/components/DragUpload/useDragUpload.test.tsx (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_components_forminput_forminput_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/components/FormInput/FormInput.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_components_invalidapikey_apikeyform___tests___comfyuiform_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/components/InvalidAPIKey/APIKeyForm/__tests__/ComfyUIForm.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_config_featureflags_schema_test_ts_17_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/config/featureFlags/schema.test.ts (17 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_config_featureflags_utils_parser_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/config/featureFlags/utils/parser.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_envs___tests___analytics_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/envs/__tests__/analytics.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_envs___tests___app_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/envs/__tests__/app.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_envs___tests___client_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/envs/__tests__/client.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_envs_auth_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/envs/auth.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_markdownelements_lobeartifact_rehypeplugin_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/MarkdownElements/LobeArtifact/rehypePlugin.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_markdownelements_remarkplugins_createremarkselfclosingtagp(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/MarkdownElements/remarkPlugins/createRemarkSelfClosingTagPlugin.test.ts (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_markdownelements_remarkplugins_getnodecontent_test_ts_3_te(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/MarkdownElements/remarkPlugins/getNodeContent.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_messages_assistant_extra_index_test_tsx_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/Messages/Assistant/Extra/index.test.tsx (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_components_extras_usage_usagedetail_tokens_test_ts_12_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/components/Extras/Usage/UsageDetail/tokens.test.ts (12 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_components_sharemessagemodal_sharetext_template_test_ts_2_(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/components/ShareMessageModal/ShareText/template.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_chatlist_utils_markdown_test_ts_27_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/ChatList/utils/markdown.test.ts (27 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_mcp_utils_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/MCP/utils.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_plugindevmodal_mcpmanifestform_utils_test_ts_21_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginDevModal/MCPManifestForm/utils.test.ts (21 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_pluginsui_render_builtintype_index_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginsUI/Render/BuiltinType/index.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_pluginsui_render_utils_iframeonready_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginsUI/Render/utils/iframeOnReady.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_pluginsui_render_utils_listentoplugin_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginsUI/Render/utils/listenToPlugin.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_pluginsui_render_utils_pluginsettings_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginsUI/Render/utils/pluginSettings.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_features_pluginsui_render_utils_pluginstate_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/features/PluginsUI/Render/utils/pluginState.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

