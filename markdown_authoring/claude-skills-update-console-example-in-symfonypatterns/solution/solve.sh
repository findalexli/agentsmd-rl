#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "$user = $this->userService->createUser($email, $password, $isAdmin);" "skills/php-pro/references/symfony-patterns.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/php-pro/references/symfony-patterns.md b/skills/php-pro/references/symfony-patterns.md
@@ -322,16 +322,11 @@ final class CreateUserCommand extends Command
         $password = $input->getArgument('password');
         $isAdmin = $input->getOption('admin');
 
-        try {
-            $user = $this->userService->createUser($email, $password, $isAdmin);
+        $user = $this->userService->createUser($email, $password, $isAdmin);
 
-            $io->success(sprintf('User created with ID: %d', $user->getId()));
+        $io->success(sprintf('User created with ID: %d', $user->getId()));
 
-            return Command::SUCCESS;
-        } catch (\Exception $e) {
-            $io->error($e->getMessage());
-            return Command::FAILURE;
-        }
+        return Command::SUCCESS;
     }
 }
 ```
PATCH

echo "Gold patch applied."
