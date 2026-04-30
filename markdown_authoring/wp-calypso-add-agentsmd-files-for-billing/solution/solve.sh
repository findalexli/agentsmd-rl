#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wp-calypso

# Idempotency guard
if grep -qF "- client/dashboard/me/billing-purchases \u2014 billing & purchase management" "AGENTS.md" && grep -qF "- Prefer `@wordpress/components` over custom UI primitives (Button, Modal, Card," "client/AGENTS.md" && grep -qF "- **me/billing-purchases/** \u2014 Billing & purchase management (cancel flows, payme" "client/dashboard/AGENTS.md" && grep -qF "6. **Siteless purchases** \u2014 Some products (Akismet, Jetpack, Marketplace) use te" "client/dashboard/me/billing-purchases/AGENTS.md" && grep -qF "client/dashboard/me/billing-purchases/CLAUDE.md" "client/dashboard/me/billing-purchases/CLAUDE.md" && grep -qF "9. **Siteless purchases** \u2014 Some products (Akismet, Jetpack, Marketplace) use te" "client/me/purchases/AGENTS.md" && grep -qF "client/me/purchases/CLAUDE.md" "client/me/purchases/CLAUDE.md" && grep -qF "10. **Siteless purchases** \u2014 Some products (Akismet, Jetpack, Marketplace) use t" "client/my-sites/checkout/AGENTS.md" && grep -qF "client/my-sites/checkout/CLAUDE.md" "client/my-sites/checkout/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -10,12 +10,15 @@
 
 - **Calypso** — the classic WordPress.com hosting dashboard, sharing data using Redux and split via Webpack section chunks.
   - client/my-sites — per-site management; deprecated in favor of the Dashboard client
+  - client/my-sites/checkout — checkout flow
+  - client/me/purchases — purchase management
   - client/landing/stepper — onboarding/signup flows (site creation, domain purchase, migration wizards)
   - client/reader — WordPress.com Reader: feed streams, discover, conversations, likes, lists, following management
   - Shared infra: client/components, client/state, client/lib, client/layout
 - **Jetpack Cloud** (client/jetpack-cloud) — reuses Calypso shared infra (client/state, client/components).
 - **A8C for Agencies** (client/a8c-for-agencies) — reuses Calypso shared infra.
 - **Dashboard** (client/dashboard) — the new multi-site dashboard. Self-contained: does not reuse Calypso client code. Has its own components, data fetching (TanStack Query), and routing (TanStack Router).
+  - client/dashboard/me/billing-purchases — billing & purchase management
 
 ## Packages
 
