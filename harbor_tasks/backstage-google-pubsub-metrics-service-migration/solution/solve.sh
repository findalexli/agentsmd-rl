#!/bin/bash
# Apply the gold patch from PR backstage/backstage#33754.
set -euo pipefail

cd /workspace/backstage

# Idempotency: if the gold change is already applied, do nothing.
if grep -q "MetricsServiceCounter<{ subscription: string; status: string }>" \
    plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.ts 2>/dev/null; then
  echo "Gold patch already applied; skipping."
  exit 0
fi

# Apply the inlined PR diff.
git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/common-plums-chew.md b/.changeset/common-plums-chew.md
new file mode 100644
index 00000000000000..714d29b5dcf90a
--- /dev/null
+++ b/.changeset/common-plums-chew.md
@@ -0,0 +1,5 @@
+---
+'@backstage/plugin-events-backend-module-google-pubsub': patch
+---
+
+Migrated internal metrics in `GooglePubSubConsumingEventPublisher` and `EventConsumingGooglePubSubPublisher` to use the new alpha `MetricsService`
diff --git a/plugins/events-backend-module-google-pubsub/package.json b/plugins/events-backend-module-google-pubsub/package.json
index 23bb7b1e9fc503..c460ea0cc564fb 100644
--- a/plugins/events-backend-module-google-pubsub/package.json
+++ b/plugins/events-backend-module-google-pubsub/package.json
@@ -40,8 +40,7 @@
     "@backstage/filter-predicates": "workspace:^",
     "@backstage/plugin-events-node": "workspace:^",
     "@backstage/types": "workspace:^",
