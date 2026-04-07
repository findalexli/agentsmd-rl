# Add Resend Email Provider Support

The email service in `src/server/services/email/` currently only supports SMTP via Nodemailer. The project needs to add [Resend](https://resend.com) as an alternative email delivery provider.

## What needs to change

### Code changes

1. **New Resend implementation**: Create a `ResendImpl` class in `src/server/services/email/impls/resend/index.ts` that implements the `EmailServiceImpl` interface. It should:
   - Initialize a Resend client using `RESEND_API_KEY`
   - Handle missing `from` address by falling back to `RESEND_FROM` env var
   - Convert Buffer attachments to base64 for the Resend API
   - Throw `TRPCError` with appropriate error codes for failures

2. **Register the provider**: Add `Resend = 'resend'` to the `EmailImplType` enum in `src/server/services/email/impls/index.ts`, import the new `ResendImpl`, and add a factory case.

3. **Environment configuration**: Add `RESEND_API_KEY`, `RESEND_FROM`, and `EMAIL_SERVICE_PROVIDER` to `src/envs/email.ts`. The `EMAIL_SERVICE_PROVIDER` should accept `'nodemailer'` or `'resend'`.

4. **Provider resolution**: Update `src/server/services/email/index.ts` so the `EmailService` constructor reads `EMAIL_SERVICE_PROVIDER` from the environment and uses it as the default when no explicit type is passed.

5. **Dependency**: Add the `resend` npm package to `package.json` dependencies.

### Documentation/config updates

The project's documentation must be updated to reflect these changes:

- **`src/server/services/email/README.md`**: Document the Resend provider configuration, including the `RESEND_API_KEY` and `RESEND_FROM` environment variables, and the `EMAIL_SERVICE_PROVIDER` selector.

- **`AGENTS.md`**: Add a "Project Description" section at the top (after the title) that describes the project as an "AI Agent Workspace" under the LobeHub name.

Look at the existing `NodemailerImpl` in `src/server/services/email/impls/nodemailer/` for the implementation pattern, and at the existing README for documentation style.