diff --git a/client/AGENTS.md b/client/AGENTS.md
@@ -1,67 +1,34 @@
-You are an expert React + TypeScript programming assistant focused on producing clear, readable, and production-quality code.
-
-## Core Principles
-
-- Provide concise, technical answers with accurate TypeScript examples.
-- Use functional, declarative React (no classes).
-- Prefer composition and modularization over duplication.
-- Prioritize accessibility, performance, and scalability.
-- Read linked documentation files to have wider context.
-- Research existing patterns and conventions in the codebase before coming up with new solutions.
-
-## Code Style
-
-- Use TypeScript strictly; no `any` unless justified.
-  - Type-check with `yarn typecheck-client` (note: this is slow)
-- Keep components small and focused.
-- Use `import clsx from 'clsx'` instead of `classnames`.
-- There should be 1 empty line between `import './style.scss'` and other imports.
-- Adhere strictly to lint rules.
-  - Lint JS/TS/TSX: `yarn eslint <file>`
-  - Lint + fix JS/TS/TSX: `yarn eslint --fix <file>`
-  - Lint CSS/SCSS: `yarn stylelint <file>`
-- Format any file with `yarn prettier --write <file>` or only with `yarn prettier --check <file>`.
-
-## Naming
-
-- Descriptive names with auxiliary verbs (e.g., `isLoading`, `hasError`).
-- kebab-case directories (e.g., `components/auth-wizard`).
-
-## Styling
-
-- Avoid BEM shortcuts (`&--`, `&__`).
-- Use logical properties (e.g., `margin-inline-start`).
-- Prefer scalable, accessible layouts.
-
-## WordPress UI Components
-
-- When building UI, prefer existing components from `@wordpress/components` instead of creating custom implementations.
-- Do NOT recreate common primitives such as:
-  - Button
-  - Modal
-  - Card
-  - Panel
-  - Notice
-  - Tooltip
-  - Spinner
-  - TextControl / SelectControl / ToggleControl / CheckboxControl
-  - Flex / VStack / HStack / Grid
-  - Popover / Dropdown
-  - Form controls and layout primitives
-- Only build custom components if no suitable WordPress component exists.
-- Avoid `__experimental*` components unless explicitly requested or there are already existing examples.
-
-## Documentation
-
-- Follow JSDoc.
-- Explain intent and reasoning, not obvious behavior.
-- Wrap comments at 100 columns.
-
-## Testing
-
-- Use React Testing Library.
-- Prefer `userEvent` over `fireEvent`.
-- Use `toBeVisible` for user-visible assertions instead of `toBeInTheDocument`.
-- Run tests to verify changes:
-  - Run specific test file: `yarn test-client <test-file>`
-  - Find + run tests for a source file: `yarn test-client --findRelatedTests <file>`
+# Calypso Client
+
+React + TypeScript application clients for WordPress.com. For repo-level context, see root `AGENTS.md`.
+
+## Project Knowledge
+
+Two coexisting architectures: Classic (`client/me/`, `client/my-sites/`) uses Redux +
+page.js routing. Dashboard (`client/dashboard/`) uses TanStack Query + TanStack Router.
+
+## Commands
+
+```bash
+yarn eslint <file>                    # Lint JS/TS/TSX
+yarn eslint --fix <file>              # Lint + fix
+yarn stylelint <file>                 # Lint CSS/SCSS
+yarn prettier --write <file>          # Format
+yarn typecheck-client                 # Type-check (slow)
+yarn test-client <test-file>          # Run specific test
+yarn test-client --findRelatedTests <file>  # Find + run related tests
+```
+
+## Conventions
+
+- Use `import clsx from 'clsx'` — not `classnames`.
+- One empty line between `import './style.scss'` and other imports.
+- Avoid BEM shortcuts (`&--`, `&__`) in SCSS.
+- Use CSS logical properties (`margin-inline-start`, not `margin-left`).
+- Prefer `@wordpress/components` over custom UI primitives (Button, Modal, Card, etc.). Avoid `__experimental*` components unless existing usage in codebase.
+- No `any` unless justified — strict TypeScript throughout.
+- kebab-case for directories (e.g., `components/auth-wizard`).
+- `userEvent` over `fireEvent` in tests. `toBeVisible` over `toBeInTheDocument`.
+- Dialog buttons on mobile: `.dialog__action-buttons` flips to
+  `flex-direction: column-reverse` below `$break-mobile`. Flex labels inside
+  buttons need `width: 100%` for `justify-content: center` to work.
diff --git a/client/dashboard/AGENTS.md b/client/dashboard/AGENTS.md
@@ -1,5 +1,9 @@
 You are an expert AI programming assistant specializing in the WordPress.com Dashboard. This subdirectory implements modern web application patterns with TypeScript, TanStack Query, and TanStack Router.
 
