#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'accessToken' templates/ecommerce/src/plugins/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts b/packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts
index 531d77f0fff..c93b2fe8482 100644
--- a/packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts
+++ b/packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts
@@ -129,6 +129,7 @@ export const confirmOrder: (props: Props) => NonNullable<PaymentAdapter>['confir
         message: 'Payment initiated successfully',
         orderID: order.id,
         transactionID: transaction.id,
+        ...(order.accessToken ? { accessToken: order.accessToken } : {}),
       }
     } catch (error) {
       payload.logger.error(error, 'Error initiating payment with Stripe')
diff --git a/templates/ecommerce/README.md b/templates/ecommerce/README.md
index 156aa584ca6..ec2db2b669c 100644
--- a/templates/ecommerce/README.md
+++ b/templates/ecommerce/README.md
@@ -119,14 +119,24 @@ Basic access control is setup to limit access to various content based based on
 - `carts`: Customers can access their own saved cart, guest users can access any unclaimed cart by ID.
 - `addresses`: Customers can access their own addresses for record keeping.
 - `transactions`: Only admins can access these as they're meant for internal tracking.
-- `orders`: Only admins and users who own the orders can access these.
+- `orders`: Only admins and users who own the orders can access these. Guests require a valid `accessToken` (sent via email) along with the order's email to view order details.

 For more details on how to extend this functionality, see the [Payload Access Control](https://payloadcms.com/docs/access-control/overview#access-control) docs.

 ## User accounts

+Registered users can log in to view their order history, manage saved addresses, and track ongoing orders directly from their account dashboard.
+
 ## Guests

+Guest checkout allows users to complete purchases without creating an account. When a guest places an order:
+
+1. The order is associated with their email address
+2. A unique `accessToken` is generated for secure order lookup
+3. An order confirmation email is sent containing a secure link to view the order
+
+To look up an order as a guest, users visit `/find-order`, enter their email and order ID, and receive an email with a secure access link. This prevents order enumeration attacks where malicious users could iterate through sequential order IDs to access other customers' order information.
+
 ## Layout Builder

 Create unique page layouts for any type of content using a powerful layout builder. This template comes pre-configured with the following layout building blocks:
@@ -173,7 +183,19 @@ This template comes with SSR search features can easily be implemented into Next

 Transactions are intended for keeping a record of any payment made, as such it will contain information regarding an order or billing address used or the payment method used and amount. Only admins can access transactions.

-An order is created only once a transaction is successfully completed. This is a record that the user who completed the transaction has access so they can keep track of their history. Guests can also access their own orders by providing an order ID and the email associated with that order.
+An order is created only once a transaction is successfully completed. This is a record that the user who completed the transaction has access so they can keep track of their history.
+
+### Guest Order Access
+
+Guest users can securely access their orders through the `/find-order` page:
+
+1. Guest enters their email address and order ID
+2. If the order exists and matches the email, an access link is sent to their email
+3. The link contains a secure `accessToken` that grants temporary access to view the order
+
+This email verification flow prevents unauthorized access to order details. The `accessToken` is a unique UUID generated when the order is created and is required (along with the email) to view order details as a guest.
+
+**Security note:** Order confirmation emails should include the order ID so guests can use the "Find Order" feature. The access token is only sent via the verification email to prevent enumeration attacks.

 ## Currencies

diff --git a/templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx b/templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx
index 5dce533735e..19a38318687 100644
--- a/templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx
+++ b/templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx
@@ -19,7 +19,7 @@ export const dynamic = 'force-dynamic'

type PageProps = {
   params: Promise<{ id: string }>
-  searchParams: Promise<{ email?: string }>
+  searchParams: Promise<{ email?: string; accessToken?: string }>
}

 export default async function Order({ params, searchParams }: PageProps) {
@@ -28,7 +28,7 @@ export default async function Order({ params, searchParams }: PageProps) {
   const { user } = await payload.auth({ headers })

   const { id } = await params
-  const { email = '' } = await searchParams
+  const { email = '', accessToken = '' } = await searchParams

   let order: Order | null = null

@@ -55,16 +55,22 @@ export default async function Order({ params, searchParams }: PageProps) {
                   },
                 },
               ]
-            : []),
-          ...(email
-            ? [
+            : [
                 {
-                  customerEmail: {
-                    equals: email,
+                  accessToken: {
+                    equals: accessToken,
                   },
                 },
-              ]
-            : []),
+                ...(email
+                  ? [
+                      {
+                        customerEmail: {
+                          equals: email,
+                        },
+                      },
+                    ]
+                  : []),
+              ]),
         ],
       },
       select: {
@@ -83,6 +89,7 @@ export default async function Order({ params, searchParams }: PageProps) {
     const canAccessAsGuest =
       !user &&
       email &&
+      accessToken &&
       orderResult &&
       orderResult.customerEmail &&
       orderResult.customerEmail === email
diff --git a/templates/ecommerce/src/app/(app)/find-order/page.tsx b/templates/ecommerce/src/app/(app)/find-order/page.tsx
index 39ed4213782..9627aa0c6f7 100644
--- a/templates/ecommerce/src/app/(app)/find-order/page.tsx
+++ b/templates/ecommerce/src/app/(app)/find-order/page.tsx
@@ -20,7 +20,7 @@ export default async function FindOrderPage() {
}

 export const metadata: Metadata = {
-  description: 'Find your order with us using your email.',
+  description: 'Find your order using your email and order ID.',
   openGraph: mergeOpenGraph({
     title: 'Find order',
     url: '/find-order',
diff --git a/templates/ecommerce/src/components/checkout/ConfirmOrder.tsx b/templates/ecommerce/src/components/checkout/ConfirmOrder.tsx
index 59f169d9cf8..195d129a704 100644
--- a/templates/ecommerce/src/components/checkout/ConfirmOrder.tsx
+++ b/templates/ecommerce/src/components/checkout/ConfirmOrder.tsx
@@ -32,7 +32,18 @@ export const ConfirmOrder: React.FC = () => {
           },
         }).then((result) => {
           if (result && typeof result === 'object' && 'orderID' in result && result.orderID) {
-            router.push(`/shop/order/${result.orderID}?email=${email}`)
+            const accessToken = 'accessToken' in result ? (result.accessToken as string) : ''
+            const queryParams = new URLSearchParams()
+
+            if (email) {
+              queryParams.set('email', email)
+            }
+            if (accessToken) {
+              queryParams.set('accessToken', accessToken)
+            }
+
+            const queryString = queryParams.toString()
+            router.push(`/orders/${result.orderID}${queryString ? `?${queryString}` : ''}`)
           }
         })
       }
@@ -40,7 +51,7 @@ export const ConfirmOrder: React.FC = () => {
       // If no payment intent ID is found, redirect to the home
       router.push('/')
     }
-  }, [cart, searchParams])
+  }, [cart, confirmOrder, router, searchParams])

   return (
     <div className="text-center w-full flex flex-col items-center justify-start gap-4">
diff --git a/templates/ecommerce/src/components/forms/CheckoutForm/index.tsx b/templates/ecommerce/src/components/forms/CheckoutForm/index.tsx
index df9f2c42312..9d66eaf4a33 100644
--- a/templates/ecommerce/src/components/forms/CheckoutForm/index.tsx
+++ b/templates/ecommerce/src/components/forms/CheckoutForm/index.tsx
@@ -75,7 +75,19 @@ export const CheckoutForm: React.FC<Props> = ({
                 'orderID' in confirmResult &&
                 confirmResult.orderID
               ) {
-                const redirectUrl = `/orders/${confirmResult.orderID}${customerEmail ? `?email=${customerEmail}` : ''}`
+                const accessToken =
+                  'accessToken' in confirmResult ? (confirmResult.accessToken as string) : ''
+                const queryParams = new URLSearchParams()
+
+                if (customerEmail) {
+                  queryParams.set('email', customerEmail)
+                }
+                if (accessToken) {
+                  queryParams.set('accessToken', accessToken)
+                }
+
+                const queryString = queryParams.toString()
+                const redirectUrl = `/orders/${confirmResult.orderID}${queryString ? `?${queryString}` : ''}`

                 // Clear the cart after successful payment
                 clearCart()
diff --git a/templates/ecommerce/src/components/forms/FindOrderForm/index.tsx b/templates/ecommerce/src/components/forms/FindOrderForm/index.tsx
index 4a965cb8b4e..1fdcd5e528f 100644
--- a/templates/ecommerce/src/components/forms/FindOrderForm/index.tsx
+++ b/templates/ecommerce/src/components/forms/FindOrderForm/index.tsx
@@ -6,9 +6,9 @@ import { Button } from '@/components/ui/button'
 import { Input } from '@/components/ui/input'
 import { Label } from '@/components/ui/label'
 import { useAuth } from '@/providers/Auth'
-import { useRouter } from 'next/navigation'
-import React, { Fragment, useCallback } from 'react'
+import React, { Fragment, useCallback, useState } from 'react'
 import { useForm } from 'react-hook-form'
+import { sendOrderAccessEmail } from './sendOrderAccessEmail'

type FormData = {
   email: string
@@ -20,8 +20,10 @@ type Props = {
}

 export const FindOrderForm: React.FC<Props> = ({ initialEmail }) => {
-  const router = useRouter()
   const { user } = useAuth()
+  const [isSubmitting, setIsSubmitting] = useState(false)
+  const [submitError, setSubmitError] = useState<string | null>(null)
+  const [success, setSuccess] = useState(false)

   const {
     formState: { errors },
@@ -33,18 +35,46 @@ export const FindOrderForm: React.FC<Props> = ({ initialEmail }) => {
     },
   })

-  const onSubmit = useCallback(
-    async (data: FormData) => {
-      router.push(`/orders/${data.orderID}?email=${data.email}`)
-    },
-    [router],
-  )
+  const onSubmit = useCallback(async (data: FormData) => {
+    setIsSubmitting(true)
+    setSubmitError(null)
+
+    try {
+      const result = await sendOrderAccessEmail({
+        email: data.email,
+        orderID: data.orderID,
+      })
+
+      if (result.success) {
+        setSuccess(true)
+      } else {
+        setSubmitError(result.error || 'Something went wrong. Please try again.')
+      }
+    } catch {
+      setSubmitError('Something went wrong. Please try again.')
+    } finally {
+      setIsSubmitting(false)
+    }
+  }, [])
+
+  if (success) {
+    return (
+      <Fragment>
+        <h1 className="text-xl mb-4">Check your email</h1>
+        <div className="prose dark:prose-invert">
+          <p>
+            {`If an order exists with the provided email and order ID, we've sent you an email with a link to view your order details.`}
+          </p>
+        </div>
+      </Fragment>
+    )
+  }

   return (
     <Fragment>
       <h1 className="text-xl mb-4">Find my order</h1>
       <div className="prose dark:prose-invert mb-8">
-        <p>{`Please enter your email and order ID below.`}</p>
+        <p>{`Please enter your email and order ID below. We'll send you a link to view your order.`}</p>
       </div>
       <form className="max-w-lg flex flex-col gap-8" onSubmit={handleSubmit(onSubmit)}>
         <FormItem>
@@ -65,14 +95,15 @@ export const FindOrderForm: React.FC<Props> = ({ initialEmail }) => {
           <Input
             id="orderID"
             {...register('orderID', {
-              required: 'Order ID is required. You can find this in your email.',
+              required: 'Order ID is required.',
             })}
             type="text"
           />
           {errors.orderID && <FormError message={errors.orderID.message} />}
         </FormItem>
-        <Button type="submit" className="self-start" variant="default">
-          Find my order
+        {submitError && <FormError message={submitError} />}
+        <Button type="submit" className="self-start" variant="default" disabled={isSubmitting}>
+          {isSubmitting ? 'Sending...' : 'Find order'}
         </Button>
       </form>
     </Fragment>
diff --git a/templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts b/templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts
new file mode 100644
index 00000000000..5d18b0eb99b
--- /dev/null
+++ b/templates/ecommerce/src/components/forms/FindOrderForm/sendOrderAccessEmail.ts
@@ -0,0 +1,64 @@
+'use server'
+
+import configPromise from '@payload-config'
+import { getPayload } from 'payload'
+import { getServerSideURL } from '@/utilities/getURL'
+
+type SendOrderAccessEmailArgs = {
+  email: string
+  orderID: string
+}
+
+type SendOrderAccessEmailResult = {
+  success: boolean
+  error?: string
+}
+
+export async function sendOrderAccessEmail({
+  email,
+  orderID,
+}: SendOrderAccessEmailArgs): Promise<SendOrderAccessEmailResult> {
+  const payload = await getPayload({ config: configPromise })
+
+  try {
+    const { docs: orders } = await payload.find({
+      collection: 'orders',
+      where: {
+        and: [{ id: { equals: orderID } }, { customerEmail: { equals: email } }],
+      },
+      limit: 1,
+      depth: 0,
+    })
+
+    const order = orders[0]
+
+    if (!order || !order.accessToken) {
+      return { success: true }
+    }
+
+    const serverURL = getServerSideURL()
+    const orderURL = `${serverURL}/orders/${order.id}?email=${encodeURIComponent(email)}&accessToken=${order.accessToken}`
+
+    const emailBody = `
+        <h1>View Your Order</h1>
+        <p>Click the link below to view your order details:</p>
+        <p><a href="${orderURL}">View Order #${order.id}</a></p>
+        <p>Or copy and paste this URL into your browser:</p>
+        <p>${orderURL}</p>
+        <p>This link will give you access to view your order details.</p>
+      `
+
+    console.log('[sendOrderAccessEmail] Email body:', emailBody)
+
+    await payload.sendEmail({
+      to: email,
+      subject: `Access your order #${order.id}`,
+      html: emailBody,
+    })
+
+    return { success: true }
+  } catch (err) {
+    payload.logger.error({ msg: 'Failed to send order access email', err })
+    return { success: true }
+  }
+}
diff --git a/templates/ecommerce/src/plugins/index.ts b/templates/ecommerce/src/plugins/index.ts
index 823266bbf77..b41387a03c4 100644
--- a/templates/ecommerce/src/plugins/index.ts
+++ b/templates/ecommerce/src/plugins/index.ts
@@ -76,6 +76,34 @@ export const plugins: Plugin[] = [
     customers: {
       slug: 'users',
     },
+    orders: {
+      ordersCollectionOverride: ({ defaultCollection }) => ({
+        ...defaultCollection,
+        fields: [
+          ...defaultCollection.fields,
+          {
+            name: 'accessToken',
+            type: 'text',
+            unique: true,
+            index: true,
+            admin: {
+              position: 'sidebar',
+              readOnly: true,
+            },
+            hooks: {
+              beforeValidate: [
+                ({ value, operation }) => {
+                  if (operation === 'create' || !value) {
+                    return crypto.randomUUID()
+                  }
+                  return value
+                },
+              ],
+            },
+          },
+        ],
+      }),
+    },
     payments: {
       paymentMethods: [
         stripeAdapter({

PATCH

echo "Patch applied successfully."
