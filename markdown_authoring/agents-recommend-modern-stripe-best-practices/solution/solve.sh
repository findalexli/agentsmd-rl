#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "- Provides built-in checkout capabilities (line items, discounts, tax, shipping," "plugins/payment-processing/skills/stripe-integration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/payment-processing/skills/stripe-integration/SKILL.md b/plugins/payment-processing/skills/stripe-integration/SKILL.md
@@ -21,19 +21,21 @@ Master Stripe payment processing integration for robust, PCI-compliant payment f
 
 ### 1. Payment Flows
 
-**Checkout Session (Hosted)**
+**Checkout Sessions**
 
-- Stripe-hosted payment page
-- Minimal PCI compliance burden
-- Fastest implementation
-- Supports one-time and recurring payments
+- Recommended for most integrations
+- Supports all UI paths:
+  - Stripe-hosted checkout page
+  - Embedded checkout form
+  - Custom UI with Elements (Payment Element, Express Checkout Element) using `ui_mode='custom'`
+- Provides built-in checkout capabilities (line items, discounts, tax, shipping, address collection, saved payment methods, and checkout lifecycle events)
+- Lower integration and maintenance burden than Payment Intents
 
-**Payment Intents (Custom UI)**
+**Payment Intents (Bespoke control)**
 
-- Full control over payment UI
+- You calculate the final amount with taxes, discounts, subscriptions, and currency conversion yourself.
+- More complex implementation and long-term maintenance burden
 - Requires Stripe.js for PCI compliance
-- More complex implementation
-- Better customization options
 
 **Setup Intents (Save Payment Methods)**
 
@@ -77,7 +79,6 @@ stripe.api_key = "sk_test_..."
 
 # Create a checkout session
 session = stripe.checkout.Session.create(
-    payment_method_types=['card'],
     line_items=[{
         'price_data': {
             'currency': 'usd',
@@ -93,7 +94,7 @@ session = stripe.checkout.Session.create(
     }],
     mode='subscription',
     success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
-    cancel_url='https://yourdomain.com/cancel',
+    cancel_url='https://yourdomain.com/cancel'
 )
 
 # Redirect user to session.url
@@ -109,12 +110,11 @@ def create_checkout_session(amount, currency='usd'):
     """Create a one-time payment checkout session."""
     try:
         session = stripe.checkout.Session.create(
-            payment_method_types=['card'],
             line_items=[{
                 'price_data': {
                     'currency': currency,
                     'product_data': {
-                        'name': 'Purchase',
+                        'name': 'Blue T-shirt',
                         'images': ['https://example.com/product.jpg'],
                     },
                     'unit_amount': amount,  # Amount in cents
@@ -136,11 +136,77 @@ def create_checkout_session(amount, currency='usd'):
         raise
 ```
 
-### Pattern 2: Custom Payment Intent Flow
+### Pattern 2: Elements with Checkout Sessions
+
+```python
+def create_checkout_session_for_elements(amount, currency='usd'):
+    """Create a checkout session configured for Payment Element."""
+    session = stripe.checkout.Session.create(
+        mode='payment',
+        ui_mode='custom',
+        line_items=[{
+            'price_data': {
+                'currency': currency,
+                'product_data': {'name': 'Blue T-shirt'},
+                'unit_amount': amount,
+            },
+            'quantity': 1,
+        }],
+        return_url='https://yourdomain.com/complete?session_id={CHECKOUT_SESSION_ID}'
+    )
+    return session.client_secret  # Send to frontend
+```
+
+```javascript
+const stripe = Stripe("pk_test_...");
+const appearance = { theme: "stripe" };
+
+const checkout = stripe.initCheckout({
+  clientSecret,
+  elementsOptions: { appearance },
+});
+const loadActionsResult = await checkout.loadActions();
+
+if (loadActionsResult.type === "success") {
+  const { actions } = loadActionsResult;
+  const session = actions.getSession();
+
+  const button = document.getElementById("pay-button");
+  const checkoutContainer = document.getElementById("checkout-container");
+  const emailInput = document.getElementById("email");
+  const emailErrors = document.getElementById("email-errors");
+  const errors = document.getElementById("confirm-errors");
+
+  // Display a formatted string representing the total amount
+  checkoutContainer.append(`Total: ${session.total.total.amount}`);
+
+  // Mount Payment Element
+  const paymentElement = checkout.createPaymentElement();
+  paymentElement.mount("#payment-element");
+
+  // Store email for submission
+  emailInput.addEventListener("blur", () => {
+    actions.updateEmail(emailInput.value).then((result) => {
+      if (result.error) emailErrors.textContent = result.error.message;
+    });
+  });
+
+  // Handle form submission
+  button.addEventListener("click", () => {
+    actions.confirm().then((result) => {
+      if (result.type === "error") errors.textContent = result.error.message;
+    });
+  });
+}
+```
+
+### Pattern 3: Elements with Payment Intents
+
+Pattern 2 (Elements with Checkout Sessions) is Stripe's recommended approach, but you can also use Payment Intents as an alternative.
 
 ```python
 def create_payment_intent(amount, currency='usd', customer_id=None):
-    """Create a payment intent for custom checkout UI."""
+    """Create a payment intent for bespoke checkout UI with Payment Element."""
     intent = stripe.PaymentIntent.create(
         amount=amount,
         currency=currency,
@@ -153,35 +219,32 @@ def create_payment_intent(amount, currency='usd', customer_id=None):
         }
     )
     return intent.client_secret  # Send to frontend
+```
 
-# Frontend (JavaScript)
-"""
-const stripe = Stripe('pk_test_...');
-const elements = stripe.elements();
-const cardElement = elements.create('card');
-cardElement.mount('#card-element');
-
-const {error, paymentIntent} = await stripe.confirmCardPayment(
-    clientSecret,
-    {
-        payment_method: {
-            card: cardElement,
-            billing_details: {
-                name: 'Customer Name'
-            }
-        }
-    }
-);
-
-if (error) {
-    // Handle error
-} else if (paymentIntent.status === 'succeeded') {
-    // Payment successful
-}
-"""
+```javascript
+// Mount Payment Element and confirm via Payment Intents
+const stripe = Stripe("pk_test_...");
+const appearance = { theme: "stripe" };
+const elements = stripe.elements({ appearance, clientSecret });
+
+const paymentElement = elements.create("payment");
+paymentElement.mount("#payment-element");
+
+document.getElementById("pay-button").addEventListener("click", async () => {
+  const { error } = await stripe.confirmPayment({
+    elements,
+    confirmParams: {
+      return_url: "https://yourdomain.com/complete",
+    },
+  });
+
+  if (error) {
+    document.getElementById("errors").textContent = error.message;
+  }
+});
 ```
 
-### Pattern 3: Subscription Creation
+### Pattern 4: Subscription Creation
 
 ```python
 def create_subscription(customer_id, price_id):
@@ -204,7 +267,7 @@ def create_subscription(customer_id, price_id):
         raise
 ```
 
-### Pattern 4: Customer Portal
+### Pattern 5: Customer Portal
 
 ```python
 def create_customer_portal_session(customer_id):
@@ -412,9 +475,11 @@ def test_payment_flow():
     # Create payment intent
     intent = stripe.PaymentIntent.create(
         amount=1000,
+        automatic_payment_methods={
+            'enabled': True
+        },
         currency='usd',
-        customer=customer.id,
-        payment_method_types=['card']
+        customer=customer.id
     )
 
     # Confirm with test card
PATCH

echo "Gold patch applied."
