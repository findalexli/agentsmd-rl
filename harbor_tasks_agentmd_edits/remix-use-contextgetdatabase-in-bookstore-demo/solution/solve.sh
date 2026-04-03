#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'context\.set(Database, db)' demos/bookstore/app/middleware/database.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/demos/bookstore/README.md b/demos/bookstore/README.md
index efbb1fd07b6..1a3d8f30609 100644
--- a/demos/bookstore/README.md
+++ b/demos/bookstore/README.md
@@ -28,13 +28,12 @@ Then visit http://localhost:44100
 - [`app/routes.ts`](app/routes.ts) shows declarative route definitions using `route()`, `form()`, and `resources()` helpers. All route URLs are generated with full type safety, so `routes.admin.books.edit.href({ bookId: '123' })` ensures you never have broken links.
 - [`app/router.ts`](app/router.ts) demonstrates how to compose middleware for cross-cutting concerns: static file serving, form data parsing, method override, sessions, and async context. Each middleware is independent and reusable.
 - [`data/migrations/20260228090000_create_bookstore_schema.ts`](data/migrations/20260228090000_create_bookstore_schema.ts) defines the schema using `remix/data-table/migrations`.
-- [`app/middleware/database.ts`](app/middleware/database.ts) shows a request-scoped database pattern. It "checks out" a database handle at the start of each request, stores it in request context, and releases it in a `finally` block.
+- [`app/middleware/database.ts`](app/middleware/database.ts) stores the bookstore database on request context with `context.set(Database, db)`, and request handlers read it back with `get(Database)` just like they do for `Session` and `FormData`.
 - [`app/middleware/auth.ts`](app/middleware/auth.ts) provides two patterns:
   - **`loadAuth()`** - Optionally loads the current user without requiring authentication
   - **`requireAuth()`** - Redirects to login with a `returnTo` parameter for post-login redirect
 - [`app/middleware/admin.ts`](app/middleware/admin.ts) shows role-based authorization that returns 403 for non-admin users.
 - [`app/utils/context.ts`](app/utils/context.ts) demonstrates sharing data across the request lifecycle without prop drilling. Any code can call `getCurrentUser()` to access the authenticated user set by middleware earlier in the chain.
-- [`app/middleware/database.ts`](app/middleware/database.ts) attaches `context.db` for every request so route actions can query tables directly without AsyncLocalStorage.
 - [`app/utils/session.ts`](app/utils/session.ts) configures signed cookies and filesystem-based session storage.
 - [`app/utils/uploads.ts`](app/utils/uploads.ts) handles file uploads with `@remix-run/form-data-middleware`. The upload handler stores files and returns public URLs. [`app/uploads.tsx`](app/uploads.tsx) serves uploaded files with appropriate caching headers.
 - HTML forms only support GET and POST. [`app/components/restful-form.tsx`](app/components/restful-form.tsx) adds a hidden `_method` field for PUT and DELETE, which the `methodOverride()` middleware translates back to the original method.
diff --git a/demos/bookstore/app/account.tsx b/demos/bookstore/app/account.tsx
index 82a76c4c1d8..5318c0661a8 100644
--- a/demos/bookstore/app/account.tsx
+++ b/demos/bookstore/app/account.tsx
@@ -2,6 +2,7 @@ import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from './routes.ts'
@@ -118,7 +119,8 @@ export default {
           )
         },

