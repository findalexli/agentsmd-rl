#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q '# opencode Effect guide' packages/opencode/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/opencode/AGENTS.md b/packages/opencode/AGENTS.md
index dcfc336d6525..930297baa9f2 100644
--- a/packages/opencode/AGENTS.md
+++ b/packages/opencode/AGENTS.md
@@ -8,3 +8,37 @@
 - **Command**: `bun run db generate --name <slug>`.
 - **Output**: creates `migration/<timestamp>_<slug>/migration.sql` and `snapshot.json`.
 - **Tests**: migration tests should read the per-folder layout (no `_journal.json`).
+
+# opencode Effect guide
+
+Instructions to follow when writing Effect.
+
+## Schemas
+
+- Use `Schema.Class` for data types with multiple fields.
+- Use branded schemas (`Schema.brand`) for single-value types.
+
+## Services
+
+- Services use `ServiceMap.Service<ServiceName, ServiceName.Service>()("@console/<Name>")`.
+- In `Layer.effect`, always return service implementations with `ServiceName.of({ ... })`, never a plain object.
+
+## Errors
+
+- Use `Schema.TaggedErrorClass` for typed errors.
+- For defect-like causes, use `Schema.Defect` instead of `unknown`.
+- In `Effect.gen`, prefer `yield* new MyError(...)` over `yield* Effect.fail(new MyError(...))` for direct early-failure branches.
+
+## Effects
+
+- Use `Effect.gen(function* () { ... })` for composition.
+- Use `Effect.fn("ServiceName.method")` for named/traced effects and `Effect.fnUntraced` for internal helpers.
+- `Effect.fn` / `Effect.fnUntraced` accept pipeable operators as extra arguments, so avoid unnecessary `flow` or outer `.pipe()` wrappers.
+
+## Time
+
+- Prefer `DateTime.nowAsDate` over `new Date(yield* Clock.currentTimeMillis)` when you need a `Date`.
+
+## Errors
+
+- In `Effect.gen/fn`, prefer `yield* new MyError(...)` over `yield* Effect.fail(new MyError(...))` for direct early-failure branches.
diff --git a/packages/opencode/src/account/account.sql.ts b/packages/opencode/src/account/account.sql.ts
index e66b3c299280..35bfd1e3ed4c 100644
--- a/packages/opencode/src/account/account.sql.ts
+++ b/packages/opencode/src/account/account.sql.ts
@@ -1,20 +1,24 @@
 import { sqliteTable, text, integer, primaryKey } from "drizzle-orm/sqlite-core"
+
+import { type AccessToken, type AccountID, type OrgID, type RefreshToken } from "./schema"
 import { Timestamps } from "../storage/schema.sql"
 
 export const AccountTable = sqliteTable("account", {
-  id: text().primaryKey(),
+  id: text().$type<AccountID>().primaryKey(),
   email: text().notNull(),
   url: text().notNull(),
-  access_token: text().notNull(),
-  refresh_token: text().notNull(),
+  access_token: text().$type<AccessToken>().notNull(),
+  refresh_token: text().$type<RefreshToken>().notNull(),
   token_expiry: integer(),
   ...Timestamps,
 })
 
 export const AccountStateTable = sqliteTable("account_state", {
   id: integer().primaryKey(),
-  active_account_id: text().references(() => AccountTable.id, { onDelete: "set null" }),
-  active_org_id: text(),
+  active_account_id: text()
+    .$type<AccountID>()
+    .references(() => AccountTable.id, { onDelete: "set null" }),
+  active_org_id: text().$type<OrgID>(),
 })
 
 // LEGACY