+## Sub-area Guides
+
+- **me/billing-purchases/** — Billing & purchase management (cancel flows, payment methods, DataViews)
+
 ## Documentation
 
 For detailed implementation guidance, refer to:
diff --git a/client/dashboard/me/billing-purchases/AGENTS.md b/client/dashboard/me/billing-purchases/AGENTS.md
@@ -0,0 +1,111 @@
+# Dashboard Billing — Purchase Management
+
+TanStack Query/Router-based billing and purchase management. The largest and most
+complex billing area in the Dashboard client. Related billing areas:
+`client/me/purchases/` (Classic), `client/my-sites/checkout/` (Checkout).
+
+## Project Knowledge
+
+### Directory Structure
+
+```
+billing-purchases/
+├── index.tsx + dataviews.tsx     # Purchase list (DataViews table)
+├── purchase-settings/index.tsx   # Heavy component — see Arch Decision #2
+├── cancel-purchase/              # Multi-step cancellation flow (most complex area)
+│   ├── cancel-purchase-form/     # Survey steps, product-specific options
+│   └── domain-removal-flow       # Domain-specific removal steps
+├── payment-methods/              # use-create-* factory hooks (one per payment type)
+├── payment-method-selector/      # Payment method selection UI
+├── change-payment-method.tsx     # Per-purchase payment method change
+└── add-payment-method.tsx        # Standalone new card addition
+```
+
+### Sibling Billing Areas
+
+Non-obvious details about sibling directories under `client/dashboard/me/`:
+
+| Directory                  | Trap                                                                             |
+| -------------------------- | -------------------------------------------------------------------------------- |
+| `billing-payment-methods/` | Delete dialog queries `userPurchasesQuery()` to show affected subscriptions      |
+| `billing-tax-details/`     | Read-only when `can_user_edit === false` — no error, just silently disables form |
+
+### Data Layer
+
+Helpers in `client/dashboard/utils/purchase.ts` (~50 functions). Queries are loaded
+via router loaders in `client/dashboard/app/router/me.tsx`.
+
+### Architecture Context
+
+Dashboard uses `Purchase` from `@automattic/api-core` (snake_case fields, e.g.,
+`purchase.site_slug`). Expiry values: `'auto-renewing'`, `'manual-renew'`. Classic
+(`client/me/purchases/`) uses a different `Purchase` type from
+`calypso/lib/purchases/types` (camelCase, different string values) — never copy
+logic between the two without converting field names and values.
+
+Query key prefix for purchases is `'upgrades'` (NOT `'purchases'` — historical).
+Receipts use `'receipt'`, payment methods use `'me'`. Wrong prefix silently breaks
+cache invalidation.
+
+Queries live in `@automattic/api-queries` (`packages/api-queries/`), NOT in
+`client/dashboard/data/` or `client/dashboard/app/queries/`. Adding a new query
+requires a fetcher in `@automattic/api-core` (`packages/api-core/src/`) first,
+then a query wrapper in `api-queries`.
+
+## Architectural Decisions
+
+1. **Purchase list uses DataViews** — `dataviews.tsx` defines fields, filters, actions,
+   and responsive column visibility via `usePersistentView()`. Transferred purchases
+   are fetched separately and disable management actions.
+
+2. **Purchase settings is a heavy component** — Single `index.tsx` handles domain queries,
+   storage queries, auto-renew state, renewal dialogs, and product-specific key displays.
+   This is intentional consolidation, not a candidate for splitting.
+
+3. **Payment method factory pattern** — `use-create-*` hooks return `PaymentMethod` objects
+   with processors. `use-create-assignable-payment-methods.tsx` filters by
+   `allowedPaymentMethodsQuery()` and returns empty array while loading (intentional).
+
+### Cancel Purchase Flow
+
+Three flow types, derived by `getPurchaseCancellationFlowType()` in
+`utils/purchase.ts` from `is_refundable`, `hasAmountAvailableToRefund()`, and
+`is_auto_renew_enabled` (not passed as props):
+
+| Flow Type            | When                                                          | API Call                            |
+| -------------------- | ------------------------------------------------------------- | ----------------------------------- |
+| `REMOVE`             | Expired, grace-period, or (not refundable AND auto-renew off) | `removePurchaseMutation()` (DELETE) |
+| `CANCEL_WITH_REFUND` | Refundable, amount > 0, auto-renew on                         | `cancelAndRefundPurchaseMutation()` |
+| `CANCEL_AUTORENEW`   | Not refundable, auto-renew on                                 | Turns off auto-renew                |
+
+Survey steps vary by product type (Jetpack, domains, plans, Akismet, marketplace).
+Agency partner purchases skip survey. Marketplace plan cancellation cascades to all
+marketplace subscriptions on site.
+
+## Common Pitfalls
+
+1. **`isPartnerPurchase` type guard narrows to wrong field** — Checks
+   `purchase?.partner_name` but narrows the type to `{ partnerType: string }` (camelCase).
+   The actual field on the `Purchase` interface is `partner_type` (snake_case). Downstream
+   code using the narrowed type will reference a field that doesn't exist.
+
+2. **Payment method list is empty while loading** — `allowedPaymentMethods === undefined`
+   returns `[]` (no methods shown). Errors fail open (all methods shown). Don't add
+   conditional logic before the undefined guard in `use-create-assignable-payment-methods.tsx`.
+
+3. **`REMOVE` and `CANCEL` are different APIs** — `getPurchaseCancellationFlowType`
+   returns `REMOVE` for expired purchases, which maps to a DELETE call, not a cancel.
+   Don't assume all paths through "cancel purchase" call the same mutation.
+
+4. **CRITICAL: `flowType` gets silently overridden** — Inside `onSurveyComplete()`,
+   `state.cancelIntent === 'refund'` switches `CANCEL_AUTORENEW` → `CANCEL_WITH_REFUND`.
+   The `shouldShowRefundEligibilityNotice` feature flag also changes the default path.
+
+5. **Survey completion tracked per-purchase** — Stored in user preferences to avoid
+   re-surveying. A new survey won't appear for a purchase that was already surveyed.
+
+6. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never call `siteBySlugQuery()` for these — use `purchase.domain` or `purchase.blog_id` for display, skip site-dependent UI entirely.
+
+7. **Transferred purchases** — Always check ownership before allowing purchase actions.
+
+8. **Route params are strings** — `purchaseId` from URL params must be `parseInt()`'d before passing to query functions.
diff --git a/client/dashboard/me/billing-purchases/CLAUDE.md b/client/dashboard/me/billing-purchases/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
diff --git a/client/me/purchases/AGENTS.md b/client/me/purchases/AGENTS.md
@@ -0,0 +1,104 @@
+# Classic Purchases — Billing & Purchase Management
+
+Redux/page.js-based billing and purchase management. Covers the full purchase
+lifecycle: listing, detail, payment methods, billing history, cancellation, and
+tax details. Related billing areas: `client/dashboard/me/billing-purchases/`
+(Dashboard), `client/my-sites/checkout/` (Checkout).
+
+## Project Knowledge
+
+### Directory Structure
+
+```
+client/me/purchases/
+├── index.js + controller.jsx       # page.js route registration (not React Router)
+├── manage-purchase/
+│   └── index.tsx                   # Main detail page — class component (not functional)
+├── purchases-list-in-dataviews/    # Modern DataViews list (retrofitted into Redux architecture)
+├── cancel-purchase/                # Cancel flow — separate from remove-purchase/
+├── remove-purchase/                # Remove flow (expired items, DELETE API) — separate from cancel
+└── billing-history/main.tsx        # DataViews-based history list
+```
+
+### Redux Selectors
+
+`getSitePurchases(state, siteId)` returns `[]` when not loaded — indistinguishable
+from "no purchases." `getUserPurchases(state)` returns `null` when not loaded.
+Always check `hasLoadedUserPurchasesFromServer` / `hasLoadedSitePurchasesFromServer`
+before trusting results.
+
+`getByPurchaseId` searches ALL purchases (user + site) from a single flat array.
+What's in that array depends on which `Query*Purchases` components have mounted.
+
+### Architecture Context
+
+Classic uses `Purchase` from `calypso/lib/purchases/types` (camelCase fields, e.g.,
+`purchase.siteSlug`). Expiry values: `'autoRenewing'`, `'manualRenew'`. Dashboard
+(`client/dashboard/me/billing-purchases/`) uses a different `Purchase` type from
+`@automattic/api-core` (snake_case, different string values) — never copy logic
+between the two without converting field names and values.
+
+## Architectural Decisions
+
+1. **Two cancel paths (mutually exclusive)** — `manage-purchase/index.tsx` renders one
+   of two cancel entry points based on `canAutoRenewBeTurnedOff(purchase)`:
+
+   - **True** → `renderCancelPurchaseNavItem()` → navigates to cancel page (full flow)
+   - **False** → `renderRemovePurchaseNavItem()` → renders `<RemovePurchase>` inline (delete)
+
+   These map to different API calls (`cancelPurchase` for refund, `removePurchase`
+   DELETE for expired, `disableAutoRenew` for toggle). All say "Cancel" in the UI
+   but are NOT interchangeable.
+
+2. **Three payment method paths** — `changePaymentMethod` (per-purchase, has card),
+   `addPaymentMethod` (per-purchase, no card), `addNewPaymentMethod` (account-level).
+   Different routes, different components. `getChangePaymentMethodPath` in `utils.ts`
+   chooses between the first two.
+
+3. **Auto-renew toggle is asymmetric** — Enabling requires a valid payment method
+   (silently shows dialog instead). Disabling has no such gate.
+
+## Common Pitfalls
+
+1. **`canAutoRenewBeTurnedOff` name lies** — Despite the name, this function is the
+   **cancel eligibility gate**, not an auto-renew check. Returns `true` for refundable
+   purchases even when auto-renew is already off. See `client/lib/purchases/index.ts`.
+   Don't substitute `purchase.isAutoRenewEnabled`.
+
+2. **`isSiteLevel` prop changes data source silently** — In `manage-purchase`,
+   `isSiteLevel=true` checks `hasLoadedSitePurchasesFromServer` instead of
+   `hasLoadedUserPurchasesFromServer`. Without the matching `QuerySitePurchases`
+   component, you get a permanent loading state with no error.
+
+3. **Auto-renew toggle: deferred notice pattern** — Notices created while
+   `showAutoRenewDisablingDialog` is visible get swallowed. The component uses
+   `pendingNotice` state + `componentDidUpdate` to defer. Don't call `createNotice`
+   directly in dialog callbacks.
+
+4. **`page()` vs `page.redirect()` after actions** — Use `page.redirect()` after
+   cancel/remove so users can't navigate back to an invalid state. `page()` is
+   for normal navigation.
+
+5. **`purchase` is optional in PaymentMethodSelector** — The "add payment method"
+   flow passes `undefined`. Processors must handle this case. Success messages
+   branch on whether `purchase` exists.
+
+6. **`site.wpcom_url` lies for `.home.blog` sites** — Always returns
+   `.wordpress.com` even when the site's free domain is `.home.blog` (or 27
+   other `.blog` subdomains). Use `getWpComDomainBySiteId()` selector to get
+   the actual free domain. Affects `NonPrimaryDomainDialog` in both
+   `remove-purchase/` and `manage-purchase/`.
+
+7. **`isMonthly()` only checks plan slugs** — Returns `false` for Jetpack
+   product slugs like `jetpack_videopress_monthly` because it only checks
+   `JETPACK_MONTHLY_PLANS`. Use `getJetpackItemTermVariants()` for products.
+   Same issue with `getYearlyPlanByMonthly()` — only works for plans.
+
+8. **VAT API errors need field mapping** — `useMutation` error has
+   `{ error: string, message: string }` but no field indicator. Map error
+   codes to fields: `missing_country`/`invalid_country` → country field,
+   `invalid_vat`/`missing_id`/`validation_failed` → id field.
+
+9. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never query site data for these — use `purchase.domain` for display, skip site-dependent UI entirely.
+
+10. **Transferred purchases** — Always check ownership before allowing purchase actions.
diff --git a/client/me/purchases/CLAUDE.md b/client/me/purchases/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
diff --git a/client/my-sites/checkout/AGENTS.md b/client/my-sites/checkout/AGENTS.md
@@ -0,0 +1,126 @@
+# Checkout — WordPress.com Purchase Flow
+
+Customer-facing checkout UI. Related billing areas:
+`client/me/purchases/` (Classic), `client/dashboard/me/billing-purchases/` (Dashboard).
+
+## Project Knowledge
+
+### Directory Structure
+
+```
+client/my-sites/checkout/
+├── src/
+│   ├── components/
+│   │   ├── checkout-main.tsx           # Top-level orchestrator
+│   │   ├── item-variation-picker/     # Billing cycle selector (name misleads — not "variants")
+│   │   └── wp-contact-form/           # Contact form (varies by product type — see Checkout Steps)
+│   ├── payment-methods/               # One UI component per processor
+│   ├── hooks/use-create-payment-methods/  # Generates PaymentMethod[] from cart + server config
+│   └── lib/
+│       ├── wpcom-store.ts               # @wordpress/data store (not Redux — checkout-specific state)
+│       ├── leave-checkout.ts            # navigate() trap — see pitfall #6
+│       └── *-processor.ts              # One per payment method (13 files)
+├── get-thank-you-page-url/          # 800+ lines, exhaustive tests — see pitfall #5
+└── checkout-thank-you/              # Post-purchase pages (8+ variants)
+```
+
+### Checkout Steps
+
+Three hard-coded steps (not extensible without changes here):
+
+1. **Review Order**
+2. **Contact Details** — Form varies by cart contents:
+   - No domains → billing address only
+   - Domain registration → full ICANN contact details
+   - Google Workspace → company name + billing address
+   - Contact type determined by `getContactDetailsType(responseCart)` from `wpcom-checkout`
+3. **Payment Method**
+
+The sidebar/summary view is NOT a step — visibility is manually managed via
+`isSummaryVisible` state to prevent it from blocking form submission.
+
+### Checkout State
+
+- **Redux** — global state (site, user, notices)
+- **`@wordpress/data` store** (`wpcom-store.ts`) — checkout-specific: contact details, VAT,
+  domain validation results, form touched fields
+- **`useFormStatus()`** from `composite-checkout` — LOADING, READY, SUBMITTING
+- **`useTransactionStatus()`** — NOT_STARTED, PENDING, COMPLETE, REDIRECTING, ERROR
+
+### Payment Processing
+
+Processors must handle four response paths: immediate success, redirect (PayPal/WeChat),
+3DS challenge (Stripe), and polling (PIX). Not all paths apply to all processors.
+
+### Package Boundaries
+
+| Package              | Role                                                        | Key Rule                    |
+| -------------------- | ----------------------------------------------------------- | --------------------------- |
+| `composite-checkout` | Generic multi-step checkout framework                       | NO WP.com logic here        |
+| `wpcom-checkout`     | WP.com-specific checkout (line items, tax, payment methods) | WP.com logic goes here      |
+| `shopping-cart`      | Cart state via `useShoppingCart()`                          | Independent of checkout     |
+| `calypso-stripe`     | Stripe.js wrapper                                           | Stripe-specific integration |
+| `api-core`           | Fetchers, mutators, types for all API calls                 | Foundation layer            |
+| `api-queries`        | TanStack Query wrappers around api-core                     | Dashboard consumes these    |
+
+## Architectural Decisions
+
+1. **Thank-you URL generated before transaction** — For redirect payment methods
+   (PayPal, Bancontact), the thank-you URL is generated and passed to the processor
+   BEFORE the transaction starts. Uses `:receiptId` placeholder, replaced by
+   `/me/transactions` endpoint on return.
+
+2. **Contact validation is two-step** — Form validation (required fields, format)
+   then async domain registration validation (WPCOM backend). Both must pass.
+
+### Adding a Payment Method
+
+Seven touchpoints required (follow an existing implementation like PIX or Razorpay):
+
+1. **Payment method component** — `src/payment-methods/{name}.tsx`, export `create{Name}PaymentMethod()` returning a `PaymentMethod` object (`{ id, paymentProcessorId, label, activeContent, submitButton }`)
+2. **Processor function** — `src/lib/{name}-processor.ts`, signature: `async (submitData, options, translate) => PaymentProcessorResponse`
+3. **Register processor** — Add to processor map in `src/components/checkout-main.tsx`
+4. **Create hook** — `src/hooks/use-create-payment-methods/use-create-{name}.ts`, gate with `isEnabled('checkout/{name}')`
+5. **Register hook** — Call in `use-create-payment-methods/index.tsx`, add result to `paymentMethods` array
+6. **Slug mapping** — Add bidirectional mapping in `packages/wpcom-checkout/src/translate-payment-method-names.ts` (e.g., `'pix'` ↔ `'WPCOM_Billing_Ebanx_Redirect_Brazil_Pix'`)
+7. **Feature flag** — Add to `config/{environment}.json` (e.g., `checkout/ebanx-pix`)
+
+Steps 6-7 are the ones agents miss — without slug mapping the method never appears.
+
+## Common Pitfalls
+
+1. **Checkout links MUST include `redirect_to` and `cancel_to` params** — Missing
+   these causes broken back/cancel navigation.
+
+2. **Cart key matters** — Wrong cart key = wrong cart. `'no-site'` vs site ID vs
+   `undefined` have different behaviors. See `packages/shopping-cart/README.md`.
+
+3. **Checkout URL format** — Products use slugs, domain meta uses colon separator.
+   Example: `/checkout/example.com/personal,domain_reg:example.com`. Don't construct
+   URLs manually — use existing helpers.
+
+4. **Payment method filtering** — Not all methods are available everywhere.
+   `filterAppropriatePaymentMethods()` in `packages/wpcom-checkout/src/` handles
+   country/currency/product filtering. Don't bypass this or hardcode availability.
+
+5. **Thank-you page routing is 800+ lines with 20+ branches** — Routing logic is in
+   `get-thank-you-page-url/index.ts` with exhaustive unit tests. The code explicitly
+   warns: "IF YOU CHANGE THIS FUNCTION ALSO CHANGE THE TESTS." Don't add new
+   thank-you routes without updating both.
+
+6. **`navigate()` silently fails for `/setup/` routes** — `navigate()` uses
+   `page.show()` which doesn't work for Stepper routes. Use `window.location.href`
+   for cross-origin or setup redirects. See `src/lib/leave-checkout.ts`.
+
+7. **3DS challenges not guaranteed** — Stripe 3D Secure may or may not trigger.
+   Processors must handle both paths (direct success and challenge flow).
+
+8. **Gift purchases bypass everything** — Check `cart.is_gift_purchase` first.
+   Gift purchases skip all upsell logic and route to a separate thank-you page.
+
+9. **Atomic sites use `.wpcomstaging.com`** — Thank-you URL logic replaces
+   `.wordpress.com` with `.wpcomstaging.com` for Atomic sites.
+
+10. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never query site data for these.
+
+11. **Transferred purchases** — Always check ownership before allowing purchase actions.
diff --git a/client/my-sites/checkout/CLAUDE.md b/client/my-sites/checkout/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
