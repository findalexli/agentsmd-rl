#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for PR #13606
patch -p1 <<'PATCH'
diff --git a/frontend/__tests__/components/features/auth/login-cta.test.tsx b/frontend/__tests__/components/features/auth/login-cta.test.tsx
index 76a39bd6c20e..e1db11a2e496 100644
--- a/frontend/__tests__/components/features/auth/login-cta.test.tsx
+++ b/frontend/__tests__/components/features/auth/login-cta.test.tsx
@@ -17,11 +17,11 @@ describe("LoginCTA", () => {
     vi.clearAllMocks();
   });

-  const renderWithRouter = () => {
+  const renderWithRouter = (source?: "login_page" | "device_verify") => {
     const Stub = createRoutesStub([
       {
         path: "/",
-        Component: LoginCTA,
+        Component: () => <LoginCTA source={source} />,
       },
       {
         path: "/information-request",
@@ -75,4 +75,32 @@ describe("LoginCTA", () => {
       "/information-request",
     );
   });
+
+  it("should render external enterprise URL in device verify mode", () => {
+    renderWithRouter("device_verify");
+
+    const learnMoreLink = screen.getByRole("link", {
+      name: "CTA$LEARN_MORE",
+    });
+    expect(learnMoreLink).toHaveAttribute(
+      "href",
+      "https://openhands.dev/enterprise",
+    );
+    expect(learnMoreLink).toHaveAttribute("target", "_blank");
+    expect(learnMoreLink).toHaveAttribute("rel", "noopener noreferrer");
+  });
+
+  it("should track device_verify location when Learn More is clicked in device verify mode", async () => {
+    const user = userEvent.setup();
+    renderWithRouter("device_verify");
+
+    const learnMoreLink = screen.getByRole("link", {
+      name: "CTA$LEARN_MORE",
+    });
+    await user.click(learnMoreLink);
+
+    expect(mockTrackSaasSelfhostedInquiry).toHaveBeenCalledWith({
+      location: "device_verify",
+    });
+  });
 });
diff --git a/frontend/__tests__/routes/device-verify.test.tsx b/frontend/__tests__/routes/device-verify.test.tsx
index 289abc4643db..4fef716e266d 100644
--- a/frontend/__tests__/routes/device-verify.test.tsx
+++ b/frontend/__tests__/routes/device-verify.test.tsx
@@ -235,7 +235,7 @@ describe("DeviceVerify", () => {
       });
     });

