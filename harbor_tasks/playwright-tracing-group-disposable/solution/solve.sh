#!/bin/bash
set -e

cd /workspace/playwright

# Apply the gold patch: Tracing.group returns Disposable + CLAUDE.md update
patch -p1 <<'EOF'
diff --git a/CLAUDE.md b/CLAUDE.md
index 9b85a3d23fa0e..d5bdcd3a62372 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -96,6 +96,8 @@ When creating or moving files, update the relevant `DEPS.list` to declare allowe

 ## Commit Convention

+Before committing, run `npm run flint` and fix errors.
+
 Semantic commit messages: `label(scope): description`

 Labels: `fix`, `feat`, `chore`, `docs`, `test`, `devops`
diff --git a/docs/src/api/class-tracing.md b/docs/src/api/class-tracing.md
index 704409a1705da..9c4b5221d0e62 100644
--- a/docs/src/api/class-tracing.md
+++ b/docs/src/api/class-tracing.md
@@ -305,6 +305,7 @@ To specify the final trace zip file name, you need to pass `path` option to

 ## async method: Tracing.group
 * since: v1.49
+- returns: <[Disposable]>

 :::caution
 Use `test.step` instead when available.
diff --git a/packages/playwright-client/types/types.d.ts b/packages/playwright-client/types/types.d.ts
index 572435010d35c..3f8e9d677c7cd 100644
--- a/packages/playwright-client/types/types.d.ts
+++ b/packages/playwright-client/types/types.d.ts
@@ -21957,7 +21957,7 @@ export interface Tracing {

       column?: number;
     };
-  }): Promise<void>;
+  }): Promise<Disposable>;

   /**
    * Closes the last group created by
diff --git a/packages/playwright-core/src/client/tracing.ts b/packages/playwright-core/src/client/tracing.ts
index cd5e06ff5d042..5fed143e0a805 100644
--- a/packages/playwright-core/src/client/tracing.ts
+++ b/packages/playwright-core/src/client/tracing.ts
@@ -16,6 +16,7 @@

 import { Artifact } from './artifact';
 import { ChannelOwner } from './channelOwner';
+import { DisposableStub } from './disposable';

 import type * as api from '../../types/types';
 import type * as channels from '@protocol/channels';
@@ -62,6 +63,7 @@ export class Tracing extends ChannelOwner<channels.TracingChannel> implements ap
     if (options.location)
       this._additionalSources.add(options.location.file);
     await this._channel.tracingGroup({ name, location: options.location });
+    return new DisposableStub(() => this.groupEnd());
   }

   async groupEnd() {
diff --git a/packages/playwright-core/types/types.d.ts b/packages/playwright-core/types/types.d.ts
index 572435010d35c..3f8e9d677c7cd 100644
--- a/packages/playwright-core/types/types.d.ts
+++ b/packages/playwright-core/types/types.d.ts
@@ -21957,7 +21957,7 @@ export interface Tracing {

       column?: number;
     };
-  }): Promise<void>;
+  }): Promise<Disposable>;

   /**
    * Closes the last group created by
diff --git a/tests/library/screencast.spec.ts b/tests/library/screencast.spec.ts
index 69bdfbe150615..7ab98d300b008 100644
--- a/tests/library/screencast.spec.ts
+++ b/tests/library/screencast.spec.ts
@@ -97,9 +97,9 @@ test('screencast.start dispose stops screencast', async ({ browser, server, tr
   const page = await context.newPage();

   const frames: { data: Buffer }[] = [];
-  page.screencast().on('screencastframe', frame => frames.push(frame));
+  page.screencast.on('screencastframe', frame => frames.push(frame));

-  const disposable = await page.screencast().start({ maxSize: { width: 500, height: 400 } });
+  const disposable = await page.screencast.start({ maxSize: { width: 500, height: 400 } });
   await page.goto(server.EMPTY_PAGE);
   await page.evaluate(() => document.body.style.backgroundColor = 'red');
   await rafraf(page, 100);
EOF

# Idempotency check: verify the key change is in place
if ! grep -q "Before committing, run \`npm run flint\`" CLAUDE.md; then
    echo "ERROR: CLAUDE.md was not patched correctly"
    exit 1
fi

if ! grep -q "return new DisposableStub" packages/playwright-core/src/client/tracing.ts; then
    echo "ERROR: tracing.ts was not patched correctly"
    exit 1
fi

echo "Gold patch applied successfully"
