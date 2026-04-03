"""
Task: payload-fixtemplates-ecommerce-find-my-order
Repo: payloadcms/payload @ 7f3c6c8f4628fb066002e2fd5c3cc6b83ddf4ccc
PR:   15736

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/payload"
ECOMMERCE = Path(REPO) / "templates" / "ecommerce"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Key TypeScript files must have balanced braces and parentheses."""
    ts_files = [
        ECOMMERCE / "src" / "plugins" / "index.ts",
        ECOMMERCE / "src" / "components" / "forms" / "FindOrderForm" / "index.tsx",
        ECOMMERCE / "src" / "app" / "(app)" / "(account)" / "orders" / "[id]" / "page.tsx",
        ECOMMERCE / "src" / "components" / "checkout" / "ConfirmOrder.tsx",
        ECOMMERCE / "src" / "components" / "forms" / "CheckoutForm" / "index.tsx",
    ]
    for f in ts_files:
        content = f.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {f.name}"
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parentheses in {f.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_access_token_field_in_plugin():
    """Plugin config must add an accessToken field to the orders collection."""
    content = (ECOMMERCE / "src" / "plugins" / "index.ts").read_text()
    # Must have an accessToken field definition
    assert "accessToken" in content, \
        "plugins/index.ts must define an accessToken field"
    assert "unique" in content and "true" in content.lower(), \
        "accessToken field must be unique"
    # Must use some kind of random/unique token generation
    assert "randomUUID" in content or "uuid" in content.lower() or "crypto" in content \
        or "random" in content.lower() or "nanoid" in content.lower(), \
        "accessToken must be generated using a random/UUID approach"
    # Must be in the orders collection override
    assert "ordersCollectionOverride" in content or "orders" in content, \
        "accessToken must be part of orders collection configuration"


# [pr_diff] fail_to_pass
def test_access_token_in_confirm_order_response():
    """Stripe confirmOrder must include accessToken in the success response."""
    content = (
        Path(REPO) / "packages" / "plugin-ecommerce" / "src" / "payments"
        / "adapters" / "stripe" / "confirmOrder.ts"
    ).read_text()
    assert "accessToken" in content, \
        "confirmOrder.ts must reference accessToken in the response"


# [pr_diff] fail_to_pass
def test_order_page_requires_access_token():
    """Order detail page must require accessToken for guest access."""
    content = (
        ECOMMERCE / "src" / "app" / "(app)" / "(account)"
        / "orders" / "[id]" / "page.tsx"
    ).read_text()
    # Must destructure accessToken from searchParams
    assert "accessToken" in content, \
        "Order page must use accessToken from searchParams"
    # Must use accessToken in the query filter (not just email)
    assert re.search(r"accessToken.*equals", content, re.DOTALL), \
        "Order page must filter by accessToken in the database query"
    # Guest access check must require accessToken
    lines = content.split("\n")
    guest_check_lines = [l for l in lines if "canAccessAsGuest" in l or "accessToken" in l]
    assert len(guest_check_lines) >= 2, \
        "Guest access check must involve accessToken"


# [pr_diff] fail_to_pass
def test_send_order_access_email_exists():
    """A server action for sending order access emails must exist."""
    email_file = (
        ECOMMERCE / "src" / "components" / "forms"
        / "FindOrderForm" / "sendOrderAccessEmail.ts"
    )
    assert email_file.exists(), \
        "sendOrderAccessEmail.ts must exist"
    content = email_file.read_text()
    # Must be a server action
    assert "'use server'" in content or '"use server"' in content, \
        "sendOrderAccessEmail must be a server action ('use server')"
    # Must export the function
    assert "export" in content and "sendOrderAccessEmail" in content, \
        "Must export sendOrderAccessEmail function"
    # Must query orders and send email
    assert "payload.find" in content or "find(" in content, \
        "Must query orders collection"
    assert "sendEmail" in content or "email" in content.lower(), \
        "Must send an email with the access link"
    # Must include accessToken in the email link
    assert "accessToken" in content, \
        "Email link must include accessToken"


# [pr_diff] fail_to_pass
def test_find_order_form_uses_email_flow():
    """FindOrderForm must send email instead of navigating directly."""
    content = (
        ECOMMERCE / "src" / "components" / "forms"
        / "FindOrderForm" / "index.tsx"
    ).read_text()
    # Must NOT have direct router.push to /orders/ with just email
    assert not re.search(r"router\.push\s*\(\s*`/orders/.*\?email=", content), \
        "FindOrderForm must not directly navigate to order page with just email"
    # Must reference the sendOrderAccessEmail action
    assert "sendOrderAccessEmail" in content, \
        "FindOrderForm must use sendOrderAccessEmail server action"
    # Must show a success/confirmation state
    assert "success" in content.lower() or "check your email" in content.lower() \
        or "sent" in content.lower(), \
        "FindOrderForm must show confirmation after submitting"


# [pr_diff] fail_to_pass
def test_checkout_redirects_include_access_token():
    """Checkout components must pass accessToken in redirect URLs."""
    for component_path in [
        ECOMMERCE / "src" / "components" / "checkout" / "ConfirmOrder.tsx",
        ECOMMERCE / "src" / "components" / "forms" / "CheckoutForm" / "index.tsx",
    ]:
        content = component_path.read_text()
        assert "accessToken" in content, \
            f"{component_path.name} must include accessToken in redirect URL"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_plugin_config_intact():
    """Existing plugin configuration (customers, payments) must still be present."""
    content = (ECOMMERCE / "src" / "plugins" / "index.ts").read_text()
    assert "customers" in content, "customers config must still exist"
    assert "payments" in content, "payments config must still exist"
    assert "stripeAdapter" in content or "stripe" in content.lower(), \
        "Stripe adapter must still be configured"


# [repo_tests] pass_to_pass