-    "@google-cloud/pubsub": "^4.10.0",
-    "@opentelemetry/api": "^1.9.0"
+    "@google-cloud/pubsub": "^4.10.0"
   },
   "devDependencies": {
     "@backstage/backend-defaults": "workspace:^",
diff --git a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.test.ts b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.test.ts
index 96ef7d4551369f..23fa0f0763d65c 100644
--- a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.test.ts
+++ b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.test.ts
@@ -15,6 +15,7 @@
  */

 import { mockServices } from '@backstage/backend-test-utils';
+import { metricsServiceMock } from '@backstage/backend-test-utils/alpha';
 import { EventParams } from '@backstage/plugin-events-node';
 import { PubSub } from '@google-cloud/pubsub';
 import waitFor from 'wait-for-expect';
@@ -23,6 +24,7 @@ import { EventConsumingGooglePubSubPublisher } from './EventConsumingGooglePubSu
 describe('EventConsumingGooglePubSubPublisher', () => {
   const logger = mockServices.logger.mock();
   const events = mockServices.events.mock();
+  const metrics = metricsServiceMock.mock();

   let onEvent: undefined | ((event: EventParams) => void);
   events.subscribe.mockImplementation(async options => {
@@ -47,6 +49,7 @@ describe('EventConsumingGooglePubSubPublisher', () => {
     const publisher = new EventConsumingGooglePubSubPublisher({
       logger,
       events,
+      metrics,
       tasks: [
         {
           id: 'my-id',
diff --git a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.ts b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.ts
index 6847d944d5f632..280025b5316344 100644
--- a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.ts
+++ b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher.ts
@@ -21,7 +21,10 @@ import {
 } from '@backstage/backend-plugin-api';
 import { EventsService } from '@backstage/plugin-events-node';
 import { PubSub } from '@google-cloud/pubsub';
-import { Counter, metrics } from '@opentelemetry/api';
+import type {
+  MetricsService,
+  MetricsServiceCounter,
+} from '@backstage/backend-plugin-api/alpha';
 import { readSubscriptionTasksFromConfig } from './config';
 import { EventContext, SubscriptionTask } from './types';
 import { JsonValue } from '@backstage/types';
@@ -35,7 +38,9 @@ export class EventConsumingGooglePubSubPublisher {
   readonly #events: EventsService;
   readonly #tasks: SubscriptionTask[];
   readonly #pubSubFactory: (projectId: string) => PubSub;
-  readonly #metrics: { messages: Counter };
+  readonly #metrics: {
+    messages: MetricsServiceCounter<{ subscription: string; status: string }>;
+  };
   #activeClientsByProjectId: Map<string, PubSub>;

   static create(options: {
@@ -43,10 +48,12 @@ export class EventConsumingGooglePubSubPublisher {
     logger: LoggerService;
     rootLifecycle: RootLifecycleService;
     events: EventsService;
+    metrics: MetricsService;
   }) {
     const publisher = new EventConsumingGooglePubSubPublisher({
       logger: options.logger,
       events: options.events,
+      metrics: options.metrics,
       tasks: readSubscriptionTasksFromConfig(options.config),
       pubSubFactory: projectId => new PubSub({ projectId }),
     });
@@ -65,6 +72,7 @@ export class EventConsumingGooglePubSubPublisher {
   constructor(options: {
     logger: LoggerService;
     events: EventsService;
+    metrics: MetricsService;
     tasks: SubscriptionTask[];
     pubSubFactory: (projectId: string) => PubSub;
   }) {
@@ -73,14 +81,13 @@ export class EventConsumingGooglePubSubPublisher {
     this.#tasks = options.tasks;
     this.#pubSubFactory = options.pubSubFactory;

-    const meter = metrics.getMeter('default');
     this.#metrics = {
-      messages: meter.createCounter(
+      messages: options.metrics.createCounter(
         'events.google.pubsub.publisher.messages.total',
         {
           description:
             'Number of Pub/Sub messages sent by EventConsumingGooglePubSubPublisher',
-          unit: 'short',
+          unit: '{message}',
         },
       ),
     };
diff --git a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/module.ts b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/module.ts
index 498996fee031ae..db2503389b75ac 100644
--- a/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/module.ts
+++ b/plugins/events-backend-module-google-pubsub/src/EventConsumingGooglePubSubPublisher/module.ts
@@ -18,6 +18,7 @@ import {
   coreServices,
   createBackendModule,
 } from '@backstage/backend-plugin-api';
+import { metricsServiceRef } from '@backstage/backend-plugin-api/alpha';
 import { eventsServiceRef } from '@backstage/plugin-events-node';
 import { EventConsumingGooglePubSubPublisher } from './EventConsumingGooglePubSubPublisher';

@@ -38,13 +39,15 @@ export const eventsModuleEventConsumingGooglePubSubPublisher =
           logger: coreServices.logger,
           rootLifecycle: coreServices.rootLifecycle,
           events: eventsServiceRef,
+          metrics: metricsServiceRef,
         },
-        async init({ config, logger, rootLifecycle, events }) {
+        async init({ config, logger, rootLifecycle, events, metrics }) {
           EventConsumingGooglePubSubPublisher.create({
             config,
             logger,
             rootLifecycle,
             events,
+            metrics,
           });
         },
       });
diff --git a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.test.ts b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.test.ts
index 8b2f98d8af7c02..a3c4979acaeafb 100644
--- a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.test.ts
+++ b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.test.ts
@@ -15,6 +15,7 @@
  */

 import { mockServices } from '@backstage/backend-test-utils';
+import { metricsServiceMock } from '@backstage/backend-test-utils/alpha';
 import { Message, PubSub } from '@google-cloud/pubsub';
 import { GooglePubSubConsumingEventPublisher } from './GooglePubSubConsumingEventPublisher';
 import { JsonObject } from '@backstage/types';
@@ -36,6 +37,7 @@ function makeMessage(
 describe('GooglePubSubConsumingEventPublisher', () => {
   const logger = mockServices.logger.mock();
   const events = mockServices.events.mock();
+  const metrics = metricsServiceMock.mock();

   let onMessage: undefined | ((message: Message) => void);
   const subscription = {
@@ -62,6 +64,7 @@ describe('GooglePubSubConsumingEventPublisher', () => {
     const publisher = new GooglePubSubConsumingEventPublisher({
       logger,
       events,
+      metrics,
       tasks: [
         {
           id: 'my-id',
diff --git a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.ts b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.ts
index 12f7225da19496..d04b0ad4ed26e8 100644
--- a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.ts
+++ b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher.ts
@@ -23,7 +23,10 @@ import { ForwardedError } from '@backstage/errors';
 import { EventParams, EventsService } from '@backstage/plugin-events-node';
 import { JsonValue } from '@backstage/types';
 import { Message, PubSub, Subscription } from '@google-cloud/pubsub';
-import { Counter, metrics } from '@opentelemetry/api';
+import type {
+  MetricsService,
+  MetricsServiceCounter,
+} from '@backstage/backend-plugin-api/alpha';
 import { readSubscriptionTasksFromConfig } from './config';
 import { MessageContext, SubscriptionTask } from './types';

@@ -36,7 +39,9 @@ export class GooglePubSubConsumingEventPublisher {
   readonly #events: EventsService;
   readonly #tasks: SubscriptionTask[];
   readonly #pubSubFactory: (projectId: string) => PubSub;
-  readonly #metrics: { messages: Counter };
+  readonly #metrics: {
+    messages: MetricsServiceCounter<{ subscription: string; status: string }>;
+  };
   #activeClientsByProjectId: Map<string, PubSub>;
   #activeSubscriptions: Subscription[];

@@ -45,10 +50,12 @@ export class GooglePubSubConsumingEventPublisher {
     logger: LoggerService;
     rootLifecycle: RootLifecycleService;
     events: EventsService;
+    metrics: MetricsService;
   }) {
     const publisher = new GooglePubSubConsumingEventPublisher({
       logger: options.logger,
       events: options.events,
+      metrics: options.metrics,
       tasks: readSubscriptionTasksFromConfig(options.config),
       pubSubFactory: projectId => new PubSub({ projectId }),
     });
@@ -67,6 +74,7 @@ export class GooglePubSubConsumingEventPublisher {
   constructor(options: {
     logger: LoggerService;
     events: EventsService;
+    metrics: MetricsService;
     tasks: SubscriptionTask[];
     pubSubFactory: (projectId: string) => PubSub;
   }) {
@@ -75,14 +83,13 @@ export class GooglePubSubConsumingEventPublisher {
     this.#tasks = options.tasks;
     this.#pubSubFactory = options.pubSubFactory;

-    const meter = metrics.getMeter('default');
     this.#metrics = {
-      messages: meter.createCounter(
+      messages: options.metrics.createCounter(
         'events.google.pubsub.consumer.messages.total',
         {
           description:
             'Number of Pub/Sub messages received by GooglePubSubConsumingEventPublisher',
-          unit: 'short',
+          unit: '{message}',
         },
       ),
     };
diff --git a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/module.ts b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/module.ts
index 3d5fce14ee38ce..e76e2f2cb2b8ae 100644
--- a/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/module.ts
+++ b/plugins/events-backend-module-google-pubsub/src/GooglePubSubConsumingEventPublisher/module.ts
@@ -18,6 +18,7 @@ import {
   coreServices,
   createBackendModule,
 } from '@backstage/backend-plugin-api';
+import { metricsServiceRef } from '@backstage/backend-plugin-api/alpha';
 import { eventsServiceRef } from '@backstage/plugin-events-node';
 import { GooglePubSubConsumingEventPublisher } from './GooglePubSubConsumingEventPublisher';

@@ -36,13 +37,15 @@ export const eventsModuleGooglePubsubConsumingEventPublisher =
           logger: coreServices.logger,
           rootLifecycle: coreServices.rootLifecycle,
           events: eventsServiceRef,
+          metrics: metricsServiceRef,
         },
-        async init({ config, logger, rootLifecycle, events }) {
+        async init({ config, logger, rootLifecycle, events, metrics }) {
           GooglePubSubConsumingEventPublisher.create({
             config,
             logger,
             rootLifecycle,
             events,
+            metrics,
           });
         },
       });
PATCH

echo "Gold patch applied successfully."
