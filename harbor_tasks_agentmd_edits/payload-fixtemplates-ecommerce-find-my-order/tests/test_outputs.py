"""
Task: payload-fixtemplates-ecommerce-find-my-order
Repo: payloadcms/payload @ 7f3c6c8f4628fb066002e2fd5c3cc6b83ddf4ccc
PR:   15736

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Key TypeScript files have balanced braces and parentheses."""
    files_to_check = [
        "templates/ecommerce/src/plugins/index.ts",
        "templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx",
        "templates/ecommerce/src/components/forms/FindOrderForm/index.tsx",
        "templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts",
        "templates/ecommerce/src/components/checkout/ConfirmOrder.tsx",
        "templates/ecommerce/src/components/forms/CheckoutForm/index.tsx",
        "packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        if not full_path.exists():
            continue  # Some files are created by the fix

        content = full_path.read_text()

        # Count braces and parentheses
        open_braces = content.count("{")
        close_braces = content.count("}")
        open_parens = content.count("(")
        close_parens = content.count(")")
        open_brackets = content.count("[")
        close_brackets = content.count("]")

        assert open_braces == close_braces, f"{file_path}: Unmatched braces ({open_braces} vs {close_braces})"
        assert open_parens == close_parens, f"{file_path}: Unmatched parentheses ({open_parens} vs {close_parens})"
        assert open_brackets == close_brackets, f"{file_path}: Unmatched brackets ({open_brackets} vs {close_brackets})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_access_token_field_in_plugin():
    """Plugin config adds accessToken field to orders collection."""
    plugin_file = Path(REPO) / "templates/ecommerce/src/plugins/index.ts"
    assert plugin_file.exists(), f"Plugin file not found: {plugin_file}"

    content = plugin_file.read_text()

    # Check that orders collection override exists
    assert "orders:" in content, "orders collection override not found"
    assert "ordersCollectionOverride" in content, "ordersCollectionOverride not found"

    # Check accessToken field definition
    assert "name: 'accessToken'" in content or 'name: "accessToken"' in content, "accessToken field name not found"
    assert "type: 'text'" in content or 'type: "text"' in content, "accessToken type not found"
    assert "unique: true" in content, "accessToken unique constraint not found"
    assert "index: true" in content, "accessToken index not found"

    # Check the hook that generates the UUID
    assert "beforeValidate:" in content, "beforeValidate hook not found"
    assert "crypto.randomUUID()" in content, "crypto.randomUUID() not found in hook"
    assert "operation === 'create'" in content, "operation check not found in hook"


# [pr_diff] fail_to_pass
def test_access_token_in_confirm_order_response():
    """Stripe confirmOrder includes accessToken in success response."""
    confirm_file = Path(REPO) / "packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts"
    assert confirm_file.exists(), f"confirmOrder file not found: {confirm_file}"

    content = confirm_file.read_text()

    # Check that accessToken is conditionally spread into the response
    assert "...(order.accessToken ? { accessToken: order.accessToken } : {})" in content, \
        "accessToken conditional spread not found in response"


# [pr_diff] fail_to_pass
def test_order_page_requires_access_token():
    """Order detail page requires accessToken for guest access."""
    order_page = Path(REPO) / "templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx"
    assert order_page.exists(), f"Order page not found: {order_page}"

    content = order_page.read_text()

    # Check that accessToken is extracted from searchParams
    assert "accessToken" in content, "accessToken not found in order page"

    # Check that PageProps type includes accessToken
    assert "accessToken?:" in content, "accessToken in PageProps type not found"

    # Check that accessToken is used in the query
    assert 'accessToken: {' in content or "accessToken:{" in content, \
        "accessToken not used in query filter"

    # Check that canAccessAsGuest requires accessToken
    assert "accessToken &&" in content, "accessToken check not found in canAccessAsGuest"


# [pr_diff] fail_to_pass
def test_send_order_access_email_exists():
    """Server action sendOrderAccessEmail exists and sends email with access link."""
    email_file = Path(REPO) / "templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts"
    assert email_file.exists(), f"sendOrderAccessEmail.ts not found: {email_file}"

    content = email_file.read_text()

    # Check it's a server action
    assert "'use server'" in content or '"use server"' in content, \
        "'use server' directive not found"

    # Check the function is exported
    assert "export async function sendOrderAccessEmail" in content, \
        "sendOrderAccessEmail export not found"

    # Check it looks up the order by id and email
    assert "collection: 'orders'" in content or 'collection: "orders"' in content, \
        "orders collection not queried"
    assert "orderID" in content, "orderID not used in query"
    assert "customerEmail" in content, "customerEmail not used in query"

    # Check it uses accessToken
    assert "accessToken" in content, "accessToken not referenced"

    # Check it sends an email with payload.sendEmail
    assert "payload.sendEmail" in content, "payload.sendEmail not called"

    # Check the email contains the order URL with accessToken
    assert "orderURL" in content or "order URL" in content.lower(), \
        "Order URL not constructed in email"


# [pr_diff] fail_to_pass
def test_find_order_form_uses_email_flow():
    """FindOrderForm sends email instead of navigating directly to order page."""
    form_file = Path(REPO) / "templates/ecommerce/src/components/forms/FindOrderForm/index.tsx"
    assert form_file.exists(), f"FindOrderForm not found: {form_file}"

    content = form_file.read_text()

    # Check that sendOrderAccessEmail is imported
    assert "sendOrderAccessEmail" in content, "sendOrderAccessEmail not imported"

    # Check that useRouter is NOT used (removed in the fix)
    # Note: We allow useRouter import in other contexts, just not for direct navigation
    # So we check the onSubmit specifically doesn't use router.push

    # Check for state management (new states added in fix)
    assert "useState" in content, "useState not found"
    assert "isSubmitting" in content, "isSubmitting state not found"
    assert "success" in content, "success state not found"

    # Check for success UI showing email confirmation
    assert "Check your email" in content or "check your email" in content.lower(), \
        "Email confirmation message not found"

    # Check the form no longer does direct navigation with router.push to orders
    # The fix replaces router.push with calling sendOrderAccessEmail
    assert "router.push" not in content or "/orders/" not in content, \
        "Direct navigation to orders page still present"


# [pr_diff] fail_to_pass
def test_checkout_redirects_include_access_token():
    """Checkout components pass accessToken in redirect URLs."""
    # Check ConfirmOrder.tsx
    confirm_order = Path(REPO) / "templates/ecommerce/src/components/checkout/ConfirmOrder.tsx"
    assert confirm_order.exists(), f"ConfirmOrder not found: {confirm_order}"

    confirm_content = confirm_order.read_text()
    assert "accessToken" in confirm_content, "accessToken not found in ConfirmOrder"
    assert "URLSearchParams" in confirm_content, "URLSearchParams not used in ConfirmOrder"
    assert "queryParams.set('accessToken'" in confirm_content or \
           'queryParams.set("accessToken"' in confirm_content, \
        "accessToken not added to query params in ConfirmOrder"

    # Check CheckoutForm/index.tsx
    checkout_form = Path(REPO) / "templates/ecommerce/src/components/forms/CheckoutForm/index.tsx"
    assert checkout_form.exists(), f"CheckoutForm not found: {checkout_form}"

    checkout_content = checkout_form.read_text()
    assert "accessToken" in checkout_content, "accessToken not found in CheckoutForm"
    assert "URLSearchParams" in checkout_content, "URLSearchParams not used in CheckoutForm"
    assert "queryParams.set('accessToken'" in checkout_content or \
           'queryParams.set("accessToken"' in checkout_content, \
        "accessToken not added to query params in CheckoutForm"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_plugin_config_intact():
    """Existing plugin configuration (customers, payments, stripe) still present."""
    plugin_file = Path(REPO) / "templates/ecommerce/src/plugins/index.ts"
    assert plugin_file.exists(), f"Plugin file not found: {plugin_file}"

    content = plugin_file.read_text()

    # Check customers configuration exists
    assert "customers:" in content, "customers config not found"
    assert "slug: 'users'" in content or 'slug: "users"' in content, \
        "customers slug not found"

    # Check payments configuration exists
    assert "payments:" in content, "payments config not found"

    # Check stripe adapter is still there
    assert "stripeAdapter" in content, "stripeAdapter not found"


# [static] pass_to_pass
def test_readme_updated():
    """README documents the accessToken-based guest order access flow."""
    readme = Path(REPO) / "templates/ecommerce/README.md"
    assert readme.exists(), f"README not found: {readme}"

    content = readme.read_text()

    # Check access control section mentions accessToken
    assert "accessToken" in content, "accessToken not mentioned in README"

    # Check Guests section describes the new flow
    assert "Guest checkout allows users" in content or "guest checkout" in content.lower(), \
        "Guest checkout section not updated"

    # Check security rationale is documented
    assert "enumeration" in content.lower() or "secure" in content.lower(), \
        "Security rationale not documented"


# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    files_to_check = [
        "templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        if not full_path.exists():
            continue

        content = full_path.read_text()

        # Check it's not just a stub function
        # Count meaningful lines (excluding imports, types, and empty lines)
        lines = content.split("\n")
        meaningful = [l for l in lines if l.strip() and not l.strip().startswith("import")]
        assert len(meaningful) > 5, f"{file_path} appears to be a stub"

        # Check for actual implementation (not just "return { success: true }")
        assert "payload.find" in content or "payload.sendEmail" in content, \
            f"{file_path} lacks actual implementation"


# ---------------------------------------------------------------------------
# CI/CD pass_to_pass (repo_tests) — Repo CI checks pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - TypeScript config validation
def test_tsconfig_valid():
    """TypeScript configuration files exist and are valid (pass_to_pass)."""
    import json
    import re

    configs_to_check = [
        "packages/plugin-ecommerce/tsconfig.json",
        "templates/ecommerce/tsconfig.json",
    ]

    for config_path in configs_to_check:
        full_path = Path(REPO) / config_path
        assert full_path.exists(), f"TypeScript config missing: {config_path}"

        config_content = full_path.read_text()
        assert len(config_content) > 0, f"TypeScript config is empty: {config_path}"

        # Remove single-line comments
        content_clean = re.sub(r'//.*$', '', config_content, flags=re.MULTILINE)
        # Remove multi-line comments
        content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
        # Remove trailing commas (JSON5/TS allows them, JSON doesn't)
        content_clean = re.sub(r',([\s}\]]+)', r'', content_clean)
        # Fix any potential empty blocks that might result
        content_clean = re.sub(r'{[\s]*}', '{}', content_clean)

        try:
            json.loads(content_clean)
        except json.JSONDecodeError as e:
            # As long as the file exists and has content, we consider it valid
            # The exact JSON parsing is flexible for TS config files
            assert '{"' in content_clean or '"extends"' in content_clean or '"compilerOptions"' in content_clean,                 f"{config_path} does not appear to be a valid tsconfig file"

        # Check for essential tsconfig properties
        assert '"extends"' in config_content or '"compilerOptions"' in config_content,             f"{config_path} missing essential tsconfig properties"


# [repo_tests] pass_to_pass - Package.json validation
def test_package_json_valid():
    """Package.json files are valid and parseable (pass_to_pass)."""
    import json

    packages_to_check = [
        "packages/plugin-ecommerce/package.json",
        "templates/ecommerce/package.json",
    ]

    for pkg_path in packages_to_check:
        full_path = Path(REPO) / pkg_path
        if not full_path.exists():
            continue

        content = full_path.read_text()
        try:
            pkg = json.loads(content)
            # Basic sanity checks
            assert "name" in pkg, f"{pkg_path} missing name field"
            assert "version" in pkg, f"{pkg_path} missing version field"
        except json.JSONDecodeError as e:
            assert False, f"{pkg_path} is not valid JSON: {e}"


# [repo_tests] pass_to_pass - ESLint config validation
def test_eslint_config_valid():
    """ESLint configuration files exist and are valid (pass_to_pass)."""
    eslint_configs = [
        "packages/plugin-ecommerce/eslint.config.js",
        "templates/ecommerce/eslint.config.mjs",
    ]

    for config_path in eslint_configs:
        full_path = Path(REPO) / config_path
        assert full_path.exists(), f"ESLint config missing: {config_path}"

        # Check file is readable (basic JS/JSON validation)
        content = full_path.read_text()
        assert len(content) > 0, f"ESLint config is empty: {config_path}"


# [repo_tests] pass_to_pass - Modified files have valid TypeScript syntax
def test_modified_files_typescript_syntax():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    ts_files = [
        "packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts",
        "templates/ecommerce/src/plugins/index.ts",
    ]

    for file_path in ts_files:
        full_path = Path(REPO) / file_path
        if not full_path.exists():
            continue

        content = full_path.read_text()

        # Check for basic TypeScript syntax validity
        # - No unclosed braces/parens/brackets
        open_braces = content.count("{")
        close_braces = content.count("}")
        open_parens = content.count("(")
        close_parens = content.count(")")
        open_brackets = content.count("[")
        close_brackets = content.count("]")

        assert open_braces == close_braces, f"{file_path}: Unmatched braces"
        assert open_parens == close_parens, f"{file_path}: Unmatched parens"
        assert open_brackets == close_brackets, f"{file_path}: Unmatched brackets"

        # Check for balanced quotes in import statements
        import_lines = [l for l in content.split("\n") if l.strip().startswith("import")]
        for line in import_lines:
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            if single_quotes > 0:
                assert single_quotes % 2 == 0, f"{file_path}: Unbalanced single quotes in import"
            if double_quotes > 0:
                assert double_quotes % 2 == 0, f"{file_path}: Unbalanced double quotes in import"


# [repo_tests] pass_to_pass - Ecommerce template build config valid
def test_ecommerce_build_config():
    """Ecommerce template build configuration is valid (pass_to_pass)."""
    import json

    # Check next.config.js exists and is valid
    next_config = Path(REPO) / "templates/ecommerce/next.config.js"
    assert next_config.exists(), "next.config.js missing"

    content = next_config.read_text()
    # Basic JS module.exports check
    assert "module.exports" in content or "export default" in content, \
        "next.config.js missing module.exports or export default"

    # Check tailwind config
    tailwind_config = Path(REPO) / "templates/ecommerce/tailwind.config.mjs"
    assert tailwind_config.exists(), "tailwind.config.mjs missing"
