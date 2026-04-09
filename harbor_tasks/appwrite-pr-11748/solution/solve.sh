#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already applied
if grep -q "Utopia\\\\Messaging\\\\Adapter\\\\Email\\\\SMTP" app/init/registers.php 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the patch
patch -p1 <<'PATCH'
diff --git a/app/init/registers.php b/app/init/registers.php
index 88160aae79b..68ccbd20975 100644
--- a/app/init/registers.php
+++ b/app/init/registers.php
@@ -6,7 +6,6 @@
 use Appwrite\PubSub\Adapter\Redis as PubSub;
 use Appwrite\URL\URL as AppwriteURL;
 use MaxMind\Db\Reader;
-use PHPMailer\PHPMailer\PHPMailer;
 use Swoole\Database\PDOProxy;
 use Utopia\Cache\Adapter\Redis as RedisCache;
 use Utopia\Config\Config;
@@ -25,6 +24,7 @@
 use Utopia\Logger\Adapter\Raygun;
 use Utopia\Logger\Adapter\Sentry;
 use Utopia\Logger\Logger;
+use Utopia\Messaging\Adapter\Email\SMTP;
 use Utopia\Mongo\Client as MongoClient;
 use Utopia\Pools\Adapter\Stack as StackPool;
 use Utopia\Pools\Adapter\Swoole as SwoolePool;
