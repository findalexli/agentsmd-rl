#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -qE '^\s+Resend = .resend.\s*,\s*$' src/server/services/email/impls/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use Python for all file modifications to ensure precision
python3 << 'PYEOF'
import os
import re

# 1. Update .cursor/rules/project-introduce.mdc
with open('.cursor/rules/project-introduce.mdc', 'r') as f:
    content = f.read()
content = content.replace(
    'You are developing an open-source, modern-design AI chat framework: lobehub(previous lobe-chat).',
    'You are developing an open-source, modern-design AI Agent Workspace: LobeHub(previous LobeChat).'
)
with open('.cursor/rules/project-introduce.mdc', 'w') as f:
    f.write(content)
print('Updated project-introduce.mdc')

# 2. Update AGENTS.md - add Project Description after title
with open('AGENTS.md', 'r') as f:
    content = f.read()
if '## Project Description' not in content:
    content = content.replace(
        'This document serves as a comprehensive guide for all team members when developing LobeChat.',
        'This document serves as a comprehensive guide for all team members when developing LobeChat.\n\n## Project Description\n\nYou are developing an open-source, modern-design AI Agent Workspace: LobeHub(previous LobeChat).'
    )
    with open('AGENTS.md', 'w') as f:
        f.write(content)
    print('Updated AGENTS.md')
else:
    print('AGENTS.md already has Project Description')

# 3. Update docs/self-hosting/advanced/auth.mdx
with open('docs/self-hosting/advanced/auth.mdx', 'r') as f:
    content = f.read()

old_section = '''### Email Service Configuration

If you want to enable email verification or password reset features, you need to configure SMTP settings:

| Environment Variable                  | Type     | Description                                                       |
| ------------------------------------- | -------- | ----------------------------------------------------------------- |
| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | Optional | Set to `1` to require email verification before users can sign in |
| `SMTP_HOST`                           | Required | SMTP server hostname (e.g., `smtp.gmail.com`)                     |
| `SMTP_PORT`                           | Required | SMTP server port (usually `587` for TLS, `465` for SSL)           |
| `SMTP_SECURE`                         | Optional | Set to `true` for SSL (port `465`), `false` for TLS (port `587`)      |
| `SMTP_USER`                           | Required | SMTP authentication username                                      |
| `SMTP_PASS`                           | Required | SMTP authentication password                                      |

<Callout type={'tip'}>
  For detailed provider configuration, refer to the [Next Auth provider documentation](/docs/self-hosting/advanced/auth/next-auth) as most configurations are compatible, or visit the official [Better Auth documentation](https://www.better-auth.com/docs/introduction).
</Callout>'''

new_section = '''### Email Service Configuration

Used by email verification, password reset, and magic-link delivery. Choose a provider, then fill the matching variables:

| Environment Variable                  | Type        | Description                                                                                                                                       |
| ------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `NEXT_PUBLIC_AUTH_EMAIL_VERIFICATION` | Optional    | Set to `1` to require email verification before users can sign in                                                                                 |
| `EMAIL_SERVICE_PROVIDER`              | Optional    | Email provider selector: `nodemailer` (default, SMTP) or `resend`                                                                                 |
| `SMTP_HOST`                           | Required    | SMTP server hostname (e.g., `smtp.gmail.com`). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                      |
| `SMTP_PORT`                           | Required    | SMTP server port (usually `587` for TLS, `465` for SSL). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                            |
| `SMTP_SECURE`                         | Optional    | `true` for SSL (port `465`), `false` for TLS (port `587`). Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                              |
| `SMTP_USER`                           | Required    | SMTP auth username. Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                                                 |
| `SMTP_PASS`                           | Required    | SMTP auth password. Used when `EMAIL_SERVICE_PROVIDER=nodemailer`                                                                                 |
| `RESEND_API_KEY`                      | Required    | Resend API key. Required when `EMAIL_SERVICE_PROVIDER=resend`                                                                                     |
| `RESEND_FROM`                         | Recommended | Default sender address (e.g., `noreply@your-verified-domain.com`). Must be a domain verified in Resend. Used when `EMAIL_SERVICE_PROVIDER=resend` |

### Magic Link (Passwordless) Login

Enable BetterAuth magic-link login (depends on a working email provider above):

| Environment Variable            | Type     | Description                                        |
| ------------------------------- | -------- | -------------------------------------------------- |
| `NEXT_PUBLIC_ENABLE_MAGIC_LINK` | Optional | Set to `1` to enable passwordless magic-link login |

<Callout type={'tip'}>
  For detailed provider configuration, refer to the [Next Auth provider documentation](/docs/self-hosting/advanced/auth/next-auth) as most configurations are compatible, or visit the official [Better Auth documentation](https://www.better-auth.com/docs/introduction).
</Callout>'''

