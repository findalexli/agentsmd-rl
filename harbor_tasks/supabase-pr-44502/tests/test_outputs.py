#!/usr/bin/env python3
"""
Test that formatCurrency preserves decimal precision and that the reduce sums
pass fractional values through to formatCurrency (not rounded first).

The issue: Math.round() in subscription preview was stripping decimals before
formatCurrency could render them with 2 decimal places. E.g., $10.256 -> $10
instead of $10.26.

After fix: formatCurrency receives raw values and renders them correctly via
Intl.NumberFormat with minimumFractionDigits: 2, maximumFractionDigits: 2.

The behavioral tests check the source code structure to detect if Math.round
wraps the reduce expressions. If Math.round wraps the reduce, the test fails
(bug state). If Math.round doesn't wrap the reduce, the test passes (fixed state).
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/supabase-project/apps/studio"
COMPONENT = os.path.join(REPO, "components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx")


def runtsx(code: str, cwd: str = REPO):
    """Run TypeScript code using tsx in the studio directory."""
    test_file = os.path.join(cwd, "_test_currency.ts")
    with open(test_file, 'w') as f:
        f.write(code)
    try:
        r = subprocess.run(
            ["npx", "tsx", "_test_currency.ts"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def _check_reduce_wrapped_in_math_round(content: str, pattern: str) -> bool:
    """
    Check if the reduce expression matching `pattern` is wrapped in Math.round.
    In the bug state:
        {formatCurrency(
          Math.round(
            subscriptionPreview?.breakdown?.reduce(
    In the fixed state:
        {formatCurrency(
          subscriptionPreview?.breakdown?.reduce(
    """
    match = re.search(pattern, content)
    if not match:
        return False

    start = match.start()
    # Look back from start for "Math.round" - need to find it on a preceding line
    # In buggy code: "Math.round" is on a line above, before subscriptionPreview

    # Get the 150 chars before the reduce
    look_back = content[max(0, start-150):start]

    # Split into lines and check the last few lines before reduce
    lines = look_back.split('\n')
    # The lines just before the reduce
    last_lines = lines[-6:]  # Last 6 lines

    # Check if any of these lines contain Math.round
    for line in last_lines:
        stripped = line.strip()
        if 'Math.round' in stripped:
            # Found Math.round on a line before the reduce
            return True

    return False


def test_formatCurrency_preserves_decimals():
    """formatCurrency formats with 2 decimal places via Intl.NumberFormat."""
    code = """
import { formatCurrency } from './lib/helpers';

const testCases: [number | null | undefined, string | null][] = [
    [10.256, '$10.26'],
    [10.254, '$10.25'],
    [10.005, '$10.01'],
    [10.999, '$11.00'],
    [100.0, '$100.00'],
    [10.2, '$10.20'],
    [null, null],
    [undefined, null],
];

let passed = 0, failed = 0;
for (const [input, expected] of testCases) {
    const result = formatCurrency(input);
    if (result === expected) {
        console.log('PASS:', input, '->', result);
        passed++;
    } else {
        console.log('FAIL:', input, 'expected:', expected, 'got:', result);
        failed++;
    }
}
if (failed > 0) {
    console.error('FAILED: ' + failed + ' tests');
    process.exit(1);
} else {
    console.log('All tests passed: ' + passed);
}
"""
    r = runtsx(code)
    print("STDOUT:", r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr[:500])
    assert r.returncode == 0, f"formatCurrency tests failed:\n{r.stderr}"


def test_total_per_month_reduce_behavior():
    """
    Verify the 'Total per month' reduce expression is not wrapped in Math.round.

    The bug: Math.round(subscriptionPreview?.breakdown?.reduce(...)) passes an
    integer to formatCurrency, causing "$10.00" instead of "$10.26".

    After fix: subscriptionPreview?.breakdown?.reduce(...) passes the raw
    fractional sum to formatCurrency.

    This test checks the source code structure to detect if Math.round wraps
    the reduce. If so, the test fails (indicating bug). If not, the test passes.
    """
    with open(COMPONENT, 'r') as f:
        content = f.read()

    # Pattern: the first reduce in the component
    pattern = r'subscriptionPreview\?\.breakdown\?\.reduce'

    wrapped = _check_reduce_wrapped_in_math_round(content, pattern)

    print(f"Math.round wrapping first reduce detected: {wrapped}")

    assert not wrapped, (
        "Bug detected: Math.round wraps the first reduce expression. "
        "The fix should pass the raw fractional sum to formatCurrency."
    )


def test_monthly_invoice_reduce_behavior():
    """
    Verify the 'Monthly invoice estimate' reduce expression is not wrapped in Math.round.

    The bug: Math.round(subscriptionPreview?.breakdown.reduce(...)) passes an
    integer to formatCurrency, causing "$11.00" instead of "$11.11".

    After fix: subscriptionPreview?.breakdown.reduce(...) passes the raw
    fractional sum to formatCurrency.
    """
    with open(COMPONENT, 'r') as f:
        content = f.read()

    # Pattern: the second reduce (no extra ? after breakdown)
    pattern = r'subscriptionPreview\?\.breakdown\.reduce'

    wrapped = _check_reduce_wrapped_in_math_round(content, pattern)

    print(f"Math.round wrapping second reduce detected: {wrapped}")

    assert not wrapped, (
        "Bug detected: Math.round wraps the second reduce expression. "
        "The fix should pass the raw fractional sum to formatCurrency."
    )


def test_intl_numberformat_two_decimals():
    """JavaScript's Intl.NumberFormat with 2 decimal places works correctly for currency."""
    code = """
const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

const testCases: [number, string][] = [
    [10.256, '$10.26'],
    [10.254, '$10.25'],
    [10.005, '$10.01'],
    [10.999, '$11.00'],
    [100.0, '$100.00'],
    [10.2, '$10.20'],
    [0.009, '$0.01'],
];

let passed = 0, failed = 0;
for (const [input, expected] of testCases) {
    const result = formatter.format(input);
    if (result === expected) {
        console.log('PASS:', input, '->', result);
        passed++;
    } else {
        console.log('FAIL:', input, 'expected:', expected, 'got:', result);
        failed++;
    }
}
if (failed > 0) {
    console.error('FAILED: ' + failed);
    process.exit(1);
}
console.log('All tests passed: ' + passed);
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    print("STDOUT:", r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr[:500])
    assert r.returncode == 0, f"Intl.NumberFormat test failed:\n{r.stderr}"


def test_repo_unit_tests():
    """Repo's unit tests for helpers/lib pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "--run", "lib/helpers.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"vitest helpers.test.ts failed:\n{r.stdout[-500:]}"


def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}"


if __name__ == "__main__":
    print("=" * 60)
    print("Running tests...")
    print("=" * 60)

    test_formatCurrency_preserves_decimals()
    print()

    test_total_per_month_reduce_behavior()
    print()

    test_monthly_invoice_reduce_behavior()
    print()

    test_intl_numberformat_two_decimals()
    print()

    test_repo_unit_tests()
    print()

    test_repo_lint()
    print()

    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
