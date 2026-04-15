# Add Resend Email Provider Support

The email service in `src/server/services/email/` currently only supports SMTP via Nodemailer. The project needs to add [Resend](https://resend.com) as an alternative email delivery provider.

## Problem Description

When attempting to use Resend as an email provider, the service cannot:
1. Instantiate a Resend-specific implementation because no implementation class exists
2. Select Resend via the factory because `EmailImplType` enum lacks a `resend` value
3. Configure Resend credentials because `RESEND_API_KEY` and `RESEND_FROM` are not defined in the environment schema
4. Choose a provider via environment variables because `EMAIL_SERVICE_PROVIDER` is not supported

The service should support both providers with Nodemailer remaining the default when no explicit selection is made.

## Functional Requirements

### 1. Resend Provider Implementation
Create a Resend implementation following the pattern established by `NodemailerImpl` in `src/server/services/email/impls/nodemailer/`. The implementation must:
- Conform to the `EmailServiceImpl` interface (imported from `../type`)
- Initialize a Resend client using an API key from environment configuration
- Implement `sendMail(payload: EmailPayload): Promise<EmailResponse>`
- Handle missing sender addresses by falling back to a configured default
- Convert Buffer attachments to base64 strings for the Resend API
- Use `TRPCError` from `@trpc/server` for error handling with appropriate error codes (`PRECONDITION_FAILED` for configuration issues, `SERVICE_UNAVAILABLE` for API failures)

### 2. Factory Registration
Extend the `EmailImplType` enum in `src/server/services/email/impls/index.ts` to include a `resend` value with the literal string `'resend'`. Update the factory function to instantiate the Resend implementation when this type is requested.

### 3. Environment Configuration
Add to `src/envs/email.ts`:
- `RESEND_API_KEY` - API key for Resend authentication
- `RESEND_FROM` - Default sender address for Resend emails
- `EMAIL_SERVICE_PROVIDER` - Provider selector accepting `'nodemailer'` or `'resend'` values

### 4. Provider Selection via Environment
Modify `src/server/services/email/index.ts` so the `EmailService` constructor reads `EMAIL_SERVICE_PROVIDER` from the environment configuration. The logic should:
- Use the environment-specified provider when no explicit type is passed to the constructor
- Fall back to Nodemailer when `EMAIL_SERVICE_PROVIDER` is unset

### 5. Dependency
Add the `resend` npm package to `package.json` dependencies.

## Documentation Requirements

### Email Service README
Update `src/server/services/email/README.md` to document the Resend provider. The documentation must include:
- A `Resend` section header
- Documentation of `RESEND_API_KEY` for API authentication
- Documentation of `RESEND_FROM` for default sender address
- Documentation of `EMAIL_SERVICE_PROVIDER` for selecting between `nodemailer` and `resend`

### AGENTS.md Project Description
Add a section with the heading `## Project Description` to `AGENTS.md` that describes the project as an "AI Agent Workspace" under the "LobeHub" name.

## Reference
The existing `NodemailerImpl` in `src/server/services/email/impls/nodemailer/` demonstrates the expected implementation pattern.