if old_section in content:
    content = content.replace(old_section, new_section)
    with open('docs/self-hosting/advanced/auth.mdx', 'w') as f:
        f.write(content)
    print('Updated auth.mdx')
else:
    print('WARNING: auth.mdx section not found as expected')

# 4. Update package.json
with open('package.json', 'r') as f:
    content = f.read()
if '"resend"' not in content:
    content = content.replace(
        '"remark-html": "^16.0.1",',
        '"remark-html": "^16.0.1",\n    "resend": "^6.5.2",'
    )
    with open('package.json', 'w') as f:
        f.write(content)
    print('Updated package.json')
else:
    print('package.json already has resend')

# 5. Update src/envs/email.ts
with open('src/envs/email.ts', 'r') as f:
    content = f.read()

# Add env vars to global namespace
if 'RESEND_API_KEY' not in content:
    content = content.replace(
        'SMTP_USER?: string;\n    }',
        'SMTP_USER?: string;\n      RESEND_API_KEY?: string;\n      RESEND_FROM?: string;\n      EMAIL_SERVICE_PROVIDER?: string;\n    }'
    )
    print('Updated email.ts globals')

# Add server config
if "EMAIL_SERVICE_PROVIDER: z.enum" not in content:
    content = content.replace(
        '''server: {
      SMTP_HOST: z.string().optional(),''',
        '''server: {
      EMAIL_SERVICE_PROVIDER: z.enum(['nodemailer', 'resend']).optional(),
      RESEND_API_KEY: z.string().optional(),
      RESEND_FROM: z.string().optional(),
      SMTP_HOST: z.string().optional(),'''
    )
    print('Updated email.ts server config')

# Add runtime mappings
if 'process.env.RESEND_API_KEY' not in content:
    content = content.replace(
        '''SMTP_PASS: process.env.SMTP_PASS,
    },''',
        '''SMTP_PASS: process.env.SMTP_PASS,
      EMAIL_SERVICE_PROVIDER: process.env.EMAIL_SERVICE_PROVIDER
        ? process.env.EMAIL_SERVICE_PROVIDER.toLowerCase()
        : undefined,
      RESEND_API_KEY: process.env.RESEND_API_KEY,
      RESEND_FROM: process.env.RESEND_FROM,
    },'''
    )
    with open('src/envs/email.ts', 'w') as f:
        f.write(content)
    print('Updated email.ts runtime mappings')
else:
    print('email.ts already has RESEND_API_KEY')

# 6. Create resend/index.ts
os.makedirs('src/server/services/email/impls/resend', exist_ok=True)
resend_impl = '''import { TRPCError } from '@trpc/server';
import debug from 'debug';
import { Resend } from 'resend';
import type { CreateEmailOptions } from 'resend';

import { emailEnv } from '@/envs/email';

import { EmailPayload, EmailResponse, EmailServiceImpl } from '../type';

const log = debug('lobe-email:Resend');

/**
 * Resend implementation of the email service
 */
export class ResendImpl implements EmailServiceImpl {
  private client: Resend;

  constructor() {
    if (!emailEnv.RESEND_API_KEY) {
      throw new Error(
        'RESEND_API_KEY environment variable is required to use Resend email service. Please configure it in your .env file.',
      );
    }

    this.client = new Resend(emailEnv.RESEND_API_KEY);
    log('Initialized Resend client');
  }

  async sendMail(payload: EmailPayload): Promise<EmailResponse> {
    const from = payload.from ?? emailEnv.RESEND_FROM;
    const html = payload.html;
    const text = payload.text;

    if (!from) {
      throw new TRPCError({
        code: 'PRECONDITION_FAILED',
        message: 'Missing sender address. Provide payload.from or RESEND_FROM environment variable.',
      });
    }

    if (!html && !text) {
      throw new TRPCError({
        code: 'PRECONDITION_FAILED',
        message: 'Resend requires either html or text content in the email payload.',
      });
    }

    const attachments = payload.attachments?.map((attachment) => {
      if (attachment.content instanceof Buffer) {
        return {
          ...attachment,
          content: attachment.content.toString('base64'),
        };
      }

      return attachment;
    });

    try {
      log('Sending email via Resend: %o', {
        from,
        subject: payload.subject,
        to: payload.to,
      });

      const emailOptions: CreateEmailOptions = html
        ? {
            attachments,
            from,
            html,
            replyTo: payload.replyTo,
            subject: payload.subject,
            text,
            to: payload.to,
          }
        : {
            attachments,
            from,
            replyTo: payload.replyTo,
            subject: payload.subject,
            text: text!,
            to: payload.to,
          };

      const { data, error } = await this.client.emails.send(emailOptions);

      if (error) {
        log.extend('error')('Failed to send email via Resend: %o', error);
        throw new TRPCError({
          cause: error,
          code: 'SERVICE_UNAVAILABLE',
          message: `Failed to send email via Resend: ${error.message}`,
        });
      }

      if (!data?.id) {
        log.extend('error')('Resend sendMail returned no message id: %o', data);
        throw new TRPCError({
          code: 'SERVICE_UNAVAILABLE',
          message: 'Failed to send email via Resend: missing message id',
        });
      }

      return {
        messageId: data.id,
      };
    } catch (error) {
      if (error instanceof TRPCError) {
        throw error;
      }

      log.extend('error')('Unexpected Resend sendMail error: %o', error);
      throw new TRPCError({
        cause: error,
        code: 'SERVICE_UNAVAILABLE',
        message: `Failed to send email via Resend: ${(error as Error).message}`,
      });
    }
  }
}
'''
with open('src/server/services/email/impls/resend/index.ts', 'w') as f:
    f.write(resend_impl)
