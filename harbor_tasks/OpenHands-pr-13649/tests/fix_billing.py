#!/usr/bin/env python3
"""Fix billing.tsx by moving amount and sessionId extraction outside useEffect."""

import re

BILLING_FILE = "/workspace/openhands/frontend/src/routes/billing.tsx"

# Read the file
with open(BILLING_FILE, "r") as f:
    content = f.read()

# The fix: move amount and sessionId extraction outside useEffect
# Find the old pattern and replace with the new one

old_code = '''  const checkoutStatus = searchParams.get("checkout");

  React.useEffect(() => {
    if (checkoutStatus === "success") {
      // Get purchase details from URL params
      const amount = searchParams.get("amount");
      const sessionId = searchParams.get("session_id");

      // Track credits purchased if we have the necessary data
      if (amount && sessionId) {
        trackCreditsPurchased({
          amountUsd: parseFloat(amount),
          stripeSessionId: sessionId,
        });
      }

      displaySuccessToast(t(I18nKey.PAYMENT$SUCCESS));

      setSearchParams({});
    } else if (checkoutStatus === "cancel") {
      displayErrorToast(t(I18nKey.PAYMENT$CANCELLED));
      setSearchParams({});
    }
  }, [checkoutStatus, searchParams, setSearchParams, t, trackCreditsPurchased]);'''

new_code = '''  const checkoutStatus = searchParams.get("checkout");
  const amount = searchParams.get("amount");
  const sessionId = searchParams.get("session_id");

  React.useEffect(() => {
    if (checkoutStatus === "success") {
      // Track credits purchased if we have the necessary data
      if (amount && sessionId) {
        trackCreditsPurchased({
          amountUsd: parseFloat(amount),
          stripeSessionId: sessionId,
        });
      }

      displaySuccessToast(t(I18nKey.PAYMENT$SUCCESS));

      setSearchParams({});
    } else if (checkoutStatus === "cancel") {
      displayErrorToast(t(I18nKey.PAYMENT$CANCELLED));
      setSearchParams({});
    }
  }, [
    checkoutStatus,
    amount,
    sessionId,
    setSearchParams,
    t,
    trackCreditsPurchased,
  ]);'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(BILLING_FILE, "w") as f:
        f.write(content)
    print("billing.tsx fixed successfully!")
else:
    print("ERROR: Could not find the old code pattern to replace")
    print("Checking if already fixed...")
    if 'const amount = searchParams.get("amount");' in content and 'const sessionId = searchParams.get("session_id");' in content:
        # Check if it's outside the useEffect
        checkout_idx = content.find('const checkoutStatus = searchParams.get("checkout");')
        amount_idx = content.find('const amount = searchParams.get("amount");')
        effect_idx = content.find("React.useEffect")

        if checkout_idx < amount_idx < effect_idx:
            print("billing.tsx is already correctly fixed!")
        else:
            print("billing.tsx has amount/sessionId but not in the right location")
    else:
        print("billing.tsx does not have the fix applied")