@@ -433,35 +433,20 @@
 });

 $register->set('smtp', function () {
-    $mail = new PHPMailer(true);
-
-    $mail->isSMTP();
-
-    $username = System::getEnv('_APP_SMTP_USERNAME');
-    $password = System::getEnv('_APP_SMTP_PASSWORD');
-
-    $mail->XMailer = 'Appwrite Mailer';
-    $mail->Host = System::getEnv('_APP_SMTP_HOST', 'smtp');
-    $mail->Port = (int) System::getEnv('_APP_SMTP_PORT', 25);
-    $mail->SMTPAuth = !empty($username) && !empty($password);
-    $mail->Username = $username;
-    $mail->Password = $password;
-    $mail->SMTPSecure = System::getEnv('_APP_SMTP_SECURE', '');
-    $mail->SMTPAutoTLS = false;
-    $mail->SMTPKeepAlive = true;
-    $mail->CharSet = 'UTF-8';
-    $mail->Timeout = 10; /* Connection timeout */
-    $mail->getSMTPInstance()->Timelimit = 30; /* Timeout for each individual SMTP command (e.g. HELO, EHLO, etc.) */
-
-    $from = \urldecode(System::getEnv('_APP_SYSTEM_EMAIL_NAME', APP_NAME . ' Server'));
-    $email = System::getEnv('_APP_SYSTEM_EMAIL_ADDRESS', APP_EMAIL_TEAM);
-
-    $mail->setFrom($email, $from);
-    $mail->addReplyTo($email, $from);
-
-    $mail->isHTML(true);
-
-    return $mail;
+    $username = System::getEnv('_APP_SMTP_USERNAME', '');
+    $password = System::getEnv('_APP_SMTP_PASSWORD', '');
+    return new SMTP(
+        host: System::getEnv('_APP_SMTP_HOST', 'smtp'),
+        port: (int) System::getEnv('_APP_SMTP_PORT', 25),
+        username: $username,
+        password: $password,
+        smtpSecure: System::getEnv('_APP_SMTP_SECURE', ''),
+        smtpAutoTLS: false,
+        xMailer: 'Appwrite Mailer',
+        timeout: 10,
+        keepAlive: true,
+        timelimit: 30,
+    );
 });
 $register->set('geodb', function () {
     return new Reader(__DIR__ . '/../assets/dbip/dbip-country-lite-2025-12.mmdb');
diff --git a/composer.json b/composer.json
index 1a530bfc5be..0f4dcfb8db4 100644
--- a/composer.json
+++ b/composer.json
@@ -72,7 +72,7 @@
         "utopia-php/image": "0.8.*",
         "utopia-php/locale": "0.8.*",
         "utopia-php/logger": "0.6.*",
-        "utopia-php/messaging": "0.20.*",
+        "utopia-php/messaging": "0.22.*",
         "utopia-php/migration": "1.9.*",
         "utopia-php/platform": "0.7.*",
         "utopia-php/pools": "1.*",
diff --git a/composer.lock b/composer.lock
index 0a79c5bee38..420dddc9a53 100644
--- a/composer.lock
+++ b/composer.lock
@@ -4,7 +4,7 @@
         "Read more about it at https://getcomposer.org/doc/01-basic-usage.md#installing-dependencies",
         "This file is @generated automatically"
     ],
-    "content-hash": "b5261855586680e467168f527e0634ae",
+    "content-hash": "4fe91e67f343fbe6deac1fdc7eda949f",
     "packages": [
         {
             "name": "adhocore/jwt",
@@ -4467,23 +4467,23 @@
         },
         {
             "name": "utopia-php/messaging",
-            "version": "0.20.1",
+            "version": "0.22.0",
             "source": {
                 "type": "git",
                 "url": "https://github.com/utopia-php/messaging.git",
-                "reference": "fcb4c3c46a48008a677957690bd45ec934dd33b0"
+                "reference": "a6ac04fd204fb6a16bf8c75a84d0b9fc10aa5030"
             },
             "dist": {
                 "type": "zip",
-                "url": "https://api.github.com/repos/utopia-php/messaging/zipball/fcb4c3c46a48008a677957690bd45ec934dd33b0",
-                "reference": "fcb4c3c46a48008a677957690bd45ec934dd33b0",
+                "url": "https://api.github.com/repos/utopia-php/messaging/zipball/a6ac04fd204fb6a16bf8c75a84d0b9fc10aa5030",
+                "reference": "a6ac04fd204fb6a16bf8c75a84d0b9fc10aa5030",
                 "shasum": ""
             },
             "require": {
                 "ext-curl": "*",
                 "ext-openssl": "*",
                 "giggsey/libphonenumber-for-php-lite": "9.0.23",
-                "php": ">=8.0.0",
+                "php": ">=8.1.0",
                 "phpmailer/phpmailer": "6.9.1"
             },
             "require-dev": {
@@ -4512,9 +4512,9 @@
             ],
             "support": {
                 "issues": "https://github.com/utopia-php/messaging/issues",
-                "source": "https://github.com/utopia-php/messaging/tree/0.20.1"
+                "source": "https://github.com/utopia-php/messaging/tree/0.22.0"
             },
-            "time": "2026-02-06T09:56:06+00:00"
+            "time": "2026-04-02T04:09:19+00:00"
         },
         {
             "name": "utopia-php/migration",
diff --git a/src/Appwrite/Event/Message/Usage.php b/src/Appwrite/Event/Message/Usage.php
index ec8484e45ec..c72bc8ae2a2 100644
--- a/src/Appwrite/Event/Message/Usage.php
+++ b/src/Appwrite/Event/Message/Usage.php
@@ -4,7 +4,7 @@

 use Utopia\Database\Document;

-final class Usage extends Base
+class Usage extends Base
 {
     /**
      * @param Document $project
@@ -40,7 +40,8 @@ public function toArray(): array
      */
     public static function fromArray(array $data): static
     {
-        return new self(
+        /** @phpstan-ignore new.static (subclass constructors are backwards-compatible via optional params) */
+        return new static(
             project: new Document($data['project'] ?? []),
             metrics: $data['metrics'] ?? [],
             reduce: array_map(fn (array $doc) => new Document($doc), $data['reduce'] ?? []),
diff --git a/src/Appwrite/Platform/Tasks/Doctor.php b/src/Appwrite/Platform/Tasks/Doctor.php
index 67b6eb44622..3eeaa95e642 100644
--- a/src/Appwrite/Platform/Tasks/Doctor.php
+++ b/src/Appwrite/Platform/Tasks/Doctor.php
@@ -4,7 +4,6 @@

 use Appwrite\ClamAV\Network;
 use Appwrite\PubSub\Adapter\Pool as PubSubPool;
-use PHPMailer\PHPMailer\PHPMailer;
 use Utopia\Cache\Adapter\Pool as CachePool;
 use Utopia\Config\Config;
 use Utopia\Console;
@@ -13,6 +12,8 @@
 use Utopia\DSN\DSN;
 use Utopia\Http\Http;
 use Utopia\Logger\Logger;
+use Utopia\Messaging\Adapter\Email as EmailAdapter;
+use Utopia\Messaging\Messages\Email as EmailMessage;
 use Utopia\Platform\Action;
 use Utopia\Pools\Group;
 use Utopia\Queue\Broker\Pool as BrokerPool;
@@ -212,15 +213,18 @@ public function action(Registry $register): void
         }

         try {
-            /* @var PHPMailer $mail */
-            $mail = $register->get('smtp');
-
-            $mail->addAddress('demo@example.com', 'Example.com');
-            $mail->Subject = 'Test SMTP Connection';
-            $mail->Body = 'Hello World';
-            $mail->AltBody = 'Hello World';
-
-            $mail->send();
+            /** @var EmailAdapter $smtp */
+            $smtp = $register->get('smtp');
+
+            $emailMessage = new EmailMessage(
+                to: ['demo@example.com'],
+                subject: 'Test SMTP Connection',
+                content: 'Hello World',
+                fromName: \urldecode(System::getEnv('_APP_SYSTEM_EMAIL_NAME', APP_NAME . ' Server')),
+                fromEmail: System::getEnv('_APP_SYSTEM_EMAIL_ADDRESS', APP_EMAIL_TEAM),
+            );
+
+            $smtp->send($emailMessage);
             Console::success('🟢 ' . str_pad("SMTP", 50, '.') . 'connected');
         } catch (\Throwable) {
             Console::error('🔴 ' . str_pad("SMTP", 47, '.') . 'disconnected');
diff --git a/src/Appwrite/Platform/Workers/Mails.php b/src/Appwrite/Platform/Workers/Mails.php
index f144c58e1b9..32de1e50d6e 100644
--- a/src/Appwrite/Platform/Workers/Mails.php
+++ b/src/Appwrite/Platform/Workers/Mails.php
@@ -4,10 +4,13 @@

 use Appwrite\Template\Template;
 use Exception;
-use PHPMailer\PHPMailer\PHPMailer;
 use Swoole\Runtime;
 use Utopia\Database\Document;
 use Utopia\Logger\Log;
+use Utopia\Messaging\Adapter\Email as EmailAdapter;
+use Utopia\Messaging\Adapter\Email\SMTP;
+use Utopia\Messaging\Messages\Email as EmailMessage;
+use Utopia\Messaging\Messages\Email\Attachment;
 use Utopia\Platform\Action;
 use Utopia\Queue\Message;
 use Utopia\Registry\Registry;
@@ -49,9 +52,9 @@ public function __construct()

     /**
      * @param Message $message
+     * @param Document $project
      * @param Registry $register
      * @param Log $log
-     * @throws \PHPMailer\PHPMailer\Exception
      * @return void
      * @throws Exception
      */
@@ -132,36 +135,38 @@ public function action(Message $message, Document $project, Registry $register,
         // render() will return the subject in <p> tags, so use strip_tags() to remove them
         $subject = \strip_tags($subjectTemplate->render());

-        /** @var PHPMailer $mail */
-        $mail = empty($smtp)
+        /** @var EmailAdapter $adapter */
+        $adapter = empty($smtp)
             ? $register->get('smtp')
-            : $this->getMailer($smtp);
-
-        $mail->clearAddresses();
-        $mail->clearAllRecipients();
-        $mail->clearReplyTos();
-        $mail->clearAttachments();
-        $mail->clearBCCs();
-        $mail->clearCCs();
-        $mail->addAddress($recipient, $name);
-        $mail->Subject = $subject;
-        $mail->Body = $body;
-
-        $mail->AltBody = $body;
-        $mail->AltBody = preg_replace('/<style\b[^>]*>(.*?)<\/style>/is', '', $mail->AltBody);
-        $mail->AltBody = \strip_tags($mail->AltBody);
-        $mail->AltBody = \trim($mail->AltBody);
-
-        $replyTo = System::getEnv('_APP_SYSTEM_EMAIL_ADDRESS', APP_EMAIL_TEAM);
-        $replyToName = \urldecode(System::getEnv('_APP_SYSTEM_EMAIL_NAME', APP_NAME . ' Server'));
+            : new SMTP(
+                host: $smtp['host'],
+                port: (int) $smtp['port'],
+                username: $smtp['username'] ?? '',
+                password: $smtp['password'] ?? '',
+                smtpSecure: $smtp['secure'] ?? '',
+                smtpAutoTLS: false,
+                xMailer: 'Appwrite Mailer',
+                timeout: 10,
+                keepAlive: true,
+                timelimit: 30,
+            );
+
+        // Resolve from/replyTo using fallback hierarchy: Custom options > SMTP config > Defaults
+        $defaultFromEmail = System::getEnv('_APP_SYSTEM_EMAIL_ADDRESS', APP_EMAIL_TEAM);
+        $defaultFromName = \urldecode(System::getEnv('_APP_SYSTEM_EMAIL_NAME', APP_NAME . ' Server'));
+
+        $fromEmail = !empty($smtp) ? ($smtp['senderEmail'] ?? $defaultFromEmail) : $defaultFromEmail;
+        $fromName = !empty($smtp) ? ($smtp['senderName'] ?? $defaultFromName) : $defaultFromName;
+        $replyTo = $defaultFromEmail;
+        $replyToName = $defaultFromName;

         $customMailOptions = $payload['customMailOptions'] ?? [];

-        // fallback hierarchy: Custom options > SMTP config > Defaults.
-        if (!empty($customMailOptions['senderEmail']) || !empty($customMailOptions['senderName'])) {
-            $fromEmail = $customMailOptions['senderEmail'] ?? $mail->From;
-            $fromName = $customMailOptions['senderName'] ?? $mail->FromName;
-            $mail->setFrom($fromEmail, $fromName);
+        if (!empty($customMailOptions['senderEmail'])) {
+            $fromEmail = $customMailOptions['senderEmail'];
+        }
+        if (!empty($customMailOptions['senderName'])) {
+            $fromName = $customMailOptions['senderName'];
         }

         if (!empty($customMailOptions['replyToEmail']) || !empty($customMailOptions['replyToName'])) {
@@ -172,18 +177,32 @@ public function action(Message $message, Document $project, Registry $register,
             $replyToName = $smtp['senderName'] ?? $replyToName;
         }

-        $mail->addReplyTo($replyTo, $replyToName);
+        $attachments = null;
         if (!empty($attachment['content'] ?? '')) {
-            $mail->AddStringAttachment(
-                base64_decode($attachment['content']),
-                $attachment['filename'] ?? 'unknown.file',
-                $attachment['encoding'] ?? PHPMailer::ENCODING_BASE64,
-                $attachment['type'] ?? 'plain/text'
-            );
+            $attachments = [
+                new Attachment(
+                    name: $attachment['filename'] ?? 'unknown.file',
+                    path: '',
+                    type: $attachment['type'] ?? 'plain/text',
+                    content: \base64_decode($attachment['content']),
+                ),
+            ];
         }

+        $emailMessage = new EmailMessage(
+            to: [['email' => $recipient, 'name' => $name]],
+            subject: $subject,
+            content: $body,
+            fromName: $fromName,
+            fromEmail: $fromEmail,
+            replyToName: $replyToName,
+            replyToEmail: $replyTo,
+            attachments: $attachments,
+            html: true,
+        );
+
         try {
-            $mail->send();
+            $adapter->send($emailMessage);
         } catch (\Throwable $error) {
             if ($type === 'smtp') {
                 throw new Exception('Error sending mail: ' . $error->getMessage(), 401);
@@ -191,38 +210,4 @@ public function action(Message $message, Document $project, Registry $register,
             throw new Exception('Error sending mail: ' . $error->getMessage(), 500);
         }
     }
-
-    /**
-     * @param array $smtp
-     * @return PHPMailer
-     * @throws \PHPMailer\PHPMailer\Exception
-     */
-    protected function getMailer(array $smtp): PHPMailer
-    {
-        $mail = new PHPMailer(true);
-
-        $mail->isSMTP();
-
-        $username = $smtp['username'];
-        $password = $smtp['password'];
-
-        $mail->XMailer = 'Appwrite Mailer';
-        $mail->Host = $smtp['host'];
-        $mail->Port = $smtp['port'];
-        $mail->SMTPAuth = (!empty($username) && !empty($password));
-        $mail->Username = $username;
-        $mail->Password = $password;
-        $mail->SMTPSecure = $smtp['secure'];
-        $mail->SMTPAutoTLS = false;
-        $mail->SMTPKeepAlive = true;
-        $mail->CharSet = 'UTF-8';
-        $mail->Timeout = 10; /* Connection timeout */
-        $mail->getSMTPInstance()->Timelimit = 30; /* Timeout for each individual SMTP command (e.g. HELO, EHLO, etc.) */
-
-        $mail->setFrom($smtp['senderEmail'], $smtp['senderName']);
-
-        $mail->isHTML();
-
-        return $mail;
-    }
 }
PATCH

echo "Patch applied successfully!"