print('Created resend/index.ts')

# 7. Update impls/index.ts
with open('src/server/services/email/impls/index.ts', 'r') as f:
    content = f.read()

# Add import
if "import { ResendImpl } from './resend';" not in content:
    content = content.replace(
        "import { NodemailerImpl } from './nodemailer';",
        "import { NodemailerImpl } from './nodemailer';\nimport { ResendImpl } from './resend';"
    )
    print('Updated impls/index.ts import')

# Update enum - uncomment Resend, remove the commented line
content = content.replace(
    "Nodemailer = 'nodemailer',\n  // Future providers can be added here:\n  // Resend = 'resend',",
    "Nodemailer = 'nodemailer',\n  Resend = 'resend',\n  // Future providers can be added here:"
)
print('Updated impls/index.ts enum')

# Add case to switch
if 'case EmailImplType.Resend:' not in content:
    content = content.replace(
        '''    case EmailImplType.Nodemailer: {
      return new NodemailerImpl();
    }

    default:''',
        '''    case EmailImplType.Nodemailer: {
      return new NodemailerImpl();
    }
    case EmailImplType.Resend: {
      return new ResendImpl();
    }

    default:'''
    )
    with open('src/server/services/email/impls/index.ts', 'w') as f:
        f.write(content)
    print('Updated impls/index.ts switch')
else:
    with open('src/server/services/email/impls/index.ts', 'w') as f:
        f.write(content)
    print('impls/index.ts switch already updated')

# 8. Update README.md
with open('src/server/services/email/README.md', 'r') as f:
    readme = f.read()

if '### Resend' not in readme:
    readme += '''

### Resend

If you prefer Resend, configure the following and initialize the service with `EmailImplType.Resend`:

```bash
RESEND_API_KEY=your-resend-api-key
RESEND_FROM=noreply@example.com
```

`RESEND_FROM` is used when `from` is not provided in the payload.

### Choose Provider by Environment

Set `EMAIL_SERVICE_PROVIDER` to `nodemailer` or `resend` to pick the default implementation without changing code:

```bash
EMAIL_SERVICE_PROVIDER=resend
```
'''
    with open('src/server/services/email/README.md', 'w') as f:
        f.write(readme)
    print('Updated README.md')
else:
    print('README.md already has Resend section')

# 9. Update index.test.ts
with open('src/server/services/email/index.test.ts', 'r') as f:
    content = f.read()
content = content.replace(
    'expect(createEmailServiceImpl).toHaveBeenCalledWith(undefined);',
    'expect(createEmailServiceImpl).toHaveBeenCalledWith(EmailImplType.Nodemailer);'
)
with open('src/server/services/email/index.test.ts', 'w') as f:
    f.write(content)
print('Updated index.test.ts')

# 10. Update index.ts
with open('src/server/services/email/index.ts', 'r') as f:
    content = f.read()

if "import { emailEnv } from '@/envs/email';" not in content:
    content = "import { emailEnv } from '@/envs/email';\n\n" + content
    print('Added import to index.ts')

old_constructor = '''  constructor(implType?: EmailImplType) {
    this.emailImpl = createEmailServiceImpl(implType);
  }'''

new_constructor = '''  constructor(implType?: EmailImplType) {
    // Avoid client-side access to server env when executed in browser-like test environments
    const envImplType =
      typeof window === 'undefined'
        ? (emailEnv.EMAIL_SERVICE_PROVIDER as EmailImplType | undefined)
        : undefined;
    const resolvedImplType = implType ?? envImplType ?? EmailImplType.Nodemailer;

    this.emailImpl = createEmailServiceImpl(resolvedImplType);
  }'''

content = content.replace(old_constructor, new_constructor)
with open('src/server/services/email/index.ts', 'w') as f:
    f.write(content)
print('Updated index.ts constructor')

print('\nAll modifications completed successfully!')
PYEOF

echo "Patch applied successfully."
