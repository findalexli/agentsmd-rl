#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q "Resend = 'resend'" src/server/services/email/impls/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.cursor/rules/project-introduce.mdc b/.cursor/rules/project-introduce.mdc
index 5f7719d26d4..51d297d0d9f 100644
--- a/.cursor/rules/project-introduce.mdc
+++ b/.cursor/rules/project-introduce.mdc
@@ -4,7 +4,7 @@ alwaysApply: true

 ## Project Description

-You are developing an open-source, modern-design AI chat framework: lobehub(previous lobe-chat).
+You are developing an open-source, modern-design AI Agent Workspace: LobeHub(previous LobeChat).

 Supported platforms:

diff --git a/AGENTS.md b/AGENTS.md
index 4263993a512..8834c27b7ed 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -2,6 +2,10 @@

 This document serves as a comprehensive guide for all team members when developing LobeChat.

+## Project Description
+
+You are developing an open-source, modern-design AI Agent Workspace: LobeHub(previous LobeChat).
+
 ## Tech Stack

 Built with modern technologies:
diff --git a/docs/self-hosting/advanced/auth.mdx b/docs/self-hosting/advanced/auth.mdx
index 11290b5a057..a9f5f0dcf2d 100644
--- a/docs/self-hosting/advanced/auth.mdx
+++ b/docs/self-hosting/advanced/auth.mdx
@@ -89,16 +89,27 @@ When configuring OAuth providers, use the following callback URL format:

 ### Email Service Configuration