-        async update({ db, get }) {
+        async update({ get }) {
+          let db = get(Database)
           let formData = get(FormData)
           let user = getCurrentUser()

@@ -138,7 +140,8 @@ export default {

     orders: {
       actions: {
-        async index({ db }) {
+        async index({ get }) {
+          let db = get(Database)
           let user = getCurrentUser()
           let userOrders = await db.findMany(orders, {
             where: { user_id: user.id },
@@ -200,7 +203,8 @@ export default {
           )
         },

-        async show({ db, params }) {
+        async show({ get, params }) {
+          let db = get(Database)
           let user = getCurrentUser()
           let orderId = parseId(params.orderId)
           let order =
diff --git a/demos/bookstore/app/admin.books.tsx b/demos/bookstore/app/admin.books.tsx
index b4f12ab3ca3..ac3f5abc37e 100644
--- a/demos/bookstore/app/admin.books.tsx
+++ b/demos/bookstore/app/admin.books.tsx
@@ -3,6 +3,7 @@ import { css } from 'remix/component'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
 import * as coerce from 'remix/data-schema/coerce'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from './routes.ts'
@@ -36,7 +37,8 @@ const bookSchema = f.object({

 export default {
   actions: {
-    async index({ db }) {
+    async index({ get }) {
+      let db = get(Database)
       let allBooks = await db.findMany(books, { orderBy: ['id', 'asc'] })

       return render(
@@ -111,7 +113,8 @@ export default {
       )
     },

-    async show({ db, params }) {
+    async show({ get, params }) {
+      let db = get(Database)
       let bookId = parseId(params.bookId)
       let book = bookId === undefined ? undefined : await db.find(books, bookId)

@@ -262,7 +265,8 @@ export default {
       )
     },

-    async create({ db, get }) {
+    async create({ get }) {
+      let db = get(Database)
       let formData = get(FormData)
       let { author, cover, description, genre, inStock, isbn, price, publishedYear, slug, title } =
         s.parse(bookSchema, formData)
@@ -284,7 +288,8 @@ export default {
       return redirect(routes.admin.books.index.href())
     },

-    async edit({ db, params }) {
+    async edit({ get, params }) {
+      let db = get(Database)
       let bookId = parseId(params.bookId)
       let book = bookId === undefined ? undefined : await db.find(books, bookId)

@@ -410,7 +415,8 @@ export default {
       )
     },

-    async update({ db, get, params }) {
+    async update({ get, params }) {
+      let db = get(Database)
       let formData = get(FormData)
       let bookId = parseId(params.bookId)
       let book = bookId === undefined ? undefined : await db.find(books, bookId)
@@ -441,7 +447,8 @@ export default {
       return redirect(routes.admin.books.index.href())
     },

-    async destroy({ db, params }) {
+    async destroy({ get, params }) {
+      let db = get(Database)
       let bookId = parseId(params.bookId)
       let book = bookId === undefined ? undefined : await db.find(books, bookId)
       if (book) {
diff --git a/demos/bookstore/app/admin.orders.tsx b/demos/bookstore/app/admin.orders.tsx
index 54293d6ca6a..7aa6cc30a86 100644
--- a/demos/bookstore/app/admin.orders.tsx
+++ b/demos/bookstore/app/admin.orders.tsx
@@ -1,5 +1,6 @@
 import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
+import { Database } from 'remix/data-table'

 import { routes } from './routes.ts'
 import { orders, orderItemsWithBook } from './data/schema.ts'
@@ -9,7 +10,8 @@ import { render } from './utils/render.ts'

 export default {
   actions: {
-    async index({ db }) {
+    async index({ get }) {
+      let db = get(Database)
       let allOrders = await db.findMany(orders, {
         orderBy: ['created_at', 'asc'],
         with: { items: orderItemsWithBook },
@@ -65,7 +67,8 @@ export default {
       )
     },

-    async show({ db, params }) {
+    async show({ get, params }) {
+      let db = get(Database)
       let orderId = parseId(params.orderId)
       let order =
         orderId === undefined
diff --git a/demos/bookstore/app/admin.users.tsx b/demos/bookstore/app/admin.users.tsx
index 3bec00b0bac..d50cb89fd49 100644
--- a/demos/bookstore/app/admin.users.tsx
+++ b/demos/bookstore/app/admin.users.tsx
@@ -2,6 +2,7 @@ import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from './routes.ts'
@@ -24,7 +25,8 @@ const userSchema = f.object({

 export default {
   actions: {
-    async index({ db }) {
+    async index({ get }) {
+      let db = get(Database)
       let user = getCurrentUser()
       let allUsers = await db.findMany(users, { orderBy: ['id', 'asc'] })

@@ -93,7 +95,8 @@ export default {
       )
     },

-    async show({ db, params }) {
+    async show({ get, params }) {
+      let db = get(Database)
       let userId = parseId(params.userId)
       let targetUser = userId === undefined ? undefined : await db.find(users, userId)

@@ -146,7 +149,8 @@ export default {
       )
     },

-    async edit({ db, params }) {
+    async edit({ get, params }) {
+      let db = get(Database)
       let userId = parseId(params.userId)
       let targetUser = userId === undefined ? undefined : await db.find(users, userId)

@@ -208,7 +212,8 @@ export default {
       )
     },

-    async update({ db, get, params }) {
+    async update({ get, params }) {
+      let db = get(Database)
       let formData = get(FormData)
       let userId = parseId(params.userId)
       let targetUser = userId === undefined ? undefined : await db.find(users, userId)
@@ -225,7 +230,8 @@ export default {
       return redirect(routes.admin.users.index.href())
     },

-    async destroy({ db, params }) {
+    async destroy({ get, params }) {
+      let db = get(Database)
       let userId = parseId(params.userId)
       let targetUser = userId === undefined ? undefined : await db.find(users, userId)
       if (targetUser) {
diff --git a/demos/bookstore/app/auth.tsx b/demos/bookstore/app/auth.tsx
index 8957fc92a17..312a3d55e14 100644
--- a/demos/bookstore/app/auth.tsx
+++ b/demos/bookstore/app/auth.tsx
@@ -2,6 +2,7 @@ import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from './routes.ts'
@@ -105,7 +106,8 @@ export default {
           )
         },

-        async action({ db, get, url }) {
+        async action({ get, url }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { email, password } = s.parse(loginSchema, formData)
@@ -168,7 +170,8 @@ export default {
           )
         },

-        async action({ db, get }) {
+        async action({ get }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { email, name, password } = s.parse(registrationSchema, formData)
@@ -249,7 +252,8 @@ export default {
           )
         },

-        async action({ db, get }) {
+        async action({ get }) {
+          let db = get(Database)
           let formData = get(FormData)
           let { email } = s.parse(forgotPasswordSchema, formData)
           let normalizedEmail = normalizeEmail(email)
@@ -358,7 +362,8 @@ export default {
           )
         },

-        async action({ db, get, params }) {
+        async action({ get, params }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { confirmPassword, password } = s.parse(resetPasswordSchema, formData)
diff --git a/demos/bookstore/app/books.tsx b/demos/bookstore/app/books.tsx
index 9dc1f917ac4..21ee9a29579 100644
--- a/demos/bookstore/app/books.tsx
+++ b/demos/bookstore/app/books.tsx
@@ -2,7 +2,7 @@ import type { Controller } from 'remix/fetch-router'
 import { Frame, css } from 'remix/component'

 import { routes } from './routes.ts'
-import { ilike } from 'remix/data-table'
+import { Database, ilike } from 'remix/data-table'

 import { books } from './data/schema.ts'
 import { BookCard } from './components/book-card.tsx'
@@ -15,7 +15,8 @@ import { ImageCarousel } from './assets/image-carousel.tsx'
 export default {
   middleware: [loadAuth()],
   actions: {
-    async index({ db }) {
+    async index({ get }) {
+      let db = get(Database)
       let allBooks = await db.findMany(books, { orderBy: ['id', 'asc'] })
       let genres = await db.query(books).select('genre').distinct().orderBy('genre', 'asc').all()
       let cart = getCurrentCart()
@@ -68,7 +69,8 @@ export default {
       )
     },

-    async genre({ params, db }) {
+    async genre({ get, params }) {
+      let db = get(Database)
       let genre = params.genre
       let matchingBooks = await db.findMany(books, {
         where: ilike('genre', genre),
@@ -113,7 +115,8 @@ export default {
       )
     },

-    async show({ params, db }) {
+    async show({ get, params }) {
+      let db = get(Database)
       let book = await db.findOne(books, { where: { slug: params.slug } })

       if (!book) {
diff --git a/demos/bookstore/app/cart.tsx b/demos/bookstore/app/cart.tsx
index 178d1af5292..3799f72e305 100644
--- a/demos/bookstore/app/cart.tsx
+++ b/demos/bookstore/app/cart.tsx
@@ -1,5 +1,6 @@
 import type { Controller, RequestContext } from 'remix/fetch-router'
 import { Frame } from 'remix/component'
+import { Database } from 'remix/data-table'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
 import { redirect } from 'remix/response/redirect'
@@ -48,7 +49,8 @@ export default {

     api: {
       actions: {
-        async add({ db, get }) {
+        async add({ get }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { bookId, redirect: redirectTo } = s.parse(cartActionSchema, formData)
@@ -75,7 +77,8 @@ export default {
           return redirect(routes.cart.index.href())
         },

-        async update({ db, get }) {
+        async update({ get }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { bookId, quantity, redirect: redirectTo } = s.parse(cartUpdateSchema, formData)
@@ -98,7 +101,8 @@ export default {
           return redirect(routes.cart.index.href())
         },

-        async remove({ db, get }) {
+        async remove({ get }) {
+          let db = get(Database)
           let session = get(Session)
           let formData = get(FormData)
           let { bookId, redirect: redirectTo } = s.parse(cartActionSchema, formData)
@@ -126,7 +130,8 @@ export default {
   },
 } satisfies Controller<typeof routes.cart>

-export async function toggleCart({ db, get }: RequestContext) {
+export async function toggleCart({ get }: RequestContext) {
+  let db = get(Database)
   let session = get(Session)
   let formData = get(FormData)
   let { bookId } = s.parse(bookIdSchema, formData)
diff --git a/demos/bookstore/app/checkout.tsx b/demos/bookstore/app/checkout.tsx
index bb179d39a37..bcb5d96a496 100644
--- a/demos/bookstore/app/checkout.tsx
+++ b/demos/bookstore/app/checkout.tsx
@@ -2,6 +2,7 @@ import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
 import * as s from 'remix/data-schema'
 import * as f from 'remix/data-schema/form-data'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from './routes.ts'
@@ -120,7 +121,8 @@ export default {
       )
     },

-    async action({ db, get }) {
+    async action({ get }) {
+      let db = get(Database)
       let session = get(Session)
       let formData = get(FormData)
       let user = getCurrentUser()
@@ -172,7 +174,8 @@ export default {
       return redirect(routes.checkout.confirmation.href({ orderId: order.id }))
     },

-    async confirmation({ db, params }) {
+    async confirmation({ get, params }) {
+      let db = get(Database)
       let user = getCurrentUser()
       let orderId = parseId(params.orderId)
       let order =
diff --git a/demos/bookstore/app/fragments.tsx b/demos/bookstore/app/fragments.tsx
index 97587b02778..dcc8636a217 100644
--- a/demos/bookstore/app/fragments.tsx
+++ b/demos/bookstore/app/fragments.tsx
@@ -1,5 +1,6 @@
 import type { Controller } from 'remix/fetch-router'
 import { css } from 'remix/component'
+import { Database } from 'remix/data-table'
 import type { routes } from './routes.ts'
 import { CartButton } from './assets/cart-button.tsx'
 import { CartItems } from './assets/cart-items.tsx'
@@ -14,7 +15,8 @@ import { routes as appRoutes } from './routes.ts'
 export default {
   middleware: [loadAuth()],
   actions: {
-    async cartButton({ db, params }) {
+    async cartButton({ get, params }) {
+      let db = get(Database)
       let bookId = parseId(params.bookId)
       let book = bookId === undefined ? undefined : await db.find(books, bookId)

diff --git a/demos/bookstore/app/marketing.tsx b/demos/bookstore/app/marketing.tsx
index c7b63e91d36..672ba4c2da7 100644
--- a/demos/bookstore/app/marketing.tsx
+++ b/demos/bookstore/app/marketing.tsx
@@ -4,13 +4,14 @@ import { css } from 'remix/component'
 import { routes } from './routes.ts'
 import { BookCard } from './components/book-card.tsx'
 import { Layout } from './layout.tsx'
-import { ilike, inList, or } from 'remix/data-table'
+import { Database, ilike, inList, or } from 'remix/data-table'
 import { books } from './data/schema.ts'
 import { render } from './utils/render.ts'
 import { getCurrentCart } from './utils/context.ts'

 export let home: BuildAction<'GET', typeof routes.home> = {
-  async action({ db }) {
+  async action({ get }) {
+    let db = get(Database)
     let cart = getCurrentCart()
     let featuredSlugs = ['bbq', 'heavy-metal', 'three-ways']
     let featuredBookRows = await db.findMany(books, {
@@ -166,7 +167,8 @@ export let contact: Controller<typeof routes.contact> = {
 }

 export let search: BuildAction<'GET', typeof routes.search> = {
-  async action({ db, url }) {
+  async action({ get, url }) {
+    let db = get(Database)
     let query = url.searchParams.get('q') ?? ''
     let matchingBooks = query
       ? await db.findMany(books, {
diff --git a/demos/bookstore/app/middleware/auth.ts b/demos/bookstore/app/middleware/auth.ts
index 87d600d1e5c..00b7c7f7c66 100644
--- a/demos/bookstore/app/middleware/auth.ts
+++ b/demos/bookstore/app/middleware/auth.ts
@@ -1,5 +1,6 @@
 import type { Middleware } from 'remix/fetch-router'
 import type { Route } from 'remix/fetch-router/routes'
+import { Database } from 'remix/data-table'
 import { redirect } from 'remix/response/redirect'

 import { routes } from '../routes.ts'
@@ -14,7 +15,8 @@ import { Session } from '../utils/session.ts'
  * Attaches user (if any) to request context.
  */
 export function loadAuth(): Middleware {
-  return async ({ db, get }) => {
+  return async ({ get }) => {
+    let db = get(Database)
     let session = get(Session)
     let userId = parseId(session.get('userId'))

@@ -43,7 +45,8 @@ export interface RequireAuthOptions {
 export function requireAuth(options?: RequireAuthOptions): Middleware {
   let redirectRoute = options?.redirectTo ?? routes.auth.login.index

-  return async ({ db, get, url }) => {
+  return async ({ get, url }) => {
+    let db = get(Database)
     let session = get(Session)
     let userId = parseId(session.get('userId'))
     let user = userId === undefined ? undefined : await db.find(users, userId)
diff --git a/demos/bookstore/app/middleware/database.ts b/demos/bookstore/app/middleware/database.ts
index 4ee460c7803..65a01674360 100644
--- a/demos/bookstore/app/middleware/database.ts
+++ b/demos/bookstore/app/middleware/database.ts
@@ -1,10 +1,11 @@
 import type { Middleware } from 'remix/fetch-router'
+import { Database } from 'remix/data-table'

 import { db } from '../data/setup.ts'

 export function loadDatabase(): Middleware {
   return async (context, next) => {
-    context.db = db
+    context.set(Database, db)
     return next()
   }
 }
diff --git a/demos/bookstore/app/types/context.db.ts b/demos/bookstore/app/types/context.db.ts
deleted file mode 100644
index d7c1f99dce1..00000000000
--- a/demos/bookstore/app/types/context.db.ts
+++ /dev/null
@@ -1,7 +0,0 @@
-import type { Database } from 'remix/data-table'
-
-declare module 'remix/fetch-router' {
-  interface RequestContext {
-    db: Database
-  }
-}
diff --git a/demos/bookstore/app/utils/context.ts b/demos/bookstore/app/utils/context.ts
index d3077747ae0..4513bd5e551 100644
--- a/demos/bookstore/app/utils/context.ts
+++ b/demos/bookstore/app/utils/context.ts
@@ -7,13 +7,13 @@ import type { User } from '../data/schema.ts'
 import { Session } from './session.ts'

 // Context key for attaching user data to request context
-let USER_KEY = createContextKey<User>()
+const CurrentUser = createContextKey<User>()

 /**
  * Get the current authenticated user from request context.
  */
 export function getCurrentUser(): User {
-  return getContext().get(USER_KEY)
+  return getContext().get(CurrentUser)
 }

 /**
@@ -32,7 +32,7 @@ export function getCurrentUserSafely(): User | null {
  * Set the current authenticated user in request context.
  */
 export function setCurrentUser(user: User): void {
-  getContext().set(USER_KEY, user)
+  getContext().set(CurrentUser, user)
 }

 /**

PATCH

echo "Patch applied successfully."
