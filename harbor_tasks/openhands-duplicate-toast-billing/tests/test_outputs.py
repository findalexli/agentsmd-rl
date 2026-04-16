"""Test outputs for OpenHands billing duplicate toast fix."""
import subprocess
import os
import sys

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_npm_install():
    """Dependencies are installed (pass_to_pass)."""
    assert os.path.exists(f"{FRONTEND}/node_modules"), "node_modules not found"


def test_billing_component_renders():
    """Billing component renders without crashing (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "billing.test.tsx", "-t", "renders the payment form"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_checkout_success_toast_once():
    """Success toast displays exactly once on checkout success (f2p regression test).
    
    This test verifies the core bug fix: the checkout success effect should fire
    exactly once, not multiple times due to improper dependency array management.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "billing.test.tsx", "-t", "should display success toast exactly once"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_checkout_cancel_toast_once():
    """Error toast displays exactly once on checkout cancel (f2p regression test).
    
    This test verifies the core bug fix: the checkout cancel effect should fire
    exactly once, not multiple times due to improper dependency array management.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "billing.test.tsx", "-t", "should display error toast exactly once"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_track_credits_called_once():
    """Credits tracking only fires once on checkout success (f2p regression test).
    
    This test verifies the core bug fix: credits tracking should fire exactly once
    when checkout succeeds, not repeatedly due to useEffect re-firing.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "billing.test.tsx", "-t", "track credits on checkout success"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_lint():
    """Frontend linting passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_build():
    """Frontend builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_frontend_typecheck():
    """Frontend TypeScript typecheck passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_frontend_translation_completeness():
    """Frontend translation completeness check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_toast_handlers():
    """Toast handler unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/utils/custom-toast-handlers.test.ts", "__tests__/utils/toast-duration.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Toast handler tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_billing_visibility():
    """Billing visibility unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/utils/billing-visibility.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Billing visibility tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_plan_click_hook():
    """Plan click hook unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/hooks/use-handle-plan-click.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Plan click hook tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
