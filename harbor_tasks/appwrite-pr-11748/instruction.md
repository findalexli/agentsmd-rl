# Replace PHPMailer with utopia-php/messaging SMTP adapter

The codebase currently uses raw PHPMailer for SMTP functionality, creating tight coupling that makes it difficult to swap in alternative email adapters (like Resend), properly inject email configuration, and use modern attachment handling.

## Problem Description

The SMTP register (`app/init/registers.php`) currently creates and returns a `PHPMailer\PHPMailer\PHPMailer` instance with extensive manual configuration including SMTP setup methods like `isSMTP()`, `setFrom()`, `addReplyTo()`, `isHTML()`, and various property assignments (`XMailer`, `SMTPAuth`, `Username`, `Password`, `SMTPSecure`, `SMTPAutoTLS`, `SMTPKeepAlive`, `CharSet`, `Timeout`). The current tight coupling to PHPMailer prevents using the `Utopia\Messaging\Adapter\Email\SMTP` class with named parameters for `host`, `port`, `keepAlive`, `timelimit`, and other SMTP settings.

The Mails worker (`src/Appwrite/Platform/Workers/Mails.php`) contains PHPMailer-specific patterns including a protected method that constructs PHPMailer instances, and uses PHPMailer-specific state manipulation methods like `clearAddresses()`, `clearAllRecipients()`, `clearReplyTos()`, `clearAttachments()`, `clearBCCs()`, `clearCCs()`, `addAddress()`, as well as direct property assignments for `Subject`, `Body`, `AltBody`, and `AddStringAttachment`. These patterns prevent using `EmailAdapter` type hints, `EmailMessage` object construction, and the `Attachment` class from `utopia-php/messaging`.

The Doctor task (`src/Appwrite/Platform/Tasks/Doctor.php`) similarly uses PHPMailer-specific methods including `addAddress()`, `Subject`, `Body`, `AltBody`, and `$mail->send()` for sending test emails, preventing migration to `EmailAdapter` and `EmailMessage`.

The `Usage` class (`src/Appwrite/Event/Message/Usage.php`) is declared as `final class Usage` and its `fromArray()` method uses `new self(...)`. These patterns prevent proper subclassing and should be changed to allow extension and proper factory pattern usage.

The composer dependency on `utopia-php/messaging` is currently at version `0.20.*` and needs to be updated to `0.22.*` to access the new messaging adapter classes.

## Files to Modify

- `app/init/registers.php` - Return SMTP adapter instead of PHPMailer
- `src/Appwrite/Platform/Workers/Mails.php` - Use EmailAdapter, EmailMessage, Attachment
- `src/Appwrite/Platform/Tasks/Doctor.php` - Use EmailAdapter and EmailMessage
- `src/Appwrite/Event/Message/Usage.php` - Allow subclassing and proper factory pattern
- `composer.json` - Update utopia-php/messaging to 0.22.*
- `composer.lock` - Will auto-update on composer install

## Required Classes and Imports

The solution must import and use these classes from `utopia-php/messaging`:
- `Utopia\Messaging\Adapter\Email` (aliased as `EmailAdapter`)
- `Utopia\Messaging\Adapter\Email\SMTP`
- `Utopia\Messaging\Messages\Email` (aliased as `EmailMessage`)
- `Utopia\Messaging\Messages\Email\Attachment`

## Reference - SMTP Constructor Parameters

The `Utopia\Messaging\Adapter\Email\SMTP` constructor accepts these named parameters:
- `host`, `port`, `username`, `password` - SMTP connection settings
- `smtpSecure`, `smtpAutoTLS` - Security settings
- `xMailer` - X-Mailer header value
- `timeout` - Connection timeout
- `keepAlive` - Keep connection alive between sends
- `timelimit` - Per-command timeout

## Reference - EmailMessage Constructor Parameters

The `EmailMessage` constructor accepts:
- `to` - Array of recipients (each with 'email' and optional 'name')
- `subject`, `content` - Message content
- `fromName`, `fromEmail` - Sender info
- `replyToName`, `replyToEmail` - Reply-to info
- `attachments` - Array of `Attachment` objects
- `html` - Boolean indicating HTML content

## Success Criteria

After the changes:
- No PHPMailer imports should remain in the modified files
- No PHPMailer-specific methods (`clearAddresses`, `addAddress`, `Subject`, `Body`, etc.) should be present
- SMTP adapter should use named parameters for configuration
- Email messages should be sent via `$adapter->send($emailMessage)` or `$smtp->send($emailMessage)`
- The `Usage` class should not be declared `final` and should use `new static()` in `fromArray()`
- `composer.json` should require `utopia-php/messaging` version `0.22.*`