-    it("should include the EnterpriseBanner component when feature flag is enabled", async () => {
+    it("should include the LoginCTA component when feature flag is enabled", async () => {
       useIsAuthedMock.mockReturnValue({
         data: true,
         isLoading: false,
@@ -249,11 +249,11 @@ describe("DeviceVerify", () => {
       );

       await waitFor(() => {
-        expect(screen.getByText("ENTERPRISE$TITLE")).toBeInTheDocument();
+        expect(screen.getByTestId("login-cta")).toBeInTheDocument();
       });
     });

-    it("should not include the EnterpriseBanner and be center-aligned when feature flag is disabled", async () => {
+    it("should not include the LoginCTA and be center-aligned when feature flag is disabled", async () => {
       ENABLE_PROJ_USER_JOURNEY_MOCK.mockReturnValue(false);
       useIsAuthedMock.mockReturnValue({
         data: true,
@@ -273,8 +273,8 @@ describe("DeviceVerify", () => {
         ).toBeInTheDocument();
       });

-      // Banner should not be rendered
-      expect(screen.queryByText("ENTERPRISE$TITLE")).not.toBeInTheDocument();
+      // CTA should not be rendered
+      expect(screen.queryByTestId("login-cta")).not.toBeInTheDocument();

       // Container should use max-w-md (centered layout) instead of max-w-4xl
       const container = document.querySelector(".max-w-md");
diff --git a/frontend/src/components/features/auth/login-cta.tsx b/frontend/src/components/features/auth/login-cta.tsx
index 06823837c3d0..dd2d71b29377 100644
--- a/frontend/src/components/features/auth/login-cta.tsx
+++ b/frontend/src/components/features/auth/login-cta.tsx
@@ -8,21 +8,45 @@ import { cn } from "#/utils/utils";
 import StackedIcon from "#/icons/stacked.svg?react";
 import { useTracking } from "#/hooks/use-tracking";

-export function LoginCTA() {
+type LoginCTAProps = {
+  className?: string;
+  source?: "login_page" | "device_verify";
+};
+
+const ENTERPRISE_URL = "https://openhands.dev/enterprise";
+const INFORMATION_REQUEST_PATH = "/information-request";
+
+export function LoginCTA({
+  className,
+  source = "login_page",
+}: LoginCTAProps = {}) {
   const { t } = useTranslation();
   const { trackSaasSelfhostedInquiry } = useTracking();
+  const isDeviceVerifySource = source === "device_verify";
+  const learnMoreButtonClassName = cn(
+    "inline-flex items-center justify-center",
+    "h-10 px-4 rounded",
+    "bg-[#050505] border border-[#242424]",
+    "text-white hover:bg-white hover:text-black",
+    "font-semibold text-sm",
+    "transition-colors",
+  );

   const handleLearnMoreClick = () => {
-    trackSaasSelfhostedInquiry({ location: "login_page" });
+    trackSaasSelfhostedInquiry({ location: source });
   };

   return (
     <Card
       testId="login-cta"
       theme="dark"
-      className={cn("w-full max-w-80 h-auto flex-col", "cta-card-gradient")}
+      className={cn(
+        "w-full max-w-80 h-auto flex-col",
+        "cta-card-gradient",
+        className,
+      )}
     >
-      <div className={cn("flex flex-col gap-[11px] p-6")}>
+      <div className={cn("flex h-full flex-col gap-[11px] p-6")}>
         <div className={cn("size-10")}>
           <StackedIcon width={40} height={40} />
         </div>
@@ -44,21 +68,27 @@ export function LoginCTA() {
           <li>{t(I18nKey.CTA$FEATURE_SUPPORT)}</li>
         </ul>

-        <div className={cn("h-10 flex justify-start")}>
-          <Link
-            to="/information-request"
-            onClick={handleLearnMoreClick}
-            className={cn(
-              "inline-flex items-center justify-center",
-              "h-10 px-4 rounded",
-              "bg-[#050505] border border-[#242424]",
-              "text-white hover:bg-white hover:text-black",
-              "font-semibold text-sm",
-              "transition-colors",
-            )}
-          >
-            {t(I18nKey.CTA$LEARN_MORE)}
-          </Link>
+        <div className={cn("mt-auto h-10 flex justify-start")}>
+          {/* Use <a> for external destination; react-router <Link> is only for internal app routes. */}
+          {isDeviceVerifySource ? (
+            <a
+              href={ENTERPRISE_URL}
+              target="_blank"
+              rel="noopener noreferrer"
+              onClick={handleLearnMoreClick}
+              className={learnMoreButtonClassName}
+            >
+              {t(I18nKey.CTA$LEARN_MORE)}
+            </a>
+          ) : (
+            <Link
+              to={INFORMATION_REQUEST_PATH}
+              onClick={handleLearnMoreClick}
+              className={learnMoreButtonClassName}
+            >
+              {t(I18nKey.CTA$LEARN_MORE)}
+            </Link>
+          )}
         </div>
       </div>
     </Card>
diff --git a/frontend/src/routes/device-verify.tsx b/frontend/src/routes/device-verify.tsx
index b05db95240b3..03459385ce14 100644
--- a/frontend/src/routes/device-verify.tsx
+++ b/frontend/src/routes/device-verify.tsx
@@ -2,7 +2,7 @@ import React, { useState } from "react";
 import { useSearchParams } from "react-router";
 import { useTranslation } from "react-i18next";
 import { useIsAuthed } from "#/hooks/query/use-is-authed";
-import { EnterpriseBanner } from "#/components/features/device-verify/enterprise-banner";
+import { LoginCTA } from "#/components/features/auth/login-cta";
 import { I18nKey } from "#/i18n/declaration";
 import { H1 } from "#/ui/typography";
 import { ENABLE_PROJ_USER_JOURNEY } from "#/utils/feature-flags";
@@ -151,11 +151,11 @@ export default function DeviceVerify() {
     return (
       <div className="min-h-screen flex items-center justify-center bg-background p-4">
         <div
-          className={`flex flex-col lg:flex-row items-center lg:items-start gap-6 w-full ${showEnterpriseBanner ? "max-w-4xl" : "max-w-md"}`}
+          className={`flex flex-col lg:flex-row items-center lg:items-stretch gap-6 w-full ${showEnterpriseBanner ? "max-w-4xl" : "max-w-md"}`}
         >
           {/* Device Authorization Card */}
           <div
-            className={`flex-1 min-w-0 max-w-md w-full mx-auto p-6 bg-card rounded-lg shadow-lg border border-neutral-700 ${showEnterpriseBanner ? "lg:mx-0" : ""}`}
+            className={`flex-1 min-w-0 max-w-md w-full mx-auto p-6 bg-card rounded-2xl shadow-lg border border-[#242424] ${showEnterpriseBanner ? "lg:mx-0 lg:self-stretch" : ""}`}
           >
             <H1 className="text-2xl mb-4 text-center">
               {t(I18nKey.DEVICE$AUTHORIZATION_REQUEST)}
@@ -197,8 +197,10 @@ export default function DeviceVerify() {
             </div>
           </div>

-          {/* Enterprise Banner */}
-          {showEnterpriseBanner && <EnterpriseBanner />}
+          {/* Login CTA */}
+          {showEnterpriseBanner && (
+            <LoginCTA source="device_verify" className="lg:self-stretch" />
+          )}
         </div>
       </div>
     );
PATCH

echo "Patch applied successfully"