-If you want to enable email verification or password reset features, you need to configure SMTP settings:
-
-| Environment Variable                  | Type     | Description                                                       |
-| ------------------------------------- | -------- | ----------------------------------------------------------------- |
-| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | Optional | Set to `1` to require email verification before users can sign in |
-| `SMTP_HOST`                           | Required | SMTP server hostname (e.g., `smtp.gmail.com`)                     |
-| `SMTP_PORT`                           | Required | SMTP server port (usually `587` for TLS, `465` for SSL)           |
-| `SMTP_SECURE`                         | Optional | Set to `true` for SSL (port 465), `false` for TLS (port 587)      |
-| `SMTP_USER`                           | Required | SMTP authentication username                                      |
-| `SMTP_PASS`                           | Required | SMTP authentication password                                      |
+Used by email verification, password reset, and magic-link delivery. Choose a provider, then fill the matching variables:
+
+| Environment Variable                  | Type        | Description                                                                                                                                       |
+| ------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | Optional    | Set to `1` to require email verification before users can sign in                                                                                 |
+| `EMAIL_SERVICE_PROVIDER`              | Optional    | Email provider selector: `nodemailer` (default, SMTP) or `resend`                                                                                 |
+| `SMTP_HOST`                           | Required    | SMTP server hostname (e.g., `smtp.gmail.com`). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                      |
+| `SMTP_PORT`                           | Required    | SMTP server port (usually `587` for TLS, `465` for SSL). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                            |
+| `SMTP_SECURE`                         | Optional    | `true` for SSL (port 465), `false` for TLS (port 587). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                              |
+| `SMTP_USER`                           | Required    | SMTP auth username. Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                                                 |
+| `SMTP_PASS`                           | Required    | SMTP auth password. Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                                                 |
+| `RESEND_API_KEY`                      | Required    | Resend API key. Required when `EMAIL_SERVICE_PROVIDER=resend`                                                                                     |
+| `RESEND_FROM`                         | Recommended | Default sender address (e.g., `noreply@your-verified-domain.com`). Must be a domain verified in Resend. Used when `EMAIL_SERVICE_PROVIDER=resend` |
+
+### Magic Link (Passwordless) Login
+
+Enable BetterAuth magic-link login (depends on a working email provider above):
+
+| Environment Variable            | Type     | Description                                        |
+| ------------------------------- | -------- | -------------------------------------------------- |
+| `NEXT_PUBLIC_ENABLE_MAGIC_LINK` | Optional | Set to `1` to enable passwordless magic-link login |

 <Callout type={'tip'}>
   For detailed provider configuration, refer to the [Next Auth provider documentation](/docs/self-hosting/advanced/auth/next-auth) as most configurations are compatible, or visit the official [Better Auth documentation](https://www.better-auth.com/docs/introduction).
diff --git a/docs/self-hosting/advanced/auth.zh-CN.mdx b/docs/self-hosting/advanced/auth.zh-CN.mdx
index 7f950b1ebd5..eefce6007cf 100644
--- a/docs/self-hosting/advanced/auth.zh-CN.mdx
+++ b/docs/self-hosting/advanced/auth.zh-CN.mdx
@@ -87,16 +87,27 @@ LobeChat 与 Clerk 做了深度集成，能够为用户提供一个更加安全

 ### 邮件服务配置

-如果需要启用邮箱验证或密码重置功能，需要配置 SMTP 设置：
-
-| 环境变量                                  | 类型 | 描述                                             |
-| ------------------------------------- | -- | ---------------------------------------------- |
-| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | 可选 | 设置为 `1` 以要求用户在登录前验证邮箱                          |
-| `SMTP_HOST`                           | 必选 | SMTP 服务器主机名（例如 `smtp.gmail.com`）               |
-| `SMTP_PORT`                           | 必选 | SMTP 服务器端口（TLS 通常为 `587`，SSL 为 `465`）          |
-| `SMTP_SECURE`                         | 可选 | SSL 设置为 `true`（端口 465），TLS 设置为 `false`（端口 587） |
-| `SMTP_USER`                           | 必选 | SMTP 认证用户名                                     |
-| `SMTP_PASS`                           | 必选 | SMTP 认证密码                                      |
+用于邮箱验证、密码重置和魔法链接发送。先选择邮件服务，再填对应变量：
+
+| 环境变量                                  | 类型 | 描述                                                                                        |
-| ------------------------------------- | -- | ----------------------------------------------------------------------------------------- |
-| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | 可选 | 设置为 `1` 以要求用户在登录前验证邮箱                                                                     |
-| `EMAIL_SERVICE_PROVIDER`              | 可选 | 邮件服务选择：`nodemailer`（默认，SMTP）或 `resend`                                                    |
-| `SMTP_HOST`                           | 必选 | SMTP 服务器主机名（如 `smtp.gmail.com`），仅在 `EMAIL_SERVICE_PROVIDER=nodemailer` 时需要                |
-| `SMTP_PORT`                           | 必选 | SMTP 服务器端口（TLS 通常为 `587`，SSL 为 `465`），仅在 `EMAIL_SERVICE_PROVIDER=nodemailer` 时需要          |
-| `SMTP_SECURE`                         | 可选 | SSL 设置为 `true`（端口 465），TLS 设置为 `false`（端口 587），仅在 `EMAIL_SERVICE_PROVIDER=nodemailer` 时需要 |
-| `SMTP_USER`                           | 必选 | SMTP 认证用户名，仅在 `EMAIL_SERVICE_PROVIDER=nodemailer` 时需要                                     |
-| `SMTP_PASS`                           | 必选 | SMTP 认证密码，仅在 `EMAIL_SERVICE_PROVIDER=nodemailer` 时需要                                      |
-| `RESEND_API_KEY`                      | 必选 | Resend API Key，`EMAIL_SERVICE_PROVIDER=resend` 时必填                                        |
-| `RESEND_FROM`                         | 推荐 | 默认发件人地址（如 `noreply@已验证域名`），需为 Resend 已验证域名下的邮箱，`EMAIL_SERVICE_PROVIDER=resend` 时使用        |
+
+### 魔法链接（免密）登录
+
+启用 BetterAuth 魔法链接登录（依赖上方已配置好的邮件服务）：
+
+| 环境变量                            | 类型 | 描述                |
+| ------------------------------- | -- | ----------------- |
+| `NEXT_PUBLIC_ENABLE_MAGIC_LINK` | 可选 | 设置为 `1` 以启用魔法链接登录 |

 <Callout type={'tip'}>
 详细的提供商配置可参考 [Next Auth 提供商文档](/zh/docs/self-hosting/advanced/auth/next-auth)（大部分配置兼容），或访问官方 [Better Auth 文档](https://www.better-auth.com/docs/introduction)。
diff --git a/package.json b/package.json
index 5a5b1df2d9e..907a096ac9c 100644
--- a/package.json
+++ b/package.json
@@ -285,6 +285,7 @@
     "remark": "^15.0.1",
     "remark-gfm": "^4.0.1",
     "remark-html": "^16.0.1",
+    "resend": "^6.5.2",
     "resolve-accept-language": "^3.1.15",
     "rtl-detect": "^1.1.15",
     "semver": "^7.7.3",
diff --git a/src/envs/email.ts b/src/envs/email.ts
index d1e6860994d..f33bc6e5801 100644
--- a/src/envs/email.ts
+++ b/src/envs/email.ts
@@ -11,6 +11,9 @@ declare global {
       SMTP_PORT?: string;
       SMTP_SECURE?: string;
       SMTP_USER?: string;
+      RESEND_API_KEY?: string;
+      RESEND_FROM?: string;
+      EMAIL_SERVICE_PROVIDER?: string;
     }
   }
 }
