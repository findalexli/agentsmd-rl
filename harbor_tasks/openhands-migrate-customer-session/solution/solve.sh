#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for PR #13558
cat <<'PATCH' | git apply -
diff --git a/enterprise/integrations/stripe_service.py b/enterprise/integrations/stripe_service.py
index ce9e25ce477c..972636ab37a5 100644
--- a/enterprise/integrations/stripe_service.py
+++ b/enterprise/integrations/stripe_service.py
@@ -100,27 +100,25 @@ async def has_payment_method_by_user_id(user_id: str) -> bool:
     return bool(payment_methods.data)


-async def migrate_customer(user_id: str, org: Org):
-    async with a_session_maker() as session:
-        result = await session.execute(
-            select(StripeCustomer).where(StripeCustomer.keycloak_user_id == user_id)
-        )
-        stripe_customer = result.scalar_one_or_none()
-        if stripe_customer is None:
-            return
-        stripe_customer.org_id = org.id
-        customer = await stripe.Customer.modify_async(
-            id=stripe_customer.stripe_customer_id,
-            email=org.contact_email,
-            metadata={'user_id': '', 'org_id': str(org.id)},
-        )
+async def migrate_customer(session, user_id: str, org: Org):
+    result = await session.execute(
+        select(StripeCustomer).where(StripeCustomer.keycloak_user_id == user_id)
+    )
+    stripe_customer = result.scalar_one_or_none()
+    if stripe_customer is None:
+        return
+    stripe_customer.org_id = org.id
+    customer = await stripe.Customer.modify_async(
+        id=stripe_customer.stripe_customer_id,
+        email=org.contact_email,
+        metadata={'user_id': '', 'org_id': str(org.id)},
+    )

-        logger.info(
-            'migrated_customer',
-            extra={
-                'user_id': user_id,
-                'org_id': str(org.id),
-                'stripe_customer_id': customer.id,
-            },
-        )
-        await session.commit()
+    logger.info(
+        'migrated_customer',
+        extra={
+            'user_id': user_id,
+            'org_id': str(org.id),
+            'stripe_customer_id': customer.id,
+        },
+    )
 diff --git a/enterprise/storage/user_store.py b/enterprise/storage/user_store.py
index ad4244928541..0bdcd2cf4eb7 100644
--- a/enterprise/storage/user_store.py
+++ b/enterprise/storage/user_store.py
@@ -214,14 +214,15 @@ async def migrate_user(
                 decrypted_user_settings, user_settings.user_version
             )

-            # avoids circular reference. This migrate method is temprorary until all users are migrated.
+            # Migrate stripe customer (pass session to avoid FK violation)
+            # avoids circular reference. This migrate method is temporary until all users are migrated.
             from integrations.stripe_service import migrate_customer

             logger.debug(
                 'user_store:migrate_user:calling_stripe_migrate_customer',
                 extra={'user_id': user_id},
             )
-            await migrate_customer(user_id, org)
+            await migrate_customer(session, user_id, org)
             logger.debug(
                 'user_store:migrate_user:done_stripe_migrate_customer',
                 extra={'user_id': user_id},
PATCH

# Verify the patch was applied by checking for distinctive line
grep -q "async def migrate_customer(session, user_id: str, org: Org)" enterprise/integrations/stripe_service.py && echo "Patch applied successfully"