@@ -23,8 +27,8 @@ export const ControlAccountTable = sqliteTable(
   {
     email: text().notNull(),
     url: text().notNull(),
-    access_token: text().notNull(),
-    refresh_token: text().notNull(),
+    access_token: text().$type<AccessToken>().notNull(),
+    refresh_token: text().$type<RefreshToken>().notNull(),
     token_expiry: integer(),
     active: integer({ mode: "boolean" })
       .notNull()
diff --git a/packages/opencode/src/account/index.ts b/packages/opencode/src/account/index.ts
index b48ada1fb589..ed4c3d879882 100644
--- a/packages/opencode/src/account/index.ts
+++ b/packages/opencode/src/account/index.ts
@@ -1,4 +1,4 @@
-import { Effect, Option, ServiceMap } from "effect"
+import { Effect, Option } from "effect"
 
 import {
   Account as AccountSchema,
@@ -13,13 +13,11 @@ export { AccessToken, AccountID, OrgID } from "./service"
 
 import { runtime } from "@/effect/runtime"
 
-type AccountServiceShape = ServiceMap.Service.Shape<typeof AccountService>
-
-function runSync<A>(f: (service: AccountServiceShape) => Effect.Effect<A, AccountError>) {
+function runSync<A>(f: (service: AccountService.Service) => Effect.Effect<A, AccountError>) {
   return runtime.runSync(AccountService.use(f))
 }
 
-function runPromise<A>(f: (service: AccountServiceShape) => Effect.Effect<A, AccountError>) {
+function runPromise<A>(f: (service: AccountService.Service) => Effect.Effect<A, AccountError>) {
   return runtime.runPromise(AccountService.use(f))
 }
 
diff --git a/packages/opencode/src/account/repo.ts b/packages/opencode/src/account/repo.ts
index 65f56727b9b0..5caf1a3b9461 100644
--- a/packages/opencode/src/account/repo.ts
+++ b/packages/opencode/src/account/repo.ts
@@ -3,43 +3,16 @@ import { Effect, Layer, Option, Schema, ServiceMap } from "effect"
 
 import { Database } from "@/storage/db"
 import { AccountStateTable, AccountTable } from "./account.sql"
-import { Account, AccountID, AccountRepoError, OrgID } from "./schema"
+import { AccessToken, Account, AccountID, AccountRepoError, OrgID, RefreshToken } from "./schema"
 
 export type AccountRow = (typeof AccountTable)["$inferSelect"]
 
-const decodeAccount = Schema.decodeUnknownSync(Account)
-
 type DbClient = Parameters<typeof Database.use>[0] extends (db: infer T) => unknown ? T : never
 
 const ACCOUNT_STATE_ID = 1
 
-const db = <A>(run: (db: DbClient) => A) =>
-  Effect.try({
-    try: () => Database.use(run),
-    catch: (cause) => new AccountRepoError({ message: "Database operation failed", cause }),
-  })
-
-const current = (db: DbClient) => {
-  const state = db.select().from(AccountStateTable).where(eq(AccountStateTable.id, ACCOUNT_STATE_ID)).get()
-  if (!state?.active_account_id) return
-  const account = db.select().from(AccountTable).where(eq(AccountTable.id, state.active_account_id)).get()
-  if (!account) return
-  return { ...account, active_org_id: state.active_org_id ?? null }
-}
-
-const setState = (db: DbClient, accountID: AccountID, orgID: string | null) =>
-  db
-    .insert(AccountStateTable)
-    .values({ id: ACCOUNT_STATE_ID, active_account_id: accountID, active_org_id: orgID })
-    .onConflictDoUpdate({
-      target: AccountStateTable.id,
-      set: { active_account_id: accountID, active_org_id: orgID },
-    })
-    .run()
-
-export class AccountRepo extends ServiceMap.Service<
-  AccountRepo,
-  {
+export namespace AccountRepo {
+  export interface Service {
     readonly active: () => Effect.Effect<Option.Option<Account>, AccountRepoError>
     readonly list: () => Effect.Effect<Account[], AccountRepoError>
     readonly remove: (accountID: AccountID) => Effect.Effect<void, AccountRepoError>
@@ -47,62 +20,96 @@ export class AccountRepo extends ServiceMap.Service<
     readonly getRow: (accountID: AccountID) => Effect.Effect<Option.Option<AccountRow>, AccountRepoError>
     readonly persistToken: (input: {
       accountID: AccountID
-      accessToken: string
-      refreshToken: string
+      accessToken: AccessToken
+      refreshToken: RefreshToken
       expiry: Option.Option<number>
     }) => Effect.Effect<void, AccountRepoError>
     readonly persistAccount: (input: {
       id: AccountID
       email: string
       url: string
-      accessToken: string
-      refreshToken: string
+      accessToken: AccessToken
+      refreshToken: RefreshToken
       expiry: number
       orgID: Option.Option<OrgID>
     }) => Effect.Effect<void, AccountRepoError>
   }
->()("@opencode/AccountRepo") {
-  static readonly layer: Layer.Layer<AccountRepo> = Layer.succeed(
+}
+
+export class AccountRepo extends ServiceMap.Service<AccountRepo, AccountRepo.Service>()("@opencode/AccountRepo") {
+  static readonly layer: Layer.Layer<AccountRepo> = Layer.effect(
     AccountRepo,
-    AccountRepo.of({
-      active: Effect.fn("AccountRepo.active")(() =>
-        db((db) => current(db)).pipe(Effect.map((row) => (row ? Option.some(decodeAccount(row)) : Option.none()))),
-      ),
+    Effect.gen(function* () {
+      const decode = Schema.decodeUnknownSync(Account)
+
+      const query = <A>(f: (db: DbClient) => A) =>
+        Effect.try({
+          try: () => Database.use(f),
+          catch: (cause) => new AccountRepoError({ message: "Database operation failed", cause }),
+        })
+
+      const tx = <A>(f: (db: DbClient) => A) =>
+        Effect.try({
+          try: () => Database.transaction(f),
+          catch: (cause) => new AccountRepoError({ message: "Database operation failed", cause }),
+        })
+
+      const current = (db: DbClient) => {
+        const state = db.select().from(AccountStateTable).where(eq(AccountStateTable.id, ACCOUNT_STATE_ID)).get()
+        if (!state?.active_account_id) return
+        const account = db.select().from(AccountTable).where(eq(AccountTable.id, state.active_account_id)).get()
+        if (!account) return
+        return { ...account, active_org_id: state.active_org_id ?? null }
+      }
+
+      const state = (db: DbClient, accountID: AccountID, orgID: Option.Option<OrgID>) => {
+        const id = Option.getOrNull(orgID)
+        return db
+          .insert(AccountStateTable)
+          .values({ id: ACCOUNT_STATE_ID, active_account_id: accountID, active_org_id: id })
+          .onConflictDoUpdate({
+            target: AccountStateTable.id,
+            set: { active_account_id: accountID, active_org_id: id },
+          })
+          .run()
+      }
 
-      list: Effect.fn("AccountRepo.list")(() =>
-        db((db) =>
+      const active = Effect.fn("AccountRepo.active")(() =>
+        query((db) => current(db)).pipe(Effect.map((row) => (row ? Option.some(decode(row)) : Option.none()))),
+      )
+
+      const list = Effect.fn("AccountRepo.list")(() =>
+        query((db) =>
           db
             .select()
             .from(AccountTable)
             .all()
-            .map((row) => decodeAccount({ ...row, active_org_id: null })),
+            .map((row: AccountRow) => decode({ ...row, active_org_id: null })),
         ),
-      ),
-
-      remove: Effect.fn("AccountRepo.remove")((accountID: AccountID) =>
-        db((db) =>
-          Database.transaction((tx) => {
-            tx.update(AccountStateTable)
-              .set({ active_account_id: null, active_org_id: null })
-              .where(eq(AccountStateTable.active_account_id, accountID))
-              .run()
-            tx.delete(AccountTable).where(eq(AccountTable.id, accountID)).run()
-          }),
-        ).pipe(Effect.asVoid),
-      ),
+      )
+
+      const remove = Effect.fn("AccountRepo.remove")((accountID: AccountID) =>
+        tx((db) => {
+          db.update(AccountStateTable)
+            .set({ active_account_id: null, active_org_id: null })
+            .where(eq(AccountStateTable.active_account_id, accountID))
+            .run()
+          db.delete(AccountTable).where(eq(AccountTable.id, accountID)).run()
+        }).pipe(Effect.asVoid),
+      )
 
-      use: Effect.fn("AccountRepo.use")((accountID: AccountID, orgID: Option.Option<OrgID>) =>
-        db((db) => setState(db, accountID, Option.getOrNull(orgID))).pipe(Effect.asVoid),
-      ),
+      const use = Effect.fn("AccountRepo.use")((accountID: AccountID, orgID: Option.Option<OrgID>) =>
+        query((db) => state(db, accountID, orgID)).pipe(Effect.asVoid),
+      )
 
-      getRow: Effect.fn("AccountRepo.getRow")((accountID: AccountID) =>
-        db((db) => db.select().from(AccountTable).where(eq(AccountTable.id, accountID)).get()).pipe(
+      const getRow = Effect.fn("AccountRepo.getRow")((accountID: AccountID) =>
+        query((db) => db.select().from(AccountTable).where(eq(AccountTable.id, accountID)).get()).pipe(
           Effect.map(Option.fromNullishOr),
         ),
-      ),
+      )
 
-      persistToken: Effect.fn("AccountRepo.persistToken")((input) =>
-        db((db) =>
+      const persistToken = Effect.fn("AccountRepo.persistToken")((input) =>
+        query((db) =>
           db
             .update(AccountTable)
             .set({
@@ -113,34 +120,41 @@ export class AccountRepo extends ServiceMap.Service<
             .where(eq(AccountTable.id, input.accountID))
             .run(),
         ).pipe(Effect.asVoid),
-      ),
-
-      persistAccount: Effect.fn("AccountRepo.persistAccount")((input) => {
-        const orgID = Option.getOrNull(input.orgID)
-        return db((db) =>
-          Database.transaction((tx) => {
-            tx.insert(AccountTable)
-              .values({
-                id: input.id,
-                email: input.email,
-                url: input.url,
+      )
+
+      const persistAccount = Effect.fn("AccountRepo.persistAccount")((input) =>
+        tx((db) => {
+          db.insert(AccountTable)
+            .values({
+              id: input.id,
+              email: input.email,
+              url: input.url,
+              access_token: input.accessToken,
+              refresh_token: input.refreshToken,
+              token_expiry: input.expiry,
+            })
+            .onConflictDoUpdate({
+              target: AccountTable.id,
+              set: {
                 access_token: input.accessToken,
                 refresh_token: input.refreshToken,
                 token_expiry: input.expiry,
-              })
-              .onConflictDoUpdate({
-                target: AccountTable.id,
-                set: {
-                  access_token: input.accessToken,
-                  refresh_token: input.refreshToken,
-                  token_expiry: input.expiry,
-                },
-              })
-              .run()
-            setState(tx, input.id, orgID)
-          }),
-        ).pipe(Effect.asVoid)
-      }),
+              },
+            })
+            .run()
+          void state(db, input.id, input.orgID)
+        }).pipe(Effect.asVoid),
+      )
+
+      return AccountRepo.of({
+        active,
+        list,
+        remove,
+        use,
+        getRow,
+        persistToken,
+        persistAccount,
+      })
     }),
   )
 }
diff --git a/packages/opencode/src/account/schema.ts b/packages/opencode/src/account/schema.ts
index 49c37932ff46..6b62484ab66a 100644
--- a/packages/opencode/src/account/schema.ts
+++ b/packages/opencode/src/account/schema.ts
@@ -20,6 +20,24 @@ export const AccessToken = Schema.String.pipe(
 )
 export type AccessToken = Schema.Schema.Type<typeof AccessToken>
 
+export const RefreshToken = Schema.String.pipe(
+  Schema.brand("RefreshToken"),
+  withStatics((s) => ({ make: (token: string) => s.makeUnsafe(token) })),
+)
+export type RefreshToken = Schema.Schema.Type<typeof RefreshToken>
+
+export const DeviceCode = Schema.String.pipe(
+  Schema.brand("DeviceCode"),
+  withStatics((s) => ({ make: (code: string) => s.makeUnsafe(code) })),
+)
+export type DeviceCode = Schema.Schema.Type<typeof DeviceCode>
+
+export const UserCode = Schema.String.pipe(
+  Schema.brand("UserCode"),
+  withStatics((s) => ({ make: (code: string) => s.makeUnsafe(code) })),
+)
+export type UserCode = Schema.Schema.Type<typeof UserCode>
+
 export class Account extends Schema.Class<Account>("Account")({
   id: AccountID,
   email: Schema.String,
@@ -45,12 +63,12 @@ export class AccountServiceError extends Schema.TaggedErrorClass<AccountServiceE
 export type AccountError = AccountRepoError | AccountServiceError
 
 export class Login extends Schema.Class<Login>("Login")({
-  code: Schema.String,
-  user: Schema.String,
+  code: DeviceCode,
+  user: UserCode,
   url: Schema.String,
   server: Schema.String,
-  expiry: Schema.Number,
-  interval: Schema.Number,
+  expiry: Schema.Duration,
+  interval: Schema.Duration,
 }) {}
 
 export class PollSuccess extends Schema.TaggedClass<PollSuccess>()("PollSuccess", {
diff --git a/packages/opencode/src/account/service.ts b/packages/opencode/src/account/service.ts
index ab1de72557fd..87e95c8f444d 100644
--- a/packages/opencode/src/account/service.ts
+++ b/packages/opencode/src/account/service.ts
@@ -1,11 +1,5 @@
-import { Clock, Effect, Layer, Option, Schema, ServiceMap } from "effect"
-import {
-  FetchHttpClient,
-  HttpClient,
-  HttpClientError,
-  HttpClientRequest,
-  HttpClientResponse,
-} from "effect/unstable/http"
+import { Clock, Duration, Effect, Layer, Option, Schema, SchemaGetter, ServiceMap } from "effect"
+import { FetchHttpClient, HttpClient, HttpClientRequest, HttpClientResponse } from "effect/unstable/http"
 
 import { withTransientReadRetry } from "@/util/effect-http-client"
 import { AccountRepo, type AccountRow } from "./repo"
@@ -14,6 +8,8 @@ import {
   AccessToken,
   Account,
   AccountID,
+  DeviceCode,
+  RefreshToken,
   AccountServiceError,
   Login,
   Org,
@@ -25,83 +21,101 @@ import {
   type PollResult,
   PollSlow,
   PollSuccess,
+  UserCode,
 } from "./schema"
 
 export * from "./schema"
 
 export type AccountOrgs = {
   account: Account
-  orgs: Org[]
+  orgs: readonly Org[]
 }
 
-const RemoteOrg = Schema.Struct({
-  id: Schema.optional(OrgID),
-  name: Schema.optional(Schema.String),
-})
+class RemoteConfig extends Schema.Class<RemoteConfig>("RemoteConfig")({
+  config: Schema.Record(Schema.String, Schema.Json),
+}) {}
+
+const DurationFromSeconds = Schema.Number.pipe(
+  Schema.decodeTo(Schema.Duration, {
+    decode: SchemaGetter.transform((n) => Duration.seconds(n)),
+    encode: SchemaGetter.transform((d) => Duration.toSeconds(d)),
+  }),
+)
+
+class TokenRefresh extends Schema.Class<TokenRefresh>("TokenRefresh")({
+  access_token: AccessToken,
+  refresh_token: RefreshToken,
+  expires_in: DurationFromSeconds,
+}) {}
+
+class DeviceAuth extends Schema.Class<DeviceAuth>("DeviceAuth")({
+  device_code: DeviceCode,
+  user_code: UserCode,
+  verification_uri_complete: Schema.String,
+  expires_in: DurationFromSeconds,
+  interval: DurationFromSeconds,
+}) {}
+
+class DeviceTokenSuccess extends Schema.Class<DeviceTokenSuccess>("DeviceTokenSuccess")({
+  access_token: AccessToken,
+  refresh_token: RefreshToken,
+  token_type: Schema.Literal("Bearer"),
+  expires_in: DurationFromSeconds,
+}) {}
+
+class DeviceTokenError extends Schema.Class<DeviceTokenError>("DeviceTokenError")({
+  error: Schema.String,
+  error_description: Schema.String,
+}) {
+  toPollResult(): PollResult {
+    if (this.error === "authorization_pending") return new PollPending()
+    if (this.error === "slow_down") return new PollSlow()
+    if (this.error === "expired_token") return new PollExpired()
+    if (this.error === "access_denied") return new PollDenied()
+    return new PollError({ cause: this.error })
+  }
+}
 
-const RemoteOrgs = Schema.Array(RemoteOrg)
+const DeviceToken = Schema.Union([DeviceTokenSuccess, DeviceTokenError])
 
-const RemoteConfig = Schema.Struct({
-  config: Schema.Record(Schema.String, Schema.Json),
-})
+class User extends Schema.Class<User>("User")({
+  id: AccountID,
+  email: Schema.String,
+}) {}
 
-const TokenRefresh = Schema.Struct({
-  access_token: Schema.String,
-  refresh_token: Schema.optional(Schema.String),
-  expires_in: Schema.optional(Schema.Number),
-})
+class ClientId extends Schema.Class<ClientId>("ClientId")({ client_id: Schema.String }) {}
 
-const DeviceCode = Schema.Struct({
-  device_code: Schema.String,
-  user_code: Schema.String,
-  verification_uri_complete: Schema.String,
-  expires_in: Schema.Number,
-  interval: Schema.Number,
-})
-
-const DeviceToken = Schema.Struct({
-  access_token: Schema.optional(Schema.String),
-  refresh_token: Schema.optional(Schema.String),
-  expires_in: Schema.optional(Schema.Number),
-  error: Schema.optional(Schema.String),
-  error_description: Schema.optional(Schema.String),
-})
-
-const User = Schema.Struct({
-  id: Schema.optional(AccountID),
-  email: Schema.optional(Schema.String),
-})
-
-const ClientId = Schema.Struct({ client_id: Schema.String })
-
-const DeviceTokenRequest = Schema.Struct({
+class DeviceTokenRequest extends Schema.Class<DeviceTokenRequest>("DeviceTokenRequest")({
   grant_type: Schema.String,
-  device_code: Schema.String,
+  device_code: DeviceCode,
   client_id: Schema.String,
-})
+}) {}
 
-const clientId = "opencode-cli"
+class TokenRefreshRequest extends Schema.Class<TokenRefreshRequest>("TokenRefreshRequest")({
+  grant_type: Schema.String,
+  refresh_token: RefreshToken,
+  client_id: Schema.String,
+}) {}
 
-const toAccountServiceError = (message: string, cause?: unknown) => new AccountServiceError({ message, cause })
+const clientId = "opencode-cli"
 
 const mapAccountServiceError =
-  (operation: string, message = "Account service operation failed") =>
+  (message = "Account service operation failed") =>
   <A, E, R>(effect: Effect.Effect<A, E, R>): Effect.Effect<A, AccountServiceError, R> =>
     effect.pipe(
-      Effect.mapError((error) =>
-        error instanceof AccountServiceError ? error : toAccountServiceError(`${message} (${operation})`, error),
+      Effect.mapError((cause) =>
+        cause instanceof AccountServiceError ? cause : new AccountServiceError({ message, cause }),
       ),
     )
 
-export class AccountService extends ServiceMap.Service<
-  AccountService,
-  {
+export namespace AccountService {
+  export interface Service {
     readonly active: () => Effect.Effect<Option.Option<Account>, AccountError>
     readonly list: () => Effect.Effect<Account[], AccountError>
-    readonly orgsByAccount: () => Effect.Effect<AccountOrgs[], AccountError>
+    readonly orgsByAccount: () => Effect.Effect<readonly AccountOrgs[], AccountError>
     readonly remove: (accountID: AccountID) => Effect.Effect<void, AccountError>
     readonly use: (accountID: AccountID, orgID: Option.Option<OrgID>) => Effect.Effect<void, AccountError>
-    readonly orgs: (accountID: AccountID) => Effect.Effect<Org[], AccountError>
+    readonly orgs: (accountID: AccountID) => Effect.Effect<readonly Org[], AccountError>
     readonly config: (
       accountID: AccountID,
       orgID: OrgID,
@@ -110,80 +124,98 @@ export class AccountService extends ServiceMap.Service<
     readonly login: (url: string) => Effect.Effect<Login, AccountError>
     readonly poll: (input: Login) => Effect.Effect<PollResult, AccountError>
   }
->()("@opencode/Account") {
+}
+
+export class AccountService extends ServiceMap.Service<AccountService, AccountService.Service>()("@opencode/Account") {
   static readonly layer: Layer.Layer<AccountService, never, AccountRepo | HttpClient.HttpClient> = Layer.effect(
     AccountService,
     Effect.gen(function* () {
       const repo = yield* AccountRepo
       const http = yield* HttpClient.HttpClient
       const httpRead = withTransientReadRetry(http)
+      const httpOk = HttpClient.filterStatusOk(http)
+      const httpReadOk = HttpClient.filterStatusOk(httpRead)
 
-      const execute = (operation: string, request: HttpClientRequest.HttpClientRequest) =>
-        http.execute(request).pipe(mapAccountServiceError(operation, "HTTP request failed"))
+      const executeRead = (request: HttpClientRequest.HttpClientRequest) =>
+        httpRead.execute(request).pipe(mapAccountServiceError("HTTP request failed"))
 
-      const executeRead = (operation: string, request: HttpClientRequest.HttpClientRequest) =>
-        httpRead.execute(request).pipe(mapAccountServiceError(operation, "HTTP request failed"))
+      const executeReadOk = (request: HttpClientRequest.HttpClientRequest) =>
+        httpReadOk.execute(request).pipe(mapAccountServiceError("HTTP request failed"))
 
-      const executeEffect = <E>(operation: string, request: Effect.Effect<HttpClientRequest.HttpClientRequest, E>) =>
+      const executeEffectOk = <E>(request: Effect.Effect<HttpClientRequest.HttpClientRequest, E>) =>
         request.pipe(
-          Effect.flatMap((req) => http.execute(req)),
-          mapAccountServiceError(operation, "HTTP request failed"),
-        )
-
-      const okOrNone = (operation: string, response: HttpClientResponse.HttpClientResponse) =>
-        HttpClientResponse.filterStatusOk(response).pipe(
-          Effect.map(Option.some),
-          Effect.catch((error) =>
-            HttpClientError.isHttpClientError(error) && error.reason._tag === "StatusCodeError"
-              ? Effect.succeed(Option.none<HttpClientResponse.HttpClientResponse>())
-              : Effect.fail(error),
-          ),
-          mapAccountServiceError(operation),
+          Effect.flatMap((req) => httpOk.execute(req)),
+          mapAccountServiceError("HTTP request failed"),
         )
 
-      const tokenForRow = Effect.fn("AccountService.tokenForRow")(function* (found: AccountRow) {
+      // Returns a usable access token for a stored account row, refreshing and
+      // persisting it when the cached token has expired.
+      const resolveToken = Effect.fnUntraced(function* (row: AccountRow) {
         const now = yield* Clock.currentTimeMillis
-        if (found.token_expiry && found.token_expiry > now) return Option.some(AccessToken.make(found.access_token))
+        if (row.token_expiry && row.token_expiry > now) return row.access_token
 
-        const response = yield* execute(
-          "token.refresh",
-          HttpClientRequest.post(`${found.url}/oauth/token`).pipe(
+        const response = yield* executeEffectOk(
+          HttpClientRequest.post(`${row.url}/auth/device/token`).pipe(
             HttpClientRequest.acceptJson,
-            HttpClientRequest.bodyUrlParams({
-              grant_type: "refresh_token",
-              refresh_token: found.refresh_token,
-            }),
+            HttpClientRequest.schemaBodyJson(TokenRefreshRequest)(
+              new TokenRefreshRequest({
+                grant_type: "refresh_token",
+                refresh_token: row.refresh_token,
+                client_id: clientId,
+              }),
+            ),
           ),
         )
 
-        const ok = yield* okOrNone("token.refresh", response)
-        if (Option.isNone(ok)) return Option.none()
-
-        const parsed = yield* HttpClientResponse.schemaBodyJson(TokenRefresh)(ok.value).pipe(
-          mapAccountServiceError("token.refresh", "Failed to decode response"),
+        const parsed = yield* HttpClientResponse.schemaBodyJson(TokenRefresh)(response).pipe(
+          mapAccountServiceError("Failed to decode response"),
         )
 
-        const expiry = Option.fromNullishOr(parsed.expires_in).pipe(Option.map((e) => now + e * 1000))
+        const expiry = Option.some(now + Duration.toMillis(parsed.expires_in))
 
         yield* repo.persistToken({
-          accountID: AccountID.make(found.id),
+          accountID: row.id,
           accessToken: parsed.access_token,
-          refreshToken: parsed.refresh_token ?? found.refresh_token,
+          refreshToken: parsed.refresh_token,
           expiry,
         })
 
-        return Option.some(AccessToken.make(parsed.access_token))
+        return parsed.access_token
       })
 
-      const resolveAccess = Effect.fn("AccountService.resolveAccess")(function* (accountID: AccountID) {
+      const resolveAccess = Effect.fnUntraced(function* (accountID: AccountID) {
         const maybeAccount = yield* repo.getRow(accountID)
-        if (Option.isNone(maybeAccount)) return Option.none<{ account: AccountRow; accessToken: AccessToken }>()
+        if (Option.isNone(maybeAccount)) return Option.none()
 
         const account = maybeAccount.value
-        const accessToken = yield* tokenForRow(account)
-        if (Option.isNone(accessToken)) return Option.none<{ account: AccountRow; accessToken: AccessToken }>()
+        const accessToken = yield* resolveToken(account)
+        return Option.some({ account, accessToken })
+      })
+
+      const fetchOrgs = Effect.fnUntraced(function* (url: string, accessToken: AccessToken) {
+        const response = yield* executeReadOk(
+          HttpClientRequest.get(`${url}/api/orgs`).pipe(
+            HttpClientRequest.acceptJson,
+            HttpClientRequest.bearerToken(accessToken),
+          ),
+        )
 
-        return Option.some({ account, accessToken: accessToken.value })
+        return yield* HttpClientResponse.schemaBodyJson(Schema.Array(Org))(response).pipe(
+          mapAccountServiceError("Failed to decode response"),
+        )
+      })
+
+      const fetchUser = Effect.fnUntraced(function* (url: string, accessToken: AccessToken) {
+        const response = yield* executeReadOk(
+          HttpClientRequest.get(`${url}/api/user`).pipe(
+            HttpClientRequest.acceptJson,
+            HttpClientRequest.bearerToken(accessToken),
+          ),
+        )
+
+        return yield* HttpClientResponse.schemaBodyJson(User)(response).pipe(
+          mapAccountServiceError("Failed to decode response"),
+        )
       })
 
       const token = Effect.fn("AccountService.token")((accountID: AccountID) =>
@@ -211,23 +243,7 @@ export class AccountService extends ServiceMap.Service<
 
         const { account, accessToken } = resolved.value
 
-        const response = yield* executeRead(
-          "orgs",
-          HttpClientRequest.get(`${account.url}/api/orgs`).pipe(
-            HttpClientRequest.acceptJson,
-            HttpClientRequest.bearerToken(accessToken),
-          ),
-        )
-
-        const ok = yield* okOrNone("orgs", response)
-        if (Option.isNone(ok)) return []
-
-        const orgs = yield* HttpClientResponse.schemaBodyJson(RemoteOrgs)(ok.value).pipe(
-          mapAccountServiceError("orgs", "Failed to decode response"),
-        )
-        return orgs
-          .filter((org) => org.id !== undefined && org.name !== undefined)
-          .map((org) => new Org({ id: org.id!, name: org.name! }))
+        return yield* fetchOrgs(account.url, accessToken)
       })
 
       const config = Effect.fn("AccountService.config")(function* (accountID: AccountID, orgID: OrgID) {
@@ -237,7 +253,6 @@ export class AccountService extends ServiceMap.Service<
         const { account, accessToken } = resolved.value
 
         const response = yield* executeRead(
-          "config",
           HttpClientRequest.get(`${account.url}/api/config`).pipe(
             HttpClientRequest.acceptJson,
             HttpClientRequest.bearerToken(accessToken),
@@ -245,32 +260,26 @@ export class AccountService extends ServiceMap.Service<
           ),
         )
 
-        const ok = yield* okOrNone("config", response)
-        if (Option.isNone(ok)) return Option.none()
+        if (response.status === 404) return Option.none()
+
+        const ok = yield* HttpClientResponse.filterStatusOk(response).pipe(mapAccountServiceError())
 
-        const parsed = yield* HttpClientResponse.schemaBodyJson(RemoteConfig)(ok.value).pipe(
-          mapAccountServiceError("config", "Failed to decode response"),
+        const parsed = yield* HttpClientResponse.schemaBodyJson(RemoteConfig)(ok).pipe(
+          mapAccountServiceError("Failed to decode response"),
         )
         return Option.some(parsed.config)
       })
 
       const login = Effect.fn("AccountService.login")(function* (server: string) {
-        const response = yield* executeEffect(
-          "login",
+        const response = yield* executeEffectOk(
           HttpClientRequest.post(`${server}/auth/device/code`).pipe(
             HttpClientRequest.acceptJson,
-            HttpClientRequest.schemaBodyJson(ClientId)({ client_id: clientId }),
+            HttpClientRequest.schemaBodyJson(ClientId)(new ClientId({ client_id: clientId })),
           ),
         )
 
-        const ok = yield* okOrNone("login", response)
-        if (Option.isNone(ok)) {
-          const body = yield* response.text.pipe(Effect.orElseSucceed(() => ""))
-          return yield* toAccountServiceError(`Failed to initiate device flow: ${body || response.status}`)
-        }
-
-        const parsed = yield* HttpClientResponse.schemaBodyJson(DeviceCode)(ok.value).pipe(
-          mapAccountServiceError("login", "Failed to decode response"),
+        const parsed = yield* HttpClientResponse.schemaBodyJson(DeviceAuth)(response).pipe(
+          mapAccountServiceError("Failed to decode response"),
         )
         return new Login({
           code: parsed.device_code,
@@ -283,91 +292,49 @@ export class AccountService extends ServiceMap.Service<
       })
 
       const poll = Effect.fn("AccountService.poll")(function* (input: Login) {
-        const response = yield* executeEffect(
-          "poll",
+        const response = yield* executeEffectOk(
           HttpClientRequest.post(`${input.server}/auth/device/token`).pipe(
             HttpClientRequest.acceptJson,
-            HttpClientRequest.schemaBodyJson(DeviceTokenRequest)({
-              grant_type: "urn:ietf:params:oauth:grant-type:device_code",
-              device_code: input.code,
-              client_id: clientId,
-            }),
-          ),
-        )
-
-        const parsed = yield* HttpClientResponse.schemaBodyJson(DeviceToken)(response).pipe(
-          mapAccountServiceError("poll", "Failed to decode response"),
-        )
-
-        if (!parsed.access_token) {
-          if (parsed.error === "authorization_pending") return new PollPending()
-          if (parsed.error === "slow_down") return new PollSlow()
-          if (parsed.error === "expired_token") return new PollExpired()
-          if (parsed.error === "access_denied") return new PollDenied()
-          return new PollError({ cause: parsed.error })
-        }
-
-        const access = parsed.access_token
-
-        const fetchUser = executeRead(
-          "poll.user",
-          HttpClientRequest.get(`${input.server}/api/user`).pipe(
-            HttpClientRequest.acceptJson,
-            HttpClientRequest.bearerToken(access),
-          ),
-        ).pipe(
-          Effect.flatMap((r) =>
-            HttpClientResponse.schemaBodyJson(User)(r).pipe(
-              mapAccountServiceError("poll.user", "Failed to decode response"),
+            HttpClientRequest.schemaBodyJson(DeviceTokenRequest)(
+              new DeviceTokenRequest({
+                grant_type: "urn:ietf:params:oauth:grant-type:device_code",
+                device_code: input.code,
+                client_id: clientId,
+              }),
             ),
           ),
         )
 
-        const fetchOrgs = executeRead(
-          "poll.orgs",
-          HttpClientRequest.get(`${input.server}/api/orgs`).pipe(
-            HttpClientRequest.acceptJson,
-            HttpClientRequest.bearerToken(access),
-          ),
-        ).pipe(
-          Effect.flatMap((r) =>
-            HttpClientResponse.schemaBodyJson(RemoteOrgs)(r).pipe(
-              mapAccountServiceError("poll.orgs", "Failed to decode response"),
-            ),
-          ),
+        const parsed = yield* HttpClientResponse.schemaBodyJson(DeviceToken)(response).pipe(
+          mapAccountServiceError("Failed to decode response"),
         )
 
-        const [user, remoteOrgs] = yield* Effect.all([fetchUser, fetchOrgs], { concurrency: 2 })
+        if (parsed instanceof DeviceTokenError) return parsed.toPollResult()
+        const accessToken = parsed.access_token
 
-        const userId = user.id
-        const userEmail = user.email
+        const user = fetchUser(input.server, accessToken)
+        const orgs = fetchOrgs(input.server, accessToken)
 
-        if (!userId || !userEmail) {
-          return new PollError({ cause: "No id or email in response" })
-        }
+        const [account, remoteOrgs] = yield* Effect.all([user, orgs], { concurrency: 2 })
 
-        const firstOrgID = remoteOrgs.length > 0 ? Option.fromNullishOr(remoteOrgs[0].id) : Option.none()
+        // TODO: When there are multiple orgs, let the user choose
+        const firstOrgID = remoteOrgs.length > 0 ? Option.some(remoteOrgs[0].id) : Option.none<OrgID>()
 
         const now = yield* Clock.currentTimeMillis
-        const expiry = now + (parsed.expires_in ?? 0) * 1000
-        const refresh = parsed.refresh_token ?? ""
-        if (!refresh) {
-          yield* Effect.logWarning(
-            "Server did not return a refresh token — session may expire without ability to refresh",
-          )
-        }
+        const expiry = now + Duration.toMillis(parsed.expires_in)
+        const refreshToken = parsed.refresh_token
 
         yield* repo.persistAccount({
-          id: userId,
-          email: userEmail,
+          id: account.id,
+          email: account.email,
           url: input.server,
-          accessToken: access,
-          refreshToken: refresh,
+          accessToken,
+          refreshToken,
           expiry,
           orgID: firstOrgID,
         })
 
-        return new PollSuccess({ email: userEmail })
+        return new PollSuccess({ email: account.email })
       })
 
       return AccountService.of({
diff --git a/packages/opencode/src/cli/cmd/account.ts b/packages/opencode/src/cli/cmd/account.ts
index 7e9f893a8fb6..dd0834a3d805 100644
--- a/packages/opencode/src/cli/cmd/account.ts
+++ b/packages/opencode/src/cli/cmd/account.ts
@@ -24,17 +24,17 @@ const loginEffect = Effect.fn("login")(function* (url: string) {
   const s = Prompt.spinner()
   yield* s.start("Waiting for authorization...")
 
-  const poll = (wait: number): Effect.Effect<PollResult, AccountError> =>
+  const poll = (wait: Duration.Duration): Effect.Effect<PollResult, AccountError> =>
     Effect.gen(function* () {
       yield* Effect.sleep(wait)
       const result = yield* service.poll(login)
       if (result._tag === "PollPending") return yield* poll(wait)
-      if (result._tag === "PollSlow") return yield* poll(wait + 5000)
+      if (result._tag === "PollSlow") return yield* poll(Duration.sum(wait, Duration.seconds(5)))
       return result
     })
 
-  const result = yield* poll(login.interval * 1000).pipe(
-    Effect.timeout(Duration.seconds(login.expiry)),
+  const result = yield* poll(login.interval).pipe(
+    Effect.timeout(login.expiry),
     Effect.catchTag("TimeoutError", () => Effect.succeed(new PollExpired())),
   )
 
diff --git a/packages/opencode/test/account/repo.test.ts b/packages/opencode/test/account/repo.test.ts
index ecc392ead5ef..74a6d7a570c9 100644
--- a/packages/opencode/test/account/repo.test.ts
+++ b/packages/opencode/test/account/repo.test.ts
@@ -2,7 +2,7 @@ import { expect } from "bun:test"
 import { Effect, Layer, Option } from "effect"
 
 import { AccountRepo } from "../../src/account/repo"
-import { AccountID, OrgID } from "../../src/account/schema"
+import { AccessToken, AccountID, OrgID, RefreshToken } from "../../src/account/schema"
 import { Database } from "../../src/storage/db"
 import { testEffect } from "../fixture/effect"
 
@@ -41,8 +41,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "at_123",
-        refreshToken: "rt_456",
+        accessToken: AccessToken.make("at_123"),
+        refreshToken: RefreshToken.make("rt_456"),
         expiry: Date.now() + 3600_000,
         orgID: Option.some(OrgID.make("org-1")),
       }),
@@ -51,7 +51,7 @@ it.effect(
     const row = yield* AccountRepo.use((r) => r.getRow(id))
     expect(Option.isSome(row)).toBe(true)
     const value = Option.getOrThrow(row)
-    expect(value.id).toBe("user-1")
+    expect(value.id).toBe(AccountID.make("user-1"))
     expect(value.email).toBe("test@example.com")
 
     const active = yield* AccountRepo.use((r) => r.active())
@@ -70,8 +70,8 @@ it.effect(
         id: id1,
         email: "first@example.com",
         url: "https://control.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 3600_000,
         orgID: Option.some(OrgID.make("org-1")),
       }),
@@ -82,8 +82,8 @@ it.effect(
         id: id2,
         email: "second@example.com",
         url: "https://control.example.com",
-        accessToken: "at_2",
-        refreshToken: "rt_2",
+        accessToken: AccessToken.make("at_2"),
+        refreshToken: RefreshToken.make("rt_2"),
         expiry: Date.now() + 3600_000,
         orgID: Option.some(OrgID.make("org-2")),
       }),
@@ -108,8 +108,8 @@ it.effect(
         id: id1,
         email: "a@example.com",
         url: "https://control.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 3600_000,
         orgID: Option.none(),
       }),
@@ -120,8 +120,8 @@ it.effect(
         id: id2,
         email: "b@example.com",
         url: "https://control.example.com",
-        accessToken: "at_2",
-        refreshToken: "rt_2",
+        accessToken: AccessToken.make("at_2"),
+        refreshToken: RefreshToken.make("rt_2"),
         expiry: Date.now() + 3600_000,
         orgID: Option.some(OrgID.make("org-1")),
       }),
@@ -143,8 +143,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 3600_000,
         orgID: Option.none(),
       }),
@@ -168,8 +168,8 @@ it.effect(
         id: id1,
         email: "first@example.com",
         url: "https://control.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 3600_000,
         orgID: Option.none(),
       }),
@@ -180,8 +180,8 @@ it.effect(
         id: id2,
         email: "second@example.com",
         url: "https://control.example.com",
-        accessToken: "at_2",
-        refreshToken: "rt_2",
+        accessToken: AccessToken.make("at_2"),
+        refreshToken: RefreshToken.make("rt_2"),
         expiry: Date.now() + 3600_000,
         orgID: Option.none(),
       }),
@@ -208,8 +208,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "old_token",
-        refreshToken: "old_refresh",
+        accessToken: AccessToken.make("old_token"),
+        refreshToken: RefreshToken.make("old_refresh"),
         expiry: 1000,
         orgID: Option.none(),
       }),
@@ -219,16 +219,16 @@ it.effect(
     yield* AccountRepo.use((r) =>
       r.persistToken({
         accountID: id,
-        accessToken: "new_token",
-        refreshToken: "new_refresh",
+        accessToken: AccessToken.make("new_token"),
+        refreshToken: RefreshToken.make("new_refresh"),
         expiry: Option.some(expiry),
       }),
     )
 
     const row = yield* AccountRepo.use((r) => r.getRow(id))
     const value = Option.getOrThrow(row)
-    expect(value.access_token).toBe("new_token")
-    expect(value.refresh_token).toBe("new_refresh")
+    expect(value.access_token).toBe(AccessToken.make("new_token"))
+    expect(value.refresh_token).toBe(RefreshToken.make("new_refresh"))
     expect(value.token_expiry).toBe(expiry)
   }),
 )
@@ -243,8 +243,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "old_token",
-        refreshToken: "old_refresh",
+        accessToken: AccessToken.make("old_token"),
+        refreshToken: RefreshToken.make("old_refresh"),
         expiry: 1000,
         orgID: Option.none(),
       }),
@@ -253,8 +253,8 @@ it.effect(
     yield* AccountRepo.use((r) =>
       r.persistToken({
         accountID: id,
-        accessToken: "new_token",
-        refreshToken: "new_refresh",
+        accessToken: AccessToken.make("new_token"),
+        refreshToken: RefreshToken.make("new_refresh"),
         expiry: Option.none(),
       }),
     )
@@ -274,8 +274,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "at_v1",
-        refreshToken: "rt_v1",
+        accessToken: AccessToken.make("at_v1"),
+        refreshToken: RefreshToken.make("rt_v1"),
         expiry: 1000,
         orgID: Option.some(OrgID.make("org-1")),
       }),
@@ -286,8 +286,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "at_v2",
-        refreshToken: "rt_v2",
+        accessToken: AccessToken.make("at_v2"),
+        refreshToken: RefreshToken.make("rt_v2"),
         expiry: 2000,
         orgID: Option.some(OrgID.make("org-2")),
       }),
@@ -298,7 +298,7 @@ it.effect(
 
     const row = yield* AccountRepo.use((r) => r.getRow(id))
     const value = Option.getOrThrow(row)
-    expect(value.access_token).toBe("at_v2")
+    expect(value.access_token).toBe(AccessToken.make("at_v2"))
 
     const active = yield* AccountRepo.use((r) => r.active())
     expect(Option.getOrThrow(active).active_org_id).toBe(OrgID.make("org-2"))
@@ -315,8 +315,8 @@ it.effect(
         id,
         email: "test@example.com",
         url: "https://control.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 3600_000,
         orgID: Option.some(OrgID.make("org-1")),
       }),
diff --git a/packages/opencode/test/account/service.test.ts b/packages/opencode/test/account/service.test.ts
index 87f5b23f2828..5caa33235a13 100644
--- a/packages/opencode/test/account/service.test.ts
+++ b/packages/opencode/test/account/service.test.ts
@@ -1,10 +1,10 @@
 import { expect } from "bun:test"
-import { Effect, Layer, Option, Ref, Schema } from "effect"
+import { Duration, Effect, Layer, Option, Ref, Schema } from "effect"
 import { HttpClient, HttpClientResponse } from "effect/unstable/http"
 
 import { AccountRepo } from "../../src/account/repo"
 import { AccountService } from "../../src/account/service"
-import { AccountID, Login, Org, OrgID } from "../../src/account/schema"
+import { AccessToken, AccountID, DeviceCode, Login, Org, OrgID, RefreshToken, UserCode } from "../../src/account/schema"
 import { Database } from "../../src/storage/db"
 import { testEffect } from "../fixture/effect"
 
@@ -42,8 +42,8 @@ it.effect(
         id: AccountID.make("user-1"),
         email: "one@example.com",
         url: "https://one.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 60_000,
         orgID: Option.none(),
       }),
@@ -54,8 +54,8 @@ it.effect(
         id: AccountID.make("user-2"),
         email: "two@example.com",
         url: "https://two.example.com",
-        accessToken: "at_2",
-        refreshToken: "rt_2",
+        accessToken: AccessToken.make("at_2"),
+        refreshToken: RefreshToken.make("rt_2"),
         expiry: Date.now() + 60_000,
         orgID: Option.none(),
       }),
@@ -101,8 +101,8 @@ it.effect(
         id,
         email: "user@example.com",
         url: "https://one.example.com",
-        accessToken: "at_old",
-        refreshToken: "rt_old",
+        accessToken: AccessToken.make("at_old"),
+        refreshToken: RefreshToken.make("rt_old"),
         expiry: Date.now() - 1_000,
         orgID: Option.none(),
       }),
@@ -110,7 +110,7 @@ it.effect(
 
     const client = HttpClient.make((req) =>
       Effect.succeed(
-        req.url === "https://one.example.com/oauth/token"
+        req.url === "https://one.example.com/auth/device/token"
           ? json(req, {
               access_token: "at_new",
               refresh_token: "rt_new",
@@ -127,8 +127,8 @@ it.effect(
 
     const row = yield* AccountRepo.use((r) => r.getRow(id))
     const value = Option.getOrThrow(row)
-    expect(value.access_token).toBe("at_new")
-    expect(value.refresh_token).toBe("rt_new")
+    expect(value.access_token).toBe(AccessToken.make("at_new"))
+    expect(value.refresh_token).toBe(RefreshToken.make("rt_new"))
     expect(value.token_expiry).toBeGreaterThan(Date.now())
   }),
 )
@@ -143,8 +143,8 @@ it.effect(
         id,
         email: "user@example.com",
         url: "https://one.example.com",
-        accessToken: "at_1",
-        refreshToken: "rt_1",
+        accessToken: AccessToken.make("at_1"),
+        refreshToken: RefreshToken.make("rt_1"),
         expiry: Date.now() + 60_000,
         orgID: Option.none(),
       }),
@@ -180,12 +180,12 @@ it.effect(
   "poll stores the account and first org on success",
   Effect.gen(function* () {
     const login = new Login({
-      code: "device-code",
-      user: "user-code",
+      code: DeviceCode.make("device-code"),
+      user: UserCode.make("user-code"),
       url: "https://one.example.com/verify",
       server: "https://one.example.com",
-      expiry: 600,
-      interval: 5,
+      expiry: Duration.seconds(600),
+      interval: Duration.seconds(5),
     })
 
     const client = HttpClient.make((req) =>
@@ -194,6 +194,7 @@ it.effect(
           ? json(req, {
               access_token: "at_1",
               refresh_token: "rt_1",
+              token_type: "Bearer",
               expires_in: 60,
             })
           : req.url === "https://one.example.com/api/user"


PATCH

echo "Patch applied successfully."