@@ -18,6 +21,9 @@ declare global {
 export const getEmailConfig = () => {
   return createEnv({
     server: {
+      EMAIL_SERVICE_PROVIDER: z.enum(['nodemailer', 'resend']).optional(),
+      RESEND_API_KEY: z.string().optional(),
+      RESEND_FROM: z.string().optional(),
       SMTP_HOST: z.string().optional(),
       SMTP_PORT: z.coerce.number().optional(),
       SMTP_SECURE: z.boolean().optional(),
@@ -30,6 +36,11 @@ export const getEmailConfig = () => {
       SMTP_SECURE: process.env.SMTP_SECURE === 'true',
       SMTP_USER: process.env.SMTP_USER,
       SMTP_PASS: process.env.SMTP_PASS,
+      EMAIL_SERVICE_PROVIDER: process.env.EMAIL_SERVICE_PROVIDER
+        ? process.env.EMAIL_SERVICE_PROVIDER.toLowerCase()
+        : undefined,
+      RESEND_API_KEY: process.env.RESEND_API_KEY,
+      RESEND_FROM: process.env.RESEND_FROM,
     },
   });
 };
diff --git a/src/libs/better-auth/email-templates/magic-link.ts b/src/libs/better-auth/email-templates/magic-link.ts
index 1e2945cb366..c5b55541eaa 100644
--- a/src/libs/better-auth/email-templates/magic-link.ts
+++ b/src/libs/better-auth/email-templates/magic-link.ts
@@ -18,7 +18,7 @@ export const getMagicLinkEmailTemplate = (params: { expiresInSeconds: number; ur
 <head>
   <meta charset="utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
-  <title>Sign in to LobeChat</title>
+  <title>Sign in to LobeHub</title>
 </head>
 <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f5; color: #1a1a1a;">
   <!-- Container -->
@@ -28,7 +28,7 @@ export const getMagicLinkEmailTemplate = (params: { expiresInSeconds: number; ur
     <div style="text-align: center; margin-bottom: 32px;">
       <div style="display: inline-flex; align-items: center; justify-content: center; background-color: #ffffff; border-radius: 12px; padding: 8px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
         <span style="font-size: 24px; line-height: 1; margin-right: 10px;">🤯</span>
-        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeChat</span>
+        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeHub</span>
       </div>
     </div>

@@ -38,7 +38,7 @@ export const getMagicLinkEmailTemplate = (params: { expiresInSeconds: number; ur
       <!-- Header -->
       <div style="text-align: center; margin-bottom: 32px;">
         <h1 style="color: #111827; font-size: 24px; font-weight: 700; margin: 0 0 12px 0; letter-spacing: -0.5px;">
-          Sign in to LobeChat
+          Sign in to LobeHub
         </h1>
         <p style="color: #6b7280; font-size: 16px; margin: 0; line-height: 1.5;">
           Click the link below to sign in to your account.
@@ -85,14 +85,14 @@ export const getMagicLinkEmailTemplate = (params: { expiresInSeconds: number; ur
     <!-- Footer -->
     <div style="text-align: center; margin-top: 32px;">
       <p style="color: #a1a1aa; font-size: 13px; margin: 0;">
-        © ${new Date().getFullYear()} LobeChat. All rights reserved.
+        © ${new Date().getFullYear()} LobeHub. All rights reserved.
       </p>
     </div>
   </div>
 </body>
 </html>
     `,
-    subject: 'Your LobeChat sign-in link',
+    subject: 'Your LobeHub sign-in link',
     text: `Use this link to sign in: ${url}\n\nThis link expires in ${expirationText}.`,
   };
 };
diff --git a/src/libs/better-auth/email-templates/reset-password.ts b/src/libs/better-auth/email-templates/reset-password.ts
index 2f7baed4175..15ebbbe68b1 100644
--- a/src/libs/better-auth/email-templates/reset-password.ts
+++ b/src/libs/better-auth/email-templates/reset-password.ts
@@ -22,7 +22,7 @@ export const getResetPasswordEmailTemplate = (params: { url: string }) => {
     <div style="text-align: center; margin-bottom: 32px;">
       <div style="display: inline-flex; align-items: center; justify-content: center; background-color: #ffffff; border-radius: 12px; padding: 8px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
         <span style="font-size: 24px; line-height: 1; margin-right: 10px;">🤯</span>
-        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeChat</span>
+        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeHub</span>
       </div>
     </div>

@@ -42,7 +42,7 @@ export const getResetPasswordEmailTemplate = (params: { url: string }) => {
       <!-- Content -->
       <div style="color: #374151; font-size: 16px; line-height: 1.6;">
         <p style="margin: 0 0 24px 0; text-align: center;">
-          You recently requested to reset your password for your LobeChat account. Click the button below to proceed.
+          You recently requested to reset your password for your LobeHub account. Click the button below to proceed.
         </p>

         <!-- Button -->
@@ -78,14 +78,14 @@ export const getResetPasswordEmailTemplate = (params: { url: string }) => {
     <!-- Footer -->
     <div style="text-align: center; margin-top: 32px;">
       <p style="color: #a1a1aa; font-size: 13px; margin: 0;">
-        © ${new Date().getFullYear()} LobeChat. All rights reserved.
+        © ${new Date().getFullYear()} LobeHub. All rights reserved.
       </p>
     </div>
   </div>
 </body>
 </html>
     `,
-    subject: 'Reset Your Password - LobeChat',
+    subject: 'Reset Your Password - LobeHub',
     text: `Reset your password by clicking this link: ${url}`,
   };
 };
diff --git a/src/libs/better-auth/email-templates/verification.ts b/src/libs/better-auth/email-templates/verification.ts
index 22d40498712..593be75655c 100644
--- a/src/libs/better-auth/email-templates/verification.ts
+++ b/src/libs/better-auth/email-templates/verification.ts
@@ -33,7 +33,7 @@ export const getVerificationEmailTemplate = (params: {
     <div style="text-align: center; margin-bottom: 32px;">
       <div style="display: inline-flex; align-items: center; justify-content: justify-content: center; background-color: #ffffff; border-radius: 12px; padding: 8px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
         <span style="font-size: 24px; line-height: 1; margin-right: 10px;">🤯</span>
-        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeChat</span>
+        <span style="font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.5px;">LobeHub</span>
       </div>
     </div>

@@ -55,7 +55,7 @@ export const getVerificationEmailTemplate = (params: {
         ${userName ? `<p style="margin: 0 0 16px 0;">Hi <strong>${userName}</strong>,</p>` : ''}

         <p style="margin: 0 0 24px 0;">
-          Thanks for creating an account with LobeChat. To access your account, please verify your email address by clicking the button below.
+          Thanks for creating an account with LobeHub. To access your account, please verify your email address by clicking the button below.
         </p>

         <!-- Button -->
@@ -95,14 +95,14 @@ export const getVerificationEmailTemplate = (params: {
     <!-- Footer -->
     <div style="text-align: center; margin-top: 32px;">
       <p style="color: #a1a1aa; font-size: 13px; margin: 0;">
-        © 2025 LobeChat. All rights reserved.
+        © 2025 LobeHub. All rights reserved.
       </p>
     </div>
   </div>
 </body>
 </html>
     `,
-    subject: 'Verify Your Email - LobeChat',
+    subject: 'Verify Your Email - LobeHub',
     text: `Please verify your email by clicking this link: ${url}\n\nThis link will expire in ${expirationText}.`,
   };
 };
diff --git a/src/server/services/email/README.md b/src/server/services/email/README.md
index 350da301753..5748dc1a34d 100644
--- a/src/server/services/email/README.md
+++ b/src/server/services/email/README.md
@@ -86,6 +86,25 @@ SMTP_USER=your-username
 SMTP_PASS=your-password
 ```

+### Resend
+
+If you prefer Resend, configure the following and initialize the service with `EmailImplType.Resend`:
+
+```bash
+RESEND_API_KEY=your-resend-api-key
+RESEND_FROM=noreply@example.com
+```
+
+`RESEND_FROM` is used when `from` is not provided in the payload.
+
+### Choose Provider by Environment
+
+Set `EMAIL_SERVICE_PROVIDER` to `nodemailer` or `resend` to pick the default implementation without changing code:
+
+```bash
+EMAIL_SERVICE_PROVIDER=resend
+```
+
 ### Using Well-Known Services

 You can also use well-known email services (Gmail, SendGrid, etc.):
diff --git a/src/server/services/email/impls/index.ts b/src/server/services/email/impls/index.ts
index 8f2002beb6c..cc8297e6ecd 100644
--- a/src/server/services/email/impls/index.ts
+++ b/src/server/services/email/impls/index.ts
@@ -1,4 +1,5 @@
 import { NodemailerImpl } from './nodemailer';
+import { ResendImpl } from './resend';
 import { EmailServiceImpl } from './type';

 /**
@@ -6,8 +7,8 @@ import { EmailServiceImpl } from './type';
  */
 export enum EmailImplType {
   Nodemailer = 'nodemailer',
+  Resend = 'resend',
   // Future providers can be added here:
-  // Resend = 'resend',
   // SendGrid = 'sendgrid',
 }

@@ -21,6 +22,9 @@ export const createEmailServiceImpl = (
     case EmailImplType.Nodemailer: {
       return new NodemailerImpl();
     }
+    case EmailImplType.Resend: {
+      return new ResendImpl();
+    }

     default: {
       return new NodemailerImpl();
diff --git a/src/server/services/email/impls/resend/index.ts b/src/server/services/email/impls/resend/index.ts
new file mode 100644
index 00000000000..71b93e88409
--- /dev/null
+++ b/src/server/services/email/impls/resend/index.ts
@@ -0,0 +1,120 @@
+import { TRPCError } from '@trpc/server';
+import debug from 'debug';
+import { Resend } from 'resend';
+import type { CreateEmailOptions } from 'resend';
+
+import { emailEnv } from '@/envs/email';
+
+import { EmailPayload, EmailResponse, EmailServiceImpl } from '../type';
+
+const log = debug('lobe-email:Resend');
+
+/**
+ * Resend implementation of the email service
+ */
+export class ResendImpl implements EmailServiceImpl {
+  private client: Resend;
+
+  constructor() {
+    if (!emailEnv.RESEND_API_KEY) {
+      throw new Error(
+        'RESEND_API_KEY environment variable is required to use Resend email service. Please configure it in your .env file.',
+      );
+    }
+
+    this.client = new Resend(emailEnv.RESEND_API_KEY);
+    log('Initialized Resend client');
+  }
+
+  async sendMail(payload: EmailPayload): Promise<EmailResponse> {
+    const from = payload.from ?? emailEnv.RESEND_FROM;
+    const html = payload.html;
+    const text = payload.text;
+
+    if (!from) {
+      throw new TRPCError({
+        code: 'PRECONDITION_FAILED',
+        message: 'Missing sender address. Provide payload.from or RESEND_FROM environment variable.',
+      });
+    }
+
+    if (!html && !text) {
+      throw new TRPCError({
+        code: 'PRECONDITION_FAILED',
+        message: 'Resend requires either html or text content in the email payload.',
+      });
+    }
+
+    const attachments = payload.attachments?.map((attachment) => {
+      if (attachment.content instanceof Buffer) {
+        return {
+          ...attachment,
+          content: attachment.content.toString('base64'),
+        };
+      }
+
+      return attachment;
+    });
+
+    try {
+      log('Sending email via Resend: %o', {
+        from,
+        subject: payload.subject,
+        to: payload.to,
+      });
+
+      const emailOptions: CreateEmailOptions = html
+        ? {
+            attachments,
+            from,
+            html,
+            replyTo: payload.replyTo,
+            subject: payload.subject,
+            text,
+            to: payload.to,
+          }
+        : {
+            attachments,
+            from,
+            replyTo: payload.replyTo,
+            subject: payload.subject,
+            text: text!,
+            to: payload.to,
+          };
+
+      const { data, error } = await this.client.emails.send(emailOptions);
+
+      if (error) {
+        log.extend('error')('Failed to send email via Resend: %o', error);
+        throw new TRPCError({
+          cause: error,
+          code: 'SERVICE_UNAVAILABLE',
+          message: `Failed to send email via Resend: ${error.message}`,
+        });
+      }
+
+      if (!data?.id) {
+        log.extend('error')('Resend sendMail returned no message id: %o', data);
+        throw new TRPCError({
+          code: 'SERVICE_UNAVAILABLE',
+          message: 'Failed to send email via Resend: missing message id',
+        });
+      }
+
+      return {
+        messageId: data.id,
+      };
+    } catch (error) {
+      if (error instanceof TRPCError) {
+        throw error;
+      }
+
+      log.extend('error')('Unexpected Resend sendMail error: %o', error);
+      throw new TRPCError({
+        cause: error,
+        code: 'SERVICE_UNAVAILABLE',
+        message: `Failed to send email via Resend: ${(error as Error).message}`,
+      });
+    }
+  }
+}
diff --git a/src/server/services/email/index.test.ts b/src/server/services/email/index.test.ts
index e84ff07364d..1bedd10ca94 100644
--- a/src/server/services/email/index.test.ts
+++ b/src/server/services/email/index.test.ts
@@ -26,7 +26,7 @@ describe('EmailService', () => {

   describe('constructor', () => {
     it('should create instance with default email implementation', () => {
-      expect(createEmailServiceImpl).toHaveBeenCalledWith(undefined);
+      expect(createEmailServiceImpl).toHaveBeenCalledWith(EmailImplType.Nodemailer);
     });

     it('should create instance with specified implementation type', () => {
diff --git a/src/server/services/email/index.ts b/src/server/services/email/index.ts
index 7e5889936dc..70dea243e50 100644
--- a/src/server/services/email/index.ts
+++ b/src/server/services/email/index.ts
@@ -1,3 +1,4 @@
+import { emailEnv } from '@/envs/email';

 import { EmailImplType, EmailPayload, EmailResponse, createEmailServiceImpl } from './impls';
 import type { EmailServiceImpl } from './impls';
@@ -10,7 +11,14 @@ export class EmailService {
   private emailImpl: EmailServiceImpl;

   constructor(implType?: EmailImplType) {
-    this.emailImpl = createEmailServiceImpl(implType);
+    // Avoid client-side access to server env when executed in browser-like test environments
+    const envImplType =
+      typeof window === 'undefined'
+        ? (emailEnv.EMAIL_SERVICE_PROVIDER as EmailImplType | undefined)
+        : undefined;
+    const resolvedImplType = implType ?? envImplType ?? EmailImplType.Nodemailer;
+
+    this.emailImpl = createEmailServiceImpl(resolvedImplType);
   }

   /**

PATCH

echo "Patch applied successfully."
