# Replace PHPMailer with utopia-php/messaging SMTP adapter

The codebase currently uses raw PHPMailer for SMTP functionality. This needs to be refactored to use the `Utopia\Messaging\Adapter\Email\SMTP` adapter instead, which provides a cleaner abstraction and enables dependency injection with other email adapters.

## What's broken

The SMTP register (`app/init/registers.php`) currently creates and returns a `PHPMailer\PHPMailer\PHPMailer` instance with extensive manual configuration. The Mails worker (`src/Appwrite/Platform/Workers/Mails.php`) and Doctor task (`src/Appwrite/Platform/Tasks/Doctor.php`) interact with this PHPMailer instance directly, using methods like `clearAddresses()`, `addAddress()`, `Subject`, `Body`, etc.

This tight coupling to PHPMailer makes it difficult to:
- Swap in alternative email adapters (like Resend)
- Properly inject email configuration
- Use modern attachment handling

## What needs to change

1. **app/init/registers.php**: Replace the PHPMailer instantiation with `new SMTP(...)` using named parameters. Remove all PHPMailer-specific configuration (isSMTP, setFrom, addReplyTo, isHTML, etc.). Return the SMTP adapter directly.

2. **src/Appwrite/Platform/Workers/Mails.php**: 
   - Replace PHPMailer import with imports for `EmailAdapter`, `SMTP`, `EmailMessage`, and `Attachment` from `utopia-php/messaging`
   - Remove the `getMailer()` protected method entirely
   - When custom SMTP config is provided, construct a new `SMTP(...)` directly instead of calling `getMailer()`
   - Replace all PHPMailer state manipulation (clearAddresses, clearAttachments, addAddress, Subject, Body, AltBody, etc.) with construction of an `EmailMessage` object
   - Handle attachments using the new `Attachment` class with string content
   - Call `$adapter->send($emailMessage)` to send

3. **src/Appwrite/Platform/Tasks/Doctor.php**:
   - Replace PHPMailer import with `EmailAdapter` and `EmailMessage` imports
   - Replace PHPMailer-specific code with `EmailMessage` construction and `$smtp->send($emailMessage)`

4. **src/Appwrite/Event/Message/Usage.php**:
   - Remove `final` keyword from class declaration
   - Change `new self(...)` to `new static(...)` in `fromArray()`

5. **composer.json**: Update `utopia-php/messaging` requirement from `0.20.*` to `0.22.*`

## Files to modify

- `app/init/registers.php`
- `src/Appwrite/Platform/Workers/Mails.php`
- `src/Appwrite/Platform/Tasks/Doctor.php`
- `src/Appwrite/Event/Message/Usage.php`
- `composer.json`
- `composer.lock` (will auto-update on composer install)

## Reference

The `Utopia\Messaging\Adapter\Email\SMTP` constructor accepts these named parameters:
- `host`, `port`, `username`, `password` - SMTP connection settings
- `smtpSecure`, `smtpAutoTLS` - Security settings
- `xMailer` - X-Mailer header value
- `timeout` - Connection timeout
- `keepAlive` - Keep connection alive between sends
- `timelimit` - Per-command timeout

The `EmailMessage` constructor accepts:
- `to` - Array of recipients (each with 'email' and optional 'name')
- `subject`, `content` - Message content
- `fromName`, `fromEmail` - Sender info
- `replyToName`, `replyToEmail` - Reply-to info
- `attachments` - Array of `Attachment` objects
- `html` - Boolean indicating HTML content
